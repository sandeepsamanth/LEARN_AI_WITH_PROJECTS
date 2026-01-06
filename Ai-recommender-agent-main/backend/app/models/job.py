from sqlalchemy import Column, String, DateTime, Text, Boolean, JSON, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid
from app.core.database import Base


class JobPosting(Base):
    __tablename__ = "job_postings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic info
    title = Column(String(500), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255))  # Can be "Remote"
    description = Column(Text, nullable=False)
    
    # Job details
    job_type = Column(String(50))  # full-time, internship, part-time, contract
    experience_level = Column(String(50))  # entry, mid, senior
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String(10), default="USD")
    
    # Requirements
    required_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    requirements_text = Column(Text)
    
    # Source information
    source = Column(String(100), nullable=False, index=True)  # indeed, linkedin, etc.
    source_url = Column(String(1000), unique=True, nullable=False)
    source_id = Column(String(255), index=True)  # ID from source
    posted_date = Column(DateTime(timezone=True))
    application_url = Column(String(1000))
    
    # Embeddings and AI data
    description_embedding = Column(Vector(1536))  # pgvector embedding (1536 dimensions)
    title_embedding = Column(Vector(1536))  # pgvector embedding (1536 dimensions)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    job_metadata = Column(JSON, default=dict)  # Source-specific data (renamed from metadata to avoid SQLAlchemy conflict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    saved_by = relationship("SavedJob", back_populates="job")
    job_skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<JobPosting {self.title} at {self.company}>"


class SavedJob(Base):
    __tablename__ = "saved_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False, index=True)
    
    # User notes
    notes = Column(Text)
    status = Column(String(50), default="saved")  # saved, applied, rejected, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="saved_jobs")
    job = relationship("JobPosting", back_populates="saved_by")
    
    def __repr__(self):
        return f"<SavedJob user={self.user_id} job={self.job_id}>"







