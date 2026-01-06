"""
DEPRECATED: This scraper is not used in production.
Real-time scraping only - no sample/test jobs.
This file is kept for reference only.
"""
from typing import List, Dict
from app.agents.scrapers.base_scraper import BaseScraper
import random
from datetime import datetime, timedelta


class TestScraper(BaseScraper):
    """
    DEPRECATED: This scraper generates sample jobs for testing.
    NOT USED in production - only real-time scraping is enabled.
    This class is kept for reference only and is not accessible through the API.
    """

    def scrape(self, search_terms: List[str]) -> List[Dict]:
        """Generate sample jobs based on search terms (DEPRECATED - not used)"""
        all_jobs = []
        base_jobs = [
            {"title": "Software Engineer", "company": "Tech Corp", "location": "Remote", "description": "Develop scalable software solutions.", "skills": ["Python", "React", "AWS"]},
            {"title": "Data Scientist", "company": "Data Insights", "location": "New York", "description": "Analyze complex data sets and build predictive models.", "skills": ["Python", "R", "SQL", "Machine Learning"]},
            {"title": "Frontend Developer", "company": "Web Solutions", "location": "San Francisco", "description": "Build responsive user interfaces.", "skills": ["JavaScript", "React", "CSS", "HTML"]},
            {"title": "Backend Engineer", "company": "API Masters", "location": "Remote", "description": "Design and implement robust backend services.", "skills": ["Node.js", "Python", "FastAPI", "PostgreSQL"]},
            {"title": "DevOps Engineer", "company": "Cloud Innovators", "location": "London", "description": "Manage CI/CD pipelines and cloud infrastructure.", "skills": ["Docker", "Kubernetes", "AWS", "Terraform"]},
        ]

        for term in search_terms:
            for i, base_job in enumerate(base_jobs):
                job = base_job.copy()
                job["title"] = f"{term.title()} {job['title']} {i+1}"
                job["company"] = f"{job['company']} {random.choice(['Inc', 'LLC', 'Group'])}"
                job["location"] = random.choice([job["location"], "Remote", "Berlin", "Pune"])
                job["description"] = f"This is a sample job description for a {job['title']}. {job['description']}"
                job["source_url"] = f"https://example.com/job/{random.randint(1000, 9999)}"
                job["source"] = "test_scraper"
                job["posted_date"] = (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
                job["job_type"] = random.choice(["full-time", "internship", "contract"])
                job["experience_level"] = random.choice(["entry", "mid", "senior"])
                job["salary_min"] = random.randint(50000, 100000) if random.random() > 0.3 else None
                job["salary_max"] = job["salary_min"] + random.randint(10000, 50000) if job["salary_min"] else None
                job["required_skills"] = random.sample(job["skills"], k=random.randint(1, len(job["skills"])))

                all_jobs.append(job)
        return all_jobs

