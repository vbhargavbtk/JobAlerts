"""
Eligibility Explanations Generator
Formats clean, human-readable verification breakdowns for alerts.
"""
from typing import Dict
from app.eligibility.models import EligibilityDecision, EligibilityCriterionResult


def format_eligibility_explanation(decision: EligibilityDecision) -> str:
    """
    Produces formatted breakdown:
    Qualification: PASS
    Age: PASS
    Experience: PASS
    Branch: PASS
    Job type: PASS
    """
    lines = []
    lines.append(f"*Eligibility Verdict:* `{decision.status}`\n")

    for key, res in decision.criteria.items():
        icon = "✅" if res.status == "PASS" else ("❌" if res.status == "FAIL" else "⚠️")
        title = key.replace("_", " ").capitalize()
        lines.append(f"{icon} *{title}:* `{res.status}` — {res.details}")

    return "\n".join(lines)
