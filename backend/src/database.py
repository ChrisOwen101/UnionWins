"""
Database connection and initialization.
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL
from src.models import Base

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database and create tables."""
    inspector = inspect(engine)

    # Check if union_name and emoji columns exist, add them if they don't
    columns = [
        col['name'] for col in inspector.get_columns('union_wins')
    ] if inspector.has_table('union_wins') else []

    if 'union_wins' in inspector.get_table_names():
        with engine.connect() as conn:
            if 'union_name' not in columns:
                # Add the union_name column to existing table
                print("Adding union_name column to union_wins table...")
                conn.execute(
                    text("ALTER TABLE union_wins ADD COLUMN union_name VARCHAR")
                )
                conn.commit()
                print("union_name column added successfully!")

            if 'emoji' not in columns:
                # Add the emoji column to existing table
                print("Adding emoji column to union_wins table...")
                conn.execute(
                    text("ALTER TABLE union_wins ADD COLUMN emoji VARCHAR")
                )
                conn.commit()
                print("emoji column added successfully!")

            # Add unique constraint on url if it doesn't exist
            try:
                constraints = inspector.get_unique_constraints('union_wins')
                url_constraint_exists = any(
                    'url' in constraint.get('column_names', [])
                    for constraint in constraints
                )

                if not url_constraint_exists:
                    conn.execute(
                        text(
                            "CREATE UNIQUE INDEX IF NOT EXISTS ix_union_wins_url ON union_wins (url)")
                    )
                    conn.commit()
            except Exception as e:
                print(
                    f"Note: Could not add unique constraint (may already exist): {e}"
                )

    # Check newsletter_subscriptions table for new columns
    if inspector.has_table('newsletter_subscriptions'):
        newsletter_columns = [
            col['name'] for col in inspector.get_columns('newsletter_subscriptions')
        ]
        with engine.connect() as conn:
            if 'last_email_sent_at' not in newsletter_columns:
                print(
                    "Adding last_email_sent_at column to newsletter_subscriptions table...")
                conn.execute(
                    text(
                        "ALTER TABLE newsletter_subscriptions ADD COLUMN last_email_sent_at TIMESTAMP")
                )
                conn.commit()
                print("last_email_sent_at column added successfully!")

    Base.metadata.create_all(bind=engine)
