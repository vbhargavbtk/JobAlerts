"""
NVIDIA NIM AI Provider Adapter (Primary Provider)
Uses OpenAI-compatible endpoint at https://integrate.api.nvidia.com/v1
"""
import json
import logging
import re
from typing import Optional, Tuple
import httpx

from app.ai.base import AIProvider
from app.ai.schemas import JobExtractionSchema
from app.ai.prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT_TEMPLATE
from app.content.normalizer import NormalizedContent
from config.settings import settings

logger = logging.getLogger(__name__)


class NvidiaNIMProvider(AIProvider):
    def __init__(
        self,
        api_key: Optional[str] = settings.NIM_API_KEY,
        base_url: str = settings.NIM_BASE_URL,
        model: str = settings.NIM_MODEL,
        timeout_seconds: int = 45
    ):
        super().__init__("nvidia_nim", "NVIDIA NIM", model, timeout_seconds)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("nvapi-your_"))

    async def extract_job_data(
        self,
        content: NormalizedContent
    ) -> Tuple[Optional[JobExtractionSchema], Optional[str]]:
        if not self.is_configured():
            return None, "NVIDIA NIM API key is not configured"

        user_prompt = EXTRACTION_USER_PROMPT_TEMPLATE.format(
            source_url=content.source_url,
            title=content.title or "Government Recruitment Notification",
            retrieval_method=content.retrieval_method,
            content_text=content.content_text[:20000]
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,  # Low temperature for strict factual extraction
            "max_tokens": 3000
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )

                if response.status_code != 200:
                    err_msg = f"NVIDIA NIM error HTTP {response.status_code}: {response.text[:200]}"
                    logger.warning(err_msg)
                    return None, err_msg

                data = response.json()
                raw_text = data["choices"][0]["message"]["content"].strip()

                # Clean markdown backticks if present
                clean_json_str = _clean_json_markdown(raw_text)
                parsed_data = json.loads(clean_json_str)

                if isinstance(parsed_data, list):
                    parsed_data = parsed_data[0] if parsed_data else {}

                # Strict Pydantic validation
                schema_validated = JobExtractionSchema.model_validate(parsed_data)
                return schema_validated, None

        except json.JSONDecodeError as jde:
            return None, f"Malformed JSON from NVIDIA NIM: {jde}"
        except Exception as e:
            return None, f"NVIDIA NIM call exception: {e}"


def _clean_json_markdown(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    first_brace = text.find("{")
    first_bracket = text.find("[")
    
    start_idx = -1
    if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
        start_idx = first_brace
        end_idx = text.rfind("}")
    elif first_bracket != -1:
        start_idx = first_bracket
        end_idx = text.rfind("]")
    else:
        end_idx = -1

    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return text[start_idx:end_idx + 1].strip()

    return text
