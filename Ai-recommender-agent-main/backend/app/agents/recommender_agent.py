"""
Recommender Agent using LangGraph
Generates personalized job recommendations based on user profile
"""
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from app.models.user import User
from app.models.job import JobPosting
from sqlalchemy.orm import Session


class RecommenderState(TypedDict):
    user_id: str
    user_skills: List[str]
    user_embedding: List[float]
    job_candidates: List[Dict]
    scored_jobs: List[Dict]
    recommendations: List[Dict]
    errors: List[str]


def get_user_embedding_node(state: RecommenderState) -> RecommenderState:
    """Get or generate user embedding"""
    # This is handled in get_recommendations function
    return state


def fetch_job_candidates_node(state: RecommenderState) -> RecommenderState:
    """Fetch job candidates from database"""
    # This is handled in get_recommendations function
    return state


def normalize_skill(skill: str) -> str:
    """Normalize skill name for comparison (lowercase, strip, handle variations)"""
    if not skill:
        return ""
    # Convert to lowercase and strip whitespace
    normalized = skill.lower().strip()
    
    # Remove common suffixes/prefixes
    normalized = normalized.replace("-", " ").replace("_", " ").replace(".", "")
    
    # Handle common variations and aliases
    variations = {
        "node.js": "nodejs",
        "node js": "nodejs",
        "nodejs": "nodejs",
        "machine learning": "ml",
        "artificial intelligence": "ai",
        "ai": "ai",
        "data science": "datascience",
        "datascience": "datascience",
        "javascript": "js",
        "js": "js",
        "typescript": "ts",
        "ts": "ts",
        "c++": "cpp",
        "cplusplus": "cpp",
        "cpp": "cpp",
        "expressjs": "express",
        "express.js": "express",
        "express": "express",
        "fastapi": "fastapi",
        "fast api": "fastapi",
        "scikit-learn": "scikitlearn",
        "scikitlearn": "scikitlearn",
        "scikit learn": "scikitlearn",
        "llm models": "llm",
        "llm": "llm",
        "deep learning": "deeplearning",
        "deeplearning": "deeplearning",
        "prompt engineering": "promptengineering",
        "promptengineering": "promptengineering",
    }
    return variations.get(normalized, normalized)


def score_jobs_node(state: RecommenderState) -> RecommenderState:
    """Score jobs based on similarity and skill matching"""
    from app.utils.embeddings import embedding_generator
    
    user_embedding = state.get("user_embedding")
    # Normalize user skills for comparison
    user_skills_raw = state.get("user_skills", [])
    user_skills_normalized = {normalize_skill(skill) for skill in user_skills_raw if skill}
    job_candidates = state.get("job_candidates", [])
    
    scored_jobs = []
    
    for job in job_candidates:
        # Vector similarity
        similarity_score = 0.0
        if job.get("description_embedding") is not None and user_embedding is not None:
            try:
                job_embedding = job["description_embedding"]
                # Ensure both are lists
                if not isinstance(job_embedding, list):
                    job_embedding = embedding_generator.json_to_embedding(job_embedding)
                similarity_score = embedding_generator.cosine_similarity(
                    user_embedding, job_embedding
                )
                # Ensure similarity is between 0 and 1
                similarity_score = max(0.0, min(1.0, similarity_score))
            except Exception as e:
                print(f"Error calculating similarity: {e}")
                similarity_score = 0.0
        
        # Skill matching with normalized comparison
        job_skills_raw = job.get("required_skills", [])
        job_skills_normalized = {normalize_skill(skill) for skill in job_skills_raw if skill}
        
        # Count matching skills (case-insensitive, normalized)
        skill_match_count = len(user_skills_normalized.intersection(job_skills_normalized))
        skill_match_ratio = skill_match_count / len(job_skills_normalized) if job_skills_normalized else 0.0
        
        # If no embeddings available, rely more on skill matching
        if similarity_score == 0.0 and skill_match_ratio > 0:
            # Boost skill-based score when no embedding similarity
            combined_score = skill_match_ratio * 0.8  # Higher weight for skill-only matching
        else:
            # Combined score (weighted) - prioritize skill matching more
            combined_score = (similarity_score * 0.5) + (skill_match_ratio * 0.5)
        
        # Include jobs if they have:
        # 1. Any skill match (even if score is low)
        # 2. Or similarity score > 0.3 (reasonable match)
        # 3. Or combined score > 0.1 (some relevance)
        if skill_match_count > 0 or similarity_score > 0.3 or combined_score > 0.1:
            scored_jobs.append({
                **job,
                "similarity_score": similarity_score,
                "skill_match_count": skill_match_count,
                "skill_match_ratio": skill_match_ratio,
                "combined_score": combined_score
            })
    
    # Sort by combined score (descending)
    scored_jobs.sort(key=lambda x: x["combined_score"], reverse=True)
    
    return {
        **state,
        "scored_jobs": scored_jobs
    }


def generate_recommendations_node(state: RecommenderState) -> RecommenderState:
    """Generate final recommendations with explanations"""
    from app.utils.llm import llm_service
    
    scored_jobs = state.get("scored_jobs", [])
    top_jobs = scored_jobs[:10]  # Top 10
    
    recommendations = []
    for job in top_jobs:
        # Generate explanation using LLM
        explanation = ""
        try:
            prompt = f"""Explain why this job matches the user:
Job: {job.get('title')} at {job.get('company')}
Required Skills: {', '.join(job.get('required_skills', [])[:5])}
Match Score: {job.get('combined_score', 0):.2%}
Similarity: {job.get('similarity_score', 0):.2%}
Skills Match: {job.get('skill_match_count', 0)}/{len(job.get('required_skills', []))}

Provide a brief 1-2 sentence explanation."""
            
            explanation = llm_service.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=150
            )
        except:
            explanation = f"Good match based on skills and job description similarity."
        
        recommendations.append({
            **job,
            "explanation": explanation
        })
    
    return {
        **state,
        "recommendations": recommendations
    }


def create_recommender_agent():
    """Create the Recommender Agent workflow"""
    workflow = StateGraph(RecommenderState)
    
    # Add nodes
    workflow.add_node("get_user_embedding", get_user_embedding_node)
    workflow.add_node("fetch_job_candidates", fetch_job_candidates_node)
    workflow.add_node("score_jobs", score_jobs_node)
    workflow.add_node("generate_recommendations", generate_recommendations_node)
    
    # Set entry point
    workflow.set_entry_point("get_user_embedding")
    
    # Add edges
    workflow.add_edge("get_user_embedding", "fetch_job_candidates")
    workflow.add_edge("fetch_job_candidates", "score_jobs")
    workflow.add_edge("score_jobs", "generate_recommendations")
    workflow.add_edge("generate_recommendations", END)
    
    return workflow.compile()


# Global agent instance
recommender_agent = create_recommender_agent()


def get_recommendations(user: User, db: Session, limit: int = 10) -> List[dict]:
    """
    Get job recommendations for a user
    
    Args:
        user: User object
        db: Database session
        limit: Number of recommendations to return
        
    Returns:
        List of recommended jobs with scores
    """
    from app.utils.embeddings import embedding_generator
    
    # Get user embedding - use stored embedding if available, otherwise generate
    user_embedding = None
    if user.resume_embedding is not None:
        # pgvector stores as array, convert to list if needed
        if isinstance(user.resume_embedding, list):
            user_embedding = list(user.resume_embedding)  # Ensure it's a Python list
        elif hasattr(user.resume_embedding, '__len__'):  # numpy array or similar
            user_embedding = list(user.resume_embedding)
        else:
            try:
                user_embedding = embedding_generator.json_to_embedding(user.resume_embedding)
            except:
                pass
    
    # If no stored embedding, generate from resume text and skills
    if not user_embedding:
        # Build user profile text from available data
        user_parts = []
        if user.resume_text:
            user_parts.append(user.resume_text)
        if user.skills:
            user_parts.append(f"Skills: {', '.join(user.skills)}")
        if user.experience_years:
            user_parts.append(f"Experience: {user.experience_years} years")
        if user.education_level:
            user_parts.append(f"Education: {user.education_level}")
        
        user_text = " ".join(user_parts)
        
        if user_text.strip():
            try:
                user_embedding = embedding_generator.generate_embedding(user_text)
                # Store the embedding directly (pgvector handles arrays)
                user.resume_embedding = user_embedding
                db.commit()
                print(f"Generated and stored user embedding for user {user.id}")
            except Exception as e:
                print(f"Error generating user embedding: {e}")
                # Don't return empty - continue with skill-based matching only
                user_embedding = None
        else:
            print(f"Warning: No user text available for embedding generation for user {user.id}")
            user_embedding = None
    
    # Prepare state
    initial_state = {
        "user_id": str(user.id),
        "user_skills": user.skills or [],
        "user_embedding": user_embedding,
        "job_candidates": [],
        "scored_jobs": [],
        "recommendations": [],
        "errors": []
    }
    
    # Fetch jobs (we'll do this outside the agent for now)
    # Increase limit to get more candidates for better matching
    jobs = db.query(JobPosting).filter(JobPosting.is_active == True).limit(500).all()
    
    print(f"Found {len(jobs)} active jobs for user {user.id}")
    
    job_candidates = []
    jobs_with_embeddings = 0
    jobs_without_embeddings = 0
    
    for job in jobs:
        job_embedding = None
        
        # Try to get job embedding if available
        if job.description_embedding is not None:
            try:
                # Convert pgvector embedding to list if needed
                if isinstance(job.description_embedding, list):
                    job_embedding = list(job.description_embedding)
                elif hasattr(job.description_embedding, '__len__'):
                    job_embedding = list(job.description_embedding)
                else:
                    job_embedding = embedding_generator.json_to_embedding(job.description_embedding)
                jobs_with_embeddings += 1
            except Exception as e:
                print(f"Error processing job embedding for job {job.id}: {e}")
                job_embedding = None
        
        # Include job even if it doesn't have embedding (will use skill matching only)
        # This ensures jobs with matching skills are still recommended
        job_candidates.append({
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "job_type": job.job_type,
            "description": job.description,
            "required_skills": job.required_skills or [],
            "description_embedding": job_embedding,
            "application_url": job.application_url,
            "source": job.source,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
        })
        
        if job_embedding is None:
            jobs_without_embeddings += 1
    
    print(f"Jobs with embeddings: {jobs_with_embeddings}, without: {jobs_without_embeddings}")
    print(f"User skills: {user.skills or []}")
    
    initial_state["job_candidates"] = job_candidates
    
    # Run scoring
    state_after_scoring = score_jobs_node(initial_state)
    
    # Get top recommendations
    scored_jobs = state_after_scoring.get("scored_jobs", [])
    
    print(f"Total scored jobs: {len(scored_jobs)}")
    if scored_jobs:
        print(f"Score range: {min(j.get('combined_score', 0) for j in scored_jobs):.3f} - {max(j.get('combined_score', 0) for j in scored_jobs):.3f}")
        print(f"Jobs with skill matches: {sum(1 for j in scored_jobs if j.get('skill_match_count', 0) > 0)}")
        print(f"Jobs with similarity > 0.3: {sum(1 for j in scored_jobs if j.get('similarity_score', 0) > 0.3)}")
    
    # Filter: Keep jobs with any skill match or reasonable similarity
    # Lower thresholds to ensure users get recommendations
    filtered_jobs = [
        job for job in scored_jobs 
        if (job.get("skill_match_count", 0) > 0 or 
            job.get("similarity_score", 0) > 0.15 or  # Lower threshold
            job.get("combined_score", 0) > 0.01)  # Very low threshold
    ]
    
    # If still no jobs, include top jobs by similarity score alone
    if not filtered_jobs and scored_jobs:
        print("Warning: No jobs passed filter, including top jobs by similarity")
        # Sort by similarity score and take top ones
        scored_jobs.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        filtered_jobs = scored_jobs[:limit]
    
    # Sort again by combined score (in case filtering changed order)
    filtered_jobs.sort(key=lambda x: x.get("combined_score", 0), reverse=True)
    
    # Get top N recommendations
    top_jobs = filtered_jobs[:limit]
    
    print(f"Returning {len(top_jobs)} recommendations for user {user.id}")
    if top_jobs:
        for i, job in enumerate(top_jobs[:3], 1):
            print(f"  {i}. {job.get('title')} - Score: {job.get('combined_score', 0):.3f}, "
                  f"Similarity: {job.get('similarity_score', 0):.3f}, "
                  f"Skills: {job.get('skill_match_count', 0)}/{len(job.get('required_skills', []))}")
    else:
        print(f"WARNING: No recommendations found for user {user.id}")
        print(f"  - User skills: {user.skills or []}")
        print(f"  - Total jobs available: {len(job_candidates)}")
        print(f"  - Jobs with embeddings: {jobs_with_embeddings}")
        print(f"  - Jobs with skills: {sum(1 for j in job_candidates if j.get('required_skills'))}")
    
    return top_jobs







