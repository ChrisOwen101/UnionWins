#!/usr/bin/env python3
"""
Script to fix remaining edge cases after union name cleanup.
"""
import sys
from pathlib import Path

# Add backend to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from src.models import UnionWinDB
from src.database import SessionLocal


def fix_edge_cases(dry_run: bool = True):
    """
    Fix remaining edge cases after main union name cleanup.
    
    Args:
        dry_run: If True, only report changes without making them
    """
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("EDGE CASE FIXES")
        print("=" * 80)
        print(f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE (changes will be committed)'}")
        print("=" * 80)
        print()
        
        # Fix 1: Delete invalid win with bad URL
        print("1. Invalid win with bad URL:")
        invalid_win = db.query(UnionWinDB).filter(UnionWinDB.id == 298).first()
        if invalid_win:
            print(f"   ID: {invalid_win.id}")
            print(f"   Title: {invalid_win.title}")
            print(f"   URL: {invalid_win.url}")
            print(f"   Action: DELETE")
            if not dry_run:
                db.delete(invalid_win)
                print(f"   ✅ Deleted")
        else:
            print(f"   Not found (may have been deleted already)")
        print()
        
        # Fix 2: Handle Department for Business and Trade entry
        print("2. Department for Business and Trade entry:")
        dept_win = db.query(UnionWinDB).filter(UnionWinDB.id == 77).first()
        if dept_win:
            print(f"   ID: {dept_win.id}")
            print(f"   Title: {dept_win.title}")
            print(f"   URL: {dept_win.url}")
            print(f"   Current union: {dept_win.union_name}")
            print(f"   Action: UPDATE to 'Trades Union Congress (TUC)'")
            print(f"   Reason: Minimum wage enforcement benefits all unions under TUC umbrella")
            if not dry_run:
                dept_win.union_name = "Trades Union Congress (TUC)"
                print(f"   ✅ Updated")
        else:
            print(f"   Not found")
        print()
        
        # Fix 3: Normalize IWGB apostrophes  
        print("3. Normalize IWGB apostrophes:")
        canonical_iwgb = "Independent Workers' Union of Great Britain (IWGB)"
        iwgb_wins = db.query(UnionWinDB).filter(
            UnionWinDB.union_name.like('%Independent Workers%')
        ).all()
        
        updated_count = 0
        for win in iwgb_wins:
            if win.union_name != canonical_iwgb:
                print(f"   ID: {win.id}")
                print(f"   Current: {repr(win.union_name)}")
                print(f"   New: {repr(canonical_iwgb)}")
                if not dry_run:
                    win.union_name = canonical_iwgb
                    updated_count += 1
        
        if iwgb_wins:
            print(f"   {len(iwgb_wins)} IWGB wins found, {len([w for w in iwgb_wins if w.union_name != canonical_iwgb])} need normalization")
            if not dry_run and updated_count > 0:
                print(f"   ✅ Updated {updated_count} wins")
        else:
            print(f"   No IWGB wins found")
        print()
        
        # Commit changes
        if not dry_run:
            db.commit()
            print("=" * 80)
            print("✅ All changes committed successfully")
            print("=" * 80)
        else:
            print("=" * 80)
            print("To apply these changes, run with --apply flag")
            print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix edge cases in union data")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (default is dry-run mode)"
    )
    
    args = parser.parse_args()
    
    fix_edge_cases(dry_run=not args.apply)
