"""
Pydantic schemas for request/response models.
"""
from pydantic import BaseModel


class UnionWin(BaseModel):
    """Schema for a union win response."""
    id: int
    title: str
    union_name: str | None
    emoji: str | None
    date: str
    url: str
    image: str
    summary: str


class PendingWin(BaseModel):
    """Schema for a pending win submission."""
    id: int
    title: str
    union_name: str | None
    emoji: str | None
    date: str
    url: str
    image: str
    summary: str
    status: str
    submitted_by: str | None


class SubmitWinRequest(BaseModel):
    """Schema for submitting a new win URL."""
    url: str
    submitted_by: str | None = None


class ReviewWinRequest(BaseModel):
    """Schema for admin review action."""
    action: str  # 'approve' or 'reject'


class SearchRequest(BaseModel):
    """Schema for search request with optional date parameter."""
    date: str | None = None  # Optional date in format YYYY-MM-DD


class SearchResponse(BaseModel):
    """Schema for search operation response."""
    success: bool
    message: str
    searched: str
    newWinsFound: int
    note: str


class SearchRequestStatus(BaseModel):
    """Schema for search request status."""
    id: int
    status: str
    date_range: str
    new_wins_found: int
    error_message: str | None
    created_at: str
    updated_at: str
