"""
Unit Tests for Personal Job Eligibility & Preference Profile
Tests the 3-tier separation:
  - HARD ELIGIBILITY (official qualification)
  - PERSONAL PREFERENCES (interest in applying)
  - APPLICATION CONSTRAINTS (feasibility/warnings)
And verifies combined classification results:
  - ELIGIBLE + WANT TO APPLY
  - ELIGIBLE + MAYBE
  - ELIGIBLE + NOT INTERESTED
  - NOT_ELIGIBLE
  - UNCERTAIN
"""
import pytest
from app.ai.schemas import JobExtractionSchema
from app.eligibility.models import (
    UserRequirementsProfile,
    PersonalDetails,
    RolePreferences,
    ConstraintsPreferences,
    ClassificationPreferences,
    AgeRequirement,
    EducationRequirement,
)
from app.eligibility.evaluator import EligibilityEvaluator


@pytest.fixture
def default_evaluator():
    profile = UserRequirementsProfile()
    return EligibilityEvaluator(profile)


def test_preferred_organization_becomes_want_to_apply(default_evaluator):
    """An eligible job from ISRO (in preferred_organizations) should be WANT_TO_APPLY."""
    job = JobExtractionSchema(
        is_job=True,
        job_type="central_government",
        organization="ISRO - Indian Space Research Organisation",
        post_name="Scientist / Engineer SC (Computer Science)",
        qualification=["B.Tech"],
        accepted_branches=["Computer Science"],
        age_max=30,
        experience_required=False,
    )
    decision = default_evaluator.evaluate(job)
    assert decision.status == "ELIGIBLE"
    assert decision.preference_status == "WANT_TO_APPLY"
    assert decision.combined_status == "ELIGIBLE + WANT TO APPLY"
    assert "preferred_organization" in decision.preference_breakdown


def test_avoided_organization_becomes_not_interested():
    """If user adds an organization to avoid_organizations, job is ELIGIBLE + NOT INTERESTED."""
    profile = UserRequirementsProfile(
        avoid_organizations=["Specific Dept of Unwanted Affairs"]
    )
    evaluator = EligibilityEvaluator(profile)
    job = JobExtractionSchema(
        is_job=True,
        job_type="central_government",
        organization="Specific Dept of Unwanted Affairs",
        post_name="Assistant Section Officer",
        qualification=["Graduation in any discipline"],
        accepted_branches=[],
        age_max=30,
        experience_required=False,
    )
    decision = evaluator.evaluate(job)
    assert decision.status == "ELIGIBLE"  # Hard eligibility still passes!
    assert decision.preference_status == "NOT_INTERESTED"
    assert decision.combined_status == "ELIGIBLE + NOT INTERESTED"
    assert "avoid_organization" in decision.preference_breakdown


def test_avoided_role_becomes_not_interested(default_evaluator):
    """Avoided role like Police / Constable should be NOT_INTERESTED even if educationally eligible."""
    job = JobExtractionSchema(
        is_job=True,
        job_type="state_government",
        organization="State Police Recruitment Board",
        post_name="Police Sub Inspector",
        qualification=["Graduation in any discipline"],
        accepted_branches=[],
        age_max=30,
        experience_required=False,
        important_conditions=["Physical Endurance Test running 1600m"],
    )
    decision = default_evaluator.evaluate(job)
    # Even if degree is graduation, candidate avoids police/uniformed roles
    assert decision.preference_status == "NOT_INTERESTED"
    assert decision.combined_status == "ELIGIBLE + NOT INTERESTED"
    assert len(decision.constraints_warnings) > 0


def test_physical_tests_constraint_warning():
    """If candidate refuses physical tests, job requiring PET gets warning and downgrade."""
    profile = UserRequirementsProfile(
        constraints=ConstraintsPreferences(willing_physical_tests=False)
    )
    evaluator = EligibilityEvaluator(profile)
    job = JobExtractionSchema(
        is_job=True,
        job_type="central_government",
        organization="Central Bureau of Investigation",
        post_name="Sub Inspector",
        qualification=["Bachelor Degree"],
        accepted_branches=[],
        age_max=30,
        experience_required=False,
        selection_process=["Written Exam", "Physical Measurement and Endurance Test"],
    )
    decision = evaluator.evaluate(job)
    assert decision.status == "ELIGIBLE"
    assert any("physical" in w.lower() for w in decision.constraints_warnings)


def test_fee_constraint_and_category_exemption():
    """A high fee job triggers warning, but not if candidate's category is exempt."""
    # Profile with general category and max fee 500
    gen_profile = UserRequirementsProfile(
        age=AgeRequirement(category="General"),
        constraints=ConstraintsPreferences(max_application_fee=500, exclude_high_fee_jobs=True),
    )
    gen_eval = EligibilityEvaluator(gen_profile)

    job = JobExtractionSchema(
        is_job=True,
        job_type="central_government",
        organization="UPSC",
        post_name="Assistant Director",
        qualification=["B.Tech"],
        accepted_branches=["Computer Science"],
        age_max=30,
        experience_required=False,
        application_fee=["General/OBC: Rs 1000", "SC/ST/PwD/Women: Exempted"],
    )

    gen_decision = gen_eval.evaluate(job)
    assert gen_decision.preference_status == "NOT_INTERESTED"
    assert any("exceeds maximum limit" in w for w in gen_decision.constraints_warnings)

    # SC Profile with same job: exempt, so fee warning should not trigger!
    sc_profile = UserRequirementsProfile(
        age=AgeRequirement(category="SC"),
        constraints=ConstraintsPreferences(max_application_fee=500, exclude_high_fee_jobs=True),
    )
    sc_eval = EligibilityEvaluator(sc_profile)
    sc_decision = sc_eval.evaluate(job)
    assert not any("exceeds maximum limit" in w for w in sc_decision.constraints_warnings)


def test_hard_ineligible_never_overridden_by_preference():
    """A job where age or education fails is strictly NOT_ELIGIBLE regardless of preferences."""
    profile = UserRequirementsProfile(
        preferred_organizations=["ISRO"],
        age=AgeRequirement(maximum=28, category="General"),
    )
    evaluator = EligibilityEvaluator(profile)
    job = JobExtractionSchema(
        is_job=True,
        job_type="central_government",
        organization="ISRO",
        post_name="Scientist Engineer",
        qualification=["B.Tech"],
        accepted_branches=["Civil"],  # User only accepts CS/IT
        age_max=35,
        experience_required=False,
    )
    decision = evaluator.evaluate(job)
    assert decision.status == "NOT_ELIGIBLE"
    assert decision.combined_status == "NOT_ELIGIBLE"
    # Even though ISRO was preferred, hard eligibility cannot be overridden
    assert decision.action_recommended == "DISCARD"


def test_configurable_unknown_handling():
    """Tests REVIEW vs POTENTIALLY_ELIGIBLE vs NOT_ELIGIBLE for missing fields."""
    job_with_missing_branches = JobExtractionSchema(
        is_job=True,
        job_type="central_government",
        organization="Defense Research Center",
        post_name="Scientist B (Technical)",
        qualification=["B.Tech"],
        accepted_branches=[],  # Missing branches for specialized technical post
        age_max=30,
        experience_required=False,
    )

    # 1. Default: REVIEW -> UNCERTAIN (when profile requires specific branches)
    strict_profile = UserRequirementsProfile(
        education=EducationRequirement(branches=["Computer Science"])
    )
    eval_review = EligibilityEvaluator(strict_profile)
    dec_review = eval_review.evaluate(job_with_missing_branches)
    assert dec_review.status == "UNCERTAIN"
    assert dec_review.combined_status == "UNCERTAIN"

    # 2. Configured: NOT_ELIGIBLE
    discard_profile = UserRequirementsProfile(
        education=EducationRequirement(branches=["Computer Science"]),
        classification_preferences=ClassificationPreferences(unknown_handling="NOT_ELIGIBLE")
    )
    eval_discard = EligibilityEvaluator(discard_profile)
    dec_discard = eval_discard.evaluate(job_with_missing_branches)
    assert dec_discard.status == "NOT_ELIGIBLE"
    assert dec_discard.combined_status == "NOT_ELIGIBLE"

    # 3. Configured: POTENTIALLY_ELIGIBLE
    potential_profile = UserRequirementsProfile(
        education=EducationRequirement(branches=["Computer Science"]),
        classification_preferences=ClassificationPreferences(unknown_handling="POTENTIALLY_ELIGIBLE")
    )
    eval_potential = EligibilityEvaluator(potential_profile)
    dec_potential = eval_potential.evaluate(job_with_missing_branches)
    assert dec_potential.status == "ELIGIBLE"
    assert "ELIGIBLE" in dec_potential.combined_status
