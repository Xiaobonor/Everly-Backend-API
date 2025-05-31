"""Base module class for all feature modules."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis


class BaseModule(ABC):
    """Base class for all feature modules."""
    
    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        dependencies: Optional[List[str]] = None
    ):
        self.name = name
        self.version = version
        self.description = description
        self.dependencies = dependencies or []
        self.logger = logging.getLogger(f"modules.{name}")
        self._is_initialized = False
        self._db: Optional[AsyncIOMotorDatabase] = None
        self._redis: Optional[Redis] = None
        
    @property
    def is_initialized(self) -> bool:
        """Check if module is initialized."""
        return self._is_initialized
    
    @property
    def module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "dependencies": self.dependencies,
            "initialized": self._is_initialized
        }
    
    @abstractmethod
    def get_router(self) -> APIRouter:
        """Get the FastAPI router for this module."""
        pass
    
    @abstractmethod
    async def initialize(
        self, 
        db: AsyncIOMotorDatabase, 
        redis: Optional[Redis] = None
    ) -> None:
        """Initialize the module with database and cache connections."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup module resources."""
        pass
    
    async def _base_initialize(
        self, 
        db: AsyncIOMotorDatabase, 
        redis: Optional[Redis] = None
    ) -> None:
        """Base initialization logic."""
        self._db = db
        self._redis = redis
        self.logger.info(f"模塊 {self.name} 初始化開始")
        
        # Call module-specific initialization
        await self.initialize(db, redis)
        
        self._is_initialized = True
        self.logger.info(f"模塊 {self.name} 初始化完成")
    
    async def _base_cleanup(self) -> None:
        """Base cleanup logic."""
        self.logger.info(f"模塊 {self.name} 清理開始")
        
        # Call module-specific cleanup
        await self.cleanup()
        
        self._is_initialized = False
        self.logger.info(f"模塊 {self.name} 清理完成")
    
    def get_config_schema(self) -> Optional[Dict[str, Any]]:
        """Get configuration schema for this module."""
        return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for this module."""
        return {
            "name": self.name,
            "status": "healthy" if self._is_initialized else "not_initialized",
            "version": self.version
        } 