from functools import wraps
import logging

from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest


# Декоратор для единообразной обработки ошибок
def error_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TelegramBadRequest as e:
            if "message is not modified" in str(e).lower():
                if len(args) > 0 and isinstance(args[0], CallbackQuery):
                    await args[0].answer()
            elif "message to edit not found" in str(e).lower():
                if len(args) > 0 and isinstance(args[0], CallbackQuery):
                    await args[0].answer("Сообщение устарело", show_alert=True)
            else:
                logging.error(f"Telegram error in {func.__name__}: {e}")
                if len(args) > 0 and isinstance(args[0], (CallbackQuery, Message)):
                    await args[0].answer("❌ Ошибка обновления", show_alert=True)
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {e}")
            if len(args) > 0 and isinstance(args[0], (CallbackQuery, Message)):
                await args[0].answer("❌ Произошла ошибка", show_alert=True)

    return wrapper
