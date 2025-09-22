from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from shared.i18n import i18n
from shared.utils.logger import get_logger


class I18nMiddleware(BaseMiddleware):
    def __init__(self):
        self.logger = get_logger("i18n_middleware")
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Process the event and set user language."""

        user_language = None
        user_id = None
        
        if isinstance(event, (Message, CallbackQuery)):
            if hasattr(event, "from_user") and event.from_user:
                user_id = event.from_user.id
                
                # Try to get saved language from database
                try:
                    user_service = data.get("user_service")
                    if user_service:
                        saved_language = await user_service.get_language(user_id)
                        if saved_language and saved_language != "en":  # If user has set a preference
                            user_language = saved_language
                            self.logger.debug(f"Using saved language '{user_language}' for user {user_id}")
                        else:
                            # Use Telegram language as fallback for new users
                            telegram_language = event.from_user.language_code or "en"
                            mapped_language = i18n.get_user_language(telegram_language)
                            user_language = mapped_language
                            # Save this as user's initial preference
                            try:
                                await user_service.set_language(user_id, mapped_language)
                            except Exception as e:
                                self.logger.warning(f"Failed to save initial language for user {user_id}: {e}")
                            self.logger.debug(f"Using Telegram language '{user_language}' for user {user_id}")
                    else:
                        # Fallback if user_service not available
                        telegram_language = event.from_user.language_code or "en"
                        mapped_language = i18n.get_user_language(telegram_language)
                        user_language = mapped_language
                        self.logger.debug(f"Using fallback language '{user_language}' for user {user_id}")
                except Exception as e:
                    self.logger.error(f"Error getting language for user {user_id}: {e}")
                    # Fallback to Telegram language
                    telegram_language = event.from_user.language_code or "en"
                    mapped_language = i18n.get_user_language(telegram_language)
                    user_language = mapped_language

        # Set the language for this user
        if user_language:
            i18n.set_language(user_language)

        # Add i18n instance to data for handlers to use
        data["i18n"] = i18n

        return await handler(event, data)
