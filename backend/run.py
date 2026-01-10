from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from cv_engine import initialize_system, CV  # Import from our engine file

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin requests so frontend can talk to backend

# Initialize the heavy ML models and DB once when server starts
job_database = initialize_system()


# --- ROUTES ---

@app.route('/')
def home():
    # Looks for index.html inside the 'templates' folder
    return render_template('index.html')

@app.route('/api/analyze-all', methods=['POST'])
def analyze_all_jobs():
    try:
        data = request.json
        cv_text = data.get('cv_text', '')
        user_cv = CV(cv_text)

        # Get all jobs from the vector database
        # This accesses the jobs loaded into your JobDatabase class
        all_jobs = job_database.jobs 
        
        results = []
        for job in all_jobs:
            # Calculate match percentage
            score_raw = job_database.calculate_score(user_cv, job)
            score_percent = round(float(score_raw * 100), 1)
            
            # Identify missing skills
            missing_skills, recommendations = job_database.skill_gap_analysis_and_recommender(user_cv, job)
            
            results.append({
                "job_id": getattr(job, 'id', None),
                "score": score_percent,
                "missing_skills": missing_skills if isinstance(missing_skills, list) else [str(missing_skills)] if missing_skills else [],
                "recommendations": recommendations if recommendations else []
            })

        return jsonify({"status": "success", "results": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_cv():
    try:
        data = request.json
        cv_text = data.get('cv_text', '')

        if not cv_text:
            return jsonify({"error": "No CV text provided"}), 400

        print(f"Received CV of length: {len(cv_text)}")

        # Create CV object
        user_cv = CV(cv_text)

        # 1. Find Top Jobs
        top_jobs_raw = job_database.find_top_k(user_cv, 3)

        if not top_jobs_raw:
            return jsonify({"status": "success", "jobs": [], "missing_skills": []})

        # Convert Python Objects to JSON-ready format
        jobs_json = []
        best_job = top_jobs_raw[0][0]

        for job_obj, score in top_jobs_raw:
            jobs_json.append({
                "id": job_obj.id,  # <--- ADD THIS LINE
                "title": job_obj.name,
                "company": job_obj.company,
                "score": round(float(score), 3),
                "location": job_obj.location,
                "link": job_obj.link,
                "tags": job_obj.tags
            })

        # 2. Get Recommendations
        missing_skills, courses = job_database.skill_gap_analysis_and_recommender(user_cv, best_job)

        return jsonify({
            "status": "success",
            "jobs": jobs_json,
            "missing_skills": missing_skills,
            "recommendations": courses
        })

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Debug=True allows auto-reload when you change code
    app.run(debug=True, port=5000)