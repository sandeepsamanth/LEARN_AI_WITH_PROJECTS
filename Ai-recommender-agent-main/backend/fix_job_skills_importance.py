"""
Add missing 'importance' column to job_skills table
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from app.core.config import settings

def add_importance_column():
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.begin() as connection:
            # Check if column exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='job_skills' AND column_name='importance'
            """)
            result = connection.execute(check_query)
            exists = result.fetchone() is not None
            
            if not exists:
                # Add the column
                alter_query = text("""
                    ALTER TABLE job_skills 
                    ADD COLUMN importance FLOAT DEFAULT 1.0
                """)
                connection.execute(alter_query)
                print("✓ Added 'importance' column to job_skills table")
            else:
                print("✓ Column 'importance' already exists in job_skills table")
        
        print("✓ Database migration completed successfully")
        
    except Exception as e:
        print(f"✗ Error adding importance column: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    add_importance_column()

