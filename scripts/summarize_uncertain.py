import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('scripts/all_15_uncertain_jobs.json', 'r', encoding='utf-8') as f:
    jobs = json.load(f)

for j in jobs:
    print(f"#{j['index']}: ID {j['job_id']}")
    print(f"  Org: {j['organization']}")
    print(f"  Post: {j['post_name']}")
    print(f"  Qual: {j['qualification']}")
    print(f"  Branches: {j['accepted_branches']}")
    print(f"  Age: min={j['age_min']}, max={j['age_max']}")
    print(f"  Exp: required={j['experience_required']}, years={j['experience_years_min']}")
    print(f"  Unknowns: {list(j['unknown_criteria'].keys())}")
    for u, det in j['unknown_criteria'].items():
        print(f"     [{u}] {det.get('details')}")
    msg = (j['message_text'] or '').strip()
    first_line = msg.split('\n')[0] if msg else 'None'
    print(f"  Msg first line: {first_line}")
    print("-" * 50)
