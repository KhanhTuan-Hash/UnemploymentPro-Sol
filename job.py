import sqlite3

db_path = "jobs.db"

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
            preferred_skills TEXT,
            benefits TEXT,
            link TEXT,
            end_date TEXT,
            Point REAL DEFAULT -1,
            Recommend TEXT
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

def add_job(name, company, location, tags, responsibilities, skills, preferred_skills, benefits, link, end_date):
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    cursor.execute('INSERT INTO jobs (name, company, location, tags, responsibilities, skills, preferred_skills, benefits, link, end_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                    (name, company, location, tags, responsibilities, skills, preferred_skills, benefits, link, end_date))
    connect.commit()
    connect.close()

def update_job(id, name, company, location, tags, responsibilities, skills, preferred_skills, benefits, link, end_date):  
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    cursor.execute('''
        UPDATE jobs 
        SET name = ?, company = ?, location = ?, tags = ?, 
            responsibilities = ?, skills = ?, preferred_skills = ?, 
            benefits = ?, link = ?, end_date = ?
        WHERE id = ?
    ''', (name, company, location, tags, responsibilities, skills, preferred_skills, benefits, link, end_date, id))
    connect.commit()
    connect.close()

def delete_job(id):
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    cursor.execute('DELETE FROM jobs WHERE id = ?', (id,))
    connect.commit()
    connect.close()