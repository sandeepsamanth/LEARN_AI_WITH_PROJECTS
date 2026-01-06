"""
Scrapers module - Real-time job scraping only
"""
from app.agents.scrapers.base_scraper import BaseScraper
from app.agents.scrapers.indeed_scraper import IndeedScraper
from app.agents.scrapers.remoteok_scraper import RemoteOKScraper
from app.agents.scrapers.rss_scraper import RSSScraper

__all__ = [
    "BaseScraper",
    "IndeedScraper",
    "RemoteOKScraper",
    "RSSScraper"
]

