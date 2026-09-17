"""
End-to-End Database Audit Script
Re-evaluates every single job in `job_alerts.db` through the enhanced classification pipeline.
Compares old vs new classifications, tracks transitions, and generates the final audit metrics report.
"""
import sqlite3
import json
import sys
import os
import yaml
from typing import Dict, List, Any
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from app.ai.schemas import JobExtractionSchema
from app.eligibility.models import UserRequirementsProfile
from app.eligibility.evaluator import EligibilityEvaluator
from app.content.message_fusion import fuse_message_text_if_needed

# Load standard profile from user_requirements.yaml
with open('config/user_requirements.yaml', 'r', encoding='utf-8') as f:
    yaml_conf = yaml.safe_load(f)

standard_profile = UserRequirementsProfile(**yaml_conf)

conn = sqlite3.connect('job_alerts.db')
c = conn.cursor()

c.execute('''
    SELECT j.id, j.organization, j.post_name, j.eligibility_status, j.structured_data,
           (SELECT GROUP_CONCAT(m.message_text, ' --- ') FROM processed_messages m WHERE m.job_id = j.id) as msg_text
    FROM jobs j
    ORDER BY j.created_at ASC
''')

rows = c.fetchall()
print(f"Total jobs loaded from database: {len(rows)}\n")

evaluator = EligibilityEvaluator(standard_profile)

old_counts = {"ELIGIBLE": 0, "UNCERTAIN": 0, "NOT_ELIGIBLE": 0}
new_counts = {"ELIGIBLE": 0, "UNCERTAIN": 0, "NOT_ELIGIBLE": 0}

transitions = []
remaining_uncertain = []
changed_jobs = []

for idx, (job_id, org, post, old_status, struct_raw, msg_text) in enumerate(rows, 1):
    old_counts[old_status] = old_counts.get(old_status, 0) + 1
    
    struct = json.loads(struct_raw) if struct_raw else {}
    job_schema = JobExtractionSchema(**struct)
    
    # Fuse Telegram message text if present (fills missing fields)
    if msg_text:
        job_schema = fuse_message_text_if_needed(job_schema, msg_text)
    
    decision = evaluator.evaluate(job_schema)
    new_status = decision.status
    new_counts[new_status] = new_counts.get(new_status, 0) + 1
    
    changed = (old_status != new_status)
    if changed:
        changed_jobs.append({
            "index": idx,
            "job_id": job_id,
            "org": org,
            "post": post,
            "old_status": old_status,
            "new_status": new_status,
            "summary": decision.summary,
            "taxonomy": decision.taxonomy_tag,
        })
        
    transitions.append((job_id, org, post, old_status, new_status, decision.summary))
    
    if new_status == "UNCERTAIN":
        unknown_reasons = [f"{k}: {v.details}" for k, v in decision.criteria.items() if v.status == "UNKNOWN"]
        remaining_uncertain.append({
            "index": idx,
            "job_id": job_id,
            "org": org,
            "post": post,
            "reasons": unknown_reasons,
        })

print("=" * 80)
print("                     COMPREHENSIVE FINAL AUDIT REPORT")
print("=" * 80)
print(f"OLD REVIEW COUNT (UNCERTAIN)    : {old_counts['UNCERTAIN']}")
print(f"NEW REVIEW COUNT (UNCERTAIN)    : {new_counts['UNCERTAIN']}")
total_classified = len(rows) - new_counts['UNCERTAIN']
auto_pct = (total_classified / len(rows)) * 100
print(f"TOTAL JOBS EVALUATED            : {len(rows)}")
print(f"AUTOMATICALLY CLASSIFIED        : {total_classified} / {len(rows)}")
print(f"AUTOMATIC CLASSIFICATION %      : {auto_pct:.1f}%\n")

print(f"CLASSIFICATION BREAKDOWN (NEW):")
print(f"  • ELIGIBLE     : {new_counts['ELIGIBLE']} jobs (was {old_counts['ELIGIBLE']})")
print(f"  • NOT_ELIGIBLE : {new_counts['NOT_ELIGIBLE']} jobs (was {old_counts['NOT_ELIGIBLE']})")
print(f"  • UNCERTAIN    : {new_counts['UNCERTAIN']} jobs (was {old_counts['UNCERTAIN']})\n")

print("=" * 80)
print(f"JOBS WHOSE CLASSIFICATION CHANGED ({len(changed_jobs)} jobs):")
print("=" * 80)
for ch in changed_jobs:
    print(f"#{ch['index']}: [{ch['old_status']} -> {ch['new_status']}] {ch['org']} | {ch['post']}")
    print(f"    Reason: {ch['summary']}")
    print(f"    Taxonomy Tag: {ch['taxonomy']}")
    print()

print("=" * 80)
print(f"REMAINING REVIEW (UNCERTAIN) CASES ({len(remaining_uncertain)} jobs):")
print("=" * 80)
for unc in remaining_uncertain:
    print(f"#{unc['index']}: {unc['org']} | {unc['post']} (ID: {unc['job_id']})")
    for r in unc['reasons']:
        print(f"    ⚠ {r}")
    print()

with open('scripts/full_audit_results.json', 'w', encoding='utf-8') as f:
    json.dump({
        "total_jobs": len(rows),
        "old_counts": old_counts,
        "new_counts": new_counts,
        "automatic_classification_pct": auto_pct,
        "changed_jobs": changed_jobs,
        "remaining_uncertain": remaining_uncertain,
    }, f, indent=2, ensure_ascii=False)

print("Saved detailed results to scripts/full_audit_results.json")
