# AI Internship + Job Recommender Portal

A comprehensive web platform that recommends internships, jobs, roles, and career pathways using AI agents, user data, skills assessments, and market data.

## Tech Stack

### Frontend
- **Next.js 14** (App Router)
- **React 18**
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui**

### Backend
- **FastAPI**
- **PostgreSQL** with **pgvector**
- **SQLAlchemy** (ORM)
- **Alembic** (Migrations)
- **Celery** + **Redis** (Background tasks)

### AI Stack
- **LLM**: euron
- **Embeddings**: euron
- **Agent Framework**: LangGraph
- **RAG**: Vector search with pgvector

### Scraping
- **Playwright** (Dynamic content)
- **BeautifulSoup4** (HTML parsing)
- **Scrapy** (Structured scraping)

## Project Structure

```
ai_recommendation/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── models/      # Database models
│   │   ├── agents/      # LangGraph agents
│   │   ├── services/    # Business logic
│   │   ├── utils/       # Utilities (embeddings, parsing)
│   │   └── core/        # Config, auth, database
│   ├── alembic/         # Database migrations
│   └── requirements.txt
├── frontend/            # Next.js frontend
│   ├── app/             # Next.js app router
│   ├── components/      # React components
│   ├── lib/             # Utilities, API clients
│   └── package.json
├── agents/              # Shared agent utilities
└── docker/              # Docker configurations
```

## Features

1. **User Onboarding**: Skill capture and profile creation
2. **Resume Parsing**: Extract skills, experience, education
3. **Skill Gap Analysis**: Compare user skills vs job requirements
4. **Job Recommendations**: AI-powered personalized recommendations
5. **Profile Editing**: Update profile information, skills, and preferences
6. **Career Assistant Chat**: Conversational AI with conversation history
7. **Job Scraping**: Real-time job data collection from multiple sources
8. **Saved Jobs**: Bookmark and track interesting opportunities
9. **Admin Dashboard**: Manage jobs and users

## AI Agents

1. **Resume Parser Agent**: Extracts structured data from resumes
2. **Skill Gap Analysis Agent**: Identifies skill gaps
3. **Recommender Agent**: Generates personalized job recommendations
4. **Career Advisor Agent**: Provides career guidance via chat
5. **Market Data Scraper Agent**: Scrapes and ingests job postings
6. **Notification Agent**: Sends alerts for new matches

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with pgvector extension
- Redis (for Celery)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Environment Variables
Create `.env` files in both backend and frontend directories (see `.env.example`)

## License

MIT

