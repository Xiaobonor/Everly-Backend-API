"""Module manager for handling all feature modules."""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Type

from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.core.base_module import BaseModule
from app.core.dependency_injector import dependency_container, service_registry
from app.core.event_bus import event_bus, Event, EventType


class ModuleManager:
    """Manager for all feature modules."""
    
    def __init__(self):
        self.modules: Dict[str, BaseModule] = {}
        self.logger = logging.getLogger(__name__)
        self._db: Optional[AsyncIOMotorDatabase] = None
        self._redis: Optional[Redis] = None
        
        # Setup event bus for module communication
        self.event_bus = event_bus
        self.dependency_container = dependency_container
        self.service_registry = service_registry
        
    def register_module(self, module: BaseModule) -> None:
        """Register a new module."""
        if module.name in self.modules:
            raise ValueError(f"Module {module.name} is already registered")
        
        self.modules[module.name] = module
        self.logger.info(f"Registered module: {module.name} v{module.version}")
        
        # Register module in dependency container
        self.dependency_container.register_singleton(f"module.{module.name}", module)
    
    def get_module(self, name: str) -> Optional[BaseModule]:
        """Get a module by name."""
        return self.modules.get(name)
    
    def list_modules(self) -> List[str]:
        """List all registered module names."""
        return list(self.modules.keys())
    
    def get_modules_info(self) -> List[Dict[str, Any]]:
        """Get information about all modules."""
        return [module.module_info for module in self.modules.values()]
    
    async def initialize_all(
        self, 
        db: AsyncIOMotorDatabase, 
        redis: Optional[Redis] = None
    ) -> None:
        """Initialize all registered modules."""
        self._db = db
        self._redis = redis
        
        # Register shared services
        self.dependency_container.register_singleton("shared.database", db)
        if redis:
            self.dependency_container.register_singleton("shared.redis", redis)
        
        self.logger.info(f"Starting initialization of {len(self.modules)} modules")
        
        # Check dependencies
        await self._check_dependencies()
        
        # Initialize modules in dependency order
        initialization_order = self._get_initialization_order()
        
        for module_name in initialization_order:
            module = self.modules[module_name]
            try:
                # Register module-specific services
                self.service_registry.register_module_services(module_name, db, redis)
                
                # Initialize module
                await module._base_initialize(db, redis)
                
                # Emit module initialization event
                await self._emit_module_event(
                    EventType.MODULE_INITIALIZED.value, 
                    module_name, 
                    {"version": module.version}
                )
                
            except Exception as e:
                self.logger.error(f"Module {module_name} initialization failed: {str(e)}")
                raise
        
        self.logger.info("All modules have been initialized")
    
    async def cleanup_all(self) -> None:
        """Cleanup all modules."""
        self.logger.info("Starting cleanup of all modules")
        
        # Cleanup in reverse order
        cleanup_tasks = []
        for module in reversed(list(self.modules.values())):
            if module.is_initialized:
                cleanup_tasks.append(self._cleanup_module(module))
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        # Clear dependency container
        self.dependency_container.clear()
        
        # Clear event subscribers
        self.event_bus.clear_subscribers()
        
        self.logger.info("All modules have been cleaned up")
    
    async def _cleanup_module(self, module: BaseModule) -> None:
        """Cleanup a single module."""
        try:
            await module._base_cleanup()
            
            # Emit module shutdown event
            await self._emit_module_event(
                EventType.MODULE_SHUTDOWN.value,
                module.name,
                {"version": module.version}
            )
            
        except Exception as e:
            self.logger.error(f"Module {module.name} cleanup failed: {str(e)}")
    
    def create_main_router(self) -> APIRouter:
        """Create the main API router with all module routers."""
        main_router = APIRouter()
        
        for module in self.modules.values():
            if module.is_initialized:
                module_router = module.get_router()
                # Use module name as prefix, but handle special cases
                prefix = f"/{module.name}"
                
                # Special handling for auth module to maintain compatibility
                if module.name == "auth":
                    prefix = "/auth"
                elif module.name == "users":
                    prefix = "/users"
                elif module.name == "diaries":
                    prefix = "/diaries"
                elif module.name == "media":
                    prefix = "/media"
                
                main_router.include_router(
                    module_router,
                    prefix=prefix,
                    tags=[module.name]
                )
                self.logger.debug(f"Included routes for module {module.name} with prefix: {prefix}")
        
        return main_router
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Perform health check on all modules."""
        health_results = {}
        
        for module in self.modules.values():
            try:
                health_results[module.name] = await module.health_check()
            except Exception as e:
                health_results[module.name] = {
                    "name": module.name,
                    "status": "error",
                    "error": str(e)
                }
        
        overall_status = "healthy"
        for result in health_results.values():
            if result.get("status") != "healthy":
                overall_status = "degraded"
                break
        
        # Add system information
        system_info = {
            "event_subscribers": self.event_bus.list_subscribers(),
            "registered_services": len(self.dependency_container.list_services()),
            "registered_singletons": len(self.dependency_container.list_singletons())
        }
        
        return {
            "status": overall_status,
            "modules": health_results,
            "total_modules": len(self.modules),
            "system": system_info
        }
    
    async def _check_dependencies(self) -> None:
        """Check if all module dependencies are satisfied."""
        for module in self.modules.values():
            for dependency in module.dependencies:
                if dependency not in self.modules:
                        raise ValueError(
                        f"Dependency {dependency} for module {module.name} not found"
                    )
    
    def _get_initialization_order(self) -> List[str]:
        """Get the correct initialization order based on dependencies."""
        # Simple topological sort
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(module_name: str):
            if module_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving module {module_name}")
            
            if module_name not in visited:
                temp_visited.add(module_name)
                
                module = self.modules[module_name]
                for dependency in module.dependencies:
                    visit(dependency)
                
                temp_visited.remove(module_name)
                visited.add(module_name)
                order.append(module_name)
        
        for module_name in self.modules:
            if module_name not in visited:
                visit(module_name)
        
        return order
    
    async def _emit_module_event(self, event_type: str, module_name: str, data: Dict[str, Any]) -> None:
        """Emit a module-related event."""
        event = Event.create(
            event_type=event_type,
            source_module="system",
            data={"module_name": module_name, **data}
        )
        await self.event_bus.publish(event)
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get a service from the dependency container."""
        return self.dependency_container.get_service(service_name)
    
    def get_module_service(self, module_name: str, service_name: str) -> Optional[Any]:
        """Get a service for a specific module."""
        return self.service_registry.get_module_service(module_name, service_name)


# Global module manager instance
module_manager = ModuleManager() 