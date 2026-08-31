"""
Database Models Module
Defines the 7 mandatory logical tables required by the Master Specification:
1. channels
2. processed_messages
3. jobs
4. sources
5. alerts
6. failures
7. user_requirements
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON,
    Float,
    Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Channel(Base):
    __tablename__ = "channels"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    telegram_channel_id = Column(String(128), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(32), nullable=False, default="public")  # 'public' or 'private'
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    messages = relationship("ProcessedMessage", back_populates="channel")


class ProcessedMessage(Base):
    __tablename__ = "processed_messages"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    channel_id = Column(String(64), ForeignKey("channels.id", ondelete="SET NULL"), nullable=True, index=True)
    telegram_message_id = Column(String(64), nullable=False, index=True)
    channel_identifier = Column(String(128), nullable=True)  # Raw telegram ID or username
    received_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    message_text = Column(Text, nullable=True)
    raw_metadata = Column(JSON, nullable=True)
    processing_status = Column(String(32), default="PENDING", nullable=False, index=True)  
    # Statuses: PENDING, EXTRACTING, PROCESSED, NON_JOB, FAILED, RETRYING
    error = Column(Text, nullable=True)
    job_id = Column(String(64), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, index=True)

    channel = relationship("Channel", back_populates="messages")
    job = relationship("Job", back_populates="processed_messages")

    __table_args__ = (
        Index("ix_channel_message_unique", "channel_identifier", "telegram_message_id", unique=False),
    )


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    fingerprint = Column(String(128), unique=True, nullable=False, index=True)
    organization = Column(String(255), nullable=True, index=True)
    post_name = Column(String(255), nullable=True)
    notification_number = Column(String(128), nullable=True, index=True)
    structured_data = Column(JSON, nullable=False)  # Normalized JobExtractionSchema
    eligibility_status = Column(String(32), nullable=False, default="UNCERTAIN", index=True)
    # Statuses: ELIGIBLE, UNCERTAIN, NOT_ELIGIBLE, AI_REVIEW_REQUIRED
    eligibility_explanation = Column(JSON, nullable=True)
    ai_provider_used = Column(String(64), nullable=True)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    processed_messages = relationship("ProcessedMessage", back_populates="job")
    sources = relationship("Source", back_populates="job", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="job", cascade="all, delete-orphan")


class Source(Base):
    __tablename__ = "sources"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    job_id = Column(String(64), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(Text, nullable=False)
    canonical_url = Column(Text, nullable=True)
    source_type = Column(String(32), nullable=False, default="unknown")  
    # 'official', 'secondary', 'telegram_only', 'unknown'
    verification_status = Column(String(32), nullable=False, default="unverified")
    # 'verified', 'unverified', 'conflicting'
    retrieval_method = Column(String(64), nullable=True)
    source_confidence = Column(Float, default=0.0)
    retrieved_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    job = relationship("Job", back_populates="sources")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    job_id = Column(String(64), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    telegram_chat_id = Column(String(64), nullable=False, index=True)
    sent_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    alert_type = Column(String(32), nullable=False)  # 'ELIGIBLE', 'UNCERTAIN'
    telegram_message_id = Column(String(64), nullable=True)
    delivery_status = Column(String(32), default="SENT", nullable=False)

    job = relationship("Job", back_populates="alerts")


class Failure(Base):
    __tablename__ = "failures"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    processing_id = Column(String(64), nullable=False, index=True)
    component = Column(String(64), nullable=False, index=True)
    # 'telegram_listener', 'content_acquisition', 'ai_extraction', 'eligibility_engine', 'notification_bot'
    error = Column(Text, nullable=False)
    error_class = Column(String(128), nullable=True)
    failure_type = Column(String(32), default="transient", nullable=False)
    # 'transient', 'permanent', 'rate_limit', 'content_unavailable', 'ai_failure', 'database_failure'
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(32), default="pending", nullable=False, index=True)
    # 'pending', 'resolved', 'dead_letter'
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class UserRequirement(Base):
    __tablename__ = "user_requirements"

    id = Column(String(64), primary_key=True, default="default_user")
    configuration = Column(JSON, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
