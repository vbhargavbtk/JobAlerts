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
            "Ex-Serviceman": 5
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


class UserRequirementsProfile(BaseModel):
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


class EligibilityCriterionResult(BaseModel):
    status: str = Field(..., description="PASS, FAIL, or UNKNOWN")
    details: str = Field(..., description="Explanation of evaluation")
    extracted_value: Any = None
    required_value: Any = None


class EligibilityDecision(BaseModel):
    status: str = Field(..., description="ELIGIBLE, UNCERTAIN, or NOT_ELIGIBLE")
    criteria: Dict[str, EligibilityCriterionResult] = Field(default_factory=dict)
    summary: str = Field(..., description="Human-readable decision summary")
    action_recommended: str = Field(..., description="ALERT, UNCERTAIN_ALERT, or DISCARD")
