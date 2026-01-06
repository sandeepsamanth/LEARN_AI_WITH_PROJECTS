"""
Indeed.com scraper
Scrapes job postings from Indeed
"""
from typing import List, Dict
from bs4 import BeautifulSoup
from app.agents.scrapers.base_scraper import BaseScraper
import urllib.parse


class IndeedScraper(BaseScraper):
    """Scraper for Indeed.com"""
    
    BASE_URL = "https://www.indeed.com/jobs"
    
    def scrape(self, search_terms: List[str]) -> List[Dict]:
        """Scrape jobs from Indeed"""
        all_jobs = []
        
        for term in search_terms:
            jobs = self._scrape_search_term(term)
            all_jobs.extend(jobs)
        
        return all_jobs
    
    def _scrape_search_term(self, search_term: str, max_pages: int = 2) -> List[Dict]:
        """Scrape jobs for a specific search term"""
        jobs = []
        
        for page in range(max_pages):
            params = {
                "q": search_term,
                "start": page * 10
            }
            url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
            
            try:
                soup = self._get_page(url)
                page_jobs = self._parse_job_listings(soup)
                
                # Debug: print what we found
                print(f"Indeed: Found {len(page_jobs)} jobs on page {page} for '{search_term}'")
                
                jobs.extend(page_jobs)
                
                if len(page_jobs) == 0:
                    print(f"Indeed: No more jobs found, stopping at page {page}")
                    break  # No more jobs
                    
            except Exception as e:
                print(f"Error scraping Indeed page {page} for '{search_term}': {str(e)}")
                # Continue to next page instead of breaking
                continue
        
        print(f"Indeed: Total jobs scraped for '{search_term}': {len(jobs)}")
        return jobs
    
    def _parse_job_listings(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse job listings from Indeed search results page"""
        jobs = []
        
        # Try multiple selectors as Indeed changes their HTML structure
        job_cards = soup.find_all("div", class_="job_seen_beacon")
        
        # Fallback: try other common selectors
        if len(job_cards) == 0:
            job_cards = soup.find_all("div", {"data-jk": True})
        if len(job_cards) == 0:
            job_cards = soup.find_all("a", {"data-jk": True})
        if len(job_cards) == 0:
            # Try finding any div with job-related classes
            job_cards = soup.find_all("div", class_=lambda x: x and ("job" in x.lower() or "result" in x.lower()))
        
        print(f"Indeed: Found {len(job_cards)} job cards using various selectors")
        
        for card in job_cards:
            try:
                # Extract job title
                title_elem = card.find("h2", class_="jobTitle")
                title = self._extract_text(title_elem.find("a")) if title_elem else ""
                
                # Extract company
                company_elem = card.find("span", {"data-testid": "company-name"})
                company = self._extract_text(company_elem) if company_elem else ""
                
                # Extract location
                location_elem = card.find("div", {"data-testid": "text-location"})
                location = self._extract_text(location_elem) if location_elem else ""
                
                # Extract job URL
                link_elem = title_elem.find("a") if title_elem else None
                job_url = ""
                if link_elem and link_elem.get("href"):
                    href = link_elem["href"]
                    if href.startswith("/"):
                        job_url = f"https://www.indeed.com{href}"
                    else:
                        job_url = href
                
                # Extract snippet/description
                snippet_elem = card.find("div", class_="job-snippet")
                snippet = self._extract_text(snippet_elem) if snippet_elem else ""
                
                if title and company:
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "description": snippet,
                        "source_url": job_url,
                        "source": "indeed"
                    })
            except Exception as e:
                print(f"Error parsing job card: {str(e)}")
                continue
        
        return jobs

