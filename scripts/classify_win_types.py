#!/usr/bin/env python3
"""
Script to classify union wins by type using LLM.

This script goes through each win in the database and uses an LLM to assign
a win type from a predefined list based on the title, URL, union name, and summary.
"""
import sys
import json
from pathlib import Path
from sqlalchemy.orm import Session

# Add the backend directory to the Python path BEFORE importing
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from src.config import client
from src.models import UnionWinDB, WIN_TYPES
from src.database import SessionLocal


def classify_win_type(win: UnionWinDB) -> list[str]:
    """
    Use LLM to classify a union win based on its attributes.

    Args:
        win: The UnionWinDB object to classify

    Returns:
        list[str]: List of classified win types (up to 2) from WIN_TYPES list
    """
    print(f"🔍 Classifying win ID {win.id}: {win.title[:50]}...", flush=True)

    # Prepare the prompt for the LLM
    prompt = f"""You are an expert at classifying union victories and labour wins.

Analyze the following union win and classify it into UP TO TWO of these types (primary and optional secondary):
{', '.join(WIN_TYPES)}

Win Information:
- Title: {win.title}
- Union: {win.union_name or 'Unknown'}
- Date: {win.date}
- URL: {win.url}
- Summary: {win.summary}

Classification Guidelines:
- "Pay Rise": Wage increases, salary improvements, bonuses
- "Recognition": Union recognition, organising victories, new union formation
- "Strike Action": Successful strikes, industrial action victories
- "Working Conditions": Improvements to hours, breaks, workload, scheduling
- "Job Security": Protection from redundancies, job guarantees, contract improvements
- "Benefits": Pensions, healthcare, leave policies, perks
- "Health & Safety": Workplace safety improvements, PPE, safety protocols
- "Equality": Anti-discrimination wins, equal pay, diversity improvements
- "Legal Victory": Court cases, tribunal wins, legal precedents
- "Organising": Successful campaigns, membership growth, coalition building
- "Other": Anything that doesn't clearly fit the above categories

Return ONLY a valid JSON object with this exact format (no markdown, no explanation):
{{"primary_type": "Type Name", "secondary_type": "Type Name or null"}}

Note: 
- primary_type is REQUIRED and MUST be one of the types listed above
- secondary_type is OPTIONAL - use null if there is no secondary type
- Both values (if provided) MUST be from the types listed above
- Use secondary_type only if the win genuinely fits multiple categories"""

    try:
        # Use GPT-5.2 for classification
        response = client.responses.create(
            model="gpt-5-nano",
            reasoning={"effort": "low"},
            input=prompt
        )

        # Parse the response
        result = json.loads(response.output_text)
        primary_type = result.get("primary_type", "Other")
        secondary_type = result.get("secondary_type")

        # Validate primary type
        if primary_type not in WIN_TYPES:
            print(
                f"⚠️  LLM returned invalid primary type '{primary_type}', defaulting to 'Other'", flush=True)
            primary_type = "Other"

        # Validate secondary type if provided
        if secondary_type and secondary_type not in WIN_TYPES:
            print(
                f"⚠️  LLM returned invalid secondary type '{secondary_type}', ignoring", flush=True)
            secondary_type = None

        # Build the types list
        win_types = [primary_type]
        if secondary_type:
            win_types.append(secondary_type)

        print(f"✅ Classified as: {', '.join(win_types)}", flush=True)
        return win_types

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}", flush=True)
        print(f"   Response was: {response.output_text}", flush=True)
        return ["Other"]
    except Exception as e:
        print(f"❌ Error classifying win: {e}", flush=True)
        return ["Other"]


def classify_all_wins(db: Session, limit: int = None, skip_existing: bool = True) -> dict:
    """
    Classify all wins in the database.

    Args:
        db: Database session
        limit: Optional limit on number of wins to process
        skip_existing: If True, skip wins that already have win_types assigned

    Returns:
        dict: Statistics about the classification process
    """
    print("\n" + "="*80)
    print("🏷️  UNION WIN TYPE CLASSIFICATION")
    print("="*80 + "\n")

    # Query all approved wins
    query = db.query(UnionWinDB)

    if skip_existing:
        query = query.filter(
            (UnionWinDB.win_types == None) | (UnionWinDB.win_types == "")
        )

    wins = query.all()

    total_wins = len(wins)
    if limit:
        wins = wins[:limit]

    print(f"📊 Found {total_wins} wins to classify")
    if limit:
        print(f"🔢 Processing first {limit} wins")
    if skip_existing:
        print(f"⏭️  Skipping wins that already have types assigned")
    print()

    # Statistics
    stats = {
        "total": len(wins),
        "processed": 0,
        "updated": 0,
        "errors": 0,
        "types": {win_type: 0 for win_type in WIN_TYPES},
        "multi_type_wins": 0
    }

    # Process each win
    for idx, win in enumerate(wins, 1):
        print(f"\n[{idx}/{len(wins)}] Processing win ID {win.id}")
        print(f"   Title: {win.title[:60]}...")

        try:
            # Classify the win
            win_types_list = classify_win_type(win)

            # Store as comma-separated string
            win_types_str = ", ".join(win_types_list)

            # Update the database
            win.win_types = win_types_str
            db.commit()

            # Update statistics
            stats["processed"] += 1
            stats["updated"] += 1
            for wtype in win_types_list:
                stats["types"][wtype] += 1
            
            if len(win_types_list) > 1:
                stats["multi_type_wins"] += 1

            print(f"💾 Updated win ID {win.id} with types: {win_types_str}")

        except Exception as e:
            print(f"❌ Error processing win ID {win.id}: {e}", flush=True)
            stats["errors"] += 1
            db.rollback()

    return stats


def print_statistics(stats: dict) -> None:
    """
    Print classification statistics.

    Args:
        stats: Dictionary containing classification statistics
    """
    print("\n" + "="*80)
    print("📊 CLASSIFICATION STATISTICS")
    print("="*80 + "\n")

    print(f"Total wins processed: {stats['processed']}")
    print(f"Successfully updated: {stats['updated']}")
    print(f"Errors encountered: {stats['errors']}")
    print(f"Wins with multiple types: {stats.get('multi_type_wins', 0)}")
    print()

    print("Win Types Distribution:")
    print("-" * 40)
    for win_type, count in sorted(stats['types'].items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            percentage = (count / stats['processed']
                          * 100) if stats['processed'] > 0 else 0
            print(f"  {win_type:.<30} {count:>4} ({percentage:>5.1f}%)")

    print("\n" + "="*80 + "\n")


def main():
    """Main entry point for the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Classify union wins by type using LLM"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of wins to process"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Re-classify all wins, including those that already have a type"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run classification without updating the database"
    )

    args = parser.parse_args()

    # Create database session
    db = SessionLocal()

    try:
        # Run classification
        stats = classify_all_wins(
            db,
            limit=args.limit,
            skip_existing=not args.all
        )

        # Print statistics
        print_statistics(stats)

        if args.dry_run:
            print("🔄 DRY RUN: Rolling back all changes...")
            db.rollback()
        else:
            print("✅ All changes committed to database")

    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
        db.rollback()
        print("🔄 Changes rolled back")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        db.rollback()
        print("🔄 Changes rolled back")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
