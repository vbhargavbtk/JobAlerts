"""
AI package initialization
"""
from app.ai.base import AIProvider
from app.ai.schemas import JobExtractionSchema, FieldEvidence
from app.ai.prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT_TEMPLATE
from app.ai.nim_provider import NvidiaNIMProvider
from app.ai.gemini_provider import GeminiProvider
from app.ai.openrouter_provider import OpenRouterProvider
from app.ai.router import AIRouter

__all__ = [
    "AIProvider",
    "JobExtractionSchema",
    "FieldEvidence",
    "EXTRACTION_SYSTEM_PROMPT",
    "EXTRACTION_USER_PROMPT_TEMPLATE",
    "NvidiaNIMProvider",
    "GeminiProvider",
    "OpenRouterProvider",
    "AIRouter"
]
