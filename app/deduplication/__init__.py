"""
Deduplication package initialization
"""
from app.deduplication.fingerprint import compute_job_fingerprint, normalize_text

__all__ = ["compute_job_fingerprint", "normalize_text"]
