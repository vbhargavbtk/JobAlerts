"""
Level 3 Content Acquisition: Search Engine Fallback
When original URL is broken or missing, searches DuckDuckGo / Tavily using message facts
(organization, post name, notification number) to pinpoint official recruitment portals.
Never treats a search result as proof without verifying it corresponds to the recruitment.
"""
import logging
from typing import Optional, List, Dict
import httpx

from app.content.normalizer import NormalizedContent
from app.content.source_verifier import classify_source_domain
from config.settings import settings

logger = logging.getLogger(__name__)


class SearchFallback:
    def __init__(self, tavily_api_key: Optional[str] = settings.TAVILY_API_KEY):
        self.tavily_api_key = tavily_api_key

    async def search_and_retrieve(
        self,
        query_terms: List[str]
    ) -> Optional[NormalizedContent]:
        """
        Executes query on search engines to find official recruitment circulars.
        Prioritizes:
        1. Official organization website (.gov.in, .nic.in, official PSU)
        2. Official recruitment portal
        3. Official notification PDF
        4. Reputable secondary source
        """
        clean_terms = [t.strip() for t in query_terms if t and len(t.strip()) > 2]
        if not clean_terms:
            return None

        search_query = " ".join(clean_terms) + " recruitment notification apply online"
        logger.info(f"Level 3 Search fallback query: {search_query}")

        # Try Tavily if API key is provided
        if self.tavily_api_key:
            res = await self._search_tavily(search_query)
            if res:
                return res

        # Fallback to DuckDuckGo search
        return await self._search_duckduckgo(search_query)

    async def _search_tavily(self, query: str) -> Optional[NormalizedContent]:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self.tavily_api_key,
                        "query": query,
                        "search_depth": "advanced",
                        "include_raw_content": False,
                        "max_results": 5
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("results", [])
                    return self._select_best_result(results, query, "search_tavily")
        except Exception as e:
            logger.warning(f"Tavily search failed: {e}")
        return None

    async def _search_duckduckgo(self, query: str) -> Optional[NormalizedContent]:
        try:
            from duckduckgo_search import DDGS
            ddgs = DDGS()
            results = list(ddgs.text(query, max_results=5))
            if results:
                formatted = [
                    {"url": r.get("href"), "title": r.get("title"), "content": r.get("body")}
                    for r in results
                ]
                return self._select_best_result(formatted, query, "search_duckduckgo")
        except Exception as e:
            logger.warning(f"DuckDuckGo search fallback failed: {e}")
        return None

    def _select_best_result(
        self,
        results: List[Dict[str, str]],
        query: str,
        method_name: str
    ) -> Optional[NormalizedContent]:
        if not results:
            return None

        # Sort results: official portals first
        scored = []
        for item in results:
            url = item.get("url") or item.get("href")
            if not url:
                continue
            src_type, verif_status, conf = classify_source_domain(url)
            score = 10.0 if src_type == "official" else 5.0
            if ".pdf" in url.lower():
                score += 2.0
            scored.append((score, url, item, src_type, verif_status, conf))

        if not scored:
            return None

        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0]

        url = best[1]
        item = best[2]
        src_type = best[3]
        verif_status = best[4]
        conf = best[5]

        content_text = item.get("content") or item.get("body") or item.get("snippet", "")
        pdf_url = url if url.lower().endswith(".pdf") else None

        return NormalizedContent(
            source_url=url,
            canonical_url=url,
            source_type=src_type,
            title=item.get("title"),
            organization=None,
            content_text=f"Extracted via search for '{query}':\n\n{content_text}",
            pdf_url=pdf_url,
            retrieval_method=method_name,
            source_confidence=conf,
            verification_status=verif_status
        )
