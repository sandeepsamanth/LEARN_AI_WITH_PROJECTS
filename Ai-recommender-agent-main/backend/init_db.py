"""
Initialize database and create all tables
"""
import sys
from sqlalchemy import create_engine
from app.core.config import settings
from app.core.database import Base
from app.models import user, job, conversation, skill


def init_database():
    """Create database and all tables"""
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Import all models to ensure they're registered
        from app.models.user import User
        from app.models.job import JobPosting, SavedJob
        from app.models.conversation import Conversation, Message
        from app.models.skill import Skill, UserSkill, JobSkill
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Enable pgvector extension
        with engine.connect() as connection:
            connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
            connection.commit()
        
        print("✓ Database initialized successfully")
        print("✓ All tables created")
        print("✓ pgvector extension enabled")
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your DATABASE_URL in .env file")
        print("3. Ensure the database exists (run create_database.py first)")
        sys.exit(1)


if __name__ == "__main__":
    init_database()







