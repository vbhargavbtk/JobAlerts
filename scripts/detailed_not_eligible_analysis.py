import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

conn = sqlite3.connect('job_alerts.db')
c = conn.cursor()

c.execute('''
    SELECT j.id, j.organization, j.post_name, j.structured_data, j.eligibility_explanation,
           (SELECT GROUP_CONCAT(m.message_text, ' --- ') FROM processed_messages m WHERE m.job_id = j.id)
    FROM jobs j
    WHERE j.eligibility_status = 'NOT_ELIGIBLE'
    ORDER BY j.created_at ASC
''')

rows = c.fetchall()
not_eligible_jobs = []
for i, r in enumerate(rows, 1):
    job_id, org, post, struct_raw, expl_raw, msg_text = r
    struct = json.loads(struct_raw) if struct_raw else {}
    expl = json.loads(expl_raw) if expl_raw else {}
    criteria = expl.get('criteria', {})
    fails = {k: v.get('details') for k, v in criteria.items() if v.get('status') == 'FAIL'}
    
    not_eligible_jobs.append({
        "index": i,
        "job_id": job_id,
        "organization": org,
        "post_name": post,
        "qualification": struct.get("qualification"),
        "accepted_branches": struct.get("accepted_branches"),
        "age_min": struct.get("age_min"),
        "age_max": struct.get("age_max"),
        "experience_required": struct.get("experience_required"),
        "experience_years_min": struct.get("experience_years_min"),
        "fails": fails,
        "msg_preview": (msg_text or "")[:150]
    })

with open('scripts/all_31_not_eligible_jobs.json', 'w', encoding='utf-8') as f:
    json.dump(not_eligible_jobs, f, indent=2, ensure_ascii=False)

print(f"Saved all {len(rows)} NOT_ELIGIBLE jobs to scripts/all_31_not_eligible_jobs.json")
