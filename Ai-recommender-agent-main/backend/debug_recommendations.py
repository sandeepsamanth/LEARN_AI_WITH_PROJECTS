"""
Debug script to check why users aren't getting recommendations
"""
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User
from app.models.job import JobPosting

def debug_recommendations():
    db = SessionLocal()
    try:
        # Check users
        users = db.query(User).all()
        print(f"\n=== USERS ({len(users)}) ===")
        for user in users:
            print(f"\nUser: {user.email}")
            print(f"  - Onboarding completed: {user.onboarding_completed}")
            print(f"  - Skills: {user.skills or []}")
            print(f"  - Skills count: {len(user.skills) if user.skills else 0}")
            print(f"  - Has resume_text: {bool(user.resume_text)}")
            print(f"  - Has resume_embedding: {user.resume_embedding is not None}")
            if user.resume_text:
                print(f"  - Resume text length: {len(user.resume_text)} chars")
        
        # Check jobs
        jobs = db.query(JobPosting).filter(JobPosting.is_active == True).all()
        print(f"\n=== JOBS ({len(jobs)} active) ===")
        
        jobs_with_skills = 0
        jobs_with_embeddings = 0
        jobs_with_both = 0
        jobs_with_neither = 0
        
        for job in jobs[:10]:  # Check first 10
            has_skills = bool(job.required_skills and len(job.required_skills) > 0)
            has_embedding = job.description_embedding is not None
            
            if has_skills:
                jobs_with_skills += 1
            if has_embedding:
                jobs_with_embeddings += 1
            if has_skills and has_embedding:
                jobs_with_both += 1
            if not has_skills and not has_embedding:
                jobs_with_neither += 1
            
            if has_skills:
                print(f"\nJob: {job.title} at {job.company}")
                print(f"  - Required skills: {job.required_skills[:5] if job.required_skills else []}")
                print(f"  - Has embedding: {has_embedding}")
        
        print(f"\n=== SUMMARY ===")
        print(f"Total active jobs: {len(jobs)}")
        print(f"Jobs with skills: {jobs_with_skills}")
        print(f"Jobs with embeddings: {jobs_with_embeddings}")
        print(f"Jobs with both: {jobs_with_both}")
        print(f"Jobs with neither: {jobs_with_neither}")
        
        # Check a specific user's potential matches
        if users:
            user = users[0]
            if user.skills:
                print(f"\n=== TESTING RECOMMENDATIONS FOR {user.email} ===")
                user_skills_normalized = {s.lower().strip() for s in user.skills if s}
                print(f"User skills (normalized): {user_skills_normalized}")
                
                matching_jobs = []
                for job in jobs[:50]:
                    if job.required_skills:
                        job_skills_normalized = {s.lower().strip() for s in job.required_skills if s}
                        matches = user_skills_normalized.intersection(job_skills_normalized)
                        if matches:
                            matching_jobs.append({
                                'title': job.title,
                                'company': job.company,
                                'matches': list(matches),
                                'match_count': len(matches)
                            })
                
                print(f"\nFound {len(matching_jobs)} jobs with skill matches:")
                for job in matching_jobs[:5]:
                    print(f"  - {job['title']} at {job['company']}: {job['match_count']} matches ({', '.join(job['matches'][:3])})")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_recommendations()

