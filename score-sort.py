from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

_global_embedder = None


def get_embedder():
    # singleton pattern
    global _global_embedder
    if _global_embedder is None:
        print("Loading sentence-transformer for the first time...")
        _global_embedder = SentenceTransformerEmbedder()
        print("sentence-transformer ready!")
    return _global_embedder


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
        return f"{self.tags} {self.responsibilities} {self.skills} {self.preferred_skills}"

class JobDatabase:
    def __init__(self):
        self.embedder = get_embedder()
        self.jobs = {}
        self.job_embeddings = {}

    def add_job(self, job):
        self.jobs[job.id] = job
        self.job_embeddings[job.id] = self.embedder.embed_text(job.get_content())

    def find_top_k(self, cv, top_k):
        cv_embedding = self.embedder.embed_text(cv.get_content())

        results = []
        for job_id, job_embedding in self.job_embeddings.items():
            result = cosine_similarity([cv_embedding, job_embedding])[0][1]
            results.append((self.jobs[job_id], result))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


class CV:
    def __init__(self, text):
        self.text = text

    def get_content(self):
        return self.text


class SentenceTransformerEmbedder:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384

    def embed_text(self, text):
        return self.model.encode(text)


def main():
    """to use it, add a job object to the job_database, and call job_database.find_top_k().
    The result returns a sorted list of (job; score)"""
    print("Job Matcher - Demo")

    job_database = JobDatabase()

    cv = CV("""
    Experienced Python developer with 3 years in web development and machine learning.
    Strong skills in Python, Django, Flask, SQL, and JavaScript. Some experience with 
    React and Node.js. Worked on data analysis projects using pandas and scikit-learn.
    Familiar with Docker and AWS deployment. Looking for full-stack or backend roles.

    Education: BS Computer Science, University of Tech
    Experience: 2 years at Startup Inc, 1 year at TechCorp
    """)

    jobs = [
        Job(
            id=1,
            name="Senior Software Engineer",
            company="TechCorp Inc.",
            location="San Francisco, CA (Hybrid)",
            tags=["Full-time", "Senior-level", "Engineering"],
            responsibilities=[
                "Design and develop scalable web applications",
                "Lead technical architecture decisions",
                "Mentor junior developers",
                "Collaborate with product and design teams"
            ],
            skills=["Python", "Django", "React", "PostgreSQL", "AWS"],
            preferred_skills=["Docker", "Kubernetes", "CI/CD", "Microservices"],
            benefits=["Health insurance", "401(k) matching", "Flexible PTO", "Remote work options"],
            link="https://techcorp.com/careers/senior-software-engineer"
        ),

        Job(
            id=2,
            name="Data Scientist",
            company="DataAnalytics Co.",
            location="New York, NY (Remote)",
            tags=["Full-time", "Mid-level", "Data Science"],
            responsibilities=[
                "Build and deploy machine learning models",
                "Analyze large datasets to extract insights",
                "Create data visualizations and reports",
                "Collaborate with business stakeholders"
            ],
            skills=["Python", "SQL", "Machine Learning", "Pandas", "Scikit-learn"],
            preferred_skills=["TensorFlow", "PyTorch", "Spark", "BigQuery"],
            benefits=["Competitive salary", "Stock options", "Learning budget", "Health wellness"],
            link="https://dataanalytics.co/jobs/data-scientist-ny"
        ),

        Job(
            id=3,
            name="Frontend Developer",
            company="WebSolutions LLC",
            location="Austin, TX (On-site)",
            tags=["Full-time", "Mid-level", "Frontend"],
            responsibilities=[
                "Develop responsive web applications",
                "Optimize web performance",
                "Implement UI/UX designs",
                "Write clean, maintainable code"
            ],
            skills=["JavaScript", "React", "HTML5", "CSS3", "TypeScript"],
            preferred_skills=["Next.js", "GraphQL", "Jest", "Webpack"],
            benefits=["Health dental vision", "Unlimited PTO", "Professional development", "Gym membership"],
            link="https://websolutions.com/careers/frontend-dev"
        ),

        Job(
            id=4,
            name="DevOps Engineer",
            company="CloudSystems Ltd.",
            location="Seattle, WA (Remote)",
            tags=["Full-time", "Senior-level", "DevOps"],
            responsibilities=[
                "Manage cloud infrastructure",
                "Implement CI/CD pipelines",
                "Monitor system performance",
                "Ensure system security and compliance"
            ],
            skills=["AWS", "Docker", "Kubernetes", "Terraform", "Linux"],
            preferred_skills=["GCP", "Ansible", "Prometheus", "GitLab CI"],
            benefits=["Remote-first culture", "Equipment stipend", "Health insurance", "Flexible hours"],
            link="https://cloudsystems.io/jobs/devops-engineer"
        ),

        Job(
            id=5,
            name="Product Manager",
            company="InnovateTech",
            location="Boston, MA (Hybrid)",
            tags=["Full-time", "Senior-level", "Product"],
            responsibilities=[
                "Define product roadmap and strategy",
                "Gather and prioritize requirements",
                "Work with engineering and design teams",
                "Analyze market and customer needs"
            ],
            skills=["Product Management", "Agile", "JIRA", "Analytics", "User Research"],
            preferred_skills=["SQL", "A/B Testing", "Roadmapping tools", "Technical background"],
            benefits=["Equity package", "Comprehensive benefits", "Learning stipend", "Parental leave"],
            link="https://innovatetech.com/careers/product-manager"
        ),

        Job(
            id=6,
            name="UX/UI Designer",
            company="CreativeDesign Studio",
            location="Los Angeles, CA (Remote)",
            tags=["Full-time", "Mid-level", "Design"],
            responsibilities=[
                "Create wireframes and prototypes",
                "Conduct user research and testing",
                "Design user interfaces",
                "Collaborate with development teams"
            ],
            skills=["Figma", "Sketch", "Adobe Creative Suite", "User Research", "Wireframing"],
            preferred_skills=["HTML/CSS", "Design Systems", "Animation", "Mobile Design"],
            benefits=["Flexible schedule", "Design conference budget", "Health benefits", "Creative freedom"],
            link="https://creativedesign.studio/jobs/ux-ui-designer"
        ),

        Job(
            id=7,
            name="Backend Engineer",
            company="ServerTech",
            location="Chicago, IL (On-site)",
            tags=["Full-time", "Mid-level", "Backend"],
            responsibilities=[
                "Develop RESTful APIs",
                "Optimize database performance",
                "Implement security best practices",
                "Write unit and integration tests"
            ],
            skills=["Java", "Spring Boot", "MySQL", "REST APIs", "Maven"],
            preferred_skills=["Microservices", "Redis", "Kafka", "MongoDB"],
            benefits=["Competitive compensation", "Health insurance", "401(k)", "Tuition reimbursement"],
            link="https://servertech.com/careers/backend-engineer-chicago"
        ),

        Job(
            id=8,
            name="Machine Learning Engineer",
            company="AI Innovations",
            location="Remote (Global)",
            tags=["Full-time", "Senior-level", "AI/ML"],
            responsibilities=[
                "Research and implement ML algorithms",
                "Deploy models to production",
                "Optimize model performance",
                "Stay current with AI research"
            ],
            skills=["Python", "PyTorch", "TensorFlow", "MLOps", "Data Pipelines"],
            preferred_skills=["PhD in CS/ML", "Publications", "Cloud ML platforms", "Distributed computing"],
            benefits=["Fully remote", "Unlimited vacation", "Stock options", "Research budget"],
            link="https://ai-innovations.com/jobs/ml-engineer"
        ),

        Job(
            id=9,
            name="Full Stack Developer",
            company="StartupXYZ",
            location="Miami, FL (Hybrid)",
            tags=["Full-time", "Junior-level", "Full Stack"],
            responsibilities=[
                "Develop both frontend and backend features",
                "Participate in code reviews",
                "Debug and fix issues",
                "Learn and apply best practices"
            ],
            skills=["JavaScript", "Node.js", "React", "MongoDB", "Git"],
            preferred_skills=["Express.js", "Redux", "AWS", "Testing frameworks"],
            benefits=["Equity", "Mentorship program", "Health benefits", "Startup environment"],
            link="https://startupxyz.com/jobs/full-stack-junior"
        ),

        Job(
            id=10,
            name="QA Automation Engineer",
            company="QualityAssurance Pro",
            location="Denver, CO (Remote)",
            tags=["Full-time", "Mid-level", "QA"],
            responsibilities=[
                "Develop automated test scripts",
                "Create test plans and strategies",
                "Perform manual testing when needed",
                "Report and track bugs"
            ],
            skills=["Selenium", "Java", "TestNG", "JIRA", "API Testing"],
            preferred_skills=["Cypress", "Performance Testing", "Security Testing", "CI/CD integration"],
            benefits=["Work from home", "Health benefits", "Professional certs", "Flexible schedule"],
            link="https://qapro.com/careers/qa-automation-engineer"
        )
    ]
    
    for job in jobs:
        job_database.add_job(job)

    print(f"Analyzing CV against {len(jobs)} jobs...")

    results = job_database.find_top_k(cv, 3)

    # Display quick results
    print("\nTOP 3:")
    for i, result in enumerate(results):
        print(f"{i + 1}. {result[0].name} at {result[0].company}")
        print(f"   Score: {result[1]:.3f}")


if __name__ == "__main__":
    main()