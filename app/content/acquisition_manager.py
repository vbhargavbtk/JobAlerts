"""
Content Acquisition Layer Manager
Orchestrates progressive 4-level acquisition with Deep Multi-Hop Crawling:
Level 1 (Direct HTTP) + Deep Outbound Link Crawling
-> Level 2 (Browser-based)
-> Level 3 (Search Fallback with Multi-Query Retrieval)
-> Level 4 (PDF Text & OCR Extraction)
"""
import logging
from typing import Optional, List
from app.content.normalizer import NormalizedContent
from app.content.http_reader import HttpReader
from app.content.browser_reader import BrowserReader
from app.content.search_fallback import SearchFallback
from app.content.pdf_reader import PdfExtractor

logger = logging.getLogger(__name__)


class ContentAcquisitionManager:
    def __init__(self):
        self.http_reader = HttpReader()
        self.browser_reader = BrowserReader()
        self.search_fallback = SearchFallback()
        self.pdf_extractor = PdfExtractor()

    async def acquire_content(
        self,
        urls: List[str],
        query_terms: Optional[List[str]] = None,
        fallback_raw_text: Optional[str] = None
    ) -> Optional[NormalizedContent]:
        """
        Executes deep progressive multi-source acquisition.
        """
        # Step 1: Check if any initial URL is a direct PDF
        for url in urls:
            if url.lower().endswith(".pdf") or ".pdf?" in url.lower():
                logger.info(f"Targeting Level 4 direct PDF extraction for {url}")
                pdf_res = await self.pdf_extractor.extract_from_url(url)
                if pdf_res and len(pdf_res.content_text.strip()) > 100:
                    if fallback_raw_text:
                        pdf_res.content_text += f"\n\n[Telegram Announcement Excerpt]:\n{fallback_raw_text}"
                    return pdf_res

        # Step 2: Level 1 Direct HTTP Extraction + Deep Outbound Crawling
        primary_content: Optional[NormalizedContent] = None
        for url in urls:
            logger.info(f"Trying Level 1 Direct HTTP extraction for {url}")
            res = await self.http_reader.fetch(url)
            if res:
                primary_content = res
                # Check for direct PDF link discovered on the page
                if res.pdf_url:
                    logger.info(f"Discovered PDF on page: {res.pdf_url}. Fetching PDF content...")
                    pdf_res = await self.pdf_extractor.extract_from_url(res.pdf_url)
                    if pdf_res and len(pdf_res.content_text.strip()) > 100:
                        primary_content.content_text += f"\n\n[Official Notification PDF Excerpt ({res.pdf_url})]:\n{pdf_res.content_text}"
                        primary_content.pdf_url = res.pdf_url

                # Deep 2-Hop Crawling: If page is secondary aggregator or short, crawl top candidate deep links
                if res.deep_links and (res.source_type == "secondary" or len(res.content_text.strip()) < 3500):
                    logger.info(f"Triggering Deep Link Crawling on {len(res.deep_links)} candidate links...")
                    for deep_url in res.deep_links[:2]:
                        try:
                            if deep_url.lower().endswith(".pdf"):
                                deep_pdf = await self.pdf_extractor.extract_from_url(deep_url)
                                if deep_pdf and len(deep_pdf.content_text.strip()) > 100:
                                    primary_content.content_text += f"\n\n[Deep Official PDF ({deep_url})]:\n{deep_pdf.content_text[:15000]}"
                                    primary_content.pdf_url = deep_url
                            else:
                                deep_page = await self.http_reader.fetch(deep_url)
                                if deep_page and len(deep_page.content_text.strip()) > 200:
                                    primary_content.content_text += f"\n\n[Detailed Circular Page ({deep_url})]:\n{deep_page.content_text[:12000]}"
                                    if deep_page.pdf_url and not primary_content.pdf_url:
                                        primary_content.pdf_url = deep_page.pdf_url
                        except Exception as e:
                            logger.warning(f"Error crawling deep link {deep_url}: {e}")

                if fallback_raw_text:
                    primary_content.content_text += f"\n\n[Telegram Post Excerpt]:\n{fallback_raw_text}"
                return primary_content

        # Step 3: Level 2 Headless Browser Extraction
        for url in urls:
            logger.info(f"Trying Level 2 Headless Browser extraction for {url}")
            res = await self.browser_reader.fetch(url)
            if res:
                if fallback_raw_text:
                    res.content_text += f"\n\n[Telegram Post Excerpt]:\n{fallback_raw_text}"
                return res

        # Step 4: Level 3 Targeted Search Fallback
        if query_terms:
            logger.info(f"Trying Level 3 Search Fallback with terms: {query_terms}")
            search_res = await self.search_fallback.search_and_retrieve(query_terms)
            if search_res:
                if fallback_raw_text:
                    search_res.content_text += f"\n\n[Telegram Post Excerpt]:\n{fallback_raw_text}"
                return search_res

        # Step 5: Guaranteed Telegram Raw Text Fallback
        if fallback_raw_text and len(fallback_raw_text.strip()) >= 10:
            logger.info("Using raw Telegram text as fallback content.")
            return NormalizedContent(
                source_url=urls[0] if urls else "telegram://internal",
                canonical_url=urls[0] if urls else "telegram://internal",
                source_type="telegram_only",
                title="Telegram Recruitment Message",
                organization=None,
                content_text=fallback_raw_text,
                pdf_url=None,
                retrieval_method="telegram_text",
                source_confidence=0.4,
                verification_status="unverified"
            )

        return None
