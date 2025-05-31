"""Configuration for media module."""

import os
from typing import List, Optional


class MediaConfig:
    """Configuration for media module."""
    
    # File upload settings
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    ALLOWED_VIDEO_TYPES: List[str] = ["video/mp4", "video/avi", "video/mov", "video/wmv"]
    ALLOWED_AUDIO_TYPES: List[str] = ["audio/mpeg", "audio/wav", "audio/ogg", "audio/mp3"]
    
    # Upload paths
    MEDIA_UPLOAD_PATH: str = "static/uploads/media"
    
    # Base URL for serving files
    BASE_URL: str = "http://localhost:8000"
    
    @classmethod
    def from_env(cls):
        """Create config from environment variables."""
        config = cls()
        config.MAX_FILE_SIZE = int(
            os.getenv("MAX_MEDIA_FILE_SIZE", config.MAX_FILE_SIZE)
        )
        config.MEDIA_UPLOAD_PATH = os.getenv(
            "MEDIA_UPLOAD_PATH", config.MEDIA_UPLOAD_PATH
        )
        config.BASE_URL = os.getenv("BASE_URL", config.BASE_URL)
        
        return config

    @property
    def allowed_types(self) -> List[str]:
        """Get all allowed file types."""
        return self.ALLOWED_IMAGE_TYPES + self.ALLOWED_VIDEO_TYPES + self.ALLOWED_AUDIO_TYPES 