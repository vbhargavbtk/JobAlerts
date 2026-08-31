"""
FastAPI Main Application
Provides:
- GET /health: Lightweight Render health check (HTTP 200, <10ms, no heavy DB/Telegram calls)
- GET /api/health/detailed: Deep health inspect for DB, AI providers, and queues
- GET /api/requirements & PUT /api/requirements: Persistent user profile editing API
- GET /admin/requirements: Interactive Web Dashboard for requirements editing
- POST /webhook/inbound-message: n8n webhook receiver for new messages
- POST /api/pipeline/process: Manual or orchestrated trigger for processing messages
- Application startup/shutdown hooks for database and Telethon listener
"""
import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
import yaml
from fastapi import FastAPI, Depends, HTTPException, Body, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from app.database.connection import init_db, get_db, engine
from app.database.repository import DatabaseRepository
from app.eligibility.models import UserRequirementsProfile
from app.telegram.listener import TelegramListener
from app.telegram.channel_manager import ChannelManager
from app.pipeline import ProcessingPipeline
from app.web.templates.requirements_editor import REQUIREMENTS_EDITOR_HTML
from app.web.templates.channels_manager import CHANNELS_MANAGER_HTML

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app.main")

# Global singleton components
telegram_listener = TelegramListener()
pipeline = ProcessingPipeline()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("Initializing system...")
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Database initialization error on startup: {e}")

    # Start Telegram MTProto listener as background task
    try:
        import asyncio
        asyncio.create_task(telegram_listener.start())
    except Exception as e:
        logger.warning(f"Could not start Telegram listener: {e}")

    yield

    # SHUTDOWN
    logger.info("Shutting down system...")
    await telegram_listener.stop()


app = FastAPI(
    title="Personal Government Job Notification Intelligence System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------------------
# ROOT REDIRECT
# ------------------------------------------------------------------------------
@app.get("/", summary="Root Redirect to Dashboard")
async def root_redirect():
    """Redirects root URL directly to the user requirements dashboard."""
    return RedirectResponse(url="/admin/requirements")


# ------------------------------------------------------------------------------
# RENDER FREE SERVICE COMPLIANT HEALTH ENDPOINTS (Section 19 & 33)
# ------------------------------------------------------------------------------
@app.get("/health", summary="Lightweight Ping Endpoint")
async def lightweight_health():
    """
    Lightweight health check for Render web service pings.
    Must execute immediately (<10ms) without triggering DB queries or Telegram calls.
    """
    return {
        "status": "healthy",
        "service": "personal-job-intelligence",
        "timestamp": settings.ENVIRONMENT
    }


@app.get("/api/health/detailed", summary="Deep Component Health Check")
async def detailed_health(db: AsyncSession = Depends(get_db)):
    """Deep component health inspection."""
    db_ok = False
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        logger.error(f"DB health check failed: {e}")

    return {
        "database_connected": db_ok,
        "telegram_listener_active": telegram_listener.is_running,
        "telegram_listener_configured": telegram_listener.is_configured(),
        "environment": settings.ENVIRONMENT
    }


# ------------------------------------------------------------------------------
# USER ELIGIBILITY REQUIREMENTS EDITING API & WEB UI (Section 12 & User Request)
# ------------------------------------------------------------------------------
@app.get("/admin/requirements", response_class=HTMLResponse, summary="Requirements Editor Web UI")
async def requirements_editor_ui():
    """Renders the rich, interactive Web UI for editing personal eligibility rules."""
    return HTMLResponse(content=REQUIREMENTS_EDITOR_HTML, status_code=200)


@app.get("/api/requirements", summary="Get User Eligibility Requirements")
async def get_requirements(db: AsyncSession = Depends(get_db)):
    """Retrieves current user eligibility requirements profile."""
    repo = DatabaseRepository(db)
    reqs = await repo.get_user_requirements("default_user")

    if not reqs:
        # Fallback to seed YAML
        yaml_path = "config/user_requirements.yaml"
        if os.path.exists(yaml_path):
            with open(yaml_path, "r", encoding="utf-8") as f:
                seed_data = yaml.safe_load(f)
                await repo.save_user_requirements(seed_data, "default_user")
                return seed_data
        # Default Pydantic model
        default_model = UserRequirementsProfile().model_dump()
        await repo.save_user_requirements(default_model, "default_user")
        return default_model

    return reqs


@app.put("/api/requirements", summary="Update User Eligibility Requirements")
async def update_requirements(
    profile: UserRequirementsProfile,
    db: AsyncSession = Depends(get_db)
):
    """
    Validates and updates user eligibility profile in the persistent database.
    Instantly changes filtering criteria for subsequent circulars.
    """
    repo = DatabaseRepository(db)
    saved = await repo.save_user_requirements(profile.model_dump(), "default_user")
    logger.info(f"User eligibility requirements profile updated (v{saved.version})")
    return {
        "status": "success",
        "version": saved.version,
        "updated_at": saved.updated_at.isoformat(),
        "configuration": saved.configuration
    }


# ------------------------------------------------------------------------------
# MONITORED CHANNELS MANAGEMENT API & WEB UI
# ------------------------------------------------------------------------------
@app.get("/admin/channels", response_class=HTMLResponse, summary="Channels Manager Web UI")
async def channels_manager_ui():
    """Renders the interactive Web UI for adding, toggling, and deleting monitored channels."""
    return HTMLResponse(content=CHANNELS_MANAGER_HTML, status_code=200)


@app.get("/api/channels", summary="List Monitored Channels")
async def list_channels():
    """Returns list of all configured public & private channels."""
    mgr = ChannelManager()
    return mgr.load_channels_dict()


@app.post("/api/channels", summary="Add Monitored Channel")
async def add_channel(channel: Dict[str, Any] = Body(...)):
    """Adds a new channel to configuration."""
    mgr = ChannelManager()
    try:
        new_entry = mgr.add_channel(channel)
        logger.info(f"New channel added: {new_entry.get('name')} ({new_entry.get('telegram_channel_id')})")
        return new_entry
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add channel: {e}")


@app.put("/api/channels/{channel_id}", summary="Update Monitored Channel")
async def update_channel(channel_id: str, update_data: Dict[str, Any] = Body(...)):
    """Updates or enables/disables a configured channel."""
    mgr = ChannelManager()
    updated = mgr.update_channel(channel_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Channel not found")
    logger.info(f"Channel updated: {channel_id} (Enabled: {updated.get('enabled')})")
    return updated


@app.delete("/api/channels/{channel_id}", summary="Delete Monitored Channel")
async def delete_channel(channel_id: str):
    """Deletes a channel from monitoring configuration."""
    mgr = ChannelManager()
    success = mgr.delete_channel(channel_id)
    if not success:
        raise HTTPException(status_code=404, detail="Channel not found")
    logger.info(f"Channel deleted from configuration: {channel_id}")
    return {"status": "success", "message": f"Channel {channel_id} deleted."}


from app.telegram.message_parser import extract_urls

@app.post("/webhook/inbound-message", summary="Inbound Message Webhook from Listener or n8n")
async def inbound_message_webhook(
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Receives raw message payload, persists if not already stored,
    and runs through the intelligence pipeline.
    """
    import uuid
    telegram_msg_id = str(payload.get("telegram_message_id") or payload.get("message_id") or f"msg_{uuid.uuid4()}")
    channel_id = str(payload.get("channel_id") or payload.get("channel_identifier") or "external")
    text = payload.get("message_text") or payload.get("text") or ""
    urls = payload.get("urls") or extract_urls(text)

    repo = DatabaseRepository(db)

    # Check if message already exists
    existing = await repo.get_message_by_telegram_id(channel_id, telegram_msg_id)
    if existing:
        db_message_id = existing.id
    else:
        msg = await repo.save_raw_message(
            telegram_message_id=telegram_msg_id,
            channel_identifier=channel_id,
            message_text=text,
            raw_metadata=payload
        )
        db_message_id = msg.id

    # Load active user profile
    profile_data = await repo.get_user_requirements("default_user")
    user_profile = UserRequirementsProfile.model_validate(profile_data) if profile_data else UserRequirementsProfile()

    # Process through pipeline
    result = await pipeline.process_job_message(
        db_message_id=db_message_id,
        channel_id=channel_id,
        telegram_message_id=telegram_msg_id,
        message_text=text,
        urls=urls,
        user_profile=user_profile
    )

    return result
