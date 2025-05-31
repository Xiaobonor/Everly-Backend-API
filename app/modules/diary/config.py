"""Configuration for diary module."""

import os
from typing import Optional


class DiaryConfig:
    """Configuration for diary module."""
    
    # Pagination settings
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    # Search settings
    SEARCH_RESULT_LIMIT: int = 50
    
    # Cache settings
    DIARY_CACHE_TTL: int = 300  # 5 minutes
    ENTRY_CACHE_TTL: int = 180  # 3 minutes
    
    @classmethod
    def from_env(cls):
        """Create config from environment variables."""
        config = cls()
        config.DEFAULT_PAGE_SIZE = int(
            os.getenv("DIARY_DEFAULT_PAGE_SIZE", config.DEFAULT_PAGE_SIZE)
        )
        config.MAX_PAGE_SIZE = int(
            os.getenv("DIARY_MAX_PAGE_SIZE", config.MAX_PAGE_SIZE)
        )
        config.SEARCH_RESULT_LIMIT = int(
            os.getenv("DIARY_SEARCH_RESULT_LIMIT", config.SEARCH_RESULT_LIMIT)
        )
        
        return config 