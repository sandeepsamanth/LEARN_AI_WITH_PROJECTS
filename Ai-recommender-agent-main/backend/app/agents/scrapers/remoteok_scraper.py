"""
RemoteOK scraper
Scrapes job postings from RemoteOK (remote jobs)
"""
from typing import List, Dict
import json
from app.agents.scrapers.base_scraper import BaseScraper
import requests


class RemoteOKScraper(BaseScraper):
    """Scraper for RemoteOK.com"""
    
    BASE_URL = "https://remoteok.com/api"
    
    def scrape(self, search_terms: List[str]) -> List[Dict]:
        """Scrape jobs from RemoteOK"""
        all_jobs = []
        
        try:
            # RemoteOK has a public API endpoint (no auth required)
            self._rate_limit()
            response = requests.get(self.BASE_URL, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # RemoteOK returns JSON array
            jobs_data = response.json()
            
            # Filter by search terms if provided
            for job in jobs_data:
                if isinstance(job, dict) and job.get("id"):
                    # Check if job matches any search term
                    if not search_terms or any(
                        term.lower() in job.get("position", "").lower() or
                        term.lower() in job.get("description", "").lower()
                        for term in search_terms
                    ):
                        normalized_job = self._normalize_job(job)
                        all_jobs.append(normalized_job)
        
        except Exception as e:
            print(f"Error scraping RemoteOK: {str(e)}")
        
        return all_jobs
    
    def _normalize_job(self, job: Dict) -> Dict:
        """Normalize RemoteOK job data"""
        return {
            "title": job.get("position", ""),
            "company": job.get("company", ""),
            "location": "Remote",
            "description": job.get("description", ""),
            "source_url": job.get("url", f"https://remoteok.com/remote-jobs/{job.get('id', '')}"),
            "source": "remoteok",
            "salary": job.get("salary", ""),
            "tags": job.get("tags", [])
        }







