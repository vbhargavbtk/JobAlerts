import pytest
from app.ai.schemas import JobExtractionSchema
from app.deduplication.fingerprint import compute_job_fingerprint


def test_fingerprint_identical_recruitments():
    job1 = JobExtractionSchema(
        is_job=True,
        organization="ISRO - URSC",
        post_name="Scientist Engineer SC",
        notification_number="URSC:01:2026",
        application_deadline="2026-10-15"
    )
    job2 = JobExtractionSchema(
        is_job=True,
        organization="isro - ursc ",
        post_name="Scientist  Engineer  SC",
        notification_number="ursc:01:2026",
        application_deadline="2026-10-15"
    )

    fp1 = compute_job_fingerprint(job1, "https://isro.gov.in/ursc2026")
    fp2 = compute_job_fingerprint(job2, "https://isro.gov.in/ursc2026")

    assert fp1 == fp2
    assert len(fp1) == 64  # SHA-256 hex length
