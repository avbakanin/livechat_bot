"""
I18n middleware for automatic language detection and setting.
"""
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Callable, Dict, Any, Awaitable

from shared.i18n import i18n


class I18nMiddleware(BaseMiddleware):
    """Middleware for handling internationalization."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process the event and set user language."""
        
        # Extract user language from the event
        user_language = None
        if isinstance(event, (Message, CallbackQuery)):
            if hasattr(event, 'from_user') and event.from_user:
                user_language = event.from_user.language_code
        
        # Set the language for this user
        if user_language:
            i18n.set_language(i18n.get_user_language(user_language))
        
        # Add i18n instance to data for handlers to use
        data['i18n'] = i18n
        
        return await handler(event, data)
