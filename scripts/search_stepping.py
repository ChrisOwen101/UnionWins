#!/usr/bin/env python3
"""
Script to make HTTP requests to the /search backend endpoint
stepping back in 3-day increments for 30 days.
"""

import requests
import time
from datetime import datetime, timedelta
from typing import Optional


def make_search_request(
    base_url: str = "http://localhost:8000",
    date: Optional[str] = None
) -> bool:
    """
    Make a single search request to the backend.

    Args:
        base_url: The base URL of the backend server
        date: Optional date in YYYY-MM-DD format

    Returns:
        True if successful, False otherwise
    """
    url = f"{base_url}/api/wins/search"
    payload = {}
    if date:
        payload["date"] = date

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(
                f"✅ Search request successful{f' for {date}' if date else ''}")
            print(
                f"   Response: {response.json().get('message', 'No message')}")
            return True
        else:
            print(f"❌ Search request failed for {date if date else 'today'}")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error making request{f' for {date}' if date else ''}: {e}")
        return False


def search_stepping(
    base_url: str = "http://localhost:8000",
    days_back: int = 30,
    step_days: int = 3,
    delay_seconds: float = 0.5
) -> None:
    """
    Make search requests stepping back in time.

    Args:
        base_url: The base URL of the backend server
        days_back: How many days back to go (default 30)
        step_days: Number of days to step back each request (default 3)
        delay_seconds: Delay between requests in seconds (default 0.5)
    """
    today = datetime.now().date()
    print(
        f"🚀 Starting search requests from {today} stepping back {days_back} days")
    print(f"   Step size: {step_days} days")
    print(f"   Delay between requests: {delay_seconds}s\n")

    successful = 0
    failed = 0

    # Request for today (no date parameter needed, but we include it for clarity)
    date = today.strftime("%Y-%m-%d")
    print(f"📅 Request 1/11: {date} (today)")
    if make_search_request(base_url, date):
        successful += 1
    else:
        failed += 1
    time.sleep(delay_seconds)

    # Step back in time
    request_num = 2
    current_date = today - timedelta(days=step_days)

    while (today - current_date).days <= days_back:
        date_str = current_date.strftime("%Y-%m-%d")
        days_ago = (today - current_date).days
        print(f"📅 Request {request_num}/11: {date_str} ({days_ago} days ago)")

        if make_search_request(base_url, date_str):
            successful += 1
        else:
            failed += 1

        time.sleep(delay_seconds)
        current_date -= timedelta(days=step_days)
        request_num += 1

    print(f"\n📊 Summary:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Total: {successful + failed}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Make HTTP requests to /search backend stepping back 3 days at a time"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the backend server (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--days-back",
        type=int,
        default=30,
        help="How many days back to go (default: 30)"
    )
    parser.add_argument(
        "--step",
        type=int,
        default=3,
        help="Number of days to step back each request (default: 3)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay between requests in seconds (default: 0.5)"
    )

    args = parser.parse_args()

    search_stepping(
        base_url=args.url,
        days_back=args.days_back,
        step_days=args.step,
        delay_seconds=args.delay
    )
