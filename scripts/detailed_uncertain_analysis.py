import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

conn = sqlite3.connect('job_alerts.db')
c = conn.cursor()

c.execute('''
    SELECT j.id, j.organization, j.post_name, j.structured_data, j.eligibility_explanation, j.confidence,
           (SELECT GROUP_CONCAT(m.message_text, ' ---NEXT MSG--- ') FROM processed_messages m WHERE m.job_id = j.id),
           (SELECT GROUP_CONCAT(s.url, ' | ') FROM sources s WHERE s.job_id = j.id)
    FROM jobs j
    WHERE j.eligibility_status = 'UNCERTAIN'
    ORDER BY j.created_at ASC
''')

rows = c.fetchall()
print(f"Total UNCERTAIN jobs: {len(rows)}")

jobs_analysis = []
for i, r in enumerate(rows, 1):
    job_id, org, post, struct_raw, expl_raw, conf, msg_text, sources = r
    struct = json.loads(struct_raw) if struct_raw else {}
    expl = json.loads(expl_raw) if expl_raw else {}
    criteria = expl.get('criteria', {})
    
    unknowns = {k: v for k, v in criteria.items() if v.get('status') == 'UNKNOWN'}
    fails = {k: v for k, v in criteria.items() if v.get('status') == 'FAIL'}
    passes = {k: v for k, v in criteria.items() if v.get('status') == 'PASS'}
    
    analysis_entry = {
        "index": i,
        "job_id": job_id,
        "organization": org,
        "post_name": post,
        "confidence": conf,
        "sources": sources,
        "qualification": struct.get("qualification"),
        "accepted_branches": struct.get("accepted_branches"),
        "age_min": struct.get("age_min"),
        "age_max": struct.get("age_max"),
        "experience_required": struct.get("experience_required"),
        "experience_years_min": struct.get("experience_years_min"),
        "location": struct.get("location"),
        "minimum_percentage": struct.get("minimum_percentage"),
        "unknown_criteria": unknowns,
        "fail_criteria": fails,
        "pass_criteria": passes,
        "message_text": msg_text,
    }
    jobs_analysis.append(analysis_entry)

with open('scripts/all_15_uncertain_jobs.json', 'w', encoding='utf-8') as f:
    json.dump(jobs_analysis, f, indent=2, ensure_ascii=False)

print("Saved all 15 uncertain jobs to scripts/all_15_uncertain_jobs.json")
