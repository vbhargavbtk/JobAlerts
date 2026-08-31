import pytest
from app.content.source_verifier import classify_source_domain


def test_classify_official_domains():
    src_type, status, conf = classify_source_domain("https://upsc.gov.in/recruitment/exam")
    assert src_type == "official"
    assert status == "verified"
    assert conf == 1.0

    src_type2, status2, conf2 = classify_source_domain("https://drdo.res.in/circulars")
    assert src_type2 == "official"
    assert status2 == "verified"


def test_classify_secondary_aggregator_domains():
    src_type, status, conf = classify_source_domain("https://www.sarkariresult.com/latestjobs")
    assert src_type == "secondary"
    assert status == "unverified"
    assert conf < 1.0
