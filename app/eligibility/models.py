"""
User Requirements & Eligibility Domain Models
Defines Pydantic schemas for the editable user profile and evaluation decisions.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class EducationRequirement(BaseModel):
    minimum_level: str = Field(
        default="bachelors",
        description="Minimum education: any, 10th, 12th, diploma, bachelors, masters, doctorate"
    )
    accepted_degrees: List[str] = Field(
        default_factory=lambda: ["B.E.", "B.Tech", "B.Sc", "BCA", "MCA", "M.Tech", "Graduation"],
        description="Accepted degree certificates"
    )
    branches: List[str] = Field(
        default_factory=lambda: ["Computer Science", "Information Technology", "CSE", "IT", "Electronics", "ECE", "Any Branch"],
        description="Accepted branches / specializations"
    )
    minimum_percentage: Optional[float] = Field(
        default=60.0,
        description="Minimum aggregate marks or percentage required (if specified in notification)"
    )


class ExperienceRequirement(BaseModel):
    fresher_allowed: bool = Field(
        default=True,
        description="If True, matches jobs accepting freshers or requiring 0 experience"
    )
    max_years_experience_required: int = Field(
        default=2,
        description="Maximum years of experience the user currently possesses"
    )


class AgeRequirement(BaseModel):
    maximum: int = Field(
        default=30,
        description="Base upper age limit"
    )
    category: str = Field(
        default="General",
        description="Reservation category: General, OBC, SC, ST, EWS, PwD"
    )
    category_age_relaxations: Dict[str, int] = Field(
        default_factory=lambda: {
            "OBC": 3,
            "SC": 5,
            "ST": 5,
            "PwD": 10,
            "Ex-Serviceman": 5,
            "EWS": 0
        },
        description="Age relaxation in years by category"
    )


class LocationRequirement(BaseModel):
    allowed: List[str] = Field(
        default_factory=lambda: ["All India", "India"],
        description="Allowed job locations or posting states"
    )
    exclude_locations: List[str] = Field(
        default_factory=list,
        description="Locations explicitly excluded"
    )


class NotificationPreferences(BaseModel):
    alert_on_uncertain: bool = Field(
        default=True,
        description="Whether to send 🟡 UNCERTAIN alerts for manual review"
    )
    min_vacancies: int = Field(default=1, description="Minimum number of vacancies to alert")
    min_salary_inr_month: int = Field(default=0, description="Minimum monthly salary filter")


# ==============================================================================
# 4-TIER EXTENDED PERSONAL PROFILE, PREFERENCE & READINESS SUB-MODELS
# ==============================================================================

class PersonalDetails(BaseModel):
    full_name: Optional[str] = Field(default=None, description="Candidate full name")
    gender: Optional[str] = Field(default="Male", description="Male, Female, or Any")
    nationality: str = Field(default="Indian", description="Default: Indian")
    state_of_domicile: Optional[str] = Field(default=None, description="State of domicile")
    current_state: Optional[str] = Field(default=None, description="Current residing state")
    current_city: Optional[str] = Field(default=None, description="Current city")
    permanent_state: Optional[str] = Field(default=None, description="Permanent residence state")
    local_area_district: Optional[str] = Field(default=None, description="Local district or quota zone")
    willing_to_relocate: bool = Field(default=True, description="Willing to relocate for job")
    willing_to_relocate_all_india: bool = Field(default=True, description="Willing to work anywhere in India")
    preferred_relocation_states: List[str] = Field(default_factory=list, description="Specific preferred states if relocation restricted")


class EducationRecord(BaseModel):
    level: str = Field(default="bachelors", description="10th, 12th, diploma, iti, bachelors, masters, doctorate")
    degree_name: str = Field(default="B.Tech", description="e.g., B.Tech, B.E., B.Sc, BCA, MCA")
    branch: str = Field(default="Computer Science and Engineering", description="e.g. Computer Science, Mechanical")
    specialization: Optional[str] = Field(default=None, description="e.g. Artificial Intelligence, VLSI")
    institution_board: Optional[str] = Field(default=None, description="University, College, or School Board")
    passing_year: Optional[int] = Field(default=None, description="Passing Year")
    percentage: Optional[float] = Field(default=None, description="Percentage")
    cgpa: Optional[float] = Field(default=None, description="CGPA")
    conversion_formula: Optional[str] = Field(default=None, description="CGPA to % multiplier")
    mode: str = Field(default="full_time", description="full_time, part_time, distance")
    completion_status: str = Field(default="completed", description="completed, pursuing, final_year")


class SubjectsProfile10_12(BaseModel):
    twelfth_stream: str = Field(default="Science", description="Science-PCM, Science-PCB, Science-PCMB, Commerce, Arts, Vocational")
    studied_maths_12th: bool = Field(default=True, description="Studied Mathematics in 10+2")
    studied_physics_12th: bool = Field(default=True, description="Studied Physics in 10+2")
    studied_chemistry_12th: bool = Field(default=True, description="Studied Chemistry in 10+2")
    studied_biology_12th: bool = Field(default=False, description="Studied Biology in 10+2")
    studied_computer_science_12th: bool = Field(default=True, description="Studied Computer Science in 10+2")
    studied_english: bool = Field(default=True, description="Studied English in 10th/12th")
    other_subjects: List[str] = Field(default_factory=list, description="Other specialized subjects")


class CompleteEducationHistory(BaseModel):
    """Legacy helper for backward compatibility with existing tests."""
    tenth_board: Optional[str] = Field(default=None, description="10th Board name")
    tenth_year: Optional[int] = Field(default=None, description="10th Passing Year")
    tenth_percentage: Optional[float] = Field(default=None, description="10th Percentage")
    tenth_cgpa: Optional[float] = Field(default=None, description="10th CGPA")
    twelfth_board: Optional[str] = Field(default=None, description="12th Board name")
    twelfth_year: Optional[int] = Field(default=None, description="12th Passing Year")
    twelfth_percentage: Optional[float] = Field(default=None, description="12th Percentage")
    twelfth_cgpa: Optional[float] = Field(default=None, description="12th CGPA")
    twelfth_stream: Optional[str] = Field(default="Science", description="Science, Commerce, Arts, or Other")
    twelfth_subjects: List[str] = Field(default_factory=lambda: ["Mathematics", "Physics", "Chemistry"], description="Key subjects studied")
    graduation_degree: Optional[str] = Field(default="B.Tech", description="e.g., B.Tech, B.E., B.Sc, BCA")
    graduation_branch: Optional[str] = Field(default="Computer Science and Engineering", description="e.g., Computer Science, IT")
    graduation_university: Optional[str] = Field(default=None, description="University or Institute name")
    graduation_year: Optional[int] = Field(default=None, description="Graduation Passing Year")
    graduation_percentage: Optional[float] = Field(default=None, description="Aggregate Degree Percentage")
    graduation_cgpa: Optional[float] = Field(default=None, description="Aggregate Degree CGPA")
    has_post_graduation: bool = Field(default=False, description="Whether candidate holds a Master's degree")
    post_graduation_details: Optional[str] = Field(default=None, description="Degree, branch, university of PG")
    has_driving_licence: bool = Field(default=False, description="Holds valid driving licence")
    driving_licence_types: List[str] = Field(default_factory=list, description="e.g., LMV, HMV, Two-Wheeler")
    certifications: List[str] = Field(default_factory=list, description="Computer or technical certifications")


class ExperienceRecord(BaseModel):
    employer: str = Field(..., description="Company or Organization Name")
    sector: str = Field(default="private", description="government, psu, private, banking, autonomous")
    designation: str = Field(default="", description="Job Title / Role")
    start_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    end_date: Optional[str] = Field(default=None, description="YYYY-MM-DD or null if current")
    total_months: int = Field(default=0, description="Duration in months")
    is_current: bool = Field(default=False, description="Currently employed here")
    is_relevant: bool = Field(default=True, description="Directly relevant to primary discipline")
    mode: str = Field(default="full_time", description="full_time, part_time")
    contract_type: str = Field(default="permanent", description="permanent, contract, apprentice, internship")
    has_certificate: bool = Field(default=True, description="Experience certificate / service letter available")


class LicenceRecord(BaseModel):
    category: str = Field(..., description="LMV, HMV, Two_Wheeler, Commercial, Nursing_Council, Bar_Council, Medical_Council")
    validity_status: str = Field(default="valid", description="valid, expired, learning, applied")
    expiry_date: Optional[str] = Field(default=None, description="YYYY-MM-DD if applicable")


class PhysicalEligibility(BaseModel):
    height_cm: Optional[float] = Field(default=None, description="Candidate height in cm")
    chest_normal_cm: Optional[float] = Field(default=None, description="Unexpanded chest in cm (male)")
    chest_expanded_cm: Optional[float] = Field(default=None, description="Expanded chest in cm (male)")
    weight_kg: Optional[float] = Field(default=None, description="Weight in kg")
    willing_physical_tests: bool = Field(default=False, description="Willing to participate in running/jumping PET")
    willing_running: bool = Field(default=False, description="Willing to take 1600m / sprint test")
    willing_jump: bool = Field(default=False, description="Willing to take high jump / long jump test")
    willing_police_standards: bool = Field(default=False, description="Willing to meet police/CAPF physical standards")


class MedicalStandards(BaseModel):
    willing_medical_exam: bool = Field(default=True, description="Willing to undergo official medical exam")
    has_color_blindness: bool = Field(default=False, description="Candidate has color blindness")
    visual_standards_acceptable: bool = Field(default=True, description="Meets standard eyesight criteria")
    eye_sight_specs: Optional[str] = Field(default=None, description="e.g., 6/6, 6/9 with or without glasses")


class DocumentReadinessRecord(BaseModel):
    document_key: str = Field(..., description="e.g., ews_certificate, caste_certificate, degree_certificate, lmv_licence, noc")
    name: str = Field(..., description="Human readable document title")
    status: str = Field(default="AVAILABLE", description="AVAILABLE, NOT_AVAILABLE, EXPIRED, RENEWAL_REQUIRED, UNKNOWN, NOT_APPLICABLE")
    valid_up_to_date: Optional[str] = Field(default=None, description="Expiry / financial year end")
    notes: Optional[str] = Field(default=None, description="User note or issue")


class SalaryPreferences(BaseModel):
    min_gross_monthly_inr: Optional[int] = Field(default=None, description="Minimum acceptable gross salary per month")
    min_basic_pay_inr: Optional[int] = Field(default=None, description="Minimum basic pay")
    preferred_pay_level: Optional[str] = Field(default=None, description="e.g., Level 7, Level 10")
    is_hard_filter: bool = Field(default=False, description="If True, rejects jobs below salary threshold")


class RolePreferences(BaseModel):
    preferred_roles: List[str] = Field(
        default_factory=lambda: ["Technical", "Software / IT", "Engineering", "Data / Analytics", "Administration", "Clerical"],
        description="Preferred job role categories"
    )
    avoid_roles: List[str] = Field(
        default_factory=lambda: ["Police / Uniformed", "Defence Combat", "Sales / Field Agent", "Manual Labor", "Nursing"],
        description="Roles to strictly avoid or deprioritize"
    )
    work_nature: str = Field(default="desk_only", description="desk_only, mixed, or field_acceptable")
    job_security_preference: str = Field(default="permanent_only", description="permanent_only, permanent_preferred, or any")
    shift_preference: str = Field(default="day_shifts_only", description="day_shifts_only, rotational_acceptable, any")


class ConstraintsPreferences(BaseModel):
    willing_physical_tests: bool = Field(default=False, description="Willing to participate in physical efficiency tests")
    max_application_fee: Optional[int] = Field(default=500, description="Maximum fee willing to pay (None = any)")
    exclude_high_fee_jobs: bool = Field(default=False, description="If True, marks jobs exceeding fee limit as NOT_INTERESTED")
    willing_to_travel_for_exams: bool = Field(default=True, description="Willing to travel for examinations")
    max_travel_distance_km: Optional[int] = Field(default=None, description="Maximum exam travel distance in km")
    service_bond_acceptable: bool = Field(default=True, description="Willing to sign mandatory service bond")
    max_bond_years: Optional[int] = Field(default=3, description="Maximum acceptable bond duration in years")
    transfer_tolerance: str = Field(default="state_or_district", description="no_transfer, state_or_district, or nationwide")
    min_salary_gross_monthly: Optional[int] = Field(default=None, description="Minimum acceptable monthly gross salary in INR")


class ClassificationPreferences(BaseModel):
    unknown_handling: str = Field(default="REVIEW", description="REVIEW, POTENTIALLY_ELIGIBLE, or NOT_ELIGIBLE")
    hide_not_interested: bool = Field(default=False, description="Whether to hide NOT_INTERESTED jobs from main feed")
    alert_on_maybe: bool = Field(default=True, description="Whether to send notifications for MAYBE jobs")


class UserRequirementsProfile(BaseModel):
    # Core legacy sections preserved for 100% backward compatibility
    education: EducationRequirement = Field(default_factory=EducationRequirement)
    experience: ExperienceRequirement = Field(default_factory=ExperienceRequirement)
    age: AgeRequirement = Field(default_factory=AgeRequirement)
    job_categories: List[str] = Field(
        default_factory=lambda: [
            "central_government",
            "state_government",
            "psu",
            "banking",
            "defense",
            "autonomous_body"
        ]
    )
    location: LocationRequirement = Field(default_factory=LocationRequirement)
    excluded_types: List[str] = Field(
        default_factory=lambda: ["internship", "unpaid_volunteer", "ad_hoc_short_term"]
    )
    notification_preferences: NotificationPreferences = Field(default_factory=NotificationPreferences)
    date_of_birth: Optional[str] = Field(
        default=None,
        description="User date of birth (YYYY-MM-DD). Used to derive age automatically."
    )
    max_application_fee: Optional[int] = Field(
        default=None,
        description="Maximum application fee user is willing to pay in INR. None means Any."
    )
    matching_mode: str = Field(
        default="balanced",
        description="Matching strictness: strict | balanced | broad"
    )

    # 4-Tier Extended Personal Profile, Preference & Readiness Sections
    personal: PersonalDetails = Field(default_factory=PersonalDetails)
    education_history: CompleteEducationHistory = Field(default_factory=CompleteEducationHistory)
    education_records: List[EducationRecord] = Field(
        default_factory=lambda: [
            EducationRecord(level="10th", degree_name="Secondary School Certificate", branch="All Subjects", percentage=85.0),
            EducationRecord(level="12th", degree_name="Senior Secondary Certificate", branch="Science (PCM)", percentage=75.0),
            EducationRecord(level="bachelors", degree_name="B.Tech", branch="Computer Science and Engineering", percentage=70.0),
        ],
        description="Chronological education qualifications"
    )
    subjects_10_12: SubjectsProfile10_12 = Field(default_factory=SubjectsProfile10_12)
    experience_records: List[ExperienceRecord] = Field(default_factory=list, description="Employment records")
    licences: List[LicenceRecord] = Field(default_factory=list, description="Possessed licences and registrations")
    physical: PhysicalEligibility = Field(default_factory=PhysicalEligibility)
    medical: MedicalStandards = Field(default_factory=MedicalStandards)
    role_preferences: RolePreferences = Field(default_factory=RolePreferences)
    constraints: ConstraintsPreferences = Field(default_factory=ConstraintsPreferences)
    salary_preferences: SalaryPreferences = Field(default_factory=SalaryPreferences)
    classification_preferences: ClassificationPreferences = Field(default_factory=ClassificationPreferences)
    documents_readiness: Dict[str, DocumentReadinessRecord] = Field(
        default_factory=lambda: {
            "degree_cert": DocumentReadinessRecord(document_key="degree_cert", name="Degree Certificate / Marksheets", status="AVAILABLE"),
            "tenth_cert": DocumentReadinessRecord(document_key="tenth_cert", name="10th Board Certificate (Proof of Date of Birth)", status="AVAILABLE"),
            "twelfth_cert": DocumentReadinessRecord(document_key="twelfth_cert", name="12th Board Certificate", status="AVAILABLE"),
            "caste_ews_cert": DocumentReadinessRecord(document_key="caste_ews_cert", name="Category / EWS / OBC Certificate", status="AVAILABLE"),
            "domicile_cert": DocumentReadinessRecord(document_key="domicile_cert", name="Domicile / Residence Certificate", status="AVAILABLE"),
            "driving_licence": DocumentReadinessRecord(document_key="driving_licence", name="Driving Licence (LMV)", status="NOT_APPLICABLE"),
            "experience_cert": DocumentReadinessRecord(document_key="experience_cert", name="Experience Certificate / Service Letter", status="NOT_APPLICABLE"),
            "noc": DocumentReadinessRecord(document_key="noc", name="No Objection Certificate (for Govt/PSU employees)", status="NOT_APPLICABLE")
        },
        description="Document readiness states for quick verification"
    )
    avoid_organizations: List[str] = Field(
        default_factory=list,
        description="Specific government organizations or departments to avoid"
    )
    preferred_organizations: List[str] = Field(
        default_factory=lambda: ["ISRO", "DRDO", "BARC", "UPSC", "SSC", "NIC", "RBI", "SBI", "IOCL", "ONGC", "NTPC", "BHEL"],
        description="Priority government organizations"
    )
    branch_mappings: Dict[str, str] = Field(
        default_factory=lambda: {
            "Computer Science": "ACCEPT",
            "Information Technology": "ACCEPT",
            "CSE": "ACCEPT",
            "IT": "ACCEPT",
            "Computer Engineering": "ACCEPT",
            "AI & ML": "ACCEPT",
            "Data Science": "ACCEPT",
            "Electronics": "ACCEPT",
            "ECE": "ACCEPT",
            "Electrical": "POSSIBLY_ACCEPT",
            "Mechanical": "DO_NOT_ACCEPT",
            "Civil": "DO_NOT_ACCEPT"
        },
        description="Strictness mapping per branch: ACCEPT | POSSIBLY_ACCEPT | DO_NOT_ACCEPT"
    )
    hard_exclusions: List[str] = Field(default_factory=list, description="Explicit blacklist phrases")
    target_jobs: List[str] = Field(default_factory=list, description="Priority exams or specific posts")


class EligibilityCriterionResult(BaseModel):
    status: str = Field(..., description="PASS, FAIL, or UNKNOWN")
    details: str = Field(..., description="Explanation of evaluation")
    extracted_value: Any = None
    required_value: Any = None


class PostEligibilityResult(BaseModel):
    post_name: str = Field(..., description="Title of the individual post evaluated")
    status: str = Field(..., description="PASS, FAIL, or UNKNOWN")
    details: str = Field(..., description="Summary of post eligibility")
    criteria: Dict[str, EligibilityCriterionResult] = Field(default_factory=dict)


class EligibilityDecision(BaseModel):
    status: str = Field(..., description="Tier A Hard Eligibility: ELIGIBLE, UNCERTAIN, or NOT_ELIGIBLE")
    preference_status: str = Field(
        default="WANT_TO_APPLY",
        description="Tier B Personal Preference: WANT_TO_APPLY, MAYBE, or NOT_INTERESTED"
    )
    readiness_status: str = Field(
        default="READY",
        description="Tier D Application Readiness: READY, WARNING, or MISSING_DOCUMENTS"
    )
    combined_status: str = Field(
        default="ELIGIBLE + WANT TO APPLY",
        description="Combined verdict: ELIGIBLE + WANT TO APPLY, ELIGIBLE + MAYBE, ELIGIBLE + NOT INTERESTED, NOT_ELIGIBLE, or UNCERTAIN"
    )
    criteria: Dict[str, EligibilityCriterionResult] = Field(default_factory=dict)
    posts: Dict[str, PostEligibilityResult] = Field(default_factory=dict, description="Post-wise breakdown for multi-post notifications")
    preference_breakdown: Dict[str, Any] = Field(default_factory=dict, description="Reasons for preference verdict")
    constraints_warnings: List[str] = Field(default_factory=list, description="Warnings about application constraints (fees, physical, bonds)")
    readiness_warnings: List[str] = Field(default_factory=list, description="Warnings about missing or expired application documents")
    summary: str = Field(..., description="Human-readable decision summary")
    action_recommended: str = Field(..., description="ALERT, UNCERTAIN_ALERT, or DISCARD")
    taxonomy_tag: Optional[str] = Field(default=None, description="Diagnostic classification category tag")

