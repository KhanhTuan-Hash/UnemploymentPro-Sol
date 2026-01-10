from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
import requests
import json
from typing import List, Dict
import time
import os
from dotenv import load_dotenv
from pathlib import Path
import sqlite3
import pandas as pd

# Load environment variables immediately
load_dotenv()

_global_extractor = None
_global_embedder = None
_global_recommender = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED_DB_PATH = os.path.join(BASE_DIR, 'frontend', 'database', 'jobs.db')

def get_extractor():
    global _global_extractor
    if _global_extractor is None:
        print("Loading SkillNER for the first time...")
        _global_extractor = SkillNERExtractor()
        print("SkillNER ready!")
    return _global_extractor


def get_embedder():
    global _global_embedder
    if _global_embedder is None:
        print("Loading sentence-transformer for the first time...")
        _global_embedder = SentenceTransformerEmbedder()
        print("sentence-transformer ready!")
    return _global_embedder


def get_recommender():
    global _global_recommender
    if _global_recommender is None:
        print("Loading Youtube API...")
        _global_recommender = YoutubeRecommender()
        print("Youtube API ready!")
    return _global_recommender


class Job:
    def __init__(self, id, name, company, location, tags, responsibilities, skills, preferred_skills, benefits, link):
        self.id = id
        self.name = name
        self.company = company
        self.location = location
        self.tags = tags
        self.responsibilities = responsibilities
        self.skills = skills
        self.preferred_skills = preferred_skills
        self.benefits = benefits
        self.link = link

    def get_content(self):
        # Convert lists to strings if they aren't already (safety for DB loading)
        t = self.tags if isinstance(self.tags, str) else " ".join(self.tags)
        r = self.responsibilities if isinstance(self.responsibilities, str) else " ".join(self.responsibilities)
        s = self.skills if isinstance(self.skills, str) else " ".join(self.skills)
        p = self.preferred_skills if isinstance(self.preferred_skills, str) else " ".join(self.preferred_skills)
        return f"{t} {r} {s} {p}"


class SQLiteManager:
    def __init__(self, db_name="jobs.db"):
        self.db_name = db_name

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
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
        conn.commit()
        conn.close()

    def job_exists(self, job_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM jobs WHERE id = ?", (job_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def insert_job(self, job):
        if self.job_exists(job.id):
            return

        conn = self.get_connection()
        cursor = conn.cursor()
        # Store complex lists as JSON strings
        cursor.execute('''
            INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?)
        ''', (
            job.id, job.name, job.company, job.location,
            json.dumps(job.tags), json.dumps(job.responsibilities),
            json.dumps(job.skills), json.dumps(job.preferred_skills),
            json.dumps(job.benefits), job.link
        ))
        conn.commit()
        conn.close()

    def get_all_jobs(self):
        def safe_json_load(data):
            if not data: return []
            try:
                val = json.loads(data)
                return val if isinstance(val, list) else [str(val)]
            except:
                # Fallback for plain text separated by commas or hyphens
                if '-' in str(data): return [x.strip() for x in data.split('-') if x.strip()]
                if ',' in str(data): return [x.strip() for x in data.split(',') if x.strip()]
                return [str(data)]

        connect = sqlite3.connect(self.db_path)
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM jobs') # Selects all 14 columns
        rows = cursor.fetchall()
        connect.close()

        jobs = []
        for row in rows:
            jobs.append(Job(
                id=row[0], 
                name=row[1], 
                company=row[2], 
                location=row[3],
                tags=safe_json_load(row[4]),
                responsibilities=safe_json_load(row[5]),
                skills=safe_json_load(row[6]),
                preskills=safe_json_load(row[7]),
                benefits=safe_json_load(row[8]),
                link=row[9] # This matches row[9] in your job.py table
            ))
        return jobs


class JobDatabase:
    def __init__(self):
        self.extractor = get_extractor()
        self.embedder = get_embedder()
        self.recommender = get_recommender()
        self.jobs = {}
        self.job_extractions = {}
        self.job_skills = {}
        self.job_skill_embeddings = {}
        self.job_embeddings = {}
        self.results = []

    def add_job(self, job):
        self.jobs[job.id] = job
        self.job_extractions[job.id] = self.extractor.extract_skill(job.get_content())
        self.job_skills[job.id] = ' '.join(self.job_extractions[job.id])
        self.job_skill_embeddings[job.id] = self.embedder.embed_text(self.job_skills[job.id])
        self.job_embeddings[job.id] = self.embedder.embed_text(job.get_content())

    def find_top_k(self, cv, top_k):
        cv_extraction = self.extractor.extract_skill(cv.get_content())
        cv_skills = ' '.join(cv_extraction)
        cv_skill_embedding = self.embedder.embed_text(cv_skills)
        cv_embedding = self.embedder.embed_text(cv.get_content())

        self.results = []
        for job_id, job_embedding in self.job_embeddings.items():
            skill_result = cosine_similarity([cv_skill_embedding], [self.job_skill_embeddings[job_id]])[0][0]
            whole_result = cosine_similarity([cv_embedding], [job_embedding])[0][0]
            self.results.append((self.jobs[job_id], (2 * skill_result + whole_result) / 3))

        self.results.sort(key=lambda x: x[1], reverse=True)
        return self.results[:top_k]

    def skill_gap_analysis_and_recommender(self, cv, job):
        cv_extraction = self.extractor.extract_skill(cv.get_content())
        missing_skills = []

        for job_skill in self.job_extractions[job.id]:
            job_skill_embedding = self.embedder.embed_text(job_skill)
            max_similarity = 0

            for cv_skill in cv_extraction:
                cv_skill_embedding = self.embedder.embed_text(cv_skill)
                similarity = cosine_similarity([cv_skill_embedding], [job_skill_embedding])[0][0]
                max_similarity = max(max_similarity, similarity)

            if max_similarity < 0.7:
                missing_skills.append(job_skill)

        recommendations = self.recommender.recommend_courses_for_skills(missing_skills, 3)
        return missing_skills, recommendations


class CV:
    def __init__(self, text):
        self.text = text

    def get_content(self):
        return self.text


class SkillNERExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.model = SkillExtractor(self.nlp, SKILL_DB, PhraseMatcher)

    def extract_skill(self, text):
        annotations = self.model.annotate(text)
        skills = set()
        for match in annotations['results']['full_matches']:
            skills.add(match['doc_node_value'])
        for match in annotations['results']['ngram_scored']:
            if match['score'] > 0.7:
                skills.add(match['doc_node_value'])
        return list(skills)


class SentenceTransformerEmbedder:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384

    def embed_text(self, text):
        return self.model.encode(text)


class YoutubeRecommender:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def make_api_request(self, endpoint: str, params: dict) -> dict:
        if not self.api_key:
            print("WARNING: No Youtube API Key found in .env")
            return {}

        params['key'] = self.api_key
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Youtube API request failed: {e}")
            return {}

    def search_educational_content(self, skill: str, max_results: int = 5) -> List[Dict]:
        search_queries = [f"{skill} full course", f"{skill} tutorial"]
        all_courses = []

        for query in search_queries:
            params = {
                'part': 'snippet', 'q': query, 'type': 'video',
                'videoDuration': 'medium', 'maxResults': max_results, 'order': 'relevance'
            }
            data = self.make_api_request('search', params)
            if not data: continue

            for item in data.get('items', []):
                snippet = item['snippet']
                all_courses.append({
                    'name': snippet['title'],
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    'channel': snippet['channelTitle']
                })
            time.sleep(0.1)

        # Simple dedupe by URL
        seen = set()
        unique = []
        for c in all_courses:
            if c['url'] not in seen:
                seen.add(c['url'])
                unique.append(c)
        return unique[:max_results]

    def recommend_courses_for_skills(self, missing_skills: List[str], max_per_skill: int = 3) -> Dict[str, List[Dict]]:
        recommendations = {}
        for skill in missing_skills:
            print(f"🔍 Searching YouTube for '{skill}'...")
            courses = self.search_educational_content(skill, max_results=5)
            recommendations[skill] = courses[:max_per_skill]
        return recommendations


# --- INITIALIZATION LOGIC ---

def initialize_system():
    print("--- SYSTEM STARTUP ---")

    # 1. Setup SQLite
    db_manager = SQLiteManager(db_name=SHARED_DB_PATH)
    db_manager.create_table()

    # 2. Check for data, if empty, SEED it
    existing_jobs = db_manager.get_all_jobs()

    if not existing_jobs:
        print("Database empty. Seeding initial jobs...")
        seed_jobs = [
            Job(1, "Senior Software Engineer", "TechCorp Inc.", "San Francisco, CA (Hybrid)",
                ["Full-time", "Senior-level", "Engineering"],
                ["Design and develop scalable web applications", "Lead technical architecture decisions"],
                ["Python", "Django", "React", "PostgreSQL", "AWS"], ["Docker", "Kubernetes", "CI/CD", "Microservices"],
                ["Health insurance"], "https://techcorp.com/careers/senior-software-engineer"),
            Job(2, "Data Scientist", "DataAnalytics Co.", "New York, NY (Remote)",
                ["Full-time", "Mid-level", "Data Science"],
                ["Build and deploy machine learning models", "Analyze large datasets"],
                ["Python", "SQL", "Machine Learning", "Pandas", "Scikit-learn"], ["TensorFlow", "PyTorch", "Spark"],
                ["Stock options"], "https://dataanalytics.co/jobs/data-scientist-ny"),
            Job(3, "Frontend Developer", "WebSolutions LLC", "Austin, TX (On-site)",
                ["Full-time", "Mid-level", "Frontend"],
                ["Develop responsive web applications", "Optimize web performance"],
                ["JavaScript", "React", "HTML5", "CSS3", "TypeScript"], ["Next.js", "GraphQL", "Jest"],
                ["Unlimited PTO"], "https://websolutions.com/careers/frontend-dev"),
            Job(4, "DevOps Engineer", "CloudSystems Ltd.", "Seattle, WA (Remote)",
                ["Full-time", "Senior-level", "DevOps"], ["Manage cloud infrastructure", "Implement CI/CD pipelines"],
                ["AWS", "Docker", "Kubernetes", "Terraform", "Linux"], ["GCP", "Ansible", "Prometheus"],
                ["Remote-first culture"], "https://cloudsystems.io/jobs/devops-engineer"),
            Job(5, "Product Manager", "InnovateTech", "Boston, MA (Hybrid)", ["Full-time", "Senior-level", "Product"],
                ["Define product roadmap", "Gather requirements"], ["Product Management", "Agile", "JIRA", "Analytics"],
                ["SQL", "A/B Testing"], ["Equity package"], "https://innovatetech.com/careers/product-manager"),
            Job(6, "UX/UI Designer", "CreativeDesign Studio", "Los Angeles, CA (Remote)",
                ["Full-time", "Mid-level", "Design"], ["Create wireframes and prototypes", "Conduct user research"],
                ["Figma", "Sketch", "Adobe Creative Suite"], ["HTML/CSS", "Animation"], ["Flexible schedule"],
                "https://creativedesign.studio/jobs/ux-ui-designer"),
            Job(7, "Backend Engineer", "ServerTech", "Chicago, IL (On-site)", ["Full-time", "Mid-level", "Backend"],
                ["Develop RESTful APIs", "Optimize database"], ["Java", "Spring Boot", "MySQL", "REST APIs"],
                ["Microservices", "Redis", "Kafka"], ["Competitive compensation"],
                "https://servertech.com/careers/backend-engineer-chicago"),
            Job(8, "Machine Learning Engineer", "AI Innovations", "Remote (Global)",
                ["Full-time", "Senior-level", "AI/ML"], ["Research and implement ML algorithms", "Deploy models"],
                ["Python", "PyTorch", "TensorFlow", "MLOps"], ["PhD in CS/ML", "Cloud ML platforms"], ["Fully remote"],
                "https://ai-innovations.com/jobs/ml-engineer"),
            Job(9, "Full Stack Developer", "StartupXYZ", "Miami, FL (Hybrid)",
                ["Full-time", "Junior-level", "Full Stack"],
                ["Develop both frontend and backend features", "Debug issues"],
                ["JavaScript", "Node.js", "React", "MongoDB"], ["Express.js", "Redux", "AWS"], ["Mentorship program"],
                "https://startupxyz.com/jobs/full-stack-junior"),
            Job(10, "QA Automation Engineer", "QualityAssurance Pro", "Denver, CO (Remote)",
                ["Full-time", "Mid-level", "QA"], ["Develop automated test scripts", "Create test plans"],
                ["Selenium", "Java", "TestNG", "JIRA"], ["Cypress", "Performance Testing"], ["Work from home"],
                "https://qapro.com/careers/qa-automation-engineer")
        ]

        for job in seed_jobs:
            db_manager.insert_job(job)

        existing_jobs = db_manager.get_all_jobs()

    # 3. Load into Vector Engine
    engine_db = JobDatabase()
    print(f"Loading {len(existing_jobs)} jobs from SQLite into Vector Engine...")
    for job in existing_jobs:
        engine_db.add_job(job)

    print("--- SYSTEM READY ---")
    return engine_db