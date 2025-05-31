"""Configuration for authentication module."""

from typing import Optional

class AuthConfig:
    """Configuration for authentication module."""
    
    # JWT settings
    JWT_SECRET_KEY: str = "your-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    # Redis cache settings for tokens
    TOKEN_CACHE_PREFIX: str = "auth_token:"
    TOKEN_CACHE_TTL: int = 1800  # 30 minutes
    
    @classmethod
    def from_env(cls):
        """Create config from environment variables."""
        import os
        
        config = cls()
        config.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", config.JWT_SECRET_KEY)
        config.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", config.JWT_ALGORITHM)
        config.ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", config.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        config.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        config.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
        
        return config 