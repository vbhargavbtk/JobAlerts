import sqlite3
import json
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

conn = sqlite3.connect('job_alerts.db')
c = conn.cursor()
c.execute('''
    SELECT j.id, j.organization, j.post_name, j.eligibility_status, j.eligibility_explanation, j.structured_data, m.message_text
    FROM jobs j
    LEFT JOIN processed_messages m ON m.job_id = j.id
    WHERE j.eligibility_status = 'UNCERTAIN'
''')
rows = c.fetchall()
print(f'Total UNCERTAIN jobs found: {len(rows)}')

records = []
for i, r in enumerate(rows, 1):
    job_id, org, post, status, expl_raw, struct_raw, msg_text = r
    expl = json.loads(expl_raw) if expl_raw else {}
    struct = json.loads(struct_raw) if struct_raw else {}
    criteria = expl.get('criteria', {})
    unknown_criteria = {k: v for k, v in criteria.items() if v.get('status') == 'UNKNOWN'}
    fail_criteria = {k: v for k, v in criteria.items() if v.get('status') == 'FAIL'}
    pass_criteria = {k: v for k, v in criteria.items() if v.get('status') == 'PASS'}
    
    rec = {
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
        "unknown_criteria": unknown_criteria,
        "fail_criteria": fail_criteria,
        "pass_criteria": pass_criteria,
        "message_text": msg_text
    }
    records.append(rec)
    
    print(f'=== [{i}/{len(rows)}] Job ID: {job_id} ===')
    print(f'Org: {org} | Post: {post}')
    print(f'Qual: {struct.get("qualification")} | Branch: {struct.get("accepted_branches")}')
    print(f'Age Min/Max: {struct.get("age_min")} / {struct.get("age_max")} | Exp Req/Years: {struct.get("experience_required")} / {struct.get("experience_years_min")}')
    print(f'Unknown Criteria: {list(unknown_criteria.keys())}')
    for uk, uv in unknown_criteria.items():
        print(f'   -> {uk}: {uv.get("details")} (extracted: {uv.get("extracted_value")})')
    if fail_criteria:
        print(f'Fail Criteria: {list(fail_criteria.keys())}')
    if msg_text:
        preview = msg_text.replace('\n', ' ')[:200]
        print(f'Msg: {preview}')
    print('-' * 60)

with open('scripts/uncertain_jobs_dump.json', 'w', encoding='utf-8') as f:
    json.dump(records, f, indent=2, ensure_ascii=False)
print("Saved dump to scripts/uncertain_jobs_dump.json")
