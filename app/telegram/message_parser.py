"""
Telegram Message Parser
Extracts structured metadata, text, URLs, media attributes, and forwarded details
from raw Telethon event messages.
"""
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

URL_PATTERN = re.compile(
    r'(?:https?://|www\.)[^\s<>"\'()]+(?:\([^\s<>"\'()]+\)|[^\s`!()\[\]{};:\'\".,<>?«»“”‘’])',
    re.IGNORECASE
)

# Common indicators of job/recruitment posts
JOB_INDICATORS = [
    "recruitment", "vacancy", "vacancies", "notification", "apply online",
    "government job", "govt job", "employment", "posts", "post", "eligibility",
    "recruitment notification", "apprentice", "apprenticeship", "selection",
    "application", "officer", "engineer", "clerk", "assistant", "salary",
    "last date", "qualification", "sarkari"
]

# Non-job indicators to classify separately
NON_JOB_INDICATORS = {
    "exam_result": ["result declared", "final result", "merit list", "score card", "results out"],
    "answer_key": ["answer key", "provisional answer key", "objection tracker"],
    "exam_date": ["exam date", "admit card", "hall ticket", "call letter", "exam postponed"],
    "admission": ["admission open", "counseling schedule", "seat allotment", "entrance exam"],
    "syllabus": ["syllabus pdf", "exam pattern & syllabus", "detailed syllabus"]
}


class ParsedTelegramMessage:
    def __init__(
        self,
        telegram_message_id: str,
        channel_id: str,
        channel_name: str,
        timestamp: datetime,
        message_text: str,
        urls: List[str],
        media_metadata: Dict[str, Any],
        is_forwarded: bool,
        forward_from: Optional[str],
        pre_filter_category: str,
        is_potential_job: bool,
        raw_event: Optional[Dict[str, Any]] = None
    ):
        self.telegram_message_id = telegram_message_id
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.timestamp = timestamp
        self.message_text = message_text
        self.urls = urls
        self.media_metadata = media_metadata
        self.is_forwarded = is_forwarded
        self.forward_from = forward_from
        self.pre_filter_category = pre_filter_category
        self.is_potential_job = is_potential_job
        self.raw_event = raw_event or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "telegram_message_id": self.telegram_message_id,
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "timestamp": self.timestamp.isoformat(),
            "message_text": self.message_text,
            "urls": self.urls,
            "media_metadata": self.media_metadata,
            "is_forwarded": self.is_forwarded,
            "forward_from": self.forward_from,
            "pre_filter_category": self.pre_filter_category,
            "is_potential_job": self.is_potential_job,
            "raw_event": self.raw_event
        }


def extract_urls(text: str) -> List[str]:
    """Extract all URLs cleanly from text."""
    if not text:
        return []
    matches = URL_PATTERN.findall(text)
    clean_urls = []
    for match in matches:
        if not match.startswith("http://") and not match.startswith("https://"):
            match = "https://" + match
        clean_urls.append(match.rstrip("/."))
    return list(dict.fromkeys(clean_urls))  # deduplicate preserving order


def classify_pre_filter(text: str) -> tuple[str, bool]:
    """
    Inexpensive rule-based pre-filter.
    Returns (category, is_potential_job).
    Does NOT make the final eligibility decision.
    """
    if not text:
        return "empty", False

    text_lower = text.lower()

    # Check non-job indicators first
    for category, keywords in NON_JOB_INDICATORS.items():
        if any(kw in text_lower for kw in keywords):
            return category, False

    # Check job indicators
    is_job = any(kw in text_lower for kw in JOB_INDICATORS)
    category = "potential_job" if is_job else "general_or_unknown"
    return category, is_job


def parse_telethon_message(event) -> ParsedTelegramMessage:
    """Parses a Telethon NewMessage event into a clean structured object."""
    message = event.message
    chat = event.chat

    channel_id = str(event.chat_id) if event.chat_id else "unknown"
    channel_name = getattr(chat, "title", None) or getattr(chat, "username", "Unknown Channel")
    msg_id = str(message.id)
    msg_date = message.date if message.date else datetime.now(timezone.utc)
    msg_text = message.message or message.raw_text or ""

    # URLs from text and message entities
    urls = extract_urls(msg_text)
    if message.entities:
        for entity in message.entities:
            entity_url = getattr(entity, "url", None)
            if entity_url and entity_url not in urls:
                urls.append(entity_url)

    # Media metadata
    media_metadata = {
        "has_media": message.media is not None,
        "media_type": type(message.media).__name__ if message.media else None,
        "is_document": getattr(message, "file", None) is not None,
        "mime_type": getattr(getattr(message, "file", None), "mime_type", None),
        "file_name": getattr(getattr(message, "file", None), "name", None),
        "file_size": getattr(getattr(message, "file", None), "size", None)
    }

    # Forwarded metadata
    is_forwarded = message.fwd_from is not None
    forward_from = None
    if is_forwarded and message.fwd_from:
        forward_from = getattr(message.fwd_from, "from_name", None) or str(getattr(message.fwd_from, "from_id", ""))

    pre_filter_cat, is_job = classify_pre_filter(msg_text)

    return ParsedTelegramMessage(
        telegram_message_id=msg_id,
        channel_id=channel_id,
        channel_name=str(channel_name),
        timestamp=msg_date,
        message_text=msg_text,
        urls=urls,
        media_metadata=media_metadata,
        is_forwarded=is_forwarded,
        forward_from=forward_from,
        pre_filter_category=pre_filter_cat,
        is_potential_job=is_job,
        raw_event={
            "chat_id": channel_id,
            "message_id": msg_id,
            "grouped_id": str(message.grouped_id) if message.grouped_id else None
        }
    )
