"""
Job Deduplication & Cryptographic Fingerprinting Module
Computes SHA-256 fingerprint from normalized fields:
organization | post_name | notification_number | application_deadline | official_url
Ensures identical recruitments posted across dozens of public and private channels
generate only ONE alert.
"""
import hashlib
import re
from typing import Optional
from app.ai.schemas import JobExtractionSchema


def normalize_text(text: Optional[str]) -> str:
    if not text:
        return ""
    # Strip special punctuation and standardize case/spacing
    clean = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
    return clean.strip()


def compute_job_fingerprint(
    job: JobExtractionSchema,
    canonical_url: Optional[str] = None
) -> str:
    """
    Computes a deterministic cryptographic SHA-256 fingerprint.
    """
    norm_org = normalize_text(job.organization)
    norm_post = normalize_text(job.post_name)
    norm_notif_no = normalize_text(job.notification_number)
    norm_deadline = normalize_text(job.application_deadline)

    # Primary key component
    components = [norm_org, norm_post]

    # If notification number exists, it is an authoritative identifier
    if norm_notif_no:
        components.append(norm_notif_no)
    elif norm_deadline:
        components.append(norm_deadline)

    if canonical_url and ("gov.in" in canonical_url or "nic.in" in canonical_url):
        # Official URLs serve as strong anchors
        components.append(normalize_text(canonical_url))

    fingerprint_raw = "|".join(filter(None, components))

    # Fallback to post name and deadline if org is missing
    if not fingerprint_raw:
        fingerprint_raw = f"unknown_job_{job.organization}_{job.post_name}"

    return hashlib.sha256(fingerprint_raw.encode("utf-8")).hexdigest()
