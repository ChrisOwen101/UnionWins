#!/usr/bin/env python3
"""
Script to check all URLs in the database for 404 errors and delete dead links.
"""
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from src.models import UnionWinDB, Base
from src.database import SessionLocal, engine
import sys
import os
import requests
from typing import List, Tuple
from urllib.parse import urlparse

# Add backend directory to path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)


def create_session_with_retries(
    retries: int = 3,
    backoff_factor: float = 0.3,
    status_forcelist: Tuple[int, ...] = (500, 502, 504),
) -> requests.Session:
    """Create a requests session with retry strategy."""
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        status_forcelist=status_forcelist,
        allowed_methods=["HEAD", "GET"],
        backoff_factor=backoff_factor,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def check_url(session: requests.Session, url: str, timeout: int = 8) -> Tuple[bool, int, str]:
    """
    Check if a URL is accessible (not 404).

    Returns:
        Tuple of (is_valid, status_code, error_message)
    """
    try:
        # Try HEAD request first (faster)
        response = session.head(url, timeout=timeout, allow_redirects=True)

        if response.status_code == 404:
            return False, response.status_code, "404 Not Found"

        # If HEAD failed or returned an error, try GET
        if response.status_code >= 400:
            response = session.get(url, timeout=timeout, allow_redirects=True)
            if response.status_code == 404:
                return False, response.status_code, "404 Not Found"
            if response.status_code >= 400:
                return False, response.status_code, f"HTTP {response.status_code}"

        return True, response.status_code, ""

    except requests.exceptions.Timeout:
        return False, 0, "Request timeout"
    except requests.exceptions.ConnectionError:
        return False, 0, "Connection error"
    except requests.exceptions.InvalidURL:
        return False, 0, "Invalid URL"
    except requests.exceptions.RequestException as e:
        return False, 0, f"Request error: {str(e)}"


def main():
    """Main function to check all URLs and delete dead links."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check URLs in database for dead links")
    parser.add_argument("--dry-run", action="store_true",
                        help="Just list URLs without checking them")
    args = parser.parse_args()

    print("Initializing database...")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return

    db = SessionLocal()
    session = create_session_with_retries() if not args.dry_run else None

    try:
        # Get all wins from database
        wins = db.query(UnionWinDB).all()
        print(f"Found {len(wins)} URLs to check\n")

        if not wins:
            print("No URLs found in database.")
            return

        if args.dry_run:
            print("URLs in database (dry-run mode):")
            for i, win in enumerate(wins, 1):
                print(f"[{i}] {win.url}")
            return

        dead_urls: List[Tuple[int, str, str]] = []
        valid_count = 0

        for i, win in enumerate(wins, 1):
            url = win.url
            print(f"[{i}/{len(wins)}] Checking: {url}")

            is_valid, status_code, error_msg = check_url(session, url)

            if is_valid:
                print(f"  ✓ OK ({status_code})")
                valid_count += 1
            else:
                print(f"  ✗ DEAD - {error_msg}")
                dead_urls.append((win.id, url, error_msg))

        print(f"\n{'='*60}")
        print(f"Results: {valid_count} valid, {len(dead_urls)} dead URLs")
        print(f"{'='*60}\n")

        if dead_urls:
            print("Dead URLs found:")
            for win_id, url, reason in dead_urls:
                print(f"  ID: {win_id} - {reason}")
                print(f"     {url}")

            # Ask for confirmation before deleting
            response = input(
                f"\nDelete {len(dead_urls)} entries with dead URLs? (yes/no): "
            ).strip().lower()

            if response == "yes":
                for win_id, url, _ in dead_urls:
                    win = db.query(UnionWinDB).filter(
                        UnionWinDB.id == win_id).first()
                    if win:
                        db.delete(win)
                        print(f"  Deleted: {url}")

                db.commit()
                print(f"\n✓ Successfully deleted {len(dead_urls)} entries!")
            else:
                print("Deletion cancelled.")
        else:
            print("✓ All URLs are valid!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise

    finally:
        if session:
            session.close()
        db.close()


if __name__ == "__main__":
    main()
