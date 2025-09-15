"""
FSM Middleware for caching user data and reducing database queries.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from shared.fsm.user_cache import UserCacheData, user_cache


class FSMMiddleware(BaseMiddleware):
    """Middleware for caching user data in FSM."""

    async def __call__(
        self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]
    ) -> Any:
        """Process event and inject cached user data."""

        # Extract user ID from event
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id:
            # Try to get cached user data
            cached_data = await user_cache.get(user_id)

            if cached_data:
                # Inject cached data into handler context
                data["cached_user"] = cached_data
                data["user_cache"] = user_cache
            else:
                # No cached data available, handlers will need to fetch from DB
                data["cached_user"] = None
                data["user_cache"] = user_cache

        return await handler(event, data)
