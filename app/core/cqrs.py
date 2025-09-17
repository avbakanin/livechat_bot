"""
CQRS (Command Query Responsibility Segregation) implementation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar('T')


class Command(ABC):
    """Base class for commands."""


class Query(ABC):
    """Base class for queries."""


class CommandHandler(ABC, Generic[T]):
    """Base class for command handlers."""
    
    @abstractmethod
    async def handle(self, command: Command) -> T:
        """Handle command."""


class QueryHandler(ABC, Generic[T]):
    """Base class for query handlers."""
    
    @abstractmethod
    async def handle(self, query: Query) -> T:
        """Handle query."""


# Commands
@dataclass
class CreateUserCommand(Command):
    """Command to create user."""
    telegram_id: int
    username: str = None
    first_name: str = None
    last_name: str = None


@dataclass
class UpdateUserCommand(Command):
    """Command to update user."""
    telegram_id: int
    changes: dict


@dataclass
class DeleteUserCommand(Command):
    """Command to delete user."""
    telegram_id: int


@dataclass
class SendMessageCommand(Command):
    """Command to send message."""
    user_id: int
    text: str


@dataclass
class CreateSubscriptionCommand(Command):
    """Command to create subscription."""
    user_id: int
    plan_type: str
    duration_days: int


@dataclass
class CreatePaymentCommand(Command):
    """Command to create payment."""
    user_id: int
    amount: float
    description: str


# Queries
@dataclass
class GetUserQuery(Query):
    """Query to get user."""
    telegram_id: int


@dataclass
class GetUserMessagesQuery(Query):
    """Query to get user messages."""
    user_id: int
    limit: int = 10
    offset: int = 0


@dataclass
class GetUserSubscriptionQuery(Query):
    """Query to get user subscription."""
    user_id: int


@dataclass
class GetUserPaymentsQuery(Query):
    """Query to get user payments."""
    user_id: int


@dataclass
class CanSendMessageQuery(Query):
    """Query to check if user can send message."""
    user_id: int


class CommandBus:
    """Command bus for handling commands."""
    
    def __init__(self):
        self._handlers: dict = {}
        
    def register_handler(self, command_type: type, handler: CommandHandler):
        """Register command handler."""
        self._handlers[command_type] = handler
        
    async def execute(self, command: Command) -> Any:
        """Execute command."""
        handler = self._handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler registered for command {type(command).__name__}")
            
        return await handler.handle(command)


class QueryBus:
    """Query bus for handling queries."""
    
    def __init__(self):
        self._handlers: dict = {}
        
    def register_handler(self, query_type: type, handler: QueryHandler):
        """Register query handler."""
        self._handlers[query_type] = handler
        
    async def execute(self, query: Query) -> Any:
        """Execute query."""
        handler = self._handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler registered for query {type(query).__name__}")
            
        return await handler.handle(query)


class CQRSMediator:
    """Mediator for CQRS operations."""
    
    def __init__(self, command_bus: CommandBus, query_bus: QueryBus):
        self.command_bus = command_bus
        self.query_bus = query_bus
        
    async def send_command(self, command: Command) -> Any:
        """Send command."""
        return await self.command_bus.execute(command)
        
    async def send_query(self, query: Query) -> Any:
        """Send query."""
        return await self.query_bus.execute(query)
