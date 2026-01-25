#!/usr/bin/env python3
import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0] + "/backend")

from src.models import UnionWinDB
from src.database import SessionLocal

# Check what's in the database
db = SessionLocal()
wins = db.query(UnionWinDB).filter(UnionWinDB.union_name.like('%Independent%')).all()
print(f"Found {len(wins)} IWGB wins")
if wins:
    db_name = wins[0].union_name
    print(f"Database name: {repr(db_name)}")
    print(f"Database bytes: {db_name.encode('utf-8')}")
    
    # Find the apostrophe character
    for i, char in enumerate(db_name):
        if char in ["'", "'", "'"]:
            print(f"\nApostrophe at position {i}: {repr(char)} (U+{ord(char):04X})")
    
db.close()
