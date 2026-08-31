"""
Telegram Ingestion Listener (Component A)
Uses Telethon MTProto user-client protocol.
Monitors public channels and user-joined private channels.
Immediately persists raw messages to PostgreSQL `processed_messages` before downstream processing.
Dispatches new-message events to n8n webhook or the internal pipeline.
"""
import logging
import asyncio
from typing import Optional, Callable
import httpx
from telethon import TelegramClient, events
from telethon.sessions import StringSession

from config.settings import settings
from app.telegram.message_parser import parse_telethon_message, ParsedTelegramMessage
from app.telegram.channel_manager import ChannelManager
from app.database.connection import AsyncSessionLocal
from app.database.repository import DatabaseRepository

logger = logging.getLogger(__name__)


class TelegramListener:
    def __init__(
        self,
        api_id: Optional[int] = settings.TELEGRAM_API_ID,
        api_hash: Optional[str] = settings.TELEGRAM_API_HASH,
        session_string: Optional[str] = settings.TELEGRAM_SESSION,
        n8n_webhook_url: str = settings.N8N_WEBHOOK_URL
    ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_string = session_string
        self.n8n_webhook_url = n8n_webhook_url
        self.client: Optional[TelegramClient] = None
        self.channel_manager = ChannelManager()
        self.is_running = False

    def is_configured(self) -> bool:
        return bool(
            self.api_id and
            self.api_hash and
            self.session_string and
            not self.session_string.startswith("your_telethon_")
        )

    async def start(self, on_message_callback: Optional[Callable[[ParsedTelegramMessage], None]] = None) -> None:
        """Starts Telethon client and attaches message listeners."""
        if not self.is_configured():
            logger.warning("TelegramListener is NOT configured (missing API ID/Hash/Session). Listener running in simulated mode.")
            self.is_running = True
            return

        try:
            self.client = TelegramClient(
                StringSession(self.session_string),
                int(self.api_id),
                self.api_hash
            )
            await self.client.connect()

            if not await self.client.is_user_authorized():
                logger.error("Telethon session string is invalid or expired. Re-run scripts/generate_session.py")
                return

            me = await self.client.get_me()
            logger.info(f"Connected to Telegram MTProto as {me.first_name} (@{me.username}) [ID: {me.id}]")

            # Discover configured channels
            channels = self.channel_manager.load_channels()
            target_ids = [ch.telegram_channel_id for ch in channels if ch.enabled]
            logger.info(f"Monitoring {len(target_ids)} channels: {target_ids}")

            @self.client.on(events.NewMessage)
            async def handle_new_message(event):
                await self._process_inbound_event(event, on_message_callback)

            self.is_running = True
            logger.info("Telegram listener is actively streaming new messages...")
        except Exception as e:
            logger.error(f"Error starting Telegram listener: {e}", exc_info=True)

    async def _process_inbound_event(self, event, callback=None) -> None:
        """Parses, persists immediately, and triggers processing."""
        try:
            parsed = parse_telethon_message(event)
            logger.info(f"Inbound Telegram message {parsed.telegram_message_id} from {parsed.channel_name} ({parsed.pre_filter_category})")

            # MANDATORY SPECIFICATION RULE: Immediately persist before expensive processing
            async with AsyncSessionLocal() as session:
                repo = DatabaseRepository(session)
                saved_msg = await repo.save_raw_message(
                    telegram_message_id=parsed.telegram_message_id,
                    channel_identifier=parsed.channel_id,
                    message_text=parsed.message_text,
                    raw_metadata=parsed.to_dict()
                )
                msg_uuid = saved_msg.id

            # Dispatch to n8n Webhook
            await self._dispatch_to_n8n(parsed, msg_uuid)

            # Invoke local callback if registered
            if callback:
                await callback(parsed, msg_uuid)

        except Exception as e:
            logger.error(f"Error processing inbound Telegram message: {e}", exc_info=True)

    async def _dispatch_to_n8n(self, parsed: ParsedTelegramMessage, db_message_id: str) -> None:
        """Sends new-message event to n8n orchestrator."""
        if not self.n8n_webhook_url:
            return

        payload = {
            "db_message_id": db_message_id,
            "telegram_message_id": parsed.telegram_message_id,
            "channel_id": parsed.channel_id,
            "channel_name": parsed.channel_name,
            "timestamp": parsed.timestamp.isoformat(),
            "message_text": parsed.message_text,
            "urls": parsed.urls,
            "media_metadata": parsed.media_metadata,
            "pre_filter_category": parsed.pre_filter_category,
            "is_potential_job": parsed.is_potential_job
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                headers = {}
                if settings.N8N_API_KEY:
                    headers["X-N8N-API-KEY"] = settings.N8N_API_KEY
                resp = await client.post(self.n8n_webhook_url, json=payload, headers=headers)
                logger.info(f"Dispatched event to n8n webhook: HTTP {resp.status_code}")
        except Exception as e:
            # Network issue dispatching to n8n: message is safely in DB; will be retried
            logger.warning(f"Could not reach n8n webhook: {e}")

    async def stop(self) -> None:
        if self.client and self.client.is_connected():
            await self.client.disconnect()
        self.is_running = False
        logger.info("Telegram listener disconnected.")
