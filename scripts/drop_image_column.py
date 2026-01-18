#!/usr/bin/env python3
"""
Script to drop the image column from the union_wins table.
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import text
from src.database import engine


def drop_image_column():
    """Drop the image column from union_wins table."""
    try:
        with engine.connect() as connection:
            print("🔧 Dropping image column from union_wins table...")
            
            # Drop the image column
            connection.execute(text(
                "ALTER TABLE union_wins DROP COLUMN IF EXISTS image"
            ))
            connection.commit()
            
            print("✅ Successfully dropped image column from database")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    drop_image_column()
