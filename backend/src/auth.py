"""
Authentication utilities for API key and admin password protection.
"""
import secrets
import hashlib
from datetime import datetime
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from src.config import ADMIN_PASSWORD
from src.database import get_db
from src.models import ApiKeyDB


def generate_api_key() -> str:
    """
    Generate a secure random API key.

    Returns:
        A 32-character hex string API key prefixed with 'uw_'
    """
    return f"uw_{secrets.token_hex(16)}"


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage.

    Args:
        api_key: The plain text API key

    Returns:
        SHA-256 hash of the API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
) -> ApiKeyDB:
    """
    Dependency to verify API key from request header.

    Args:
        x_api_key: API key from X-API-Key header
        db: Database session

    Returns:
        The ApiKeyDB record if valid

    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Include X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Hash the provided key to compare with stored hash
    key_hash = hash_api_key(x_api_key)

    api_key_record = (
        db.query(ApiKeyDB)
        .filter(ApiKeyDB.key_hash == key_hash, ApiKeyDB.is_active)
        .first()
    )

    if not api_key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Update last used timestamp
    api_key_record.last_used_at = datetime.now()
    db.commit()

    return api_key_record


def verify_admin_password(
    x_admin_password: str | None = Header(None, alias="X-Admin-Password"),
) -> bool:
    """
    Dependency to verify admin password from request header.

    Args:
        x_admin_password: Admin password from X-Admin-Password header

    Returns:
        True if valid

    Raises:
        HTTPException: If password is missing or incorrect
    """
    if not x_admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin password required",
        )

    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin password",
        )

    return True


def optional_api_key(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
) -> ApiKeyDB | None:
    """
    Optional API key verification - returns None if no key provided.
    Used for endpoints that work differently for authenticated vs anonymous users.

    Args:
        x_api_key: API key from X-API-Key header
        db: Database session

    Returns:
        The ApiKeyDB record if valid, None if no key provided

    Raises:
        HTTPException: If API key is provided but invalid
    """
    if not x_api_key:
        return None

    return verify_api_key(x_api_key, db)
