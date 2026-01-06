# pgvector Migration Guide

## What Changed

The system now uses **pgvector** for storing embeddings instead of JSON strings in Text columns. This provides:

1. **Native vector operations** - Faster similarity searches
2. **Vector indexes** - IVFFlat indexes for efficient nearest neighbor search
3. **Better performance** - Optimized for vector similarity queries

## Migration Steps

### 1. Update Database Schema

The models have been updated to use `Vector(1536)` type. You need to:

1. **Drop and recreate tables** (if you have no important data):
   ```bash
   python init_db.py
   ```

2. **OR migrate existing data** (if you have existing embeddings):
   ```bash
   python migrate_to_pgvector.py
   ```

### 2. Verify pgvector Extension

Make sure pgvector extension is enabled:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Vector Indexes

The migration script creates IVFFlat indexes for faster similarity search:
- `users_resume_embedding_idx` - For user resume embeddings
- `job_postings_description_embedding_idx` - For job description embeddings  
- `job_postings_title_embedding_idx` - For job title embeddings

## Using pgvector for Similarity Search

You can now use native SQL for similarity search:

```sql
-- Find similar jobs using cosine distance
SELECT 
    id, 
    title, 
    company,
    1 - (description_embedding <=> '[0.1, 0.2, ...]'::vector) as similarity
FROM job_postings
WHERE description_embedding IS NOT NULL
ORDER BY description_embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;
```

## Code Changes

- **Storage**: Embeddings are now stored as arrays directly (no JSON conversion)
- **Retrieval**: pgvector automatically handles array conversion
- **Compatibility**: Code still works with old JSON format (backward compatible)

## Benefits

1. **Performance**: Vector indexes make similarity search much faster
2. **Native Operations**: Use PostgreSQL's vector operators (`<=>`, `<->`)
3. **Scalability**: Better performance as data grows
4. **Type Safety**: Proper vector type instead of JSON strings

