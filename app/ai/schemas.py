"""
Strict AI Extraction Schemas
Enforces zero-hallucination policy and required evidence backing.
Includes pre-validators to normalize AI response formatting variations (None -> [], aliases).
"""
from typing import List, Optional, Any, Union, Dict
from pydantic import BaseModel, Field, field_validator, model_validator


class FieldEvidence(BaseModel):
    field_name: str = Field(..., description="Name of the extracted field")
    source_url: Optional[str] = Field(None, description="URL where evidence was observed")
    page_number: Optional[int] = Field(None, description="PDF page number if available")
    supporting_excerpt: str = Field(..., description="Short verbatim excerpt from source")
    extraction_method: str = Field(default="direct_text", description="e.g., pdf_text, html_text, ocr")

    @model_validator(mode="before")
    @classmethod
    def normalize_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Normalize field_name
            if "field_name" not in data:
                data["field_name"] = data.get("field") or data.get("name") or "general"
            # Normalize supporting_excerpt
            if "supporting_excerpt" not in data:
                data["supporting_excerpt"] = (
                    data.get("excerpt") or data.get("sentence") or data.get("quote") or data.get("text") or str(data)
                )
        return data


class JobExtractionSchema(BaseModel):
    is_job: bool = Field(
        ...,
        description="True if content announces an active job/recruitment vacancy. False if exam result, answer key, admission, syllabus, or general news."
    )
    job_type: Optional[str] = Field(
        None,
        description="Type: central_government, state_government, psu, banking, defense, autonomous_body, private, apprenticeship, or internship"
    )
    organization: Optional[str] = Field(
        None,
        description="Exact issuing government organization or department name"
    )
    post_name: Optional[str] = Field(
        None,
        description="Title of the job position/post"
    )
    notification_number: Optional[str] = Field(
        None,
        description="Official advertisement / notification / circular number (null if not explicitly stated)"
    )
    vacancies: Optional[int] = Field(
        None,
        description="Total number of vacancies declared (null if unstated)"
    )
    qualification: List[str] = Field(
        default_factory=list,
        description="List of mandatory educational qualifications declared (e.g., B.E., B.Tech, Any Degree)"
    )
    accepted_branches: List[str] = Field(
        default_factory=list,
        description="List of engineering disciplines or subjects explicitly accepted"
    )
    minimum_percentage: Optional[float] = Field(
        None,
        description="Minimum cutoff percentage/CGPA in qualification"
    )
    age_min: Optional[int] = Field(
        None,
        description="Minimum age requirement in years (null if unstated)"
    )
    age_max: Optional[int] = Field(
        None,
        description="Maximum general age limit in years (null if unstated)"
    )
    age_relaxations: List[str] = Field(
        default_factory=list,
        description="Declared age relaxation rules for reserved categories"
    )
    experience_required: Optional[bool] = Field(
        None,
        description="True if prior experience is required, False if freshers eligible, null if unstated"
    )
    experience_years_min: Optional[int] = Field(
        None,
        description="Minimum years of experience required"
    )
    experience_details: Optional[str] = Field(
        None,
        description="Specific experience field or domain required"
    )
    salary: Optional[str] = Field(
        None,
        description="Pay scale, CTC, or stipend explicitly mentioned"
    )
    pay_level: Optional[str] = Field(
        None,
        description="7th CPC Pay Matrix Level if stated (e.g. Level 7, Level 10)"
    )
    location: List[str] = Field(
        default_factory=list,
        description="Job posting locations or states"
    )
    application_start: Optional[str] = Field(
        None,
        description="Application start date in YYYY-MM-DD format (null if unstated)"
    )
    application_deadline: Optional[str] = Field(
        None,
        description="Last date to apply in YYYY-MM-DD format (null if unstated)"
    )
    application_fee: List[str] = Field(
        default_factory=list,
        description="Fee details by category"
    )
    selection_process: List[str] = Field(
        default_factory=list,
        description="Declared stages (e.g. Written Exam, Interview, GATE Score)"
    )
    official_notification_url: Optional[str] = Field(
        None,
        description="Direct link to official notification PDF or official circular"
    )
    official_apply_url: Optional[str] = Field(
        None,
        description="Direct link to official portal application form"
    )
    source_urls: List[str] = Field(
        default_factory=list,
        description="All URLs referenced"
    )
    important_conditions: List[str] = Field(
        default_factory=list,
        description="Mandatory conditions, bond requirements, gate qualifications, etc."
    )
    confidence: float = Field(
        default=0.9,
        description="Confidence score between 0.0 and 1.0"
    )
    evidence: List[FieldEvidence] = Field(
        default_factory=list,
        description="Mandatory evidence citations for each extracted field"
    )

    @field_validator(
        "qualification", "accepted_branches", "age_relaxations", "location",
        "application_fee", "selection_process", "source_urls", "important_conditions",
        "evidence",
        mode="before"
    )
    @classmethod
    def coerce_list_fields(cls, v: Any) -> List[Any]:
        if v is None:
            return []
        if isinstance(v, str):
            return [v] if v.strip() else []
        if isinstance(v, list):
            return v
        return [v]
