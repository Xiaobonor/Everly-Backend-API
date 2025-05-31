"""Media module implementation."""

import logging
from typing import Optional

from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.core.base_module import BaseModule
from app.modules.media.api import router as media_router
from app.modules.media.config import MediaConfig
from app.modules.media.services import MediaService


class MediaModule(BaseModule):
    """Media handling module for file uploads and management."""
    
    def __init__(self):
        super().__init__(
            name="media",
            version="1.0.0",
            description="Media file handling and storage module",
            dependencies=["auth"]  # Media module depends on auth module
        )
        self.config = MediaConfig.from_env()
        self.media_service: Optional[MediaService] = None
    
    def get_router(self) -> APIRouter:
        """Get the FastAPI router for media endpoints."""
        return media_router
    
    async def initialize(
        self, 
        db: AsyncIOMotorDatabase, 
        redis: Optional[Redis] = None
    ) -> None:
        """Initialize the media module."""
        # Initialize media service
        self.media_service = MediaService(self.config)
        self.media_service.initialize(db, redis)
        
        self.logger.info("媒體模塊初始化完成")
    
    async def cleanup(self) -> None:
        """Cleanup media module resources."""
        if self.media_service:
            # Perform any necessary cleanup
            pass
        
        self.logger.info("媒體模塊清理完成")
    
    async def health_check(self) -> dict:
        """Perform health check for media module."""
        base_health = await super().health_check()
        
        # Add module-specific health checks
        media_health = {
            "upload_path_configured": bool(self.config.MEDIA_UPLOAD_PATH),
            "base_url_configured": bool(self.config.BASE_URL),
            "service_initialized": self.media_service is not None,
            "max_file_size": f"{self.config.MAX_FILE_SIZE // (1024*1024)}MB"
        }
        
        base_health.update(media_health)
        return base_health 