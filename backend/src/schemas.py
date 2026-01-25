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
    win_types: str | None  # Comma-separated list of up to 2 types
    date: str
    url: str
    summary: str


class PendingWin(BaseModel):
    """Schema for a pending win submission."""
    id: int
    title: str
    union_name: str | None
    emoji: str | None
    win_types: str | None  # Comma-separated list of up to 2 types
    date: str
    url: str
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


class UpdateWinRequest(BaseModel):
    """Schema for updating an existing win."""
    title: str | None = None
    union_name: str | None = None
    emoji: str | None = None
    win_types: str | None = None  # Comma-separated list of up to 2 types
    date: str | None = None
    url: str | None = None
    summary: str | None = None


class PaginatedWinsResponse(BaseModel):
    """Schema for paginated wins response."""
    wins: list[UnionWin]
    months: list[str]
    has_more: bool
    total_months: int


class WinsSearchResponse(BaseModel):
    """Schema for wins search response."""
    wins: list[UnionWin]
    query: str
    total: int


class SearchRequest(BaseModel):
    """Schema for search request with optional date parameter."""
    date: str | None = None  # Optional date in format YYYY-MM-DD
    days: int = 7  # Number of days to search back (default: 7)


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


class NewsletterSubscribeRequest(BaseModel):
    """Schema for newsletter subscription request."""
    email: str
    name: str | None = None
    frequency: str = "weekly"  # 'daily', 'weekly', 'monthly'


class NewsletterSubscribeResponse(BaseModel):
    """Schema for newsletter subscription response."""
    success: bool
    message: str
