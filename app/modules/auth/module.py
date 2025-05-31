"""Authentication module implementation."""

import logging
from typing import Optional

from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.core.base_module import BaseModule
from app.modules.auth.api import router as auth_router
from app.modules.auth.config import AuthConfig
from app.modules.auth.services import AuthService


class AuthModule(BaseModule):
    """Authentication module for handling user authentication."""
    
    def __init__(self):
        super().__init__(
            name="auth",
            version="1.0.0",
            description="Authentication and authorization module",
            dependencies=[]  # Auth module has no dependencies
        )
        self.config = AuthConfig.from_env()
        self.auth_service: Optional[AuthService] = None
    
    def get_router(self) -> APIRouter:
        """Get the FastAPI router for authentication endpoints."""
        return auth_router
    
    async def initialize(
        self, 
        db: AsyncIOMotorDatabase, 
        redis: Optional[Redis] = None
    ) -> None:
        """Initialize the authentication module."""
        # Initialize auth service
        self.auth_service = AuthService(self.config)
        self.auth_service.initialize(db, redis)
        
        self.logger.info("認證模塊初始化完成")
    
    async def cleanup(self) -> None:
        """Cleanup authentication module resources."""
        if self.auth_service:
            # Perform any necessary cleanup
            pass
        
        self.logger.info("認證模塊清理完成")
    
    async def health_check(self) -> dict:
        """Perform health check for authentication module."""
        base_health = await super().health_check()
        
        # Add module-specific health checks
        auth_health = {
            "jwt_configured": bool(self.config.JWT_SECRET_KEY),
            "google_oauth_configured": bool(self.config.GOOGLE_CLIENT_ID),
            "service_initialized": self.auth_service is not None
        }
        
        base_health.update(auth_health)
        return base_health 