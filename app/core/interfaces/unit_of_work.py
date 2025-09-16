"""
Unit of Work pattern interface for transaction management.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncContextManager, Generic, TypeVar

from .repository import (
    IMessageRepository,
    IPaymentRepository, 
    ISubscriptionRepository,
    IUserRepository
)

T = TypeVar('T')


class IUnitOfWork(ABC, Generic[T]):
    """Unit of Work interface for transaction management."""
    
    @abstractmethod
    async def __aenter__(self) -> 'IUnitOfWork[T]':
        """Enter async context manager."""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        pass
    
    @abstractmethod
    async def commit(self) -> None:
        """Commit transaction."""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Rollback transaction."""
        pass
    
    @property
    @abstractmethod
    def users(self) -> IUserRepository[T]:
        """Get user repository."""
        pass
    
    @property
    @abstractmethod
    def messages(self) -> IMessageRepository[T]:
        """Get message repository."""
        pass
    
    @property
    @abstractmethod
    def payments(self) -> IPaymentRepository[T]:
        """Get payment repository."""
        pass
    
    @property
    @abstractmethod
    def subscriptions(self) -> ISubscriptionRepository[T]:
        """Get subscription repository."""
        pass


class IUnitOfWorkFactory(ABC):
    """Factory for creating Unit of Work instances."""
    
    @abstractmethod
    def create(self) -> AsyncContextManager[IUnitOfWork[Any]]:
        """Create new Unit of Work instance."""
        pass
