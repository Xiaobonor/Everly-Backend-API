"""Event bus system for inter-module communication."""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
from datetime import datetime


class EventType(Enum):
    """Predefined event types for common module interactions."""
    
    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_LOGIN = "user.login"
    
    # Diary events
    DIARY_CREATED = "diary.created"
    DIARY_UPDATED = "diary.updated"
    DIARY_DELETED = "diary.deleted"
    DIARY_ENTRY_CREATED = "diary_entry.created"
    DIARY_ENTRY_UPDATED = "diary_entry.updated"
    DIARY_ENTRY_DELETED = "diary_entry.deleted"
    
    # Media events
    MEDIA_UPLOADED = "media.uploaded"
    MEDIA_DELETED = "media.deleted"
    
    # System events
    MODULE_INITIALIZED = "module.initialized"
    MODULE_SHUTDOWN = "module.shutdown"


@dataclass
class Event:
    """Event data structure."""
    
    id: str
    event_type: str
    source_module: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(
        cls,
        event_type: str,
        source_module: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> "Event":
        """Create a new event."""
        return cls(
            id=str(uuid.uuid4()),
            event_type=event_type,
            source_module=source_module,
            timestamp=datetime.utcnow(),
            data=data,
            metadata=metadata or {}
        )


class EventBus:
    """Event bus for inter-module communication."""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._middleware: List[Callable] = []
        self.logger = logging.getLogger(__name__)
        
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
        self.logger.debug(f"Subscribed to event: {event_type} -> {handler.__name__}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> bool:
        """Unsubscribe from an event type."""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                self.logger.debug(f"Unsubscribed from event: {event_type} -> {handler.__name__}")
                return True
            except ValueError:
                pass
        return False
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware for event processing."""
        self._middleware.append(middleware)
        self.logger.debug(f"Added middleware: {middleware.__name__}")
    
    async def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        self.logger.debug(f"Publishing event: {event.event_type} from {event.source_module}")
        
        # Apply middleware
        for middleware in self._middleware:
            try:
                event = await self._call_middleware(middleware, event)
                if event is None:
                    self.logger.debug("Event intercepted by middleware")
                    return
            except Exception as e:
                self.logger.error(f"Middleware processing error: {e}")
                continue
        
        # Call handlers
        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            self.logger.debug(f"No subscribers for event: {event.event_type}")
            return
        
        # Execute handlers concurrently
        tasks = []
        for handler in handlers:
            tasks.append(self._call_handler(handler, event))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    handler_name = handlers[i].__name__
                    self.logger.error(f"Event handler error {handler_name}: {result}")
    
    async def publish_and_wait(self, event: Event) -> List[Any]:
        """Publish an event and wait for all handlers to complete."""
        self.logger.debug(f"Publishing and waiting for event: {event.event_type}")
        
        # Apply middleware
        for middleware in self._middleware:
            try:
                event = await self._call_middleware(middleware, event)
                if event is None:
                    return []
            except Exception as e:
                self.logger.error(f"Middleware processing error: {e}")
                continue
        
        # Call handlers
        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            return []
        
        # Execute handlers concurrently and return results
        tasks = []
        for handler in handlers:
            tasks.append(self._call_handler(handler, event))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]
    
    async def _call_handler(self, handler: Callable, event: Event) -> Any:
        """Call an event handler."""
        try:
            if asyncio.iscoroutinefunction(handler):
                return await handler(event)
            else:
                return handler(event)
        except Exception as e:
            self.logger.error(f"Event handler error: {e}")
            raise
    
    async def _call_middleware(self, middleware: Callable, event: Event) -> Optional[Event]:
        """Call middleware and return modified event or None to stop processing."""
        try:
            if asyncio.iscoroutinefunction(middleware):
                return await middleware(event)
            else:
                return middleware(event)
        except Exception as e:
            self.logger.error(f"Middleware error: {e}")
            raise
    
    def list_subscribers(self) -> Dict[str, int]:
        """List all event types and their subscriber counts."""
        return {event_type: len(handlers) for event_type, handlers in self._handlers.items()}
    
    def clear_subscribers(self, event_type: Optional[str] = None) -> None:
        """Clear subscribers for a specific event type or all events."""
        if event_type:
            self._handlers.pop(event_type, None)
            self.logger.debug(f"Cleared subscribers for event: {event_type}")
        else:
            self._handlers.clear()
            self.logger.debug("Cleared all event subscribers")


# Global event bus instance
event_bus = EventBus()


# Helper functions for common events
async def emit_user_event(event_type: str, user_id: str, data: Dict[str, Any]) -> None:
    """Emit a user-related event."""
    event = Event.create(
        event_type=event_type,
        source_module="users",
        data={"user_id": user_id, **data}
    )
    await event_bus.publish(event)


async def emit_diary_event(event_type: str, diary_id: str, user_id: str, data: Dict[str, Any]) -> None:
    """Emit a diary-related event."""
    event = Event.create(
        event_type=event_type,
        source_module="diaries",
        data={"diary_id": diary_id, "user_id": user_id, **data}
    )
    await event_bus.publish(event)


async def emit_media_event(event_type: str, file_url: str, user_id: str, data: Dict[str, Any]) -> None:
    """Emit a media-related event."""
    event = Event.create(
        event_type=event_type,
        source_module="media",
        data={"file_url": file_url, "user_id": user_id, **data}
    )
    await event_bus.publish(event) 