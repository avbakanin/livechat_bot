"""
Event Bus implementation for domain events and loose coupling.
"""

import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable, Dict, List, Type, TypeVar

from core.events import DomainEvent
from core.interfaces.event_bus import IEventBus, IEventHandler

T = TypeVar('T', bound=DomainEvent)


class EventBus(IEventBus):
    """Event Bus implementation for publishing and subscribing to events."""
    
    def __init__(self):
        self._subscribers: Dict[Type[DomainEvent], List[Callable]] = defaultdict(list)
        self._event_store: Optional[IEventStore] = None
        self._logger = logging.getLogger(__name__)
        
    async def publish(self, event: DomainEvent) -> None:
        """Publish domain event."""
        try:
            # Store event if event store is available
            if self._event_store:
                await self._event_store.save(event)
                
            # Get subscribers for this event type
            event_type = type(event)
            subscribers = self._subscribers.get(event_type, [])
            
            if not subscribers:
                self._logger.debug(f"No subscribers for event {event_type.__name__}")
                return
                
            # Execute all subscribers concurrently
            tasks = []
            for subscriber in subscribers:
                task = asyncio.create_task(self._execute_handler(subscriber, event))
                tasks.append(task)
                
            # Wait for all handlers to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            
            self._logger.debug(f"Published event {event_type.__name__} to {len(subscribers)} subscribers")
            
        except Exception as e:
            self._logger.error(f"Error publishing event {type(event).__name__}: {e}")
            
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """Publish multiple events."""
        tasks = [self.publish(event) for event in events]
        await asyncio.gather(*tasks, return_exceptions=True)
        
    def subscribe(self, event_type: Type[T], handler: Callable[[T], Any]) -> None:
        """Subscribe to event type."""
        self._subscribers[event_type].append(handler)
        self._logger.debug(f"Subscribed handler to {event_type.__name__}")
        
    def unsubscribe(self, event_type: Type[T], handler: Callable[[T], Any]) -> None:
        """Unsubscribe from event type."""
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
            self._logger.debug(f"Unsubscribed handler from {event_type.__name__}")
            
    def get_subscribers(self, event_type: Type[T]) -> List[Callable[[T], Any]]:
        """Get all subscribers for event type."""
        return self._subscribers.get(event_type, []).copy()
        
    async def _execute_handler(self, handler: Callable, event: DomainEvent) -> None:
        """Execute event handler with error handling."""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            self._logger.error(f"Error in event handler {handler.__name__}: {e}")
            
    def set_event_store(self, event_store: 'IEventStore') -> None:
        """Set event store for persistence."""
        self._event_store = event_store


class EventStore:
    """Simple in-memory event store implementation."""
    
    def __init__(self):
        self._events: List[DomainEvent] = []
        self._logger = logging.getLogger(__name__)
        
    async def save(self, event: DomainEvent) -> None:
        """Save domain event."""
        self._events.append(event)
        self._logger.debug(f"Saved event {type(event).__name__}")
        
    async def get_events(
        self, 
        aggregate_id: str, 
        from_version: int = 0
    ) -> List[DomainEvent]:
        """Get events for aggregate."""
        # Simple implementation - in real app would filter by aggregate_id
        return self._events[from_version:]
        
    async def get_events_by_type(
        self, 
        event_type: Type[T]
    ) -> List[T]:
        """Get events by type."""
        return [event for event in self._events if isinstance(event, event_type)]


# Global event bus instance
event_bus = EventBus()
event_store = EventStore()
event_bus.set_event_store(event_store)
