"""
End-to-End Orchestrator Pipeline
Orchestrates the entire intelligence flow:
RECEIVE -> STORE -> ACQUIRE -> AI EXTRACT -> DEDUP -> EVALUATE -> ALERT -> AUDIT
Used directly by FastAPI webhook endpoints and n8n orchestration.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.content.acquisition_manager import ContentAcquisitionManager
from app.content.online_enricher import OnlineJobEnricher
from app.ai.router import AIRouter
from app.ai.schemas import JobExtractionSchema
from app.deduplication.fingerprint import compute_job_fingerprint
from app.eligibility.models import UserRequirementsProfile
from app.eligibility.evaluator import EligibilityEvaluator
from app.notifications.telegram_bot import TelegramNotifier
from app.database.connection import AsyncSessionLocal
from app.database.repository import DatabaseRepository
from app.reliability.retry import classify_error

logger = logging.getLogger(__name__)


class ProcessingPipeline:
    def __init__(self):
        self.acquisition_manager = ContentAcquisitionManager()
        self.enricher = OnlineJobEnricher()
        self.ai_router = AIRouter()
        self.notifier = TelegramNotifier()

    async def process_job_message(
        self,
        db_message_id: str,
        channel_id: str,
        telegram_message_id: str,
        message_text: str,
        urls: list[str],
        user_profile: UserRequirementsProfile
    ) -> Dict[str, Any]:
        """
        Executes complete pipeline on an inbound message.
        """
        async with AsyncSessionLocal() as session:
            repo = DatabaseRepository(session)
            await repo.update_message_status(db_message_id, "EXTRACTING")

            try:
                # 1. CONTENT ACQUISITION (Levels 1 - 4 Fallbacks)
                # Build search query terms from message lines if available
                query_terms = [w for w in message_text.split() if len(w) > 3][:10]
                content = await self.acquisition_manager.acquire_content(
                    urls=urls,
                    query_terms=query_terms,
                    fallback_raw_text=message_text
                )

                if not content or not content.content_text:
                    err_msg = "Content acquisition failed across all 4 fallback levels."
                    await repo.update_message_status(db_message_id, "FAILED", error=err_msg)
                    await repo.log_failure(db_message_id, "content_acquisition", err_msg, "content_unavailable")
                    return {"status": "FAILED", "error": err_msg}

                # 2. AI EXTRACTION WITH MULTI-PROVIDER FALLBACK
                job_data, provider_used, ai_err = await self.ai_router.extract(content)

                if not job_data:
                    # Place in AI_REVIEW_REQUIRED
                    await repo.update_message_status(db_message_id, "AI_REVIEW_REQUIRED", error=ai_err)
                    await repo.log_failure(db_message_id, "ai_extraction", str(ai_err), "ai_failure")
                    return {"status": "AI_REVIEW_REQUIRED", "error": ai_err}

                # If content is classified as non-job (e.g. exam result or answer key)
                if not job_data.is_job:
                    await repo.update_message_status(db_message_id, "NON_JOB")
                    return {"status": "NON_JOB", "message": "Content classified as non-job."}

                # 2.5 ONLINE SEARCH ENRICHMENT
                # If key details are missing, automatically search the web and merge newly discovered official facts.
                job_data, content = await self.enricher.enrich_job_if_needed(job_data, content)

                # 3. DEDUPLICATION VIA CRYPTOGRAPHIC FINGERPRINT
                fingerprint = compute_job_fingerprint(job_data, content.canonical_url)
                existing_job = await repo.get_job_by_fingerprint(fingerprint)

                if existing_job:
                    logger.info(f"Duplicate job detected (Fingerprint {fingerprint[:12]}...). Attaching source without re-alerting.")
                    await repo.add_source(
                        job_id=existing_job.id,
                        url=content.source_url,
                        source_type=content.source_type,
                        verification_status=content.verification_status,
                        canonical_url=content.canonical_url,
                        retrieval_method=content.retrieval_method,
                        source_confidence=content.source_confidence
                    )
                    await repo.update_message_status(db_message_id, "PROCESSED", job_id=existing_job.id)
                    return {"status": "DUPLICATE", "job_id": existing_job.id}

                # 4. DETERMINISTIC ELIGIBILITY ENGINE
                evaluator = EligibilityEvaluator(user_profile)
                decision = evaluator.evaluate(job_data)

                # Persist new Job record
                saved_job = await repo.create_job(
                    fingerprint=fingerprint,
                    organization=job_data.organization or "Unknown Organization",
                    post_name=job_data.post_name or "Recruitment Notification",
                    notification_number=job_data.notification_number,
                    structured_data=job_data.model_dump(),
                    eligibility_status=decision.status,
                    eligibility_explanation=decision.model_dump(),
                    ai_provider_used=provider_used,
                    confidence=getattr(job_data, "confidence", 0.9)
                )

                # Attach source
                await repo.add_source(
                    job_id=saved_job.id,
                    url=content.source_url,
                    source_type=content.source_type,
                    verification_status=content.verification_status,
                    canonical_url=content.canonical_url,
                    retrieval_method=content.retrieval_method,
                    source_confidence=content.source_confidence
                )

                # Link message to created job
                await repo.update_message_status(db_message_id, "PROCESSED", job_id=saved_job.id)

                # 5. DISPATCH OUTGOING ALERTS
                if decision.action_recommended in ("ALERT", "UNCERTAIN_ALERT"):
                    # Check if alert already recorded for this job
                    has_alert = await repo.has_alert_been_sent(saved_job.id, decision.status)
                    if not has_alert:
                        msg_id = await self.notifier.send_job_alert(job_data, decision, content)
                        if msg_id:
                            await repo.record_alert(
                                job_id=saved_job.id,
                                telegram_chat_id=str(self.notifier.default_chat_id or "default"),
                                alert_type=decision.status,
                                telegram_message_id=msg_id
                            )

                return {
                    "status": "SUCCESS",
                    "job_id": saved_job.id,
                    "eligibility_status": decision.status,
                    "action": decision.action_recommended
                }

            except Exception as e:
                err_text = str(e)
                logger.error(f"Pipeline failure on message {db_message_id}: {err_text}", exc_info=True)
                await repo.update_message_status(db_message_id, "FAILED", error=err_text)
                await repo.log_failure(db_message_id, "pipeline", err_text, classify_error(e))
                return {"status": "FAILED", "error": err_text}
