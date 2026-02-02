#!/usr/bin/env python3
"""
Script to deduplicate union names in the database.

This script:
1. Fetches all unique union names from the database
2. Maps variants to their canonical forms (from UK_UNIONS)
3. Updates all records with the canonical names
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

# Add the backend to the path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import text
from src.database import engine
from src.models import UK_UNIONS


def normalize_name(name: str) -> str:
    """Normalize a union name for comparison."""
    if not name:
        return ""
    # Lowercase, strip whitespace, normalize quotes and apostrophes
    normalized = name.lower().strip()
    # Replace various quote characters with standard apostrophe
    normalized = normalized.replace("'", "'").replace("'", "'").replace("`", "'")
    normalized = normalized.replace("'", "'").replace(""", "").replace(""", "")
    # Replace en-dash and em-dash with hyphen
    normalized = normalized.replace("–", "-").replace("—", "-")
    # Remove extra spaces
    normalized = " ".join(normalized.split())
    return normalized


def extract_acronym(name: str) -> Optional[str]:
    """Extract acronym from a name like 'Something (ABC)'."""
    if "(" in name and ")" in name:
        start = name.rfind("(")
        end = name.rfind(")")
        if start < end:
            return name[start + 1 : end].strip().upper()
    return None


def build_canonical_lookup() -> dict:
    """Build a lookup table mapping normalized names to canonical names."""
    lookup = {}

    for canonical in UK_UNIONS:
        # Add the full canonical name
        normalized = normalize_name(canonical)
        lookup[normalized] = canonical

        # Add version without acronym
        if "(" in canonical:
            name_without_acronym = canonical[: canonical.rfind("(")].strip()
            lookup[normalize_name(name_without_acronym)] = canonical

        # Add just the acronym
        acronym = extract_acronym(canonical)
        if acronym:
            lookup[acronym.lower()] = canonical

    # Add common variations manually
    manual_mappings = {
        # Musicians' Union variations
        "musicians union": "Musicians' Union (MU)",
        "musicians' union": "Musicians' Union (MU)",
        "musician's union": "Musicians' Union (MU)",
        "the musicians union": "Musicians' Union (MU)",
        "the musicians' union": "Musicians' Union (MU)",
        "mu": "Musicians' Union (MU)",
        # Unite variations
        "unite": "Unite the Union",
        "unite union": "Unite the Union",
        # GMB variations
        "gmb union": "GMB",
        "the gmb": "GMB",
        # Unison variations
        "the unison": "Unison",
        "unison union": "Unison",
        # RMT variations
        "rmt": "National Union of Rail, Maritime and Transport Workers (RMT)",
        "the rmt": "National Union of Rail, Maritime and Transport Workers (RMT)",
        "rmt union": "National Union of Rail, Maritime and Transport Workers (RMT)",
        # CWU variations
        "cwu": "Communication Workers Union (CWU)",
        "the cwu": "Communication Workers Union (CWU)",
        # NEU variations
        "neu": "National Education Union (NEU)",
        "the neu": "National Education Union (NEU)",
        # UCU variations
        "ucu": "University and College Union (UCU)",
        "the ucu": "University and College Union (UCU)",
        # PCS variations
        "pcs": "Public and Commercial Services Union (PCS)",
        "the pcs": "Public and Commercial Services Union (PCS)",
        # BMA variations
        "bma": "British Medical Association (BMA)",
        "the bma": "British Medical Association (BMA)",
        # FBU variations
        "fbu": "Fire Brigades Union (FBU)",
        "the fbu": "Fire Brigades Union (FBU)",
        # NUJ variations
        "nuj": "National Union of Journalists (NUJ)",
        "the nuj": "National Union of Journalists (NUJ)",
        # ASLEF variations
        "aslef": "Associated Society of Locomotive Engineers and Firemen (ASLEF)",
        "the aslef": "Associated Society of Locomotive Engineers and Firemen (ASLEF)",
        # RCN variations
        "rcn": "Royal College of Nursing (RCN)",
        "the rcn": "Royal College of Nursing (RCN)",
        # NASUWT variations
        "nasuwt": "National Association of Schoolmasters Union of Women Teachers (NASUWT)",
        "the nasuwt": "National Association of Schoolmasters Union of Women Teachers (NASUWT)",
        # USDAW variations
        "usdaw": "Union of Shop, Distributive and Allied Workers (USDAW)",
        "the usdaw": "Union of Shop, Distributive and Allied Workers (USDAW)",
        # Equity variations
        "equity union": "Equity",
        "the equity": "Equity",
        # Prospect variations
        "prospect union": "Prospect",
        # IWGB variations
        "iwgb": "Independent Workers' Union of Great Britain (IWGB)",
        "the iwgb": "Independent Workers' Union of Great Britain (IWGB)",
        # UVW variations
        "uvw": "United Voices of the World (UVW)",
        "the uvw": "United Voices of the World (UVW)",
        # Writers Guild variations
        "writers guild": "Writers' Guild of Great Britain (WGGB)",
        "writers' guild": "Writers' Guild of Great Britain (WGGB)",
        "wggb": "Writers' Guild of Great Britain (WGGB)",
        # BALPA variations
        "balpa": "British Airline Pilots' Association (BALPA)",
        "the balpa": "British Airline Pilots' Association (BALPA)",
        # TUC variations
        "tuc": "Trades Union Congress (TUC)",
        "the tuc": "Trades Union Congress (TUC)",
        # NAHT variations
        "naht": "National Association of Head Teachers (NAHT)",
        "the naht": "National Association of Head Teachers (NAHT)",
        # POA variations
        "poa": "Prison Officers Association (POA)",
        "the poa": "Prison Officers Association (POA)",
        # CSP variations
        "csp": "Chartered Society of Physiotherapy (CSP)",
        "the csp": "Chartered Society of Physiotherapy (CSP)",
        # RCM variations
        "rcm": "Royal College of Midwives (RCM)",
        "the rcm": "Royal College of Midwives (RCM)",
        # Community variations
        "community union": "Community",
        "the community": "Community",
        # EIS variations
        "eis": "Educational Institute of Scotland (EIS)",
        "the eis": "Educational Institute of Scotland (EIS)",
        # TSSA variations
        "tssa": "Transport Salaried Staffs' Association (TSSA)",
        "the tssa": "Transport Salaried Staffs' Association (TSSA)",
        # Additional variations for unmatched names
        "accord union": "Accord",
        "advance union": "Advance",
        "artists union england": "Artists' Union England (AUE)",
        "bda trade union": "British Dietetic Association (BDA)",
        "iwgb (independent workers union of great britain)": "Independent Workers' Union of Great Britain (IWGB)",
        "nasuwt – the teachers' union": "National Association of Schoolmasters Union of Women Teachers (NASUWT)",
        "nasuwt - the teachers' union": "National Association of Schoolmasters Union of Women Teachers (NASUWT)",
        "royal college of occupational therapists (rcot)": "British Association of Occupational Therapists (BAOT)",
        "rcot": "British Association of Occupational Therapists (BAOT)",
        "snct teachers' side": "Educational Institute of Scotland (EIS)",
        "tuc cymru": "Trades Union Congress (TUC)",
    }

    lookup.update(manual_mappings)
    return lookup


def find_best_match(name: str, lookup: dict) -> Optional[str]:
    """Find the best canonical match for a union name."""
    if not name:
        return None

    normalized = normalize_name(name)

    # Direct lookup
    if normalized in lookup:
        return lookup[normalized]

    # Try removing "the" prefix
    if normalized.startswith("the "):
        without_the = normalized[4:]
        if without_the in lookup:
            return lookup[without_the]

    # Try fuzzy matching by checking if any canonical name is contained
    for canonical in UK_UNIONS:
        canonical_normalized = normalize_name(canonical)
        # Check if the input contains the main part of the canonical name
        if "(" in canonical:
            main_part = normalize_name(canonical[: canonical.rfind("(")])
            if main_part in normalized or normalized in main_part:
                return canonical

    return None


def main():
    """Main function to deduplicate union names."""
    print("=" * 60)
    print("Union Name Deduplication Script")
    print("=" * 60)

    # Build the lookup table
    lookup = build_canonical_lookup()
    print(f"\nLoaded {len(lookup)} name variations mapping to {len(UK_UNIONS)} canonical unions")

    # Get all unique union names from the database
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT DISTINCT union_name FROM union_wins WHERE union_name IS NOT NULL ORDER BY union_name")
        )
        existing_names = [row[0] for row in result.fetchall()]

    print(f"\nFound {len(existing_names)} unique union names in database:")
    print("-" * 60)

    # Analyze each name and find matches
    updates_needed = []
    unmatched = []

    for name in existing_names:
        canonical = find_best_match(name, lookup)
        if canonical:
            if name != canonical:
                updates_needed.append((name, canonical))
                print(f"  '{name}' -> '{canonical}'")
            else:
                print(f"  '{name}' ✓ (already canonical)")
        else:
            unmatched.append(name)
            print(f"  '{name}' ⚠ (no match found)")

    print("-" * 60)
    print(f"\nSummary:")
    print(f"  - {len(existing_names)} unique names found")
    print(f"  - {len(updates_needed)} names need updating")
    print(f"  - {len(unmatched)} names have no canonical match")

    if unmatched:
        print(f"\nUnmatched names (may need manual mapping):")
        for name in unmatched:
            print(f"  - '{name}'")

    if not updates_needed:
        print("\nNo updates needed. Database is already deduplicated.")
        return

    # Ask for confirmation
    print(f"\nAbout to update {len(updates_needed)} union name variations.")
    response = input("Proceed with updates? (yes/no): ").strip().lower()

    if response != "yes":
        print("Aborted. No changes made.")
        return

    # Perform the updates
    print("\nUpdating database...")
    with engine.connect() as conn:
        for old_name, new_name in updates_needed:
            result = conn.execute(
                text("UPDATE union_wins SET union_name = :new_name WHERE union_name = :old_name"),
                {"old_name": old_name, "new_name": new_name},
            )
            print(f"  Updated {result.rowcount} records: '{old_name}' -> '{new_name}'")
        conn.commit()

    print("\n✓ Database updated successfully!")

    # Verify the results
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT DISTINCT union_name FROM union_wins WHERE union_name IS NOT NULL ORDER BY union_name")
        )
        final_names = [row[0] for row in result.fetchall()]

    print(f"\nFinal state: {len(final_names)} unique union names in database")


if __name__ == "__main__":
    main()
