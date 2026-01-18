"""
Service for managing search requests.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models import SearchRequestDB


def calculate_date_range(days: int = 7) -> tuple[datetime, datetime, str]:
    """
    Calculate a date range from today backwards.

    Args:
        days: Number of days to go back

    Returns:
        Tuple of (start_date, end_date, formatted_string)
    """
    today = datetime.now()
    start_date = today - timedelta(days=days)
    date_range_str = (
        f"{start_date.strftime('%B %d, %Y')} to {today.strftime('%B %d, %Y')}"
    )
    return start_date, today, date_range_str


def create_search_request(db: Session, date_range: str) -> SearchRequestDB:
    """
    Create a new search request in the database.

    Args:
        db: Database session
        date_range: String representation of date range

    Returns:
        Created SearchRequestDB instance
    """
    search_request = SearchRequestDB(
        status="pending",
        date_range=date_range
    )
    db.add(search_request)
    db.commit()
    db.refresh(search_request)
    return search_request


def get_pending_requests(db: Session) -> SearchRequestDB | None:
    """
    Get the first pending search request.

    Args:
        db: Database session

    Returns:
        First pending SearchRequestDB or None
    """
    return db.query(SearchRequestDB).filter(
        SearchRequestDB.status == "pending"
    ).first()


def get_processing_requests(db: Session) -> list[SearchRequestDB]:
    """
    Get all processing search requests that have a response ID.

    Args:
        db: Database session

    Returns:
        List of processing SearchRequestDB instances
    """
    return db.query(SearchRequestDB).filter(
        SearchRequestDB.status == "processing",
        SearchRequestDB.response_id.isnot(None)
    ).all()
