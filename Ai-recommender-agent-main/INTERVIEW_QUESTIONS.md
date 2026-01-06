# Interview Questions - AI Job Recommender Project

This document contains comprehensive interview questions related to the AI Job Recommender project, organized by category.

---

## Table of Contents

1. [Project Overview & Architecture](#project-overview--architecture)
2. [AI/ML & Embeddings](#aiml--embeddings)
3. [Database & Vector Search](#database--vector-search)
4. [Backend (FastAPI)](#backend-fastapi)
5. [Frontend (Next.js)](#frontend-nextjs)
6. [LangGraph & Agents](#langgraph--agents)
7. [System Design & Scalability](#system-design--scalability)
8. [Security & Authentication](#security--authentication)
9. [Web Scraping](#web-scraping)
10. [Code Quality & Best Practices](#code-quality--best-practices)

---

## Project Overview & Architecture

### Q1: Can you give me a high-level overview of this project?

**Answer:**
This is an AI-powered job recommendation platform that helps users find relevant internships and jobs. The system:
- Analyzes user profiles, resumes, and skills
- Uses vector embeddings for semantic similarity matching
- Leverages LangGraph agents for intelligent processing
- Provides personalized job recommendations with explanations

**Architecture:**
- **Frontend**: Next.js 14 with React 18 and TypeScript
- **Backend**: FastAPI with Python
- **Database**: PostgreSQL with pgvector extension for vector storage
- **AI**: Euron AI for LLM and embeddings
- **Agents**: LangGraph for workflow orchestration

---

### Q2: Why did you choose this tech stack?

**Answer:**

**Frontend - Next.js:**
- Server-side rendering for better SEO
- Built-in optimization (code splitting, image optimization)
- App Router for modern routing
- TypeScript for type safety

**Backend - FastAPI:**
- High performance (comparable to Node.js)
- Native async/await support
- Auto-generated API documentation
- Type hints for validation

**Database - PostgreSQL + pgvector:**
- Relational data needs (users, jobs, relationships)
- Vector similarity search in same database
- ACID compliance for data integrity
- No need for separate vector database

**AI - LangGraph:**
- Agent workflows as graphs
- State management across steps
- Modular and testable
- Easy to visualize and debug

---

### Q3: How does the system handle user onboarding?

**Answer:**
1. User uploads resume (PDF/DOCX)
2. Backend extracts text using PyPDF2/docx
3. Resume Parser Agent (LangGraph) processes the text:
   - Extracts skills, experience, education
   - Uses LLM to parse structured data
4. Generate embedding from resume text
5. Store embedding in `user.resume_embedding` (pgvector)
6. Store skills in `user.skills` (JSON array)
7. Mark `onboarding_completed = True`

**Key Files:**
- `backend/app/agents/resume_parser_agent.py`
- `backend/app/utils/resume_parser.py`
- `backend/app/utils/embeddings.py`

---

## AI/ML & Embeddings

### Q4: What are embeddings and why are they used in this project?

**Answer:**
**Embeddings** are numerical vector representations of text that capture semantic meaning. Similar texts have similar vectors.

**Why Used:**
- **Semantic Matching**: Finds similar jobs even with different wording
  - Example: "Python developer" and "Python programmer" → similar vectors
- **Vector Search**: Fast similarity calculations using cosine similarity
- **Better than Keywords**: Understands context, not just exact matches

**Example:**
```python
text = "Python developer with ML experience"
embedding = [0.123, -0.456, 0.789, ...]  # 1536 numbers
```

**Storage:**
- Stored in PostgreSQL using pgvector extension
- Dimension: 1536 (text-embedding-3-small model)

---

### Q5: How does the recommendation algorithm work?

**Answer:**
The recommendation uses a **hybrid scoring approach**:

1. **Vector Similarity Score** (50% weight):
   - Calculate cosine similarity between user embedding and job embedding
   - Captures semantic meaning
   - Example: "ML engineer" matches "Machine Learning developer"

2. **Skill Match Score** (50% weight):
   - Normalize skill names (Python → python, Node.js → nodejs)
   - Count matching skills between user and job
   - Calculate ratio: `matches / total_required_skills`

3. **Combined Score**:
   ```python
   combined_score = (similarity_score * 0.5) + (skill_match_ratio * 0.5)
   ```

4. **Filtering**:
   - Include jobs with: skill_match_count > 0 OR similarity > 0.3 OR combined_score > 0.1
   - Sort by combined_score (descending)
   - Return top 10 with LLM-generated explanations

**Why Hybrid?**
- Vector similarity: Good for semantic matching
- Skill matching: Ensures required skills are present
- Combined: More accurate than either alone

---

### Q6: Why normalize skills? Give an example.

**Answer:**
Skills come in various formats, so normalization ensures accurate matching.

**Example:**
```python
# User has: ["Python", "Node.js", "Machine Learning"]
# Job requires: ["python", "NodeJS", "ML"]

# Without normalization: 0 matches
# With normalization: 3 matches
```

**Normalization Steps:**
1. Convert to lowercase
2. Remove special characters (-, _, .)
3. Handle aliases:
   - "Node.js" → "nodejs"
   - "Machine Learning" → "ml"
   - "JavaScript" → "js"

**Code Location:** `backend/app/agents/recommender_agent.py` - `normalize_skill()` function

---

### Q7: How do you handle cases where embeddings are missing?

**Answer:**
The system has **fallback mechanisms**:

1. **User Embedding Missing:**
   - Generate from `resume_text + skills + experience`
   - Store in database for future use
   - If no text available, use skill-based matching only

2. **Job Embedding Missing:**
   - Include job in candidates anyway
   - Use skill matching only (no vector similarity)
   - Boost skill match weight: `combined_score = skill_match_ratio * 0.8`

3. **Both Missing:**
   - Pure skill-based matching
   - Still provides recommendations based on skill overlap

**Code:**
```python
if similarity_score == 0.0 and skill_match_ratio > 0:
    combined_score = skill_match_ratio * 0.8  # Higher weight
else:
    combined_score = (similarity_score * 0.5) + (skill_match_ratio * 0.5)
```

---

### Q8: What is cosine similarity and how is it calculated?

**Answer:**
**Cosine Similarity** measures the angle between two vectors, not their magnitude. Range: -1 to 1 (1 = identical, 0 = orthogonal, -1 = opposite).

**Formula:**
```
cosine_similarity = (A · B) / (||A|| × ||B||)
```

**Python Implementation:**
```python
def cosine_similarity(embedding1, embedding2):
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    return dot_product / (norm1 * norm2)
```

**Why Cosine, Not Euclidean?**
- **Magnitude Independent**: Focuses on direction (meaning), not size
- **Better for Text**: Word frequency doesn't affect similarity
- **Normalized**: Always between -1 and 1

---

## Database & Vector Search

### Q9: Why use pgvector instead of a separate vector database?

**Answer:**

**Advantages:**
1. **Simplicity**: One database for relational data and vectors
2. **ACID Transactions**: Embeddings and job data in same transaction
3. **Cost**: No separate service needed
4. **Performance**: Good enough for this scale (thousands of jobs)
5. **SQL Integration**: Can join vectors with relational data

**Trade-offs:**
- **Scale**: May need Pinecone/Weaviate for millions of vectors
- **Specialized Features**: Separate vector DBs have advanced features

**For This Project:**
- Scale: ~10K-100K jobs → pgvector is sufficient
- Simplicity: Easier to maintain one database

---

### Q10: How do you query similar vectors in PostgreSQL?

**Answer:**
Using pgvector's **distance operators**:

```sql
-- Cosine distance (1 - cosine similarity)
SELECT * FROM job_postings
ORDER BY description_embedding <=> $1  -- <=> is cosine distance
LIMIT 10;

-- Euclidean distance
SELECT * FROM job_postings
ORDER BY description_embedding <-> $1  -- <-> is Euclidean distance
LIMIT 10;
```

**In SQLAlchemy:**
```python
# pgvector handles this automatically
job.description_embedding = embedding  # Just assign the list
```

**Indexing:**
```sql
CREATE INDEX ON job_postings 
USING ivfflat (description_embedding vector_cosine_ops);
```

---

### Q11: How is the database schema designed?

**Answer:**

**User Table:**
```python
class User(Base):
    id = UUID
    email = String (unique, indexed)
    hashed_password = String
    resume_text = Text
    resume_embedding = Vector(1536)  # pgvector
    skills = JSON  # ["Python", "ML", ...]
    experience_years = String
    onboarding_completed = Boolean
```

**Job Table:**
```python
class JobPosting(Base):
    id = UUID
    title = String (indexed)
    company = String (indexed)
    description = Text
    description_embedding = Vector(1536)  # pgvector
    required_skills = JSON
    source_url = String (unique, indexed)
    is_active = Boolean
```

**Why JSON for Skills?**
- Flexible: Easy to store arrays
- Queryable: PostgreSQL supports JSON queries
- Simple: No need for separate skills table

**Relationships:**
- User → SavedJob (many-to-many through SavedJob)
- User → Conversation (one-to-many)

---

## Backend (FastAPI)

### Q12: How does FastAPI dependency injection work?

**Answer:**
FastAPI uses **dependency injection** to provide dependencies to route handlers.

**Example:**
```python
@router.get("/recommendations")
async def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # db and current_user are automatically injected
    return get_recommendations(current_user, db)
```

**How It Works:**
1. `Depends(get_db)` calls `get_db()` function
2. `get_db()` yields a database session
3. FastAPI provides it to the route handler
4. After handler completes, `finally` block closes session

**Benefits:**
- **Testability**: Easy to mock dependencies
- **Reusability**: Same dependencies across endpoints
- **Clean Code**: No manual session management

---

### Q13: How is authentication implemented?

**Answer:**

**Registration:**
1. User provides email and password
2. Hash password using bcrypt
3. Create User record
4. Generate JWT token
5. Return token to frontend

**Login:**
1. Find user by email
2. Verify password hash
3. Generate JWT token
4. Return token

**Protected Routes:**
```python
@router.get("/recommendations")
async def get_recommendations(
    current_user: User = Depends(get_current_user)
):
    # get_current_user verifies JWT token
    # Returns User object or raises 401
```

**JWT Structure:**
- Header: Algorithm (HS256)
- Payload: User ID, expiration
- Signature: Signed with SECRET_KEY

**Code Location:** `backend/app/core/security.py`

---

### Q14: How do you handle errors in FastAPI?

**Answer:**

**HTTP Exceptions:**
```python
from fastapi import HTTPException, status

if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )
```

**Try-Except Blocks:**
```python
try:
    recommendations = get_recommendations(user, db)
except Exception as e:
    # Log error
    print(f"Error: {e}")
    # Return user-friendly message
    return {
        "recommendations": [],
        "error": str(e) if user.is_admin else None
    }
```

**Validation Errors:**
- Pydantic models automatically validate request data
- Returns 422 with validation details

---

### Q15: How is the FastAPI app structured?

**Answer:**

```
backend/app/
├── main.py              # FastAPI app, CORS, route registration
├── core/
│   ├── config.py        # Settings (env variables)
│   ├── database.py      # DB connection, session
│   └── security.py      # Password hashing, JWT
├── models/              # SQLAlchemy models
├── api/                 # Route handlers
│   ├── auth.py
│   ├── recommendations.py
│   └── chat.py
├── agents/              # LangGraph agents
└── utils/               # Utilities (embeddings, LLM)
```

**Route Registration:**
```python
app.include_router(auth.router, prefix="/api/auth")
app.include_router(recommendations.router, prefix="/api/recommendations")
```

**Lifespan Events:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: Cleanup (if needed)
```

---

## Frontend (Next.js)

### Q16: How is authentication handled on the frontend?

**Answer:**

**Token Storage:**
```typescript
// Store token in localStorage
localStorage.setItem('token', token);

// Include in API requests
headers: {
  'Authorization': `Bearer ${token}`
}
```

**Auth Utilities:**
```typescript
// lib/auth.ts
export async function getCurrentUser(): Promise<User | null> {
  const token = localStorage.getItem('token');
  if (!token) return null;
  
  // Call /api/auth/me
  const response = await fetch('/api/auth/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}
```

**Protected Routes:**
```typescript
useEffect(() => {
  const user = await getCurrentUser();
  if (!user) {
    router.push('/auth/login');
  }
}, []);
```

**Note:** For production, consider httpOnly cookies instead of localStorage.

---

### Q17: How does the frontend communicate with the backend?

**Answer:**

**API Client:**
```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getRecommendations() {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_URL}/api/recommendations`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
}
```

**Usage in Components:**
```typescript
const [recommendations, setRecommendations] = useState([]);

useEffect(() => {
  getRecommendations().then(setRecommendations);
}, []);
```

**Error Handling:**
```typescript
try {
  const data = await getRecommendations();
  setRecommendations(data.recommendations);
} catch (error) {
  console.error('Error:', error);
  // Show error message to user
}
```

---

### Q18: How is the UI structured in Next.js?

**Answer:**

**App Router Structure:**
```
frontend/app/
├── layout.tsx           # Root layout (navbar, footer)
├── page.tsx             # Home page
├── auth/
│   ├── login/page.tsx
│   └── register/page.tsx
├── dashboard/page.tsx
├── recommendations/page.tsx
└── chat/page.tsx
```

**Component Structure:**
- **Server Components**: Default (can fetch data directly)
- **Client Components**: Use `'use client'` directive (for interactivity)

**Example:**
```typescript
'use client'  // Client component (uses hooks)

import { useState, useEffect } from 'react';

export default function DashboardPage() {
  const [user, setUser] = useState(null);
  // ...
}
```

---

## LangGraph & Agents

### Q19: What is LangGraph and why is it used?

**Answer:**
**LangGraph** is a framework for building AI agent workflows as graphs.

**Key Concepts:**
- **Nodes**: Individual processing steps (functions)
- **Edges**: Flow between nodes
- **State**: Data passed between nodes (TypedDict)

**Example:**
```python
# Define state
class RecommenderState(TypedDict):
    user_embedding: List[float]
    job_candidates: List[Dict]
    scored_jobs: List[Dict]

# Create workflow
workflow = StateGraph(RecommenderState)
workflow.add_node("score_jobs", score_jobs_node)
workflow.add_node("generate_recommendations", generate_recommendations_node)
workflow.add_edge("score_jobs", "generate_recommendations")

# Execute
result = workflow.invoke(initial_state)
```

**Why Use It:**
- **Modularity**: Each step is separate (easy to test)
- **Debugging**: Can inspect state at each step
- **Visualization**: Can visualize workflow as graph
- **Flexibility**: Easy to add/remove steps

---

### Q20: How does the Recommender Agent work?

**Answer:**

**Workflow:**
1. **get_user_embedding_node**: Get or generate user embedding
2. **fetch_job_candidates_node**: Query jobs from database
3. **score_jobs_node**: Calculate similarity and skill match scores
4. **generate_recommendations_node**: Generate explanations using LLM

**State Flow:**
```
Initial State
  ↓
{user_embedding: [...], job_candidates: []}
  ↓
score_jobs_node
  ↓
{scored_jobs: [{score: 0.85, ...}, ...]}
  ↓
generate_recommendations_node
  ↓
{recommendations: [{explanation: "...", ...}, ...]}
```

**Code Location:** `backend/app/agents/recommender_agent.py`

---

### Q21: How does the Career Advisor Agent work?

**Answer:**

**Workflow:**
1. **retrieve_context_node**:
   - Generate embedding for user message
   - Query jobs with vector similarity
   - Get top 5 relevant jobs

2. **generate_response_node**:
   - Build prompt with:
     - System prompt (role: career advisor)
     - Conversation history (last 5 messages)
     - User message
     - Relevant jobs
   - Call LLM to generate response

**RAG (Retrieval-Augmented Generation):**
- Retrieves relevant context (jobs) before generating response
- Makes responses more accurate and context-aware

**Code Location:** `backend/app/agents/career_advisor_agent.py`

---

## System Design & Scalability

### Q22: How would you scale this system for millions of users?

**Answer:**

**Database:**
1. **Read Replicas**: Separate read/write databases
2. **Connection Pooling**: Already using SQLAlchemy pool
3. **Caching**: Redis for frequently accessed data
4. **Vector DB**: Consider Pinecone/Weaviate for millions of vectors

**Backend:**
1. **Horizontal Scaling**: Multiple FastAPI instances behind load balancer
2. **Async Processing**: Use Celery for background tasks (already set up)
3. **CDN**: Serve static assets
4. **Rate Limiting**: Prevent abuse

**Frontend:**
1. **Static Generation**: Pre-render pages where possible
2. **Image Optimization**: Next.js handles this
3. **Code Splitting**: Already built-in

**Caching Strategy:**
- Cache user embeddings (rarely change)
- Cache job embeddings (until job updated)
- Cache recommendations (TTL: 1 hour)

---

### Q23: How do you handle concurrent requests?

**Answer:**

**FastAPI Async:**
```python
@router.get("/recommendations")
async def get_recommendations(...):
    # Async function - can handle multiple requests concurrently
    recommendations = await get_recommendations_async(user, db)
```

**Database Connection Pool:**
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,      # 10 connections
    max_overflow=20    # Up to 20 additional
)
```

**GIL Limitation:**
- Python GIL limits CPU-bound tasks
- For I/O-bound (database, API calls): async works well
- For CPU-bound: Consider multiprocessing or separate workers

---

### Q24: How would you monitor this system in production?

**Answer:**

**Metrics:**
1. **Application Metrics**: Response times, error rates
2. **Database Metrics**: Query performance, connection pool usage
3. **AI Metrics**: LLM API latency, embedding generation time
4. **Business Metrics**: Recommendations generated, user engagement

**Tools:**
- **APM**: New Relic, Datadog, or Sentry
- **Logging**: Structured logging (JSON format)
- **Health Checks**: `/health` endpoint
- **Alerts**: Set up alerts for errors, high latency

**Example:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": check_db_connection(),
        "redis": check_redis_connection()
    }
```

---

## Security & Authentication

### Q25: How are passwords stored securely?

**Answer:**

**Hashing with bcrypt:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Why bcrypt?**
- **One-way**: Cannot reverse hash to get password
- **Salt**: Each password has unique salt (prevents rainbow tables)
- **Slow**: Intentionally slow to prevent brute force (adaptive)

**Storage:**
```python
# Never store plain passwords
user.hashed_password = get_password_hash(password)
```

---

### Q26: What are the security vulnerabilities and how are they mitigated?

**Answer:**

**Vulnerabilities & Mitigations:**

1. **SQL Injection**
   - **Risk**: User input directly in SQL
   - **Mitigation**: SQLAlchemy ORM (parameterized queries)

2. **XSS (Cross-Site Scripting)**
   - **Risk**: Malicious scripts in user input
   - **Mitigation**: React escapes by default, sanitize user input

3. **CSRF (Cross-Site Request Forgery)**
   - **Risk**: Unauthorized actions
   - **Mitigation**: CORS settings, SameSite cookies

4. **JWT Token Theft**
   - **Risk**: Token stolen from localStorage
   - **Mitigation**: Use httpOnly cookies in production, HTTPS only

5. **File Upload Attacks**
   - **Risk**: Malicious files
   - **Mitigation**: Size limits, type validation, scan files

---

## Web Scraping

### Q27: How does the job scraping work?

**Answer:**

**Scraper Agent Workflow:**
1. **select_scraper_node**: Choose scraper (Indeed, RemoteOK, RSS)
2. **scrape_jobs_node**: 
   - Use Playwright to load page (handles JavaScript)
   - Extract job listings with BeautifulSoup
   - Return raw job data
3. **normalize_jobs_node**: Convert to unified schema

**Why Playwright?**
- Handles dynamic content (React apps)
- Renders pages like a real browser
- More reliable than requests for modern sites

**Normalization:**
- Each source has different format
- Convert to unified schema: title, company, description, skills, etc.

**Code Location:** `backend/app/agents/scraper_agent.py`

---

### Q28: How do you handle rate limiting and avoid being blocked?

**Answer:**

**Rate Limiting:**
```python
SCRAPING_RATE_LIMIT = 10  # requests per minute
```

**Strategies:**
1. **Delays**: Add delays between requests
2. **User Agents**: Rotate user agents
3. **Proxies**: Use proxy rotation (if needed)
4. **Respect robots.txt**: Check before scraping
5. **Caching**: Don't re-scrape same URLs

**Example:**
```python
import time

for url in urls:
    scrape(url)
    time.sleep(6)  # 10 requests per minute
```

**Legal Considerations:**
- Check website's Terms of Service
- Use APIs when available
- Consider official partnerships

---

## Code Quality & Best Practices

### Q29: How do you ensure code quality?

**Answer:**

**Practices:**
1. **Type Hints**: Python type hints, TypeScript
2. **Error Handling**: Try-except blocks, proper HTTP status codes
3. **Logging**: Structured logging for debugging
4. **Documentation**: Docstrings, README files
5. **Code Organization**: Modular structure (agents, utils, api)

**Testing (Should Add):**
- Unit tests for agents
- Integration tests for API endpoints
- E2E tests for critical flows

**Linting:**
- Python: black, flake8, mypy
- TypeScript: ESLint, Prettier

---

### Q30: How would you improve this project?

**Answer:**

**Short-term:**
1. **Testing**: Add unit and integration tests
2. **Error Handling**: More specific error messages
3. **Logging**: Structured logging (JSON format)
4. **Documentation**: API documentation improvements

**Medium-term:**
1. **Caching**: Redis for recommendations
2. **Background Jobs**: Celery for scraping (already set up)
3. **Monitoring**: Add APM and alerting
4. **Performance**: Optimize database queries

**Long-term:**
1. **Real-time**: WebSocket for live updates
2. **ML Model**: Train custom recommendation model
3. **A/B Testing**: Test different recommendation algorithms
4. **Multi-language**: Support non-English resumes/jobs

---

## Behavioral Questions

### Q31: What was the most challenging part of this project?

**Answer:**
The most challenging part was **combining vector similarity with skill matching** for accurate recommendations.

**Challenge:**
- Vector similarity alone: Too broad (matches unrelated jobs)
- Skill matching alone: Too narrow (misses semantic matches)

**Solution:**
- Hybrid approach: 50% vector similarity + 50% skill matching
- Normalize skills for accurate matching
- Fallback mechanisms when embeddings missing

**Learning:**
- Understanding trade-offs between different matching approaches
- Importance of normalization and data preprocessing

---

### Q32: How did you handle debugging when recommendations were inaccurate?

**Answer:**

**Debugging Process:**
1. **Logging**: Added detailed logs at each step
   - User skills, job skills
   - Similarity scores, skill match counts
   - Final combined scores

2. **Inspection**: Checked embeddings
   - Verified embeddings were generated correctly
   - Checked similarity calculations

3. **Testing**: Tested with known good/bad matches
   - Verified normalization worked
   - Checked edge cases (missing embeddings, empty skills)

4. **Iteration**: Adjusted weights and thresholds
   - Tuned combined score formula
   - Adjusted filtering thresholds

**Tools:**
- Print statements (for development)
- Database queries to inspect data
- Manual testing with sample users

---

### Q33: How would you explain this project to a non-technical person?

**Answer:**
"This is like a smart job matching system. When you upload your resume, it:
1. Reads your resume and understands your skills
2. Compares you to thousands of job postings
3. Finds jobs that match your skills and experience
4. Explains why each job is a good fit

It's smarter than a simple keyword search because it understands meaning. For example, if a job says 'Machine Learning engineer' and your resume says 'ML developer', it knows they're the same thing.

The system also has a chat assistant that can answer career questions and suggest relevant jobs based on your questions."

---

## Technical Deep Dives

### Q34: Explain the cosine similarity calculation in detail.

**Answer:**

**Mathematical Formula:**
```
cosine_similarity = (A · B) / (||A|| × ||B||)
```

**Step-by-Step:**
1. **Dot Product**: Multiply corresponding elements and sum
   ```python
   dot_product = sum(a[i] * b[i] for i in range(len(a)))
   ```

2. **Magnitude (Norm)**: Square root of sum of squares
   ```python
   norm_a = sqrt(sum(a[i]^2 for i in range(len(a))))
   ```

3. **Divide**: Dot product divided by product of magnitudes

**Why This Works:**
- Measures angle between vectors (not distance)
- Range: -1 to 1
- 1 = identical direction, 0 = orthogonal, -1 = opposite

**Example:**
```python
embedding1 = [1, 0, 0]  # "Python"
embedding2 = [0.9, 0.1, 0]  # "Python developer"
cosine_similarity ≈ 0.99  # Very similar
```

---

### Q35: How does pgvector store and query vectors?

**Answer:**

**Storage:**
```python
# SQLAlchemy model
description_embedding = Column(Vector(1536))

# Insert
job.description_embedding = embedding  # Just assign list
db.commit()  # pgvector handles conversion
```

**Querying:**
```sql
-- Cosine distance (1 - cosine similarity)
SELECT * FROM job_postings
ORDER BY description_embedding <=> $1
LIMIT 10;

-- With index (for performance)
CREATE INDEX ON job_postings 
USING ivfflat (description_embedding vector_cosine_ops);
```

**Index Type: IVFFlat:**
- Inverted File Index (IVF)
- Divides vectors into clusters
- Searches only relevant clusters (faster)

**Trade-offs:**
- **Accuracy**: Slightly less accurate than exact search
- **Speed**: Much faster for large datasets
- **Build Time**: Index takes time to build

---

## Summary

These questions cover:
- **Architecture**: System design and tech stack choices
- **AI/ML**: Embeddings, similarity, recommendations
- **Backend**: FastAPI, database, authentication
- **Frontend**: Next.js, React, API communication
- **Agents**: LangGraph workflows
- **Scalability**: Performance and scaling strategies
- **Security**: Authentication and vulnerabilities
- **Best Practices**: Code quality and improvements

Use these questions to prepare for technical interviews related to this project!

