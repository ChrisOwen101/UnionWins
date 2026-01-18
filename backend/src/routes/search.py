"""
API routes for search endpoints.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import SearchRequest, SearchResponse, SearchRequestStatus
from src.services.search_service import calculate_date_range, create_search_request
from src.models import SearchRequestDB

router = APIRouter(prefix="/api/wins", tags=["search"])


@router.post("/search")
async def search_wins(request: SearchRequest, db: Session = Depends(get_db)) -> SearchResponse:
    """
    Queue a search for new trade What Have Unions Done For Us.
    The actual processing happens in the background polling thread.

    Args:
        request: SearchRequest containing optional date parameter (YYYY-MM-DD format)
                 and days parameter (default: 7)
        db: Database session
    """
    try:
        print("🔍 Queuing new search request...")

        # Calculate date range: if date provided, use it as end date; otherwise use current date
        if request.date:
            end_date = datetime.strptime(request.date, "%Y-%m-%d")
            start_date = end_date - timedelta(days=request.days)
            date_range = (
                f"{start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"
            )
        else:
            _, _, date_range = calculate_date_range(days=request.days)

        # Create a search request in the database
        search_request = create_search_request(db, date_range)

        print(
            f"✅ Search request {search_request.id} queued for background processing"
        )

        return SearchResponse(
            success=True,
            message="Search queued for background processing",
            searched=datetime.now().isoformat(),
            newWinsFound=0,
            note=f"Search request for {date_range} has been queued. Results will be processed in the background."
        )

    except Exception as e:
        print(f"Search error: {e}")
        import traceback
        traceback.print_exc()
        return SearchResponse(
            success=False,
            message="Search failed",
            searched=datetime.now().isoformat(),
            newWinsFound=0,
            note=f"Error: {str(e)}"
        )


@router.get("/search/status")
async def get_search_status(db: Session = Depends(get_db)) -> list[SearchRequestStatus]:
    """
    Get the status of recent search requests.
    Returns the last 10 search requests ordered by most recent first.

    Args:
        db: Database session
    """
    try:
        # Get the last 10 search requests
        search_requests = (
            db.query(SearchRequestDB)
            .order_by(SearchRequestDB.created_at.desc())
            .limit(10)
            .all()
        )

        return [
            SearchRequestStatus(
                id=req.id,
                status=req.status,
                date_range=req.date_range,
                new_wins_found=req.new_wins_found,
                error_message=req.error_message,
                created_at=req.created_at.isoformat(),
                updated_at=req.updated_at.isoformat(),
            )
            for req in search_requests
        ]
    except Exception as e:
        print(f"Error fetching search status: {e}")
        import traceback
        traceback.print_exc()
        return []
