"""
Message Intelligence & Fallback Fusion
Extracts and fuses structured recruitment facts from Telegram announcement text
when secondary aggregators or official PDFs omit them.
"""
import re
import logging
from typing import Optional
from app.ai.schemas import JobExtractionSchema
from app.eligibility.normalization import is_non_job_announcement

logger = logging.getLogger(__name__)


def fuse_message_text_if_needed(job: JobExtractionSchema, message_text: Optional[str]) -> JobExtractionSchema:
    """
    Scans the raw message text for recruitment parameters that the AI or web crawler
    omitted (e.g., qualification, branches, age limits, fresher status, vacancies).
    """
    if not message_text or not message_text.strip():
        return job

    text = message_text.strip()

    # 1. Non-Job Check
    if job.is_job and is_non_job_announcement(job.post_name, text, None):
        job.is_job = False
        return job

    # 2. Organization Fallback
    if not job.organization or job.organization.lower() in ("unknown", "recruitment"):
        org_match = re.search(r"^(?:🔥|📢|✅|‼️)?\s*([A-Z][A-Za-z0-9\s&,–\-\(\)]{3,50}?)\s+(?:Recruitment|Notification|CEN|Vacanc|Examination)", text, re.MULTILINE)
        if org_match:
            job.organization = org_match.group(1).strip()

    # 3. Post Name Fallback
    if not job.post_name or job.post_name.lower() in ("recruitment notification", "various posts", "none"):
        post_match = re.search(r"(?:Posts?|Designation|Position|Vacancies\s+for):\s*([^\n]+)", text, re.IGNORECASE)
        if post_match:
            job.post_name = post_match.group(1).strip()

    # 4. Vacancies Fallback
    if job.vacancies is None:
        vac_match = re.search(r"(?:Vacancies|Total\s+Posts?|No\.\s+of\s+Posts?):\s*([0-9,]+)", text, re.IGNORECASE)
        if vac_match:
            try:
                job.vacancies = int(vac_match.group(1).replace(",", ""))
            except ValueError:
                pass

    # 5. Qualification Fallback
    if not job.qualification:
        qual_match = re.search(r"(?:Qualification|Eligibility|Edu(?:cation)?\s*Qual(?:ification)?):\s*([^\n]+)", text, re.IGNORECASE)
        if qual_match:
            raw_qual = qual_match.group(1).strip()
            # Split by slashes, commas, or 'or'
            parts = [q.strip() for q in re.split(r"[/,]|(?:\s+or\s+)", raw_qual) if len(q.strip()) > 1]
            job.qualification = parts if parts else [raw_qual]

    # 6. Accepted Branches Fallback
    if not job.accepted_branches:
        # Check inside post_name or text for parenthesized engineering branches, e.g., (Civil, Mechanical, Electrical, E&T)
        branch_match = re.search(r"\((Civil|Mechanical|Electrical|Electronics|CSE|IT|CS|E&T|ETC|Chemical)[^)]*\)", text, re.IGNORECASE)
        if branch_match:
            raw_branches = branch_match.group(0).strip("()")
            # Split only on commas, or 'and'/'&' surrounded by whitespace so acronyms like E&T, AI&ML are preserved
            b_list = [b.strip() for b in re.split(r",|\s+and\s+|\s+&\s+", raw_branches) if len(b.strip()) > 1]
            if b_list:
                job.accepted_branches = b_list
        else:
            # Check for discipline lines
            disc_match = re.search(r"(?:Branches?|Disciplines?|Streams?):\s*([^\n]+)", text, re.IGNORECASE)
            if disc_match:
                raw_b = disc_match.group(1).strip()
                job.accepted_branches = [b.strip() for b in re.split(r",|\s+and\s+|\s+&\s+", raw_b) if len(b.strip()) > 1]

    # 7. Age Limits Fallback
    if job.age_max is None:
        age_range_match = re.search(r"(?:Age\s+Limit|Age):\s*(\d{2})\s*(?:to|-)\s*(\d{2})\s*years?", text, re.IGNORECASE)
        if age_range_match:
            job.age_min = int(age_range_match.group(1))
            job.age_max = int(age_range_match.group(2))
        else:
            max_age_match = re.search(r"(?:Max(?:imum)?\s+Age|Upper\s+Age\s+Limit|Age\s+Limit):\s*(?:Up\s+to\s+)?(\d{2})\s*years?", text, re.IGNORECASE)
            if max_age_match:
                job.age_max = int(max_age_match.group(1))

    # 8. Experience & Freshers Fallback
    if job.experience_required is None:
        if re.search(r"\b(freshers?\s*(?:can\s*apply|eligible)|no\s*experience\s*required|0\s*years?\s*exp)\b", text, re.IGNORECASE):
            job.experience_required = False
            job.experience_years_min = 0
        elif re.search(r"\b(\d+)\+?\s*years?\s*(?:of\s*)?exp(?:erience)?\s*required\b", text, re.IGNORECASE):
            m = re.search(r"\b(\d+)\+?\s*years?\s*(?:of\s*)?exp(?:erience)?\s*required\b", text, re.IGNORECASE)
            job.experience_required = True
            job.experience_years_min = int(m.group(1)) if m else 1

    return job
