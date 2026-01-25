"""
Email service for sending newsletter updates using Resend API.
"""
from datetime import datetime, timedelta
from typing import List
import re
import resend
from sqlalchemy.orm import Session

from src.config import RESEND_API_KEY, FROM_EMAIL
from src.models import NewsletterSubscriptionDB, UnionWinDB

# Initialize Resend
resend.api_key = RESEND_API_KEY


def remove_markdown_links(text: str) -> str:
    """Remove markdown links [text](url), keeping only the text."""
    # Pattern to match markdown links: [text](url)
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    # Replace with just the text part
    return re.sub(pattern, r'\1', text)


def generate_email_html(wins: List[UnionWinDB], subscriber_name: str | None, frequency: str) -> str:
    """Generate HTML email content for newsletter."""
    greeting = f"Hi {subscriber_name}" if subscriber_name else "Hi"
    period = "today" if frequency == "daily" else f"this {frequency.replace('ly', '')}"

    wins_html = ""
    for win in wins:
        emoji = win.emoji if win.emoji else "✊"
        union = f" - {win.union_name}" if win.union_name else ""

        # Remove markdown links from summary
        summary_text = remove_markdown_links(win.summary)

        wins_html += f"""
        <div style="margin-bottom: 24px; padding: 16px; background-color: #f9fafb; border-left: 4px solid #ef4444; border-radius: 4px;">
            <h3 style="margin: 0 0 8px 0; font-size: 16px; color: #111827;">
                {emoji} {win.title}
            </h3>
            <p style="margin: 0 0 8px 0; font-size: 12px; color: #6b7280;">
                {win.date}{union}
            </p>
            <p style="margin: 0 0 12px 0; font-size: 14px; color: #374151; line-height: 1.5;">
                {summary_text}
            </p>
            <a href="{win.url}" style="display: inline-block; padding: 8px 16px; background-color: #ef4444; color: white; text-decoration: none; border-radius: 4px; font-size: 14px; font-weight: 500;">
                Read More →
            </a>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Union Wins Update</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 0; background-color: #ffffff;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <!-- Header -->
            <div style="text-align: center; padding: 24px 0; border-bottom: 2px solid #ef4444;">
                <h1 style="margin: 0; font-size: 24px; color: #111827;">
                    ✊ What Have Unions Done For Us?
                </h1>
                <p style="margin: 8px 0 0 0; font-size: 14px; color: #6b7280;">
                    Your {frequency} union wins update
                </p>
            </div>
            
            <!-- Body -->
            <div style="padding: 32px 0;">
                <p style="font-size: 16px; color: #111827; margin: 0 0 24px 0;">
                    {greeting},
                </p>
                
                <p style="font-size: 14px; color: #374151; margin: 0 0 24px 0; line-height: 1.6;">
                    Here are the latest union victories from {period}. These wins show the power of workers organising together.
                </p>
                
                <!-- Wins List -->
                {wins_html if wins else '<p style="font-size: 14px; color: #6b7280; font-style: italic;">No new wins to report during this period.</p>'}
            </div>
            
            <!-- Footer -->
            <div style="border-top: 1px solid #e5e7eb; padding: 24px 0; text-align: center;">
                <p style="font-size: 12px; color: #6b7280; margin: 0 0 8px 0;">
                    You're receiving this because you subscribed to union wins updates.
                </p>
                <p style="font-size: 12px; color: #6b7280; margin: 0;">
                    <a href="https://whathaveunionsdoneforus.uk/" style="color: #ef4444; text-decoration: none;">Visit Website</a>
                    {' | '}
                    <a href="mailto:unsubscribe@whathaveunionsdoneforus.uk" style="color: #6b7280; text-decoration: none;">Unsubscribe</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    return html


def get_wins_since(db: Session, since: datetime) -> List[UnionWinDB]:
    """Get all approved wins since a specific datetime."""
    wins = db.query(UnionWinDB).filter(
        UnionWinDB.status == "approved"
    ).order_by(UnionWinDB.date.desc()).all()

    # Filter by date string comparison (since date is stored as string)
    since_date_str = since.strftime("%Y-%m-%d")
    filtered_wins = [
        win for win in wins
        if win.date >= since_date_str
    ]

    return filtered_wins


def send_newsletter_email(
    subscriber: NewsletterSubscriptionDB,
    wins: List[UnionWinDB],
    db: Session
) -> bool:
    """Send newsletter email to a subscriber."""
    if not RESEND_API_KEY:
        print("⚠️  RESEND_API_KEY not configured, skipping email send", flush=True)
        return False

    try:
        html_content = generate_email_html(
            wins, subscriber.name, subscriber.frequency)

        params = {
            "from": FROM_EMAIL,
            "to": [subscriber.email],
            "subject": f"Union Wins Update - {len(wins)} New Victories",
            "html": html_content,
        }

        resend.Emails.send(params)

        # Update last_email_sent_at
        subscriber.last_email_sent_at = datetime.now()
        db.commit()

        print(
            f"✉️  Sent {subscriber.frequency} newsletter to {subscriber.email} ({len(wins)} wins)", flush=True)
        return True

    except Exception as e:
        print(f"❌ Error sending email to {subscriber.email}: {e}", flush=True)
        db.rollback()
        return False


def send_daily_newsletters(db: Session) -> int:
    """Send newsletters to daily subscribers."""
    # Get active daily subscribers
    subscribers = db.query(NewsletterSubscriptionDB).filter(
        NewsletterSubscriptionDB.is_active == 1,
        NewsletterSubscriptionDB.frequency == "daily"
    ).all()

    sent_count = 0
    for subscriber in subscribers:
        # Get wins from the last 24 hours
        since = subscriber.last_email_sent_at if subscriber.last_email_sent_at else datetime.now() - \
            timedelta(days=1)
        wins = get_wins_since(db, since)

        # Skip sending if there are no wins
        if not wins:
            print(
                f"⏭️  Skipping {subscriber.frequency} newsletter to {subscriber.email} - no wins to report", flush=True)
            continue

        if send_newsletter_email(subscriber, wins, db):
            sent_count += 1

    return sent_count


def send_weekly_newsletters(db: Session) -> int:
    """Send newsletters to weekly subscribers."""
    # Get active weekly subscribers
    subscribers = db.query(NewsletterSubscriptionDB).filter(
        NewsletterSubscriptionDB.is_active == 1,
        NewsletterSubscriptionDB.frequency == "weekly"
    ).all()

    sent_count = 0
    for subscriber in subscribers:
        # Get wins from the last 7 days
        since = subscriber.last_email_sent_at if subscriber.last_email_sent_at else datetime.now() - \
            timedelta(days=7)
        wins = get_wins_since(db, since)

        # Skip sending if there are no wins
        if not wins:
            print(
                f"⏭️  Skipping {subscriber.frequency} newsletter to {subscriber.email} - no wins to report", flush=True)
            continue

        if send_newsletter_email(subscriber, wins, db):
            sent_count += 1

    return sent_count


def send_monthly_newsletters(db: Session) -> int:
    """Send newsletters to monthly subscribers."""
    # Get active monthly subscribers
    subscribers = db.query(NewsletterSubscriptionDB).filter(
        NewsletterSubscriptionDB.is_active == 1,
        NewsletterSubscriptionDB.frequency == "monthly"
    ).all()

    sent_count = 0
    for subscriber in subscribers:
        # Get wins from the last 30 days
        since = subscriber.last_email_sent_at if subscriber.last_email_sent_at else datetime.now() - \
            timedelta(days=30)
        wins = get_wins_since(db, since)

        # Skip sending if there are no wins
        if not wins:
            print(
                f"⏭️  Skipping {subscriber.frequency} newsletter to {subscriber.email} - no wins to report", flush=True)
            continue

        if send_newsletter_email(subscriber, wins, db):
            sent_count += 1

    return sent_count


def preview_newsletter_email(
    subscriber_email: str,
    subscriber_name: str | None,
    frequency: str,
    db: Session
) -> str:
    """Generate preview HTML for a newsletter email."""
    # Get recent wins based on frequency
    days_map = {"daily": 1, "weekly": 7, "monthly": 30}
    days = days_map.get(frequency, 7)
    since = datetime.now() - timedelta(days=days)

    wins = get_wins_since(db, since)

    return generate_email_html(wins, subscriber_name, frequency)
