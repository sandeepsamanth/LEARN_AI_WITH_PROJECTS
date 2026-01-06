"""
Market Data Scraper Agent using LangGraph
Scrapes job postings from multiple sources (no paid APIs)
"""
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
# Scrapers will be imported when needed


class ScraperState(TypedDict):
    source: str
    search_terms: List[str]
    scraped_jobs: List[Dict]
    normalized_jobs: List[Dict]
    errors: List[str]


def select_scraper_node(state: ScraperState) -> ScraperState:
    """Select appropriate scraper based on source"""
    return state


def scrape_jobs_node(state: ScraperState) -> ScraperState:
    """Scrape jobs from selected source (real-time only, no sample/test jobs)"""
    source = state.get("source", "")
    search_terms = state.get("search_terms", [])
    
    scraper = None
    if source == "indeed":
        from app.agents.scrapers.indeed_scraper import IndeedScraper
        scraper = IndeedScraper()
    elif source == "remoteok":
        from app.agents.scrapers.remoteok_scraper import RemoteOKScraper
        scraper = RemoteOKScraper()
    elif source == "rss":
        from app.agents.scrapers.rss_scraper import RSSScraper
        scraper = RSSScraper()
    else:
        return {
            **state,
            "errors": state.get("errors", []) + [f"Unknown source: {source}. Supported sources: indeed, remoteok, rss"]
        }
    
    try:
        print(f"Scraping real-time jobs from {source} with terms: {search_terms}")
        scraped_jobs = scraper.scrape(search_terms)
        print(f"Scraped {len(scraped_jobs)} real jobs from {source}")
        
        if len(scraped_jobs) == 0:
            error_msg = f"No jobs found from {source} for search terms: {search_terms}. Try different search terms or another source."
            print(error_msg)
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg],
                "scraped_jobs": []
            }
        
        return {
            **state,
            "scraped_jobs": scraped_jobs
        }
    except Exception as e:
        error_msg = f"Error scraping from {source}: {str(e)}"
        print(error_msg)
        return {
            **state,
            "errors": state.get("errors", []) + [error_msg],
            "scraped_jobs": []
        }


def normalize_jobs_node(state: ScraperState) -> ScraperState:
    """Normalize scraped jobs to unified schema"""
    from app.agents.scrapers.job_normalizer import normalize_job
    
    scraped_jobs = state.get("scraped_jobs", [])
    normalized_jobs = []
    
    for job in scraped_jobs:
        try:
            normalized = normalize_job(job, state.get("source", ""))
            normalized_jobs.append(normalized)
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Normalization error: {str(e)}"]
    
    return {
        **state,
        "normalized_jobs": normalized_jobs
    }


def create_scraper_agent():
    """Create the Scraper Agent workflow"""
    workflow = StateGraph(ScraperState)
    
    # Add nodes
    workflow.add_node("select_scraper", select_scraper_node)
    workflow.add_node("scrape_jobs", scrape_jobs_node)
    workflow.add_node("normalize_jobs", normalize_jobs_node)
    
    # Set entry point
    workflow.set_entry_point("select_scraper")
    
    # Add edges
    workflow.add_edge("select_scraper", "scrape_jobs")
    workflow.add_edge("scrape_jobs", "normalize_jobs")
    workflow.add_edge("normalize_jobs", END)
    
    return workflow.compile()


# Global agent instance
scraper_agent = create_scraper_agent()

