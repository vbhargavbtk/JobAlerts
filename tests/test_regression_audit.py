"""
Comprehensive Regression Test Suite — Job Classification Audit & Resolution
Verifies exact deterministic classification across all previously UNCERTAIN jobs,
false negative recoveries, multi-post circulars, domain guards, and alias normalization.
"""
import pytest
from app.ai.schemas import JobExtractionSchema, PostItemSchema
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
# Default Test Profile (B.Tech Computer Science / General Graduate Candidate)
# ---------------------------------------------------------------------------
def make_test_profile(**kwargs) -> UserRequirementsProfile:
    defaults = dict(
        education=EducationRequirement(
            minimum_level="bachelors",
            accepted_degrees=["B.Tech", "B.E.", "B.Sc", "BCA", "Graduation"],
            branches=["Computer Science", "Information Technology", "CSE", "IT", "Electronics", "ECE"],
            minimum_percentage=60.0,
        ),
        experience=ExperienceRequirement(fresher_allowed=True, max_years_experience_required=0),
        age=AgeRequirement(
            maximum=27,
            category="General",
            category_age_relaxations={"OBC": 3, "SC": 5, "ST": 5, "PwD": 10, "EWS": 0, "Ex-Serviceman": 5},
        ),
        job_categories=["central_government", "state_government", "psu", "banking", "defense", "autonomous_body"],
        location=LocationRequirement(allowed=["All India"], exclude_locations=[]),
        excluded_types=["internship", "unpaid_volunteer", "ad_hoc_short_term"],
        notification_preferences=NotificationPreferences(alert_on_uncertain=True),
    )
    defaults.update(kwargs)
    return UserRequirementsProfile(**defaults)


# ---------------------------------------------------------------------------
# 1. AUDIT RESOLUTION: THE 15 PREVIOUSLY UNCERTAIN JOBS
# ---------------------------------------------------------------------------

class TestAuditUncertainJobsResolution:
    def test_job_1_upsc_ese_eligible_with_e_and_t_alias(self):
        """UPSC ESE: Engineering degree with E&T (Electronics & Telecom) -> ELIGIBLE."""
        profile = make_test_profile()
        job = JobExtractionSchema(
            is_job=True,
            job_type="central_government",
            organization="Union Public Service Commission",
            post_name="Assistant Executive Engineer (Civil, Mechanical, Electrical, E&T)",
            qualification=["Degree in Engineering (B.E. / B.Tech)"],
            accepted_branches=["Civil", "Mechanical", "Electrical", "E&T"],
            age_min=21,
            age_max=30,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "ELIGIBLE", f"Expected ELIGIBLE, got {decision.status}: {decision.summary}"
        assert decision.criteria["branch"].status == "PASS"

    def test_job_2_delhi_postal_circle_truly_missing_info_remains_uncertain(self):
        """Delhi Postal Circle: Zero extractable details -> UNCERTAIN (genuine review needed)."""
        profile = make_test_profile()
        job = JobExtractionSchema(
            is_job=True,
            job_type="central_government",
            organization="Delhi Postal Circle",
            post_name=None,
            qualification=[],
            accepted_branches=[],
            age_min=None,
            age_max=None,
            experience_required=None,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "UNCERTAIN"
        assert decision.criteria["qualification"].status == "UNKNOWN"

    def test_job_3_income_tax_ta_mts_open_degree_eligible(self):
        """Income Tax Dept TA & MTS: 'A Degree from a recognized University' -> ELIGIBLE."""
        profile = make_test_profile()
        job = JobExtractionSchema(
            is_job=True,
            job_type="central_government",
            organization="Income Tax Department, West Bengal & Sikkim Region",
            post_name="Tax Assistant (TA) & Multi-Tasking Staff (MTS)",
            qualification=[
                "A Degree from a recognized University or an equivalent qualification",
                "Matriculation (Class 10) pass or equivalent qualification from a recognized Board"
            ],
            accepted_branches=[],
            age_min=18,
            age_max=27,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "ELIGIBLE"
        assert decision.criteria["branch"].status == "PASS"

    def test_job_4_sbi_clerk_graduation_in_any_discipline_eligible(self):
        """SBI Clerk: 'Graduation in any discipline' -> ELIGIBLE."""
        profile = make_test_profile()
        job = JobExtractionSchema(
            is_job=True,
            job_type="banking",
            organization="State Bank of India",
            post_name="Junior Associate (Customer Support & Sales)",
            qualification=["Graduation in any discipline", "Integrated Dual Degree (IDD)"],
            accepted_branches=[],
            age_min=20,
            age_max=28,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "ELIGIBLE"
        assert decision.criteria["branch"].status == "PASS"

    def test_job_5_srinagar_court_degree_eligible(self):
        """District & Session Judge Srinagar: 'Degree', '10th Pass', '12th Pass' -> ELIGIBLE."""
        profile = make_test_profile()
        job = JobExtractionSchema(
            is_job=True,
            job_type="state_government",
            organization="District & Session Judge, Srinagar",
            post_name="Process Server, Orderly/Chowkidar",
            qualification=["10th Pass", "12th Pass", "Degree"],
            accepted_branches=[],
            age_min=18,
            age_max=40,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "ELIGIBLE"

    def test_job_6_income_tax_graduation_eligible(self):
        """Income Tax Dept: 'Graduation' -> ELIGIBLE."""
        profile = make_test_profile()
        job = JobExtractionSchema(
            is_job=True,
            job_type="central_government",
            organization="Principal Chief Commissioner of Income Tax",
            post_name="Tax Assistant (TA) & Multi-Tasking Staff (MTS)",
            qualification=["Graduation", "10th Pass"],
            accepted_branches=[],
            age_min=18,
            age_max=27,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "ELIGIBLE"

    def test_job_7_echs_delhi_multi_post_clerk_eligible(self):
        """ECHS Delhi Multi-Post: Contains Clerk (Graduate Pass) -> ELIGIBLE for Clerk."""
        profile = make_test_profile()
        job = JobExtractionSchema(
            is_job=True,
            job_type="defense",
            organization="Ex-Servicemen Contributory Health Scheme (ECHS), Delhi",
            post_name="Clerk, Medical Specialist, Medical Officer, Dental Assistant/Hygienist, Physiotherapist",
            qualification=[
                "Graduate Pass",
                "MD/ MS in concerned Specialty/ DNB",
                "MBBS",
                "Diploma in Dental Hygienist/Class-I DH/DORA Course",
                "Diploma/ Class-I Physiotherapy Course (Armed Forces)"
            ],
            accepted_branches=[],
            age_min=18,
            age_max=56,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "ELIGIBLE"

    def test_job_8_ibps_rrb_any_graduate_eligible(self):
        """IBPS RRB: 'Any Graduate' for Office Assistant -> ELIGIBLE."""
        profile = make_test_profile()
        job = JobExtractionSchema(
            is_job=True,
            job_type="banking",
            organization="Institute of Banking Personnel Selection (IBPS)",
            post_name="Office Assistants (Multipurpose) and Officers Scale-I, II, and III",
            qualification=["Any Graduate", "Degree in Relevant Field", "CA"],
            accepted_branches=[],
            age_min=18,
            age_max=40,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "ELIGIBLE"

    def test_job_9_rrb_paramedical_not_eligible(self):
        """RRB Paramedical: Requires paramedical qualifications -> NOT_ELIGIBLE."""
        profile = make_test_profile()
        job = JobExtractionSchema(
            is_job=True,
            job_type="central_government",
            organization="Railway Recruitment Boards (RRBs)",
            post_name="Various Posts of Paramedical Categories",
            qualification=["Paramedical qualification as per CEN 05/2026", "Diploma in Medical Lab Technology"],
            accepted_branches=[],
            age_min=18,
            age_max=35,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "NOT_ELIGIBLE"
        assert decision.criteria["qualification"].status == "FAIL"

    def test_job_10_phhc_clerk_graduation_eligible(self):
        """Punjab and Haryana High Court Clerk: 'Graduation' -> ELIGIBLE."""
        profile = make_test_profile()
        job = JobExtractionSchema(
            is_job=True,
            job_type="state_government",
            organization="Punjab and Haryana High Court (PHHC)",
            post_name="Clerk",
            qualification=["Graduation"],
            accepted_branches=[],
            age_min=18,
            age_max=42,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "ELIGIBLE"

    def test_job_11_uksssc_steno_intermediate_graduation_eligible(self):
        """UKSSSC PA / Steno: 'Intermediate', 'Graduation' -> ELIGIBLE."""
        profile = make_test_profile()
        job = JobExtractionSchema(
            is_job=True,
            job_type="state_government",
            organization="Uttarakhand Subordinate Service Selection Commission (UKSSSC)",
            post_name="Personal Assistant, Stenographer, Stenographer Grade-III, Stenographer Grade-2",
            qualification=["Intermediate", "Graduation"],
            accepted_branches=[],
            age_min=18,
            age_max=42,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "ELIGIBLE"

    def test_job_12_pgimer_nursing_officer_medical_guard_not_eligible(self):
        """PGIMER Nursing Officer: 'B.Sc. Nursing' does NOT match general B.Sc -> NOT_ELIGIBLE."""
        profile = make_test_profile()
        job = JobExtractionSchema(
            is_job=True,
            job_type="autonomous_body",
            organization="Postgraduate Institute of Medical Education & Research (PGIMER), Chandigarh",
            post_name="Nursing Officer (NO)",
            qualification=["B.Sc. (Hons) Nursing", "B.Sc. Nursing", "Post Basic B.Sc. Nursing", "GNM Diploma"],
            accepted_branches=[],
            age_min=18,
            age_max=35,
            experience_required=True,
            experience_years_min=1,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "NOT_ELIGIBLE"
        assert decision.criteria["qualification"].status == "FAIL"

    def test_job_13_rrb_section_controller_any_graduate_eligible(self):
        """RRB Section Controller: 'Graduation', 'Any Graduate' -> ELIGIBLE."""
        profile = make_test_profile()
        job = JobExtractionSchema(
            is_job=True,
            job_type="central_government",
            organization="Railway Recruitment Boards (RRBs)",
            post_name="Section Controller",
            qualification=["Graduation", "Any Graduate"],
            accepted_branches=[],
            age_min=20,
            age_max=33,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "ELIGIBLE"

    def test_job_14_upessc_assistant_professor_education_level_not_eligible(self):
        """UPESSC Assistant Professor: Requires Master's/PhD; user has Bachelor's -> NOT_ELIGIBLE."""
        profile = make_test_profile(education=EducationRequirement(minimum_level="bachelors"))
        job = JobExtractionSchema(
            is_job=True,
            job_type="state_government",
            organization="UPESSC",
            post_name="Assistant Professor",
            qualification=["Master's Degree with 55%", "UGC NET / Ph.D"],
            accepted_branches=[],
            age_min=21,
            age_max=40,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "NOT_ELIGIBLE"
        assert decision.criteria["education_level"].status == "FAIL"

    def test_job_15_delhi_police_admit_card_detected_as_non_job(self):
        """Delhi Police Constable Admit Card: Non-job pre-filter sets status to NOT_ELIGIBLE / DISCARD."""
        profile = make_test_profile()
        job = JobExtractionSchema(
            is_job=True,
            job_type="defense",
            organization="Delhi Police",
            post_name="Constable (Executive) Physical Admit Card OUT",
            qualification=[],
            accepted_branches=[],
            age_min=None,
            age_max=None,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "NOT_ELIGIBLE"
        assert decision.action_recommended == "DISCARD"
        assert decision.taxonomy_tag == "non_job_announcement"


# ---------------------------------------------------------------------------
# 2. FALSE NEGATIVE RECOVERIES (Previously NOT_ELIGIBLE jobs)
# ---------------------------------------------------------------------------

class TestFalseNegativeRecoveries:
    def test_isro_assistant_graduate_synonym_match(self):
        """ISRO Assistant requires 'Graduate' -> user profile accepts 'Graduation' -> ELIGIBLE."""
        profile = make_test_profile(
            education=EducationRequirement(
                minimum_level="bachelors",
                accepted_degrees=["B.Tech", "Graduation"],
                branches=["Computer Science", "CSE"],
            )
        )
        job = JobExtractionSchema(
            is_job=True,
            job_type="central_government",
            organization="Indian Space Research Organization (ISRO)",
            post_name="Assistant, Upper Division Clerk (UDC), Junior Personal Assistant (JPA)",
            qualification=["Graduate"],
            accepted_branches=[],
            age_min=18,
            age_max=28,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "ELIGIBLE", f"Expected ELIGIBLE, got {decision.status}: {decision.summary}"
        assert decision.criteria["qualification"].status == "PASS"

    def test_balmer_lawrie_full_time_engineering_degree_match(self):
        """Balmer Lawrie requires 'Full-time engineering degree' -> matches B.Tech -> ELIGIBLE."""
        profile = make_test_profile(
            education=EducationRequirement(
                minimum_level="bachelors",
                accepted_degrees=["B.Tech", "Graduation"],
                branches=["Computer Science", "Information Technology"],
            ),
            age=AgeRequirement(maximum=27)
        )
        job = JobExtractionSchema(
            is_job=True,
            job_type="psu",
            organization="Balmer Lawrie & Co. Ltd.",
            post_name="Junior Officer (IT)",
            qualification=["Full-time engineering degree"],
            accepted_branches=["Information Technology", "Computer Science"],
            age_min=18,
            age_max=32,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "ELIGIBLE"
        assert decision.criteria["qualification"].status == "PASS"
        assert decision.criteria["branch"].status == "PASS"


# ---------------------------------------------------------------------------
# 3. STRUCTURED MULTI-POST NOTIFICATIONS
# ---------------------------------------------------------------------------

class TestMultiPostNotifications:
    def test_structured_posts_evaluation(self):
        """Notification with 2 posts: Post 1 (Civil -> Fail), Post 2 (CSE -> Pass) -> Overall ELIGIBLE."""
        profile = make_test_profile()
        job = JobExtractionSchema(
            is_job=True,
            organization="Central Public Works Department",
            post_name="Recruitment of Engineers 2026",
            posts=[
                PostItemSchema(
                    post_name="Junior Engineer (Civil)",
                    qualification=["B.Tech"],
                    accepted_branches=["Civil Engineering"],
                    age_max=30,
                    experience_required=False,
                ),
                PostItemSchema(
                    post_name="Junior Engineer (IT/Computer)",
                    qualification=["B.Tech"],
                    accepted_branches=["Computer Science & Engineering"],
                    age_max=30,
                    experience_required=False,
                )
            ]
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.status == "ELIGIBLE"
        assert "Junior Engineer (IT/Computer)" in decision.posts
        assert decision.posts["Junior Engineer (IT/Computer)"].status == "ELIGIBLE"
        assert decision.posts["Junior Engineer (Civil)"].status == "NOT_ELIGIBLE"


# ---------------------------------------------------------------------------
# 4. BRANCH & ALIAS NORMALIZATION TESTS
# ---------------------------------------------------------------------------

class TestBranchNormalization:
    @pytest.mark.parametrize("branch_term", [
        "Computer Science",
        "CSE",
        "Computer Science & Engineering",
        "Computer Engineering",
        "CS",
        "Information Science",
    ])
    def test_cse_aliases_match_user_cse(self, branch_term):
        profile = make_test_profile(education=EducationRequirement(branches=["CSE"]))
        job = JobExtractionSchema(
            is_job=True,
            qualification=["B.Tech"],
            accepted_branches=[branch_term],
            age_max=30,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["branch"].status == "PASS"

    @pytest.mark.parametrize("branch_term", [
        "Electronics & Communication",
        "ECE",
        "Electronics & Telecommunication",
        "E&T",
        "ETC",
        "Electronics and Telecom",
    ])
    def test_ece_aliases_match_user_ece(self, branch_term):
        profile = make_test_profile(education=EducationRequirement(branches=["ECE", "Electronics"]))
        job = JobExtractionSchema(
            is_job=True,
            qualification=["B.Tech"],
            accepted_branches=[branch_term],
            age_max=30,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["branch"].status == "PASS"

    def test_ai_ml_data_science_branch_match(self):
        profile = make_test_profile(education=EducationRequirement(branches=["Computer Science", "Artificial Intelligence"]))
        job = JobExtractionSchema(
            is_job=True,
            qualification=["B.Tech"],
            accepted_branches=["AI & ML", "Data Science"],
            age_max=30,
            experience_required=False,
        )
        decision = EligibilityEvaluator(profile).evaluate(job)
        assert decision.criteria["branch"].status == "PASS"
