# AI Job Recommender - Code Flow & Architecture Explanation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack & Why It's Used](#technology-stack--why-its-used)
4. [Complete Code Flow](#complete-code-flow)
5. [Key Components Deep Dive](#key-components-deep-dive)
6. [Data Flow Diagrams](#data-flow-diagrams)

---

## Project Overview

This is an **AI-powered job recommendation system** that helps users find relevant internships and jobs by:
- Analyzing user profiles, resumes, and skills
- Using vector embeddings for semantic similarity matching
- Leveraging LangGraph agents for intelligent processing
- Providing personalized recommendations with explanations

---

## System Architecture

### High-Level Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Frontend  │ ◄─────► │   Backend   │ ◄─────► │  PostgreSQL │
│  (Next.js)  │  HTTP   │  (FastAPI)  │  SQL    │  (pgvector) │
└─────────────┘         └─────────────┘         └─────────────┘
                              │
                              │ API Calls
                              ▼
                        ┌─────────────┐
                        │  Euron AI   │
                        │  (LLM +     │
                        │  Embeddings)│
                        └─────────────┘
```

### Directory Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/                # Core configuration & database
│   │   ├── config.py        # Settings & environment variables
│   │   ├── database.py      # Database connection & session management
│   │   └── security.py      # Password hashing & JWT tokens
│   ├── models/              # SQLAlchemy database models
│   │   ├── user.py          # User model with embeddings
│   │   └── job.py           # Job posting model with embeddings
│   ├── api/                 # API route handlers
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── recommendations.py # Recommendation API
│   │   └── chat.py          # Career advisor chat API
│   ├── agents/              # LangGraph AI agents
│   │   ├── recommender_agent.py    # Job recommendation logic
│   │   ├── resume_parser_agent.py  # Resume parsing workflow
│   │   ├── career_advisor_agent.py # Chat-based career advice
│   │   └── scraper_agent.py        # Job scraping workflow
│   └── utils/               # Utility functions
│       ├── embeddings.py    # Embedding generation & similarity
│       └── llm.py           # LLM service wrapper
```

---

## Technology Stack & Why It's Used

### Frontend: Next.js 14 + React 18 + TypeScript

**Why Next.js?**
- **Server-Side Rendering (SSR)**: Better SEO and initial load performance
- **App Router**: Modern routing with file-based structure
- **API Routes**: Can handle backend logic if needed
- **Built-in Optimization**: Image optimization, code splitting

**Why TypeScript?**
- **Type Safety**: Catches errors at compile time
- **Better IDE Support**: Autocomplete and refactoring
- **Maintainability**: Easier to understand code structure

**Why Tailwind CSS?**
- **Rapid Development**: Utility-first CSS framework
- **Consistency**: Design system built-in
- **Responsive**: Mobile-first approach

### Backend: FastAPI

**Why FastAPI?**
- **Performance**: One of the fastest Python frameworks (comparable to Node.js)
- **Async Support**: Native async/await for I/O operations
- **Auto Documentation**: Swagger UI at `/docs` endpoint
- **Type Hints**: Python type hints for validation
- **Modern Python**: Uses Python 3.11+ features

### Database: PostgreSQL + pgvector

**Why PostgreSQL?**
- **Relational Data**: Users, jobs, relationships need structured storage
- **ACID Compliance**: Data integrity for critical operations
- **JSON Support**: Store flexible data (skills arrays, metadata)
- **Mature & Reliable**: Production-ready database

**Why pgvector?**
- **Vector Similarity Search**: Store and query embeddings efficiently
- **Cosine Similarity**: Built-in functions for similarity calculations
- **Performance**: Indexed vector searches are fast
- **Native Integration**: Works seamlessly with SQLAlchemy

### AI Stack: LangGraph + Euron AI

**Why LangGraph?**
- **Agent Workflows**: Define multi-step AI processes as graphs
- **State Management**: Maintains state across agent steps
- **Modularity**: Each node is a separate function (easy to test/debug)
- **Visualization**: Can visualize agent workflows

**Why Euron AI?**
- **LLM Access**: Provides GPT-4 access for text generation
- **Embeddings API**: Generates vector embeddings for semantic search
- **Unified API**: Single API for both LLM and embeddings

### Scraping: Playwright + BeautifulSoup4

**Why Playwright?**
- **JavaScript Support**: Can scrape dynamic content (React apps)
- **Headless Browser**: Renders pages like a real browser
- **Reliable**: Handles modern web apps better than requests

**Why BeautifulSoup4?**
- **HTML Parsing**: Easy to extract data from HTML
- **Simple API**: Intuitive for parsing structured data

---

## Complete Code Flow

### 1. User Registration & Authentication Flow

```
User → Frontend (Register Page)
  ↓
POST /api/auth/register
  ↓
Backend: auth.py
  ├─ Check if email exists
  ├─ Hash password (bcrypt)
  ├─ Create User record in database
  ├─ Generate JWT token
  └─ Return token to frontend
  ↓
Frontend stores token in localStorage
  ↓
User redirected to Dashboard
```

**Key Files:**
- `backend/app/api/auth.py`: Handles registration/login
- `backend/app/core/security.py`: Password hashing & JWT generation
- `frontend/lib/auth.ts`: Frontend auth utilities

**Why JWT?**
- **Stateless**: Server doesn't need to store session data
- **Scalable**: Works across multiple servers
- **Secure**: Signed tokens prevent tampering

---

### 2. User Onboarding Flow

```
User → Onboarding Page
  ↓
Upload Resume (PDF/DOCX)
  ↓
POST /api/user/upload-resume
  ↓
Backend: user.py
  ├─ Save file to uploads/
  ├─ Extract text from resume
  ├─ Call Resume Parser Agent
  └─ Store parsed data
  ↓
Resume Parser Agent (LangGraph)
  ├─ Node 1: extract_text_node
  │   └─ Extract text using PyPDF2/docx
  ├─ Node 2: parse_data_node
  │   └─ Use LLM to extract:
  │       • Skills
  │       • Experience years
  │       • Education level
  │       • Work history
  └─ Return structured data
  ↓
Backend:
  ├─ Generate embedding from resume text
  ├─ Store embedding in user.resume_embedding (pgvector)
  ├─ Store skills in user.skills (JSON array)
  └─ Mark onboarding_completed = True
  ↓
Frontend shows success message
```

**Key Files:**
- `backend/app/agents/resume_parser_agent.py`: LangGraph workflow
- `backend/app/utils/resume_parser.py`: Text extraction logic
- `backend/app/utils/embeddings.py`: Embedding generation

**Why Embeddings?**
- **Semantic Understanding**: Captures meaning, not just keywords
- **Similarity Matching**: Can find similar jobs even with different wording
- **Vector Search**: Fast similarity calculations

---

### 3. Job Recommendation Flow

```
User clicks "Get Recommendations"
  ↓
GET /api/recommendations
  ↓
Backend: recommendations.py
  ├─ Verify user is authenticated
  ├─ Check onboarding_completed
  └─ Call get_recommendations(user, db)
  ↓
Recommender Agent (recommender_agent.py)
  ├─ Step 1: Get User Embedding
  │   ├─ Check if user.resume_embedding exists
  │   ├─ If yes: Use stored embedding
  │   └─ If no: Generate from resume_text + skills
  │
  ├─ Step 2: Fetch Job Candidates
  │   ├─ Query all active jobs (limit 500)
  │   └─ Include jobs with/without embeddings
  │
  ├─ Step 3: Score Jobs (score_jobs_node)
  │   For each job:
  │   ├─ Calculate Vector Similarity
  │   │   └─ cosine_similarity(user_embedding, job_embedding)
  │   ├─ Calculate Skill Match
  │   │   ├─ Normalize skill names (Python → python)
  │   │   ├─ Count matching skills
  │   │   └─ skill_match_ratio = matches / total_required
  │   └─ Combined Score
  │       └─ (similarity * 0.5) + (skill_match * 0.5)
  │
  └─ Step 4: Generate Explanations
      ├─ Take top 10 scored jobs
      ├─ For each job: Use LLM to generate explanation
      └─ Return recommendations with scores
  ↓
Backend returns JSON:
{
  "recommendations": [
    {
      "title": "Software Engineer",
      "company": "Tech Corp",
      "combined_score": 0.85,
      "similarity_score": 0.78,
      "skill_match_count": 5,
      "explanation": "This role matches your Python and ML skills..."
    }
  ]
}
  ↓
Frontend displays recommendations
```

**Key Files:**
- `backend/app/agents/recommender_agent.py`: Core recommendation logic
- `backend/app/utils/embeddings.py`: Cosine similarity calculation
- `backend/app/api/recommendations.py`: API endpoint

**Why Combined Scoring?**
- **Vector Similarity**: Captures semantic meaning (good for job descriptions)
- **Skill Matching**: Ensures required skills are present (more precise)
- **Balanced Approach**: Both methods complement each other

**Why Normalize Skills?**
- **Variations**: "Python", "python", "PYTHON" should match
- **Aliases**: "Node.js", "NodeJS", "nodejs" are the same
- **Consistency**: Ensures accurate skill matching

---

### 4. Career Advisor Chat Flow

```
User types message in chat
  ↓
POST /api/chat/message
  Body: { "message": "What skills do I need for ML?" }
  ↓
Backend: chat.py
  ├─ Get conversation history from database
  └─ Call Career Advisor Agent
  ↓
Career Advisor Agent (career_advisor_agent.py)
  ├─ Node 1: retrieve_context_node
  │   ├─ Generate embedding for user message
  │   ├─ Query jobs with vector similarity search
  │   ├─ Get top 5 relevant jobs
  │   └─ Include in context
  │
  └─ Node 2: generate_response_node
      ├─ Build prompt with:
      │   • System prompt (role: career advisor)
      │   • Conversation history (last 5 messages)
      │   • User message
      │   • Relevant job opportunities
      ├─ Call LLM (Euron API)
      └─ Return response
  ↓
Backend:
  ├─ Save user message to database
  ├─ Save AI response to database
  └─ Return response to frontend
  ↓
Frontend displays response in chat UI
```

**Key Files:**
- `backend/app/agents/career_advisor_agent.py`: Chat agent workflow
- `backend/app/api/chat.py`: Chat API endpoints
- `backend/app/models/conversation.py`: Conversation history storage

**Why RAG (Retrieval-Augmented Generation)?**
- **Context-Aware**: AI has access to relevant job data
- **Accurate**: Responses based on actual job postings
- **Dynamic**: Updates as new jobs are added

---

### 5. Job Scraping Flow

```
Admin triggers scraping (or scheduled task)
  ↓
POST /api/admin/scrape-jobs
  Body: { "source": "indeed", "search_terms": ["python", "developer"] }
  ↓
Backend: admin.py
  └─ Call Scraper Agent
  ↓
Scraper Agent (scraper_agent.py)
  ├─ Node 1: select_scraper_node
  │   └─ Choose scraper (IndeedScraper, RemoteOKScraper, etc.)
  │
  ├─ Node 2: scrape_jobs_node
  │   ├─ Use Playwright to load page
  │   ├─ Extract job listings
  │   ├─ Parse HTML with BeautifulSoup
  │   └─ Return raw job data
  │
  └─ Node 3: normalize_jobs_node
      ├─ Convert to unified schema:
      │   • title, company, location
      │   • description, required_skills
      │   • salary, job_type
      └─ Return normalized jobs
  ↓
Backend:
  ├─ For each normalized job:
  │   ├─ Check if job exists (by source_url)
  │   ├─ If new: Create JobPosting record
  │   ├─ Generate embedding from description
  │   ├─ Store embedding in description_embedding
  │   └─ Extract skills using LLM
  └─ Return count of scraped jobs
```

**Key Files:**
- `backend/app/agents/scraper_agent.py`: Scraping workflow
- `backend/app/agents/scrapers/indeed_scraper.py`: Indeed-specific scraper
- `backend/app/agents/scrapers/job_normalizer.py`: Schema normalization

**Why Normalize?**
- **Different Sources**: Each source has different data format
- **Unified Schema**: Makes querying and matching easier
- **Consistency**: All jobs follow same structure

---

## Key Components Deep Dive

### 1. Embedding System (`utils/embeddings.py`)

**What are Embeddings?**
- Numerical representations of text (vectors)
- Similar texts have similar vectors
- Example: "Python developer" and "Python programmer" → similar vectors

**How It Works:**
```python
# Generate embedding
text = "Python developer with ML experience"
embedding = embedding_generator.generate_embedding(text)
# Returns: [0.123, -0.456, 0.789, ...] (1536 numbers)

# Calculate similarity
similarity = cosine_similarity(embedding1, embedding2)
# Returns: 0.85 (85% similar)
```

**Why 1536 Dimensions?**
- `text-embedding-3-small` model outputs 1536-dimensional vectors
- More dimensions = more nuanced understanding
- Trade-off: Higher dimensions = more storage

**Storage in PostgreSQL:**
```python
# pgvector column type
resume_embedding = Column(Vector(1536))

# Query similar vectors
SELECT * FROM users 
ORDER BY resume_embedding <-> query_embedding 
LIMIT 10;
```

---

### 2. LangGraph Agents

**What is LangGraph?**
- Framework for building AI agent workflows
- Defines workflows as graphs (nodes = steps, edges = flow)

**Example: Recommender Agent**

```python
# Define state (data passed between nodes)
class RecommenderState(TypedDict):
    user_id: str
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

**Why Use Agents?**
- **Modularity**: Each step is separate (easy to test)
- **Debugging**: Can inspect state at each step
- **Flexibility**: Easy to add/remove steps
- **Reusability**: Agents can be composed together

---

### 3. Database Models

**User Model:**
```python
class User(Base):
    id = UUID
    email = String
    resume_text = Text              # Raw resume text
    resume_embedding = Vector(1536)  # pgvector embedding
    skills = JSON                    # ["Python", "ML", ...]
    experience_years = String
    onboarding_completed = Boolean
```

**Why JSON for Skills?**
- **Flexible**: Can store arrays easily
- **Queryable**: PostgreSQL supports JSON queries
- **Simple**: No need for separate skills table

**Job Model:**
```python
class JobPosting(Base):
    id = UUID
    title = String
    company = String
    description = Text
    description_embedding = Vector(1536)  # For similarity search
    required_skills = JSON                # ["Python", "Docker", ...]
    source_url = String                   # Unique identifier
    is_active = Boolean
```

**Why Store Embeddings?**
- **Performance**: Pre-computed embeddings = faster queries
- **Consistency**: Same embedding for same text
- **Cost**: Avoids regenerating embeddings on every query

---

### 4. API Structure (FastAPI)

**Dependency Injection:**
```python
@router.get("/recommendations")
async def get_recommendations(
    db: Session = Depends(get_db),           # Database session
    current_user: User = Depends(get_current_user)  # Authenticated user
):
    # db and current_user are automatically injected
```

**Why Dependency Injection?**
- **Testability**: Easy to mock dependencies
- **Reusability**: Same dependencies across endpoints
- **Clean Code**: No manual session management

**Error Handling:**
```python
try:
    recommendations = get_recommendations(user, db)
except Exception as e:
    # Log error
    # Return user-friendly message
    return {"recommendations": [], "error": str(e)}
```

---

## Data Flow Diagrams

### Recommendation Request Flow

```
┌──────────┐
│  Client  │
└────┬─────┘
     │ GET /api/recommendations
     ▼
┌─────────────────┐
│  FastAPI Router │
└────┬────────────┘
     │
     ▼
┌──────────────────┐
│ get_current_user │ (JWT verification)
└────┬─────────────┘
     │
     ▼
┌──────────────────────┐
│ get_recommendations  │
└────┬─────────────────┘
     │
     ├─► Get user embedding (from DB or generate)
     │
     ├─► Query jobs (PostgreSQL)
     │
     ├─► Score jobs (vector similarity + skill match)
     │
     ├─► Generate explanations (LLM)
     │
     └─► Return top 10 recommendations
```

### Embedding Generation Flow

```
┌─────────────┐
│ Resume Text │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ EmbeddingGenerator│
└──────┬───────────┘
       │
       │ POST to Euron API
       ▼
┌─────────────┐
│  Euron API  │
└──────┬──────┘
       │ Returns [0.123, -0.456, ...]
       ▼
┌──────────────────┐
│  Store in DB     │ (pgvector column)
└──────────────────┘
```

---

## Key Design Decisions

### 1. Why pgvector Instead of Separate Vector DB?

**Decision**: Use pgvector (PostgreSQL extension) instead of Pinecone/Weaviate

**Reasons:**
- **Simplicity**: One database for everything
- **ACID Transactions**: Embeddings and job data in same transaction
- **Cost**: No separate vector DB service needed
- **Performance**: Good enough for this scale

**Trade-off**: May need separate vector DB for very large scale (millions of jobs)

---

### 2. Why LangGraph Instead of Simple Functions?

**Decision**: Use LangGraph for agent workflows

**Reasons:**
- **Visualization**: Can see workflow as graph
- **State Management**: Automatic state passing
- **Extensibility**: Easy to add new steps
- **Debugging**: Can inspect state at each node

**Trade-off**: Slight overhead, but worth it for complex workflows

---

### 3. Why Combined Scoring (Vector + Skills)?

**Decision**: Use both vector similarity and skill matching

**Reasons:**
- **Vector Similarity**: Good for semantic matching (catches related concepts)
- **Skill Matching**: Precise (ensures required skills are present)
- **Balanced**: Neither method alone is perfect

**Example:**
- Job requires "Python" and "Machine Learning"
- User has "Python" and "ML" (abbreviation)
- Vector similarity: 0.9 (high, because ML ≈ Machine Learning)
- Skill match: 0.5 (only Python matches exactly)
- Combined: 0.7 (balanced score)

---

## Performance Optimizations

### 1. Embedding Caching
- **Store embeddings in DB**: Avoid regenerating on every request
- **Lazy generation**: Only generate if missing

### 2. Database Indexing
```python
# Indexed columns for fast queries
email = Column(String, index=True)
title = Column(String, index=True)
source_url = Column(String, unique=True, index=True)
```

### 3. Batch Processing
- **Scrape multiple jobs**: Process in batches
- **Generate embeddings**: Batch API calls when possible

### 4. Query Optimization
```python
# Limit results early
jobs = db.query(JobPosting).filter(
    JobPosting.is_active == True
).limit(500).all()  # Don't load all jobs
```

---

## Security Considerations

### 1. Password Hashing
- **bcrypt**: One-way hashing (can't reverse)
- **Salt**: Each password has unique salt

### 2. JWT Tokens
- **Signed**: Prevents tampering
- **Expiration**: Tokens expire after 30 minutes
- **Secure Storage**: Frontend stores in localStorage (consider httpOnly cookies for production)

### 3. SQL Injection Prevention
- **SQLAlchemy ORM**: Parameterized queries (automatic)
- **No raw SQL**: All queries go through ORM

### 4. File Upload Security
- **Size Limits**: Max 10MB
- **Type Validation**: Only PDF/DOCX allowed
- **Sanitization**: Validate file content

---

## Future Enhancements

1. **Real-time Notifications**: Alert users when new matching jobs appear
2. **Skill Gap Analysis**: Show what skills user needs to learn
3. **Interview Preparation**: AI-powered interview practice
4. **Resume Builder**: Generate optimized resumes for specific jobs
5. **Multi-language Support**: Support for non-English resumes/jobs

---

## Summary

This system combines:
- **Modern Web Stack**: Next.js + FastAPI for responsive UI and fast API
- **AI/ML**: LangGraph agents + embeddings for intelligent matching
- **Vector Search**: pgvector for semantic similarity
- **Scalable Architecture**: Modular design for easy extension

The key innovation is using **embeddings + skill matching** for recommendations, providing both semantic understanding and precise skill requirements.

