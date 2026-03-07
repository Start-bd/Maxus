"""
Configuration Management for Manus Agent System
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "Manus Agent System"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None

    # Database - defaults to SQLite for Vercel (serverless)
    DATABASE_URL: str = "sqlite:///./manus_agent.db"

    # Redis (optional - for Celery background tasks)
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM Settings
    LLM_PROVIDER: str = "openai"  # "openai" or "anthropic"
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_MAX_TOKENS: int = 2000
    LLM_TEMPERATURE: float = 0.7

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    # News settings
    NEWS_FETCH_INTERVAL: int = 30  # minutes
    NEWS_CATEGORIES: List[str] = ["technology", "business", "science"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        # Allow extra fields from environment
        extra = "ignore"


settings = Settings()
