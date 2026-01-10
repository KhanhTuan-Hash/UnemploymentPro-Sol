import os
import sys

# Ensure the script can find the UPS package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from UPS.job import add_job, init_job, get_jobs

def seed_database():
    print("Initializing database...")
    init_job()

    jobs_to_add = [
        # Parameters: name, company, location, tags, responsibilities, skills, preskills, benefits, link, enddate
        ("Senior Python Developer", "Tech Solutions", "Remote", "Python-Flask-Backend", 
         "Develop scalable APIs\nMaintain legacy systems", "Python, SQL, Flask", 
         "Docker, AWS", "Health insurance, Flexible hours", "https://example.com/job1", "2026-12-31"),
        
        ("Frontend Engineer", "Creative Web", "New York, NY", "React-JS-CSS", 
         "Build responsive UIs\nCollaborate with designers", "React, JavaScript, Tailwind", 
         "TypeScript", "Gym membership, Free lunch", "https://example.com/job2", "2026-11-15"),
        
        ("Data Analyst", "Data Dynamics", "Hybrid", "SQL-Python-Tableau", 
         "Analyze customer data\nCreate weekly reports", "SQL, Python, Excel", 
         "Tableau, PowerBI", "Training budget, 401k", "https://example.com/job3", "2026-09-20"),

        ("DevOps Engineer", "CloudScale", "Remote", "Docker-Kubernetes-CI/CD", 
         "Manage cloud infrastructure\nAutomate deployments", "Docker, Kubernetes, AWS", 
         "Terraform, Jenkins", "Unlimited PTO", "https://example.com/job4", "2027-01-10")
    ]

    print(f"Adding {len(jobs_to_add)} jobs...")
    for job in jobs_to_add:
        add_job(*job)
    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed_database()