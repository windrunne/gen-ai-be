"""
Application configuration using Pydantic settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_V1_PREFIX: str = "/api"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Database Configuration (Supabase PostgreSQL)
    # Can be overridden via .env file or environment variable
    DATABASE_URL: str = "postgresql://postgres.jyjmkoyymfogepnlryyg:Chris111!!!@aws-1-us-east-2.pooler.supabase.com:6543/postgres"
    
    # Application Settings
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
