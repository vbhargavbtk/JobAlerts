import sqlite3
import json

conn = sqlite3.connect('job_alerts.db')
c = conn.cursor()
c.execute("SELECT id, organization, post_name, eligibility_status, eligibility_explanation FROM jobs")
for r in c.fetchall():
    jid, org, post, status, expl_raw = r
    expl = json.loads(expl_raw) if expl_raw else {}
    summary = expl.get("summary", "")
    criteria = expl.get("criteria", {})
    failed = [k for k, v in criteria.items() if v.get("status") == "FAIL"]
    unknown = [k for k, v in criteria.items() if v.get("status") == "UNKNOWN"]
    print(f"[{status}] {org} | {post}")
    print(f"   Summary: {summary}")
    if failed:
        print(f"   Failed criteria: {failed}")
    if unknown:
        print(f"   Unknown criteria: {unknown}")
    print()
