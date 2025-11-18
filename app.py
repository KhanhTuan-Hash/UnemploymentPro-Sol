from flask import Flask, render_template, request, redirect, url_for
from job import init_job, get_jobs, add_job, update_job, delete_job
import sqlite3

app = Flask(__name__)
db_path = "jobs.db"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/jobs')
def jobs_route():
    # jobs = get_jobs()
    # return render_template('jobs.html', jobs=jobs)
    return render_template('jobs.html')

@app.route('/form_job')
def form_job_route():
    jobs = get_jobs()
    return render_template('form_job.html', jobs=jobs)

@app.route('/add_job', methods=['POST'])
def add_job_route():
    name = request.form['name']
    company = request.form['company']
    location = request.form['location']
    end_date = request.form['end_date']
    tags = request.form['tags']
    responsibilities = request.form['responsibilities']
    skills = request.form['skills']
    preferred_skills = request.form['preferred_skills']
    benefits = request.form['benefits']
    link = request.form['link']
    add_job(name, company, location, tags, responsibilities, skills, preferred_skills, benefits, link, end_date)
    return redirect(url_for('jobs_route'))

@app.route('/update_job/<int:id>', methods=['GET', 'POST'])
def update_job_route(id):
    if request.method == 'POST':
        name = request.form['name']
        company = request.form['company']
        location = request.form['location']
        end_date = request.form['end_date']
        tags = request.form['tags']
        responsibilities = request.form['responsibilities']
        skills = request.form['skills']
        preferred_skills = request.form['preferred_skills']
        benefits = request.form['benefits']
        link = request.form['link']
        update_job(id, name, company, location, tags, responsibilities, skills, preferred_skills, benefits, link, end_date)
        return redirect(url_for('jobs_route'))
    
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    cursor.execute('SELECT * FROM jobs WHERE id = ?', (id,))
    job = cursor.fetchone()
    connect.close()
    return render_template('update_job.html', job=job)

@app.route('/delete_job/<int:id>', methods=['GET'])
def delete_job_route(id):
    delete_job(id)
    return redirect(url_for('jobs_route'))

if __name__ == '__main__':
    init_job()
    app.run(debug=True)
