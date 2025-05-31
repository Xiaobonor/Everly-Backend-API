"""User module implementation."""

import logging
from typing import Optional

from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.core.base_module import BaseModule
from app.modules.user.api import router as user_router
from app.modules.user.config import UserConfig
from app.modules.user.services import UserService


class UserModule(BaseModule):
    """User management module for handling user operations."""
    
    def __init__(self):
        super().__init__(
            name="users",
            version="1.0.0",
            description="User management and profile module",
            dependencies=["auth"]  # User module depends on auth module
        )
        self.config = UserConfig.from_env()
        self.user_service: Optional[UserService] = None
    
    def get_router(self) -> APIRouter:
        """Get the FastAPI router for user endpoints."""
        return user_router
    
    async def initialize(
        self, 
        db: AsyncIOMotorDatabase, 
        redis: Optional[Redis] = None
    ) -> None:
        """Initialize the user module."""
        # Initialize user service
        self.user_service = UserService(self.config)
        self.user_service.initialize(db, redis)
        
        self.logger.info("用戶模塊初始化完成")
    
    async def cleanup(self) -> None:
        """Cleanup user module resources."""
        if self.user_service:
            # Perform any necessary cleanup
            pass
        
        self.logger.info("用戶模塊清理完成")
    
    async def health_check(self) -> dict:
        """Perform health check for user module."""
        base_health = await super().health_check()
        
        # Add module-specific health checks
        user_health = {
            "upload_path_configured": bool(self.config.PROFILE_UPLOAD_PATH),
            "base_url_configured": bool(self.config.BASE_URL),
            "service_initialized": self.user_service is not None
        }
        
        base_health.update(user_health)
        return base_health