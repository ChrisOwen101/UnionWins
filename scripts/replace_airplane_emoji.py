#!/usr/bin/env python3
"""
Script to replace all "✈" emojis with "✈️" in the database.
"""
import sys
from pathlib import Path

# Add backend to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from src.database import SessionLocal
from src.models import UnionWinDB


def replace_emoji():
    """Replace all ✈ emojis with ✈️ in the database."""
    db = SessionLocal()
    
    try:
        # Query for all wins with the old airplane emoji
        wins_to_update = db.query(UnionWinDB).filter(
            UnionWinDB.emoji == "✈"
        ).all()
        
        if not wins_to_update:
            print("✅ No wins found with ✈ emoji!")
            return
        
        print(f"🔍 Found {len(wins_to_update)} wins with ✈ emoji")
        print("-" * 60)
        
        for win in wins_to_update:
            win.emoji = "✈️"
            db.commit()
            print(f"✅ Updated: {win.title[:50]}")
        
        print("-" * 60)
        print(f"✨ Successfully updated {len(wins_to_update)} emojis!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    replace_emoji()
