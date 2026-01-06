from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Job Recommender"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:1234@localhost:5432/job_recommender"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Euron AI (LLM)
    EURON_API_KEY: str = "euri-64abfc6072d55cfc9e327111ce40c9ddead0821c6b3a3bc2d28e8d2ffc603782"
    EURON_MODEL: str = "gpt-4.1-nano"
    
    # Euron Embeddings API
    EURON_API_URL: str = "https://api.euron.one/api/v1/euri/embeddings"
    EURON_EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536  # text-embedding-3-small dimension
    
    # Redis (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # Scraping
    SCRAPING_RATE_LIMIT: int = 10  # requests per minute
    SCRAPING_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()





