#!/usr/bin/env python3
"""
Script to remove specific union wins from the database.
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from src.database import get_db
from src.models import UnionWinDB


def remove_wins():
    """Remove the specified wins from the database."""
    # Titles to remove
    titles_to_remove = [
        "Unite wins major HSL pay deal after strike action",
        "Unite wins improved pay deal for Tunnock",
        "Arriva bus strikes called off after Unite secures new pay deal",
        "Unite secures wage win worth up to £8,000 for CNOOC offshore workers",
        "Stagecoach bus drivers win inflation-busting pay deal; strikes called off"
    ]
    
    db = next(get_db())
    
    try:
        removed_count = 0
        for title_part in titles_to_remove:
            # Find and delete wins that contain this title
            wins = db.query(UnionWinDB).filter(UnionWinDB.title.contains(title_part)).all()
            if wins:
                for win in wins:
                    print(f"🗑️  Removing: {win.title}")
                    db.delete(win)
                    removed_count += 1
            else:
                print(f"❌ Not found: {title_part}")
        
        # Commit the changes
        db.commit()
        print(f"\n✅ Successfully removed {removed_count} wins from the database")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    remove_wins()
