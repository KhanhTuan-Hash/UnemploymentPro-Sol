import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, 'database', 'jobs.db')

def init_cv():
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS cv_basic(id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT, photopath TEXT, profile TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS cv_education(id INTEGER PRIMARY KEY, degreetype TEXT, title TEXT, major TEXT, school TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS cv_certs(id INTEGER PRIMARY KEY, name TEXT, organization TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS cv_languages(id INTEGER PRIMARY KEY, language TEXT, certtype TEXT, score TEXT, provider TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS cv_skills(id INTEGER PRIMARY KEY, tool TEXT, years TEXT, review TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS cv_experience(id INTEGER PRIMARY KEY, company TEXT, time TEXT, position TEXT, url TEXT, environment TEXT, review TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS cv_contacts(id INTEGER PRIMARY KEY, platform TEXT, link TEXT)''')

    connect.commit()
    connect.close()

def has_cv_data():
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    try:
        cursor.execute('SELECT count(*) FROM cv_basic')
        count = cursor.fetchone()[0]
    except:
        count = 0

    connect.close()
    return count > 0

# Take data for core code
def get_cv_full():
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    data = {}

    cursor.execute('SELECT * FROM cv_basic LIMIT 1')
    basic = cursor.fetchone()
    if basic:
        data['basic'] = basic
        cursor.execute('SELECT * FROM cv_education')

        data['education'] = cursor.fetchall()
        cursor.execute('SELECT * FROM cv_certs')

        data['certs'] = cursor.fetchall()
        cursor.execute('SELECT * FROM cv_languages')

        data['languages'] = cursor.fetchall()
        cursor.execute('SELECT * FROM cv_skills')

        data['skills'] = cursor.fetchall()
        cursor.execute('SELECT * FROM cv_experience')

        data['experience'] = cursor.fetchall()
        cursor.execute('SELECT * FROM cv_contacts')

        data['contacts'] = cursor.fetchall()

    connect.close()
    return data if 'basic' in data else None 

def reset_cv():
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    tables = ['cv_basic', 'cv_education', 'cv_certs', 'cv_languages', 'cv_skills', 'cv_experience', 'cv_contacts']
    for table in tables:
        try: cursor.execute(f'DELETE FROM {table}')
        except: pass
    
    connect.commit()
    connect.close()

def save_cv_data(basicinfo, edulist, certlist, langlist, skilllist, explist, contactlist):
    reset_cv()
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    cursor.execute('INSERT INTO cv_basic (name, email, phone, photopath, profile) VALUES (?, ?, ?, ?, ?)', basicinfo)
    if edulist:
        cursor.executemany('INSERT INTO cv_education (degreetype, title, major, school) VALUES (?, ?, ?, ?)', edulist)
    if certlist:
        cursor.executemany('INSERT INTO cv_certs (name, organization) VALUES (?, ?)', certlist)
    if langlist:
        cursor.executemany('INSERT INTO cv_languages (language, certtype, score, provider) VALUES (?, ?, ?, ?)', langlist)
    if skilllist:
        cursor.executemany('INSERT INTO cv_skills (tool, years, review) VALUES (?, ?, ?)', skilllist)
    if explist:
        cursor.executemany('INSERT INTO cv_experience (company, time, position, url, environment, review) VALUES (?, ?, ?, ?, ?, ?)', explist)
    if contactlist:
        cursor.executemany('INSERT INTO cv_contacts (platform, link) VALUES (?, ?)', contactlist)

    connect.commit()
    connect.close()