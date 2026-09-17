import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

conn = sqlite3.connect('job_alerts.db')
c = conn.cursor()

c.execute('''
    SELECT j.id, j.organization, j.post_name, j.structured_data, j.eligibility_explanation
    FROM jobs j
    WHERE j.eligibility_status = 'NOT_ELIGIBLE'
    ORDER BY j.created_at ASC
''')

rows = c.fetchall()
print(f"Total NOT_ELIGIBLE jobs: {len(rows)}")

fail_reasons = {}
for i, r in enumerate(rows, 1):
    job_id, org, post, struct_raw, expl_raw = r
    struct = json.loads(struct_raw) if struct_raw else {}
    expl = json.loads(expl_raw) if expl_raw else {}
    criteria = expl.get('criteria', {})
    
    fails = {k: v.get('details') for k, v in criteria.items() if v.get('status') == 'FAIL'}
    for fk in fails:
        fail_reasons[fk] = fail_reasons.get(fk, 0) + 1
        
    print(f"#{i}: {org} | {post}")
    print(f"   Qual: {struct.get('qualification')} | Branches: {struct.get('accepted_branches')}")
    print(f"   FAILS: {fails}")
    print()

print(f"Fail reason counts across all {len(rows)} NOT_ELIGIBLE jobs:")
for k, count in fail_reasons.items():
    print(f"  {k}: {count}")
