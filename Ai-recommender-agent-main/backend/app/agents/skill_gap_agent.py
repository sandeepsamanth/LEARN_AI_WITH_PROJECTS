"""
Skill Gap Analysis Agent using LangGraph
Identifies skill gaps by comparing user skills vs job requirements

Usage:
    1. Via API: GET /api/user/skill-gap/{job_id}
    2. Programmatically: analyze_skill_gap(user, job, db)
    3. Direct agent: skill_gap_agent.invoke(state)

Example:
    from app.agents.skill_gap_agent import analyze_skill_gap
    analysis = analyze_skill_gap(user, job, db)
    print(f"Match: {analysis['skill_gap_analysis']['match_percentage']}%")
    print(f"Missing: {analysis['missing_skills']}")

Returns:
    Dictionary with:
    - job_id, job_title, job_company
    - user_skills, job_required_skills
    - user_has_skills, missing_skills
    - skill_gap_analysis (match %, analysis text, priority skills)
    - recommendations (AI-generated learning suggestions)
"""
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from app.models.user import User
from app.models.job import JobPosting
from sqlalchemy.orm import Session
from app.utils.llm import llm_service


class SkillGapState(TypedDict):
    user_id: str
    user_skills: List[str]
    job_id: str
    job_required_skills: List[str]
    user_has_skills: List[str]
    missing_skills: List[str]
    skill_gap_analysis: Dict
    recommendations: List[str]
    errors: List[str]


def analyze_skills_node(state: SkillGapState) -> SkillGapState:
    """Analyze which skills user has vs what's required"""
    user_skills = set(state.get("user_skills", []))
    job_required_skills = set(state.get("job_required_skills", []))
    
    # Find matching and missing skills
    user_has_skills = list(user_skills.intersection(job_required_skills))
    missing_skills = list(job_required_skills - user_skills)
    
    return {
        **state,
        "user_has_skills": user_has_skills,
        "missing_skills": missing_skills
    }


def generate_gap_analysis_node(state: SkillGapState) -> SkillGapState:
    """Generate detailed skill gap analysis using LLM"""
    user_has_skills = state.get("user_has_skills", [])
    missing_skills = state.get("missing_skills", [])
    job_required_skills = state.get("job_required_skills", [])
    
    # Calculate match percentage
    match_percentage = (len(user_has_skills) / len(job_required_skills) * 100) if job_required_skills else 0
    
    # Generate detailed analysis using LLM
    analysis_text = ""
    recommendations = []
    
    try:
        prompt = f"""Analyze the skill gap for a job application:

User's Current Skills: {', '.join(state.get('user_skills', [])[:20])}
Job Required Skills: {', '.join(job_required_skills[:20])}
Skills User Has: {', '.join(user_has_skills[:20])}
Missing Skills: {', '.join(missing_skills[:20])}
Match Percentage: {match_percentage:.1f}%

Provide:
1. A brief analysis of the skill gap
2. Top 5 actionable recommendations to bridge the gap
3. Priority skills to learn first

Format as JSON with keys: analysis, recommendations (array), priority_skills (array)"""
        
        response = llm_service.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=500
        )
        
        # Try to parse JSON from response
        import json
        import re
        
        # Extract JSON from response if it's wrapped in markdown
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                analysis_data = json.loads(json_match.group())
                analysis_text = analysis_data.get("analysis", response)
                recommendations = analysis_data.get("recommendations", [])
                priority_skills = analysis_data.get("priority_skills", missing_skills[:5])
            except:
                analysis_text = response
                recommendations = missing_skills[:5] if missing_skills else []
        else:
            analysis_text = response
            recommendations = missing_skills[:5] if missing_skills else []
            
    except Exception as e:
        print(f"Error generating gap analysis: {e}")
        analysis_text = f"Match: {match_percentage:.1f}%. Missing skills: {', '.join(missing_skills[:10])}"
        recommendations = missing_skills[:5] if missing_skills else []
    
    skill_gap_analysis = {
        "match_percentage": match_percentage,
        "skills_matched": len(user_has_skills),
        "skills_missing": len(missing_skills),
        "total_required": len(job_required_skills),
        "analysis": analysis_text,
        "priority_skills": recommendations[:5] if isinstance(recommendations, list) else []
    }
    
    return {
        **state,
        "skill_gap_analysis": skill_gap_analysis,
        "recommendations": recommendations if isinstance(recommendations, list) else []
    }


def create_skill_gap_agent():
    """Create the skill gap analysis agent workflow"""
    workflow = StateGraph(SkillGapState)
    
    # Add nodes
    workflow.add_node("analyze_skills", analyze_skills_node)
    workflow.add_node("generate_analysis", generate_gap_analysis_node)
    
    # Define edges
    workflow.set_entry_point("analyze_skills")
    workflow.add_edge("analyze_skills", "generate_analysis")
    workflow.add_edge("generate_analysis", END)
    
    return workflow.compile()


# Global agent instance
skill_gap_agent = create_skill_gap_agent()


def analyze_skill_gap(user: User, job: JobPosting, db: Session) -> Dict:
    """
    Analyze skill gap between user and a specific job
    
    Args:
        user: User object
        job: JobPosting object
        db: Database session
        
    Returns:
        Dictionary with skill gap analysis
    """
    # Get user skills
    user_skills = user.skills or []
    
    # Get job required skills
    job_required_skills = job.required_skills or []
    
    # Prepare initial state
    initial_state = {
        "user_id": str(user.id),
        "user_skills": user_skills,
        "job_id": str(job.id),
        "job_required_skills": job_required_skills,
        "user_has_skills": [],
        "missing_skills": [],
        "skill_gap_analysis": {},
        "recommendations": [],
        "errors": []
    }
    
    # Run agent
    result = skill_gap_agent.invoke(initial_state)
    
    return {
        "job_id": str(job.id),
        "job_title": job.title,
        "job_company": job.company,
        "user_skills": result.get("user_skills", []),
        "job_required_skills": result.get("job_required_skills", []),
        "user_has_skills": result.get("user_has_skills", []),
        "missing_skills": result.get("missing_skills", []),
        "skill_gap_analysis": result.get("skill_gap_analysis", {}),
        "recommendations": result.get("recommendations", [])
    }

