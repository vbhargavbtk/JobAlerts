import pytest
import pytest_asyncio
from app.ai.schemas import JobExtractionSchema, FieldEvidence
from app.ai.nim_provider import NvidiaNIMProvider
from app.ai.gemini_provider import GeminiProvider
from app.ai.openrouter_provider import OpenRouterProvider
from app.ai.router import AIRouter
from app.content.normalizer import NormalizedContent


class MockFailingProvider(NvidiaNIMProvider):
    def __init__(self):
        super().__init__(api_key="mock_key")

    def is_configured(self) -> bool:
        return True

    async def extract_job_data(self, content):
        return None, "HTTP 429 Rate Limit Exceeded"


class MockSuccessfulGemini(GeminiProvider):
    def __init__(self):
        super().__init__(api_key="mock_gemini_key")

    def is_configured(self) -> bool:
        return True

    async def extract_job_data(self, content):
        return JobExtractionSchema(
            is_job=True,
            job_type="central_government",
            organization="DRDO - RAC",
            post_name="Scientist B",
            vacancies=120,
            qualification=["B.Tech"],
            accepted_branches=["Computer Science"],
            age_max=28,
            experience_required=False,
            confidence=0.95
        ), None


@pytest.mark.asyncio
async def test_ai_router_strict_fallback():
    # Primary fails -> Secondary succeeds
    failing_nim = MockFailingProvider()
    successful_gemini = MockSuccessfulGemini()

    router = AIRouter(providers=[failing_nim, successful_gemini])

    content = NormalizedContent(
        source_url="https://rac.gov.in/notif.pdf",
        content_text="DRDO RAC Scientist B recruitment for 120 posts.",
        retrieval_method="pdf_text"
    )

    data, provider_used, err = await router.extract(content)
    assert data is not None
    assert provider_used == "gemini"
    assert data.organization == "DRDO - RAC"
    assert err is None


@pytest.mark.asyncio
async def test_ai_router_exhaustion_does_not_invent():
    # All providers fail
    p1 = MockFailingProvider()
    p2 = MockFailingProvider()

    router = AIRouter(providers=[p1, p2])
    content = NormalizedContent(
        source_url="https://portal.gov.in",
        content_text="Some circular text.",
        retrieval_method="http_direct"
    )

    data, provider, err = await router.extract(content)
    assert data is None
    assert provider is None
    assert "All AI providers failed" in err
