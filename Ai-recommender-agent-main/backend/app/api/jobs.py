from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_user_optional
from app.models.job import JobPosting, SavedJob
from app.models.user import User
from datetime import datetime

router = APIRouter()


class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    location: str
    description: str
    job_type: str
    experience_level: Optional[str]
    salary_min: Optional[float]
    salary_max: Optional[float]
    source: str
    source_url: str
    posted_date: Optional[str]
    application_url: Optional[str]
    required_skills: List[str]
    is_saved: bool = False
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    page_size: int


@router.get("/", response_model=JobListResponse)
async def get_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    company: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get list of job postings with filters"""
    query = db.query(JobPosting).filter(JobPosting.is_active == True)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                JobPosting.title.ilike(f"%{search}%"),
                JobPosting.description.ilike(f"%{search}%"),
                JobPosting.company.ilike(f"%{search}%")
            )
        )
    
    if location:
        query = query.filter(JobPosting.location.ilike(f"%{location}%"))
    
    if job_type:
        query = query.filter(JobPosting.job_type == job_type)
    
    if company:
        query = query.filter(JobPosting.company.ilike(f"%{company}%"))
    
    # Get total count
    total = query.count()
    
    # Pagination
    offset = (page - 1) * page_size
    # Order by created_at desc (most recent first)
    jobs = query.order_by(desc(JobPosting.created_at)).offset(offset).limit(page_size).all()
    
    # Check if jobs are saved by current user
    saved_job_ids = set()
    if current_user:
        saved_jobs = db.query(SavedJob.job_id).filter(SavedJob.user_id == current_user.id).all()
        saved_job_ids = {str(job_id[0]) for job_id in saved_jobs}
    
    job_responses = []
    for job in jobs:
        job_dict = {
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description[:500] + "..." if len(job.description) > 500 else job.description,
            "job_type": job.job_type,
            "experience_level": job.experience_level,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "source": job.source,
            "source_url": job.source_url,
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
            "application_url": job.application_url,
            "required_skills": job.required_skills or [],
            "is_saved": str(job.id) in saved_job_ids
        }
        job_responses.append(JobResponse(**job_dict))
    
    return {
        "jobs": job_responses,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get a single job posting by ID"""
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    is_saved = False
    if current_user:
        saved = db.query(SavedJob).filter(
            SavedJob.user_id == current_user.id,
            SavedJob.job_id == job_id
        ).first()
        is_saved = saved is not None
    
    return JobResponse(
        id=str(job.id),
        title=job.title,
        company=job.company,
        location=job.location,
        description=job.description,
        job_type=job.job_type,
        experience_level=job.experience_level,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        source=job.source,
        source_url=job.source_url,
        posted_date=job.posted_date.isoformat() if job.posted_date else None,
        application_url=job.application_url,
        required_skills=job.required_skills or [],
        is_saved=is_saved
    )


@router.post("/{job_id}/save")
async def save_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save a job for the current user"""
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if already saved
    existing = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id == job_id
    ).first()
    
    if existing:
        return {"message": "Job already saved", "saved_job_id": str(existing.id)}
    
    saved_job = SavedJob(
        user_id=current_user.id,
        job_id=job.id
    )
    db.add(saved_job)
    db.commit()
    db.refresh(saved_job)
    
    return {"message": "Job saved successfully", "saved_job_id": str(saved_job.id)}


@router.delete("/{job_id}/save")
async def unsave_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a saved job"""
    saved_job = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id == job_id
    ).first()
    
    if not saved_job:
        raise HTTPException(status_code=404, detail="Saved job not found")
    
    db.delete(saved_job)
    db.commit()
    
    return {"message": "Job unsaved successfully"}


@router.get("/saved/list", response_model=JobListResponse)
async def get_saved_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's saved jobs"""
    query = db.query(JobPosting).join(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        JobPosting.is_active == True
    )
    
    total = query.count()
    offset = (page - 1) * page_size
    jobs = query.order_by(SavedJob.created_at.desc()).offset(offset).limit(page_size).all()
    
    job_responses = []
    for job in jobs:
        job_dict = {
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description[:500] + "..." if len(job.description) > 500 else job.description,
            "job_type": job.job_type,
            "experience_level": job.experience_level,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "source": job.source,
            "source_url": job.source_url,
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
            "application_url": job.application_url,
            "required_skills": job.required_skills or [],
            "is_saved": True
        }
        job_responses.append(JobResponse(**job_dict))
    
    return {
        "jobs": job_responses,
        "total": total,
        "page": page,
        "page_size": page_size
    }







