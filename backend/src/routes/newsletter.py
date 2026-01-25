"""
Newsletter subscription routes for the UnionWins API.
"""
import re
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database import get_db
from src.models import NewsletterSubscriptionDB
from src.schemas import NewsletterSubscribeRequest, NewsletterSubscribeResponse

router = APIRouter(prefix="/api/newsletter", tags=["newsletter"])


def is_valid_email(email: str) -> bool:
    """Validate email format using regex."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_frequency(frequency: str) -> bool:
    """Validate frequency value."""
    return frequency in ("daily", "weekly", "monthly")


@router.post("/subscribe", response_model=NewsletterSubscribeResponse)
async def subscribe_to_newsletter(
    request: NewsletterSubscribeRequest,
    db: Session = Depends(get_db)
):
    """
    Subscribe to the newsletter with email, optional name, and frequency preference.
    """
    # Validate email format
    email = request.email.strip().lower()
    if not email or not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email address")

    # Validate frequency
    frequency = request.frequency.strip().lower()
    if not is_valid_frequency(frequency):
        raise HTTPException(
            status_code=400,
            detail="Invalid frequency. Must be 'daily', 'weekly', or 'monthly'"
        )

    # Sanitize name if provided
    name = request.name.strip() if request.name else None

    try:
        # Check if email already exists
        existing = db.query(NewsletterSubscriptionDB).filter(
            NewsletterSubscriptionDB.email == email
        ).first()

        if existing:
            # Update existing subscription
            existing.frequency = frequency
            existing.is_active = 1
            if name:
                existing.name = name
            db.commit()
            return NewsletterSubscribeResponse(
                success=True,
                message="Your subscription has been updated!"
            )

        # Create new subscription
        subscription = NewsletterSubscriptionDB(
            email=email,
            name=name,
            frequency=frequency,
            is_active=1
        )
        db.add(subscription)
        db.commit()

        return NewsletterSubscribeResponse(
            success=True,
            message="You've been subscribed to union wins updates!"
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Unable to process subscription. Please try again."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unsubscribe", response_model=NewsletterSubscribeResponse)
async def unsubscribe_from_newsletter(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Unsubscribe from the newsletter.
    """
    email = email.strip().lower()
    if not email or not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email address")

    try:
        subscription = db.query(NewsletterSubscriptionDB).filter(
            NewsletterSubscriptionDB.email == email
        ).first()

        if not subscription:
            return NewsletterSubscribeResponse(
                success=True,
                message="Email not found in our subscription list."
            )

        subscription.is_active = 0
        db.commit()

        return NewsletterSubscribeResponse(
            success=True,
            message="You've been unsubscribed from union wins updates."
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
