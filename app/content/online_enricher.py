"""
Online Search Enrichment Service
Searches the web for missing recruitment details (official PDF links, online apply portal,
application start dates, application fees, selection process) when secondary sources or
Telegram messages omit them.
"""
import logging
from typing import Optional, List, Tuple
import httpx

from app.ai.schemas import JobExtractionSchema
from app.content.normalizer import NormalizedContent
from app.content.search_fallback import SearchFallback
from app.content.source_verifier import classify_source_domain
from app.content.http_reader import HttpReader
from app.content.pdf_reader import PdfExtractor
from app.ai.base import AIProvider

logger = logging.getLogger(__name__)


class OnlineJobEnricher:
    def __init__(self, ai_provider: Optional[AIProvider] = None):
        self.search_fallback = SearchFallback()
        self.http_reader = HttpReader()
        self.pdf_extractor = PdfExtractor()
        self.ai_provider = ai_provider

    async def enrich_job_if_needed(
        self,
        job: JobExtractionSchema,
        content: Optional[NormalizedContent] = None,
        ai_provider: Optional[AIProvider] = None
    ) -> Tuple[JobExtractionSchema, Optional[NormalizedContent]]:
        """
        Detects missing fields in the extracted job and conducts a targeted online search
        to fill in official PDF links, apply URLs, start dates, fees, and exam processes.
        """
        provider = ai_provider or self.ai_provider
        if not provider:
            from app.ai.gemini_provider import GeminiProvider
            provider = GeminiProvider()

        # Check if enrichment is needed
        needs_official_link = not job.official_notification_url and not (content and content.pdf_url)
        needs_apply_url = not job.official_apply_url
        needs_dates = not job.application_start
        needs_fees = not job.application_fee or len(job.application_fee) == 0
        needs_selection = not job.selection_process or len(job.selection_process) == 0

        if not (needs_official_link or needs_apply_url or needs_dates or needs_fees or needs_selection):
            logger.info("Job record already contains all complete details; skipping online search enrichment.")
            return job, content

        org = job.organization or ""
        post = job.post_name or ""
        advt = job.notification_number or ""
        
        if not org and not post:
            return job, content

        query = f"{org} {post} {advt} recruitment notification application fee category wise apply online pdf official".strip()
        logger.info(f"Triggering Online Search Enrichment with query: '{query}'")

        search_results = await self.search_fallback.search_raw_results(query, max_results=8)
        if not search_results:
            logger.info("Online search enrichment found no web results.")
            return job, content

        discovered_official_url = None
        discovered_official_pdf = None
        discovered_apply_url = None
        web_snippets = []

        # Inspect results for official gov domains and PDFs
        for item in search_results:
            url = item.get("url", "")
            title = item.get("title", "")
            snippet = item.get("content", "")
            
            web_snippets.append(f"Source: {title} ({url})\n{snippet}\n")

            src_type, verif_status, _ = classify_source_domain(url)
            if src_type == "official":
                discovered_official_url = url
                if not discovered_apply_url:
                    discovered_apply_url = url
            if url.lower().endswith(".pdf") or ".pdf?" in url.lower():
                discovered_official_pdf = url

        # If an official portal or direct PDF was found, fetch its deep content
        deep_content_text = ""
        if discovered_official_pdf:
            pdf_data = await self.pdf_extractor.extract_from_url(discovered_official_pdf)
            if pdf_data and pdf_data.content_text:
                deep_content_text += f"\n\n[Official Online PDF ({discovered_official_pdf})]:\n{pdf_data.content_text[:12000]}"
        elif discovered_official_url:
            page_data = await self.http_reader.fetch(discovered_official_url)
            if page_data and page_data.content_text:
                deep_content_text += f"\n\n[Official Portal Page ({discovered_official_url})]:\n{page_data.content_text[:8000]}"
                if page_data.pdf_url:
                    discovered_official_pdf = page_data.pdf_url

        # Combine all discovered online information
        combined_search_text = "Discovered Web Search Intelligence:\n\n" + "\n".join(web_snippets) + deep_content_text

        # Create temporary NormalizedContent to pass into fast AI extractor
        temp_content = NormalizedContent(
            source_url=discovered_official_url or (content.source_url if content else "https://online-search"),
            canonical_url=discovered_official_url or (content.canonical_url if content else "https://online-search"),
            source_type="official" if discovered_official_url else "secondary",
            title=f"Online Enrichment for {org} {post}",
            content_text=combined_search_text,
            pdf_url=discovered_official_pdf,
            retrieval_method="online_search_enrichment",
            verification_status="verified" if discovered_official_url else "unverified"
        )

        try:
            enriched_schema, err = await provider.extract_job_data(temp_content)
            if enriched_schema:
                logger.info("Successfully extracted missing fields from online search intelligence.")

                # Merge missing fields into existing job
                if not job.application_start and enriched_schema.application_start:
                    job.application_start = enriched_schema.application_start
                if (not job.application_deadline or job.application_deadline == "Check official link") and enriched_schema.application_deadline:
                    job.application_deadline = enriched_schema.application_deadline
                if (not job.application_fee or len(job.application_fee) == 0) and enriched_schema.application_fee:
                    job.application_fee = enriched_schema.application_fee
                if (not job.selection_process or len(job.selection_process) == 0) and enriched_schema.selection_process:
                    job.selection_process = enriched_schema.selection_process
                if not job.salary and enriched_schema.salary:
                    job.salary = enriched_schema.salary
                if not job.vacancies and enriched_schema.vacancies:
                    job.vacancies = enriched_schema.vacancies
                
                # Official URLs
                if enriched_schema.official_notification_url:
                    job.official_notification_url = enriched_schema.official_notification_url
                elif discovered_official_pdf:
                    job.official_notification_url = discovered_official_pdf

                if enriched_schema.official_apply_url:
                    job.official_apply_url = enriched_schema.official_apply_url
                elif discovered_apply_url:
                    job.official_apply_url = discovered_apply_url

                # Update content object if official sources were verified
                if content and discovered_official_url:
                    content.source_type = "official"
                    content.verification_status = "verified"
                    if not content.pdf_url and discovered_official_pdf:
                        content.pdf_url = discovered_official_pdf

        except Exception as e:
            logger.warning(f"Error during AI extraction on search enrichment: {e}")

        # Fallback URL injection even if AI skipped them
        if not job.official_notification_url and discovered_official_pdf:
            job.official_notification_url = discovered_official_pdf
        if not job.official_apply_url and discovered_apply_url:
            job.official_apply_url = discovered_apply_url

        return job, content
