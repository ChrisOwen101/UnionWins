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
    image = Column(String, nullable=False)
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
