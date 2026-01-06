"""
Create PostgreSQL database if it doesn't exist
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.core.config import settings


def create_database():
    """Creates the PostgreSQL database if it does not exist."""
    # Parse DATABASE_URL
    # Format: postgresql://user:password@host:port/dbname
    db_url = settings.DATABASE_URL
    
    # Extract components
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "")
    
    parts = db_url.split("@")
    if len(parts) != 2:
        print("✗ Invalid DATABASE_URL format")
        return False
    
    user_pass = parts[0]
    host_port_db = parts[1]
    
    user, password = user_pass.split(":")
    host_port, db_name = host_port_db.split("/")
    
    if ":" in host_port:
        host, port = host_port.split(":")
    else:
        host = host_port
        port = "5432"
    
    # Remove query parameters if any
    db_name = db_name.split("?")[0]
    
    try:
        # Connect to the default 'postgres' database to create a new one
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✓ Database '{db_name}' created successfully.")
            
            # Connect to the newly created database to enable pgvector
            conn_new_db = psycopg2.connect(
                dbname=db_name,
                user=user,
                password=password,
                host=host,
                port=port
            )
            conn_new_db.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor_new_db = conn_new_db.cursor()
            cursor_new_db.execute("CREATE EXTENSION IF NOT EXISTS vector")
            print("✓ pgvector extension enabled in new database.")
            cursor_new_db.close()
            conn_new_db.close()
            return True
        else:
            print(f"⚠ Database '{db_name}' already exists.")
            # Ensure pgvector is enabled even if db existed
            conn_existing_db = psycopg2.connect(
                dbname=db_name,
                user=user,
                password=password,
                host=host,
                port=port
            )
            conn_existing_db.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor_existing_db = conn_existing_db.cursor()
            cursor_existing_db.execute("CREATE EXTENSION IF NOT EXISTS vector")
            print("✓ pgvector extension ensured for existing database.")
            cursor_existing_db.close()
            conn_existing_db.close()
            return False
    except psycopg2.OperationalError as e:
        print(f"✗ Error connecting to PostgreSQL: {e}")
        print("  Please ensure PostgreSQL is running and connection details in .env are correct.")
        return False
    except Exception as e:
        print(f"✗ An unexpected error occurred: {e}")
        return False
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    create_database()







