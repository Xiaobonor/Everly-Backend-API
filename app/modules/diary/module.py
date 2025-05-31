"""Diary module implementation."""

import logging
from typing import Optional

from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.core.base_module import BaseModule
from app.modules.diary.api import router as diary_router
from app.modules.diary.config import DiaryConfig
from app.modules.diary.services import DiaryService


class DiaryModule(BaseModule):
    """Diary management module for handling diary entries."""
    
    def __init__(self):
        super().__init__(
            name="diaries",
            version="1.0.0",
            description="Diary and journal entry management module",
            dependencies=["auth", "users"]  # Diary module depends on auth and users
        )
        self.config = DiaryConfig.from_env()
        self.diary_service: Optional[DiaryService] = None
    
    def get_router(self) -> APIRouter:
        """Get the FastAPI router for diary endpoints."""
        return diary_router
    
    async def initialize(
        self, 
        db: AsyncIOMotorDatabase, 
        redis: Optional[Redis] = None
    ) -> None:
        """Initialize the diary module."""
        # Initialize diary service
        self.diary_service = DiaryService(self.config)
        self.diary_service.initialize(db, redis)
        
        self.logger.info("日記模塊初始化完成")
    
    async def cleanup(self) -> None:
        """Cleanup diary module resources."""
        if self.diary_service:
            # Perform any necessary cleanup
            pass
        
        self.logger.info("日記模塊清理完成")
    
    async def health_check(self) -> dict:
        """Perform health check for diary module."""
        base_health = await super().health_check()
        
        # Add module-specific health checks
        diary_health = {
            "max_page_size": self.config.MAX_PAGE_SIZE,
            "search_limit": self.config.SEARCH_RESULT_LIMIT,
            "service_initialized": self.diary_service is not None
        }
        
        base_health.update(diary_health)
        return base_health 