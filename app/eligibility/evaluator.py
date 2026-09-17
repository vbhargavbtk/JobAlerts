"""
Deterministic Eligibility Evaluation Engine
Strictly evaluates extracted job parameters against the User Requirements Profile.

Deterministic Hard Rules:
  - If ANY mandatory requirement = FAIL  -> NOT_ELIGIBLE
  - Else if ANY mandatory requirement = UNKNOWN -> UNCERTAIN
  - Else (all mandatory PASS) -> ELIGIBLE

CRITICAL SPECIFICATION RULE: NEVER convert UNKNOWN into PASS without explicit evidence.
"""
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from app.ai.schemas import JobExtractionSchema, PostItemSchema
from app.eligibility.models import (
    UserRequirementsProfile,
    EligibilityDecision,
    EligibilityCriterionResult,
    PostEligibilityResult,
)
from app.eligibility.normalization import (
    EDUCATION_LEVELS,
    get_education_level_index,
    extract_education_levels,
    is_open_graduation_requirement,
    normalize_degree,
    get_all_branch_aliases,
    branches_overlap,
    ANY_BRANCH_PHRASES,
    is_non_job_announcement,
    normalize_category,
    is_medical_or_nursing_qualification,
    is_law_qualification,
    is_teaching_qualification,
    extract_disciplines_from_text,
)

logger = logging.getLogger(__name__)

# Phrases that indicate any graduate is acceptable
_ANY_GRADUATE_PHRASES = {
    "any graduate", "any degree", "any graduation", "graduate in any discipline",
    "degree in any field", "any bachelor", "any post graduate", "any pg",
    "graduate pass", "graduation in any discipline", "degree in any stream",
    "a degree from a recognized university", "degree from a recognized university",
    "graduate degree in any discipline", "degree or equivalent",
}

# Post titles that represent general entry-level roles where freshers are standardly accepted
_ENTRY_LEVEL_TITLES = [
    r"\bclerk\b", r"\bassistant\b", r"\bjunior\s*associate\b", r"\bconstable\b",
    r"\btrainee\b", r"\bapprentice\b", r"\bprocess\s*server\b", r"\borderly\b",
    r"\bchowkidar\b", r"\bmts\b", r"\bmulti\s*tasking\b", r"\btax\s*assistant\b",
    r"\bstenographer\b", r"\bsection\s*controller\b", r"\boffice\s*assistant\b",
]

# Post titles that generally require open graduation with no specific engineering discipline
_GENERAL_GRADUATE_POST_TITLES = [
    r"\bclerk\b", r"\btax\s*assistant\b", r"\bjunior\s*associate\b",
    r"\boffice\s*assistant\b", r"\bsection\s*controller\b", r"\bstenographer\b",
    r"\bpersonal\s*assistant\b", r"\bprocess\s*server\b", r"\bchowkidar\b",
    r"\borderly\b", r"\bmts\b", r"\bmulti\s*tasking\b", r"\bexecutive\s*assistant\b",
]


class EligibilityEvaluator:
    def __init__(self, user_profile: UserRequirementsProfile):
        self.profile = user_profile

    def update_profile(self, new_profile: UserRequirementsProfile) -> None:
        self.profile = new_profile

    def evaluate(self, job: JobExtractionSchema) -> EligibilityDecision:
        """Executes strict deterministic eligibility check with multi-post support."""
        # 0. Deterministic Non-Job Pre-Filter (Admit Cards, Results, Syllabus, Answer Keys)
        if not job.is_job or is_non_job_announcement(job.post_name, " ".join(job.qualification), job.official_notification_url):
            decision = EligibilityDecision(
                status="NOT_ELIGIBLE",
                criteria={
                    "is_job": EligibilityCriterionResult(
                        status="FAIL",
                        details="Content classified as non-job (e.g., exam admit card, answer key, result, or syllabus)",
                        extracted_value=job.is_job,
                    )
                },
                summary="Content does not announce an active job recruitment.",
                action_recommended="DISCARD",
                taxonomy_tag="non_job_announcement"
            )
            return self._enrich_with_preferences_and_constraints(job, decision)

        # Check for multi-post structure in notification
        if job.posts and len(job.posts) > 1:
            decision = self._evaluate_multi_posts(job)
            return self._enrich_with_preferences_and_constraints(job, decision)

        # Check if notification contains multiple comma-separated posts with diverse qualifications
        derived_posts = self._detect_and_split_multi_posts(job)
        if len(derived_posts) > 1:
            decision = self._evaluate_derived_multi_posts(job, derived_posts)
            return self._enrich_with_preferences_and_constraints(job, decision)

        # Single Post Standard Evaluation
        decision = self._evaluate_single_post(job)
        return self._enrich_with_preferences_and_constraints(job, decision)

    # ------------------------------------------------------------------
    # SINGLE POST EVALUATION
    # ------------------------------------------------------------------
    def _evaluate_single_post(self, job: JobExtractionSchema, post_name: Optional[str] = None) -> EligibilityDecision:
        criteria_results: Dict[str, EligibilityCriterionResult] = {}
        target_post = post_name or job.post_name or "General Post"

        # 1. Job Type / Category Exclusion Check
        criteria_results["job_type"] = self._evaluate_job_type(job)

        # 2. Education Level Check
        criteria_results["education_level"] = self._evaluate_education_level(job, post_name=target_post)

        # 3. Age Criteria Check (fixed direction + min age + dynamic DOB + relaxation)
        criteria_results["age"] = self._evaluate_age(job)

        # 4. Experience Criteria Check (fresher handling + entry-level recognition)
        criteria_results["experience"] = self._evaluate_experience(job, post_name=target_post)

        # 5. Educational Degree & Qualifications Check (canonical mapping & domain guard)
        qual_res, matched_qual = self._evaluate_qualification(job)
        criteria_results["qualification"] = qual_res

        # 6. Accepted Branches Check ("Any Branch" & "Open Degree" aware)
        criteria_results["branch"] = self._evaluate_branch(job, matched_qual=matched_qual, post_name=target_post)

        # 7. Percentage Check (absence means no restriction — PASS)
        criteria_results["percentage"] = self._evaluate_percentage(job)

        # 8. Location Criteria Check
        criteria_results["location"] = self._evaluate_location(job)

        # 9. 10th & 12th Intermediate Subjects Check (Maths, Physics, etc.)
        criteria_results["subjects_10_12"] = self._evaluate_subjects(job, post_name=target_post)

        # 10. Physical Measurement Standards Check (Height, Chest)
        criteria_results["physical_standards"] = self._evaluate_physical_standards(job, post_name=target_post)

        # Compute Final Strict Decision
        has_fail = any(res.status == "FAIL" for res in criteria_results.values())
        has_unknown = any(res.status == "UNKNOWN" for res in criteria_results.values())

        if has_fail:
            status = "NOT_ELIGIBLE"
            action = "DISCARD"
            fail_items = [f"{k}: {v.details}" for k, v in criteria_results.items() if v.status == "FAIL"]
            summary = "One or more mandatory requirements failed eligibility: " + "; ".join(fail_items)
            taxonomy_tag = "criteria_failed"
        elif has_unknown:
            unknown_mode = getattr(getattr(self.profile, "classification_preferences", None), "unknown_handling", "REVIEW")
            if unknown_mode == "NOT_ELIGIBLE":
                status = "NOT_ELIGIBLE"
                action = "DISCARD"
                unknown_items = [k for k, v in criteria_results.items() if v.status == "UNKNOWN"]
                summary = f"Key parameters ({', '.join(unknown_items)}) missing in notification; treated as NOT_ELIGIBLE per preference."
                taxonomy_tag = "missing_information_discarded"
            elif unknown_mode == "POTENTIALLY_ELIGIBLE":
                status = "ELIGIBLE"
                action = "ALERT"
                unknown_items = [k for k, v in criteria_results.items() if v.status == "UNKNOWN"]
                summary = f"Passed with potential eligibility; parameters ({', '.join(unknown_items)}) need manual verification."
                taxonomy_tag = "potentially_eligible"
            else:
                status = "UNCERTAIN"
                action = (
                    "UNCERTAIN_ALERT"
                    if self.profile.notification_preferences.alert_on_uncertain
                    else "DISCARD"
                )
                unknown_items = [k for k, v in criteria_results.items() if v.status == "UNKNOWN"]
                summary = f"Key parameters ({', '.join(unknown_items)}) are ambiguous or missing in notification; manual review required."
                taxonomy_tag = "missing_reliable_information"
        else:
            status = "ELIGIBLE"
            action = "ALERT"
            summary = "All mandatory eligibility criteria passed successfully."
            taxonomy_tag = "eligible"

        return EligibilityDecision(
            status=status,
            criteria=criteria_results,
            summary=summary,
            action_recommended=action,
            taxonomy_tag=taxonomy_tag,
        )

    # ------------------------------------------------------------------
    # MULTI-POST NOTIFICATIONS EVALUATOR
    # ------------------------------------------------------------------
    def _evaluate_multi_posts(self, job: JobExtractionSchema) -> EligibilityDecision:
        post_results: Dict[str, PostEligibilityResult] = {}
        has_eligible = False
        has_uncertain = False

        for post_item in job.posts:
            p_name = post_item.post_name or "Unnamed Post"
            p_schema = JobExtractionSchema(
                is_job=True,
                job_type=job.job_type,
                organization=job.organization,
                post_name=p_name,
                vacancies=post_item.vacancies or job.vacancies,
                qualification=post_item.qualification or job.qualification,
                accepted_branches=post_item.accepted_branches or job.accepted_branches,
                minimum_percentage=job.minimum_percentage,
                age_min=post_item.age_min if post_item.age_min is not None else job.age_min,
                age_max=post_item.age_max if post_item.age_max is not None else job.age_max,
                experience_required=post_item.experience_required if post_item.experience_required is not None else job.experience_required,
                experience_years_min=post_item.experience_years_min if post_item.experience_years_min is not None else job.experience_years_min,
                location=job.location,
            )
            decision = self._evaluate_single_post(p_schema, post_name=p_name)
            post_results[p_name] = PostEligibilityResult(
                post_name=p_name,
                status=decision.status,
                details=decision.summary,
                criteria=decision.criteria,
            )
            if decision.status == "ELIGIBLE":
                has_eligible = True
            elif decision.status == "UNCERTAIN":
                has_uncertain = True

        return self._synthesize_multi_post_verdict(job, post_results, has_eligible, has_uncertain)

    def _detect_and_split_multi_posts(self, job: JobExtractionSchema) -> List[Tuple[str, List[str]]]:
        """Detects if notification contains multiple posts with matching qualifications."""
        post_name = job.post_name or ""
        # Delimiters outside parentheses: commas, spaced ampersands, or ' and '
        raw_parts = re.split(r",(?![^(]*\))|(?<=\s)&(?=\s)(?![^(]*\))|\band\b(?![^(]*\))", post_name)
        parts = [p.strip() for p in raw_parts if len(p.strip()) > 2]
        if len(parts) <= 1:
            return []

        # If job has multiple qualifications, evaluate each post with the declared qualifications
        quals = job.qualification or []
        sub_posts = []
        for p in parts:
            # Match qualifications relevant to this post if clear
            matched_q = []
            pl = p.lower()
            for q in quals:
                ql = q.lower()
                if "clerk" in pl or "assistant" in pl or "officer" in pl or "server" in pl:
                    if is_open_graduation_requirement(ql) or "graduate" in ql or "degree" in ql:
                        matched_q.append(q)
                elif "doctor" in pl or "medical" in pl or "physiotherapist" in pl or "hygienist" in pl:
                    if is_medical_or_nursing_qualification(ql):
                        matched_q.append(q)
                elif "driver" in pl or "chowkidar" in pl or "sweeper" in pl:
                    if "10th" in ql or "matric" in ql or "5th" in ql or "8th" in ql:
                        matched_q.append(q)

            # If no specialized filter matched, retain all qualifications for the post
            sub_posts.append((p, matched_q if matched_q else quals))
        return sub_posts

    def _evaluate_derived_multi_posts(
        self,
        job: JobExtractionSchema,
        derived_posts: List[Tuple[str, List[str]]]
    ) -> EligibilityDecision:
        post_results: Dict[str, PostEligibilityResult] = {}
        has_eligible = False
        has_uncertain = False

        for p_name, p_quals in derived_posts:
            p_schema = JobExtractionSchema(
                is_job=True,
                job_type=job.job_type,
                organization=job.organization,
                post_name=p_name,
                vacancies=job.vacancies,
                qualification=p_quals,
                accepted_branches=job.accepted_branches,
                minimum_percentage=job.minimum_percentage,
                age_min=job.age_min,
                age_max=job.age_max,
                experience_required=job.experience_required,
                experience_years_min=job.experience_years_min,
                location=job.location,
            )
            decision = self._evaluate_single_post(p_schema, post_name=p_name)
            post_results[p_name] = PostEligibilityResult(
                post_name=p_name,
                status=decision.status,
                details=decision.summary,
                criteria=decision.criteria,
            )
            if decision.status == "ELIGIBLE":
                has_eligible = True
            elif decision.status == "UNCERTAIN":
                has_uncertain = True

        return self._synthesize_multi_post_verdict(job, post_results, has_eligible, has_uncertain)

    def _synthesize_multi_post_verdict(
        self,
        job: JobExtractionSchema,
        post_results: Dict[str, PostEligibilityResult],
        has_eligible: bool,
        has_uncertain: bool
    ) -> EligibilityDecision:
        # Determine aggregate criteria from best-matching post
        eligible_posts = [p for p, res in post_results.items() if res.status == "ELIGIBLE"]
        uncertain_posts = [p for p, res in post_results.items() if res.status == "UNCERTAIN"]
        ineligible_posts = [p for p, res in post_results.items() if res.status == "NOT_ELIGIBLE"]

        if has_eligible:
            best_post_name = eligible_posts[0]
            best_criteria = post_results[best_post_name].criteria
            summary = f"Eligible for {len(eligible_posts)} post(s): {', '.join(eligible_posts)}."
            if ineligible_posts:
                summary += f" (Ineligible for: {', '.join(ineligible_posts)})"
            return EligibilityDecision(
                status="ELIGIBLE",
                criteria=best_criteria,
                posts=post_results,
                summary=summary,
                action_recommended="ALERT",
                taxonomy_tag="multi_post_eligible",
            )
        elif has_uncertain:
            best_post_name = uncertain_posts[0]
            best_criteria = post_results[best_post_name].criteria
            summary = f"Multi-post notification has uncertain eligibility for: {', '.join(uncertain_posts)}."
            return EligibilityDecision(
                status="UNCERTAIN",
                criteria=best_criteria,
                posts=post_results,
                summary=summary,
                action_recommended=(
                    "UNCERTAIN_ALERT"
                    if self.profile.notification_preferences.alert_on_uncertain
                    else "DISCARD"
                ),
                taxonomy_tag="multi_post_uncertain",
            )
        else:
            first_post_name = next(iter(post_results))
            first_criteria = post_results[first_post_name].criteria
            summary = f"Ineligible across all declared posts: {', '.join(ineligible_posts)}."
            return EligibilityDecision(
                status="NOT_ELIGIBLE",
                criteria=first_criteria,
                posts=post_results,
                summary=summary,
                action_recommended="DISCARD",
                taxonomy_tag="multi_post_ineligible",
            )

    # ------------------------------------------------------------------
    # CRITERION 1: Job Type / Category
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
    # CRITERION 2: Education Level
    # ------------------------------------------------------------------
    def _evaluate_education_level(
        self,
        job: JobExtractionSchema,
        post_name: Optional[str] = None
    ) -> EligibilityCriterionResult:
        """
        Compares job's required minimum education against user's declared profile education level.
        Uses canonical rank ordering from normalization engine.
        """
        user_level = (self.profile.education.minimum_level or "bachelors").lower().strip()
        user_idx = get_education_level_index(user_level)

        # Check post-title specific implied education level
        p_name = (post_name or job.post_name or "").lower()
        if re.search(r"\b(assistant\s*professor|associate\s*professor|professor|lecturer)\b", p_name):
            # College/University teaching standardly requires Master's + NET or PhD
            job_min_idx = get_education_level_index("masters")
            if user_idx < job_min_idx:
                return EligibilityCriterionResult(
                    status="FAIL",
                    details="Assistant Professor / Lecturer positions require a minimum of Master's Degree (PG) + NET/Ph.D.",
                    extracted_value="masters",
                    required_value=user_level,
                )

        if not job.qualification:
            return EligibilityCriterionResult(
                status="UNKNOWN",
                details="Education level requirement unclear — no qualifications declared in excerpt",
                extracted_value=None,
                required_value=user_level,
            )

        found_levels = extract_education_levels(job.qualification)
        if not found_levels:
            # Check if any qualification text has open graduate wording
            if any(is_open_graduation_requirement(q) for q in job.qualification):
                found_levels = ["bachelors"]

        if not found_levels:
            return EligibilityCriterionResult(
                status="UNKNOWN",
                details="Cannot determine required education level from qualification text",
                extracted_value=job.qualification,
                required_value=user_level,
            )

        # Job minimum is the lowest level among acceptable options
        job_indices = [get_education_level_index(lvl) for lvl in found_levels]
        job_min_idx = min(job_indices)
        job_min_level = EDUCATION_LEVELS[job_min_idx]

        if user_idx >= job_min_idx:
            return EligibilityCriterionResult(
                status="PASS",
                details=f"Your education level '{user_level}' meets or exceeds required level '{job_min_level}'",
                extracted_value=job_min_level,
                required_value=user_level,
            )
        else:
            return EligibilityCriterionResult(
                status="FAIL",
                details=f"Job requires education level '{job_min_level}', but your profile level is '{user_level}'",
                extracted_value=job_min_level,
                required_value=user_level,
            )

    # ------------------------------------------------------------------
    # CRITERION 3: Age (Dynamic DOB, Min Age, Category Relaxation, Cut-off)
    # ------------------------------------------------------------------
    def _evaluate_age(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        user_age = self.profile.age.maximum
        if self.profile.date_of_birth:
            try:
                from datetime import date
                dob = date.fromisoformat(str(self.profile.date_of_birth).strip())
                today = date.today()
                user_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            except Exception:
                user_age = self.profile.age.maximum

        # 1. Minimum Age Check
        if job.age_min is not None and user_age < job.age_min:
            return EligibilityCriterionResult(
                status="FAIL",
                details=f"Job requires minimum age of {job.age_min}y, but your age is {user_age}y (underage)",
                extracted_value=job.age_min,
                required_value=f">= {job.age_min}y",
            )

        # 2. Maximum Age Check
        if job.age_max is None:
            return EligibilityCriterionResult(
                status="UNKNOWN",
                details="Maximum age limit is not explicitly declared in the notification",
                extracted_value=None,
                required_value=user_age,
            )

        user_cat = normalize_category(self.profile.age.category or "General")
        relaxation = self.profile.age.category_age_relaxations.get(user_cat, 0)
        effective_max = job.age_max + relaxation

        if user_age <= effective_max:
            return EligibilityCriterionResult(
                status="PASS",
                details=(
                    f"Job age limit {job.age_max}y + {user_cat} relaxation {relaxation}y = "
                    f"{effective_max}y limit. Your age: {user_age}y ✓"
                ),
                extracted_value=job.age_max,
                required_value=effective_max,
            )
        else:
            return EligibilityCriterionResult(
                status="FAIL",
                details=(
                    f"Job age limit {job.age_max}y + {user_cat} relaxation {relaxation}y = "
                    f"{effective_max}y limit. Your age: {user_age}y exceeds limit ✗"
                ),
                extracted_value=job.age_max,
                required_value=effective_max,
            )

    # ------------------------------------------------------------------
    # CRITERION 4: Experience (Fresher & Entry-level Detection)
    # ------------------------------------------------------------------
    def _evaluate_experience(
        self,
        job: JobExtractionSchema,
        post_name: Optional[str] = None
    ) -> EligibilityCriterionResult:
        # If experience is explicitly false or 0 years required
        if job.experience_required is False or job.experience_years_min == 0:
            return EligibilityCriterionResult(
                status="PASS",
                details="Freshers explicitly allowed / no prior experience required",
                extracted_value="0 years",
                required_value="Fresher",
            )

        # If job REQUIRES experience
        if job.experience_required is True:
            min_years = job.experience_years_min or 1
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

        # If experience_required is None (unstated in source excerpt)
        p_name = (post_name or job.post_name or "").lower()
        if any(re.search(pat, p_name) for pat in _ENTRY_LEVEL_TITLES):
            # Standard government entry-level positions without stated experience are open to freshers
            return EligibilityCriterionResult(
                status="PASS",
                details=f"Entry-level post '{post_name or job.post_name}' standardly accepts freshers without prior experience",
                extracted_value="Implicit freshers eligible",
                required_value="Fresher",
            )

        return EligibilityCriterionResult(
            status="UNKNOWN",
            details="Experience requirement wording is ambiguous or unstated in source text",
            extracted_value=None,
            required_value=f"Fresher allowed={self.profile.experience.fresher_allowed}",
        )

    # ------------------------------------------------------------------
    # CRITERION 5: Qualification & Degree (Canonical Mapping + Domain Guard)
    # ------------------------------------------------------------------
    @staticmethod
    def _match_qualification_token(acc: str, q: str) -> bool:
        """Safely matches degree abbreviations / names using token boundary checks."""
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

    def _evaluate_qualification(self, job: JobExtractionSchema) -> Tuple[EligibilityCriterionResult, Optional[str]]:
        if not job.qualification:
            p_name = (job.post_name or "").lower()
            if is_medical_or_nursing_qualification(p_name) or re.search(r"\b(nursing|nurse|paramedical|pharmacist|medical officer|doctor|physician|radiographer|laboratory technician)\b", p_name):
                return (
                    EligibilityCriterionResult(
                        status="FAIL",
                        details=f"Post '{job.post_name}' requires Medical/Nursing/Healthcare qualifications not held in your engineering profile",
                        extracted_value="Medical/Healthcare post",
                        required_value=self.profile.education.accepted_degrees,
                    ),
                    None,
                )
            if is_law_qualification(p_name) or re.search(r"\b(law officer|prosecutor|advocate|civil judge|magistrate)\b", p_name):
                return (
                    EligibilityCriterionResult(
                        status="FAIL",
                        details=f"Post '{job.post_name}' requires Legal/Law degree not held in your engineering profile",
                        extracted_value="Law/Legal post",
                        required_value=self.profile.education.accepted_degrees,
                    ),
                    None,
                )
            return (
                EligibilityCriterionResult(
                    status="UNKNOWN",
                    details="Mandatory degree qualifications are not stated in notification text",
                    extracted_value=None,
                    required_value=self.profile.education.accepted_degrees,
                ),
                None,
            )

        accepted_normalized = set()
        for d in self.profile.education.accepted_degrees:
            norm_d = normalize_degree(d)
            if norm_d:
                accepted_normalized.add(norm_d)
            accepted_normalized.add(d.strip().lower())

        user_level = (self.profile.education.minimum_level or "bachelors").lower().strip()
        user_level_idx = get_education_level_index(user_level)
        bachelors_idx = get_education_level_index("bachelors")

        matched_qual = None
        for q in job.qualification:
            ql = q.lower().strip()

            # Medical/Nursing guard: Never match to general engineering/science profile
            if is_medical_or_nursing_qualification(ql):
                if not any("nurs" in ad.lower() or "mbbs" in ad.lower() for ad in self.profile.education.accepted_degrees):
                    continue

            # Law guard
            if is_law_qualification(ql):
                if not any("law" in ad.lower() or "llb" in ad.lower() for ad in self.profile.education.accepted_degrees):
                    continue

            # 1. Check open degree phrases ("Any Graduate", "Degree in any discipline", "Graduation", etc.)
            if is_open_graduation_requirement(ql) or any(phrase in ql for phrase in _ANY_GRADUATE_PHRASES):
                if user_level_idx >= bachelors_idx or "graduation" in accepted_normalized or "degree" in accepted_normalized:
                    matched_qual = q
                    break

            # 2. Check canonical degree mapping ("Full-time engineering degree" -> "B.Tech", etc.)
            canonical_q = normalize_degree(ql)
            if canonical_q and canonical_q in accepted_normalized:
                matched_qual = q
                break

            # 3. Check exact token boundary match
            for acc in self.profile.education.accepted_degrees:
                acc_lower = acc.lower().strip()
                if self._match_qualification_token(acc_lower, ql):
                    matched_qual = q
                    break
            if matched_qual:
                break

        if matched_qual:
            return (
                EligibilityCriterionResult(
                    status="PASS",
                    details=f"Qualification '{matched_qual}' matches accepted profile degrees",
                    extracted_value=job.qualification,
                    required_value=self.profile.education.accepted_degrees,
                ),
                matched_qual,
            )

        return (
            EligibilityCriterionResult(
                status="FAIL",
                details=(
                    f"Extracted qualifications {job.qualification} do not match "
                    f"accepted degrees {self.profile.education.accepted_degrees}"
                ),
                extracted_value=job.qualification,
                required_value=self.profile.education.accepted_degrees,
            ),
            None,
        )

    # ------------------------------------------------------------------
    # CRITERION 6: Branch / Discipline ("Any Branch" & Open Degree Aware)
    # ------------------------------------------------------------------
    def _evaluate_branch(
        self,
        job: JobExtractionSchema,
        matched_qual: Optional[str] = None,
        post_name: Optional[str] = None
    ) -> EligibilityCriterionResult:
        # 1. Open graduation check
        if matched_qual and is_open_graduation_requirement(matched_qual):
            return EligibilityCriterionResult(
                status="PASS",
                details=f"Open qualification '{matched_qual}' accepts graduates from any branch/discipline",
                extracted_value=job.accepted_branches or ["Any Branch"],
                required_value=self.profile.education.branches,
            )

        # 2. General administrative/clerical post check
        p_name = (post_name or job.post_name or "").lower()
        if any(re.search(pat, p_name) for pat in _GENERAL_GRADUATE_POST_TITLES) and not job.accepted_branches:
            return EligibilityCriterionResult(
                status="PASS",
                details=f"Administrative/Clerical post '{post_name or job.post_name}' does not restrict by branch",
                extracted_value="Any Discipline",
                required_value=self.profile.education.branches,
            )

        # 3. Extract all declared or detected engineering disciplines from accepted_branches, post name, qualification, conditions
        candidate_branches = self.profile.education.branches
        branch_mappings = getattr(self.profile, "branch_mappings", {}) or {}

        raw_branches = list(job.accepted_branches or [])
        text_corpus = f"{post_name or job.post_name or ''} {' '.join(job.qualification or [])} {' '.join(job.important_conditions or [])}"
        detected_disciplines = extract_disciplines_from_text(text_corpus)

        all_disciplines_set = set(raw_branches)
        for disc in detected_disciplines:
            all_disciplines_set.add(disc)

        # 4. If explicit disciplines or branches are specified
        if all_disciplines_set:
            # First check if the job accepts any discipline or candidate's branch
            is_match, match_reason = branches_overlap(list(all_disciplines_set), candidate_branches)
            if is_match:
                return EligibilityCriterionResult(
                    status="PASS",
                    details=f"Branch matched: {match_reason}",
                    extracted_value=list(all_disciplines_set),
                    required_value=candidate_branches,
                )

            # Job requires specific branch(es), none of which match candidate's branches.
            # Inspect candidate's branch strictness mapping (ACCEPT, POSSIBLY_ACCEPT, DO_NOT_ACCEPT)
            disqualified_disciplines = []
            possible_disciplines = []
            for disc in all_disciplines_set:
                mapped_strictness = None
                for b_key, b_mode in branch_mappings.items():
                    if b_key.lower() in disc.lower() or disc.lower() in b_key.lower():
                        mapped_strictness = b_mode
                        break
                if mapped_strictness == "DO_NOT_ACCEPT":
                    disqualified_disciplines.append(disc)
                elif mapped_strictness == "POSSIBLY_ACCEPT":
                    possible_disciplines.append(disc)

            if disqualified_disciplines:
                return EligibilityCriterionResult(
                    status="FAIL",
                    details=(
                        f"Required branch(es) {disqualified_disciplines} are explicitly set to EXCLUDE "
                        f"(DO_NOT_ACCEPT) in your branch strictness matrix."
                    ),
                    extracted_value=list(all_disciplines_set),
                    required_value=f"Excluded: {disqualified_disciplines}",
                )

            if possible_disciplines:
                return EligibilityCriterionResult(
                    status="UNKNOWN",
                    details=(
                        f"Required branch(es) {possible_disciplines} are marked as POSSIBLY_ACCEPT. "
                        f"Manual verification required to confirm if CSE degree is accepted as equivalent."
                    ),
                    extracted_value=list(all_disciplines_set),
                    required_value=f"Possibly accepted: {possible_disciplines}",
                )

            # Default: Required branches do not match candidate's branches
            return EligibilityCriterionResult(
                status="FAIL",
                details=(
                    f"Required branches {list(all_disciplines_set)} do not match "
                    f"your branches {candidate_branches}"
                ),
                extracted_value=list(all_disciplines_set),
                required_value=candidate_branches,
            )

        # 5. If no specific disciplines were detected:
        # Check if user accepts 'Any Branch'
        user_branches_lower = [b.lower().strip() for b in candidate_branches]
        if any(b in ANY_BRANCH_PHRASES for b in user_branches_lower):
            return EligibilityCriterionResult(
                status="PASS",
                details="Your profile accepts Any Branch and notification does not restrict branches",
                extracted_value="Open / Unrestricted",
                required_value="Any Branch",
            )

        # If post clearly requires specialized technical engineering (e.g. B.Tech), but no branches listed
        if matched_qual and ("b.tech" in matched_qual.lower() or "engineering" in matched_qual.lower()):
            return EligibilityCriterionResult(
                status="UNKNOWN",
                details="Engineering degree required, but specific branches not stated in notification excerpt",
                extracted_value=None,
                required_value=candidate_branches,
            )

        # Default fallback when branches are omitted
        return EligibilityCriterionResult(
            status="UNKNOWN",
            details="Specific degree branches not specified in excerpt; verify official notification",
            extracted_value=None,
            required_value=candidate_branches,
        )

    # ------------------------------------------------------------------
    # CRITERION 7: Percentage / CGPA
    # ------------------------------------------------------------------
    def _evaluate_percentage(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        if job.minimum_percentage is None:
            return EligibilityCriterionResult(
                status="PASS",
                details="No minimum percentage/CGPA requirement stated in notification",
                extracted_value=None,
                required_value="Not required",
            )

        user_pct = self.profile.education.minimum_percentage
        if user_pct is None or user_pct == 0.0:
            edu_hist = getattr(self.profile, "education_history", None)
            cgpa = getattr(edu_hist, "graduation_cgpa", None) if edu_hist else None
            if cgpa:
                user_pct = round(cgpa * 9.5, 2)
            else:
                records = getattr(self.profile, "education_records", []) or []
                for r in records:
                    if getattr(r, "level", "") in ("bachelors", "graduation", "degree"):
                        if getattr(r, "percentage", None):
                            user_pct = r.percentage
                            break
                        elif getattr(r, "cgpa", None):
                            user_pct = round(r.cgpa * 9.5, 2)
                            break
        user_pct = user_pct or 0.0
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
    # CRITERION 8: Location
    # ------------------------------------------------------------------
    def _evaluate_location(self, job: JobExtractionSchema) -> EligibilityCriterionResult:
        job_locs = [loc.lower().strip() for loc in (job.location or [])]
        user_allowed = [loc.lower().strip() for loc in (self.profile.location.allowed or ["All India"])]
        user_excluded = [loc.lower().strip() for loc in (self.profile.location.exclude_locations or [])]

        # 1. Excluded locations
        for jloc in job_locs:
            for ex in user_excluded:
                if ex in jloc or jloc in ex:
                    return EligibilityCriterionResult(
                        status="FAIL",
                        details=f"Job location '{jloc}' matches your excluded location '{ex}'",
                        extracted_value=job.location,
                        required_value=f"Exclude {self.profile.location.exclude_locations}",
                    )

        # 2. Open across India
        if any(open_loc in user_allowed for open_loc in ["all india", "india", "any"]):
            return EligibilityCriterionResult(
                status="PASS",
                details="Location matches your preference (All India accepted)",
                extracted_value=job.location or ["All India"],
                required_value="All India",
            )

        # 3. Unspecified or nationwide
        if not job_locs or any(loc in ["all india", "india", "nationwide", "across india"] for loc in job_locs):
            return EligibilityCriterionResult(
                status="PASS",
                details="Job is open across India / location unspecified",
                extracted_value=job.location or ["All India"],
                required_value=self.profile.location.allowed,
            )

        # 4. State match
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

    # ------------------------------------------------------------------
    # CRITERION 9: Intermediate & School Subjects (10th/12th Specifics)
    # ------------------------------------------------------------------
    def _evaluate_subjects(self, job: JobExtractionSchema, post_name: Optional[str] = None) -> EligibilityCriterionResult:
        inter_subs = " ".join(getattr(job, "intermediate_subjects", []) or [])
        full_text = f"{post_name or job.post_name or ''} {' '.join(job.qualification or [])} {' '.join(job.important_conditions or [])} {inter_subs}".lower()
        subs = getattr(self.profile, "subjects_10_12", None)
        if not subs:
            return EligibilityCriterionResult(status="PASS", details="Intermediate subject requirements unstated or not applicable")

        # Mathematics requirement in 10+2 / Intermediate
        math_keywords = ["10+2 with maths", "10+2 with mathematics", "12th with maths", "12th with mathematics", "mathematics at 10+2", "mathematics in 12th", "maths at 10+2", "studied mathematics"]
        has_math_req = any(kw in full_text for kw in math_keywords) or (
            "mathematics" in full_text and ("12th" in full_text or "10+2" in full_text or "intermediate" in full_text)
        )
        if has_math_req:
            if not subs.studied_maths_12th:
                return EligibilityCriterionResult(
                    status="FAIL",
                    details="Position mandates Mathematics at 10+2 level; candidate profile indicates Mathematics was not studied",
                    extracted_value="10+2 with Mathematics",
                    required_value=True
                )

        # Physics requirement in 10+2
        physics_keywords = ["10+2 with physics", "12th with physics", "physics at 10+2", "physics in 12th"]
        has_phys_req = any(kw in full_text for kw in physics_keywords) or (
            "physics" in full_text and ("12th" in full_text or "10+2" in full_text or "intermediate" in full_text)
        )
        if has_phys_req:
            if not subs.studied_physics_12th:
                return EligibilityCriterionResult(
                    status="FAIL",
                    details="Position mandates Physics at 10+2 level; candidate profile indicates Physics was not studied",
                    extracted_value="10+2 with Physics",
                    required_value=True
                )

        return EligibilityCriterionResult(status="PASS", details="10+2 and school subject requirements satisfied")

    # ------------------------------------------------------------------
    # CRITERION 10: Physical Standards (Height, Chest Measurements)
    # ------------------------------------------------------------------
    def _evaluate_physical_standards(self, job: JobExtractionSchema, post_name: Optional[str] = None) -> EligibilityCriterionResult:
        conds = ' '.join(job.important_conditions or [])
        sel = ' '.join(job.selection_process or [])
        short_desc = getattr(job, "short_description", "") or ""
        phys_details = getattr(job, "physical_test_details", "") or ""
        full_text = f"{post_name or job.post_name or ''} {' '.join(job.qualification or [])} {conds} {sel} {phys_details} {short_desc}".lower()
        phys = getattr(self.profile, "physical", None)
        if not phys:
            return EligibilityCriterionResult(status="PASS", details="Physical measurement criteria not applicable")

        # Check for explicit height requirement (e.g., minimum height 170 cm)
        m = re.search(r"(?:minimum\s*height(?:\s*required)?|height\s*(?:requirement|min|criteria)?|height\s*:\s*)\s*(?:of\s*)?[:\s-]*(\d{3})\s*(?:cm)?", full_text)
        if m and phys.height_cm:
            try:
                req_height = float(m.group(1))
                if phys.height_cm < req_height:
                    return EligibilityCriterionResult(
                        status="FAIL",
                        details=f"Your height ({phys.height_cm} cm) is below mandatory minimum standard ({req_height} cm)",
                        extracted_value=f"{req_height} cm",
                        required_value=f"{phys.height_cm} cm"
                    )
            except Exception:
                pass

        return EligibilityCriterionResult(status="PASS", details="Physical measurement criteria satisfied or unstated")

    # ------------------------------------------------------------------
    # 4-TIER PREFERENCES, CONSTRAINTS & READINESS ENRICHMENT
    # ------------------------------------------------------------------
    def _enrich_with_preferences_and_constraints(
        self, job: JobExtractionSchema, decision: EligibilityDecision
    ) -> EligibilityDecision:
        """
        Enriches hard eligibility verdict with Personal Preferences and Application Constraints.
        Determines preference_status: 'WANT_TO_APPLY', 'MAYBE', or 'NOT_INTERESTED'.
        Synthesizes combined_status:
          - NOT_ELIGIBLE  -> 'NOT_ELIGIBLE'
          - UNCERTAIN     -> 'UNCERTAIN'
          - ELIGIBLE      -> 'ELIGIBLE + WANT TO APPLY' | 'ELIGIBLE + MAYBE' | 'ELIGIBLE + NOT INTERESTED'
        """
        pref_status = "MAYBE"
        pref_breakdown: Dict[str, Any] = {}
        constraints_warnings: List[str] = []

        post_title = (job.post_name or "").lower()
        org_name = (job.organization or "").lower()
        quals_str = " ".join(job.qualification or []).lower()
        branches_str = " ".join(job.accepted_branches or []).lower()
        conditions_str = " ".join(job.important_conditions or []).lower()
        full_context = f"{post_title} {org_name} {quals_str} {branches_str} {conditions_str}"

        # 1. Organization Checks
        avoid_orgs = getattr(self.profile, "avoid_organizations", []) or []
        matched_avoid_org = next((o for o in avoid_orgs if o.lower() in org_name), None)
        if matched_avoid_org:
            pref_breakdown["avoid_organization"] = f"Organization '{matched_avoid_org}' is on your avoided list."
            pref_status = "NOT_INTERESTED"

        pref_orgs = getattr(self.profile, "preferred_organizations", []) or []
        matched_pref_org = next((o for o in pref_orgs if o.lower() in org_name), None)
        if matched_pref_org:
            pref_breakdown["preferred_organization"] = f"Issued by prioritized organization: {matched_pref_org}"

        # 2. Role & Security Checks
        role_prefs = getattr(self.profile, "role_preferences", None)
        if role_prefs:
            # A. Avoided Roles
            for avoid_r in role_prefs.avoid_roles:
                keywords = [k.strip().lower() for k in avoid_r.replace("/", ",").split(",") if k.strip()]
                if any(kw in post_title for kw in keywords):
                    pref_breakdown["avoid_role"] = f"Role matches avoided category: {avoid_r}"
                    pref_status = "NOT_INTERESTED"
                    break

            # B. Preferred Roles
            matched_pref_roles = []
            for pref_r in role_prefs.preferred_roles:
                pr_lower = pref_r.lower()
                keywords = [k.strip().lower() for k in pref_r.replace("/", ",").split(",") if k.strip()]
                if any(kw in post_title for kw in keywords):
                    matched_pref_roles.append(pref_r)
                elif "technical" in pr_lower and any(k in post_title for k in ["engineer", "developer", "technical", "scientific", "analyst", "programmer", "technician"]):
                    matched_pref_roles.append("Technical")
                elif "software" in pr_lower and any(k in post_title for k in ["software", "it ", "programmer", "developer", "computer", "system"]):
                    matched_pref_roles.append("Software / IT")
                elif "administration" in pr_lower and any(k in post_title for k in ["assistant", "clerk", "officer", "executive", "admin", "section controller", "manager"]):
                    matched_pref_roles.append("Administration")

            if matched_pref_roles:
                pref_breakdown["preferred_role"] = f"Matches preferred role domain: {', '.join(set(matched_pref_roles))}"

            # C. Work Nature Check
            if role_prefs.work_nature == "desk_only":
                if any(w in post_title for w in ["patrol", "field officer", "constable", "driver", "outdoor", "traffic", "jail warder"]):
                    constraints_warnings.append("Role involves field/outdoor duties; candidate prefers desk-only work.")
                    if pref_status != "NOT_INTERESTED":
                        pref_status = "MAYBE"

            # D. Job Security (Permanent vs Contract / Apprenticeship)
            if role_prefs.job_security_preference == "permanent_only":
                is_temporary = (
                    (job.job_type in ["contract", "temporary", "apprenticeship", "internship"]) or
                    any(w in post_title for w in ["apprentice", "contract", "temporary", "short service", "adhoc", "ad-hoc", "fixed term"])
                )
                if is_temporary:
                    pref_breakdown["job_tenure"] = "Non-permanent or contract/apprenticeship opportunity; user prefers permanent positions."
                    pref_status = "NOT_INTERESTED"

        # 3. Application Constraints
        constraints = getattr(self.profile, "constraints", None)
        if constraints:
            # A. Physical Tests / PET / PMT
            has_physical_req = False
            phys_keywords = [
                "physical efficiency", "physical test", "running test", "pet/pmt",
                "physical measurement", "long jump", "high jump", "chest measurement",
                "height measurement", "endurance test"
            ]
            if any(pk in full_context for pk in phys_keywords):
                has_physical_req = True
            elif any(w in post_title for w in ["constable", "sub inspector", "police", "forest guard", "jail warder", "fireman"]):
                has_physical_req = True

            if has_physical_req:
                if not constraints.willing_physical_tests:
                    constraints_warnings.append("Notification specifies physical tests (running/PET/PMT); user preference is desk/no-physical tests.")
                    if pref_status == "WANT_TO_APPLY":
                        pref_status = "MAYBE"
                    elif any(w in post_title for w in ["constable", "jail warder", "fireman"]):
                        pref_status = "NOT_INTERESTED"

            # B. Application Fee Limit
            user_fee_limit = constraints.max_application_fee or self.profile.max_application_fee
            if user_fee_limit is not None and job.application_fee:
                user_category = self.profile.age.category.upper() if self.profile.age else "GENERAL"
                fee_text = " ".join(job.application_fee).lower()
                is_exempt = False
                if any(c in user_category for c in ["SC", "ST", "PWD", "WOMEN", "FEMALE"]):
                    if any(term in fee_text for term in ["sc/st: nil", "sc/st: exempted", "women/sc/st: nil", "exempted", "free", "no fee"]):
                        is_exempt = True
                
                if not is_exempt:
                    fee_nums = [int(n) for n in re.findall(r"(?:rs\.?|inr|₹)\s*(\d+)", fee_text)]
                    if fee_nums:
                        min_fee_found = min(fee_nums)
                        if min_fee_found > user_fee_limit:
                            constraints_warnings.append(f"Application fee (₹{min_fee_found}) exceeds maximum limit (₹{user_fee_limit}).")
                            if constraints.exclude_high_fee_jobs:
                                pref_status = "NOT_INTERESTED"
                            elif pref_status == "WANT_TO_APPLY":
                                pref_status = "MAYBE"

            # C. Service Bond
            if not constraints.service_bond_acceptable:
                if any("bond" in cond.lower() or "service agreement" in cond.lower() for cond in (job.important_conditions or [])):
                    constraints_warnings.append("Mandatory service bond or surety agreement required.")
                    if pref_status == "WANT_TO_APPLY":
                        pref_status = "MAYBE"

            # D. Travel Distance for Exams / Relocation
            personal = getattr(self.profile, "personal", None)
            if personal and not personal.willing_to_relocate_all_india:
                pref_states = personal.preferred_relocation_states or []
                if pref_states and job.location and not any(loc in pref_states or loc in ["All India", "India"] for loc in job.location):
                    constraints_warnings.append(f"Posting/Exam in {', '.join(job.location)} outside preferred states.")
                    if pref_status == "WANT_TO_APPLY":
                        pref_status = "MAYBE"

        # 4. Synthesize Final Preference Status
        if pref_status != "NOT_INTERESTED":
            has_positive = ("preferred_organization" in pref_breakdown) or ("preferred_role" in pref_breakdown)
            if has_positive and not constraints_warnings:
                pref_status = "WANT_TO_APPLY"
            elif has_positive and len(constraints_warnings) <= 1:
                pref_status = "WANT_TO_APPLY"
            elif not has_positive and not constraints_warnings:
                if any(k in post_title for k in ["engineer", "assistant", "officer", "clerk", "developer", "scientist", "trainee"]):
                    pref_status = "WANT_TO_APPLY"
                else:
                    pref_status = "MAYBE"
            else:
                pref_status = "MAYBE"

        # 5. Tier D: Application Readiness Check
        readiness_status = "READY"
        readiness_warnings: List[str] = []
        docs = getattr(self.profile, "documents_readiness", {}) or {}

        # A. EWS Document Check
        user_cat = (self.profile.age.category if self.profile.age else "General").upper()
        if "EWS" in user_cat:
            ews_doc = docs.get("caste_ews_cert")
            if ews_doc:
                if ews_doc.status in ["EXPIRED", "RENEWAL_REQUIRED"]:
                    readiness_warnings.append("EWS Certificate validity expired or needs renewal for current financial year.")
                    readiness_status = "WARNING"
                elif ews_doc.status == "NOT_AVAILABLE":
                    readiness_warnings.append("EWS Certificate not available; required for availing EWS reservation quota.")
                    readiness_status = "MISSING_DOCUMENTS"

        # B. Driving Licence Check (if required by job)
        if any(term in full_context for term in ["driving licence", "driving license", "lmv licence", "lmv license", "driver"]):
            dl_doc = docs.get("driving_licence")
            has_dl = getattr(getattr(self.profile, "education_history", None), "has_driving_licence", False)
            if not has_dl or (dl_doc and dl_doc.status in ["NOT_AVAILABLE", "NOT_APPLICABLE"]):
                readiness_warnings.append("Valid driving licence (LMV/HMV) required for this position.")
                readiness_status = "MISSING_DOCUMENTS"
            elif dl_doc and dl_doc.status in ["EXPIRED", "RENEWAL_REQUIRED"]:
                readiness_warnings.append("Driving licence requires renewal before the application cutoff date.")
                readiness_status = "WARNING"

        # C. Experience Certificate Check (if experience required)
        if job.experience_required:
            exp_doc = docs.get("experience_cert")
            if exp_doc and exp_doc.status in ["NOT_AVAILABLE", "NOT_APPLICABLE"]:
                readiness_warnings.append("Formal experience certificate / service letter required from employer.")
                if readiness_status != "MISSING_DOCUMENTS":
                    readiness_status = "WARNING"

        # D. NOC Check (for employed candidates)
        has_current_job = any(getattr(exp, "is_current", False) for exp in getattr(self.profile, "experience_records", []))
        if has_current_job:
            noc_doc = docs.get("noc")
            if noc_doc and noc_doc.status in ["NOT_AVAILABLE", "NOT_APPLICABLE"]:
                readiness_warnings.append("No Objection Certificate (NOC) required from current employer before interview.")
                if readiness_status == "READY":
                    readiness_status = "WARNING"

        # 6. Compute Combined Status
        if decision.status == "NOT_ELIGIBLE":
            combined_status = "NOT_ELIGIBLE"
        elif decision.status == "UNCERTAIN":
            combined_status = "UNCERTAIN"
        else:  # ELIGIBLE
            combined_status = f"ELIGIBLE + {pref_status.replace('_', ' ')}"

        decision.preference_status = pref_status
        decision.readiness_status = readiness_status
        decision.combined_status = combined_status
        decision.preference_breakdown = pref_breakdown
        decision.constraints_warnings = constraints_warnings
        decision.readiness_warnings = readiness_warnings
        return decision

