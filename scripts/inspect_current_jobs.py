import sqlite3
import json

conn = sqlite3.connect('job_alerts.db')
c = conn.cursor()
c.execute("SELECT id, organization, post_name, eligibility_status, structured_data FROM jobs")
rows = c.fetchall()
print(f"Total jobs in DB: {len(rows)}")
by_status = {}
for r in rows:
    st = r[3] or "UNKNOWN"
    by_status[st] = by_status.get(st, 0) + 1

print("Status counts:", by_status)
print("\nAll jobs currently marked UNCERTAIN or ELIGIBLE:")
for r in rows:
    st = r[3]
    jid = r[0]
    org = r[1] or ""
    post = r[2] or ""
    sd = json.loads(r[4]) if r[4] else {}
    branches = sd.get("accepted_branches") or []
    quals = sd.get("qualification") or []
    if st in ("UNCERTAIN", "ELIGIBLE"):
        print(f"[{st}] ID: {jid[:8]} | Org: {org[:20]} | Post: {post[:40]} | Branches: {branches} | Quals: {quals}")
