import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, 'database', 'jobs.db')

def init_job():
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs(
            id INTEGER PRIMARY KEY,
            name TEXT,
            company TEXT,
            location TEXT,
            tags TEXT,
            responsibilities TEXT,
            skills TEXT,
            preskills TEXT,
            benefits TEXT,
            link TEXT,
            enddate TEXT,
            point REAL DEFAULT -1,
            missingskill TEXT,
            rcmskills TEXT
        )
    ''')

    connect.commit()
    connect.close()

def get_jobs():
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    cursor.execute('SELECT * FROM jobs')

    jobs = cursor.fetchall()
    connect.close()
    return jobs

def get_job_by_id(id):
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    cursor.execute('SELECT * FROM jobs WHERE id = ?', (id,))

    job = cursor.fetchone()
    connect.close()
    return job

def add_job(name, company, location, tags, responsibilities, skills, preskills, benefits, link, enddate):
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    cursor.execute('INSERT INTO jobs (name, company, location, tags, responsibilities, skills, preskills, benefits, link, enddate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                    (name, company, location, tags, responsibilities, skills, preskills, benefits, link, enddate))
    
    connect.commit()
    connect.close()

def update_job(id, name, company, location, tags, responsibilities, skills, preskills, benefits, link, enddate):  
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    cursor.execute('''
        UPDATE jobs 
        SET name = ?, company = ?, location = ?, tags = ?, 
            responsibilities = ?, skills = ?, preskills = ?, 
            benefits = ?, link = ?, enddate = ?
        WHERE id = ?
    ''', (name, company, location, tags, responsibilities, skills, preskills, benefits, link, enddate, id))

    connect.commit()
    connect.close()

# This is code connect core code
def update_job_analysis(id, point, missingskill, rcmskills):
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    cursor.execute('''
        UPDATE jobs 
        SET point = ?, missingskill = ?, rcmskills = ?
        WHERE id = ?
    ''', (point, missingskill, rcmskills, id))

    connect.commit()
    connect.close()

def delete_job(id):
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    cursor.execute('DELETE FROM jobs WHERE id = ?', (id,))
    
    connect.commit()
    connect.close()

def reset_all_analysis():
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    cursor.execute('UPDATE jobs SET point = -1, missingskill = NULL, rcmskills = NULL')

    connect.commit()
    connect.close()

def delete_expired_jobs():
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('DELETE FROM jobs WHERE enddate < ?', (today,))

    connect.commit()
    connect.close()
    