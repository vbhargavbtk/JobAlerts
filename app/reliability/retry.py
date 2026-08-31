"""
Reliability: Exponential Backoff & Retry Module
Implements failure classification and exponential backoff retry policies.
"""
import asyncio
import logging
from typing import Callable, Any, TypeVar, Optional
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

T = TypeVar("T")


def classify_error(e: Exception) -> str:
    """Classifies exceptions into actionable failure categories."""
    msg = str(e).lower()
    if "429" in msg or "rate limit" in msg or "quota" in msg:
        return "rate_limit"
    if "401" in msg or "403" in msg or "auth" in msg or "unauthorized" in msg:
        return "authentication"
    if "404" in msg or "dns" in msg or "not found" in msg or "connection refused" in msg:
        return "content_unavailable"
    if "json" in msg or "schema" in msg or "decode" in msg:
        return "ai_failure"
    if "timeout" in msg or "timed out" in msg or "reset by peer" in msg:
        return "transient"
    return "transient"


async def retry_with_backoff(
    operation: Callable[..., Any],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    op_name: str = "operation"
) -> Any:
    """
    Retries an async operation with exponential backoff.
    Permanent failures (e.g. authentication) are not retried.
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            return await operation()
        except Exception as e:
            last_exception = e
            failure_type = classify_error(e)
            logger.warning(
                f"[{op_name}] Attempt {attempt}/{max_retries} failed ({failure_type}): {e}"
            )

            # Permanent failure: do not retry endlessly
            if failure_type == "authentication":
                logger.error(f"[{op_name}] Permanent failure encountered ({failure_type}). Aborting retries.")
                raise e

            if attempt < max_retries:
                await asyncio.sleep(delay)
                delay *= backoff_factor

    raise last_exception
