"""
Deterministic Eligibility Evaluation Engine
Strictly evaluates extracted job parameters against the User Requirements Profile.
Deterministic Hard Rules:
- If ANY mandatory requirement = FAIL -> NOT_ELIGIBLE
- Else if ANY mandatory requirement = UNKNOWN -> UNCERTAIN
- Else (all mandatory PASS) -> ELIGIBLE
CRITICAL SPECIFICATION RULE: NEVER convert UNKNOWN into PASS.
"""
import logging
from typing import Dict, Any, List
from app.ai.schemas import JobExtractionSchema
from app.eligibility.models import (
    UserRequirementsProfile,
    EligibilityDecision,
    EligibilityCriterionResult
)

logger = logging.getLogger(__name__)


class EligibilityEvaluator:
    def __init__(self, user_profile: UserRequirementsProfile):
        self.profile = user_profile

    def update_profile(self, new_profile: UserRequirementsProfile) -> None:
        self.profile = new_profile

    def evaluate(self, job: JobExtractionSchema) -> EligibilityDecision:
        """
        Executes strict deterministic eligibility check.
        """
        # If model extracted that this is not an active job notification
        if not job.is_job:
            return EligibilityDecision(
                status="NOT_ELIGIBLE",
                criteria={
                    "is_job": EligibilityCriterionResult(
                        status="FAIL",
                        details="Content classified as non-job (e.g., result, answer key, or syllabus)",
                        extracted_value=job.is_job
                    )
                },
                summary="Content does not announce an active job recruitment.",
                action_recommended="DISCARD"
            )

        criteria_results: Dict[str, EligibilityCriterionResult] = {}

        # 1. Job Type / Category Exclusion Check
        criteria_results["job_type"] = self._evaluate_job_type(job)

        # 2. Age Criteria Check
        criteria_results["age"] = self._evaluate_age(job)

        # 3. Experience Criteria Check
        criteria_results["experience"] = self._evaluate_experience(job)

        # 4. Educational Degree & Qualifications Check
        criteria_results["qualification"] = self._evaluate_qualification(job)

        # 5. Accepted Branches / Engineering Disciplines Check
        criteria_results["branch"] = self._evaluate_branch(job)

        # Compute Final Strict Decision
        # Decision Logic:
        # IF any mandatory requirement = FAIL: NOT_ELIGIBLE
        # ELSE IF any mandatory requirement = UNKNOWN: UNCERTAIN
        # ELSE: ELIGIBLE

        has_fail = any(res.status == "FAIL" for res in criteria_results.values())
        has_unknown = any(res.status == "UNKNOWN" for res in criteria_results.values())

        if has_fail:
            status = "NOT_ELIGIBLE"
            action = "DISCARD"
            summary = "One or more mandatory requirements failed eligibility."
        elif has_unknown:
            status = "UNCERTAIN"
            action = "UNCERTAIN_ALERT" if self.profile.notification_preferences.alert_on_uncertain else "DISCARD"
            summary = "Key parameters are ambiguous or missing in notification; manual review required."
        else:
            status = "ELIGIBLE"
            action = "ALERT"
            summary = "All mandatory eligibility criteria passed successfully."

        return EligibilityDecision(
            status=status,
            criteria=criteria_results,
            summary=summary,
            action_recommended=action
        )

    def _evaluate_job_type(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        job_type_str = job.job_type or "government"
        job_type_lower = job_type_str.lower()
        for excluded in self.profile.excluded_types:
            if excluded.lower() in job_type_lower:
                return EligibilityCriterionResult(
                    status="FAIL",
                    details=f"Job type '{job.job_type}' matches excluded type '{excluded}'",
                    extracted_value=job.job_type,
                    required_value=f"Not in {self.profile.excluded_types}"
                )

        return EligibilityCriterionResult(
            status="PASS",
            details=f"Job type '{job_type_str}' is acceptable",
            extracted_value=job_type_str,
            required_value=self.profile.job_categories
        )

    def _evaluate_age(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        if job.age_max is None:
            return EligibilityCriterionResult(
                status="UNKNOWN",
                details="Maximum age limit is not explicitly declared in the notification",
                extracted_value=None,
                required_value=self.profile.age.maximum
            )

        user_cat = self.profile.age.category
        relaxation = self.profile.age.category_age_relaxations.get(user_cat, 0)
        effective_user_max_age = self.profile.age.maximum

        # If job age max is less than user base age, check if relaxations allow it
        if effective_user_max_age <= (job.age_max + relaxation):
            return EligibilityCriterionResult(
                status="PASS",
                details=f"Job max age {job.age_max} (with category relaxation +{relaxation}) accommodates age {effective_user_max_age}",
                extracted_value=job.age_max,
                required_value=effective_user_max_age
            )
        else:
            return EligibilityCriterionResult(
                status="FAIL",
                details=f"Job max age ({job.age_max}) is lower than your age ({effective_user_max_age}) even with relaxations",
                extracted_value=job.age_max,
                required_value=effective_user_max_age
            )

    def _evaluate_experience(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        if job.experience_required is None:
            return EligibilityCriterionResult(
                status="UNKNOWN",
                details="Experience requirement wording is ambiguous or unstated in source text",
                extracted_value=None,
                required_value=f"Fresher allowed={self.profile.experience.fresher_allowed}"
            )

        if not job.experience_required:
            return EligibilityCriterionResult(
                status="PASS",
                details="Freshers explicitly allowed / no prior experience required",
                extracted_value="0 years",
                required_value="Fresher"
            )

        # Experience is required
        min_years = job.experience_years_min or 1
        if min_years <= self.profile.experience.max_years_experience_required:
            return EligibilityCriterionResult(
                status="PASS",
                details=f"Required experience ({min_years} yrs) is within your configured profile ({self.profile.experience.max_years_experience_required} yrs)",
                extracted_value=f"{min_years} years",
                required_value=f"<= {self.profile.experience.max_years_experience_required} years"
            )
        else:
            return EligibilityCriterionResult(
                status="FAIL",
                details=f"Required experience ({min_years} yrs) exceeds your profile maximum ({self.profile.experience.max_years_experience_required} yrs)",
                extracted_value=f"{min_years} years",
                required_value=f"<= {self.profile.experience.max_years_experience_required} years"
            )

    def _evaluate_qualification(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        if not job.qualification:
            return EligibilityCriterionResult(
                status="UNKNOWN",
                details="Mandatory degree qualifications are not stated in notification text",
                extracted_value=None,
                required_value=self.profile.education.accepted_degrees
            )

        job_quals = [q.lower() for q in job.qualification]
        accepted = [d.lower() for d in self.profile.education.accepted_degrees]

        # Check for any match
        matched = []
        for q in job_quals:
            for acc in accepted:
                if acc in q or q in acc or "any graduate" in q or "degree" in q:
                    matched.append(q)

        if matched:
            return EligibilityCriterionResult(
                status="PASS",
                details=f"Qualification '{matched[0]}' matches accepted profile degrees",
                extracted_value=job.qualification,
                required_value=self.profile.education.accepted_degrees
            )

        return EligibilityCriterionResult(
            status="FAIL",
            details=f"Extracted qualifications {job.qualification} do not match accepted degrees {self.profile.education.accepted_degrees}",
            extracted_value=job.qualification,
            required_value=self.profile.education.accepted_degrees
        )

    def _evaluate_branch(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        if not job.accepted_branches:
            # If branches are not mentioned, it could be general or open to all branches
            return EligibilityCriterionResult(
                status="UNKNOWN",
                details="Specific degree branches not specified in excerpt; verify official notification",
                extracted_value=None,
                required_value=self.profile.education.branches
            )

        job_branches = [b.lower() for b in job.accepted_branches]
        user_branches = [b.lower() for b in self.profile.education.branches]

        matched = []
        for jb in job_branches:
            if "any" in jb or "all" in jb:
                matched.append("All Branches")
            for ub in user_branches:
                if ub in jb or jb in ub:
                    matched.append(jb)

        if matched:
            return EligibilityCriterionResult(
                status="PASS",
                details=f"Branch '{matched[0]}' matches eligible branches",
                extracted_value=job.accepted_branches,
                required_value=self.profile.education.branches
            )

        return EligibilityCriterionResult(
            status="FAIL",
            details=f"Required branches {job.accepted_branches} do not match your branches {self.profile.education.branches}",
            extracted_value=job.accepted_branches,
            required_value=self.profile.education.branches
        )
