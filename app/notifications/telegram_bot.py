"""
Outgoing Telegram Bot Service
Dispatches high-priority ELIGIBLE and UNCERTAIN recruitment alerts.
Provides user management commands (/profile, /help) for inspecting rules.
"""
import logging
from typing import Optional
import httpx

from config.settings import settings
from app.ai.schemas import JobExtractionSchema
from app.eligibility.models import EligibilityDecision
from app.content.normalizer import NormalizedContent
from app.notifications.formatters import (
    format_eligible_job_alert,
    format_uncertain_job_alert
)

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(
        self,
        bot_token: Optional[str] = settings.TELEGRAM_BOT_TOKEN,
        default_chat_id: Optional[int] = settings.TELEGRAM_ALERT_CHAT_ID
    ):
        self.bot_token = bot_token
        self.default_chat_id = default_chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None

    def is_configured(self) -> bool:
        return bool(self.bot_token and self.default_chat_id and not self.bot_token.startswith("1234567890:"))

    async def send_job_alert(
        self,
        job: JobExtractionSchema,
        decision: EligibilityDecision,
        content: Optional[NormalizedContent] = None,
        chat_id: Optional[int] = None
    ) -> Optional[str]:
        """
        Sends formatted alert based on decision status:
        - ELIGIBLE -> 🚨 ELIGIBLE JOB
        - UNCERTAIN -> 🟡 POSSIBLE MATCH — VERIFY
        Returns telegram_message_id on success, or None on failure/skipped.
        """
        target_chat = chat_id or self.default_chat_id
        if not target_chat:
            logger.warning("No target Telegram chat ID provided for alert dispatch.")
            return None

        if decision.status == "ELIGIBLE":
            text = format_eligible_job_alert(job, decision, content)
        elif decision.status == "UNCERTAIN":
            text = format_uncertain_job_alert(job, decision, content)
        else:
            # NOT_ELIGIBLE: do not alert
            return None

        return await self._send_html_message(target_chat, text)

    async def _send_html_message(self, chat_id: int, text: str) -> Optional[str]:
        if not self.is_configured():
            logger.info(f"[SIMULATED ALERT] (Bot not configured)\n{text}")
            return "simulated_msg_id_1001"

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": False
                    }
                )

                if resp.status_code == 200:
                    data = resp.json()
                    msg_id = str(data.get("result", {}).get("message_id"))
                    logger.info(f"Telegram alert dispatched successfully. Message ID: {msg_id}")
                    return msg_id
                else:
                    logger.error(f"Failed to send Telegram HTML alert: HTTP {resp.status_code} - {resp.text}")
                    # Fallback plain text if HTML had malformed tag
                    import re
                    plain_text = re.sub(r'<[^>]+>', '', text)
                    retry_resp = await client.post(
                        f"{self.base_url}/sendMessage",
                        json={
                            "chat_id": chat_id,
                            "text": plain_text,
                            "disable_web_page_preview": False
                        }
                    )
                    if retry_resp.status_code == 200:
                        data = retry_resp.json()
                        return str(data.get("result", {}).get("message_id"))
        except Exception as e:
            logger.error(f"Telegram alert exception: {e}", exc_info=True)

        return None
