"""
Database models for UnionWins application.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class UnionWinDB(Base):
    """Model representing a union victory or win."""
    __tablename__ = "union_wins"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    union_name = Column(String, nullable=True)
    emoji = Column(String, nullable=True)
    date = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True, index=True)
    summary = Column(Text, nullable=False)
    # Status: 'approved' (default for admin-added), 'pending' (user submission), 'rejected'
    status = Column(String, nullable=False, default="approved")
    # Who submitted (optional for user submissions)
    submitted_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class SearchRequestDB(Base):
    """Model for tracking background search requests."""
    __tablename__ = "search_requests"

    id = Column(Integer, primary_key=True, index=True)
    # pending, processing, completed, failed
    status = Column(String, nullable=False, default="pending")
    # OpenAI response ID for polling
    response_id = Column(String, nullable=True)
    date_range = Column(String, nullable=False)
    new_wins_found = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ApiKeyDB(Base):
    """Model for storing API keys."""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    key_hash = Column(String, nullable=False, unique=True, index=True)
    # Using Integer for SQLite compatibility
    is_active = Column(Integer, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_used_at = Column(DateTime, nullable=True)


class NewsletterSubscriptionDB(Base):
    """Model for newsletter subscriptions."""
    __tablename__ = "newsletter_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=True)
    # Frequency: 'daily', 'weekly', 'monthly'
    frequency = Column(String, nullable=False, default="weekly")
    # Using Integer for SQLite compatibility (0 = False, 1 = True)
    is_active = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_email_sent_at = Column(DateTime, nullable=True)
