"""
Aiogram middleware for logging and service injection functionality.
"""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging user interactions."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
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

    def __init__(self, user_service, message_service, pool=None):
        self.user_service = user_service
        self.message_service = message_service
        self.pool = pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Inject services into handler data."""
        data["user_service"] = self.user_service
        data["message_service"] = self.message_service
        if self.pool:
            data["pool"] = self.pool
        return await handler(event, data)
