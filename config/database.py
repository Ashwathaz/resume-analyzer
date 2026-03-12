import sqlite3
from datetime import datetime
import os

try:
    import psycopg2
    from psycopg2.extras import DictCursor
    from psycopg2 import Binary
except ImportError:
    psycopg2 = None
    Binary = None

class DBCursorAdapter:
    def __init__(self, cursor, db_type, conn_adapter=None):
        self.cursor = cursor
        self.db_type = db_type
        self.conn_adapter = conn_adapter
        self._last_insert_id = None

    def execute(self, query, params=None):
        if self.db_type == 'postgres':
            # Translate ? to %s
            query = query.replace('?', '%s')
            # Translate sqlite types to postgres
            if "INTEGER PRIMARY KEY AUTOINCREMENT" in query:
                query = query.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
            if "datetime('now')" in query:
                 query = query.replace("datetime('now')", "CURRENT_TIMESTAMP")
            if "datetime(" in query and "created_at" in query:
                 query = query.replace("datetime(", "CAST(")
                 query = query.replace(") as date", " AS TEXT) as date")
            if "sqlite_master" in query:
                if "SELECT name FROM sqlite_master" in query:
                     query = "SELECT table_name as name FROM information_schema.tables WHERE table_schema = 'public'"
                     if "name=" in query:
                         query = query.replace("name=", "table_name=")
            
            if "date('now', '-7 days')" in query:
                 query = query.replace("date('now', '-7 days')", "CURRENT_DATE - INTERVAL '7 days'")
            if "date('now')" in query:
                 query = query.replace("date('now')", "CURRENT_DATE")
            
            # Retrieve ID for INSERTs
            if query.strip().upper().startswith("INSERT") and "RETURNING id" not in query.lower():
                query += " RETURNING id"
                try:
                    if params is None:
                        self.cursor.execute(query)
                    else:
                        self.cursor.execute(query, params)
                    row = self.cursor.fetchone()
                    self._last_insert_id = row[0] if row else None
                    return self.cursor
                except Exception as e:
                    if self.conn_adapter: self.conn_adapter.rollback()
                    raise e
                    
        try:
            if params is None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, params)
        except Exception as e:
            if self.db_type == 'postgres' and self.conn_adapter:
                self.conn_adapter.rollback()
            raise e
        return self.cursor

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    @property
    def lastrowid(self):
        if self.db_type == 'postgres':
             return self._last_insert_id
        return self.cursor.lastrowid
    
    def close(self):
        self.cursor.close()

class DBConnectionAdapter:
    def __init__(self, conn, db_type):
        self.conn = conn
        self.db_type = db_type

    def cursor(self):
        return DBCursorAdapter(self.conn.cursor(), self.db_type, self)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    @property
    def autocommit(self):
        return self.conn.autocommit if hasattr(self.conn, 'autocommit') else False

    @autocommit.setter
    def autocommit(self, value):
        if hasattr(self.conn, 'autocommit'):
            self.conn.autocommit = value

def get_database_connection():
    """Create and return a database connection"""
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url and psycopg2:
        try:
            conn = psycopg2.connect(db_url)
            return DBConnectionAdapter(conn, 'postgres')
        except Exception as e:
            print(f"Failed to connect to Postgres: {e}, falling back to SQLite")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'database', 'resume_data.db')
    conn = sqlite3.connect(db_path)
    return DBConnectionAdapter(conn, 'sqlite')

def init_database():
    conn = get_database_connection()
    db_type = conn.db_type
    
    # For Postgres, DDL like CREATE TABLE is often better with autocommit or handled carefully
    if db_type == 'postgres':
        conn.autocommit = True
    
    try:
        cursor = conn.cursor()
        
        # Create resume_data table
        if db_type == 'postgres':
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS resume_data (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                linkedin TEXT,
                github TEXT,
                portfolio TEXT,
                summary TEXT,
                target_role TEXT,
                target_category TEXT,
                education TEXT,
                experience TEXT,
                projects TEXT,
                skills TEXT,
                template TEXT,
                filename TEXT,
                file_content BYTEA,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
        else:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS resume_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                linkedin TEXT,
                github TEXT,
                portfolio TEXT,
                summary TEXT,
                target_role TEXT,
                target_category TEXT,
                education TEXT,
                experience TEXT,
                projects TEXT,
                skills TEXT,
                template TEXT,
                filename TEXT,
                file_content BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''') 

        # Create other tables
        tables = {
            "resume_skills": '''
                resume_id INTEGER,
                skill_name TEXT NOT NULL,
                skill_category TEXT NOT NULL,
                proficiency_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resume_data (id)
            ''',
            "resume_analysis": '''
                resume_id INTEGER,
                ats_score REAL,
                keyword_match_score REAL,
                format_score REAL,
                section_score REAL,
                missing_skills TEXT,
                recommendations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resume_data (id)
            ''',
            "admin_logs": '''
                admin_email TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ''',
            "admin": '''
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ''',
            "ai_analysis": '''
                resume_id INTEGER,
                model_used TEXT,
                resume_score INTEGER,
                job_role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resume_data (id)
            '''
        }

        for table_name, schema in tables.items():
            pk = "SERIAL PRIMARY KEY" if db_type == 'postgres' else "INTEGER PRIMARY KEY AUTOINCREMENT"
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id {pk}, {schema})")
        
        # Add default admin if not exists
        cursor.execute("SELECT COUNT(*) FROM admin")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO admin (email, password) VALUES (?, ?)", ('supadmin1', 'ZEUS999+'))
            print("Default admin user created: supadmin1")
        
        if db_type != 'postgres':
            conn.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

def save_resume_data(data):
    """Save resume data to database"""
    conn = get_database_connection()
    cursor = conn.cursor()
    db_type = conn.db_type
    
    try:
        personal_info = data.get('personal_info', {})
        
        # Handle file content for Postgres
        file_content = data.get('file_content', None)
        if file_content and db_type == 'postgres' and Binary:
            # For Postgres BYTEA, wrap in Binary() if available
            file_content = Binary(file_content)
        # For SQLite, file_content can be bytes directly
        
        # Handle name field - check both 'name' and 'full_name' keys
        name_value = personal_info.get('full_name') or personal_info.get('name', '')

        cursor.execute('''
        INSERT INTO resume_data (
            name, email, phone, linkedin, github, portfolio,
            summary, target_role, target_category, education, 
            experience, projects, skills, template,
            filename, file_content
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name_value,
            personal_info.get('email', ''),
            personal_info.get('phone', ''),
            personal_info.get('linkedin', ''),
            personal_info.get('github', ''),
            personal_info.get('portfolio', ''),
            data.get('summary', ''),
            data.get('target_role', ''),
            data.get('target_category', ''),
            str(data.get('education', [])),
            str(data.get('experience', [])),
            str(data.get('projects', [])),
            str(data.get('skills', [])),
            data.get('template', ''),
            data.get('filename', ''),
            file_content
        ))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error saving resume data: {str(e)}")
        conn.rollback()
        return None
    finally:
        conn.close()

def save_analysis_data(resume_id, analysis):
    """Save resume analysis data"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO resume_analysis (
            resume_id, ats_score, keyword_match_score,
            format_score, section_score, missing_skills,
            recommendations
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            resume_id,
            float(analysis.get('ats_score', 0)),
            float(analysis.get('keyword_match_score', 0)),
            float(analysis.get('format_score', 0)),
            float(analysis.get('section_score', 0)),
            analysis.get('missing_skills', ''),
            analysis.get('recommendations', '')
        ))
        
        conn.commit()
    except Exception as e:
        print(f"Error saving analysis data: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def get_resume_stats():
    """Get statistics about resumes"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Get total resumes
        cursor.execute('SELECT COUNT(*) FROM resume_data')
        total_resumes = cursor.fetchone()[0]
        
        # Get average ATS score
        cursor.execute('SELECT AVG(ats_score) FROM resume_analysis')
        avg_ats_score = cursor.fetchone()[0] or 0
        
        # Get recent activity
        cursor.execute('''
        SELECT name, target_role, created_at 
        FROM resume_data 
        ORDER BY created_at DESC 
        LIMIT 5
        ''')
        recent_activity = cursor.fetchall()
        
        return {
            'total_resumes': total_resumes,
            'avg_ats_score': round(avg_ats_score, 2),
            'recent_activity': recent_activity
        }
    except Exception as e:
        print(f"Error getting resume stats: {str(e)}")
        return None
    finally:
        conn.close()

def log_admin_action(admin_email, action):
    """Log admin login/logout actions"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO admin_logs (admin_email, action)
        VALUES (?, ?)
        ''', (admin_email, action))
        conn.commit()
    except Exception as e:
        print(f"Error logging admin action: {str(e)}")
    finally:
        conn.close()

def get_admin_logs():
    """Get all admin login/logout logs"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        SELECT admin_email, action, timestamp
        FROM admin_logs
        ORDER BY timestamp DESC
        ''')
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting admin logs: {str(e)}")
        return []
    finally:
        conn.close()

def get_all_resume_data():
    """Get all resume data for admin dashboard"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Get resume data joined with analysis data
        cursor.execute('''
        SELECT 
            r.id,
            r.name,
            r.email,
            r.phone,
            r.linkedin,
            r.github,
            r.portfolio,
            r.target_role,
            r.target_category,
            r.created_at,
            a.ats_score,
            a.keyword_match_score,
            a.format_score,
            a.section_score,
            r.filename
        FROM resume_data r
        LEFT JOIN resume_analysis a ON r.id = a.resume_id
        ORDER BY r.created_at DESC
        ''')
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting resume data: {str(e)}")
        return []
    finally:
        conn.close()

def get_resume_file(resume_id):
    """Get resume file content used for download"""
    conn = get_database_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT filename, file_content FROM resume_data WHERE id = ?', (resume_id,))
        result = cursor.fetchone()
        if result:
            filename, file_content = result
            # Handle Postgres BYTEA - convert memoryview/bytes to bytes if needed
            if file_content is not None:
                if isinstance(file_content, memoryview):
                    file_content = bytes(file_content)
                elif not isinstance(file_content, bytes):
                    file_content = bytes(file_content)
            return (filename, file_content)
        return None
    except Exception as e:
        print(f"Error getting resume file: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        conn.close()

def verify_admin(email, password):
    """Verify admin credentials"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM admin WHERE email = ? AND password = ?', (email, password))
        result = cursor.fetchone()
        return bool(result)
    except Exception as e:
        print(f"Error verifying admin: {str(e)}")
        return False
    finally:
        conn.close()

def add_admin(email, password):
    """Add a new admin"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO admin (email, password) VALUES (?, ?)', (email, password))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding admin: {str(e)}")
        return False
    finally:
        conn.close()

def save_ai_analysis_data(resume_id, analysis_data):
    """Save AI analysis data to the database"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Check if the ai_analysis table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER,
                model_used TEXT,
                resume_score INTEGER,
                job_role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resume_data (id)
            )
        """)
        
        # Insert the analysis data
        cursor.execute("""
            INSERT INTO ai_analysis (
                resume_id, model_used, resume_score, job_role
            ) VALUES (?, ?, ?, ?)
        """, (
            resume_id,
            analysis_data.get('model_used', ''),
            analysis_data.get('resume_score', 0),
            analysis_data.get('job_role', '')
        ))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error saving AI analysis data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_ai_analysis_stats():
    """Get statistics about AI analyzer usage"""
    conn = get_database_connection()
    cursor = conn.cursor()
    db_type = conn.db_type
    
    try:
        # Check if the ai_analysis table exists
        if db_type == 'postgres':
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'ai_analysis'
            """)
        else:
            cursor.execute("""
                SELECT name FROM sqlite_master WHERE type='table' AND name='ai_analysis'
            """)
        
        if not cursor.fetchone():
            return {
                "total_analyses": 0,
                "model_usage": [],
                "average_score": 0,
                "top_job_roles": []
            }
        
        # Get total number of analyses
        cursor.execute("SELECT COUNT(*) FROM ai_analysis")
        total_analyses = cursor.fetchone()[0]
        
        # Get model usage statistics
        cursor.execute("""
            SELECT model_used, COUNT(*) as count
            FROM ai_analysis
            GROUP BY model_used
            ORDER BY count DESC
        """)
        model_usage = [{"model": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Get average resume score
        cursor.execute("SELECT AVG(resume_score) FROM ai_analysis")
        average_score = cursor.fetchone()[0] or 0
        
        # Get top job roles
        cursor.execute("""
            SELECT job_role, COUNT(*) as count
            FROM ai_analysis
            GROUP BY job_role
            ORDER BY count DESC
            LIMIT 5
        """)
        top_job_roles = [{"role": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        return {
            "total_analyses": total_analyses,
            "model_usage": model_usage,
            "average_score": round(average_score, 1),
            "top_job_roles": top_job_roles
        }
    except Exception as e:
        print(f"Error getting AI analysis stats: {e}")
        return {
            "total_analyses": 0,
            "model_usage": [],
            "average_score": 0,
            "top_job_roles": []
        }
    finally:
        conn.close()

def get_detailed_ai_analysis_stats():
    """Get detailed statistics about AI analyzer usage including daily trends"""
    conn = get_database_connection()
    cursor = conn.cursor()
    db_type = conn.db_type
    
    try:
        # Check if the ai_analysis table exists
        if db_type == 'postgres':
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'ai_analysis'
            """)
        else:
            cursor.execute("""
                SELECT name FROM sqlite_master WHERE type='table' AND name='ai_analysis'
            """)
        
        if not cursor.fetchone():
            return {
                "total_analyses": 0,
                "model_usage": [],
                "average_score": 0,
                "top_job_roles": [],
                "daily_trend": [],
                "score_distribution": [],
                "recent_analyses": []
            }
        
        # Get total number of analyses
        cursor.execute("SELECT COUNT(*) FROM ai_analysis")
        total_analyses = cursor.fetchone()[0]
        
        # Get model usage statistics
        cursor.execute("""
            SELECT model_used, COUNT(*) as count
            FROM ai_analysis
            GROUP BY model_used
            ORDER BY count DESC
        """)
        model_usage = [{"model": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Get average resume score
        cursor.execute("SELECT AVG(resume_score) FROM ai_analysis")
        average_score = cursor.fetchone()[0] or 0
        
        # Get top job roles
        cursor.execute("""
            SELECT job_role, COUNT(*) as count
            FROM ai_analysis
            GROUP BY job_role
            ORDER BY count DESC
            LIMIT 5
        """)
        top_job_roles = [{"role": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Get daily trend for the last 7 days
        if db_type == 'postgres':
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM ai_analysis
                WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
        else:
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM ai_analysis
                WHERE created_at >= date('now', '-7 days')
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
        daily_trend = [{"date": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Get score distribution
        score_ranges = [
            {"min": 0, "max": 20, "range": "0-20"},
            {"min": 21, "max": 40, "range": "21-40"},
            {"min": 41, "max": 60, "range": "41-60"},
            {"min": 61, "max": 80, "range": "61-80"},
            {"min": 81, "max": 100, "range": "81-100"}
        ]
        
        score_distribution = []
        for range_info in score_ranges:
            cursor.execute("""
                SELECT COUNT(*) FROM ai_analysis 
                WHERE resume_score >= ? AND resume_score <= ?
            """, (range_info["min"], range_info["max"]))
            count = cursor.fetchone()[0]
            score_distribution.append({"range": range_info["range"], "count": count})
        
        # Get recent analyses
        cursor.execute("""
            SELECT model_used, resume_score, job_role, datetime(created_at) as date
            FROM ai_analysis
            ORDER BY created_at DESC
            LIMIT 5
        """)
        recent_analyses = [
            {
                "model": row[0],
                "score": row[1],
                "job_role": row[2],
                "date": row[3]
            } for row in cursor.fetchall()
        ]
        
        return {
            "total_analyses": total_analyses,
            "model_usage": model_usage,
            "average_score": round(average_score, 1),
            "top_job_roles": top_job_roles,
            "daily_trend": daily_trend,
            "score_distribution": score_distribution,
            "recent_analyses": recent_analyses
        }
    except Exception as e:
        print(f"Error getting detailed AI analysis stats: {e}")
        return {
            "total_analyses": 0,
            "model_usage": [],
            "average_score": 0,
            "top_job_roles": [],
            "daily_trend": [],
            "score_distribution": [],
            "recent_analyses": []
        }
    finally:
        conn.close()

def reset_ai_analysis_stats():
    """Reset AI analysis statistics by truncating the ai_analysis table"""
    conn = get_database_connection()
    cursor = conn.cursor()
    db_type = conn.db_type
    
    try:
        # Check if the ai_analysis table exists
        if db_type == 'postgres':
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'ai_analysis'
            """)
        else:
            cursor.execute("""
                SELECT name FROM sqlite_master WHERE type='table' AND name='ai_analysis'
            """)
        
        if not cursor.fetchone():
            return {"success": False, "message": "AI analysis table does not exist"}
        
        # Delete all records from the ai_analysis table
        cursor.execute("DELETE FROM ai_analysis")
        conn.commit()
        
        return {"success": True, "message": "AI analysis statistics have been reset successfully"}
    except Exception as e:
        conn.rollback()
        print(f"Error resetting AI analysis stats: {e}")
        return {"success": False, "message": f"Error resetting AI analysis statistics: {str(e)}"}
    finally:
        conn.close()