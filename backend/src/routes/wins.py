"""
API routes for What Have Unions Done For Us endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import UnionWin, UpdateWinRequest, PaginatedWinsResponse, WinsSearchResponse
from src.services.win_service import (
    get_all_wins_sorted,
    update_win,
    get_wins_by_months,
    search_wins,
    delete_win,
)
from src.auth import verify_api_key, verify_admin_password

router = APIRouter(prefix="/api/wins", tags=["wins"])


def is_browser_request(request: Request) -> bool:
    """Check if request is from a browser (has Accept header with text/html)."""
    accept = request.headers.get("accept", "")
    referer = request.headers.get("referer", "")
    # Browser requests typically accept text/html or come from our frontend
    return "text/html" in accept or referer != ""


@router.get("")
async def get_wins(
    request: Request,
    db: Session = Depends(get_db)
) -> list[UnionWin]:
    """
    Get all What Have Unions Done For Us sorted by date in reverse chronological order.
    Requires API key for external API access. Browser requests are allowed without API key.
    """
    # Check if this is an external API request (not from browser)
    if not is_browser_request(request):
        # Require API key for external requests
        api_key = request.headers.get("X-API-Key")
        if api_key:
            verify_api_key(api_key, db)
        else:
            raise HTTPException(
                status_code=401,
                detail="API key required. Include X-API-Key header. Get your key at /api-signup"
            )
    return get_all_wins_sorted(db)


@router.get("/paginated")
async def get_wins_paginated(
    request: Request,
    month_offset: int = Query(
        default=0, ge=0, description="Number of months to skip"),
    num_months: int = Query(default=3, ge=1, le=12,
                            description="Number of months to return"),
    db: Session = Depends(get_db)
) -> PaginatedWinsResponse:
    """
    Get wins paginated by months for lazy loading.
    Requires API key for external API access.
    """
    if not is_browser_request(request):
        api_key = request.headers.get("X-API-Key")
        if api_key:
            verify_api_key(api_key, db)
        else:
            raise HTTPException(
                status_code=401,
                detail="API key required. Include X-API-Key header. Get your key at /api-signup"
            )
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
    request: Request,
    q: str = Query(description="Search query string"),
    db: Session = Depends(get_db)
) -> WinsSearchResponse:
    """
    Search wins by title, union name, summary, or URL.
    Requires API key for external API access.
    """
    if not is_browser_request(request):
        api_key = request.headers.get("X-API-Key")
        if api_key:
            verify_api_key(api_key, db)
        else:
            raise HTTPException(
                status_code=401,
                detail="API key required. Include X-API-Key header. Get your key at /api-signup"
            )
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
    _: bool = Depends(verify_admin_password),
    db: Session = Depends(get_db)
) -> UnionWin:
    """Update an existing win by ID. Requires admin password."""
    updated_win = update_win(db, win_id, update_data)
    if not updated_win:
        raise HTTPException(status_code=404, detail="Win not found")
    return updated_win


@router.delete("/{win_id}")
async def delete_win_endpoint(
    win_id: int,
    _: bool = Depends(verify_admin_password),
    db: Session = Depends(get_db)
) -> dict:
    """Delete a win by ID. Requires admin password."""
    success = delete_win(db, win_id)
    if not success:
        raise HTTPException(status_code=404, detail="Win not found")
    return {"message": "Win deleted successfully", "id": win_id}
