"""
Main application entry point for UnionWins API.
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import threading
import time

from src.config import ALLOWED_ORIGINS, POLLING_INTERVAL_SECONDS, PORT
from src.database import get_db, init_db
from src.routes import wins, search, rss, submissions
from src.services.research_service import (
    create_research_input,
    create_background_task,
    poll_task_status,
    process_research_results,
    update_request_status
)
from src.services.search_service import get_pending_requests, get_processing_requests

app = FastAPI()

# Global flag to control background polling thread
polling_active = True


def process_pending_requests() -> None:
    """
    Background thread function that polls for pending search requests
    and processes them using OpenAI Deep Research API.
    Runs continuously in a separate thread.
    """
    global polling_active
    print(" ")
    print("🔄 Background polling thread started")

    while polling_active:
        db = None
        try:
            db = next(get_db())

            # Check for pending requests
            pending = get_pending_requests(db)

            if pending:
                print(f"📋 Processing pending search request {pending.id}...")
                pending.status = "processing"
                db.commit()

                # Build research input
                research_input = create_research_input(pending.date_range)

                # Create background request
                response_id = create_background_task(research_input)

                # Store response ID for polling
                pending.response_id = response_id
                db.commit()
                print(f"✅ Created background research task: {response_id}")

            # Check for processing requests and poll their status
            processing = get_processing_requests(db)

            for request in processing:
                try:
                    # Poll the response status
                    status, output_text = poll_task_status(request.response_id)

                    if status == "completed":
                        print(
                            f"✅ Research task {request.response_id} completed")

                        try:
                            # Process the results
                            new_wins_count = process_research_results(
                                db, output_text)

                            # Mark request as completed
                            update_request_status(
                                db, request, "completed", new_wins_found=new_wins_count
                            )

                        except Exception as e:
                            # Roll back the session on any error
                            db.rollback()
                            print(f"❌ Error processing wins: {e}")
                            update_request_status(
                                db, request, "failed", error_message=str(e)
                            )

                    elif status == "failed":
                        print(f"❌ Research task {request.response_id} failed")
                        update_request_status(
                            db,
                            request,
                            "failed",
                            error_message="OpenAI research task failed"
                        )
                    else:
                        print(
                            f"⏳ Task {request.response_id} still processing "
                            f"(status: {status})"
                        )

                except Exception as e:
                    # Roll back the session on any error
                    db.rollback()
                    print(f"❌ Error polling request {request.id}: {e}")
                    update_request_status(
                        db, request, "failed", error_message=str(e))

        except Exception as e:
            # Roll back the session on any error
            if db:
                db.rollback()
            print(f"❌ Background polling error: {e}")
        finally:
            if db:
                db.close()

        # Sleep for configured interval before next poll
        time.sleep(POLLING_INTERVAL_SECONDS)

    print("🛑 Background polling thread stopped")


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and start background polling thread."""
    init_db()

    # Start background polling thread
    polling_thread = threading.Thread(
        target=process_pending_requests,
        daemon=True,
        name="SearchPollingThread"
    )
    polling_thread.start()
    print("✅ Background polling thread started")
    print(" ")


@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully shutdown background polling."""
    global polling_active
    polling_active = False
    print("🛑 Shutting down background polling...")


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

# Serve static files from frontend build
# In Docker: /app/backend/static, locally: ../frontend/dist
static_dir = Path(__file__).parent.parent / "static"
if not static_dir.exists():
    # Fallback to local development path
    static_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"

if static_dir.exists():
    app.mount(
        "/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        Serve the frontend SPA. This catch-all route must be defined last.
        Returns index.html for all non-API routes to support client-side routing.
        """
        # Check if requesting a static file
        file_path = static_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        # Otherwise serve index.html for SPA routing
        return FileResponse(static_dir / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
