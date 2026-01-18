#!/usr/bin/env python3
"""
Script to add missing emojis to union wins in the database.
Uses GPT-4o-mini to select appropriate emojis based on title and summary.
"""
import sys
from pathlib import Path

# Add backend to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from src.config import client
from src.models import UnionWinDB
from src.database import SessionLocal


def get_emoji_suggestion(title: str, summary: str) -> str:
    """
    Use GPT-4o-mini to suggest an appropriate emoji for a union win.

    Args:
        title: The title of the win
        summary: The summary of the win

    Returns:
        A single emoji character
    """
    prompt = f"""Given this union win, Choose an appropriate emoji that represents the industry, sector, or type of victory (e.g., 🏥 for healthcare, 🚌 for transport, 📚 for education etc).

Title: {title}
Summary: {summary}

Respond with ONLY a single emoji character, nothing else."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=10
    )

    emoji = response.choices[0].message.content.strip()
    # Ensure we only get the emoji, not extra text
    if emoji:
        return emoji[0]
    return ""  # Default emoji if something goes wrong


def add_missing_emojis():
    """Find all wins without emojis and add them using GPT."""
    db = SessionLocal()

    try:
        # Query for all wins without emojis
        wins_without_emoji = db.query(UnionWinDB).filter(
            (UnionWinDB.emoji.is_(None)) | (UnionWinDB.emoji == "✈")
        ).all()

        if not wins_without_emoji:
            print("✅ All wins already have emojis!")
            return

        print(f"🔍 Found {len(wins_without_emoji)} wins without emojis")
        print("-" * 60)

        updated_count = 0

        for i, win in enumerate(wins_without_emoji, 1):
            print(
                f"\n[{i}/{len(wins_without_emoji)}] Processing: {win.title[:50]}...")

            try:
                emoji = get_emoji_suggestion(win.title, win.summary)
                win.emoji = emoji
                db.commit()
                updated_count += 1
                print(f"  ✅ Added emoji: {emoji}")
            except Exception as e:
                print(f"  ❌ Error processing win {win.id}: {str(e)}")
                db.rollback()
                continue

        print("\n" + "-" * 60)
        print(f"✨ Successfully updated {updated_count} wins with emojis!")

    finally:
        db.close()


if __name__ == "__main__":
    add_missing_emojis()
