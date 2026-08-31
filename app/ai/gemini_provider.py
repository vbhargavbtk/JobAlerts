"""
Google Gemini AI Provider Adapter (Secondary Fallback)
Uses Google AI Studio API with the active production model `gemini-2.5-flash`.
"""
import json
import logging
from typing import Optional, Tuple
import httpx

from app.ai.base import AIProvider
from app.ai.schemas import JobExtractionSchema
from app.ai.prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT_TEMPLATE
from app.content.normalizer import NormalizedContent
from config.settings import settings

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    def __init__(
        self,
        api_key: Optional[str] = settings.GEMINI_API_KEY,
        model: str = settings.GEMINI_MODEL,
        timeout_seconds: int = 35
    ):
        super().__init__("gemini", "Google Gemini Flash", model, timeout_seconds)
        self.api_key = api_key

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("your_gemini_"))

    async def extract_job_data(
        self,
        content: NormalizedContent
    ) -> Tuple[Optional[JobExtractionSchema], Optional[str]]:
        if not self.is_configured():
            return None, "Google Gemini API key is not configured"

        user_prompt = EXTRACTION_USER_PROMPT_TEMPLATE.format(
            source_url=content.source_url,
            title=content.title or "Government Recruitment Notification",
            retrieval_method=content.retrieval_method,
            content_text=content.content_text[:25000]
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "system_instruction": {
                "parts": [{"text": EXTRACTION_SYSTEM_PROMPT}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(url, json=payload)

                if response.status_code != 200:
                    err_msg = f"Gemini API error HTTP {response.status_code}: {response.text[:200]}"
                    logger.warning(err_msg)
                    return None, err_msg

                data = response.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    return None, "Gemini returned no response candidates"

                raw_text = candidates[0]["content"]["parts"][0]["text"].strip()
                clean_json = _clean_json(raw_text)
                parsed_dict = json.loads(clean_json)

                schema_validated = JobExtractionSchema.model_validate(parsed_dict)
                return schema_validated, None

        except json.JSONDecodeError as jde:
            return None, f"Malformed JSON from Gemini: {jde}"
        except Exception as e:
            return None, f"Gemini call exception: {e}"


def _clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()
