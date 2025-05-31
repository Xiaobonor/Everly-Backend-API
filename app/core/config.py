"""Configuration settings for the application."""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pydantic import validator
from pydantic_settings import BaseSettings

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    API_VERSION: str = os.getenv("API_VERSION", "v1")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Everly API")
    ENV: str = os.getenv("ENV", "development")
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

    # MongoDB Settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017/everly")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "everly")
    
    # Redis Settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # Authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-jwt-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_SECONDS: int = int(os.getenv("JWT_EXPIRATION_SECONDS", "604800"))
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_REDIRECT_URI: Optional[str] = os.getenv("GOOGLE_REDIRECT_URI")
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Additional validations
    @validator("MONGODB_URL")
    def validate_mongodb_url(cls, v: str) -> str:
        """Validate that the MongoDB URL is properly formatted."""
        if not v.startswith(("mongodb://", "mongodb+srv://")):
            raise ValueError("MONGODB_URL must start with mongodb:// or mongodb+srv://")
        return v

    class Config:
        """Pydantic config class."""

        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings() 