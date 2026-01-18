"""
Service for managing What Have Unions Done For Us.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from src.models import UnionWinDB
from src.schemas import UnionWin


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
