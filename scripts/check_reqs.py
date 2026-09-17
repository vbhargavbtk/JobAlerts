import sqlite3
import json

conn = sqlite3.connect('job_alerts.db')
c = conn.cursor()
c.execute("SELECT configuration, version, updated_at FROM user_requirements WHERE id='default_user'")
row = c.fetchone()
if row:
    data = json.loads(row[0])
    print("Version:", row[1], "Updated at:", row[2])
    print("Personal:", data.get("personal"))
    print("Education History:", data.get("education_history"))
    print("Education Records:", data.get("education_records"))
    print("Branch Mappings:", data.get("branch_mappings"))
    print("Subjects 10_12:", data.get("subjects_10_12"))
else:
    print("No default_user row found!")
