"""
Test script to verify recommendations are working
"""
import sys
from app.core.database import SessionLocal
from app.models.user import User
from app.agents.recommender_agent import get_recommendations

def test_recommendations():
    db = SessionLocal()
    try:
        # Get first user with completed onboarding
        user = db.query(User).filter(User.onboarding_completed == True).first()
        
        if not user:
            print("No user with completed onboarding found")
            return
        
        print(f"Testing recommendations for: {user.email}")
        print(f"User skills: {user.skills or []}")
        print(f"Has resume embedding: {user.resume_embedding is not None}")
        print("\n" + "="*50)
        
        # Get recommendations
        recommendations = get_recommendations(user, db, limit=10)
        
        print(f"\n=== RESULTS ===")
        print(f"Total recommendations: {len(recommendations)}")
        
        if recommendations:
            print("\nTop Recommendations:")
            for i, job in enumerate(recommendations[:5], 1):
                print(f"\n{i}. {job.get('title')} at {job.get('company')}")
                print(f"   Location: {job.get('location', 'N/A')}")
                print(f"   Combined Score: {job.get('combined_score', 0):.3f}")
                print(f"   Similarity: {job.get('similarity_score', 0):.3f}")
                print(f"   Skill Matches: {job.get('skill_match_count', 0)}")
                print(f"   Required Skills: {job.get('required_skills', [])[:5]}")
                print(f"   User Skills: {user.skills[:5] if user.skills else []}")
        else:
            print("\n❌ NO RECOMMENDATIONS FOUND")
            print("\nPossible reasons:")
            print("1. No active jobs in database")
            print("2. User skills don't match any job requirements")
            print("3. Embedding similarity is too low")
            print("4. Jobs don't have required_skills populated")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_recommendations()

