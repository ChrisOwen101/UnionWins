"""
Admin API routes for API key management.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database import get_db
from src.models import ApiKeyDB, NewsletterSubscriptionDB
from src.auth import verify_admin_password, generate_api_key, hash_api_key
from src.services.email_service import preview_newsletter_email


router = APIRouter(prefix="/api/admin", tags=["admin"])


class VerifyPasswordRequest(BaseModel):
    """Schema for password verification request."""
    password: str


class VerifyPasswordResponse(BaseModel):
    """Schema for password verification response."""
    valid: bool


class CreateApiKeyRequest(BaseModel):
    """Schema for creating a new API key."""
    name: str
    email: str
    description: str | None = None


class ApiKeyResponse(BaseModel):
    """Schema for API key response (without the actual key)."""
    id: int
    name: str
    email: str
    description: str | None
    is_active: bool
    created_at: str
    last_used_at: str | None


class ApiKeyCreatedResponse(BaseModel):
    """Schema for newly created API key (includes the actual key)."""
    id: int
    name: str
    email: str
    description: str | None
    api_key: str  # Only returned once on creation
    created_at: str


class ToggleApiKeyRequest(BaseModel):
    """Schema for toggling API key status."""
    is_active: bool


class NewsletterSubscriberResponse(BaseModel):
    """Schema for newsletter subscriber response."""
    id: int
    email: str
    name: str | None
    frequency: str
    is_active: bool
    created_at: str
    updated_at: str


@router.post("/verify-password")
async def verify_password(request: VerifyPasswordRequest) -> VerifyPasswordResponse:
    """Verify if the provided admin password is correct."""
    from src.config import ADMIN_PASSWORD
    return VerifyPasswordResponse(valid=request.password == ADMIN_PASSWORD)


@router.get("/api-keys")
async def list_api_keys(
    _: bool = Depends(verify_admin_password),
    db: Session = Depends(get_db)
) -> list[ApiKeyResponse]:
    """List all API keys (admin only)."""
    api_keys = db.query(ApiKeyDB).order_by(ApiKeyDB.created_at.desc()).all()
    return [
        ApiKeyResponse(
            id=key.id,
            name=key.name,
            email=key.email,
            description=key.description,
            is_active=key.is_active,
            created_at=key.created_at.isoformat() if key.created_at else "",
            last_used_at=key.last_used_at.isoformat() if key.last_used_at else None,
        )
        for key in api_keys
    ]


@router.post("/api-keys")
async def create_api_key(
    request: CreateApiKeyRequest,
    _: bool = Depends(verify_admin_password),
    db: Session = Depends(get_db)
) -> ApiKeyCreatedResponse:
    """Create a new API key (admin only)."""
    # Generate the API key
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)

    # Create database record
    api_key_record = ApiKeyDB(
        name=request.name,
        email=request.email,
        description=request.description,
        key_hash=key_hash,
        is_active=True,
    )
    db.add(api_key_record)
    db.commit()
    db.refresh(api_key_record)

    return ApiKeyCreatedResponse(
        id=api_key_record.id,
        name=api_key_record.name,
        email=api_key_record.email,
        description=api_key_record.description,
        api_key=api_key,  # Return the plain key only once
        created_at=api_key_record.created_at.isoformat() if api_key_record.created_at else "",
    )


@router.patch("/api-keys/{key_id}")
async def toggle_api_key(
    key_id: int,
    request: ToggleApiKeyRequest,
    _: bool = Depends(verify_admin_password),
    db: Session = Depends(get_db)
) -> ApiKeyResponse:
    """Toggle API key active status (admin only)."""
    api_key = db.query(ApiKeyDB).filter(ApiKeyDB.id == key_id).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key.is_active = request.is_active
    db.commit()
    db.refresh(api_key)

    return ApiKeyResponse(
        id=api_key.id,
        name=api_key.name,
        email=api_key.email,
        description=api_key.description,
        is_active=api_key.is_active,
        created_at=api_key.created_at.isoformat() if api_key.created_at else "",
        last_used_at=api_key.last_used_at.isoformat() if api_key.last_used_at else None,
    )


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: int,
    _: bool = Depends(verify_admin_password),
    db: Session = Depends(get_db)
) -> dict:
    """Delete an API key (admin only)."""
    api_key = db.query(ApiKeyDB).filter(ApiKeyDB.id == key_id).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    db.delete(api_key)
    db.commit()

    return {"message": "API key deleted successfully", "id": key_id}


@router.get("/newsletter-subscribers")
async def list_newsletter_subscribers(
    _: bool = Depends(verify_admin_password),
    db: Session = Depends(get_db)
) -> list[NewsletterSubscriberResponse]:
    """List all newsletter subscribers (admin only)."""
    subscribers = db.query(NewsletterSubscriptionDB).order_by(
        NewsletterSubscriptionDB.created_at.desc()
    ).all()
    return [
        NewsletterSubscriberResponse(
            id=sub.id,
            email=sub.email,
            name=sub.name,
            frequency=sub.frequency,
            is_active=bool(sub.is_active),
            created_at=sub.created_at.isoformat() if sub.created_at else "",
            updated_at=sub.updated_at.isoformat() if sub.updated_at else "",
        )
        for sub in subscribers
    ]


@router.delete("/newsletter-subscribers/{subscriber_id}")
async def delete_newsletter_subscriber(
    subscriber_id: int,
    _: bool = Depends(verify_admin_password),
    db: Session = Depends(get_db)
) -> dict:
    """Delete a newsletter subscriber (admin only)."""
    subscriber = db.query(NewsletterSubscriptionDB).filter(
        NewsletterSubscriptionDB.id == subscriber_id
    ).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    db.delete(subscriber)
    db.commit()

    return {"message": "Subscriber deleted successfully", "id": subscriber_id}


@router.get("/newsletter-preview/{subscriber_id}", response_class=HTMLResponse)
async def preview_newsletter(
    subscriber_id: int,
    _: bool = Depends(verify_admin_password),
    db: Session = Depends(get_db)
) -> str:
    """Preview newsletter email for a specific subscriber (admin only)."""
    subscriber = db.query(NewsletterSubscriptionDB).filter(
        NewsletterSubscriptionDB.id == subscriber_id
    ).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    html = preview_newsletter_email(
        subscriber.email,
        subscriber.name,
        subscriber.frequency,
        db
    )
    return html
