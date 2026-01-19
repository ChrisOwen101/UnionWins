"""
Service for managing What Have Unions Done For Us.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.models import UnionWinDB
from src.schemas import UnionWin, UpdateWinRequest


def get_all_wins(db: Session) -> list[UnionWinDB]:
    """
    Retrieve all approved wins from database.

    Args:
        db: Database session

    Returns:
        List of UnionWinDB instances with status='approved'
    """
    return db.query(UnionWinDB).filter(UnionWinDB.status == "approved").all()


def convert_db_win_to_schema(win_db: UnionWinDB) -> UnionWin:
    """
    Convert database model to Pydantic schema.

    Args:
        win_db: UnionWinDB instance

    Returns:
        UnionWin Pydantic model
    """
    return UnionWin(
        id=win_db.id,
        title=win_db.title,
        union_name=win_db.union_name,
        emoji=win_db.emoji,
        date=win_db.date,
        url=win_db.url,
        summary=win_db.summary
    )


def sort_wins_by_date(wins: list[UnionWin], reverse: bool = True) -> list[UnionWin]:
    """
    Sort wins by date.

    Args:
        wins: List of UnionWin instances
        reverse: If True, sort in descending order (newest first)

    Returns:
        Sorted list of wins
    """
    return sorted(
        wins,
        key=lambda w: datetime.fromisoformat(w.date),
        reverse=reverse
    )


def get_all_wins_sorted(db: Session) -> list[UnionWin]:
    """
    Get all What Have Unions Done For Us sorted by date in reverse chronological order.

    Args:
        db: Database session

    Returns:
        List of UnionWin instances sorted by date (newest first)
    """
    wins_db = get_all_wins(db)
    wins = [convert_db_win_to_schema(win) for win in wins_db]
    return sort_wins_by_date(wins, reverse=True)


def get_win_by_id(db: Session, win_id: int) -> UnionWinDB | None:
    """
    Get a single win by ID.

    Args:
        db: Database session
        win_id: ID of the win to retrieve

    Returns:
        UnionWinDB instance or None if not found
    """
    return db.query(UnionWinDB).filter(UnionWinDB.id == win_id).first()


def update_win(db: Session, win_id: int, update_data: UpdateWinRequest) -> UnionWin | None:
    """
    Update an existing win with new data.

    Args:
        db: Database session
        win_id: ID of the win to update
        update_data: UpdateWinRequest with fields to update

    Returns:
        Updated UnionWin schema or None if win not found
    """
    win_db = get_win_by_id(db, win_id)
    if not win_db:
        return None

    # Update only provided fields
    if update_data.title is not None:
        win_db.title = update_data.title
    if update_data.union_name is not None:
        win_db.union_name = update_data.union_name
    if update_data.emoji is not None:
        win_db.emoji = update_data.emoji
    if update_data.date is not None:
        win_db.date = update_data.date
    if update_data.url is not None:
        win_db.url = update_data.url
    if update_data.summary is not None:
        win_db.summary = update_data.summary

    db.commit()
    db.refresh(win_db)

    return convert_db_win_to_schema(win_db)


def get_unique_months(wins: list[UnionWin]) -> list[str]:
    """
    Get unique months from wins list in YYYY-MM format, sorted descending.

    Args:
        wins: List of UnionWin instances

    Returns:
        List of unique month strings (YYYY-MM format) sorted newest first
    """
    months = set()
    for win in wins:
        date = datetime.fromisoformat(win.date)
        months.add(date.strftime("%Y-%m"))
    return sorted(months, reverse=True)


def get_wins_by_months(
    db: Session,
    month_offset: int = 0,
    num_months: int = 3
) -> tuple[list[UnionWin], list[str], bool, int]:
    """
    Get wins for a range of months with pagination.

    Args:
        db: Database session
        month_offset: Number of months to skip from the most recent
        num_months: Number of months to return

    Returns:
        Tuple of (wins, months_included, has_more, total_months)
    """
    all_wins = get_all_wins_sorted(db)
    all_months = get_unique_months(all_wins)
    total_months = len(all_months)

    # Get the months we want
    start_idx = month_offset
    end_idx = month_offset + num_months
    target_months = all_months[start_idx:end_idx]

    # Filter wins to only those in target months
    filtered_wins = [
        win for win in all_wins
        if datetime.fromisoformat(win.date).strftime("%Y-%m") in target_months
    ]

    has_more = end_idx < total_months

    return filtered_wins, target_months, has_more, total_months


def search_wins(db: Session, query: str) -> list[UnionWin]:
    """
    Search wins by query string across title, union_name, and summary.

    Args:
        db: Database session
        query: Search query string

    Returns:
        List of matching UnionWin instances sorted by date
    """
    search_pattern = f"%{query}%"
    wins_db = (
        db.query(UnionWinDB)
        .filter(UnionWinDB.status == "approved")
        .filter(
            or_(
                UnionWinDB.title.ilike(search_pattern),
                UnionWinDB.union_name.ilike(search_pattern),
                UnionWinDB.summary.ilike(search_pattern),
                UnionWinDB.url.ilike(search_pattern),
            )
        )
        .all()
    )
    wins = [convert_db_win_to_schema(win) for win in wins_db]
    return sort_wins_by_date(wins, reverse=True)
