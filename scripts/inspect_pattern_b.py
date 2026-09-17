import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('scripts/all_15_uncertain_jobs.json', 'r', encoding='utf-8') as f:
    jobs = json.load(f)

pattern_b_indices = [1, 2, 9, 14, 15]

for j in jobs:
    if j['index'] in pattern_b_indices:
        print(f"=== Pattern B Job #{j['index']} (ID: {j['job_id']}) ===")
        print(f"Org: {j['organization']}")
        print(f"Post: {j['post_name']}")
        print(f"Confidence: {j['confidence']}")
        print(f"Sources: {j['sources']}")
        print(f"Message text:\n{j['message_text']}")
        print("-" * 60)
