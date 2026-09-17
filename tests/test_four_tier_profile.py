"""
Unit and Integration Tests for 4-Tier Personal Profile & Job Classification Engine
Verifies:
1. 10+2 Subject requirements (Criterion 9: Mathematics / Physics verification)
2. Physical measurement standards (Criterion 10: Minimum height / chest evaluation)
3. Separation of Physical Ability (Height) from Physical Preference (PET running)
4. Application Readiness (Tier D: EWS validity, Licences, NOC, Document warnings)
5. Full 4-Tier serialization & database model roundtrip
"""
import pytest
from app.ai.schemas import JobExtractionSchema
from app.eligibility.models import (
    UserRequirementsProfile,
    PersonalDetails,
    EducationRecord,
    SubjectsProfile10_12,
    ExperienceRecord,
    LicenceRecord,
    PhysicalEligibility,
    MedicalStandards,
    SalaryPreferences,
    DocumentReadinessRecord,
    EducationRequirement,
    ExperienceRequirement,
    AgeRequirement,
    LocationRequirement,
)
from app.eligibility.evaluator import EligibilityEvaluator


def build_base_profile(**kwargs) -> UserRequirementsProfile:
    """Helper to construct a complete 4-tier profile with default values."""
    defaults = dict(
        personal=PersonalDetails(
            full_name="Candidate Test",
            gender="Male",
            nationality="Indian",
            state_of_domicile="Andhra Pradesh",
            current_state="Telangana",
            current_city="Hyderabad",
            willing_to_relocate_all_india=True,
        ),
        education=EducationRequirement(
            minimum_level="bachelors",
            accepted_degrees=["B.Tech", "B.E.", "Bachelor Degree", "12th"],
            branches=["Computer Science", "Information Technology", "CSE", "General", "All Subjects"],
            minimum_percentage=60.0,
        ),
        education_records=[
            EducationRecord(level="10th", degree_name="SSC", branch="All Subjects", percentage=88.0),
            EducationRecord(level="12th", degree_name="Intermediate", branch="Science (PCM)", percentage=80.0),
            EducationRecord(level="bachelors", degree_name="B.Tech", branch="Computer Science and Engineering", percentage=72.0),
        ],
        subjects_10_12=SubjectsProfile10_12(
            twelfth_stream="Science-PCM",
            studied_maths_12th=True,
            studied_physics_12th=True,
            studied_chemistry_12th=True,
            studied_biology_12th=False,
            studied_computer_science_12th=True,
            studied_english=True,
        ),
        experience=ExperienceRequirement(fresher_allowed=True, max_years_experience_required=0),
        experience_records=[],
        age=AgeRequirement(
            maximum=32,
            category="General",
            category_age_relaxations={"OBC": 3, "SC": 5, "ST": 5, "EWS": 0},
        ),
        physical=PhysicalEligibility(
            height_cm=172.0,
            chest_normal_cm=82.0,
            chest_expanded_cm=87.0,
            willing_physical_tests=False,  # Does not want PET
            willing_police_standards=False,
        ),
        medical=MedicalStandards(
            willing_medical_exam=True,
            has_color_blindness=False,
            visual_standards_acceptable=True,
        ),
        salary_preferences=SalaryPreferences(
            min_gross_monthly_inr=40000,
            is_hard_filter=False,
        ),
        documents_readiness={
            "degree_cert": DocumentReadinessRecord(document_key="degree_cert", name="Degree Certificate", status="AVAILABLE"),
            "tenth_cert": DocumentReadinessRecord(document_key="tenth_cert", name="10th Certificate", status="AVAILABLE"),
            "caste_ews_cert": DocumentReadinessRecord(document_key="caste_ews_cert", name="Category / EWS Certificate", status="AVAILABLE"),
        },
    )
    defaults.update(kwargs)
    return UserRequirementsProfile(**defaults)


def test_10_plus_2_maths_requirement_pass():
    """Candidate with 10+2 Mathematics passes job requiring Mathematics in intermediate."""
    profile = build_base_profile()
    evaluator = EligibilityEvaluator(profile)

    job = JobExtractionSchema(
        is_job=True,
        job_type="central_government",
        organization="Indian Coast Guard",
        post_name="Navik (General Duty)",
        qualification=["12th"],
        important_conditions=["Must have passed 10+2 with Mathematics and Physics"],
        age_max=32,
        experience_required=False,
    )

    decision = evaluator.evaluate(job)
    assert decision.status == "ELIGIBLE"
    assert "subjects_10_12" in decision.criteria
    assert decision.criteria["subjects_10_12"].status == "PASS"


def test_10_plus_2_maths_requirement_fail():
    """Candidate without 10+2 Mathematics fails job requiring Mathematics."""
    profile = build_base_profile(
        subjects_10_12=SubjectsProfile10_12(
            twelfth_stream="Commerce",
            studied_maths_12th=False,
            studied_physics_12th=False,
        )
    )
    evaluator = EligibilityEvaluator(profile)

    job = JobExtractionSchema(
        is_job=True,
        job_type="central_government",
        organization="Indian Coast Guard",
        post_name="Navik (General Duty)",
        qualification=["12th"],
        important_conditions=["Must have passed 10+2 with Mathematics and Physics"],
        age_max=32,
        experience_required=False,
    )

    decision = evaluator.evaluate(job)
    assert decision.status == "NOT_ELIGIBLE"
    assert "subjects_10_12" in decision.criteria
    assert decision.criteria["subjects_10_12"].status == "FAIL"
    assert "Mathematics" in decision.criteria["subjects_10_12"].details


def test_physical_height_standard_pass():
    """Candidate with height 175cm passes minimum height 170cm requirement."""
    profile = build_base_profile(
        physical=PhysicalEligibility(height_cm=175.0, willing_physical_tests=True)
    )
    evaluator = EligibilityEvaluator(profile)

    job = JobExtractionSchema(
        is_job=True,
        job_type="central_government",
        organization="Central Armed Police Forces",
        post_name="Assistant Commandant",
        qualification=["Bachelor Degree"],
        important_conditions=["Minimum height required: 170 cm for male candidates"],
        age_max=32,
        experience_required=False,
    )

    decision = evaluator.evaluate(job)
    assert decision.status == "ELIGIBLE"
    assert "physical_standards" in decision.criteria
    assert decision.criteria["physical_standards"].status == "PASS"


def test_physical_height_standard_fail():
    """Candidate with height 168cm fails minimum height 170cm requirement."""
    profile = build_base_profile(
        physical=PhysicalEligibility(height_cm=168.0, willing_physical_tests=True)
    )
    evaluator = EligibilityEvaluator(profile)

    job = JobExtractionSchema(
        is_job=True,
        job_type="central_government",
        organization="Central Armed Police Forces",
        post_name="Assistant Commandant",
        qualification=["Bachelor Degree"],
        important_conditions=["Minimum height required: 170 cm for male candidates"],
        age_max=32,
        experience_required=False,
    )

    decision = evaluator.evaluate(job)
    assert decision.status == "NOT_ELIGIBLE"
    assert "physical_standards" in decision.criteria
    assert decision.criteria["physical_standards"].status == "FAIL"
    assert "168.0 cm" in decision.criteria["physical_standards"].details


def test_pet_constraint_separated_from_legal_eligibility():
    """
    Candidate satisfies height (172cm >= 165cm) but refuses PET tests.
    Engine must mark status as ELIGIBLE (legal match) but flag Tier C constraint warning.
    """
    profile = build_base_profile(
        physical=PhysicalEligibility(
            height_cm=172.0,
            willing_physical_tests=False,  # Dislikes running tests
        )
    )
    evaluator = EligibilityEvaluator(profile)

    job = JobExtractionSchema(
        is_job=True,
        job_type="central_government",
        organization="CISF",
        post_name="Sub-Inspector Executive",
        qualification=["Bachelor Degree"],
        important_conditions=["Physical efficiency test (PET) 1600m run required. Minimum height 165 cm."],
        selection_process=["PET Physical Endurance", "Written Examination"],
        age_max=32,
        experience_required=False,
    )

    decision = evaluator.evaluate(job)
    # Tier A Hard Eligibility is preserved!
    assert decision.status == "ELIGIBLE"
    # Tier C Constraint warning is correctly generated
    assert any("physical" in w.lower() or "pet" in w.lower() for w in decision.constraints_warnings)


def test_tier_d_readiness_ews_renewal_warning():
    """Candidate is EWS but EWS certificate status is RENEWAL_REQUIRED."""
    profile = build_base_profile(
        age=AgeRequirement(maximum=32, category="EWS"),
        documents_readiness={
            "caste_ews_cert": DocumentReadinessRecord(
                document_key="caste_ews_cert",
                name="EWS Income & Asset Certificate",
                status="RENEWAL_REQUIRED",
                valid_up_to_date="2025-03-31",
                notes="Requires renewal for current financial year",
            )
        },
    )
    evaluator = EligibilityEvaluator(profile)

    job = JobExtractionSchema(
        is_job=True,
        job_type="central_government",
        organization="ISRO",
        post_name="Scientist/Engineer 'SC'",
        qualification=["B.Tech"],
        accepted_branches=["Computer Science"],
        age_max=32,
        experience_required=False,
    )

    decision = evaluator.evaluate(job)
    assert decision.status == "ELIGIBLE"
    assert decision.readiness_status == "WARNING"
    assert any("ews" in w.lower() or "renewal" in w.lower() for w in decision.readiness_warnings)


def test_profile_model_roundtrip_all_four_tiers():
    """Ensures complete 4-tier profile serializes to dict and validates back cleanly."""
    original = build_base_profile(
        experience_records=[
            ExperienceRecord(
                employer="National Informatics Centre",
                sector="government",
                designation="Scientific Officer",
                total_months=36,
                mode="full_time",
                contract_type="permanent",
                has_certificate=True,
            )
        ],
        licences=[
            LicenceRecord(category="LMV", validity_status="valid", expiry_date="2035-10-15")
        ],
    )

    dumped = original.model_dump()
    reconstituted = UserRequirementsProfile.model_validate(dumped)

    assert reconstituted.personal.full_name == "Candidate Test"
    assert len(reconstituted.education_records) == 3
    assert reconstituted.subjects_10_12.studied_maths_12th is True
    assert len(reconstituted.experience_records) == 1
    assert reconstituted.experience_records[0].employer == "National Informatics Centre"
    assert len(reconstituted.licences) == 1
    assert reconstituted.licences[0].category == "LMV"
    assert reconstituted.physical.height_cm == 172.0
    assert reconstituted.salary_preferences.min_gross_monthly_inr == 40000
    assert reconstituted.documents_readiness["degree_cert"].status == "AVAILABLE"
