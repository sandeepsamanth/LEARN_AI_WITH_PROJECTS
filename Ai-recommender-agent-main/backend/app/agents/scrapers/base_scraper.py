"""
Base scraper class for all job scrapers
"""
from abc import ABC, abstractmethod
from typing import List, Dict
import time
import requests
from bs4 import BeautifulSoup
from app.core.config import settings


class BaseScraper(ABC):
    """Abstract base class for all job scrapers"""
    
    def __init__(self):
        self.rate_limit_delay = 60 / settings.SCRAPING_RATE_LIMIT  # seconds between requests
        self.last_request_time = 0
        self.headers = {
            "User-Agent": settings.SCRAPING_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
    
    def _rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a web page"""
        self._rate_limit()
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            raise Exception(f"Error fetching {url}: {str(e)}")
    
    @abstractmethod
    def scrape(self, search_terms: List[str]) -> List[Dict]:
        """
        Scrape jobs based on search terms
        
        Args:
            search_terms: List of search terms (e.g., ["software engineer", "python developer"])
            
        Returns:
            List of job dictionaries with raw scraped data
        """
        pass
    
    def _extract_text(self, element) -> str:
        """Safely extract text from BeautifulSoup element"""
        if element is None:
            return ""
        return element.get_text(strip=True)







