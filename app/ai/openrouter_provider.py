"""
OpenRouter AI Provider Adapter (Tertiary Fallback)
Uses OpenAI-compatible endpoint at https://openrouter.ai/api/v1
with free or verified models (e.g. meta-llama/llama-3.3-70b-instruct:free).
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


class OpenRouterProvider(AIProvider):
    def __init__(
        self,
        api_key: Optional[str] = settings.OPENROUTER_API_KEY,
        base_url: str = settings.OPENROUTER_BASE_URL,
        model: str = settings.OPENROUTER_MODEL,
        timeout_seconds: int = 45
    ):
        super().__init__("openrouter", "OpenRouter", model, timeout_seconds)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("sk-or-v1-your_"))

    async def extract_job_data(
        self,
        content: NormalizedContent
    ) -> Tuple[Optional[JobExtractionSchema], Optional[str]]:
        if not self.is_configured():
            return None, "OpenRouter API key is not configured"

        user_prompt = EXTRACTION_USER_PROMPT_TEMPLATE.format(
            source_url=content.source_url,
            title=content.title or "Government Recruitment Notification",
            retrieval_method=content.retrieval_method,
            content_text=content.content_text[:20000]
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/personal-job-intelligence",
            "X-Title": "Personal Job Alert Intelligence",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )

                if response.status_code != 200:
                    err_msg = f"OpenRouter error HTTP {response.status_code}: {response.text[:200]}"
                    logger.warning(err_msg)
                    return None, err_msg

                data = response.json()
                raw_text = data["choices"][0]["message"]["content"].strip()
                clean_json_str = _clean_json_markdown(raw_text)
                parsed_dict = json.loads(clean_json_str)

                schema_validated = JobExtractionSchema.model_validate(parsed_dict)
                return schema_validated, None

        except json.JSONDecodeError as jde:
            return None, f"Malformed JSON from OpenRouter: {jde}"
        except Exception as e:
            return None, f"OpenRouter call exception: {e}"


def _clean_json_markdown(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()
