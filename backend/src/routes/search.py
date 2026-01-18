"""
API routes for search endpoints.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import SearchRequest, SearchResponse
from src.services.search_service import calculate_date_range, create_search_request

router = APIRouter(prefix="/api/wins", tags=["search"])


@router.post("/search")
async def search_wins(request: SearchRequest, db: Session = Depends(get_db)) -> SearchResponse:
    """
    Queue a search for new trade union wins.
    The actual processing happens in the background polling thread.

    Args:
        request: SearchRequest containing optional date parameter (YYYY-MM-DD format)
        db: Database session
    """
    try:
        print("🔍 Queuing new search request...")

        # Calculate date range: if date provided, use it as end date; otherwise use current date
        if request.date:
            end_date = datetime.strptime(request.date, "%Y-%m-%d")
            start_date = end_date - timedelta(days=7)
            date_range = (
                f"{start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"
            )
        else:
            _, _, date_range = calculate_date_range(days=7)

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
