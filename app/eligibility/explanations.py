"""
Eligibility Explanations Generator
Formats clean, human-readable, structured verification breakdowns for alerts,
auditing, and web dashboard displays.
"""
from typing import Dict
from app.eligibility.models import EligibilityDecision, EligibilityCriterionResult


def format_eligibility_explanation(decision: EligibilityDecision) -> str:
    """
    Produces structured, transparent breakdown matching the specification:
    - ELIGIBLE: Verified criteria and post breakdowns
    - NOT_ELIGIBLE: Explicit blocking constraints
    - UNCERTAIN: Exact missing evidence declared
    """
    lines = []
    lines.append(f"*Eligibility Verdict:* `{decision.status}`\n")

    # If multi-post breakdown exists
    if decision.posts:
        lines.append("*Post-Wise Eligibility Breakdown:*")
        for p_name, p_res in decision.posts.items():
            icon = "✓" if p_res.status == "ELIGIBLE" else ("✗" if p_res.status == "NOT_ELIGIBLE" else "⚠")
            lines.append(f"  {icon} *{p_name}:* `{p_res.status}` — {p_res.details}")
        lines.append("")

    if decision.status == "ELIGIBLE":
        lines.append("*Passed Criteria:*")
        for key, res in decision.criteria.items():
            if res.status == "PASS":
                title = key.replace("_", " ").capitalize()
                lines.append(f"  ✓ *{title}:* {res.details}")

    elif decision.status == "NOT_ELIGIBLE":
        lines.append("*Blocking Ineligibility Criteria:*")
        for key, res in decision.criteria.items():
            if res.status == "FAIL":
                title = key.replace("_", " ").capitalize()
                lines.append(f"  ✗ *{title}:* {res.details}")
        
        # Show other criteria status briefly
        passed = [k.replace('_', ' ').capitalize() for k, v in decision.criteria.items() if v.status == "PASS"]
        if passed:
            lines.append(f"\n_Satisfied criteria:_ {', '.join(passed)}")

    else:  # UNCERTAIN / REVIEW
        lines.append("*Unresolved / Missing Criteria:*")
        for key, res in decision.criteria.items():
            if res.status == "UNKNOWN":
                title = key.replace("_", " ").capitalize()
                lines.append(f"  ⚠ *{title}:* {res.details}")

        lines.append("\n*Missing Evidence Required:*")
        for key, res in decision.criteria.items():
            if res.status == "UNKNOWN":
                title = key.replace("_", " ").capitalize()
                lines.append(f"  - Reliable official excerpt defining exact {title} terms")

    return "\n".join(lines)
