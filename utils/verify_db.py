import os
import sys
import sqlite3

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
db_path = os.path.join(root_dir, 'database', 'resume_data.db')

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check tables
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
print("Tables:", tables)

# Check admin
try:
    c.execute("SELECT * FROM admin")
    admins = c.fetchall()
    print("Admins:", admins)
except Exception as e:
    print("Admin table check failed:", e)

# Check resumes
try:
    c.execute("SELECT count(*) FROM resume_data")
    count = c.fetchone()[0]
    print("Resume count:", count)
except Exception as e:
    print("Resume table check failed:", e)

conn.close()
