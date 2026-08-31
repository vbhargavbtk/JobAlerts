"""
Content Acquisition Layer Manager
Orchestrates the 4 fallback levels progressively:
Level 1 (Direct HTTP) -> Level 2 (Browser-based) -> Level 3 (Search Fallback) -> Level 4 (PDF Extraction)
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
        Executes progressive 4-level acquisition.
        """
        # Step 1: Check if any URL is a direct PDF
        for url in urls:
            if url.lower().endswith(".pdf") or "pdf" in url.lower():
                logger.info(f"Targeting Level 4 PDF extraction for {url}")
                pdf_res = await self.pdf_extractor.extract_from_url(url)
                if pdf_res:
                    return pdf_res

        # Step 2: Try Level 1 Direct HTTP on provided URLs
        for url in urls:
            logger.info(f"Trying Level 1 Direct HTTP extraction for {url}")
            res = await self.http_reader.fetch(url)
            if res:
                # If page contains a newly discovered PDF notification link, extract that PDF!
                if res.pdf_url:
                    logger.info(f"Found PDF link on page: {res.pdf_url}. Triggering Level 4 PDF extraction...")
                    pdf_res = await self.pdf_extractor.extract_from_url(res.pdf_url)
                    if pdf_res:
                        if fallback_raw_text:
                            pdf_res.content_text += f"\n\n[Telegram Post Excerpt]:\n{fallback_raw_text}"
                        return pdf_res
                if fallback_raw_text:
                    res.content_text += f"\n\n[Telegram Post Excerpt]:\n{fallback_raw_text}"
                return res

        # Step 3: Try Level 2 Headless Browser on URLs
        for url in urls:
            logger.info(f"Trying Level 2 Headless Browser extraction for {url}")
            res = await self.browser_reader.fetch(url)
            if res:
                if res.pdf_url:
                    pdf_res = await self.pdf_extractor.extract_from_url(res.pdf_url)
                    if pdf_res:
                        if fallback_raw_text:
                            pdf_res.content_text += f"\n\n[Telegram Post Excerpt]:\n{fallback_raw_text}"
                        return pdf_res
                if fallback_raw_text:
                    res.content_text += f"\n\n[Telegram Post Excerpt]:\n{fallback_raw_text}"
                return res

        # Step 4: Try Level 3 Search Fallback using query terms (organization, post title)
        if query_terms:
            logger.info(f"Trying Level 3 Search Fallback with terms: {query_terms}")
            search_res = await self.search_fallback.search_and_retrieve(query_terms)
            if search_res:
                if search_res.pdf_url:
                    pdf_res = await self.pdf_extractor.extract_from_url(search_res.pdf_url)
                    if pdf_res:
                        return pdf_res
                return search_res

        # Step 5: If all external content retrieval fails, use Telegram raw text as guaranteed fallback
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
