"""
Add context column to conversations table
Run this script to fix the database schema
"""
import psycopg2
from app.core.config import settings

def fix_context_column():
    """Add context column to conversations table"""
    # Parse database URL
    db_url = settings.DATABASE_URL.replace("postgresql://", "")
    parts = db_url.split("@")
    if len(parts) != 2:
        print("Error: Invalid DATABASE_URL format")
        return
    
    auth, host_db = parts[0], parts[1]
    user, password = auth.split(":")
    host, db = host_db.split("/")
    host, port = host.split(":") if ":" in host else (host, "5432")
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            dbname=db,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='conversations' AND column_name='context'
        """)
        
        if cursor.fetchone() is None:
            # Add the context column
            cursor.execute("""
                ALTER TABLE conversations 
                ADD COLUMN context JSON DEFAULT '{}'::json
            """)
            print("✓ Added 'context' column to conversations table")
        else:
            print("✓ Column 'context' already exists")
        
        cursor.close()
        conn.close()
        print("✓ Database migration completed successfully")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_context_column()





