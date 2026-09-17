import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('scripts/all_31_not_eligible_jobs.json', 'r', encoding='utf-8') as f:
    jobs = json.load(f)

for j in jobs:
    qual = j['qualification'] or []
    branches = j['accepted_branches'] or []
    fails = j['fails']
    # Check if this job might actually match a B.Tech / CSE / General Graduate candidate
    has_btech = any('b.tech' in q.lower() or 'b.e.' in q.lower() or 'engineering' in q.lower() or 'graduat' in q.lower() or 'degree' in q.lower() for q in qual)
    has_cs = any('comp' in b.lower() or 'cse' in b.lower() or 'it' in b.lower() or 'information' in b.lower() or 'all' in b.lower() or 'any' in b.lower() for b in branches)
    
    print(f"#{j['index']}: {j['organization']} | {j['post_name']}")
    print(f"   Qual: {qual} | Branches: {branches}")
    print(f"   Age: {j['age_min']}-{j['age_max']} | Exp: {j['experience_required']} (yrs: {j['experience_years_min']})")
    print(f"   Fails: {fails}")
    if has_btech or has_cs:
        print(f"   >>> POTENTIAL MATCH CANDIDATE: btech={has_btech}, cs={has_cs}")
    print("-" * 50)
