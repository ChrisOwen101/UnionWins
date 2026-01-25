"""
Main application entry point for UnionWins API.
"""
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
import threading
import time
from datetime import datetime, timedelta

from src.config import ALLOWED_ORIGINS, POLLING_INTERVAL_SECONDS, PORT
from src.database import get_db, init_db
from src.routes import wins, search, rss, submissions, admin, newsletter
from src.services.research_service import (
    create_research_input,
    create_background_task,
    poll_task_status,
    process_research_results,
    update_request_status
)
from src.services.search_service import get_pending_requests, get_processing_requests
from src.services.scheduler import start_scheduler, stop_scheduler

# Global flag to control background polling thread
polling_active = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.
    Handles initialization and cleanup of background tasks.
    """
    global polling_active

    # Startup
    print(" ", flush=True)
    print("🚀 Starting UnionWins API...", flush=True)
    init_db()

    # Start background polling thread
    polling_thread = threading.Thread(
        target=safe_process_pending_requests,
        daemon=True,
        name="SearchPollingThread"
    )
    polling_thread.start()
    print("✅ Background polling thread started", flush=True)

    # Start the scheduler for automated searches
    start_scheduler()
    print(" ", flush=True)

    yield

    # Shutdown
    polling_active = False
    print("🛑 Shutting down background polling...", flush=True)
    stop_scheduler()


app = FastAPI(lifespan=lifespan)


# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    # Add cache headers for static assets
    if "/assets/" in str(request.url):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    elif request.url.path.endswith((".js", ".css", ".woff", ".woff2", ".ttf", ".eot")):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    elif request.url.path == "/" or request.url.path.endswith(".html"):
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
    elif "/api/" in str(request.url):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

    return response


def process_pending_requests() -> None:
    """
    Background thread function that polls for pending search requests
    and processes them using OpenAI Deep Research API.
    Runs continuously in a separate thread.
    """
    global polling_active
    print(" ", flush=True)
    print("🔄 Background polling thread started", flush=True)

    poll_count = 0

    while polling_active:
        db = None
        poll_count += 1

        # Log heartbeat every 12 polls (roughly every minute with 5s interval)
        if poll_count % 12 == 0:
            print(
                f"💓 Background thread heartbeat - poll #{poll_count}", flush=True)

        try:
            db = next(get_db())

            # Check for pending requests
            pending = get_pending_requests(db)

            if pending:
                print(
                    f"📋 Processing pending search request {pending.id}...", flush=True)

                try:
                    # Build research input
                    research_input = create_research_input(pending.date_range)

                    # Create background request
                    response_id = create_background_task(research_input)

                    # Only update status to processing AFTER we have a response_id
                    # This prevents requests getting stuck with no response_id
                    pending.status = "processing"
                    pending.response_id = response_id
                    db.commit()
                    print(
                        f"✅ Created background research task: {response_id}", flush=True)
                except Exception as e:
                    # If creating the background task fails, keep request as pending
                    # so it can be retried on the next poll
                    db.rollback()
                    print(
                        f"❌ Failed to create background task for request {pending.id}: {e}", flush=True)

            # Check for processing requests and poll their status
            processing = get_processing_requests(db)

            if processing:
                print(
                    f"🔍 Found {len(processing)} request(s) in processing state", flush=True)

            for request in processing:
                try:
                    # Check if task has been stuck for too long (12+ hours)
                    time_elapsed = datetime.now() - request.created_at
                    if time_elapsed > timedelta(hours=12):
                        print(
                            f"⏰ Task {request.response_id} stuck for {time_elapsed} - marking as failed", flush=True)
                        update_request_status(
                            db, request, "failed",
                            error_message=f"Task timeout after {time_elapsed}. OpenAI response may have failed."
                        )
                        continue

                    # Poll the response status
                    print(
                        f"🔎 Polling status for task {request.response_id}...", flush=True)
                    status, output_text = poll_task_status(request.response_id)

                    if status == "completed":
                        print(
                            f"✅ Research task {request.response_id} completed", flush=True)

                        try:
                            # Process the results
                            new_wins_count = process_research_results(
                                db, output_text)

                            # Mark request as completed
                            update_request_status(
                                db, request, "completed", new_wins_found=new_wins_count
                            )
                            print(
                                f"🎉 Found {new_wins_count} new wins!", flush=True)

                        except Exception as e:
                            # Roll back the session on any error
                            db.rollback()
                            print(f"❌ Error processing wins: {e}", flush=True)
                            update_request_status(
                                db, request, "failed", error_message=str(e)
                            )

                    elif status == "failed":
                        print(
                            f"❌ Research task {request.response_id} failed", flush=True)
                        update_request_status(
                            db,
                            request,
                            "failed",
                            error_message="OpenAI research task failed"
                        )
                    else:
                        print(
                            f"⏳ Task {request.response_id} still processing "
                            f"(status: {status})", flush=True
                        )

                except Exception as e:
                    # Roll back the session on any error
                    db.rollback()
                    print(
                        f"❌ Error polling request {request.id}: {e}", flush=True)
                    # Don't mark as failed immediately - could be transient error
                    # Let the timeout mechanism handle it after 12 hours
                    import traceback
                    traceback.print_exc()

        except Exception as e:
            # Roll back the session on any error
            if db:
                db.rollback()
            print(f"❌ Background polling error: {e}", flush=True)
        finally:
            if db:
                db.close()

        # Sleep for configured interval before next poll
        time.sleep(POLLING_INTERVAL_SECONDS)

    print("🛑 Background polling thread stopped", flush=True)


def safe_process_pending_requests() -> None:
    """
    Wrapper that catches any unhandled exceptions in the background thread.
    This ensures the thread doesn't die silently.
    """
    try:
        process_pending_requests()
    except Exception as e:
        print(
            f"💀 CRITICAL: Background polling thread crashed: {e}", flush=True)
        import traceback
        traceback.print_exc()


# Configure CORS - allow everything
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(wins.router)
app.include_router(search.router)
app.include_router(rss.router)
app.include_router(submissions.router)
app.include_router(admin.router)
app.include_router(newsletter.router)

# Serve static files from frontend build
# In Docker: /app/backend/static, locally: ../frontend/dist
static_dir = Path(__file__).parent.parent / "static"
if not static_dir.exists():
    # Fallback to local development path
    static_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"

if static_dir.exists():
    app.mount(
        "/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

    @app.get("/robots.txt", response_class=PlainTextResponse)
    async def serve_robots():
        """Serve robots.txt file."""
        robots_path = static_dir / "robots.txt"
        if robots_path.exists():
            return FileResponse(robots_path, media_type="text/plain")
        return PlainTextResponse("User-agent: *\nAllow: /\n")

    @app.get("/sitemap.xml")
    async def serve_sitemap():
        """Serve sitemap.xml file."""
        sitemap_path = static_dir / "sitemap.xml"
        if sitemap_path.exists():
            return FileResponse(sitemap_path, media_type="application/xml")
        # Return a basic sitemap if file doesn't exist
        from datetime import date
        today = date.today().isoformat()
        sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://whathaveunionsdoneforus.uk/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>"""
        return PlainTextResponse(sitemap_content, media_type="application/xml")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        Serve the frontend SPA.
        This catch-all route must be defined last.
        Returns index.html for all non-API routes to support client-side routing.
        """
        # Check if requesting a static file
        file_path = static_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        # For HTML routes, serve index.html
        index_path = static_dir / "index.html"
        if not index_path.exists():
            return FileResponse(index_path)

        return FileResponse(index_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT, workers=4)
