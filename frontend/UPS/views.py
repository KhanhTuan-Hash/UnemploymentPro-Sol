import os
import random
from flask import render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from UPS import app
from UPS.job import get_jobs, add_job, update_job, delete_job, get_job_by_id, update_job_analysis, reset_all_analysis, delete_expired_jobs
from UPS.cv import has_cv_data, save_cv_data, get_cv_full, reset_cv

def get_sorted_jobs():
    jobs_raw = get_jobs()
    # index 11 is Point, 10 is enddate
    jobs_sorted = sorted(jobs_raw, key=lambda job: (-job[11] if job[11] is not None else 1, job[10]))
    return jobs_sorted

@app.route('/')
def index():
    delete_expired_jobs()

    jobs = get_sorted_jobs()
    user_has_cv = has_cv_data()
    return render_template('index.html', jobs=jobs, hascv=user_has_cv)

@app.route('/jobs')
def jobs_route():
    delete_expired_jobs()

    jobs = get_sorted_jobs()
    return render_template('jobs.html', jobs=jobs)

@app.route('/form_job')
def form_job_route():
    return render_template('form_job.html')

@app.route('/add_job', methods=['POST'])
def add_job_route():
    name = request.form['name']
    company = request.form['company']
    location = request.form['location']
    enddate = request.form['enddate'] 
    tags = request.form['tags']
    responsibilities = request.form['responsibilities']
    skills = request.form['skills']
    preskills = request.form['preskills'] 
    benefits = request.form['benefits']
    link = request.form['link']

    add_job(name, company, location, tags, responsibilities, skills, preskills, benefits, link, enddate)
    return redirect(url_for('jobs_route'))

@app.route('/update_job/<int:id>', methods=['GET', 'POST'])
def update_job_route(id):
    if request.method == 'POST':
        name = request.form['name']
        company = request.form['company']
        location = request.form['location']
        enddate = request.form['enddate']
        tags = request.form['tags']
        responsibilities = request.form['responsibilities']
        skills = request.form['skills']
        preskills = request.form['preskills']
        benefits = request.form['benefits']
        link = request.form['link']

        update_job(id, name, company, location, tags, responsibilities, skills, preskills, benefits, link, enddate)
        return redirect(url_for('jobs_route'))
    
    job = get_job_by_id(id)
    return render_template('update_job.html', job=job)

@app.route('/delete_job/<int:id>', methods=['GET'])
def delete_job_route(id):
    delete_job(id)
    return redirect(url_for('jobs_route'))

@app.route('/job_analysis/<int:id>')
def job_analysis_route(id):
    job = get_job_by_id(id)

    if not job:
        return redirect(url_for('index'))
    return render_template('job_analysis.html', job=job)

@app.route('/reset_all_scores')
def reset_all_scores_route():
    reset_all_analysis()
    return redirect(url_for('jobs_route'))

# Code for core code
@app.route('/simulate_ai/<int:id>')
def simulate_ai_route(id):
    score = random.randint(45, 98)
    missingskill = "Loser"
    rcmskills = "Learning"

    update_job_analysis(id, score, missingskill, rcmskills)
    return redirect(url_for('index'))

@app.route('/cv_home')
def cv_home_route():
    if has_cv_data():
        return redirect(url_for('view_cv_route'))
    return render_template('cv_landing.html')

@app.route('/input_cv', methods=['GET'])
def input_cv_route():
    if has_cv_data():
        return redirect(url_for('view_cv_route'))
    return render_template('input_cv.html')

@app.route('/edit_cv')
def edit_cv_route():
    cv_data = get_cv_full()
    return render_template('input_cv.html', cv=cv_data)

@app.route('/save_cv', methods=['POST'])
def save_cv_route():
    old_cv = get_cv_full()
    
    if old_cv and 'basic' in old_cv and old_cv['basic']:
        old_photopath = old_cv['basic'][4]
    else:
        old_photopath = ''

    photo = request.files.get('photo')
    photopath = old_photopath

    if photo and photo.filename != '':
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        photopath = filename

    name = request.form['name']
    email = request.form['email']
    phone = request.form.get('phone', '')
    profile = request.form['profile']
    basicinfo = (name, email, phone, photopath, profile)

    edutypes = request.form.getlist('edutype[]')
    edutitles = request.form.getlist('edutitle[]')
    edumajors = request.form.getlist('edumajor[]')
    eduschools = request.form.getlist('eduschool[]')
    edulist = list(zip(edutypes, edutitles, edumajors, eduschools))

    certnames = request.form.getlist('certname[]')
    certorgs = request.form.getlist('certorg[]')
    certlist = list(zip(certnames, certorgs))

    langnames = request.form.getlist('langname[]')
    langtypes = request.form.getlist('langtype[]')
    langscores = request.form.getlist('langscore[]')
    langproviders = request.form.getlist('langprovider[]')
    langlist = list(zip(langnames, langtypes, langscores, langproviders))

    skilltools = request.form.getlist('skilltool[]')
    skillyears = request.form.getlist('skillyears[]')
    skillreviews = request.form.getlist('skillreview[]')
    skilllist = list(zip(skilltools, skillyears, skillreviews))

    expcompanies = request.form.getlist('expcompany[]')
    exptimes = request.form.getlist('exptime[]')
    exppositions = request.form.getlist('expposition[]')
    expurls = request.form.getlist('expurl[]')
    expenvs = request.form.getlist('expenv[]')
    expreviews = request.form.getlist('expreview[]')
    explist = list(zip(expcompanies, exptimes, exppositions, expurls, expenvs, expreviews))

    contactplatforms = request.form.getlist('contactplatform[]')
    contactlinks = request.form.getlist('contactlink[]')
    contactlist = list(zip(contactplatforms, contactlinks))

    save_cv_data(basicinfo, edulist, certlist, langlist, skilllist, explist, contactlist)
    return redirect(url_for('view_cv_route'))

@app.route('/view_cv')
def view_cv_route():
    cv_data = get_cv_full()
    if not cv_data:
        return redirect(url_for('cv_home_route'))
    return render_template('cv_view.html', cv=cv_data)

@app.route('/reset_cv')
def reset_cv_route():
    reset_cv()
    return redirect(url_for('cv_home_route'))