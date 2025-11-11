from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# works
db_path = "works.db"

def init_db():
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS works(
            id INTEGER PRIMARY KEY,
            name TEXT,
            company TEXT,
            location TEXT,
            tags TEXT,
            responsibilities TEXT,
            skills TEXT,
            preferred_skills TEXT,
            benefits TEXT,
            link TEXT
        )
    ''')
    connect.commit()
    connect.close()


# Get all works from the database
def get_works():
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    cursor.execute('SELECT * FROM works')
    works = cursor.fetchall()
    connect.close()
    return works

# Add a work to the database
def add_work(name, company, location, tags, responsibilities, skills, preferred_skills, benefits, link):
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    cursor.execute('INSERT INTO works (name, company, location, tags, responsibilities, skills, preferred_skills, benefits, link) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                    (name, company, location, tags, responsibilities, skills, preferred_skills, benefits, link))
    connect.commit()
    connect.close()

# Update work's details
def update_work(id, name, company, location, tags, responsibilities, skills, preferred_skills, benefits, link):  
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    cursor.execute('''
        UPDATE works 
        SET name = ?, company = ?, location = ?, tags = ?, 
            responsibilities = ?, skills = ?, preferred_skills = ?, 
            benefits = ?, link = ?
        WHERE id = ?
    ''', (name, company, location, tags, responsibilities, skills, preferred_skills, benefits, link, id))
    connect.commit()
    connect.close()

# Delete a work by ID
def delete_work(id):
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    cursor.execute('DELETE FROM works WHERE id = ?', (id,))
    connect.commit()
    connect.close()


# Home page to list works and show form to add a new work
@app.route('/')
def index():
    works = get_works()
    return render_template('index.html', works=works)

# Add work via POST request
@app.route('/add_work', methods=['POST'])
def add_work_route():
    name = request.form['name']
    company = request.form['company']
    location = request.form['location']
    tags = request.form['tags']
    responsibilities = request.form['responsibilities']
    skills = request.form['skills']
    preferred_skills = request.form['preferred_skills']
    benefits = request.form['benefits']
    link = request.form['link']
    add_work(name, company, location, tags, responsibilities, skills, preferred_skills, benefits, link)
    return redirect(url_for('index'))

# Update work via POST request
@app.route('/update_work/<int:id>', methods=['GET', 'POST'])
def update_work_route(id):
    if request.method == 'POST':
        name = request.form['name']
        company = request.form['company']
        location = request.form['location']
        tags = request.form['tags']
        responsibilities = request.form['responsibilities']
        skills = request.form['skills']
        preferred_skills = request.form['preferred_skills']
        benefits = request.form['benefits']
        link = request.form['link']
        update_work(id, name, company, location, tags, responsibilities, skills, preferred_skills, benefits, link)
        return redirect(url_for('index'))
    
    # Pre-fill form with current work data
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    cursor.execute('SELECT * FROM works WHERE id = ?', (id,))
    work = cursor.fetchone()
    connect.close()
    return render_template('update_work.html', work=work)

# Delete work via GET request
@app.route('/delete_work/<int:id>', methods=['GET'])
def delete_work_route(id):
    delete_work(id)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)