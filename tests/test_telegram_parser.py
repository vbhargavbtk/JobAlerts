import pytest
from app.telegram.message_parser import extract_urls, classify_pre_filter


def test_extract_urls():
    text = "Check notification at https://upsc.gov.in/notif.pdf and apply at www.drdo.gov.in/apply now!"
    urls = extract_urls(text)
    assert "https://upsc.gov.in/notif.pdf" in urls
    assert any("drdo.gov.in" in u for u in urls)


def test_classify_pre_filter_job():
    job_text = "New recruitment notification for 500 assistant engineers. Apply online before 30th Sept."
    category, is_job = classify_pre_filter(job_text)
    assert is_job is True
    assert category == "potential_job"


def test_classify_pre_filter_result():
    result_text = "SSC CGL 2026 final result declared and merit list published on official site."
    category, is_job = classify_pre_filter(result_text)
    assert is_job is False
    assert category == "exam_result"
