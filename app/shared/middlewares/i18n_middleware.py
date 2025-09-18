import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from shared.i18n import i18n


class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Process the event and set user language."""

        # Extract user language from the event
        user_language = None
        user_id = None
        
        if isinstance(event, (Message, CallbackQuery)):
            if hasattr(event, "from_user") and event.from_user:
                user_id = event.from_user.id
                # Language preference is not stored in database
                # Use Telegram language as fallback
                user_language = event.from_user.language_code or "ru"
                logging.debug(f"Using Telegram language '{user_language}' for user {user_id}")

        # Set the language for this user
        if user_language:
            mapped_language = i18n.get_user_language(user_language)
            i18n.set_language(mapped_language)

        # Add i18n instance to data for handlers to use
        data["i18n"] = i18n

        return await handler(event, data)
