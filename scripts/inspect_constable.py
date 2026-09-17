import sqlite3
import json

conn = sqlite3.connect('job_alerts.db')
c = conn.cursor()
c.execute("SELECT id, organization, post_name, eligibility_status, structured_data, eligibility_explanation FROM jobs WHERE post_name LIKE '%Constable%'")
for r in c.fetchall():
    print("Org:", r[1])
    print("Post:", r[2])
    print("Status:", r[3])
    print("Structured:", r[4])
    print("Explanation:", r[5])
