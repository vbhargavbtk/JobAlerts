import html
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
    Constructs the 🚨 ELIGIBLE JOB alert using clean HTML formatting.
    """
    org = html.escape(job.organization or "Government Organization")
    post = html.escape(job.post_name or "Recruitment Post")
    vacancies = str(job.vacancies) if job.vacancies is not None else "Not Specified"
    age = html.escape(f"{job.age_min or 18} to {job.age_max or 'Max'} years" if job.age_max else "Refer notification")
    exp = html.escape(f"{job.experience_years_min or 0} years" if job.experience_required else "Freshers Eligible / No Experience")
    salary = html.escape(job.salary or job.pay_level or "As per Govt Rules")
    locations = html.escape(", ".join(job.location) if job.location else "All India")
    app_start = html.escape(job.application_start or "Check official link")
    app_end = html.escape(job.application_deadline or "Check official link")
    selection = html.escape(", ".join(job.selection_process) if job.selection_process else "Written Exam / Interview")
    fees = html.escape(", ".join(job.application_fee) if job.application_fee else "Refer notification")

    lines = [
        "🚨 <b>ELIGIBLE GOVERNMENT JOB ALERT</b>",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"🏛 <b>Organization:</b> {org}",
        f"📋 <b>Post:</b> {post}",
        f"🔢 <b>Vacancies:</b> {vacancies}",
        "",
        f"💼 <b>Experience:</b> {exp}",
        f"🎂 <b>Age Limit:</b> {age}",
        f"💰 <b>Salary / Pay Level:</b> {salary}",
        f"📍 <b>Location:</b> {locations}",
        "",
        f"📅 <b>Application Start:</b> {app_start}",
        f"⏳ <b>Application Deadline:</b> {app_end}",
        "",
        f"📝 <b>Selection Process:</b> {selection}",
        f"💳 <b>Application Fee:</b> {fees}",
        "",
        "🎯 <b>Why You Are Eligible:</b>",
    ]

    # Include eligibility breakdown (excluding qualification)
    for k, v in decision.criteria.items():
        if v.status == "PASS" and k != "qualification":
            clean_k = html.escape(k.replace('_', ' ').capitalize())
            clean_det = html.escape(str(v.details))
            lines.append(f"  • <b>{clean_k}:</b> {clean_det}")

    lines.append("")

    # Source & Links
    pdf_link = job.official_notification_url or (content.pdf_url if content else None)
    apply_link = job.official_apply_url or (content.canonical_url if content else None)

    if pdf_link:
        lines.append(f'📄 <b>Official Notification PDF:</b> <a href="{pdf_link}">Download PDF</a>')
    if apply_link:
        lines.append(f'🔗 <b>Apply Online Portal:</b> <a href="{apply_link}">Click to Apply</a>')

    verif_status = content.verification_status if content else "unverified"
    source_type = content.source_type if content else "secondary"
    lines.append(f"🛡 <b>Source Status:</b> <code>{source_type.upper()} ({verif_status.upper()})</code>")

    lines.append("")
    lines.append("⚠️ <b>Important Note:</b> Verify the official notification thoroughly before applying.")
    return "\n".join(lines)


def format_uncertain_job_alert(
    job: JobExtractionSchema,
    decision: EligibilityDecision,
    content: Optional[NormalizedContent] = None
) -> str:
    """
    Constructs the 🟡 POSSIBLE MATCH — VERIFY alert using clean HTML formatting.
    """
    org = html.escape(job.organization or "Government Department")
    post = html.escape(job.post_name or "Recruitment Post")

    lines = [
        "🟡 <b>POSSIBLE MATCH — VERIFY REQUIRED</b>",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"🏛 <b>Organization:</b> {org}",
        f"📋 <b>Post:</b> {post}",
        "",
        "✅ <b>What Matched:</b>",
    ]

    for k, v in decision.criteria.items():
        if v.status == "PASS" and k != "qualification":
            clean_k = html.escape(k.replace('_', ' ').capitalize())
            clean_det = html.escape(str(v.details))
            lines.append(f"  • <b>{clean_k}:</b> {clean_det}")

    lines.append("")
    lines.append("⚠️ <b>What Requires Manual Verification (UNKNOWN):</b>")

    for k, v in decision.criteria.items():
        if v.status == "UNKNOWN" and k != "qualification":
            clean_k = html.escape(k.replace('_', ' ').capitalize())
            clean_det = html.escape(str(v.details))
            lines.append(f"  • <b>{clean_k}:</b> {clean_det}")

    lines.append("")

    pdf_link = job.official_notification_url or (content.pdf_url if content else None)
    apply_link = job.official_apply_url or (content.canonical_url if content else None)

    if pdf_link:
        lines.append(f'📄 <b>Official Notification PDF:</b> <a href="{pdf_link}">Download &amp; Verify</a>')
    if apply_link:
        lines.append(f'🔗 <b>Portal Link:</b> <a href="{apply_link}">Visit Portal</a>')

    lines.append("")
    lines.append("ℹ️ <b>Reason:</b> Key eligibility terms are ambiguous in the circular excerpt.")
    return "\n".join(lines)
