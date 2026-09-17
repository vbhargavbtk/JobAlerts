"""
Database Update Script
Updates all 46 job records in `job_alerts.db` with the newly evaluated deterministic eligibility verdicts,
criteria breakdowns, and taxonomy tags.
"""
import sqlite3
import json
import sys
import os
import yaml

sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from app.ai.schemas import JobExtractionSchema
from app.eligibility.models import UserRequirementsProfile
from app.eligibility.evaluator import EligibilityEvaluator
from app.content.message_fusion import fuse_message_text_if_needed

with open('config/user_requirements.yaml', 'r', encoding='utf-8') as f:
    yaml_conf = yaml.safe_load(f)

standard_profile = UserRequirementsProfile(**yaml_conf)
evaluator = EligibilityEvaluator(standard_profile)

conn = sqlite3.connect('job_alerts.db')
c = conn.cursor()

c.execute('''
    SELECT j.id, j.organization, j.post_name, j.eligibility_status, j.structured_data,
           (SELECT GROUP_CONCAT(m.message_text, ' --- ') FROM processed_messages m WHERE m.job_id = j.id) as msg_text
    FROM jobs j
''')

rows = c.fetchall()
print(f"Updating {len(rows)} database records with verified classifications...")

updated = 0
for job_id, org, post, old_status, struct_raw, msg_text in rows:
    struct = json.loads(struct_raw) if struct_raw else {}
    job_schema = JobExtractionSchema(**struct)
    if msg_text:
        job_schema = fuse_message_text_if_needed(job_schema, msg_text)
    
    decision = evaluator.evaluate(job_schema)
    new_status = decision.status
    explanation_json = json.dumps(decision.model_dump())
    
    c.execute('''
        UPDATE jobs
        SET eligibility_status = ?, eligibility_explanation = ?, updated_at = datetime('now')
        WHERE id = ?
    ''', (new_status, explanation_json, job_id))
    updated += 1

conn.commit()
print(f"Successfully updated {updated} jobs in job_alerts.db!")
