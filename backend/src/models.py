"""
Database models for UnionWins application.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


# Define valid win types as a constant for reference
WIN_TYPES = [
    "Pay Rise",
    "Recognition",
    "Strike Action",
    "Working Conditions",
    "Job Security",
    "Benefits",
    "Health & Safety",
    "Equality",
    "Legal Victory",
    "Organising",
    "Other",
]


# Canonical list of major UK trade unions
UK_UNIONS = [
    "Accord",
    "Advance",
    "Aegis the Union",
    "Artists' Union England (AUE)",
    "Associated Society of Locomotive Engineers and Firemen (ASLEF)",
    "Association of Educational Psychologists (AEP)",
    "Association of Flight Attendants (AFA)",
    "Association of Headteachers and Deputes in Scotland (AHDS)",
    "Association of School and College Leaders (ASCL)",
    "Bakers, Food and Allied Workers Union (BFAWU)",
    "British Airline Pilots' Association (BALPA)",
    "British Association of Dental Nurses (BADN)",
    "British Association of Occupational Therapists (BAOT)",
    "British Dietetic Association (BDA)",
    "British Medical Association (BMA)",
    "British Orthoptic Society Trade Union (BOSTU)",
    "Chartered Society of Physiotherapy (CSP)",
    "Communication Workers Union (CWU)",
    "Community",
    "Educational Institute of Scotland (EIS)",
    "Equity",
    "FDA",
    "Fire Brigades Union (FBU)",
    "GMB",
    "Hospital Consultants and Specialists Association (HCSA)",
    "Independent Workers' Union of Great Britain (IWGB)",
    "Industrial Workers of the World (IWW)",
    "Musicians' Union (MU)",
    "National Association of Head Teachers (NAHT)",
    "National Association of Probation Officers (NAPO)",
    "National Association of Racing Staff (NARS)",
    "National Association of Schoolmasters Union of Women Teachers (NASUWT)",
    "National Education Union (NEU)",
    "National House Building Council Staff Association (NHBCSA)",
    "National Society for Education in Art and Design (NSEAD)",
    "National Union of Journalists (NUJ)",
    "National Union of Mineworkers (NUM)",
    "National Union of Professional Foster Carers (NUPFC)",
    "National Union of Rail, Maritime and Transport Workers (RMT)",
    "Nationwide Group Staff Union (NGSU)",
    "Nautilus UK",
    "Prison Officers Association (POA)",
    "Professional Footballers' Association (PFA)",
    "Prospect",
    "Public and Commercial Services Union (PCS)",
    "Royal College of Midwives (RCM)",
    "Royal College of Nursing (RCN)",
    "Royal College of Podiatry (RCPod)",
    "Society of Radiographers (SoR)",
    "Trades Union Congress (TUC)",
    "Transport Salaried Staffs' Association (TSSA)",
    "Undeb Cenedlaethol Athrawon Cymru (UCAC)",
    "Union of Shop, Distributive and Allied Workers (USDAW)",
    "Unison",
    "Unite the Union",
    "United Road Transport Union (URTU)",
    "United Voices of the World (UVW)",
    "University and College Union (UCU)",
    "Writers' Guild of Great Britain (WGGB)",
]


class UnionWinDB(Base):
    """Model representing a union victory or win."""
    __tablename__ = "union_wins"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    union_name = Column(String, nullable=True)
    emoji = Column(String, nullable=True)
    # Types of win from predefined list (up to 2, comma-separated)
    win_types = Column(String, nullable=True, index=True)
    date = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True, index=True)
    summary = Column(Text, nullable=False)
    # JSON array of relevant image URLs from the article (og:image, content images)
    image_urls = Column(Text, nullable=True)
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


class ScrapeSourceDB(Base):
    """Model for managing URLs to scrape."""
    __tablename__ = "scrape_sources"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False, unique=True)
    organization_name = Column(String, nullable=True)
    last_scraped_at = Column(DateTime, nullable=True)
    last_scrape_status = Column(String, nullable=True) # 'success' or 'error'
    last_scrape_error = Column(Text, nullable=True)
    # Using Integer for SQLite compatibility (0 = False, 1 = True)
    is_active = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.now)
