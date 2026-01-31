"""
Configuration settings for the application
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App
    APP_NAME: str = "Maintenance Intelligence API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/maintenance_intel"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # AI Services
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Claude settings
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    CLAUDE_MAX_TOKENS: int = 4096
    
    # OpenAI Embeddings settings
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    OPENAI_EMBEDDING_DIMENSION: int = 1536
    
    # Cost optimization settings
    EMBEDDING_BATCH_SIZE: int = 100  # Batch embeddings to reduce API calls
    EXTRACTION_CACHE_TTL_DAYS: int = 30  # Cache extractions for 30 days
    MIN_TEXT_LENGTH_FOR_EMBEDDING: int = 50  # Skip very short texts
    
    # Processing
    MAX_DOCUMENT_SIZE_MB: int = 50
    CONCURRENT_EXTRACTIONS: int = 5
    
    # File storage
    UPLOAD_DIR: str = "/tmp/maintenance_uploads"
    
    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Cost estimates (USD) - for tracking
COST_ESTIMATES = {
    "claude-sonnet-4-20250514": {
        "input_per_1k": 0.003,
        "output_per_1k": 0.015,
    },
    "text-embedding-ada-002": {
        "per_1k": 0.0001,
    },
    "text-embedding-3-small": {
        "per_1k": 0.00002,
    },
}
