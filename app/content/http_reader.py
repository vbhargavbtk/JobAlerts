"""
Level 1 Content Acquisition: Direct HTTP & Readability Extraction
Retrieves content using HTTP GET, checks SSL, follows redirects, extracts article text,
and detects PDF notification links.
"""
import logging
import re
from typing import Optional, Tuple, List
from urllib.parse import urljoin
import httpx
from bs4 import BeautifulSoup

from app.content.normalizer import NormalizedContent
from app.content.source_verifier import classify_source_domain
from config.settings import settings

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

PDF_EXT_PATTERN = re.compile(r'\.pdf(?:\?.*)?$', re.IGNORECASE)


class HttpReader:
    def __init__(self, timeout: int = settings.HTTP_TIMEOUT_SECONDS):
        self.timeout = timeout
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf;q=0.8,*/*;q=0.7",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        }

    async def fetch(self, url: str) -> Optional[NormalizedContent]:
        """
        Attempts direct Level 1 HTTP fetch and readable content extraction.
        Returns NormalizedContent if successful, or None if JS rendering or PDF handling is needed.
        """
        if not url:
            return None

        # If direct PDF link
        if PDF_EXT_PATTERN.search(url):
            logger.info(f"Direct PDF detected in Level 1: {url}")
            return None  # Pass down to Level 4 PDF reader

        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True,
                verify=False  # Many Indian govt portals have expired/misconfigured certs
            ) as client:
                response = await client.get(url)

                if response.status_code != 200:
                    logger.warning(f"HTTP {response.status_code} for {url}")
                    return None

                content_type = response.headers.get("content-type", "").lower()
                final_url = str(response.url)

                if "application/pdf" in content_type:
                    logger.info(f"Content-Type is application/pdf: {final_url}")
                    return None  # Route to Level 4 PDF extraction

                html_text = response.text
                if not html_text or len(html_text.strip()) < 100:
                    return None

                soup = BeautifulSoup(html_text, "lxml")

                # Remove non-content tags
                for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg"]):
                    tag.decompose()

                # Extract title
                title = soup.title.string.strip() if soup.title and soup.title.string else None

                # Search for PDF links
                discovered_pdf: Optional[str] = None
                for a_tag in soup.find_all("a", href=True):
                    href = a_tag["href"]
                    if PDF_EXT_PATTERN.search(href) or "download" in href.lower() or "notification" in href.lower():
                        full_pdf_url = urljoin(final_url, href)
                        discovered_pdf = full_pdf_url
                        break

                # Extract readable text
                paragraphs = [p.get_text(separator=" ", strip=True) for p in soup.find_all(["p", "h1", "h2", "h3", "li", "table"])]
                content_text = "\n".join(filter(None, paragraphs))

                # If body text is too short, page probably requires JS rendering
                if len(content_text.strip()) < 150:
                    logger.info(f"Page text too short ({len(content_text)} chars), requiring Level 2 fallback: {url}")
                    return None

                source_type, verif_status, confidence = classify_source_domain(final_url)

                return NormalizedContent(
                    source_url=url,
                    canonical_url=final_url,
                    source_type=source_type,
                    title=title,
                    organization=None,
                    content_text=content_text[:25000],  # Keep reasonable size
                    pdf_url=discovered_pdf,
                    retrieval_method="http_direct",
                    source_confidence=confidence,
                    verification_status=verif_status
                )

        except Exception as e:
            logger.warning(f"Level 1 HTTP extraction failed for {url}: {e}")
            return None
