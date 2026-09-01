"""
Multi-Provider AI Router Module
Orchestrates strict failover across AI providers:
NVIDIA NIM (Primary) -> Google Gemini 2.5 Flash (Secondary) -> OpenRouter (Tertiary)
If all providers fail, places job into AI_REVIEW_REQUIRED without fabricating data.
"""
import logging
from typing import Optional, Tuple, List
from app.ai.base import AIProvider
from app.ai.nim_provider import NvidiaNIMProvider
from app.ai.gemini_provider import GeminiProvider
from app.ai.openrouter_provider import OpenRouterProvider
from app.ai.schemas import JobExtractionSchema
from app.content.normalizer import NormalizedContent

logger = logging.getLogger(__name__)


class AIRouter:
    def __init__(self, providers: Optional[List[AIProvider]] = None):
        if providers is not None:
            self.providers = providers
        else:
            # Prioritize Google Gemini Flash (fastest, most reliable) -> NVIDIA NIM -> OpenRouter
            self.providers = [
                GeminiProvider(),
                NvidiaNIMProvider(),
                OpenRouterProvider()
            ]

    async def extract(
        self,
        content: NormalizedContent
    ) -> Tuple[Optional[JobExtractionSchema], Optional[str], Optional[str]]:
        """
        Executes AI extraction with strict fallback routing.
        Returns:
            (JobExtractionSchema, provider_used, None) on success.
            (None, None, error_summary) if all providers fail (AI_REVIEW_REQUIRED).
        """
        errors = []

        for provider in self.providers:
            if not provider.is_configured():
                logger.info(f"AI Provider {provider.name} is not configured or lacks API key; trying next provider.")
                errors.append(f"{provider.name}: Not configured")
                continue

            logger.info(f"Attempting extraction using provider: {provider.name} ({provider.model})")
            schema_res, err = await provider.extract_job_data(content)

            if schema_res is not None:
                logger.info(f"Successfully extracted structured data with {provider.name}")
                return schema_res, provider.provider_id, None

            # Provider failed (rate limit, timeout, malformed JSON, etc.)
            logger.warning(f"Provider {provider.name} failed: {err}. Routing to next provider...")
            errors.append(f"{provider.name}: {err}")

        # All providers failed: DO NOT INVENT A RESULT
        error_summary = "All AI providers failed: " + " | ".join(errors)
        logger.error(error_summary)
        return None, None, error_summary
