"""
API routes for What Have Unions Done For Us endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import UnionWin
from src.services.win_service import get_all_wins_sorted

router = APIRouter(prefix="/api/wins", tags=["wins"])


@router.get("")
async def get_wins(db: Session = Depends(get_db)) -> list[UnionWin]:
    """Get all What Have Unions Done For Us sorted by date in reverse chronological order."""
    return get_all_wins_sorted(db)
