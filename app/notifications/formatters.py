"""
Telegram Alert Notification Formatters
Constructs rich, structured Markdown messages for:
- 🚨 ELIGIBLE JOB
- 🟡 POSSIBLE MATCH — VERIFY (UNCERTAIN)
Never converts unverified claims into official fact.
"""
from typing import Optional
from app.ai.schemas import JobExtractionSchema
from app.eligibility.models import EligibilityDecision
from app.content.normalizer import NormalizedContent


def format_eligible_job_alert(
    job: JobExtractionSchema,
    decision: EligibilityDecision,
    content: Optional[NormalizedContent] = None
) -> str:
    """
    Constructs the 🚨 ELIGIBLE JOB alert specified in Section 21 of the Master Specification.
    """
    org = job.organization or "Government Organization"
    post = job.post_name or "Recruitment Post"
    vacancies = str(job.vacancies) if job.vacancies is not None else "Not Specified"
    quals = ", ".join(job.qualification) if job.qualification else "Refer notification"
    branches = ", ".join(job.accepted_branches) if job.accepted_branches else "All/Specified branches"
    age = f"{job.age_min or 18} to {job.age_max or 'Max'} years" if job.age_max else "Refer notification"
    exp = f"{job.experience_years_min or 0} years" if job.experience_required else "Freshers Eligible / No Experience"
    salary = job.salary or job.pay_level or "As per Govt Rules"
    locations = ", ".join(job.location) if job.location else "All India"
    app_start = job.application_start or "Check official link"
    app_end = job.application_deadline or "Check official link"
    selection = ", ".join(job.selection_process) if job.selection_process else "Written Exam / Interview"
    fees = ", ".join(job.application_fee) if job.application_fee else "Refer notification"

    lines = [
        "🚨 *ELIGIBLE GOVERNMENT JOB ALERT*",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"🏛 *Organization:* {org}",
        f"📋 *Post:* {post}",
        f"🔢 *Vacancies:* {vacancies}",
        "",
        f"🎓 *Qualification:* {quals} ({branches})",
        f"🎂 *Age Limit:* {age}",
        f"💼 *Experience:* {exp}",
        f"💰 *Salary / Pay Level:* {salary}",
        f"📍 *Location:* {locations}",
        "",
        f"📅 *Application Start:* {app_start}",
        f"⏳ *Application Deadline:* {app_end}",
        "",
        f"📝 *Selection Process:* {selection}",
        f"💳 *Application Fee:* {fees}",
        "",
        "🎯 *Why You Are Eligible:*",
    ]

    # Include eligibility breakdown
    for k, v in decision.criteria.items():
        if v.status == "PASS":
            lines.append(f"  • *{k.replace('_', ' ').capitalize()}:* {v.details}")

    lines.append("")

    # Source & Links
    pdf_link = job.official_notification_url or (content.pdf_url if content else None)
    apply_link = job.official_apply_url or (content.canonical_url if content else None)

    if pdf_link:
        lines.append(f"📄 *Official Notification PDF:* [Download Here]({pdf_link})")
    if apply_link:
        lines.append(f"🔗 *Apply Online Portal:* [Click to Apply]({apply_link})")

    verif_status = content.verification_status if content else "unverified"
    source_type = content.source_type if content else "secondary"
    lines.append(f"🛡 *Source Status:* `{source_type.upper()}` ({verif_status.upper()})")

    lines.append("")
    lines.append("⚠️ *Important Note:* Verify the official notification thoroughly before applying.")
    return "\n".join(lines)


def format_uncertain_job_alert(
    job: JobExtractionSchema,
    decision: EligibilityDecision,
    content: Optional[NormalizedContent] = None
) -> str:
    """
    Constructs the 🟡 POSSIBLE MATCH — VERIFY alert specified in Section 22.
    """
    org = job.organization or "Government Department"
    post = job.post_name or "Recruitment Post"

    lines = [
        "🟡 *POSSIBLE MATCH — VERIFY REQUIRED*",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"🏛 *Organization:* {org}",
        f"📋 *Post:* {post}",
        "",
        "✅ *What Matched:*",
    ]

    for k, v in decision.criteria.items():
        if v.status == "PASS":
            lines.append(f"  • *{k.replace('_', ' ').capitalize()}:* {v.details}")

    lines.append("")
    lines.append("⚠️ *What Requires Manual Verification (UNKNOWN):*")

    for k, v in decision.criteria.items():
        if v.status == "UNKNOWN":
            lines.append(f"  • *{k.replace('_', ' ').capitalize()}:* {v.details}")

    lines.append("")

    pdf_link = job.official_notification_url or (content.pdf_url if content else None)
    apply_link = job.official_apply_url or (content.canonical_url if content else None)

    if pdf_link:
        lines.append(f"📄 *Official Notification PDF:* [Download & Verify]({pdf_link})")
    if apply_link:
        lines.append(f"🔗 *Portal Link:* [Visit Portal]({apply_link})")

    lines.append("")
    lines.append("ℹ️ *Reason:* Key eligibility terms are ambiguous in the circular excerpt.")
    return "\n".join(lines)
