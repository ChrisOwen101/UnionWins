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
            reasoning={"effort": "none"},
            input=f"""You are an expert at extracting information about union victories and labour wins from news articles and web pages.

Analyze this URL: {url}

Extract the following information and return ONLY a valid JSON object with no other text:
- title: string (clear, descriptive title)
- union_name: string (name of the union or labour organization, e.g., "Unite", "GMB", "Unison", "TUC", etc)
- emoji: string (single emoji character that represents the win, e.g., "🏥", "🚌", "📚", "✊")
- date: string (YYYY-MM-DD format)
- url: string (credible source URL)
- summary: string (3-5 sentence summary)

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
    submission = UnionWinDB(
        title=scraped_data["title"],
        union_name=scraped_data.get("union_name"),
        emoji=None,  # Admin can set this later
        date=scraped_data["date"],
        url=url,
        summary=scraped_data["summary"],
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
