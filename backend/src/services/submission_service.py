"""
Service for handling user submissions of What Have Unions Done For Us.
Uses OpenAI to scrape and extract information from submitted URLs.
"""
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.config import client
from src.models import UnionWinDB

# Set up logging
logger = logging.getLogger(__name__)


def scrape_url_with_openai(url: str) -> dict:
    """
    Use OpenAI GPT-5.2 with web search to scrape a URL and extract union win information.

    Extracts structured data including a list of relevant image URLs from the article.
    The image extraction prioritizes:
    1. Open Graph (og:image) meta tag - typically the article's main image
    2. Twitter card image (twitter:image) meta tag
    3. Content images showing workers, unions, or related to the story

    Args:
        url: The URL to scrape

    Returns:
        dict with keys: title, union_name, date, summary, image_urls (or None on failure)
    """
    try:
        print(f"🔍 Scraping URL with OpenAI: {url}", flush=True)

        # Use GPT-5.2 with Responses API and web search tool
        response = client.responses.create(
            model="gpt-5.2",
            tools=[{"type": "web_search"}],
            reasoning={"effort": "none"},
            input=f"""You are an expert at extracting information about union victories and labour wins from news articles and web pages.

Analyse this URL: {url}

Extract the following information and return ONLY a valid JSON object with no other text:
- title: string (clear, descriptive title)
- union_name: string (name of the union or labour organisation, e.g., "Unite", "GMB", "Unison", "TUC", etc)
- emoji: string (single emoji character that represents the win, e.g., "🏥", "🚌", "📚", "✊")
- primary_type: string (primary type, one of: "Pay Rise", "Recognition", "Strike Action", "Working Conditions", "Job Security", "Benefits", "Health & Safety", "Equality", "Legal Victory", "Organizing", "Other")
- secondary_type: string or null (optional secondary type if the win fits multiple categories - use null if only one type applies)
- date: string (YYYY-MM-DD format)
- url: string (credible source URL)
- summary: string (3-5 sentence summary)
- image_urls: array of strings (list of relevant image URLs from the article, up to 5 images)

For image_urls extraction, follow these rules:
1. Include the og:image (Open Graph) meta tag if present - this is typically the article's featured image
2. Include the twitter:image meta tag if present and different from og:image
3. Include content images that show workers, union members, protests, workplace scenes, or are directly related to the story
4. Order images by relevance - most relevant first
5. Return up to 5 images maximum
6. AVOID: Generic stock photos, logos, advertisements, icons, social media buttons, or unrelated decorative images
7. AVOID: Images smaller than 200x200 pixels (thumbnails, icons)
8. All image URLs must be absolute URLs (starting with http:// or https://)
9. If no suitable images are found, return an empty array []

Return ONLY the JSON object with these exact keys, no markdown formatting, no explanation."""
        )

        result = json.loads(response.output_text)
        print("✅ Successfully extracted data from URL", flush=True)

        # Ensure we have required fields
        if not result.get("title"):
            result["title"] = "Union Win"
        if not result.get("date"):
            result["date"] = datetime.now().strftime("%Y-%m-%d")
        if not result.get("summary"):
            result["summary"] = "A victory for workers and their union."
        
        # Combine primary and secondary types into comma-separated string
        types = []
        if result.get("primary_type"):
            types.append(result["primary_type"])
        if result.get("secondary_type"):
            types.append(result["secondary_type"])
        result["win_types"] = ", ".join(types) if types else None

        # Ensure image_urls is a list
        if not isinstance(result.get("image_urls"), list):
            result["image_urls"] = []

        # Log image extraction result
        image_count = len(result.get("image_urls", []))
        if image_count > 0:
            print(f"🖼️  Extracted {image_count} image(s) from article", flush=True)
        else:
            print("⚠️  No suitable images found in article", flush=True)

        return result

    except Exception as e:
        logger.error(f"Error scraping URL with OpenAI: {e}", exc_info=True)
        print(f"❌ Error scraping URL with OpenAI: {e}", flush=True)
        return None


def create_submission(db: Session, url: str, submitted_by: str | None = None) -> UnionWinDB | None:
    """
    Create a new pending submission by scraping the URL with OpenAI.

    Args:
        db: Database session
        url: The URL to scrape
        submitted_by: Optional name/email of submitter

    Returns:
        The created UnionWinDB object or None on failure
    """
    logger.info(f"Creating submission for URL: {url}")

    # Check if URL already exists
    existing = db.query(UnionWinDB).filter(UnionWinDB.url == url).first()
    if existing:
        logger.warning(f"URL already submitted: {url}")
        raise ValueError("This URL has already been submitted")

    # Scrape the URL with OpenAI
    logger.debug(f"Scraping URL with OpenAI: {url}")
    scraped_data = scrape_url_with_openai(url)
    if not scraped_data:
        logger.error(f"Failed to extract information from URL: {url}")
        raise ValueError("Failed to extract information from URL")

    # Create pending submission
    # Convert image_urls list to JSON string for storage
    image_urls_json = json.dumps(scraped_data.get("image_urls", [])) if scraped_data.get("image_urls") else None
    
    submission = UnionWinDB(
        title=scraped_data["title"],
        union_name=scraped_data.get("union_name"),
        emoji=scraped_data.get("emoji"),
        win_types=scraped_data.get("win_types"),
        date=scraped_data["date"],
        url=url,
        summary=scraped_data["summary"],
        image_urls=image_urls_json,
        status="pending",
        submitted_by=submitted_by
    )

    try:
        db.add(submission)
        db.commit()
        db.refresh(submission)
        logger.info(
            f"Successfully created submission {submission.id} for URL: {url}")
        return submission
    except IntegrityError as e:
        logger.error(
            f"Database integrity error while creating submission for URL {url}: {e}", exc_info=True)
        db.rollback()
        raise ValueError("This URL has already been submitted")
    except Exception as e:
        logger.error(
            f"Unexpected error creating submission for URL {url}: {e}", exc_info=True)
        db.rollback()
        raise


def get_pending_submissions(db: Session) -> list[UnionWinDB]:
    """Get all pending submissions for admin review."""
    try:
        submissions = db.query(UnionWinDB).filter(
            UnionWinDB.status == "pending").order_by(UnionWinDB.created_at.desc()).all()
        logger.debug(f"Retrieved {len(submissions)} pending submissions")
        return submissions
    except Exception as e:
        logger.error(
            f"Error retrieving pending submissions: {e}", exc_info=True)
        raise


def approve_submission(db: Session, submission_id: int) -> UnionWinDB:
    """Approve a pending submission, making it visible on the site."""
    try:
        submission = db.query(UnionWinDB).filter(
            UnionWinDB.id == submission_id).first()
        if not submission:
            logger.warning(
                f"Attempt to approve non-existent submission: {submission_id}")
            raise ValueError("Submission not found")

        submission.status = "approved"
        db.commit()
        db.refresh(submission)
        logger.info(f"Approved submission {submission_id}")
        return submission
    except Exception as e:
        logger.error(
            f"Error approving submission {submission_id}: {e}", exc_info=True)
        db.rollback()
        raise


def reject_submission(db: Session, submission_id: int) -> UnionWinDB:
    """Reject a pending submission."""
    try:
        submission = db.query(UnionWinDB).filter(
            UnionWinDB.id == submission_id).first()
        if not submission:
            logger.warning(
                f"Attempt to reject non-existent submission: {submission_id}")
            raise ValueError("Submission not found")

        submission.status = "rejected"
        db.commit()
        db.refresh(submission)
        logger.info(f"Rejected submission {submission_id}")
        return submission
    except Exception as e:
        logger.error(
            f"Error rejecting submission {submission_id}: {e}", exc_info=True)
        db.rollback()
        raise
