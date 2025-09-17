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
                # First try to get user's saved language preference from database
                try:
                    from services.user.user import user_service

                    # Get database pool from data if available
                    pool = data.get('pool')
                    if pool:
                        saved_language = await user_service.get_user_language(pool, user_id)
                        if saved_language:  # Use saved language if exists
                            user_language = saved_language
                            logging.debug(f"Using saved language '{saved_language}' for user {user_id}")
                except Exception as e:
                    logging.warning(f"Failed to get user language for {user_id}: {e}")
                
                # If no saved language or failed to get it, use Telegram language
                if not user_language:
                    user_language = event.from_user.language_code or "ru"

        # Set the language for this user
        if user_language:
            mapped_language = i18n.get_user_language(user_language)
            i18n.set_language(mapped_language)

        # Add i18n instance to data for handlers to use
        data["i18n"] = i18n

        return await handler(event, data)
