"""
Add context column to conversations table
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from app.core.config import settings

def add_context_column():
    """Add context column to conversations table if it doesn't exist"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.begin() as connection:  # Use begin() for autocommit
            # Check if column exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='conversations' AND column_name='context'
            """)
            result = connection.execute(check_query)
            exists = result.fetchone() is not None
            
            if not exists:
                # Add the context column
                alter_query = text("""
                    ALTER TABLE conversations 
                    ADD COLUMN context JSON DEFAULT '{}'::json
                """)
                connection.execute(alter_query)
                print("✓ Added 'context' column to conversations table")
            else:
                print("✓ Column 'context' already exists in conversations table")
        
        print("✓ Database migration completed successfully")
        
    except Exception as e:
        print(f"✗ Error adding context column: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    add_context_column()

