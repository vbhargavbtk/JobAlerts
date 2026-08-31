"""
Level 2 Content Acquisition: Browser-based Extraction
Designed for JavaScript-rendered SPAs, portal redirect pages, and dynamic DOM trees.
Employs Playwright / Chromium headless extraction or fallback headers.
"""
import logging
import asyncio
from typing import Optional
from app.content.normalizer import NormalizedContent
from app.content.source_verifier import classify_source_domain

logger = logging.getLogger(__name__)


class BrowserReader:
    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds

    async def fetch(self, url: str) -> Optional[NormalizedContent]:
        """
        Extracts JS-rendered web pages.
        Attempts playwright headless browser if available, or graceful simulation.
        """
        if not url:
            return None

        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
                try:
                    await page.goto(url, wait_until="networkidle", timeout=self.timeout_seconds * 1000)
                except Exception:
                    # Fall back to domcontentloaded if networkidle times out
                    await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_seconds * 1000)

                # Wait slightly for dynamic elements
                await asyncio.sleep(2)

                title = await page.title()
                canonical_url = page.url

                # Extract text content
                content_text = await page.inner_text("body")

                # Find any PDF links
                pdf_elements = await page.query_selector_all('a[href$=".pdf"]')
                discovered_pdf = None
                if pdf_elements:
                    discovered_pdf = await pdf_elements[0].get_attribute("href")

                await browser.close()

                if content_text and len(content_text.strip()) > 100:
                    source_type, verif_status, confidence = classify_source_domain(canonical_url)
                    return NormalizedContent(
                        source_url=url,
                        canonical_url=canonical_url,
                        source_type=source_type,
                        title=title,
                        organization=None,
                        content_text=content_text[:30000],
                        pdf_url=discovered_pdf,
                        retrieval_method="browser_headless",
                        source_confidence=confidence,
                        verification_status=verif_status
                    )
        except ImportError:
            logger.info("Playwright not installed or configured on host; Level 2 passing to Level 3 search fallback.")
            return None
        except Exception as e:
            logger.warning(f"Browser-based extraction failed for {url}: {e}")
            return None

        return None
