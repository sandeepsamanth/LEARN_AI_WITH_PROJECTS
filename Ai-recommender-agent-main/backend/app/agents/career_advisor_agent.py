"""
Career Advisor Agent using LangGraph
Provides career advice via chat interface
"""
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from app.models.user import User
from app.models.job import JobPosting
from sqlalchemy.orm import Session


class AdvisorState(TypedDict):
    user_id: str
    user_message: str
    conversation_history: List[Dict]
    relevant_jobs: List[Dict]
    response: str
    errors: List[str]


def retrieve_context_node(state: AdvisorState) -> AdvisorState:
    """Retrieve relevant context (jobs, user profile)"""
    from app.utils.embeddings import embedding_generator
    from app.core.database import get_db
    
    user_message = state.get("user_message", "")
    
    # Generate embedding for user message
    query_embedding = embedding_generator.generate_embedding(user_message)
    
    # Get all jobs with embeddings
    db = next(get_db())
    jobs = db.query(JobPosting).filter(
        JobPosting.is_active == True,
        JobPosting.description_embedding.isnot(None)
    ).limit(50).all()
    
    # Calculate similarities
    job_scores = []
    for job in jobs:
        try:
            # Handle pgvector embedding (may be list, numpy array, or JSON string)
            job_embedding = job.description_embedding
            if job_embedding is None:
                continue
                
            # Convert to list if needed
            if isinstance(job_embedding, list):
                job_embedding = list(job_embedding)
            elif hasattr(job_embedding, '__len__'):  # numpy array or similar
                job_embedding = list(job_embedding)
            else:
                job_embedding = embedding_generator.json_to_embedding(job_embedding)
            
            similarity = embedding_generator.cosine_similarity(query_embedding, job_embedding)
            job_scores.append((job, similarity))
        except Exception as e:
            print(f"Error calculating similarity for job {job.id}: {e}")
            continue
    
    # Sort by similarity and get top 5
    job_scores.sort(key=lambda x: x[1], reverse=True)
    relevant_jobs = [
        {
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "description": job.description[:200],
            "similarity": similarity
        }
        for job, similarity in job_scores[:5]
    ]
    
    return {
        **state,
        "relevant_jobs": relevant_jobs
    }


def generate_response_node(state: AdvisorState) -> AdvisorState:
    """Generate response using LLM"""
    from app.utils.llm import llm_service
    
    user_message = state.get("user_message", "")
    conversation_history = state.get("conversation_history", [])
    relevant_jobs = state.get("relevant_jobs", [])
    
    # Build context
    context = ""
    if relevant_jobs:
        context = "\n\nRelevant job opportunities:\n"
        for job in relevant_jobs:
            context += f"- {job['title']} at {job['company']}: {job['description']}\n"
    
    # Build conversation history
    history_text = ""
    for msg in conversation_history[-5:]:  # Last 5 messages
        history_text += f"{msg.get('role', 'user')}: {msg.get('content', '')}\n"
    
    system_prompt = """You are a helpful career advisor AI assistant. You help users with:
- Career guidance and advice
- Job search strategies
- Skill development recommendations
- Interview preparation
- Career path planning

Be friendly, professional, and provide actionable advice. Reference relevant job opportunities when appropriate."""
    
    user_prompt = f"""Previous conversation:
{history_text}

User question: {user_message}
{context}

Provide a helpful response:"""
    
    try:
        response = llm_service.generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1000
        )
    except Exception as e:
        response = f"I apologize, but I'm having trouble processing your request right now. Please try again later. Error: {str(e)}"
    
    return {
        **state,
        "response": response
    }


def create_career_advisor_agent():
    """Create the Career Advisor Agent workflow"""
    workflow = StateGraph(AdvisorState)
    
    # Add nodes
    workflow.add_node("retrieve_context", retrieve_context_node)
    workflow.add_node("generate_response", generate_response_node)
    
    # Set entry point
    workflow.set_entry_point("retrieve_context")
    
    # Add edges
    workflow.add_edge("retrieve_context", "generate_response")
    workflow.add_edge("generate_response", END)
    
    return workflow.compile()


# Global agent instance
career_advisor_agent = create_career_advisor_agent()







