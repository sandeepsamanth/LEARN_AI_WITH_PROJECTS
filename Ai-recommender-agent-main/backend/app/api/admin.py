from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.job import JobPosting
from app.models.conversation import Conversation

router = APIRouter()


class AdminStats(BaseModel):
    total_users: int
    total_jobs: int
    active_jobs: int
    total_conversations: int
    jobs_by_source: dict


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    job_type: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


# Admin check using is_admin field
def is_admin(current_user: User) -> bool:
    """Check if user is admin"""
    return current_user.is_admin == True


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get admin statistics"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_users = db.query(User).count()
    total_jobs = db.query(JobPosting).count()
    active_jobs = db.query(JobPosting).filter(JobPosting.is_active == True).count()
    total_conversations = db.query(Conversation).count()
    
    # Jobs by source
    jobs_by_source = db.query(
        JobPosting.source,
        func.count(JobPosting.id).label('count')
    ).group_by(JobPosting.source).all()
    
    jobs_by_source_dict = {source: count for source, count in jobs_by_source}
    
    return {
        "total_users": total_users,
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_conversations": total_conversations,
        "jobs_by_source": jobs_by_source_dict
    }


@router.get("/jobs")
async def admin_get_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all jobs (admin view)"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(JobPosting)
    total = query.count()
    offset = (page - 1) * page_size
    jobs = query.order_by(JobPosting.created_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "jobs": [
            {
                "id": str(job.id),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "source": job.source,
                "is_active": job.is_active,
                "is_verified": job.is_verified,
                "created_at": job.created_at.isoformat() if job.created_at else None
            }
            for job in jobs
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/jobs/{job_id}")
async def get_job_details(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get job details (admin)"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": str(job.id),
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
        "job_type": job.job_type,
        "source": job.source,
        "source_url": job.source_url,
        "is_active": job.is_active,
        "is_verified": job.is_verified,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        "scraped_at": job.scraped_at.isoformat() if job.scraped_at else None,
        "metadata": job.job_metadata
    }


@router.patch("/jobs/{job_id}")
async def admin_update_job(
    job_id: str,
    job_update: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a job (admin)"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job_update.title is not None:
        job.title = job_update.title
    if job_update.company is not None:
        job.company = job_update.company
    if job_update.location is not None:
        job.location = job_update.location
    if job_update.description is not None:
        job.description = job_update.description
    if job_update.job_type is not None:
        job.job_type = job_update.job_type
    if job_update.is_active is not None:
        job.is_active = job_update.is_active
    if job_update.is_verified is not None:
        job.is_verified = job_update.is_verified
    
    job.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    
    return {"message": "Job updated successfully", "job_id": str(job.id)}


@router.delete("/jobs/{job_id}")
async def admin_delete_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a job (admin)"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.models.job import SavedJob
    from app.models.skill import JobSkill
    
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    try:
        # Delete related SavedJob records first (using bulk delete for efficiency)
        saved_jobs_count = db.query(SavedJob).filter(SavedJob.job_id == job_id).count()
        db.query(SavedJob).filter(SavedJob.job_id == job_id).delete()
        
        # Delete related JobSkill records (using bulk delete for efficiency)
        job_skills_count = db.query(JobSkill).filter(JobSkill.job_id == job_id).count()
        db.query(JobSkill).filter(JobSkill.job_id == job_id).delete()
        
        # Now delete the job itself
        db.delete(job)
        db.commit()
        
        return {
            "message": "Job deleted successfully",
            "deleted_saved_jobs": saved_jobs_count,
            "deleted_job_skills": job_skills_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting job: {str(e)}"
        )


@router.get("/users")
async def admin_get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all users (admin view)"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(User)
    
    if search:
        query = query.filter(
            or_(
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    offset = (page - 1) * page_size
    users = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "users": [
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "onboarding_completed": user.onboarding_completed,
                "skills_count": len(user.skills) if user.skills else 0,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
            for user in users
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


class ScrapeRequest(BaseModel):
    source: str
    search_terms: List[str]


@router.post("/jobs/scrape")
async def admin_trigger_scrape(
    request: ScrapeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger manual job scraping (admin) - Real-time scraping only"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Validate source - only allow real-time scraping sources
    valid_sources = ["indeed", "remoteok", "rss"]
    if request.source not in valid_sources:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source: {request.source}. Supported sources: {', '.join(valid_sources)}"
        )
    
    from app.agents.scraper_agent import scraper_agent
    
    # Run scraper agent
    initial_state = {
        "source": request.source,
        "search_terms": request.search_terms,
        "scraped_jobs": [],
        "normalized_jobs": [],
        "errors": []
    }
    
    result = scraper_agent.invoke(initial_state)
    normalized_jobs = result.get("normalized_jobs", [])
    errors = result.get("errors", [])
    
    # Store jobs in database
    saved_count = 0
    for job_data in normalized_jobs:
        try:
            # Check if job already exists
            existing = db.query(JobPosting).filter(
                JobPosting.source_url == job_data.get("source_url", "")
            ).first()
            
            if existing:
                continue  # Skip duplicates
            
            # Create new job
            job = JobPosting(
                title=job_data.get("title", ""),
                company=job_data.get("company", ""),
                location=job_data.get("location", "Remote"),
                description=job_data.get("description", ""),
                job_type=job_data.get("job_type", "full-time"),
                experience_level=job_data.get("experience_level"),
                salary_min=job_data.get("salary_min"),
                salary_max=job_data.get("salary_max"),
                salary_currency=job_data.get("salary_currency", "USD"),
                required_skills=job_data.get("required_skills", []),
                source=job_data.get("source", request.source),
                source_url=job_data.get("source_url", ""),
                posted_date=job_data.get("posted_date"),
                application_url=job_data.get("application_url", ""),
                description_embedding=job_data.get("description_embedding"),
                title_embedding=job_data.get("title_embedding"),
                job_metadata=job_data.get("job_metadata", {}),
                is_active=True,
                is_verified=False
            )
            
            db.add(job)
            saved_count += 1
        except Exception as e:
            errors.append(f"Error saving job: {str(e)}")
            continue
    
    db.commit()
    
    return {
        "message": "Scraping completed",
        "jobs_scraped": len(normalized_jobs),
        "jobs_saved": saved_count,
        "errors": errors
    }

