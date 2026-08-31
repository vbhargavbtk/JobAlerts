"""
Normalized Content Schema & Content Acquisition Models
"""
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class NormalizedContent(BaseModel):
    source_url: str = Field(..., description="Original URL extracted or queried")
    canonical_url: Optional[str] = Field(None, description="Resolved final canonical destination URL")
    source_type: str = Field(
        default="unknown",
        description="Source classification: official, secondary, telegram_only, or unknown"
    )
    title: Optional[str] = Field(None, description="Extracted document / page title")
    organization: Optional[str] = Field(None, description="Discovered issuing organization name")
    content_text: str = Field(..., description="Extracted readable plain text content")
    pdf_url: Optional[str] = Field(None, description="Discovered direct link to official circular PDF")
    retrieved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of retrieval"
    )
    retrieval_method: str = Field(
        ...,
        description="Method used: http_direct, browser_headless, pdf_text, pdf_ocr, search_fallback, telegram_text"
    )
    source_confidence: float = Field(
        default=0.0,
        description="Confidence in content authenticity between 0.0 and 1.0"
    )
    verification_status: str = Field(
        default="unverified",
        description="verified, unverified, or conflicting"
    )
