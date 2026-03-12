import os
import sys
import sqlite3

# Ensure we can import from config
current_dir = os.path.dirname(os.path.abspath(__file__)) # d:/New folder/RESUME_RA/utils
root_dir = os.path.dirname(current_dir) # d:/New folder/RESUME_RA
sys.path.append(root_dir)

print(f"Root directory: {root_dir}")

from config.database import init_database, add_admin

# Paths
db_path = os.path.join(root_dir, 'database', 'resume_data.db')
feedback_db_path = os.path.join(root_dir, 'feedback', 'feedback.db')

# 1. Delete databases
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"Deleted {db_path}")
    except PermissionError:
        print(f"Warning: Could not delete {db_path} (File in use). Attempting to drop tables instead.")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
            conn.commit()
            conn.close()
            print("Dropped all tables in resume_data.db")
        except Exception as e:
            print(f"Error dropping tables: {e}")

if os.path.exists(feedback_db_path):
    try:
        os.remove(feedback_db_path)
        print(f"Deleted {feedback_db_path}")
    except Exception as e:
        print(f"Error deleting feedback db: {e}")

# 2. Re-init database
print("Initializing database...")
init_database()

# 3. Add admin
print("Adding admin...")
# First check if admin exists to avoid unique constraint error if file wasn't deleted
try:
    if add_admin('admin@resume.ai', 'admin123'):
        print("SUCCESS: Created admin user: admin@resume.ai / admin123")
    else:
        print("Admin user addition returned False (maybe already exists?)")
except Exception as e:
    print(f"Error adding admin: {e}")
