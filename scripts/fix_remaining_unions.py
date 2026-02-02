#!/usr/bin/env python3
"""
Script to fix remaining union names with special Unicode characters.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add the backend to the path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import text
from src.database import engine


def main():
    """Fix remaining special character union names."""
    print("Finding and fixing remaining problematic union names...")
    
    with engine.connect() as conn:
        # Get all union names
        result = conn.execute(text('SELECT DISTINCT union_name FROM union_wins WHERE union_name IS NOT NULL'))
        names = [row[0] for row in result.fetchall()]
        
        for name in names:
            # Check for Musicians' Union variations with curly quotes
            if 'usician' in name.lower():
                canonical = "Musicians' Union (MU)"
                if name != canonical:
                    print(f"Found: {name!r}")
                    print(f"  -> Updating to: {canonical!r}")
                    conn.execute(
                        text("UPDATE union_wins SET union_name = :new WHERE union_name = :old"),
                        {"old": name, "new": canonical}
                    )
            
            # Check for NASUWT variations
            elif 'NASUWT' in name and name != "National Association of Schoolmasters Union of Women Teachers (NASUWT)":
                canonical = "National Association of Schoolmasters Union of Women Teachers (NASUWT)"
                print(f"Found: {name!r}")
                print(f"  -> Updating to: {canonical!r}")
                conn.execute(
                    text("UPDATE union_wins SET union_name = :new WHERE union_name = :old"),
                    {"old": name, "new": canonical}
                )
        
        conn.commit()
    
    # Verify
    print("\nVerifying remaining union names...")
    with engine.connect() as conn:
        result = conn.execute(text('SELECT DISTINCT union_name FROM union_wins ORDER BY union_name'))
        names = [row[0] for row in result.fetchall()]
        print(f"Total unique names: {len(names)}")
        for name in names:
            print(f"  - {name}")


if __name__ == "__main__":
    main()
