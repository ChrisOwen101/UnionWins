"""
API routes for What Have Unions Done For Us endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import UnionWin, UpdateWinRequest, PaginatedWinsResponse, WinsSearchResponse
from src.services.win_service import (
    get_all_wins_sorted,
    update_win,
    get_wins_by_months,
    search_wins,
)

router = APIRouter(prefix="/api/wins", tags=["wins"])


@router.get("")
async def get_wins(db: Session = Depends(get_db)) -> list[UnionWin]:
    """Get all What Have Unions Done For Us sorted by date in reverse chronological order."""
    return get_all_wins_sorted(db)


@router.get("/paginated")
async def get_wins_paginated(
    month_offset: int = Query(
        default=0, ge=0, description="Number of months to skip"),
    num_months: int = Query(default=3, ge=1, le=12,
                            description="Number of months to return"),
    db: Session = Depends(get_db)
) -> PaginatedWinsResponse:
    """Get wins paginated by months for lazy loading."""
    wins, months, has_more, total_months = get_wins_by_months(
        db, month_offset, num_months)
    return PaginatedWinsResponse(
        wins=wins,
        months=months,
        has_more=has_more,
        total_months=total_months
    )


@router.get("/query")
async def search_wins_endpoint(
    q: str = Query(description="Search query string"),
    db: Session = Depends(get_db)
) -> WinsSearchResponse:
    """Search wins by title, union name, summary, or URL."""
    results = search_wins(db, q)
    return WinsSearchResponse(
        wins=results,
        query=q,
        total=len(results)
    )


@router.put("/{win_id}")
async def update_win_endpoint(
    win_id: int,
    update_data: UpdateWinRequest,
    db: Session = Depends(get_db)
) -> UnionWin:
    """Update an existing win by ID."""
    updated_win = update_win(db, win_id, update_data)
    if not updated_win:
        raise HTTPException(status_code=404, detail="Win not found")
    return updated_win
