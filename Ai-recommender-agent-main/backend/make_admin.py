"""
Script to make a user an admin
Usage: python make_admin.py <user_email>
"""
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User


def make_user_admin(email: str):
    """Sets a user's is_admin flag to True."""
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.is_admin = True
            db.commit()
            print(f"✓ User {email} is now an admin.")
        else:
            print(f"✗ User with email {email} not found.")
    except Exception as e:
        db.rollback()
        print(f"✗ Error making user admin: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <user_email>")
        sys.exit(1)
    
    user_email = sys.argv[1]
    make_user_admin(user_email)







