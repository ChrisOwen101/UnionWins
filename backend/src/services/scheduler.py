"""
Scheduler service for automated tasks.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from src.database import get_db
from src.models import SearchRequestDB
from src.services.search_service import calculate_date_range, create_search_request
from src.services.email_service import send_daily_newsletters, send_weekly_newsletters, send_monthly_newsletters
from src.services.scraping_service import run_all_scrapes

# UK timezone for scheduling newsletters
UK_TIMEZONE = ZoneInfo("Europe/London")


def scheduled_search_job() -> None:
    """
    Scheduled job that creates a search request every 12 hours.
    This will queue a search which will be picked up by the background polling thread.
    """
    db = None
    try:
        db = next(get_db())

        # Calculate date range for the last 3 days
        _, _, date_range = calculate_date_range(days=2)

        # Create a search request in the database
        search_request = create_search_request(db, date_range)

        print(
            f"⏰ Scheduled search triggered: Request {search_request.id} queued for {date_range}", flush=True)

    except Exception as e:
        print(f"❌ Error in scheduled search job: {e}", flush=True)
        if db:
            db.rollback()
    finally:
        if db:
            db.close()


def daily_newsletter_job() -> None:
    """Send daily newsletters at 9:00 AM."""
    db = None
    try:
        db = next(get_db())
        count = send_daily_newsletters(db)
        print(f"📧 Daily newsletters sent: {count} emails", flush=True)
    except Exception as e:
        print(f"❌ Error in daily newsletter job: {e}", flush=True)
        if db:
            db.rollback()
    finally:
        if db:
            db.close()


def weekly_newsletter_job() -> None:
    """Send weekly newsletters on Monday at 9:00 AM."""
    db = None
    try:
        db = next(get_db())
        count = send_weekly_newsletters(db)
        print(f"📧 Weekly newsletters sent: {count} emails", flush=True)
    except Exception as e:
        print(f"❌ Error in weekly newsletter job: {e}", flush=True)
        if db:
            db.rollback()
    finally:
        if db:
            db.close()


def monthly_newsletter_job() -> None:
    """Send monthly newsletters on the 1st of each month at 9:00 AM."""
    db = None
    try:
        db = next(get_db())
        count = send_monthly_newsletters(db)
        print(f"📧 Monthly newsletters sent: {count} emails", flush=True)
    except Exception as e:
        print(f"❌ Error in monthly newsletter job: {e}", flush=True)
        if db:
            db.rollback()
    finally:
        if db:
            db.close()


def weekly_scraping_job() -> None:
    """Run website scraping on Monday at 2:00 AM."""
    db = None
    try:
        db = next(get_db())
        results = run_all_scrapes(db)
        print(f"🕸️ Weekly scraping completed. Scraped {len(results)} sources.", flush=True)
    except Exception as e:
        print(f"❌ Error in weekly scraping job: {e}", flush=True)
    finally:
        if db:
            db.close()


# Global scheduler instance
scheduler = BackgroundScheduler()


def start_scheduler() -> None:
    """
    Initialize and start the scheduler.
    Adds a job that runs every 12 hours to trigger a search.
    Calculates next run time based on the last search request to avoid duplicate searches on restart.
    """
    if not scheduler.running:
        # Calculate next run time based on last search request
        db = None
        next_run = None
        try:
            db = next(get_db())

            # Get the most recent search request
            last_search = (
                db.query(SearchRequestDB)
                .order_by(SearchRequestDB.created_at.desc())
                .first()
            )

            if last_search:
                # Schedule next run 12 hours after the last search
                next_run = last_search.created_at + timedelta(hours=12)

                # If that time has already passed, don't run immediately - schedule for 12 hours from now
                if next_run <= datetime.now():
                    next_run = datetime.now() + timedelta(hours=12)

                print(
                    f"📅 Last search was at {last_search.created_at.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
            else:
                # No previous searches - schedule for 12 hours from now
                next_run = datetime.now() + timedelta(hours=12)
                print("📅 No previous searches found", flush=True)

        except Exception as e:
            print(f"⚠️  Error calculating next run time: {e}", flush=True)
            # Default to 12 hours from now
            next_run = datetime.now() + timedelta(hours=12)
        finally:
            if db:
                db.close()

        # Add the search job to run every 12 hours
        scheduler.add_job(
            scheduled_search_job,
            trigger=IntervalTrigger(hours=12),
            id='twelve_hour_search',
            name='Twelve-hour union wins search',
            replace_existing=True,
            next_run_time=next_run
        )

        # Add newsletter jobs with UK timezone
        # Daily newsletters at 9:00 AM UK time every day
        scheduler.add_job(
            daily_newsletter_job,
            trigger=CronTrigger(hour=9, minute=0, timezone=UK_TIMEZONE),
            id='daily_newsletter',
            name='Daily newsletter at 9:00 AM UK',
            replace_existing=True
        )

        # Weekly newsletters on Monday at 9:00 AM UK time
        scheduler.add_job(
            weekly_newsletter_job,
            trigger=CronTrigger(day_of_week='mon', hour=9, minute=0, timezone=UK_TIMEZONE),
            id='weekly_newsletter',
            name='Weekly newsletter on Monday at 9:00 AM UK',
            replace_existing=True
        )

        # Monthly newsletters on the 1st at 9:00 AM UK time
        scheduler.add_job(
            monthly_newsletter_job,
            trigger=CronTrigger(day=1, hour=9, minute=0, timezone=UK_TIMEZONE),
            id='monthly_newsletter',
            name='Monthly newsletter on 1st at 9:00 AM UK',
            replace_existing=True
        )

        # Weekly scraping on Monday at 2:00 AM UK time
        scheduler.add_job(
            weekly_scraping_job,
            trigger=CronTrigger(day_of_week='mon', hour=2, minute=0, timezone=UK_TIMEZONE),
            id='weekly_scrape',
            name='Weekly Website Scraping',
            replace_existing=True
        )

        scheduler.start()
        print("✅ Scheduler started - will run search every 12 hours", flush=True)
        print(
            f"📅 Next scheduled search: {scheduler.get_job('twelve_hour_search').next_run_time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        print("✅ Newsletter jobs scheduled (daily 9AM UK, weekly Mon 9AM UK, monthly 1st 9AM UK)", flush=True)
        
        # Print next run times for newsletter jobs
        daily_job = scheduler.get_job('daily_newsletter')
        if daily_job:
            print(f"📧 Next daily newsletter: {daily_job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')}", flush=True)


def stop_scheduler() -> None:
    """
    Gracefully shutdown the scheduler.
    """
    if scheduler.running:
        scheduler.shutdown()
        print("🛑 Scheduler stopped", flush=True)
