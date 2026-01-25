#!/usr/bin/env python3
"""
Script to clean up union names in the database.
- Ensures all unions have correct canonical names
- Handles deduplication (e.g., Unite vs Unite the Union)
- Reports on any unions not in the canonical list
"""
import sys
from pathlib import Path

# Add backend to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from src.models import UnionWinDB, UK_UNIONS
from src.database import SessionLocal
from sqlalchemy import func


# Use canonical list from models
CANONICAL_UNIONS = UK_UNIONS

# Mapping of variations to canonical names
# This handles common variations and misspellings
UNION_NAME_MAPPING = {
    # Unite variations
    "Unite": "Unite the Union",
    "Unite!": "Unite the Union",
    "unite the union": "Unite the Union",
    "unite": "Unite the Union",
    
    # Unison variations
    "unison": "Unison",
    "UNISON": "Unison",
    "UNISON (Northern Ireland)": "Unison",
    
    # GMB variations
    "gmb": "GMB",
    "Gmb": "GMB",
    "GMB (union)": "GMB",
    "GMB Union": "GMB",
    
    # RMT variations
    "RMT": "National Union of Rail, Maritime and Transport Workers (RMT)",
    "rmt": "National Union of Rail, Maritime and Transport Workers (RMT)",
    "RMT (Rail, Maritime & Transport Workers)": "National Union of Rail, Maritime and Transport Workers (RMT)",
    "RMT (Rail, Maritime and Transport Union)": "National Union of Rail, Maritime and Transport Workers (RMT)",
    
    # NEU variations
    "NEU": "National Education Union (NEU)",
    "neu": "National Education Union (NEU)",
    "National Education Union": "National Education Union (NEU)",
    
    # CWU variations
    "CWU": "Communication Workers Union (CWU)",
    "cwu": "Communication Workers Union (CWU)",
    "Communication Workers Union": "Communication Workers Union (CWU)",
    
    # BMA variations
    "BMA": "British Medical Association (BMA)",
    "bma": "British Medical Association (BMA)",
    "British Medical Association": "British Medical Association (BMA)",
    "BMA Cymru Wales": "British Medical Association (BMA)",
    
    # UCU variations
    "UCU": "University and College Union (UCU)",
    "ucu": "University and College Union (UCU)",
    "University and College Union": "University and College Union (UCU)",
    "UCU (University and College Union)": "University and College Union (UCU)",
    
    # PCS variations
    "PCS": "Public and Commercial Services Union (PCS)",
    "pcs": "Public and Commercial Services Union (PCS)",
    "Public and Commercial Services Union": "Public and Commercial Services Union (PCS)",
    
    # NASUWT variations
    "NASUWT": "National Association of Schoolmasters Union of Women Teachers (NASUWT)",
    "nasuwt": "National Association of Schoolmasters Union of Women Teachers (NASUWT)",
    "NASUWT (Northern Ireland)": "National Association of Schoolmasters Union of Women Teachers (NASUWT)",
    
    # FBU variations
    "FBU": "Fire Brigades Union (FBU)",
    "fbu": "Fire Brigades Union (FBU)",
    "Fire Brigades Union": "Fire Brigades Union (FBU)",
    
    # NUJ variations
    "NUJ": "National Union of Journalists (NUJ)",
    "nuj": "National Union of Journalists (NUJ)",
    "National Union of Journalists": "National Union of Journalists (NUJ)",
    
    # USDAW variations
    "USDAW": "Union of Shop, Distributive and Allied Workers (USDAW)",
    "usdaw": "Union of Shop, Distributive and Allied Workers (USDAW)",
    "Usdaw": "Union of Shop, Distributive and Allied Workers (USDAW)",
    
    # ASLEF variations
    "ASLEF": "Associated Society of Locomotive Engineers and Firemen (ASLEF)",
    "aslef": "Associated Society of Locomotive Engineers and Firemen (ASLEF)",
    "Aslef": "Associated Society of Locomotive Engineers and Firemen (ASLEF)",
    
    # TUC variations
    "TUC": "Trades Union Congress (TUC)",
    "tuc": "Trades Union Congress (TUC)",
    "Trades Union Congress": "Trades Union Congress (TUC)",
    "TUC (Trades Union Congress)": "Trades Union Congress (TUC)",
    
    # IWGB variations
    "IWGB": "Independent Workers' Union of Great Britain (IWGB)",
    "iwgb": "Independent Workers' Union of Great Britain (IWGB)",
    "Independent Workers' Union of Great Britain (IWGB)": "Independent Workers' Union of Great Britain (IWGB)",  # curly apostrophe version
    
    # UVW variations
    "UVW": "United Voices of the World (UVW)",
    "uvw": "United Voices of the World (UVW)",
    
    # RCN variations
    "RCN": "Royal College of Nursing (RCN)",
    "rcn": "Royal College of Nursing (RCN)",
    "Royal College of Nursing": "Royal College of Nursing (RCN)",
    
    # RCM variations
    "Royal College of Midwives": "Royal College of Midwives (RCM)",
    
    # SoR variations
    "SoR": "Society of Radiographers (SoR)",
    "sor": "Society of Radiographers (SoR)",
    
    # TSSA variations
    "TSSA": "Transport Salaried Staffs' Association (TSSA)",
    "tssa": "Transport Salaried Staffs' Association (TSSA)",
    
    # MU variations
    "Musicians' Union": "Musicians' Union (MU)",
    "Musicians' Union": "Musicians' Union (MU)",
    
    # EIS variations
    "EIS": "Educational Institute of Scotland (EIS)",
    "eis": "Educational Institute of Scotland (EIS)",
    
    # Prospect variations
    "prospect": "Prospect",
    "PROSPECT": "Prospect",
    
    # Equity variations
    "equity": "Equity",
    "EQUITY": "Equity",
    
    # Community variations
    "community": "Community",
    "COMMUNITY": "Community",
    
    # Joint campaigns - keep first union listed as primary
    "GMB & Unite": "GMB",
    "GMB & Unite the Union": "GMB",
    "GMB (joint with Unison and Unite)": "GMB",
    "Unison & Unite": "Unison",
    "Unison and GMB": "Unison",
    "Unite the Union and GMB": "Unite the Union",
    "Unite the Union and UNISON": "Unite the Union",
}


def get_canonical_name(union_name: str) -> str:
    """
    Get the canonical name for a union, handling variations and deduplication.
    
    Args:
        union_name: The union name from the database
        
    Returns:
        The canonical union name
    """
    if not union_name:
        return union_name
    
    # First check if it's already in mapping
    if union_name in UNION_NAME_MAPPING:
        return UNION_NAME_MAPPING[union_name]
    
    # Check if it's already canonical
    if union_name in CANONICAL_UNIONS:
        return union_name
    
    # Check for case-insensitive match with canonical list
    for canonical in CANONICAL_UNIONS:
        if union_name.lower() == canonical.lower():
            return canonical
    
    # Return as-is if not found (will be flagged later)
    return union_name


def clean_union_names(dry_run: bool = True):
    """
    Clean up union names in the database.
    
    Args:
        dry_run: If True, only report changes without making them
    """
    db = SessionLocal()
    
    try:
        # Get all distinct union names
        unions = db.query(
            UnionWinDB.union_name, 
            func.count(UnionWinDB.id)
        ).group_by(
            UnionWinDB.union_name
        ).order_by(
            UnionWinDB.union_name
        ).all()
        
        print("=" * 80)
        print("UNION NAME CLEANUP REPORT")
        print("=" * 80)
        print(f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE (changes will be committed)'}")
        print("=" * 80)
        print()
        
        # Track statistics
        total_unions = len(unions)
        needs_update = 0
        unknown_unions = []
        updates_by_union = {}
        needs_manual_review = []
        
        print(f"Found {total_unions} distinct union names in database:")
        print()
        
        for union_name, count in unions:
            # Handle empty/null union names
            if not union_name or union_name.strip() == "":
                needs_manual_review.append(("(empty)", count))
                print(f"  ⚠️  Empty union name ({count} wins) - NEEDS MANUAL REVIEW")
                continue
            
            # Flag non-union entities
            if union_name in ["Department for Business and Trade"]:
                needs_manual_review.append((union_name, count))
                print(f"  ⚠️  '{union_name}' ({count} wins) - NOT A UNION, NEEDS MANUAL REVIEW")
                continue
            
            canonical_name = get_canonical_name(union_name)
            
            if union_name != canonical_name:
                needs_update += 1
                print(f"  🔄 '{union_name}' ({count} wins) → '{canonical_name}'")
                updates_by_union[union_name] = canonical_name
            elif canonical_name not in CANONICAL_UNIONS:
                unknown_unions.append((union_name, count))
                print(f"  ❓ '{union_name}' ({count} wins) - NOT IN CANONICAL LIST")
            else:
                print(f"  ✅ '{union_name}' ({count} wins)")
        
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total distinct unions: {total_unions}")
        print(f"Unions needing update: {needs_update}")
        print(f"Unknown unions (not in canonical list): {len(unknown_unions)}")
        print(f"Entries needing manual review: {len(needs_manual_review)}")
        print()
        
        if needs_manual_review:
            print("Entries that need manual review:")
            for union_name, count in needs_manual_review:
                print(f"  - {union_name} ({count} wins)")
            print()
        
        if unknown_unions:
            print("Unknown unions that should be added to canonical list:")
            for union_name, count in unknown_unions:
                print(f"  - {union_name} ({count} wins)")
            print()
        
        # Perform updates if not dry run
        if not dry_run and needs_update > 0:
            print("=" * 80)
            print("APPLYING UPDATES")
            print("=" * 80)
            
            total_updated = 0
            for old_name, new_name in updates_by_union.items():
                wins = db.query(UnionWinDB).filter(
                    UnionWinDB.union_name == old_name
                ).all()
                
                count = len(wins)
                print(f"Updating {count} wins: '{old_name}' → '{new_name}'")
                
                for win in wins:
                    win.union_name = new_name
                    total_updated += 1
            
            db.commit()
            print()
            print(f"✅ Successfully updated {total_updated} wins")
            print()
        elif dry_run and needs_update > 0:
            print("To apply these changes, run with --apply flag")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up union names in the database")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (default is dry-run mode)"
    )
    
    args = parser.parse_args()
    
    clean_union_names(dry_run=not args.apply)
