from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.agents.recommender_agent import get_recommendations

router = APIRouter()


@router.get("/")
async def get_user_recommendations(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized job recommendations for the current user"""
    try:
        # Check if user has completed onboarding
        if not current_user.onboarding_completed:
            return {
                "recommendations": [],
                "count": 0,
                "message": "Please complete your profile to get personalized recommendations"
            }
        
        # Get recommendations (this is a sync function, but FastAPI handles it)
        recommendations = get_recommendations(current_user, db, limit=limit)
        
        return {
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    except Exception as e:
        # Log the error for debugging
        print(f"Error getting recommendations for user {current_user.id}: {e}")
        import traceback
        traceback.print_exc()
        
        # Return empty recommendations instead of crashing
        return {
            "recommendations": [],
            "count": 0,
            "message": "Unable to generate recommendations at this time. Please try again later.",
            "error": str(e) if current_user.is_admin else None  # Only show error to admins
        }

