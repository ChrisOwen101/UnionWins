"""
API routes for user submissions of What Have Unions Done For Us.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import SubmitWinRequest, PendingWin, ReviewWinRequest
from src.services.submission_service import (
    create_submission,
    get_pending_submissions,
    approve_submission,
    reject_submission
)
from src.auth import verify_admin_password

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


@router.post("")
async def submit_win(
    request: SubmitWinRequest,
    db: Session = Depends(get_db)
) -> dict:
    """
    Submit a URL for a union win.
    The URL will be scraped with OpenAI and queued for admin review.
    """
    try:
        submission = create_submission(db, request.url, request.submitted_by)
        return {
            "success": True,
            "message": "Your submission has been received and will be reviewed by an admin.",
            "id": submission.id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500, detail="Failed to process submission")


@router.get("/pending")
async def get_pending(
    _: bool = Depends(verify_admin_password),
    db: Session = Depends(get_db)
) -> list[PendingWin]:
    """Get all pending submissions for admin review. Requires admin password."""
    submissions = get_pending_submissions(db)
    return [
        PendingWin(
            id=s.id,
            title=s.title,
            union_name=s.union_name,
            emoji=s.emoji,
            win_types=s.win_types,
            date=s.date,
            url=s.url,
            summary=s.summary,
            status=s.status,
            submitted_by=s.submitted_by
        )
        for s in submissions
    ]


@router.post("/{submission_id}/review")
async def review_submission(
    submission_id: int,
    request: ReviewWinRequest,
    _: bool = Depends(verify_admin_password),
    db: Session = Depends(get_db)
) -> dict:
    """Approve or reject a pending submission. Requires admin password."""""
    try:
        if request.action == "approve":
            submission = approve_submission(db, submission_id)
            return {
                "success": True,
                "message": "Submission approved and published",
                "id": submission.id
            }
        elif request.action == "reject":
            submission = reject_submission(db, submission_id)
            return {
                "success": True,
                "message": "Submission rejected",
                "id": submission.id
            }
        else:
            raise HTTPException(
                status_code=400, detail="Invalid action. Must be 'approve' or 'reject'")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to process review")
