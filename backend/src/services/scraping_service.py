"""
Service for scraping union websites for potential wins.
"""
import logging
import json
import random
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sqlalchemy.orm import Session

from src.config import client
from src.database import SessionLocal
from src.models import ScrapeSourceDB, UnionWinDB
from src.services.submission_service import create_submission

logger = logging.getLogger(__name__)

# Rotating user agents to avoid bot detection
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


def create_session_with_retries(max_retries: int = 3) -> requests.Session:
    """Create a requests session with retry logic and connection pooling."""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=1,  # Wait 1s, 2s, 4s between retries
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def fetch_page_content(url: str, verify_ssl: bool = True, retry_without_ssl: bool = True):
    """
    Fetch HTML content from a URL with robust error handling.
    
    Args:
        url: The URL to fetch
        verify_ssl: Whether to verify SSL certificates (True by default)
        retry_without_ssl: If SSL fails, retry without verification
    
    Returns:
        HTML content as string, or None if fetch failed
    """
    session = create_session_with_retries()
    
    # More comprehensive headers to appear as a real browser
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    try:
        # Add a small random delay to be more polite and avoid rate limiting
        time.sleep(random.uniform(0.5, 1.5))
        
        response = session.get(
            url, 
            headers=headers, 
            timeout=30,
            verify=verify_ssl,
            allow_redirects=True
        )
        response.raise_for_status()
        return response.text
        
    except requests.exceptions.SSLError as e:
        if retry_without_ssl and verify_ssl:
            logger.warning(f"SSL error for {url}, retrying without SSL verification: {e}")
            # Retry without SSL verification for sites with certificate issues
            return fetch_page_content(url, verify_ssl=False, retry_without_ssl=False)
        logger.error(f"SSL error fetching {url}: {e}")
        return None
        
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 403:
            logger.warning(f"403 Forbidden for {url} - site may be blocking scrapers")
        else:
            logger.error(f"HTTP error fetching {url}: {e}")
        return None
        
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error fetching {url}: {e}")
        return None
        
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout fetching {url}: {e}")
        return None
        
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None
    finally:
        session.close()

def extract_candidates(base_url, html_content):
    """
    Extract potential article links from HTML content.
    Returns a list of dicts with url, text, and context.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    candidates = []
    seen_urls = set()
    
    # Heuristic: Focus on main content areas if possible, but comprehensive for now
    # We look for 'a' tags with hrefs
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        
        # Normalize URL (simple)
        full_url = full_url.split('#')[0]
        
        if full_url in seen_urls:
            continue
        
        # Basic filtering to skip obviously irrelevant links
        lower_url = full_url.lower()
        if not full_url.startswith('http'):
            continue
        
        # Skip same-page links or common non-article pages
        skip_keywords = [
            '/login', '/register', '/signin', '/signup', 
            '/contact', '/about', '/privacy', '/terms', 
            '/search', '/join', '/member', 'javascript:', 'mailto:'
        ]
        if any(k in lower_url for k in skip_keywords):
            continue
            
        # Get link text and surrounding context
        text = a.get_text(strip=True)
        if not text:
            # Try looking for nested image alt or title
            img = a.find('img')
            if img:
                text = img.get('alt') or img.get('title') or ""
        
        if not text or len(text) < 5:
            continue
            
        # Context: Get text from the parent element to give more info
        parent = a.find_parent()
        context = parent.get_text(strip=True)[:300] if parent else ""
        
        seen_urls.add(full_url)
        candidates.append({
            "url": full_url,
            "text": text,
            "context": context
        })
        
    return candidates

def filter_candidates_with_llm(candidates):
    """
    Use LLM to identify which candidates are likely "Wins" or "Achievements".
    Returns a list of candidate dicts that passed the filter.
    """
    if not candidates:
        return []
    
    # We'll process in batches to match token limits/costs
    batch_size = 20
    good_candidates = []
    
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i+batch_size]
        
        # Prepare lightweight representation for LLM
        prompt_items = []
        for idx, item in enumerate(batch):
            prompt_items.append(f"ID {idx}: TEXT: {item['text']} | URL: {item['url']} | CONTEXT: {item['context']}")
            
        prompt_text = "\n".join(prompt_items)
        
        try:
            response = client.chat.completions.create(
                model="gpt-5-nano", # Cheaper model for fast filtering
                messages=[
                    {"role": "system", "content": "You are a news curator for a Union Wins dashboard. Your goal is to identify links that point to specific news articles about union victories, agreements, wins, pay rises, or achievements. Ignore generic pages, indices, policy documents, unrelated news, elections of new leadership."},
                    {"role": "user", "content": f"Analyze the following list of links. Return a JSON object with a key 'relevant_ids' containing a list of IDs (integers) that are likely Union Wins/Achievements.\n\n{prompt_text}"}
                ],
                response_format={"type": "json_object"}
            )
            
            result_json = json.loads(response.choices[0].message.content)
            relevant_ids = result_json.get("relevant_ids", [])
            
            for rid in relevant_ids:
                if 0 <= rid < len(batch):
                    good_candidates.append(batch[rid])
                    
        except Exception as e:
            logger.error(f"Error filtering candidates with LLM: {e}")
            # On error, maybe skip or assume all false? Skip for safety.
            continue
            
    return good_candidates

def run_scrape_for_source(db: Session, source_id: int):
    """
    Execute the scraping pipeline for a specific source.
    """
    source = db.query(ScrapeSourceDB).filter(ScrapeSourceDB.id == source_id).first()
    if not source:
        logger.error(f"Source ID {source_id} not found.")
        return {"status": "error", "message": "Source not found"}
        
    logger.info(f"Starting scrape for {source.url}")
    
    # 1. Fetch
    html = fetch_page_content(source.url)
    if not html:
        source.last_scraped_at = datetime.now()
        source.last_scrape_status = "error"
        source.last_scrape_error = "Failed to fetch page content - site may be blocking scrapers, have SSL issues, or be temporarily unavailable"
        db.commit()
        return {"status": "error", "message": "Failed to fetch page"}
        
    # 2. Extract
    try:
        candidates = extract_candidates(source.url, html)
        logger.info(f"Found {len(candidates)} raw links")
        
        # 3. Dedup against DB (UnionWinDB)
        # We want to check if we've already imported these URLs recently
        # To save tokens, we check DB existence BEFORE LLM filter
        
        candidate_urls = [c['url'] for c in candidates]
        
        # Check for exact matches in DB
        existing_wins = db.query(UnionWinDB.url).filter(UnionWinDB.url.in_(candidate_urls)).all()
        existing_urls = {w[0] for w in existing_wins}
        
        new_candidates = [c for c in candidates if c['url'] not in existing_urls]
        logger.info(f"Filtered down to {len(new_candidates)} new candidates (removed {len(existing_urls)} duplicates)")
        
        if not new_candidates:
            source.last_scraped_at = datetime.now()
            source.last_scrape_status = "success"
            source.last_scrape_error = None
            db.commit()
            return {"status": "success", "new_wins": 0, "message": "No new links found"}

        # 4. Filter with LLM
        likely_wins = filter_candidates_with_llm(new_candidates)
        logger.info(f"LLM identified {len(likely_wins)} likely wins")
        
        # 5. Submit
        submitted_count = 0
        for win_candidate in likely_wins:
            try:
                # We call create_submission.
                # create_submission will do the "Heavy" scrape using GPT-5.2 or equivalent to extract details
                try:
                    create_submission(db, win_candidate['url'], submitted_by="AutoScraper")
                    submitted_count += 1
                except ValueError as ve:
                    if "already" in str(ve).lower():
                        continue
                    logger.warning(f"Submission failed for {win_candidate['url']}: {ve}")
                except Exception as e:
                    logger.error(f"Error submitting {win_candidate['url']}: {e}")
                    
            except Exception as e:
                logger.error(f"Critical error in loop: {e}")
                
        # Update source stats
        source.last_scraped_at = datetime.now()
        source.last_scrape_status = "success"
        source.last_scrape_error = None
        db.commit()
        
        return {
            "status": "success",
            "scraped_at": source.last_scraped_at,
            "raw_links_found": len(candidates),
            "new_links_checked": len(new_candidates),
            "wins_identified": len(likely_wins),
            "wins_submitted": submitted_count
        }
    except Exception as e:
        logger.error(f"Scrape failed for {source.url}: {e}")
        source.last_scraped_at = datetime.now()
        source.last_scrape_status = "error"
        source.last_scrape_error = str(e)
        db.commit()
        return {"status": "error", "message": f"Scrape failed: {e}"}


def run_scrape_for_source_safe(source_id: int):
    """
    Wrapper to run scrape for a source with its own DB session.
    Safe for threading.
    """
    db = SessionLocal()
    try:
        return run_scrape_for_source(db, source_id)
    except Exception as e:
        logger.error(f"Threaded scrape failed for {source_id}: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def run_all_scrapes(db: Session):
    """Run scraping for all active sources in parallel."""
    # We query IDs first, then let each thread handle its own DB session/object
    # This avoids sharing the same session across threads which causes concurrency issues
    source_ids = [s[0] for s in db.query(ScrapeSourceDB.id).filter(ScrapeSourceDB.is_active == 1).all()]
    
    results = []
    logger.info(f"Starting parallel scrape for {len(source_ids)} sources...")
    
    # Use ThreadPoolExecutor to run scrapes in parallel
    # Limit max_workers to avoid destroying the CPU/Network or hitting rate limits too hard
    # 5 workers is usually a safe bet for IO-bound scraping tasks on a single node
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_id = {executor.submit(run_scrape_for_source_safe, sid): sid for sid in source_ids}
        
        for future in as_completed(future_to_id):
            sid = future_to_id[future]
            try:
                res = future.result()
                results.append({"source_id": sid, "result": res})
            except Exception as e:
                logger.error(f"Scrape job failed for {sid}: {e}")
                results.append({"source_id": sid, "result": {"status": "error", "message": str(e)}})
                
    return results
