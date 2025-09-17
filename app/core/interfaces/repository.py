"""
Repository pattern interfaces for data access abstraction.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar('T')
ID = TypeVar('ID')


class IRepository(ABC, Generic[T, ID]):
    """Abstract repository interface for data access."""
    
    @abstractmethod
    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        """Get entity by ID."""
    
    @abstractmethod
    async def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """Get all entities with pagination."""
    
    @abstractmethod
    async def find_by(self, filters: Dict[str, Any]) -> List[T]:
        """Find entities by filters."""
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create new entity."""
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update existing entity."""
    
    @abstractmethod
    async def delete(self, entity_id: ID) -> bool:
        """Delete entity by ID."""
    
    @abstractmethod
    async def exists(self, entity_id: ID) -> bool:
        """Check if entity exists."""
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities matching filters."""


class IUserRepository(IRepository[T, ID]):
    """User-specific repository interface."""
    
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[T]:
        """Get user by Telegram ID."""
    
    @abstractmethod
    async def get_active_users(self, limit: Optional[int] = None) -> List[T]:
        """Get active users."""


class IMessageRepository(IRepository[T, ID]):
    """Message-specific repository interface."""
    
    @abstractmethod
    async def get_user_messages(
        self, 
        user_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> List[T]:
        """Get user messages with pagination."""
    
    @abstractmethod
    async def get_messages_by_date_range(
        self, 
        user_id: int, 
        start_date: str, 
        end_date: str
    ) -> List[T]:
        """Get messages in date range."""
    
    @abstractmethod
    async def count_user_messages_today(self, user_id: int) -> int:
        """Count user messages today."""
    
    @abstractmethod
    async def delete_user_messages(self, user_id: int) -> int:
        """Delete all user messages."""


class IPaymentRepository(IRepository[T, ID]):
    """Payment-specific repository interface."""
    
    @abstractmethod
    async def get_user_payments(self, user_id: int) -> List[T]:
        """Get user payments."""
    
    @abstractmethod
    async def get_pending_payments(self) -> List[T]:
        """Get pending payments."""


class ISubscriptionRepository(IRepository[T, ID]):
    """Subscription-specific repository interface."""
    
    @abstractmethod
    async def get_active_subscriptions(self) -> List[T]:
        """Get active subscriptions."""
    
    @abstractmethod
    async def get_expiring_subscriptions(self, days: int = 7) -> List[T]:
        """Get subscriptions expiring soon."""
