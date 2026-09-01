"""
Public Telegram Channel Web Scraper
Scrapes public channel messages directly from https://t.me/s/{channel_username}.
Provides 100% resilient fallback message ingestion without requiring MTProto user authentication.
"""
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from urllib.parse import urljoin
import httpx
from bs4 import BeautifulSoup

from app.telegram.message_parser import ParsedTelegramMessage, extract_urls, classify_pre_filter

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


class PublicChannelScraper:
    def __init__(self, timeout: int = 20):
        self.timeout = timeout
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        }

    async def fetch_channel_messages(
        self,
        channel_identifier: str,
        channel_name: Optional[str] = None,
        limit: int = 20
    ) -> List[ParsedTelegramMessage]:
        """
        Fetches the latest messages from a public Telegram channel web preview.
        channel_identifier can be '@username', 'username', or full t.me URL.
        """
        clean_username = channel_identifier.strip()
        if "t.me/" in clean_username:
            clean_username = clean_username.split("t.me/")[-1].replace("s/", "").split("/")[0]
        clean_username = clean_username.lstrip("@").strip()

        if not clean_username:
            return []

        url = f"https://t.me/s/{clean_username}"
        logger.info(f"Scraping public Telegram channel web preview: {url}")

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.headers,
                follow_redirects=True
            ) as client:
                response = await client.get(url)

                if response.status_code != 200:
                    logger.warning(f"Public channel {url} returned HTTP {response.status_code}")
                    return []

                soup = BeautifulSoup(response.text, "lxml")

                # Extract channel title if not provided
                extracted_channel_title = channel_name
                if not extracted_channel_title:
                    title_div = soup.find("div", class_="tgme_channel_info_header_title")
                    if title_div:
                        extracted_channel_title = title_div.get_text(strip=True)
                    else:
                        extracted_channel_title = f"@{clean_username}"

                msg_wraps = soup.find_all("div", class_="tgme_widget_message_wrap")
                if not msg_wraps:
                    logger.info(f"No messages found in public preview for @{clean_username}")
                    return []

                parsed_messages: List[ParsedTelegramMessage] = []

                # Iterate through message wraps (newest at the bottom of the list)
                for wrap in msg_wraps[-limit:]:
                    msg_div = wrap.find("div", class_="tgme_widget_message")
                    if not msg_div:
                        continue

                    # Extract telegram message ID
                    data_post = msg_div.get("data-post", "")
                    msg_id = data_post.split("/")[-1] if "/" in data_post else str(len(parsed_messages) + 1)
                    if not msg_id or not msg_id.isdigit():
                        continue

                    # Extract timestamp
                    time_tag = wrap.find("time")
                    dt_str = time_tag.get("datetime", "") if time_tag else ""
                    msg_date = datetime.now(timezone.utc)
                    if dt_str:
                        try:
                            msg_date = datetime.fromisoformat(dt_str)
                        except Exception:
                            pass

                    # Extract text
                    text_div = wrap.find("div", class_="tgme_widget_message_text")
                    msg_text = text_div.get_text(separator="\n").strip() if text_div else ""

                    # Skip empty placeholder system messages (e.g. 'Channel created')
                    if not msg_text and not wrap.find("a", class_="tgme_widget_message_photo_wrap") and not wrap.find("div", class_="tgme_widget_message_document"):
                        continue

                    # Extract URLs
                    urls = extract_urls(msg_text)
                    if text_div:
                        for a in text_div.find_all("a", href=True):
                            href = a["href"].strip()
                            if href.startswith("http") and href not in urls:
                                urls.append(href)

                    # Check media
                    photo_wrap = wrap.find("a", class_="tgme_widget_message_photo_wrap")
                    doc_wrap = wrap.find("div", class_="tgme_widget_message_document")
                    has_media = bool(photo_wrap or doc_wrap)

                    media_metadata = {
                        "has_media": has_media,
                        "media_type": "photo" if photo_wrap else ("document" if doc_wrap else None),
                        "is_document": bool(doc_wrap),
                        "mime_type": None,
                        "file_name": None,
                        "file_size": None
                    }

                    # Check forward
                    fwd_div = wrap.find("div", class_="tgme_widget_message_forwarded_from")
                    is_forwarded = bool(fwd_div)
                    forward_from = fwd_div.get_text(strip=True) if fwd_div else None

                    pre_filter_cat, is_job = classify_pre_filter(
                        msg_text,
                        urls=urls,
                        has_media=has_media
                    )

                    parsed_messages.append(ParsedTelegramMessage(
                        telegram_message_id=msg_id,
                        channel_id=f"@{clean_username}",
                        channel_name=str(extracted_channel_title),
                        timestamp=msg_date,
                        message_text=msg_text,
                        urls=urls,
                        media_metadata=media_metadata,
                        is_forwarded=is_forwarded,
                        forward_from=forward_from,
                        pre_filter_category=pre_filter_cat,
                        is_potential_job=is_job,
                        raw_event={
                            "source": "telegram_web_scraper",
                            "channel": clean_username,
                            "post_id": data_post
                        }
                    ))

                logger.info(f"Successfully scraped {len(parsed_messages)} messages from @{clean_username}")
                return parsed_messages

        except Exception as e:
            logger.error(f"Error scraping public Telegram channel @{clean_username}: {e}", exc_info=True)
            return []
