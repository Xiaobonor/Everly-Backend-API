"""Dependency injection container for modules."""

import logging
from typing import Any, Dict, Optional, Type, TypeVar, Generic

from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

T = TypeVar('T')


class DependencyContainer:
    """Dependency injection container for managing module dependencies."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
    def register_service(self, name: str, service_instance: Any) -> None:
        """Register a service instance."""
        self._services[name] = service_instance
        self.logger.debug(f"註冊服務: {name}")
    
    def register_singleton(self, name: str, instance: Any) -> None:
        """Register a singleton instance."""
        self._singletons[name] = instance
        self.logger.debug(f"註冊單例: {name}")
    
    def get_service(self, name: str) -> Optional[Any]:
        """Get a service by name."""
        return self._services.get(name)
    
    def get_singleton(self, name: str) -> Optional[Any]:
        """Get a singleton by name."""
        return self._singletons.get(name)
    
    def has_service(self, name: str) -> bool:
        """Check if a service is registered."""
        return name in self._services
    
    def has_singleton(self, name: str) -> bool:
        """Check if a singleton is registered."""
        return name in self._singletons
    
    def list_services(self) -> list:
        """List all registered services."""
        return list(self._services.keys())
    
    def list_singletons(self) -> list:
        """List all registered singletons."""
        return list(self._singletons.keys())
    
    def clear(self) -> None:
        """Clear all registered dependencies."""
        self._services.clear()
        self._singletons.clear()
        self.logger.debug("清除所有依賴")


class ServiceRegistry:
    """Service registry for module services."""
    
    def __init__(self, container: DependencyContainer):
        self.container = container
        self.logger = logging.getLogger(__name__)
        
    def register_module_services(
        self, 
        module_name: str, 
        db: AsyncIOMotorDatabase,
        redis: Optional[Redis] = None
    ) -> None:
        """Register common services for a module."""
        # Register database connection
        self.container.register_singleton(f"{module_name}.database", db)
        
        # Register Redis connection if available
        if redis:
            self.container.register_singleton(f"{module_name}.redis", redis)
            
        self.logger.debug(f"註冊模組 {module_name} 的基礎服務")
    
    def get_module_service(self, module_name: str, service_name: str) -> Optional[Any]:
        """Get a service for a specific module."""
        full_name = f"{module_name}.{service_name}"
        return self.container.get_service(full_name)
    
    def get_shared_service(self, service_name: str) -> Optional[Any]:
        """Get a shared service across modules."""
        return self.container.get_service(f"shared.{service_name}")


# Global dependency container
dependency_container = DependencyContainer()
service_registry = ServiceRegistry(dependency_container) 