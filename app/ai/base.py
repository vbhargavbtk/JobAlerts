"""
Base AI Provider Interface
Defines the uniform contract for all AI extraction adapters.
"""
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from app.ai.schemas import JobExtractionSchema
from app.content.normalizer import NormalizedContent


class AIProvider(ABC):
    def __init__(self, provider_id: str, name: str, model: str, timeout_seconds: int = 40):
        self.provider_id = provider_id
        self.name = name
        self.model = model
        self.timeout_seconds = timeout_seconds

    @abstractmethod
    async def extract_job_data(
        self,
        content: NormalizedContent
    ) -> Tuple[Optional[JobExtractionSchema], Optional[str]]:
        """
        Extracts structured job details from normalized content.
        Returns:
            (JobExtractionSchema, None) on success.
            (None, error_description) on failure.
        """
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if the required API keys and endpoints are configured."""
        pass
