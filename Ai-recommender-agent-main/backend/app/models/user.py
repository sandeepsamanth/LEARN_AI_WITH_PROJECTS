from sqlalchemy import Column, String, DateTime, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    phone = Column(String(20))
    
    # Profile data
    resume_text = Column(Text)
    resume_embedding = Column(Vector(1536))  # pgvector embedding (1536 dimensions for text-embedding-3-small)
    skills = Column(JSON, default=list)  # List of skill names
    experience_years = Column(String(50))
    education_level = Column(String(100))
    preferred_locations = Column(JSON, default=list)
    preferred_job_types = Column(JSON, default=list)  # full-time, internship, etc.
    
    # Onboarding status
    onboarding_completed = Column(Boolean, default=False)
    profile_data = Column(JSON, default=dict)  # Additional profile info
    
    # Admin status
    is_admin = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    saved_jobs = relationship("SavedJob", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    user_skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"







