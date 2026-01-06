# Embeddings Storage Guide

## Where Embeddings Are Stored

Embeddings are stored in PostgreSQL database using **pgvector** extension as native vector types:

### 1. User Resume Embeddings
- **Table**: `users`
- **Column**: `resume_embedding` (Vector(1536))
- **Type**: pgvector Vector type
- **Generated from**: User's resume text
- **Model**: text-embedding-3-small (1536 dimensions)
- **API**: Euron API
- **When created**: When user uploads resume via `/api/user/resume`
- **Index**: `users_resume_embedding_idx` (IVFFlat for cosine similarity)

### 2. Job Description Embeddings
- **Table**: `job_postings`
- **Column**: `description_embedding` (Vector(1536))
- **Type**: pgvector Vector type
- **Generated from**: Job description text
- **Model**: text-embedding-3-small (1536 dimensions)
- **API**: Euron API
- **When created**: When jobs are scraped and normalized
- **Index**: `job_postings_description_embedding_idx` (IVFFlat for cosine similarity)

### 3. Job Title Embeddings
- **Table**: `job_postings`
- **Column**: `title_embedding` (Vector(1536))
- **Type**: pgvector Vector type
- **Generated from**: Job title text
- **Model**: text-embedding-3-small (1536 dimensions)
- **API**: Euron API
- **When created**: When jobs are scraped and normalized
- **Index**: `job_postings_title_embedding_idx` (IVFFlat for cosine similarity)

## Storage Format

Embeddings are stored as **native PostgreSQL vectors** using pgvector:
- **Type**: `vector(1536)` - Array of 1536 float values
- **Format**: Direct array storage (no JSON conversion needed)
- **Benefits**: Native vector operations, faster similarity search, vector indexes

## How to View Embeddings

### In PostgreSQL:
```sql
-- View user resume embedding (first few dimensions)
SELECT email, resume_embedding[1:5] as embedding_preview 
FROM users 
WHERE resume_embedding IS NOT NULL;

-- View job embeddings
SELECT title, description_embedding[1:5] as embedding_preview 
FROM job_postings 
WHERE description_embedding IS NOT NULL;

-- Find similar jobs using cosine distance
SELECT 
    id, 
    title, 
    company,
    1 - (description_embedding <=> (SELECT resume_embedding FROM users WHERE id = 'user-id')::vector) as similarity
FROM job_postings
WHERE description_embedding IS NOT NULL
ORDER BY description_embedding <=> (SELECT resume_embedding FROM users WHERE id = 'user-id')::vector
LIMIT 10;
```

### In Python:
```python
from app.models.user import User

# Get user embedding (pgvector returns as list directly)
user = db.query(User).first()
if user.resume_embedding:
    embedding = user.resume_embedding  # Already a list, no conversion needed
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
```

## Embedding Generation

Embeddings are generated using:
- **API**: Euron API (`https://api.euron.one/api/v1/euri/embeddings`)
- **Model**: `text-embedding-3-small`
- **Dimension**: 1536
- **Format**: List of floats

## Usage in Recommendations

1. User resume embedding is compared with job description embeddings
2. Cosine similarity is calculated (using pgvector's native operators or Python)
3. Jobs are ranked by similarity score
4. Combined with skill matching for final recommendations

## Performance Benefits

With pgvector:
- **Native vector operations**: Use PostgreSQL's `<=>` (cosine distance) operator
- **Vector indexes**: IVFFlat indexes for fast approximate nearest neighbor search
- **Better scalability**: Handles millions of vectors efficiently
- **Type safety**: Proper vector type instead of JSON strings

