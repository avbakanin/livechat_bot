"""
Unit of Work implementation for transaction management.
"""

import logging
from typing import Any, AsyncContextManager, Optional

import asyncpg

from core.interfaces.repository import (
    IMessageRepository,
    IPaymentRepository,
    ISubscriptionRepository,
    IUserRepository,
)
from core.interfaces.unit_of_work import IUnitOfWork, IUnitOfWorkFactory


class UnitOfWork(IUnitOfWork[Any]):
    """Unit of Work implementation with transaction management."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self._connection: Optional[asyncpg.Connection] = None
        self._transaction: Optional[asyncpg.transaction.Transaction] = None
        self._repositories: dict = {}
        self._committed = False
        
    async def __aenter__(self) -> 'UnitOfWork[Any]':
        """Enter async context manager and start transaction."""
        self._connection = await self.pool.acquire()
        self._transaction = self._connection.transaction()
        await self._transaction.start()
        return self
        
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager and handle transaction."""
        try:
            if exc_type is not None:
                # Exception occurred, rollback
                await self.rollback()
            elif not self._committed:
                # No exception but not committed, rollback
                await self.rollback()
        finally:
            if self._connection:
                await self.pool.release(self._connection)
                self._connection = None
                self._transaction = None
                
    async def commit(self) -> None:
        """Commit transaction."""
        if self._transaction:
            await self._transaction.commit()
            self._committed = True
            logging.debug("Transaction committed")
            
    async def rollback(self) -> None:
        """Rollback transaction."""
        if self._transaction:
            await self._transaction.rollback()
            logging.debug("Transaction rolled back")
            
    @property
    def users(self) -> IUserRepository[Any]:
        """Get user repository."""
        if 'users' not in self._repositories:
            from infrastructure.repositories.user_repository import UserRepository
            self._repositories['users'] = UserRepository(self._connection)
        return self._repositories['users']
        
    @property
    def messages(self) -> IMessageRepository[Any]:
        """Get message repository."""
        if 'messages' not in self._repositories:
            from infrastructure.repositories.message_repository import MessageRepository
            self._repositories['messages'] = MessageRepository(self._connection)
        return self._repositories['messages']
        
    @property
    def payments(self) -> IPaymentRepository[Any]:
        """Get payment repository."""
        if 'payments' not in self._repositories:
            from infrastructure.repositories.payment_repository import PaymentRepository
            self._repositories['payments'] = PaymentRepository(self._connection)
        return self._repositories['payments']
        
    @property
    def subscriptions(self) -> ISubscriptionRepository[Any]:
        """Get subscription repository."""
        if 'subscriptions' not in self._repositories:
            from infrastructure.repositories.subscription_repository import (
                SubscriptionRepository,
            )
            self._repositories['subscriptions'] = SubscriptionRepository(self._connection)
        return self._repositories['subscriptions']


class UnitOfWorkFactory(IUnitOfWorkFactory):
    """Factory for creating Unit of Work instances."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        
    def create(self) -> AsyncContextManager[UnitOfWork]:
        """Create new Unit of Work instance."""
        return UnitOfWork(self.pool)
