# Skill Gap Analysis Agent - Usage Guide

## Overview

The Skill Gap Analysis Agent compares a user's skills against job requirements to identify:
- Skills the user already has
- Missing skills needed for the job
- Match percentage
- AI-generated recommendations to bridge the gap
- Priority skills to learn first

## Architecture

The agent uses **LangGraph** with a two-node workflow:

1. **`analyze_skills_node`**: Performs set operations to find matching and missing skills
2. **`generate_gap_analysis_node`**: Uses LLM to generate detailed analysis and recommendations

## How It Works

### 1. Skill Comparison
- Takes user's skills (from `user.skills` JSON field)
- Takes job's required skills (from `job.required_skills` JSON field)
- Performs set intersection to find matching skills
- Performs set difference to find missing skills

### 2. Analysis Generation
- Calculates match percentage: `(matching_skills / total_required_skills) * 100`
- Uses Euron AI LLM to generate:
  - Brief analysis of the skill gap
  - Top 5 actionable recommendations
  - Priority skills to learn first

## Usage Methods

### Method 1: Via API Endpoint (Recommended)

**Endpoint**: `GET /api/user/skill-gap/{job_id}`

**Authentication**: Required (JWT token)

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/user/skill-gap/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Example Response**:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "job_title": "Senior Python Developer",
  "job_company": "Tech Corp",
  "user_skills": ["Python", "Django", "PostgreSQL", "Git"],
  "job_required_skills": ["Python", "Django", "PostgreSQL", "Redis", "Docker", "AWS"],
  "user_has_skills": ["Python", "Django", "PostgreSQL"],
  "missing_skills": ["Redis", "Docker", "AWS"],
  "skill_gap_analysis": {
    "match_percentage": 50.0,
    "skills_matched": 3,
    "skills_missing": 3,
    "total_required": 6,
    "analysis": "You have a solid foundation with Python, Django, and PostgreSQL...",
    "priority_skills": ["Docker", "AWS", "Redis"]
  },
  "recommendations": [
    "Learn Docker for containerization",
    "Get AWS certification",
    "Practice with Redis for caching"
  ]
}
```

### Method 2: Programmatically in Python

**Import the function**:
```python
from app.agents.skill_gap_agent import analyze_skill_gap
from app.models.user import User
from app.models.job import JobPosting
from app.core.database import get_db

# Get database session
db = next(get_db())

# Get user and job
user = db.query(User).filter(User.id == user_id).first()
job = db.query(JobPosting).filter(JobPosting.id == job_id).first()

# Analyze skill gap
analysis = analyze_skill_gap(user, job, db)

print(f"Match: {analysis['skill_gap_analysis']['match_percentage']}%")
print(f"Missing: {', '.join(analysis['missing_skills'])}")
```

### Method 3: Direct Agent Invocation

**For advanced use cases**:
```python
from app.agents.skill_gap_agent import skill_gap_agent

# Prepare state
initial_state = {
    "user_id": "user-uuid",
    "user_skills": ["Python", "Django", "PostgreSQL"],
    "job_id": "job-uuid",
    "job_required_skills": ["Python", "Django", "Redis", "Docker"],
    "user_has_skills": [],
    "missing_skills": [],
    "skill_gap_analysis": {},
    "recommendations": [],
    "errors": []
}

# Run agent
result = skill_gap_agent.invoke(initial_state)

# Access results
print(result["skill_gap_analysis"]["match_percentage"])
print(result["missing_skills"])
```

## Frontend Integration Example

**React/Next.js Example**:
```typescript
// In a job details component
const analyzeSkillGap = async (jobId: string) => {
  try {
    const response = await api.get(`/api/user/skill-gap/${jobId}`)
    const analysis = response.data
    
    console.log(`Match: ${analysis.skill_gap_analysis.match_percentage}%`)
    console.log(`Missing: ${analysis.missing_skills.join(', ')}`)
    console.log(`Recommendations:`, analysis.recommendations)
    
    return analysis
  } catch (error) {
    console.error('Error analyzing skill gap:', error)
  }
}
```

## Response Structure

### Main Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | string | UUID of the job |
| `job_title` | string | Job title |
| `job_company` | string | Company name |
| `user_skills` | array | All user skills |
| `job_required_skills` | array | All required skills for the job |
| `user_has_skills` | array | Skills user has that match job requirements |
| `missing_skills` | array | Skills user lacks but job requires |
| `skill_gap_analysis` | object | Detailed analysis (see below) |
| `recommendations` | array | AI-generated recommendations |

### `skill_gap_analysis` Object

| Field | Type | Description |
|-------|------|-------------|
| `match_percentage` | float | Percentage of required skills user has (0-100) |
| `skills_matched` | int | Number of matching skills |
| `skills_missing` | int | Number of missing skills |
| `total_required` | int | Total number of required skills |
| `analysis` | string | LLM-generated text analysis |
| `priority_skills` | array | Top 5 priority skills to learn |

## Data Requirements

### User Model
- `user.skills`: JSON array of skill strings
  ```python
  user.skills = ["Python", "Django", "PostgreSQL", "Git"]
  ```

### Job Model
- `job.required_skills`: JSON array of skill strings
  ```python
  job.required_skills = ["Python", "Django", "Redis", "Docker", "AWS"]
  ```

## Error Handling

The agent handles errors gracefully:
- If LLM fails, returns basic analysis with match percentage
- If skills are missing, uses empty arrays
- Returns error messages in `errors` field if critical failures occur

## Use Cases

1. **Job Application Preparation**: Before applying, see what skills you need
2. **Career Development**: Identify skills to learn for career growth
3. **Recommendation System**: Enhance job recommendations with skill gap info
4. **Learning Paths**: Generate personalized learning recommendations
5. **Interview Preparation**: Understand what skills to highlight

## Integration Points

### In Job Recommendations
```python
# In recommender_agent.py
recommendations = get_recommendations(user, db)
for job in recommendations:
    gap_analysis = analyze_skill_gap(user, job, db)
    job['skill_gap'] = gap_analysis
```

### In Job Details Page
```typescript
// Show skill gap analysis when viewing a job
<JobDetails job={job} onAnalyzeGap={analyzeSkillGap} />
```

### In Career Advisor Chat
```python
# Include skill gap in chat context
gap_analysis = analyze_skill_gap(user, job, db)
context = {
    "skill_gap": gap_analysis,
    "recommendations": gap_analysis['recommendations']
}
```

## Performance Considerations

- **LLM Call**: Takes ~1-3 seconds for analysis generation
- **Caching**: Consider caching results for same user-job pairs
- **Batch Processing**: For multiple jobs, process in parallel

## Future Enhancements

Potential improvements:
- Skill similarity matching (fuzzy matching)
- Skill proficiency levels
- Learning resource recommendations
- Time estimates to learn missing skills
- Skill gap trends over time



