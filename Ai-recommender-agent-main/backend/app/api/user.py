from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.job import JobPosting
from app.utils.resume_parser import resume_parser
from app.utils.embeddings import embedding_generator
from app.agents.skill_gap_agent import analyze_skill_gap
import os
import uuid
from app.core.config import settings

router = APIRouter()


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[str] = None
    education_level: Optional[str] = None
    preferred_locations: Optional[List[str]] = None
    preferred_job_types: Optional[List[str]] = None
    onboarding_completed: Optional[bool] = None


@router.patch("/profile")
async def update_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user profile"""
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name
    if profile_data.skills is not None:
        current_user.skills = profile_data.skills
    if profile_data.experience_years is not None:
        current_user.experience_years = profile_data.experience_years
    if profile_data.education_level is not None:
        current_user.education_level = profile_data.education_level
    if profile_data.preferred_locations is not None:
        current_user.preferred_locations = profile_data.preferred_locations
    if profile_data.preferred_job_types is not None:
        current_user.preferred_job_types = profile_data.preferred_job_types
    if profile_data.onboarding_completed is not None:
        current_user.onboarding_completed = profile_data.onboarding_completed
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Profile updated successfully",
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "onboarding_completed": current_user.onboarding_completed
        }
    }


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and parse resume"""
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save file
    file_extension = os.path.splitext(file.filename)[1]
    file_path = os.path.join(settings.UPLOAD_DIR, f"{current_user.id}_{uuid.uuid4()}{file_extension}")
    
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Parse resume
        parsed_data = resume_parser.parse(file_path, use_llm=True)
        
        # Update user profile with parsed data
        if parsed_data.get("skills"):
            current_user.skills = parsed_data["skills"]
        if parsed_data.get("experience_years"):
            current_user.experience_years = parsed_data["experience_years"]
        if parsed_data.get("education_level"):
            current_user.education_level = parsed_data["education_level"]
        if parsed_data.get("full_name"):
            current_user.full_name = parsed_data["full_name"]
        
        # Store resume text
        resume_text = resume_parser.extract_text(file_path)
        current_user.resume_text = resume_text
        
        # Generate embedding
        if resume_text:
            embedding = embedding_generator.generate_embedding(resume_text)
            current_user.resume_embedding = embedding  # pgvector stores arrays directly
        
        db.commit()
        
        # Clean up file
        os.remove(file_path)
        
        return {
            "message": "Resume uploaded and parsed successfully",
            "parsed_data": parsed_data
        }
        
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Error processing resume: {str(e)}")


@router.get("/profile")
async def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user profile"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "skills": current_user.skills or [],
        "experience_years": current_user.experience_years,
        "education_level": current_user.education_level,
        "preferred_locations": current_user.preferred_locations or [],
        "preferred_job_types": current_user.preferred_job_types or [],
        "onboarding_completed": current_user.onboarding_completed,
        "is_admin": current_user.is_admin or False
    }


@router.get("/skill-gap/{job_id}")
async def get_skill_gap_analysis(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get skill gap analysis for a specific job"""
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    analysis = analyze_skill_gap(current_user, job, db)
    return analysis





