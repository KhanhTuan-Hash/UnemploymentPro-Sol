import os
import random
import requests
from flask import render_template, request, redirect, url_for, jsonify
import json
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

@app.route('/api/analyze', methods=['POST'])
def analyze_cv():
    try:
        data = request.json
        cv_text = data.get('cv_text', '')
        
        user_cv = CV(cv_text)
        top_jobs_raw = job_database.find_top_k(user_cv, 3)

        jobs_json = []
        for job_obj, score in top_jobs_raw:
            jobs_json.append({
                "title": job_obj.name,
                "company": job_obj.company,
                # FIX: Convert float32 to standard float
                "score": round(float(score), 3), 
                "location": job_obj.location,
                "tags": job_obj.tags
            })

        best_job = top_jobs_raw[0][0]
        missing_skills, courses = job_database.skill_gap_analysis_and_recommender(user_cv, best_job)

        return jsonify({
            "status": "success",
            "jobs": jobs_json,
            "missing_skills": missing_skills,
            "recommendations": courses
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/analyze_job/<int:id>')
def analyze_job_real(id):
    if not has_cv_data():
        return redirect(url_for('cv_home_route'))

    # 1. Get user data from frontend DB
    cv_data = get_cv_full()
    # Combine profile and skills into a single string for the AI
    profile_text = cv_data['basic'][5]
    skills_text = " ".join([s[0] for s in cv_data['skills']])
    full_text = f"{profile_text} {skills_text}"

    try:
        # 2. POST to the Backend Engine
        response = requests.post('http://127.0.0.1:5000/api/analyze', 
                                 json={'cv_text': full_text},
                                 timeout=10)
        result = response.json()

        if result.get('status') == 'success':
            # 3. Save the AI results into your frontend jobs.db
            # We take the score from the top match
            ai_score = result['jobs'][0]['score'] * 100 
            missing = ", ".join(result['missing_skills'])
            # Convert the recommendations dictionary to a string to store in DB
            recommendations = json.dumps(result['recommendations'])
            
            update_job_analysis(id, ai_score, missing, recommendations)

    except Exception as e:
        print(f"Failed to connect to backend engine: {e}")

    return redirect(url_for('job_analysis_route', id=id))

@app.route('/analyze_cv_real/<int:job_id>')
def analyze_cv_real(job_id):
    # 1. Get the CV text from your frontend DB
    cv_data = get_cv_full() 
    # (Construct a string from cv_data['basic'], cv_data['skills'], etc.)
    full_text = f"{cv_data['basic'][5]} {' '.join([s[0] for s in cv_data['skills']])}"

    # 2. Call the backend run.py
    try:
        response = requests.post('http://127.0.0.1:5000/api/analyze', 
                                 json={'cv_text': full_text})
        results = response.json()
        
        # 3. Update your frontend DB with real AI results
        # Find the specific job score from the results list
        top_job = results['jobs'][0] # Simplest logic: take the top match
        update_job_analysis(job_id, top_job['score'], 
                            ", ".join(results['missing_skills']), 
                            str(results['recommendations']))
    except Exception as e:
        print(f"Connection failed: {e}")

    return redirect(url_for('job_analysis_route', id=job_id))

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

@app.route('/save_analysis', methods=['POST'])
def save_analysis():
    data = request.json
    # data['jobs'] is a list of results from the ML backend
    
    for job_result in data.get('jobs', []):
        # We convert the Python List/Dict into a JSON String
        # so the database can store it in a single TEXT column
        encoded_missing = json.dumps(data.get('missing_skills', []))
        encoded_youtube = json.dumps(data.get('recommendations', {}))
        
        # Call the function in job.py
        update_job_analysis(
            job_result['id'], 
            job_result['score'], 
            encoded_missing, 
            encoded_youtube
        )
    return jsonify({"status": "success"})

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