import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('scripts/uncertain_jobs_dump.json', 'r', encoding='utf-8') as f:
    jobs = json.load(f)

for j in jobs[:8]:
    print(f"=== [{j['index']}/16] ID: {j['job_id']} ===")
    print(f"Org: {j['organization']} | Post: {j['post_name']}")
    print(f"Qual: {j['qualification']} | Branch: {j['accepted_branches']}")
    print(f"Age: {j['age_min']} - {j['age_max']} | Exp: {j['experience_required']} (years: {j['experience_years_min']})")
    print(f"Unknowns: {list(j['unknown_criteria'].keys())}")
    for k, v in j['unknown_criteria'].items():
        print(f"   * {k}: {v.get('details')} (ext: {v.get('extracted_value')})")
    for k, v in j['pass_criteria'].items():
        print(f"   + PASS {k}: {v.get('details')}")
    for k, v in j['fail_criteria'].items():
        print(f"   - FAIL {k}: {v.get('details')}")
    msg = (j['message_text'] or '').replace('\n', ' ')
    print(f"Msg: {msg[:250]}")
    print("=" * 60)
