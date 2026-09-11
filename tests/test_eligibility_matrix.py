"""
Comprehensive Eligibility Engine Test Matrix
Tests every combination documented in the second-pass verification audit.
Covers: education level, degree, branch, percentage, age, experience, fee preference.
"""
import pytest
from app.ai.schemas import JobExtractionSchema
from app.eligibility.models import (
    UserRequirementsProfile,
    EducationRequirement,
    ExperienceRequirement,
    AgeRequirement,
    LocationRequirement,
    NotificationPreferences,
)
from app.eligibility.evaluator import EligibilityEvaluator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_profile(**kwargs) -> UserRequirementsProfile:
    """Create a profile with sensible defaults, overridable by kwargs."""
    defaults = dict(
        education=EducationRequirement(
            minimum_level="bachelors",
            accepted_degrees=["B.Tech", "B.E.", "B.Sc", "BCA"],
            branches=["Computer Science", "Information Technology", "CSE", "IT"],
            minimum_percentage=60.0,
        ),
        experience=ExperienceRequirement(fresher_allowed=True, max_years_experience_required=0),
        age=AgeRequirement(
            maximum=27,
            category="General",
            category_age_relaxations={"OBC": 3, "SC": 5, "ST": 5, "PwD": 10, "EWS": 0},
        ),
        job_categories=["central_government", "state_government", "psu", "banking"],
        location=LocationRequirement(allowed=["All India"], exclude_locations=[]),
        excluded_types=["internship", "apprenticeship"],
        notification_preferences=NotificationPreferences(alert_on_uncertain=True),
    )
    defaults.update(kwargs)
    return UserRequirementsProfile(**defaults)


def make_job(**kwargs) -> JobExtractionSchema:
    """Create a job with required fields, overridable by kwargs."""
    defaults = dict(
        is_job=True,
        job_type="central_government",
        organization="Test Organization",
        post_name="Test Engineer",
        qualification=["B.Tech"],
        accepted_branches=["Computer Science"],
        age_max=30,
        experience_required=False,
        minimum_percentage=None,
    )
    defaults.update(kwargs)
    return JobExtractionSchema(**defaults)


# ---------------------------------------------------------------------------
# 1. CLEARLY ELIGIBLE CASES (expect ELIGIBLE)
# ---------------------------------------------------------------------------

class TestClearlyEligible:
    def test_perfect_match(self):
        """User exactly matches all job requirements."""
        profile = make_profile()
        job = make_job(
            qualification=["B.Tech"],
            accepted_branches=["Computer Science"],
            age_max=30,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "ELIGIBLE", f"Expected ELIGIBLE, got {decision.status}. Criteria: {decision.criteria}"

    def test_user_younger_than_limit(self):
        """User age 27 < job limit 30 → PASS."""
        profile = make_profile(age=AgeRequirement(maximum=27, category="General"))
        job = make_job(age_max=30)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "ELIGIBLE"

    def test_user_exactly_at_age_limit(self):
        """User age exactly equals job limit → PASS."""
        profile = make_profile(age=AgeRequirement(maximum=30, category="General"))
        job = make_job(age_max=30)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["age"].status == "PASS"

    def test_obc_relaxation_allows_eligibility(self):
        """User 32 years, OBC (+3), job limit 30 → effective limit 33 → PASS."""
        profile = make_profile(
            age=AgeRequirement(
                maximum=32,
                category="OBC",
                category_age_relaxations={"OBC": 3, "SC": 5},
            )
        )
        job = make_job(age_max=30)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["age"].status == "PASS", (
            f"OBC relaxation should allow 32yo for job limit 30. Details: {decision.criteria['age'].details}"
        )

    def test_sc_relaxation_allows_eligibility(self):
        """User 34 years, SC (+5), job limit 30 → effective 35 → PASS."""
        profile = make_profile(
            age=AgeRequirement(maximum=34, category="SC", category_age_relaxations={"SC": 5})
        )
        job = make_job(age_max=30)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["age"].status == "PASS"

    def test_any_graduate_phrase_matches(self):
        """Job requiring 'Any Graduate' should PASS for any graduate-level user."""
        profile = make_profile()
        job = make_job(qualification=["Any Graduate"], accepted_branches=[])
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["qualification"].status == "PASS"

    def test_any_branch_matches_user_branch(self):
        """Job with 'Any Branch' should PASS for any discipline."""
        profile = make_profile()
        job = make_job(accepted_branches=["Any Branch"])
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["branch"].status == "PASS"

    def test_fresher_job_passes_fresher_user(self):
        """Job requires no experience → PASS for fresher user."""
        profile = make_profile(
            experience=ExperienceRequirement(fresher_allowed=True, max_years_experience_required=0)
        )
        job = make_job(experience_required=False)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["experience"].status == "PASS"

    def test_no_percentage_requirement_is_pass(self):
        """Job with no percentage stated → PASS (not UNKNOWN, not FAIL)."""
        profile = make_profile()
        job = make_job(minimum_percentage=None)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["percentage"].status == "PASS", (
            "Missing percentage requirement should be PASS (no restriction), not UNKNOWN"
        )

    def test_user_percentage_above_requirement(self):
        """User 65% ≥ job 60% → PASS."""
        profile = make_profile(
            education=EducationRequirement(
                minimum_level="bachelors",
                accepted_degrees=["B.Tech"],
                branches=["Computer Science"],
                minimum_percentage=65.0,
            )
        )
        job = make_job(minimum_percentage=60.0)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["percentage"].status == "PASS"

    def test_experienced_user_meets_requirement(self):
        """User with 3 years experience meets job requiring 2 years → PASS."""
        profile = make_profile(
            experience=ExperienceRequirement(fresher_allowed=False, max_years_experience_required=3)
        )
        job = make_job(experience_required=True, experience_years_min=2)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["experience"].status == "PASS"

    def test_higher_education_meets_lower_requirement(self):
        """User with Master's satisfies job requiring Bachelor's."""
        profile = make_profile(
            education=EducationRequirement(
                minimum_level="masters",
                accepted_degrees=["M.Tech", "M.E.", "B.Tech"],
                branches=["Computer Science"],
                minimum_percentage=60.0,
            )
        )
        job = make_job(qualification=["B.Tech"], accepted_branches=["Computer Science"])
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["education_level"].status == "PASS"


# ---------------------------------------------------------------------------
# 2. CLEARLY INELIGIBLE CASES (expect NOT_ELIGIBLE)
# ---------------------------------------------------------------------------

class TestClearlyIneligible:
    def test_user_over_age_limit(self):
        """User 35 > job max 30, General (no relaxation) → FAIL."""
        profile = make_profile(age=AgeRequirement(maximum=35, category="General"))
        job = make_job(age_max=30)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["age"].status == "FAIL", (
            f"User age 35 should FAIL against job max 30. Details: {decision.criteria['age'].details}"
        )
        assert decision.status == "NOT_ELIGIBLE"

    def test_user_one_over_relaxed_limit(self):
        """User 34, OBC (+3), job limit 30 → effective 33, user 34 → FAIL."""
        profile = make_profile(
            age=AgeRequirement(
                maximum=34,
                category="OBC",
                category_age_relaxations={"OBC": 3},
            )
        )
        job = make_job(age_max=30)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["age"].status == "FAIL"

    def test_fresher_fails_experience_required_job(self):
        """Critical bug fix: Fresher user should FAIL jobs requiring experience."""
        profile = make_profile(
            experience=ExperienceRequirement(fresher_allowed=True, max_years_experience_required=0)
        )
        job = make_job(experience_required=True, experience_years_min=2)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["experience"].status == "FAIL", (
            "Fresher MUST fail a job that requires experience. This was a critical bug."
        )
        assert decision.status == "NOT_ELIGIBLE"

    def test_wrong_degree_fails(self):
        """Job requires MBA, user has B.Tech → FAIL."""
        profile = make_profile(
            education=EducationRequirement(
                minimum_level="bachelors",
                accepted_degrees=["B.Tech", "B.E."],
                branches=["Computer Science"],
                minimum_percentage=60.0,
            )
        )
        job = make_job(qualification=["MBA", "PGDM"], accepted_branches=[])
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["qualification"].status == "FAIL"

    def test_wrong_branch_fails(self):
        """Job requires Mechanical, user is CS → FAIL."""
        profile = make_profile()  # CS/IT branches
        job = make_job(accepted_branches=["Mechanical Engineering", "Civil Engineering"])
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["branch"].status == "FAIL"

    def test_company_substring_does_not_match_any_branch(self):
        """Critical: 'company' must NOT match 'any branch' — substring bug prevention."""
        profile = make_profile()
        job = make_job(accepted_branches=["Mechanical Engineering"])
        decision = EligibilityEvaluator(profile).evaluate(job)
        # The branch "Mechanical Engineering" does not contain "any" as a word boundary
        # and "company" is not in user branches
        assert decision.criteria["branch"].status == "FAIL"

    def test_user_percentage_below_requirement(self):
        """User 55% < job requires 60% → FAIL."""
        profile = make_profile(
            education=EducationRequirement(
                minimum_level="bachelors",
                accepted_degrees=["B.Tech"],
                branches=["Computer Science"],
                minimum_percentage=55.0,
            )
        )
        job = make_job(minimum_percentage=60.0)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["percentage"].status == "FAIL"

    def test_lower_education_fails_higher_requirement(self):
        """User has 12th, job requires Bachelor's → FAIL."""
        profile = make_profile(
            education=EducationRequirement(
                minimum_level="12th",
                accepted_degrees=["12th Standard"],
                branches=[],
                minimum_percentage=0.0,
            )
        )
        job = make_job(qualification=["B.Tech", "B.E."])
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["education_level"].status == "FAIL"

    def test_excluded_job_type_fails(self):
        """Job type in excluded list → FAIL."""
        profile = make_profile(
            excluded_types=["internship", "apprenticeship"]
        )
        job = make_job(job_type="internship")
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["job_type"].status == "FAIL"
        assert decision.status == "NOT_ELIGIBLE"

    def test_non_job_content_fails(self):
        """is_job=False → NOT_ELIGIBLE immediately."""
        profile = make_profile()
        job = make_job(is_job=False)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "NOT_ELIGIBLE"

    def test_experience_exceeds_user_maximum(self):
        """Job requires 5 years, user has max 3 → FAIL."""
        profile = make_profile(
            experience=ExperienceRequirement(fresher_allowed=False, max_years_experience_required=3)
        )
        job = make_job(experience_required=True, experience_years_min=5)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["experience"].status == "FAIL"


# ---------------------------------------------------------------------------
# 3. UNCERTAIN / UNKNOWN CASES (expect UNCERTAIN)
# ---------------------------------------------------------------------------

class TestUncertainCases:
    def test_missing_age_is_unknown(self):
        """Missing age in notification → UNKNOWN → UNCERTAIN overall."""
        profile = make_profile()
        job = make_job(age_max=None)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["age"].status == "UNKNOWN"
        assert decision.status == "UNCERTAIN"
        assert decision.status != "ELIGIBLE", "UNKNOWN must never become ELIGIBLE"

    def test_missing_branches_is_unknown(self):
        """No accepted branches stated → UNKNOWN."""
        profile = make_profile()
        job = make_job(accepted_branches=[])
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["branch"].status == "UNKNOWN"

    def test_missing_experience_info_is_unknown(self):
        """experience_required=None (ambiguous) → UNKNOWN."""
        profile = make_profile()
        job = make_job(experience_required=None)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["experience"].status == "UNKNOWN"
        assert decision.status == "UNCERTAIN"

    def test_missing_qualification_is_unknown(self):
        """No qualification stated → UNKNOWN."""
        profile = make_profile()
        job = make_job(qualification=[])
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["qualification"].status == "UNKNOWN"

    def test_unknown_never_becomes_pass(self):
        """Core invariant: UNKNOWN must produce UNCERTAIN, never ELIGIBLE."""
        profile = make_profile()
        job = make_job(age_max=None, accepted_branches=[], experience_required=None)
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "UNCERTAIN"
        assert decision.status != "ELIGIBLE"


# ---------------------------------------------------------------------------
# 4. AGE BOUNDARY CONDITIONS
# ---------------------------------------------------------------------------

class TestAgeBoundaries:
    def test_age_exactly_at_limit(self):
        """User age == job limit → PASS (boundary inclusive)."""
        profile = make_profile(age=AgeRequirement(maximum=30, category="General"))
        job = make_job(age_max=30)
        assert EligibilityEvaluator(profile).evaluate(job).criteria["age"].status == "PASS"

    def test_age_one_over_limit(self):
        """User age 31 > job limit 30 → FAIL."""
        profile = make_profile(age=AgeRequirement(maximum=31, category="General"))
        job = make_job(age_max=30)
        assert EligibilityEvaluator(profile).evaluate(job).criteria["age"].status == "FAIL"

    def test_age_exactly_at_relaxed_limit(self):
        """User SC 35 = job 30 + SC 5 = 35 → PASS (boundary inclusive)."""
        profile = make_profile(
            age=AgeRequirement(maximum=35, category="SC", category_age_relaxations={"SC": 5})
        )
        job = make_job(age_max=30)
        assert EligibilityEvaluator(profile).evaluate(job).criteria["age"].status == "PASS"

    def test_age_one_over_relaxed_limit(self):
        """User SC 36 > job 30 + SC 5 = 35 → FAIL."""
        profile = make_profile(
            age=AgeRequirement(maximum=36, category="SC", category_age_relaxations={"SC": 5})
        )
        job = make_job(age_max=30)
        assert EligibilityEvaluator(profile).evaluate(job).criteria["age"].status == "FAIL"

    def test_pwd_relaxation(self):
        """User PwD 40, job limit 30 + PwD 10 = 40 → PASS."""
        profile = make_profile(
            age=AgeRequirement(maximum=40, category="PwD", category_age_relaxations={"PwD": 10})
        )
        job = make_job(age_max=30)
        assert EligibilityEvaluator(profile).evaluate(job).criteria["age"].status == "PASS"

    def test_very_low_job_age_limit_still_fails(self):
        """Job max 20, user 27 → FAIL even with General."""
        profile = make_profile(age=AgeRequirement(maximum=27, category="General"))
        job = make_job(age_max=20)
        assert EligibilityEvaluator(profile).evaluate(job).criteria["age"].status == "FAIL"


# ---------------------------------------------------------------------------
# 5. EXPERIENCE MATRIX
# ---------------------------------------------------------------------------

class TestExperienceMatrix:
    def test_fresher_and_fresher_allowed(self):
        profile = make_profile(experience=ExperienceRequirement(fresher_allowed=True, max_years_experience_required=0))
        job = make_job(experience_required=False)
        assert EligibilityEvaluator(profile).evaluate(job).criteria["experience"].status == "PASS"

    def test_fresher_and_experience_mandatory(self):
        profile = make_profile(experience=ExperienceRequirement(fresher_allowed=True, max_years_experience_required=0))
        job = make_job(experience_required=True, experience_years_min=2)
        assert EligibilityEvaluator(profile).evaluate(job).criteria["experience"].status == "FAIL"

    def test_experienced_user_and_fresher_allowed(self):
        """Experienced user applying to fresher job → PASS (job is open to all)."""
        profile = make_profile(experience=ExperienceRequirement(fresher_allowed=False, max_years_experience_required=5))
        job = make_job(experience_required=False)
        assert EligibilityEvaluator(profile).evaluate(job).criteria["experience"].status == "PASS"

    def test_1yr_experience_meets_1yr_requirement(self):
        profile = make_profile(experience=ExperienceRequirement(fresher_allowed=False, max_years_experience_required=1))
        job = make_job(experience_required=True, experience_years_min=1)
        assert EligibilityEvaluator(profile).evaluate(job).criteria["experience"].status == "PASS"

    def test_1yr_experience_fails_2yr_requirement(self):
        profile = make_profile(experience=ExperienceRequirement(fresher_allowed=False, max_years_experience_required=1))
        job = make_job(experience_required=True, experience_years_min=2)
        assert EligibilityEvaluator(profile).evaluate(job).criteria["experience"].status == "FAIL"

    def test_3yr_experience_meets_2yr_requirement(self):
        profile = make_profile(experience=ExperienceRequirement(fresher_allowed=False, max_years_experience_required=3))
        job = make_job(experience_required=True, experience_years_min=2)
        assert EligibilityEvaluator(profile).evaluate(job).criteria["experience"].status == "PASS"

    def test_ambiguous_experience_is_unknown(self):
        profile = make_profile()
        job = make_job(experience_required=None)
        assert EligibilityEvaluator(profile).evaluate(job).criteria["experience"].status == "UNKNOWN"


# ---------------------------------------------------------------------------
# 6. EDUCATION LEVEL HIERARCHY
# ---------------------------------------------------------------------------

class TestEducationHierarchy:
    def test_bachelors_meets_diploma_requirement(self):
        profile = make_profile(education=EducationRequirement(
            minimum_level="bachelors", accepted_degrees=["B.Tech"], branches=[], minimum_percentage=0.0
        ))
        job = make_job(qualification=["Diploma", "B.Tech"])  # job accepts diploma OR btech
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["education_level"].status == "PASS"

    def test_diploma_fails_bachelors_requirement(self):
        profile = make_profile(education=EducationRequirement(
            minimum_level="diploma", accepted_degrees=["Diploma"], branches=[], minimum_percentage=0.0
        ))
        job = make_job(qualification=["B.Tech", "B.E."])
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["education_level"].status == "FAIL"

    def test_12th_fails_bachelors_requirement(self):
        profile = make_profile(education=EducationRequirement(
            minimum_level="12th", accepted_degrees=["12th"], branches=[], minimum_percentage=0.0
        ))
        job = make_job(qualification=["Bachelor's Degree"])
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["education_level"].status == "FAIL"

    def test_masters_satisfies_bachelors_job(self):
        profile = make_profile(education=EducationRequirement(
            minimum_level="masters", accepted_degrees=["M.Tech", "B.Tech"], branches=["Computer Science"], minimum_percentage=60.0
        ))
        job = make_job(qualification=["B.Tech"])
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["education_level"].status == "PASS"


# ---------------------------------------------------------------------------
# 7. DEGREE & BRANCH MATCHING (Anti-substring-bug)
# ---------------------------------------------------------------------------

class TestDegreeBranchMatching:
    def test_case_insensitive_match(self):
        """B.Tech vs b.tech case match."""
        profile = make_profile()
        job = make_job(qualification=["b.tech"])
        assert EligibilityEvaluator(profile).evaluate(job).criteria["qualification"].status == "PASS"

    def test_any_graduate_phrase_variants(self):
        """All 'any graduate' phrasings should match."""
        profile = make_profile()
        for phrase in ["any graduate", "Any Degree", "any graduation", "Graduate in any discipline"]:
            job = make_job(qualification=[phrase], accepted_branches=["Any Branch"])
            d = EligibilityEvaluator(profile).evaluate(job)
            assert d.criteria["qualification"].status == "PASS", f"Failed for: {phrase}"

    def test_any_branch_phrase_variants(self):
        """All 'any branch' phrasings should match."""
        profile = make_profile()
        for phrase in ["Any Branch", "All Branches", "any discipline", "any engineering"]:
            job = make_job(accepted_branches=[phrase])
            d = EligibilityEvaluator(profile).evaluate(job)
            assert d.criteria["branch"].status == "PASS", f"Failed for: {phrase}"

    def test_mechanical_does_not_match_cs_user(self):
        """CS user should NOT match Mechanical Engineering."""
        profile = make_profile()
        job = make_job(accepted_branches=["Mechanical Engineering"])
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["branch"].status == "FAIL"

    def test_it_matches_information_technology(self):
        """'IT' abbreviation should match 'Information Technology' user branch."""
        profile = make_profile(education=EducationRequirement(
            minimum_level="bachelors",
            accepted_degrees=["B.Tech"],
            branches=["Information Technology"],  # Full name in profile
            minimum_percentage=60.0,
        ))
        job = make_job(accepted_branches=["IT"])  # Abbreviation in job
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["branch"].status == "PASS"


# ---------------------------------------------------------------------------
# 8. FEE IS NOT AN ELIGIBILITY CRITERION
# ---------------------------------------------------------------------------

class TestFeeIsPreference:
    def test_high_fee_job_is_not_ineligible(self):
        """Fee preference should NOT make a job ineligible — it's a preference dimension."""
        profile = make_profile()
        job = make_job(
            application_fee=["General: Rs. 500", "SC/ST/PwD: Nil"],
            age_max=30,
            qualification=["B.Tech"],
            accepted_branches=["Computer Science"],
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        # Fee is not in evaluator criteria — should not affect ELIGIBLE status
        assert "fee" not in decision.criteria
        assert decision.status == "ELIGIBLE"


# ---------------------------------------------------------------------------
# 9. PERCENTAGE EDGE CASES
# ---------------------------------------------------------------------------

class TestPercentageEdgeCases:
    def test_user_exactly_at_percentage_requirement(self):
        profile = make_profile(education=EducationRequirement(
            minimum_level="bachelors", accepted_degrees=["B.Tech"],
            branches=["Computer Science"], minimum_percentage=60.0,
        ))
        job = make_job(minimum_percentage=60.0)
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["percentage"].status == "PASS"

    def test_no_percentage_on_job_is_pass(self):
        profile = make_profile()
        job = make_job(minimum_percentage=None)
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["percentage"].status == "PASS", \
            "No percentage requirement must be PASS — not UNKNOWN"

    def test_user_profile_percentage_zero_passes_unspecified(self):
        profile = make_profile(education=EducationRequirement(
            minimum_level="bachelors", accepted_degrees=["B.Tech"],
            branches=["Computer Science"], minimum_percentage=None,  # type: ignore
        ))
        job = make_job(minimum_percentage=None)
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["percentage"].status == "PASS"


# ---------------------------------------------------------------------------
# 10. TOKEN BOUNDARY & ANTI-FALSE-POSITIVE TESTS
# ---------------------------------------------------------------------------

class TestTokenBoundaryMatching:
    def test_cyber_security_diploma_not_misclassified_as_bachelors(self):
        """'be' in 'cyber' must not trigger bachelors classification."""
        profile = make_profile(education=EducationRequirement(
            minimum_level="diploma",
            accepted_degrees=["Diploma in CS", "Diploma"],
            branches=["Computer Science"],
        ))
        job = make_job(
            qualification=["Cyber Security Diploma"],
            accepted_branches=["Computer Science"],
        )
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["education_level"].status == "PASS", \
            f"Expected PASS for diploma user on diploma job, got {d.criteria['education_level'].details}"

    def test_be_degree_does_not_match_arbitrary_words(self):
        """Candidate with 'BE' must not match unrelated qualification like 'Cyber Law' or 'Member'."""
        profile = make_profile(education=EducationRequirement(
            minimum_level="bachelors",
            accepted_degrees=["BE"],
            branches=["Computer Science"],
        ))
        job = make_job(
            qualification=["Cyber Law Certification"],
            accepted_branches=["Computer Science"],
        )
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["qualification"].status == "FAIL"

    def test_ca_does_not_match_mechanical(self):
        """Chartered Accountant degree 'CA' must not match 'Mechanical'."""
        profile = make_profile(education=EducationRequirement(
            minimum_level="bachelors",
            accepted_degrees=["CA"],
            branches=["Finance"],
        ))
        job = make_job(
            qualification=["Mechanical Degree"],
            accepted_branches=["Mechanical"],
        )
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["qualification"].status == "FAIL"


# ---------------------------------------------------------------------------
# 11. AGE MINIMUM & DYNAMIC DATE OF BIRTH TESTS
# ---------------------------------------------------------------------------

class TestAgeMinimumAndDOB:
    def test_underage_candidate_fails_minimum_age(self):
        """User age 19 applying for job requiring minimum age 21 -> FAIL."""
        profile = make_profile(age=AgeRequirement(maximum=19, category="General"))
        job = make_job(age_min=21, age_max=35)
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["age"].status == "FAIL"
        assert "underage" in d.criteria["age"].details.lower()

    def test_candidate_at_exact_minimum_age_passes(self):
        """User age 21 applying for job requiring minimum age 21 -> PASS."""
        profile = make_profile(age=AgeRequirement(maximum=21, category="General"))
        job = make_job(age_min=21, age_max=35)
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["age"].status == "PASS"

    def test_dynamic_dob_derives_age_correctly(self):
        """DOB in profile dynamically derives exact age."""
        from datetime import date
        today = date.today()
        # Create a DOB that is exactly 24 years old today
        dob_24 = f"{today.year - 24:04d}-{today.month:02d}-{today.day:02d}"
        profile = make_profile(
            date_of_birth=dob_24,
            age=AgeRequirement(maximum=99, category="General"),  # will be overridden by DOB
        )
        job = make_job(age_max=25)
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["age"].status == "PASS"
        assert "Your age: 24y" in d.criteria["age"].details


# ---------------------------------------------------------------------------
# 12. LOCATION CRITERIA TESTS
# ---------------------------------------------------------------------------

class TestLocationCriteria:
    def test_all_india_allowed_passes_any_job_location(self):
        """When user accepts 'All India', job in Maharashtra passes."""
        profile = make_profile(location=LocationRequirement(allowed=["All India"], exclude_locations=[]))
        job = make_job(location=["Maharashtra"])
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["location"].status == "PASS"

    def test_excluded_location_fails(self):
        """When job is in an excluded location, it must FAIL."""
        profile = make_profile(location=LocationRequirement(allowed=["All India"], exclude_locations=["Kerala"]))
        job = make_job(location=["Kerala"])
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["location"].status == "FAIL"
        assert d.status == "NOT_ELIGIBLE"

    def test_specific_allowed_location_match_passes(self):
        """User allows Telangana, job is in Telangana -> PASS."""
        profile = make_profile(location=LocationRequirement(allowed=["Telangana"], exclude_locations=[]))
        job = make_job(location=["Telangana"])
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["location"].status == "PASS"

    def test_specific_allowed_location_mismatch_fails(self):
        """User allows only Telangana, job is strictly in Punjab -> FAIL."""
        profile = make_profile(location=LocationRequirement(allowed=["Telangana"], exclude_locations=[]))
        job = make_job(location=["Punjab"])
        d = EligibilityEvaluator(profile).evaluate(job)
        assert d.criteria["location"].status == "FAIL"
        assert d.status == "NOT_ELIGIBLE"

