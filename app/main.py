"""
FastAPI Main Application
Provides:
- GET /health: Lightweight Render health check (HTTP 200, <10ms, no heavy DB/Telegram calls)
- GET /api/health/detailed: Deep health inspect for DB, AI providers, and queues
- GET /api/requirements & PUT /api/requirements: Persistent user profile editing API
- GET /admin/requirements: Interactive Web Dashboard for requirements editing
- GET /admin/channels: Interactive Web Dashboard for channels management & live queue
- POST /webhook/inbound-message: n8n webhook receiver for new messages
- POST /api/pipeline/process: Manual or orchestrated trigger for processing messages
- POST /api/channels/fetch-recent: Trigger immediate scan of all monitored channels
- GET /api/messages: List recent messages and processing status
- GET /api/jobs: List extracted jobs and eligibility decisions
- Application startup/shutdown hooks for database, Telethon listener, and scheduled sync
"""
import os
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List
import yaml
from fastapi import FastAPI, Depends, HTTPException, Body, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from config.settings import settings
from app.database.connection import init_db, get_db, AsyncSessionLocal
from app.database.repository import DatabaseRepository
from app.database.models import ProcessedMessage, Job
from app.eligibility.models import UserRequirementsProfile
from app.eligibility.evaluator import EligibilityEvaluator
from app.ai.schemas import JobExtractionSchema
from app.telegram.listener import TelegramListener
from app.telegram.channel_manager import ChannelManager
from app.telegram.message_parser import extract_urls, ParsedTelegramMessage
from app.pipeline import ProcessingPipeline
from app.web.templates.requirements_editor import REQUIREMENTS_EDITOR_HTML
from app.web.templates.channels_manager import CHANNELS_MANAGER_HTML
from app.web.templates.jobs_dashboard import JOBS_DASHBOARD_HTML

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app.main")

# Global singleton components
telegram_listener = TelegramListener()
pipeline = ProcessingPipeline()


async def process_inbound_message_callback(parsed: ParsedTelegramMessage, msg_uuid: str) -> None:
    """
    Automatic callback executed whenever a message is ingested from Telethon or Web Scraper.
    Loads active user requirements and processes message through the intelligence pipeline.
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = DatabaseRepository(session)
            profile_data = await repo.get_user_requirements("default_user")
            user_profile = UserRequirementsProfile.model_validate(profile_data) if profile_data else UserRequirementsProfile()

        await pipeline.process_job_message(
            db_message_id=msg_uuid,
            channel_id=parsed.channel_id,
            telegram_message_id=parsed.telegram_message_id,
            message_text=parsed.message_text,
            urls=parsed.urls,
            user_profile=user_profile
        )
    except Exception as e:
        logger.error(f"Error in automatic message processing callback for message {msg_uuid}: {e}", exc_info=True)


async def periodic_channel_sync():
    """Background task to periodically poll configured channels for new messages."""
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        try:
            logger.info("Executing scheduled periodic channel sync...")
            await telegram_listener.sync_all_channels(on_message_callback=process_inbound_message_callback)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in periodic channel sync: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("Initializing Personal Job Intelligence System...")
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Database initialization error on startup: {e}")

    # Start Telegram multi-tier listener and background sync
    sync_task = None
    try:
        asyncio.create_task(telegram_listener.start(on_message_callback=process_inbound_message_callback))
        sync_task = asyncio.create_task(periodic_channel_sync())
    except Exception as e:
        logger.warning(f"Could not start Telegram listener tasks: {e}")

    yield

    # SHUTDOWN
    logger.info("Shutting down system...")
    if sync_task:
        sync_task.cancel()
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
# ROOT REDIRECT & JOBS PORTAL UI
# ------------------------------------------------------------------------------
@app.get("/", summary="Root Redirect to Jobs Portal")
async def root_redirect():
    """Redirects root URL directly to the jobs intelligence portal."""
    return RedirectResponse(url="/jobs")


@app.get("/jobs", response_class=HTMLResponse, summary="Jobs Intelligence Portal Web UI")
@app.get("/admin/jobs", response_class=HTMLResponse, summary="Jobs Intelligence Portal Web UI")
@app.get("/plan-to-apply", response_class=HTMLResponse, summary="Plan to Apply Web UI")
@app.get("/applied", response_class=HTMLResponse, summary="Applied Jobs Web UI")
async def jobs_dashboard_ui():
    """Renders the rich, interactive Jobs Intelligence Portal with fee filters, apply links, and telegram breakdown."""
    return HTMLResponse(content=JOBS_DASHBOARD_HTML, status_code=200)


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
        "environment": settings.ENVIRONMENT
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
        "telegram_mtproto_connected": telegram_listener.mtproto_connected,
        "telegram_listener_configured": telegram_listener.is_configured(),
        "environment": settings.ENVIRONMENT
    }


# ------------------------------------------------------------------------------
# USER ELIGIBILITY REQUIREMENTS EDITING API & WEB UI
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
        yaml_path = "config/user_requirements.yaml"
        if os.path.exists(yaml_path):
            with open(yaml_path, "r", encoding="utf-8") as f:
                seed_data = yaml.safe_load(f)
                await repo.save_user_requirements(seed_data, "default_user")
                return seed_data
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


@app.post("/api/requirements/re-evaluate", summary="Re-evaluate All Jobs with Current Profile")
async def reevaluate_all_jobs(db: AsyncSession = Depends(get_db)):
    """
    Re-runs deterministic criteria evaluation across all jobs currently stored in the database
    against the active user eligibility profile.
    """
    repo = DatabaseRepository(db)
    profile_data = await repo.get_user_requirements("default_user")
    user_profile = UserRequirementsProfile.model_validate(profile_data) if profile_data else UserRequirementsProfile()
    evaluator = EligibilityEvaluator(user_profile)

    query = select(Job)
    res = await db.execute(query)
    jobs = res.scalars().all()

    counts = {"ELIGIBLE": 0, "UNCERTAIN": 0, "NOT_ELIGIBLE": 0, "total": len(jobs)}
    for j in jobs:
        if not j.structured_data:
            continue
        try:
            extraction = JobExtractionSchema.model_validate(j.structured_data)
            decision = evaluator.evaluate(extraction)
            j.eligibility_status = decision.status
            j.eligibility_explanation = decision.model_dump()
            counts[decision.status] = counts.get(decision.status, 0) + 1
        except Exception as e:
            logger.warning(f"Failed to re-evaluate job {j.id}: {e}")

    await db.commit()
    logger.info(f"Re-evaluated {len(jobs)} jobs: {counts}")
    return {
        "status": "success",
        "message": f"Successfully re-evaluated {len(jobs)} circulars against updated profile.",
        "counts": counts
    }


@app.post("/api/requirements/reset", summary="Reset Requirements to Factory Defaults")
async def reset_requirements_to_defaults(db: AsyncSession = Depends(get_db)):
    """Resets user eligibility requirements to the baseline config/user_requirements.yaml."""
    repo = DatabaseRepository(db)
    yaml_path = "config/user_requirements.yaml"
    if os.path.exists(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as f:
            seed_data = yaml.safe_load(f)
    else:
        seed_data = UserRequirementsProfile().model_dump()

    saved = await repo.save_user_requirements(seed_data, "default_user")
    logger.info(f"User eligibility profile reset to factory defaults (v{saved.version})")
    return {
        "status": "success",
        "version": saved.version,
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


@app.post("/api/channels/fetch-recent", summary="Fetch Recent Messages Now")
async def fetch_recent_messages(limit: int = 15):
    """
    Triggers immediate scan, parsing, and pipeline processing across all configured channels.
    """
    result = await telegram_listener.sync_all_channels(
        on_message_callback=process_inbound_message_callback,
        limit_per_channel=limit
    )
    return {
        "status": "success",
        "result": result
    }


# ------------------------------------------------------------------------------
# INGESTION & PIPELINE WEBHOOKS
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
# AUDIT & QUEUE INSPECTION ENDPOINTS
# ------------------------------------------------------------------------------
@app.get("/api/messages", summary="List Ingested Messages")
async def list_messages(limit: int = 50, db: AsyncSession = Depends(get_db)):
    """Returns recent ingested messages with processing status and timestamps."""
    query = select(ProcessedMessage).order_by(ProcessedMessage.received_at.desc()).limit(limit)
    res = await db.execute(query)
    items = res.scalars().all()
    return [
        {
            "id": m.id,
            "telegram_message_id": m.telegram_message_id,
            "channel_identifier": m.channel_identifier,
            "message_text": m.message_text[:200] if m.message_text else "",
            "processing_status": m.processing_status,
            "error": m.error,
            "job_id": m.job_id,
            "received_at": m.received_at.isoformat() if m.received_at else None
        }
        for m in items
    ]


def check_fee_status(fee_list: list) -> dict:
    """
    Classifies application fee details for frontend filtering.

    BUG FIX: The original used per-character digit comparison which caused false positives
    (e.g., advertisement numbers, dates, or phone numbers in the fee text were treated as fees).
    Now uses regex to extract actual numeric values after currency symbols/keywords.

    Empty fee list → 'Fee not stated' (NOT falsely 'Free')
    Fee = 0 / nil / free → is_free = True
    Fee > 0 → has_fee = True, is_free = False
    """
    import re

    if not fee_list:
        return {
            "has_fee": False,
            "is_free": False,
            "label": "Fee not stated",
            "amount": None
        }

    fee_text = " ".join(str(f) for f in fee_list).lower()

    # 1. Check for explicit nil/free/zero declarations (highest priority)
    nil_patterns = [
        r"\bnil\b", r"\bfree\b", r"\bno fee\b", r"\bno application fee\b",
        r"rs\.?\s*0\b", r"₹\s*0\b", r"\b0/-\b", r"waived",
    ]
    is_explicitly_free = any(re.search(p, fee_text) for p in nil_patterns)

    # 2. Extract actual numeric fee amounts (₹500, Rs. 100, 250/-, fee: 300)
    # Pattern: currency symbol or keyword followed by number, OR number followed by /-
    amount_patterns = [
        r"(?:rs\.?\s*|₹\s*|inr\s*)(\d[\d,]*)",   # Rs. 500, ₹1,000
        r"(\d[\d,]*)\s*/-",                         # 500/-
        r"(?:fee\s*[=:]\s*)(\d[\d,]*)",             # fee: 500
    ]
    amounts = []
    for p in amount_patterns:
        for m in re.finditer(p, fee_text):
            try:
                # Remove commas from numbers like 1,000
                amounts.append(int(m.group(1).replace(",", "")))
            except (ValueError, IndexError):
                pass

    has_paid = any(a > 0 for a in amounts) if amounts else False
    # If all extracted amounts are 0, treat as free
    if amounts and all(a == 0 for a in amounts):
        is_explicitly_free = True

    # 3. Check for SC/ST exemptions (indicates there IS a fee for general, partial exemptions)
    has_exemption = bool(re.search(r"\b(?:sc|st|pwd|obc|ews)\b", fee_text) and re.search(r"\bexempt\b|\bnil\b|\bno fee\b", fee_text))

    if is_explicitly_free and not has_paid:
        label = "No application fee"
    elif has_exemption and has_paid:
        label = "Fee varies by category"
    elif has_paid:
        # Show the minimum visible fee amount
        first_amount = min(a for a in amounts if a > 0)
        label = f"Fee: ₹{first_amount:,}"
    elif is_explicitly_free:
        label = "No application fee"
    else:
        label = "Fee details unclear"

    # If ANY non-zero fee was found, is_free must be False — category exemptions don't count
    final_is_free = is_explicitly_free and not has_paid

    fee_amount = None
    if final_is_free:
        fee_amount = 0
    elif has_paid:
        fee_amount = min(a for a in amounts if a > 0)

    return {
        "has_fee": has_paid,
        "is_free": final_is_free,
        "label": label,
        "amount": fee_amount
    }



def resolve_job_urls(job: Job):
    """Resolves primary apply portal and official notification PDF URLs."""
    sd = job.structured_data or {}
    apply_url = sd.get("official_apply_url")
    pdf_url = sd.get("official_notification_url")
    sources_data = []

    if job.sources:
        for s in job.sources:
            sources_data.append({
                "url": s.url,
                "canonical_url": s.canonical_url,
                "source_type": s.source_type,
                "verification_status": s.verification_status
            })
            if not apply_url:
                if s.canonical_url:
                    apply_url = s.canonical_url
                elif s.url:
                    apply_url = s.url
            if not pdf_url and s.url and s.url.lower().endswith(".pdf"):
                pdf_url = s.url

    if not apply_url and sd.get("source_urls"):
        apply_url = sd["source_urls"][0]
    if not pdf_url and sd.get("source_urls"):
        for u in sd["source_urls"]:
            if u.lower().endswith(".pdf"):
                pdf_url = u
                break

    return apply_url, pdf_url, sources_data


def generate_short_description(job: Job) -> str:
    """Generates a concise 3-4 line job overview explaining what the job is."""
    sd = job.structured_data or {}
    org = job.organization or "Government Organization"
    post = job.post_name or "Recruitment Post"
    job_type = (sd.get("job_type") or "government").replace("_", " ").title()
    vacancies = sd.get("vacancies")
    vac_str = f" for {vacancies} declared vacancies" if vacancies else ""

    part1 = f"{org} is recruiting for {post}{vac_str} under a {job_type} cadre."

    quals = sd.get("qualification") or []
    branches = sd.get("accepted_branches") or []
    if quals:
        qual_disp = ", ".join(quals[:2])
        if branches:
            part2 = f"Requires educational qualification of {qual_disp} ({', '.join(branches[:2])})."
        else:
            part2 = f"Requires educational qualification of {qual_disp}."
    else:
        part2 = "Educational requirements are as declared in official notification."

    exp_req = sd.get("experience_required")
    exp_years = sd.get("experience_years_min")
    if exp_req is False or exp_years == 0:
        exp_disp = "Freshers and entry-level applicants are eligible to apply."
    elif exp_years:
        exp_disp = f"Requires minimum of {exp_years} year(s) relevant experience."
    else:
        exp_disp = "Prior experience terms as specified in recruitment circular."

    age_max = sd.get("age_max")
    age_disp = f" Maximum age limit is {age_max} years." if age_max else ""
    part3 = f"{exp_disp}{age_disp}"

    sal = sd.get("salary") or sd.get("pay_level")
    sal_disp = f" Pay scale: {sal}." if sal else ""
    stages = sd.get("selection_process") or []
    stage_disp = f" Selection mode: {', '.join(stages[:2])}." if stages else ""
    deadline = sd.get("application_deadline")
    dl_disp = f" Apply by {deadline}." if deadline else ""

    part4 = f"{sal_disp}{stage_disp}{dl_disp}".strip()

    parts = [p for p in [part1, part2, part3, part4] if p]
    return " ".join(parts)


@app.get("/api/jobs", summary="List Extracted Jobs with Full Intelligence")
async def list_jobs(
    status: Optional[str] = None,
    fee_type: Optional[str] = "all",
    search: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns extracted jobs with full Telegram-level structured data,
    resolved apply & notification URLs, fee classification, and eligibility criteria breakdown.
    """
    query = select(Job).options(selectinload(Job.sources)).order_by(Job.created_at.desc())

    if status and status.upper() != "ALL":
        query = query.where(Job.eligibility_status == status.upper())

    query = query.limit(limit)
    res = await db.execute(query)
    jobs = res.scalars().all()

    repo = DatabaseRepository(db)
    user_statuses = await repo.get_all_user_job_statuses()

    output = []
    for j in jobs:
        sd = j.structured_data or {}
        fee_info = check_fee_status(sd.get("application_fee") or [])
        apply_url, pdf_url, sources_data = resolve_job_urls(j)
        ujs = user_statuses.get(j.id)

        # Server-side fee filtering if requested
        if fee_type == "free" and not fee_info["is_free"]:
            continue
        elif fee_type == "paid" and fee_info["is_free"]:
            continue

        # Server-side search filtering if requested
        if search:
            s_low = search.lower()
            org = (j.organization or "").lower()
            post = (j.post_name or "").lower()
            notif = (j.notification_number or "").lower()
            if s_low not in org and s_low not in post and s_low not in notif:
                continue

        output.append({
            "id": j.id,
            "organization": j.organization,
            "post_name": j.post_name,
            "notification_number": j.notification_number,
            "eligibility_status": j.eligibility_status,
            "eligibility_explanation": j.eligibility_explanation,
            "structured_data": sd,
            "confidence": j.confidence,
            "ai_provider_used": j.ai_provider_used,
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "effective_apply_url": apply_url,
            "effective_notification_url": pdf_url,
            "sources": sources_data,
            "is_free": fee_info["is_free"],
            "has_fee": fee_info["has_fee"],
            "fee_label": fee_info["label"],
            "fee_amount": fee_info.get("amount"),
            "short_description": generate_short_description(j),
            "user_status": ujs["status"] if ujs else None,
            "applied_at": ujs["applied_at"] if ujs else None,
        })

    return output


@app.get("/api/user-job-statuses", summary="Get All User Job Statuses")
async def get_all_user_statuses(db: AsyncSession = Depends(get_db)):
    """Returns mapping of all job statuses: {job_id: {status: 'plan_to_apply'|'applied', applied_at: ...}}."""
    repo = DatabaseRepository(db)
    return await repo.get_all_user_job_statuses()


@app.post("/api/jobs/{job_id}/user-status", summary="Update User Job Status")
async def update_user_job_status(
    job_id: str,
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Sets or toggles the user's intent for a job:
    - status='plan_to_apply': marked as Want to Apply
    - status='applied': marked as Applied, automatically removed from Plan to Apply
    - status=None: removed from any list (returns to normal)
    """
    repo = DatabaseRepository(db)
    status = payload.get("status")
    return await repo.set_user_job_status(job_id, status)



@app.get("/api/jobs/{job_id}", summary="Get Detailed Job Intelligence")
async def get_job_detail(job_id: str, db: AsyncSession = Depends(get_db)):
    """Returns single job with complete intelligence data, sources, and telegram message link."""
    query = select(Job).options(selectinload(Job.sources), selectinload(Job.processed_messages)).where(Job.id == job_id)
    res = await db.execute(query)
    job = res.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    sd = job.structured_data or {}
    fee_info = check_fee_status(sd.get("application_fee") or [])
    apply_url, pdf_url, sources_data = resolve_job_urls(job)

    message_info = None
    if job.processed_messages:
        pm = job.processed_messages[0]
        message_info = {
            "telegram_message_id": pm.telegram_message_id,
            "channel_identifier": pm.channel_identifier,
            "message_text": pm.message_text[:500] if pm.message_text else None,
            "received_at": pm.received_at.isoformat() if pm.received_at else None
        }

    repo = DatabaseRepository(db)
    user_statuses = await repo.get_all_user_job_statuses()
    ujs = user_statuses.get(job.id)

    return {
        "id": job.id,
        "organization": job.organization,
        "post_name": job.post_name,
        "notification_number": job.notification_number,
        "eligibility_status": job.eligibility_status,
        "eligibility_explanation": job.eligibility_explanation,
        "structured_data": sd,
        "confidence": job.confidence,
        "ai_provider_used": job.ai_provider_used,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "effective_apply_url": apply_url,
        "effective_notification_url": pdf_url,
        "sources": sources_data,
        "is_free": fee_info["is_free"],
        "has_fee": fee_info["has_fee"],
        "fee_label": fee_info["label"],
        "fee_amount": fee_info.get("amount"),
        "short_description": generate_short_description(job),
        "user_status": ujs["status"] if ujs else None,
        "applied_at": ujs["applied_at"] if ujs else None,
        "message": message_info
    }


@app.delete("/api/jobs/{job_id}", summary="Delete Extracted Job")
async def delete_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Deletes a single job and cleans up associated sources, alerts, and statuses."""
    repo = DatabaseRepository(db)
    success = await repo.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    logger.info(f"Job deleted: {job_id}")
    return {"status": "success", "message": f"Job {job_id} deleted successfully."}


@app.delete("/api/jobs", summary="Delete Jobs by Status")
async def delete_jobs_by_status(
    status: str = "ELIGIBLE",
    db: AsyncSession = Depends(get_db)
):
    """Deletes all jobs matching the given eligibility status (defaults to ELIGIBLE)."""
    repo = DatabaseRepository(db)
    count = await repo.delete_jobs_by_status(status)
    logger.info(f"Deleted {count} jobs with status {status}")
    return {
        "status": "success",
        "deleted_count": count,
        "message": f"Successfully deleted {count} {status.lower()} opportunities."
    }

