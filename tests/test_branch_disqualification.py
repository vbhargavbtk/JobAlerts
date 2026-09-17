"""
Unit tests for Branch Strictness Matrix & Direct Disqualification logic.
Verifies that posts requiring branches mapped to DO_NOT_ACCEPT (Civil, Mechanical, Electrical, Electronics)
are directly disqualified (NOT_ELIGIBLE) rather than sent to manual review / UNCERTAIN.
"""
import pytest
from app.ai.schemas import JobExtractionSchema, PostItemSchema
from app.eligibility.models import UserRequirementsProfile
from app.eligibility.evaluator import EligibilityEvaluator


@pytest.fixture
def cse_profile():
    profile = UserRequirementsProfile()
    profile.education.minimum_level = "bachelors"
    profile.education.accepted_degrees = ["B.Tech", "B.E.", "Graduation"]
    profile.education.branches = ["Computer Science", "Information Technology", "CSE", "IT"]
    profile.branch_mappings = {
        "Computer Science": "ACCEPT",
        "Information Technology": "ACCEPT",
        "CSE": "ACCEPT",
        "IT": "ACCEPT",
        "Electronics": "ACCEPT",
        "Electrical": "DO_NOT_ACCEPT",
        "Mechanical": "DO_NOT_ACCEPT",
        "Civil": "DO_NOT_ACCEPT",
    }
    return profile


def test_civil_post_in_title_directly_disqualified(cse_profile):
    """Job with Civil in post title but empty accepted_branches must be NOT_ELIGIBLE."""
    evaluator = EligibilityEvaluator(cse_profile)
    job = JobExtractionSchema(
        is_job=True,
        organization="Irrigation Department",
        post_name="Junior Engineer (Civil)",
        qualification=["B.Tech"],
        accepted_branches=[],
        experience_required=False
    )
    decision = evaluator.evaluate(job)
    assert decision.status == "NOT_ELIGIBLE"
    assert decision.criteria["branch"].status == "FAIL"
    assert "DO_NOT_ACCEPT" in decision.criteria["branch"].details or "EXCLUDE" in decision.criteria["branch"].details


def test_mechanical_post_directly_disqualified(cse_profile):
    """Job requiring Mechanical Engineering must be directly NOT_ELIGIBLE."""
    evaluator = EligibilityEvaluator(cse_profile)
    job = JobExtractionSchema(
        is_job=True,
        organization="Railways",
        post_name="Assistant Loco Pilot / Mechanical Engineer",
        qualification=["Degree in Mechanical Engineering"],
        accepted_branches=["Mechanical Engineering"],
        experience_required=False
    )
    decision = evaluator.evaluate(job)
    assert decision.status == "NOT_ELIGIBLE"
    assert decision.criteria["branch"].status == "FAIL"


def test_electrical_disqualified_when_set_to_do_not_accept(cse_profile):
    """When Electrical is set to DO_NOT_ACCEPT, electrical jobs must be directly NOT_ELIGIBLE."""
    cse_profile.branch_mappings["Electrical"] = "DO_NOT_ACCEPT"
    evaluator = EligibilityEvaluator(cse_profile)
    job = JobExtractionSchema(
        is_job=True,
        organization="Power Grid",
        post_name="Executive Trainee (Electrical)",
        qualification=["B.Tech"],
        accepted_branches=["Electrical Engineering"],
        experience_required=False
    )
    decision = evaluator.evaluate(job)
    assert decision.status == "NOT_ELIGIBLE"
    assert decision.criteria["branch"].status == "FAIL"


def test_electronics_disqualified_when_excluded(cse_profile):
    """When Electronics is set to DO_NOT_ACCEPT, electronics jobs must be directly NOT_ELIGIBLE."""
    cse_profile.branch_mappings["Electronics"] = "DO_NOT_ACCEPT"
    # Remove Electronics from education.branches so candidate only has CSE
    cse_profile.education.branches = ["Computer Science", "Information Technology", "CSE", "IT"]
    evaluator = EligibilityEvaluator(cse_profile)
    job = JobExtractionSchema(
        is_job=True,
        organization="ISRO",
        post_name="Scientist/Engineer 'SC' (Electronics)",
        qualification=["B.Tech in Electronics"],
        accepted_branches=["Electronics"],
        experience_required=False
    )
    decision = evaluator.evaluate(job)
    assert decision.status == "NOT_ELIGIBLE"
    assert decision.criteria["branch"].status == "FAIL"


def test_computer_science_post_passes(cse_profile):
    """Job requiring Computer Science must PASS."""
    evaluator = EligibilityEvaluator(cse_profile)
    job = JobExtractionSchema(
        is_job=True,
        organization="NIC",
        post_name="Scientist 'B' (Computer Science)",
        qualification=["B.Tech"],
        accepted_branches=["Computer Science", "Information Technology"],
        age_max=30,
        experience_required=False
    )
    decision = evaluator.evaluate(job)
    assert decision.status == "ELIGIBLE"
    assert decision.criteria["branch"].status == "PASS"


def test_multi_branch_post_accepting_cs_passes(cse_profile):
    """Job accepting Civil, Mechanical and Computer Science must pass because CS is accepted."""
    evaluator = EligibilityEvaluator(cse_profile)
    job = JobExtractionSchema(
        is_job=True,
        organization="State PSC",
        post_name="Assistant Engineer (Multiple Disciplines)",
        qualification=["B.Tech"],
        accepted_branches=["Civil", "Mechanical", "Computer Science"],
        age_max=30,
        experience_required=False
    )
    decision = evaluator.evaluate(job)
    assert decision.status == "ELIGIBLE"
    assert decision.criteria["branch"].status == "PASS"


def test_nursing_officer_empty_qual_directly_disqualified(cse_profile):
    """Nursing Officer post with empty qualification list must be directly NOT_ELIGIBLE."""
    evaluator = EligibilityEvaluator(cse_profile)
    job = JobExtractionSchema(
        is_job=True,
        organization="Staff Selection Commission",
        post_name="Nursing Officer",
        qualification=[],
        accepted_branches=[],
        experience_required=False
    )
    decision = evaluator.evaluate(job)
    assert decision.status == "NOT_ELIGIBLE"
    assert decision.criteria["qualification"].status == "FAIL"
    assert "Medical/Nursing" in decision.criteria["qualification"].details


def test_paramedical_post_empty_qual_directly_disqualified(cse_profile):
    """Paramedical post with empty qualification list must be directly NOT_ELIGIBLE."""
    evaluator = EligibilityEvaluator(cse_profile)
    job = JobExtractionSchema(
        is_job=True,
        organization="RRB",
        post_name="Various Posts of Paramedical Categories",
        qualification=[],
        accepted_branches=[],
        experience_required=False
    )
    decision = evaluator.evaluate(job)
    assert decision.status == "NOT_ELIGIBLE"
    assert decision.criteria["qualification"].status == "FAIL"
