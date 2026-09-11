"""
Fee Parsing Tests — verifies the check_fee_status function against real-world
government job fee strings. Critical regression suite.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import check_fee_status


class TestFeeParsingRealWorld:
    def test_empty_list_is_not_free(self):
        """Empty fee list = fee not stated, NOT free."""
        r = check_fee_status([])
        assert r["is_free"] is False
        assert r["label"] == "Fee not stated", f"Got: {r['label']}"

    def test_nil_is_free(self):
        r = check_fee_status(["Nil"])
        assert r["is_free"] is True
        assert r["has_fee"] is False

    def test_free_is_free(self):
        r = check_fee_status(["Free", "No application fee for all categories"])
        assert r["is_free"] is True

    def test_rs_zero_is_free(self):
        r = check_fee_status(["Rs. 0", "Nil for SC/ST"])
        assert r["is_free"] is True
        assert r["has_fee"] is False

    def test_rupee_symbol_zero_is_free(self):
        r = check_fee_status(["₹0"])
        assert r["is_free"] is True

    def test_rs100_has_fee(self):
        r = check_fee_status(["Rs 100"])
        assert r["has_fee"] is True
        assert r["is_free"] is False

    def test_rupee_500_has_fee(self):
        r = check_fee_status(["₹500 for General", "₹300 for OBC", "Nil for SC/ST/PwD"])
        assert r["has_fee"] is True
        assert r["is_free"] is False
        assert "category" in r["label"].lower() or "500" in r["label"] or "300" in r["label"]

    def test_processing_fee(self):
        """₹100 + processing fee → has fee."""
        r = check_fee_status(["₹100 + processing fee"])
        assert r["has_fee"] is True

    def test_slash_format_100_dash(self):
        """100/- format → has fee."""
        r = check_fee_status(["100/-"])
        assert r["has_fee"] is True

    def test_no_fee_phrase(self):
        r = check_fee_status(["No fee for all candidates"])
        assert r["is_free"] is True

    def test_sc_st_exempt_still_has_fee(self):
        """SC/ST exempt but general pays → has_fee=True, is_free=False."""
        r = check_fee_status(["General: Rs. 500", "SC/ST/PwD: Exempt"])
        assert r["has_fee"] is True
        assert r["is_free"] is False

    def test_exam_fee_keyword(self):
        r = check_fee_status(["Exam fee: 200"])
        assert r["has_fee"] is True

    def test_application_fee_500(self):
        r = check_fee_status(["Application fee: 500"])
        assert r["has_fee"] is True

    def test_advertisement_number_not_treated_as_fee(self):
        """Advert numbers like '2025/01' should NOT be treated as fees."""
        r = check_fee_status(["Refer to advertisement no. 2025/01 for details"])
        # No currency symbol or fee keyword → should NOT trigger has_fee
        assert r["has_fee"] is False

    def test_vacancy_count_not_treated_as_fee(self):
        """100 vacancies mentioned → NOT a fee."""
        r = check_fee_status(["100 vacancies available"])
        assert r["has_fee"] is False

    def test_fee_details_unavailable(self):
        r = check_fee_status(["Fee details unavailable"])
        assert r["has_fee"] is False
        assert r["is_free"] is False

    def test_inr_prefix(self):
        r = check_fee_status(["INR 300"])
        assert r["has_fee"] is True

    def test_1000_comma_format(self):
        r = check_fee_status(["₹1,000"])
        assert r["has_fee"] is True
