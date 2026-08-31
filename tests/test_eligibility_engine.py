import pytest
from app.ai.schemas import JobExtractionSchema
from app.eligibility.models import UserRequirementsProfile
from app.eligibility.evaluator import EligibilityEvaluator


@pytest.fixture
def base_profile():
    return UserRequirementsProfile()


def test_clearly_eligible_job(base_profile):
    job = JobExtractionSchema(
        is_job=True,
        job_type="central_government",
        organization="ISRO",
        post_name="Scientist/Engineer 'SC'",
        qualification=["B.E.", "B.Tech"],
        accepted_branches=["Computer Science", "Information Technology"],
        age_min=18,
        age_max=30,
        experience_required=False,
        vacancies=45
    )
    evaluator = EligibilityEvaluator(base_profile)
    decision = evaluator.evaluate(job)
    assert decision.status == "ELIGIBLE"
    assert decision.action_recommended == "ALERT"


def test_clearly_ineligible_job_age_failed(base_profile):
    job = JobExtractionSchema(
        is_job=True,
        job_type="central_government",
        organization="DRDO",
        post_name="Junior Research Fellow",
        qualification=["B.Tech"],
        accepted_branches=["Computer Science"],
        age_max=25,  # User profile max is 30, so job max 25 fails user who is 30
        experience_required=False
    )
    evaluator = EligibilityEvaluator(base_profile)
    decision = evaluator.evaluate(job)
    assert decision.status == "NOT_ELIGIBLE"
    assert decision.criteria["age"].status == "FAIL"


def test_clearly_ineligible_job_experience_failed(base_profile):
    job = JobExtractionSchema(
        is_job=True,
        job_type="psu",
        organization="ONGC",
        post_name="Senior Engineer",
        qualification=["B.Tech"],
        accepted_branches=["CSE"],
        age_max=35,
        experience_required=True,
        experience_years_min=5  # User profile maximum experience is 2 years
    )
    evaluator = EligibilityEvaluator(base_profile)
    decision = evaluator.evaluate(job)
    assert decision.status == "NOT_ELIGIBLE"
    assert decision.criteria["experience"].status == "FAIL"


def test_uncertain_eligibility_unknown_never_becomes_pass(base_profile):
    # Job has missing age and missing branches in excerpt
    job = JobExtractionSchema(
        is_job=True,
        job_type="central_government",
        organization="BEL",
        post_name="Project Engineer",
        qualification=["B.Tech"],
        accepted_branches=[],  # Unstated
        age_max=None,          # Unstated
        experience_required=False
    )
    evaluator = EligibilityEvaluator(base_profile)
    decision = evaluator.evaluate(job)
    # Specification rule: Any UNKNOWN mandatory requirement MUST yield UNCERTAIN, never PASS!
    assert decision.status == "UNCERTAIN"
    assert decision.status != "ELIGIBLE"
    assert decision.criteria["age"].status == "UNKNOWN"
    assert decision.action_recommended == "UNCERTAIN_ALERT"
