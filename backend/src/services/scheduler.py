"""
Scheduler service for automated tasks.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from src.database import get_db
from src.models import SearchRequestDB
from src.services.search_service import calculate_date_range, create_search_request


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

        scheduler.start()
        print("✅ Scheduler started - will run search every 12 hours", flush=True)
        print(
            f"📅 Next scheduled search: {scheduler.get_job('twelve_hour_search').next_run_time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)


def stop_scheduler() -> None:
    """
    Gracefully shutdown the scheduler.
    """
    if scheduler.running:
        scheduler.shutdown()
        print("🛑 Scheduler stopped", flush=True)
