"""
Database Repository Module
Provides clean CRUD operations across the 7 logical tables.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import (
    Channel,
    ProcessedMessage,
    Job,
    Source,
    Alert,
    Failure,
    UserRequirement,
    utc_now
)

logger = logging.getLogger(__name__)


class DatabaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # --------------------------------------------------------------------------
    # CHANNELS
    # --------------------------------------------------------------------------
    async def get_or_create_channel(
        self,
        telegram_channel_id: str,
        name: str,
        channel_type: str = "public",
        enabled: bool = True
    ) -> Channel:
        stmt = select(Channel).where(Channel.telegram_channel_id == str(telegram_channel_id))
        result = await self.session.execute(stmt)
        channel = result.scalar_one_or_none()

        if not channel:
            channel = Channel(
                telegram_channel_id=str(telegram_channel_id),
                name=name,
                type=channel_type,
                enabled=enabled
            )
            self.session.add(channel)
            await self.session.commit()
            await self.session.refresh(channel)
        return channel

    async def list_monitored_channels(self, enabled_only: bool = True) -> List[Channel]:
        stmt = select(Channel)
        if enabled_only:
            stmt = stmt.where(Channel.enabled == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # --------------------------------------------------------------------------
    # PROCESSED MESSAGES
    # --------------------------------------------------------------------------
    async def save_raw_message(
        self,
        telegram_message_id: str,
        channel_identifier: str,
        message_text: Optional[str],
        raw_metadata: Optional[Dict[str, Any]],
        channel_id: Optional[str] = None
    ) -> ProcessedMessage:
        """Immediately persists incoming message before expensive processing."""
        msg = ProcessedMessage(
            channel_id=channel_id,
            telegram_message_id=str(telegram_message_id),
            channel_identifier=str(channel_identifier),
            message_text=message_text,
            raw_metadata=raw_metadata,
            processing_status="PENDING"
        )
        self.session.add(msg)
        await self.session.commit()
        await self.session.refresh(msg)
        return msg

    async def update_message_status(
        self,
        message_id: str,
        status: str,
        error: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> None:
        stmt = (
            update(ProcessedMessage)
            .where(ProcessedMessage.id == message_id)
            .values(
                processing_status=status,
                error=error,
                job_id=job_id
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_message_by_telegram_id(
        self,
        channel_identifier: str,
        telegram_message_id: str
    ) -> Optional[ProcessedMessage]:
        stmt = select(ProcessedMessage).where(
            and_(
                ProcessedMessage.channel_identifier == str(channel_identifier),
                ProcessedMessage.telegram_message_id == str(telegram_message_id)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # --------------------------------------------------------------------------
    # JOBS & DEDUPLICATION
    # --------------------------------------------------------------------------
    async def get_job_by_fingerprint(self, fingerprint: str) -> Optional[Job]:
        stmt = select(Job).where(Job.fingerprint == fingerprint)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_job(
        self,
        fingerprint: str,
        organization: Optional[str],
        post_name: Optional[str],
        notification_number: Optional[str],
        structured_data: Dict[str, Any],
        eligibility_status: str = "UNCERTAIN",
        eligibility_explanation: Optional[Dict[str, Any]] = None,
        ai_provider_used: Optional[str] = None,
        confidence: float = 0.0
    ) -> Job:
        job = Job(
            fingerprint=fingerprint,
            organization=organization,
            post_name=post_name,
            notification_number=notification_number,
            structured_data=structured_data,
            eligibility_status=eligibility_status,
            eligibility_explanation=eligibility_explanation,
            ai_provider_used=ai_provider_used,
            confidence=confidence
        )
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get_job_by_id(self, job_id: str) -> Optional[Job]:
        stmt = select(Job).where(Job.id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # --------------------------------------------------------------------------
    # SOURCES
    # --------------------------------------------------------------------------
    async def add_source(
        self,
        job_id: str,
        url: str,
        source_type: str = "unknown",
        verification_status: str = "unverified",
        canonical_url: Optional[str] = None,
        retrieval_method: Optional[str] = None,
        source_confidence: float = 0.0
    ) -> Source:
        source = Source(
            job_id=job_id,
            url=url,
            canonical_url=canonical_url,
            source_type=source_type,
            verification_status=verification_status,
            retrieval_method=retrieval_method,
            source_confidence=source_confidence
        )
        self.session.add(source)
        await self.session.commit()
        await self.session.refresh(source)
        return source

    # --------------------------------------------------------------------------
    # ALERTS
    # --------------------------------------------------------------------------
    async def record_alert(
        self,
        job_id: str,
        telegram_chat_id: str,
        alert_type: str,
        telegram_message_id: Optional[str] = None
    ) -> Alert:
        alert = Alert(
            job_id=job_id,
            telegram_chat_id=str(telegram_chat_id),
            alert_type=alert_type,
            telegram_message_id=telegram_message_id,
            delivery_status="SENT"
        )
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    async def has_alert_been_sent(self, job_id: str, alert_type: str) -> bool:
        stmt = select(Alert).where(
            and_(
                Alert.job_id == job_id,
                Alert.alert_type == alert_type
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    # --------------------------------------------------------------------------
    # FAILURES & RETRIES
    # --------------------------------------------------------------------------
    async def log_failure(
        self,
        processing_id: str,
        component: str,
        error: str,
        failure_type: str = "transient",
        error_class: Optional[str] = None,
        max_retries: int = 3
    ) -> Failure:
        failure = Failure(
            processing_id=processing_id,
            component=component,
            error=error,
            failure_type=failure_type,
            error_class=error_class,
            max_retries=max_retries,
            status="pending"
        )
        self.session.add(failure)
        await self.session.commit()
        await self.session.refresh(failure)
        return failure

    # --------------------------------------------------------------------------
    # USER REQUIREMENTS (EDITABLE PROFILE)
    # --------------------------------------------------------------------------
    async def get_user_requirements(self, profile_id: str = "default_user") -> Optional[Dict[str, Any]]:
        stmt = select(UserRequirement).where(UserRequirement.id == profile_id)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row:
            return row.configuration
        return None

    async def save_user_requirements(
        self,
        configuration: Dict[str, Any],
        profile_id: str = "default_user"
    ) -> UserRequirement:
        stmt = select(UserRequirement).where(UserRequirement.id == profile_id)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()

        if row:
            row.configuration = configuration
            row.version += 1
            row.updated_at = utc_now()
        else:
            row = UserRequirement(
                id=profile_id,
                configuration=configuration,
                version=1
            )
            self.session.add(row)

        await self.session.commit()
        await self.session.refresh(row)
        return row
