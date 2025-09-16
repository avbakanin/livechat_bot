"""
Event Bus interface for domain events and loose coupling.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Type, TypeVar

from ..events import DomainEvent

T = TypeVar('T', bound=DomainEvent)


class IEventBus(ABC):
    """Event Bus interface for publishing and subscribing to events."""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish domain event."""
        pass
    
    @abstractmethod
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """Publish multiple events."""
        pass
    
    @abstractmethod
    def subscribe(
        self, 
        event_type: Type[T], 
        handler: Callable[[T], Any]
    ) -> None:
        """Subscribe to event type."""
        pass
    
    @abstractmethod
    def unsubscribe(
        self, 
        event_type: Type[T], 
        handler: Callable[[T], Any]
    ) -> None:
        """Unsubscribe from event type."""
        pass
    
    @abstractmethod
    def get_subscribers(self, event_type: Type[T]) -> List[Callable[[T], Any]]:
        """Get all subscribers for event type."""
        pass


class IEventHandler(ABC):
    """Base interface for event handlers."""
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Handle domain event."""
        pass


class IEventStore(ABC):
    """Event Store interface for persisting domain events."""
    
    @abstractmethod
    async def save(self, event: DomainEvent) -> None:
        """Save domain event."""
        pass
    
    @abstractmethod
    async def get_events(
        self, 
        aggregate_id: str, 
        from_version: int = 0
    ) -> List[DomainEvent]:
        """Get events for aggregate."""
        pass
    
    @abstractmethod
    async def get_events_by_type(
        self, 
        event_type: Type[T]
    ) -> List[T]:
        """Get events by type."""
        pass
