"""
Deterministic Eligibility Evaluation Engine
Strictly evaluates extracted job parameters against the User Requirements Profile.

Deterministic Hard Rules:
  - If ANY mandatory requirement = FAIL  -> NOT_ELIGIBLE
  - Else if ANY mandatory requirement = UNKNOWN -> UNCERTAIN
  - Else (all mandatory PASS) -> ELIGIBLE

CRITICAL SPECIFICATION RULE: NEVER convert UNKNOWN into PASS.
"""
import re
import logging
from typing import Dict
from app.ai.schemas import JobExtractionSchema
from app.eligibility.models import (
    UserRequirementsProfile,
    EligibilityDecision,
    EligibilityCriterionResult,
)

logger = logging.getLogger(__name__)

# Canonical education level ordering (higher index = higher level)
_EDUCATION_LEVELS = ["any", "10th", "12th", "diploma", "iti", "bachelors", "masters", "doctorate"]

# Phrases that indicate any graduate is acceptable
_ANY_GRADUATE_PHRASES = {
    "any graduate", "any degree", "any graduation", "graduate in any discipline",
    "degree in any field", "any bachelor", "any post graduate", "any pg",
}

# Exact/prefix patterns indicating all branches acceptable
_ANY_BRANCH_PHRASES = {
    "any branch", "all branches", "any discipline", "all disciplines",
    "any engineering", "any stream", "any specialization",
}

# Common engineering branch abbreviations -> full canonical names
# Used for bidirectional matching so "IT" matches "Information Technology" etc.
_BRANCH_ALIASES: dict[str, list[str]] = {
    "cs":   ["computer science", "cse"],
    "cse":  ["computer science", "computer science & engineering", "cs"],
    "it":   ["information technology", "it engineering"],
    "ece":  ["electronics & communication", "electronics and communication", "electronics & communication engineering"],
    "eee":  ["electrical & electronics", "electrical and electronics", "electrical & electronics engineering"],
    "ee":   ["electrical engineering", "electrical"],
    "me":   ["mechanical engineering", "mechanical"],
    "ce":   ["civil engineering", "civil"],
    "che":  ["chemical engineering", "chemical"],
    "ai":   ["artificial intelligence", "ai & ml", "ai and ml"],
    "ml":   ["machine learning"],
    "ds":   ["data science"],
    "it & cs": ["information technology", "computer science"],
}

# Build reverse lookup: full name -> abbreviations
_BRANCH_REVERSE: dict[str, list[str]] = {}
for _abbr, _fulls in _BRANCH_ALIASES.items():
    for _full in _fulls:
        _BRANCH_REVERSE.setdefault(_full, []).append(_abbr)


class EligibilityEvaluator:
    def __init__(self, user_profile: UserRequirementsProfile):
        self.profile = user_profile

    def update_profile(self, new_profile: UserRequirementsProfile) -> None:
        self.profile = new_profile

    def evaluate(self, job: JobExtractionSchema) -> EligibilityDecision:
        """Executes strict deterministic eligibility check."""
        # If model extracted that this is not an active job notification
        if not job.is_job:
            return EligibilityDecision(
                status="NOT_ELIGIBLE",
                criteria={
                    "is_job": EligibilityCriterionResult(
                        status="FAIL",
                        details="Content classified as non-job (e.g., result, answer key, or syllabus)",
                        extracted_value=job.is_job,
                    )
                },
                summary="Content does not announce an active job recruitment.",
                action_recommended="DISCARD",
            )

        criteria_results: Dict[str, EligibilityCriterionResult] = {}

        # 1. Job Type / Category Exclusion Check
        criteria_results["job_type"] = self._evaluate_job_type(job)

        # 2. Education Level Check
        criteria_results["education_level"] = self._evaluate_education_level(job)

        # 3. Age Criteria Check (fixed direction + min age + dynamic DOB)
        criteria_results["age"] = self._evaluate_age(job)

        # 4. Experience Criteria Check (fresher handling)
        criteria_results["experience"] = self._evaluate_experience(job)

        # 5. Educational Degree & Qualifications Check (token/word boundary matching)
        criteria_results["qualification"] = self._evaluate_qualification(job)

        # 6. Accepted Branches / Engineering Disciplines Check (token boundary matching)
        criteria_results["branch"] = self._evaluate_branch(job)

        # 7. Percentage Check (UNKNOWN when not specified — never FAIL)
        criteria_results["percentage"] = self._evaluate_percentage(job)

        # 8. Location Criteria Check
        criteria_results["location"] = self._evaluate_location(job)

        # NOTE: Fee is a PREFERENCE dimension, not a mandatory eligibility criterion.
        # A job with a high fee should show a warning, not be marked NOT_ELIGIBLE.

        # Compute Final Strict Decision
        has_fail = any(res.status == "FAIL" for res in criteria_results.values())
        has_unknown = any(res.status == "UNKNOWN" for res in criteria_results.values())

        if has_fail:
            status = "NOT_ELIGIBLE"
            action = "DISCARD"
            summary = "One or more mandatory requirements failed eligibility."
        elif has_unknown:
            status = "UNCERTAIN"
            action = (
                "UNCERTAIN_ALERT"
                if self.profile.notification_preferences.alert_on_uncertain
                else "DISCARD"
            )
            summary = "Key parameters are ambiguous or missing in notification; manual review required."
        else:
            status = "ELIGIBLE"
            action = "ALERT"
            summary = "All mandatory eligibility criteria passed successfully."

        return EligibilityDecision(
            status=status,
            criteria=criteria_results,
            summary=summary,
            action_recommended=action,
        )

    # ------------------------------------------------------------------
    # CRITERION: Job Type
    # ------------------------------------------------------------------
    def _evaluate_job_type(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        job_type_str = (job.job_type or "government").strip()
        job_type_lower = job_type_str.lower()
        for excluded in self.profile.excluded_types:
            if excluded.lower() in job_type_lower:
                return EligibilityCriterionResult(
                    status="FAIL",
                    details=f"Job type '{job.job_type}' matches excluded type '{excluded}'",
                    extracted_value=job.job_type,
                    required_value=f"Not in {self.profile.excluded_types}",
                )
        return EligibilityCriterionResult(
            status="PASS",
            details=f"Job type '{job_type_str}' is acceptable",
            extracted_value=job_type_str,
            required_value=self.profile.job_categories,
        )

    # ------------------------------------------------------------------
    # CRITERION: Education Level
    # ------------------------------------------------------------------
    def _evaluate_education_level(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        """
        Checks whether the job's minimum qualification matches or is at/below
        the user's declared highest education level.
        Uses word-boundary regex to prevent false substring matches (e.g. 'be' in 'cyber', 'iti' in 'critical').
        """
        if not job.qualification:
            return EligibilityCriterionResult(
                status="UNKNOWN",
                details="Education level requirement unclear — see qualification criterion",
                extracted_value=None,
                required_value=self.profile.education.minimum_level,
            )

        user_level = self.profile.education.minimum_level.lower()
        user_idx = _EDUCATION_LEVELS.index(user_level) if user_level in _EDUCATION_LEVELS else 5  # default bachelors

        job_levels_found = []
        for q in job.qualification:
            ql = q.lower().strip()
            if re.search(r"\b(ph\.?d|doctorate)\b", ql):
                job_levels_found.append(_EDUCATION_LEVELS.index("doctorate"))
            elif re.search(r"\b(master|masters|m\.?tech|m\.?e\.?|mca|mba|m\.?sc|m\.?com|post\s*graduate|pg)\b", ql):
                job_levels_found.append(_EDUCATION_LEVELS.index("masters"))
            elif re.search(r"\b(b\.?tech|b\.?e\.?|be|btech|b\.?sc|bsc|bca|b\.?com|bachelor|bachelors|graduate|graduation|degree)\b", ql):
                job_levels_found.append(_EDUCATION_LEVELS.index("bachelors"))
            elif re.search(r"\b(diploma|polytechnic)\b", ql):
                job_levels_found.append(_EDUCATION_LEVELS.index("diploma"))
            elif re.search(r"\b(iti|industrial training institute)\b", ql):
                job_levels_found.append(_EDUCATION_LEVELS.index("iti"))
            elif re.search(r"\b(12th|intermediate|\+2|hsc|senior secondary|higher secondary|class 12|class xii)\b", ql):
                job_levels_found.append(_EDUCATION_LEVELS.index("12th"))
            elif re.search(r"\b(10th|matriculation|matric|secondary school|high school|class 10|class x)\b", ql):
                job_levels_found.append(_EDUCATION_LEVELS.index("10th"))

        if not job_levels_found:
            return EligibilityCriterionResult(
                status="UNKNOWN",
                details="Cannot determine required education level from qualification text",
                extracted_value=job.qualification,
                required_value=self.profile.education.minimum_level,
            )

        # Job requires MINIMUM of the lowest acceptable listed level
        job_min_idx = min(job_levels_found)

        if user_idx >= job_min_idx:
            return EligibilityCriterionResult(
                status="PASS",
                details=f"Your education level '{user_level}' meets or exceeds the job requirement",
                extracted_value=_EDUCATION_LEVELS[job_min_idx] if job_min_idx < len(_EDUCATION_LEVELS) else "unknown",
                required_value=user_level,
            )
        else:
            return EligibilityCriterionResult(
                status="FAIL",
                details=f"Job requires education level '{_EDUCATION_LEVELS[job_min_idx]}' but your profile is '{user_level}'",
                extracted_value=_EDUCATION_LEVELS[job_min_idx] if job_min_idx < len(_EDUCATION_LEVELS) else "unknown",
                required_value=user_level,
            )

    # ------------------------------------------------------------------
    # CRITERION: Age  (FIXED direction + relaxation + dynamic DOB + min age)
    # ------------------------------------------------------------------
    def _evaluate_age(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        """
        Evaluates user's age against job limits (both minimum and maximum).
        Derives current age dynamically from date_of_birth if present,
        or falls back to profile.age.maximum.
        Checks:
          1. Underage check: job.age_min is not None and user_age < job.age_min -> FAIL
          2. Age max unknown: job.age_max is None -> UNKNOWN
          3. Overage check: user_age > (job.age_max + category_relaxation) -> FAIL
          4. Otherwise: PASS
        """
        # User's actual age calculation (dynamic from DOB if available)
        user_age = self.profile.age.maximum
        if self.profile.date_of_birth:
            try:
                from datetime import date
                dob = date.fromisoformat(str(self.profile.date_of_birth).strip())
                today = date.today()
                user_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            except Exception:
                user_age = self.profile.age.maximum

        # 1. Minimum age check
        if job.age_min is not None and user_age < job.age_min:
            return EligibilityCriterionResult(
                status="FAIL",
                details=f"Job requires minimum age of {job.age_min}y, but your age is {user_age}y (underage)",
                extracted_value=job.age_min,
                required_value=f">= {job.age_min}y",
            )

        # 2. Maximum age check
        if job.age_max is None:
            return EligibilityCriterionResult(
                status="UNKNOWN",
                details="Maximum age limit is not explicitly declared in the notification",
                extracted_value=None,
                required_value=user_age,
            )

        user_cat = self.profile.age.category
        relaxation = self.profile.age.category_age_relaxations.get(user_cat, 0)
        effective_max_for_user = job.age_max + relaxation

        if user_age <= effective_max_for_user:
            return EligibilityCriterionResult(
                status="PASS",
                details=(
                    f"Job age limit {job.age_max}y + {user_cat} relaxation {relaxation}y = "
                    f"{effective_max_for_user}y limit. Your age: {user_age}y ✓"
                ),
                extracted_value=job.age_max,
                required_value=effective_max_for_user,
            )
        else:
            return EligibilityCriterionResult(
                status="FAIL",
                details=(
                    f"Job age limit {job.age_max}y + {user_cat} relaxation {relaxation}y = "
                    f"{effective_max_for_user}y limit. Your age: {user_age}y ✗"
                ),
                extracted_value=job.age_max,
                required_value=effective_max_for_user,
            )

    # ------------------------------------------------------------------
    # CRITERION: Experience  (FIXED fresher handling)
    # ------------------------------------------------------------------
    def _evaluate_experience(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        if job.experience_required is None:
            return EligibilityCriterionResult(
                status="UNKNOWN",
                details="Experience requirement wording is ambiguous or unstated in source text",
                extracted_value=None,
                required_value=f"Fresher allowed={self.profile.experience.fresher_allowed}",
            )

        if not job.experience_required:
            # Job explicitly allows freshers — always PASS regardless of user's experience
            return EligibilityCriterionResult(
                status="PASS",
                details="Freshers explicitly allowed / no prior experience required",
                extracted_value="0 years",
                required_value="Fresher",
            )

        # Job REQUIRES experience
        min_years = job.experience_years_min or 1

        # If user is a fresher (fresher_allowed=True and max_years_experience_required==0),
        # and job requires experience, this is a FAIL — not a PASS.
        if self.profile.experience.fresher_allowed and self.profile.experience.max_years_experience_required == 0:
            return EligibilityCriterionResult(
                status="FAIL",
                details=f"Job requires {min_years} year(s) experience, but your profile indicates fresher status",
                extracted_value=f"{min_years} years required",
                required_value="Fresher (0 years)",
            )

        if min_years <= self.profile.experience.max_years_experience_required:
            return EligibilityCriterionResult(
                status="PASS",
                details=(
                    f"Required experience ({min_years} yrs) is within your profile "
                    f"({self.profile.experience.max_years_experience_required} yrs)"
                ),
                extracted_value=f"{min_years} years",
                required_value=f"<= {self.profile.experience.max_years_experience_required} years",
            )
        else:
            return EligibilityCriterionResult(
                status="FAIL",
                details=(
                    f"Required experience ({min_years} yrs) exceeds your profile maximum "
                    f"({self.profile.experience.max_years_experience_required} yrs)"
                ),
                extracted_value=f"{min_years} years",
                required_value=f"<= {self.profile.experience.max_years_experience_required} years",
            )

    # ------------------------------------------------------------------
    # CRITERION: Qualification  (FIXED with token boundary matching)
    # ------------------------------------------------------------------
    @staticmethod
    def _match_qualification_token(acc: str, q: str) -> bool:
        """
        Safely matches degree abbreviations / names against qualification strings
        using token and word boundaries to prevent substring false positives
        (e.g., 'ca' in 'mechanical', 'be' in 'cyber', 'ba' in 'database').
        """
        if acc == q:
            return True
        ac = re.sub(r"[\s\.\-]+", "", acc)
        qc = re.sub(r"[\s\.\-]+", "", q)
        if ac == qc and len(ac) >= 2:
            return True
        esc_a = re.escape(acc).replace(r"\.", r"\.?")
        if re.search(r"(?<!\w)" + esc_a + r"(?!\w)", q):
            return True
        esc_q = re.escape(q).replace(r"\.", r"\.?")
        if re.search(r"(?<!\w)" + esc_q + r"(?!\w)", acc):
            return True
        return False

    def _evaluate_qualification(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        if not job.qualification:
            return EligibilityCriterionResult(
                status="UNKNOWN",
                details="Mandatory degree qualifications are not stated in notification text",
                extracted_value=None,
                required_value=self.profile.education.accepted_degrees,
            )

        job_quals_lower = [q.lower().strip() for q in job.qualification]
        accepted_lower = [d.lower().strip() for d in self.profile.education.accepted_degrees]

        matched = []
        for q in job_quals_lower:
            # SAFE: check for "any graduate/degree" phrases (PASS for any bachelor-level user)
            if any(phrase in q for phrase in _ANY_GRADUATE_PHRASES):
                matched.append(q)
                continue
            # Token/word boundary match against accepted degrees
            for acc in accepted_lower:
                if self._match_qualification_token(acc, q):
                    matched.append(q)
                    break

        if matched:
            return EligibilityCriterionResult(
                status="PASS",
                details=f"Qualification '{matched[0]}' matches accepted profile degrees",
                extracted_value=job.qualification,
                required_value=self.profile.education.accepted_degrees,
            )

        return EligibilityCriterionResult(
            status="FAIL",
            details=(
                f"Extracted qualifications {job.qualification} do not match "
                f"accepted degrees {self.profile.education.accepted_degrees}"
            ),
            extracted_value=job.qualification,
            required_value=self.profile.education.accepted_degrees,
        )

    # ------------------------------------------------------------------
    # CRITERION: Branch  (with alias expansion + token boundary matching)
    # ------------------------------------------------------------------
    @staticmethod
    def _branch_expansions(branch_lower: str) -> set[str]:
        """Return all known forms of a branch name (abbreviations + full names)."""
        forms = {branch_lower}
        if branch_lower in _BRANCH_ALIASES:
            forms.update(_BRANCH_ALIASES[branch_lower])
        if branch_lower in _BRANCH_REVERSE:
            forms.update(_BRANCH_REVERSE[branch_lower])
        return forms

    def _evaluate_branch(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        if not job.accepted_branches:
            return EligibilityCriterionResult(
                status="UNKNOWN",
                details="Specific degree branches not specified in excerpt; verify official notification",
                extracted_value=None,
                required_value=self.profile.education.branches,
            )

        job_branches_lower = [b.lower().strip() for b in job.accepted_branches]
        user_branches_lower = [b.lower().strip() for b in self.profile.education.branches]

        user_all_forms: set[str] = set()
        for ub in user_branches_lower:
            user_all_forms.update(self._branch_expansions(ub))

        matched = []
        for jb in job_branches_lower:
            # SAFE "any branch" check — exact known phrase, NOT arbitrary substring
            if any(phrase in jb for phrase in _ANY_BRANCH_PHRASES):
                matched.append("All Branches")
                continue

            jb_forms = self._branch_expansions(jb)

            # Check if any job-branch form overlaps with any user-branch form
            if jb_forms & user_all_forms:
                matched.append(jb)
                continue

            # Fallback: token boundary match in both directions (handles partial names safely)
            for ub_form in user_all_forms:
                if len(ub_form) >= 3:
                    p1 = rf"(?<!\w){re.escape(ub_form)}(?!\w)"
                    p2 = rf"(?<!\w){re.escape(jb)}(?!\w)"
                    if re.search(p1, jb) or re.search(p2, ub_form):
                        matched.append(jb)
                        break

        if matched:
            return EligibilityCriterionResult(
                status="PASS",
                details=f"Branch '{matched[0]}' matches eligible branches",
                extracted_value=job.accepted_branches,
                required_value=self.profile.education.branches,
            )

        return EligibilityCriterionResult(
            status="FAIL",
            details=(
                f"Required branches {job.accepted_branches} do not match "
                f"your branches {self.profile.education.branches}"
            ),
            extracted_value=job.accepted_branches,
            required_value=self.profile.education.branches,
        )

    # ------------------------------------------------------------------
    # CRITERION: Percentage
    # ------------------------------------------------------------------
    def _evaluate_percentage(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        """
        Key rule: Absence of a percentage requirement means NO restriction — PASS.
        Only FAIL when the job EXPLICITLY states a minimum that the user's profile
        indicates they cannot meet.
        """
        if job.minimum_percentage is None:
            return EligibilityCriterionResult(
                status="PASS",
                details="No minimum percentage/CGPA requirement stated in notification",
                extracted_value=None,
                required_value="Not required",
            )

        user_pct = self.profile.education.minimum_percentage or 0.0

        if user_pct >= job.minimum_percentage:
            return EligibilityCriterionResult(
                status="PASS",
                details=(
                    f"Job requires {job.minimum_percentage}% minimum; "
                    f"your profile specifies {user_pct}% ✓"
                ),
                extracted_value=job.minimum_percentage,
                required_value=user_pct,
            )
        else:
            return EligibilityCriterionResult(
                status="FAIL",
                details=(
                    f"Job requires {job.minimum_percentage}% minimum percentage; "
                    f"your profile specifies only {user_pct}%"
                ),
                extracted_value=job.minimum_percentage,
                required_value=user_pct,
            )

    # ------------------------------------------------------------------
    # CRITERION: Location
    # ------------------------------------------------------------------
    def _evaluate_location(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        """
        Evaluates job posting locations against user's location preferences.
        - If any job location matches an explicitly excluded location -> FAIL
        - If user accepts 'All India' or 'India' -> PASS
        - If job location is empty or 'All India' -> PASS (nationwide)
        - Otherwise, verify at least one job location matches allowed locations
        """
        job_locs = [loc.lower().strip() for loc in (job.location or [])]
        user_allowed = [loc.lower().strip() for loc in (self.profile.location.allowed or ["All India"])]
        user_excluded = [loc.lower().strip() for loc in (self.profile.location.exclude_locations or [])]

        # 1. Check excluded locations
        for jloc in job_locs:
            for ex in user_excluded:
                if ex in jloc or jloc in ex:
                    return EligibilityCriterionResult(
                        status="FAIL",
                        details=f"Job location '{jloc}' matches your excluded location '{ex}'",
                        extracted_value=job.location,
                        required_value=f"Exclude {self.profile.location.exclude_locations}",
                    )

        # 2. Check if user allows All India / open
        if any(open_loc in user_allowed for open_loc in ["all india", "india", "any"]):
            return EligibilityCriterionResult(
                status="PASS",
                details="Location matches your preference (All India accepted)",
                extracted_value=job.location or ["All India"],
                required_value="All India",
            )

        # 3. Check if job is nationwide / open
        if not job_locs or any(loc in ["all india", "india", "nationwide", "across india"] for loc in job_locs):
            return EligibilityCriterionResult(
                status="PASS",
                details="Job is open across India / location unspecified",
                extracted_value=job.location or ["All India"],
                required_value=self.profile.location.allowed,
            )

        # 4. Check if any job location matches user's allowed locations
        matched_loc = None
        for jloc in job_locs:
            for aloc in user_allowed:
                if aloc in jloc or jloc in aloc:
                    matched_loc = jloc
                    break
            if matched_loc:
                break

        if matched_loc:
            return EligibilityCriterionResult(
                status="PASS",
                details=f"Job location '{matched_loc}' matches your preferred locations",
                extracted_value=job.location,
                required_value=self.profile.location.allowed,
            )
        else:
            return EligibilityCriterionResult(
                status="FAIL",
                details=f"Job location(s) {job.location} not in your preferred locations {self.profile.location.allowed}",
                extracted_value=job.location,
                required_value=self.profile.location.allowed,
            )
