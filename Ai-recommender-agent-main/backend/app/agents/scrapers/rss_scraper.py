"""
RSS Feed scraper
Scrapes job postings from RSS feeds
"""
from typing import List, Dict
import feedparser
from app.agents.scrapers.base_scraper import BaseScraper


class RSSScraper(BaseScraper):
    """Scraper for RSS feeds"""
    
    # Common job board RSS feeds
    RSS_FEEDS = [
        "https://jobs.github.com/positions.atom",
        "https://stackoverflow.com/jobs/feed",
        # Add more RSS feeds as needed
    ]
    
    def scrape(self, search_terms: List[str]) -> List[Dict]:
        """Scrape jobs from RSS feeds"""
        all_jobs = []
        
        for feed_url in self.RSS_FEEDS:
            try:
                self._rate_limit()
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    # Check if matches search terms
                    if not search_terms or any(
                        term.lower() in entry.get("title", "").lower() or
                        term.lower() in entry.get("summary", "").lower()
                        for term in search_terms
                    ):
                        job = self._parse_rss_entry(entry, feed_url)
                        all_jobs.append(job)
            except Exception as e:
                print(f"Error scraping RSS feed {feed_url}: {str(e)}")
        
        return all_jobs
    
    def _parse_rss_entry(self, entry: Dict, feed_url: str) -> Dict:
        """Parse an RSS entry into job format"""
        # Extract company from various possible fields
        company = entry.get("author", "") or entry.get("company", "") or "Unknown"
        
        return {
            "title": entry.get("title", ""),
            "company": company,
            "location": entry.get("location", ""),
            "description": entry.get("summary", ""),
            "source_url": entry.get("link", ""),
            "source": "rss",
            "published": entry.get("published", "")
        }







