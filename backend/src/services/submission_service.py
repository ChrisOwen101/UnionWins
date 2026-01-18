"""
Service for handling user submissions of What Have Unions Done For Us.
Uses OpenAI to scrape and extract information from submitted URLs.
"""
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.config import client, DEFAULT_WIN_IMAGE_URL
from src.models import UnionWinDB


def scrape_url_with_openai(url: str) -> dict:
    """
    Use OpenAI GPT-5.2 with web search to scrape a URL and extract union win information.

    Args:
        url: The URL to scrape

    Returns:
        dict with keys: title, union_name, date, summary, image (or None on failure)
    """
    try:
        print(f"🔍 Scraping URL with OpenAI: {url}", flush=True)

        # Use GPT-5.2 with Responses API and web search tool
        response = client.responses.create(
            model="gpt-5.2",
            tools=[{"type": "web_search"}],
            reasoning={"effort": "medium"},
            text={"format": "json"},
            input=f"""You are an expert at extracting information about union victories and labour wins from news articles and web pages.

Analyze this URL: {url}

Extract the following information:
- title: A concise, compelling title (max 100 characters)
- union_name: The name of the union involved (e.g., "Unite", "GMB", "RMT", "NEU")
- date: The date of the win in YYYY-MM-DD format (if not found, use today's date)
- summary: A clear 3-5 sentence summary of the win
- image: The URL of a relevant image from the article (if available)

Return the information as a JSON object with these exact keys.
If you cannot find specific information, use reasonable defaults or indicate null."""
        )

        result = json.loads(response.output_text)
        print(f"✅ Successfully extracted data from URL", flush=True)

        # Ensure we have required fields
        if not result.get("title"):
            result["title"] = "Union Win"
        if not result.get("date"):
            result["date"] = datetime.now().strftime("%Y-%m-%d")
        if not result.get("summary"):
            result["summary"] = "A victory for workers and their union."
        if not result.get("image"):
            result["image"] = DEFAULT_WIN_IMAGE_URL

        return result

    except Exception as e:
        print(f"❌ Error scraping URL with OpenAI: {e}", flush=True)
        import traceback
        traceback.print_exc()
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
    # Check if URL already exists
    existing = db.query(UnionWinDB).filter(UnionWinDB.url == url).first()
    if existing:
        raise ValueError("This URL has already been submitted")

    # Scrape the URL with OpenAI
    scraped_data = scrape_url_with_openai(url)
    if not scraped_data:
        raise ValueError("Failed to extract information from URL")

    # Create pending submission
    submission = UnionWinDB(
        title=scraped_data["title"],
        union_name=scraped_data.get("union_name"),
        emoji=None,  # Admin can set this later
        date=scraped_data["date"],
        url=url,
        image=scraped_data["image"],
        summary=scraped_data["summary"],
        status="pending",
        submitted_by=submitted_by
    )

    try:
        db.add(submission)
        db.commit()
        db.refresh(submission)
        return submission
    except IntegrityError:
        db.rollback()
        raise ValueError("This URL has already been submitted")


def get_pending_submissions(db: Session) -> list[UnionWinDB]:
    """Get all pending submissions for admin review."""
    return db.query(UnionWinDB).filter(UnionWinDB.status == "pending").order_by(UnionWinDB.created_at.desc()).all()


def approve_submission(db: Session, submission_id: int) -> UnionWinDB:
    """Approve a pending submission, making it visible on the site."""
    submission = db.query(UnionWinDB).filter(
        UnionWinDB.id == submission_id).first()
    if not submission:
        raise ValueError("Submission not found")

    submission.status = "approved"
    db.commit()
    db.refresh(submission)
    return submission


def reject_submission(db: Session, submission_id: int) -> UnionWinDB:
    """Reject a pending submission."""
    submission = db.query(UnionWinDB).filter(
        UnionWinDB.id == submission_id).first()
    if not submission:
        raise ValueError("Submission not found")

    submission.status = "rejected"
    db.commit()
    db.refresh(submission)
    return submission
