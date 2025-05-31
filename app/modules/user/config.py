"""Configuration for user module."""

import os
from typing import Optional


class UserConfig:
    """Configuration for user module."""
    
    # File upload settings
    MAX_PROFILE_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    PROFILE_UPLOAD_PATH: str = "static/uploads/profiles"
    
    # Base URL for serving files
    BASE_URL: str = "http://localhost:8000"
    
    @classmethod
    def from_env(cls):
        """Create config from environment variables."""
        config = cls()
        config.MAX_PROFILE_IMAGE_SIZE = int(
            os.getenv("MAX_PROFILE_IMAGE_SIZE", config.MAX_PROFILE_IMAGE_SIZE)
        )
        config.PROFILE_UPLOAD_PATH = os.getenv(
            "PROFILE_UPLOAD_PATH", config.PROFILE_UPLOAD_PATH
        )
        config.BASE_URL = os.getenv("BASE_URL", config.BASE_URL)
        
        return config 