# Setup Guide

## Prerequisites

1. **Python 3.11+**
2. **Node.js 18+**
3. **PostgreSQL 15+** with **pgvector** extension
4. **Redis** (for Celery background tasks)

## Backend Setup

### 1. Install PostgreSQL with pgvector

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql-15 postgresql-contrib
# Install pgvector extension
sudo apt-get install postgresql-15-pgvector
```

**macOS:**
```bash
brew install postgresql@15
brew install pgvector
```

**Windows:**
Download PostgreSQL from https://www.postgresql.org/download/windows/
Install pgvector from https://github.com/pgvector/pgvector

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE job_recommender;

# Enable pgvector extension
\c job_recommender
CREATE EXTENSION vector;
```

### 3. Install Python Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure Environment

Create `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/job_recommender
SECRET_KEY=your-secret-key-change-in-production
GROQ_API_KEY=your-groq-api-key-here
REDIS_URL=redis://localhost:6379/0
DEBUG=True
```

Get your ChatGroq API key from: https://console.groq.com/

### 5. Initialize Database

```bash
python init_db.py
```

### 6. Run Backend

```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Frontend

```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

## Redis Setup (for Background Tasks)

### Install Redis

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
```

**macOS:**
```bash
brew install redis
```

**Windows:**
Download from https://redis.io/download

### Run Redis

```bash
redis-server
```

## Running the Application

1. Start PostgreSQL
2. Start Redis: `redis-server`
3. Start Backend: `cd backend && uvicorn app.main:app --reload`
4. Start Frontend: `cd frontend && npm run dev`

## First Steps

1. Register a new account at http://localhost:3000/auth/register
2. Upload your resume (when onboarding is implemented)
3. Browse jobs and get AI recommendations
4. Chat with the career advisor

## Troubleshooting

### pgvector Extension Error
If you get an error about pgvector, make sure:
- PostgreSQL 15+ is installed
- pgvector extension is installed
- Run: `CREATE EXTENSION vector;` in your database

### ChatGroq API Errors
- Make sure you have a valid API key
- Check your API quota at https://console.groq.com/

### Import Errors
- Make sure all Python dependencies are installed: `pip install -r requirements.txt`
- Make sure you're in the virtual environment

