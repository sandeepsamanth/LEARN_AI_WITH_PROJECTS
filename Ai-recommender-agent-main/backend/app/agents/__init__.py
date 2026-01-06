"""
AI Agents module
"""
from app.agents.resume_parser_agent import resume_parser_agent
from app.agents.recommender_agent import recommender_agent, get_recommendations
from app.agents.career_advisor_agent import career_advisor_agent
from app.agents.scraper_agent import scraper_agent

__all__ = [
    "resume_parser_agent",
    "recommender_agent",
    "get_recommendations",
    "career_advisor_agent",
    "scraper_agent"
]







