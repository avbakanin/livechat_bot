"""
Aiogram middleware for access control and other common functionality.
"""
from typing import Set, Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.dispatcher.event.handler import HandlerObject

from core.exceptions import UserException


class AccessMiddleware(BaseMiddleware):
    """Middleware to restrict bot access to specific user IDs."""
    
    def __init__(self, allowed_ids: Set[int]):
        self.allowed_ids = allowed_ids
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Check if user is allowed to use the bot."""
        
        # Get user ID from different event types
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id and user_id not in self.allowed_ids:
            if isinstance(event, Message):
                await event.answer("❌ Доступ запрещен. Обратитесь к администратору.")
            elif isinstance(event, CallbackQuery):
                await event.answer("❌ Доступ запрещен.", show_alert=True)
            return
        
        return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging user interactions."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Log user interactions."""
        import logging
        
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
            logging.info(f"Message from user {user_id}: {event.text[:50]}...")
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            logging.info(f"Callback from user {user_id}: {event.data}")
        
        return await handler(event, data)


class ServiceMiddleware(BaseMiddleware):
    """Middleware to inject services into handlers."""
    
    def __init__(self, user_service, message_service):
        self.user_service = user_service
        self.message_service = message_service
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Inject services into handler data."""
        data['user_service'] = self.user_service
        data['message_service'] = self.message_service
        return await handler(event, data)
