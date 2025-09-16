"""
Универсальный декоратор для оптимизации callback обработчиков.
"""

import logging
from functools import wraps
from typing import Callable, Any
from aiogram.types import CallbackQuery
from aiogram.exceptions import MessageNotModified, MessageToEditNotFound


def optimize_callback_edit(func: Callable) -> Callable:
    """
    Декоратор для оптимизации callback обработчиков с edit_text.
    
    Автоматически обрабатывает:
    - MessageNotModified (контент не изменился)
    - MessageToEditNotFound (сообщение удалено)
    - Общие исключения с логированием
    
    Использование:
    @optimize_callback_edit
    async def my_callback(callback: CallbackQuery):
        await callback.message.edit_text("New text")
        await callback.answer()
    """
    
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        try:
            return await func(callback, *args, **kwargs)
            
        except MessageNotModified:
            # Контент не изменился - просто подтверждаем
            await callback.answer()
            
        except MessageToEditNotFound:
            # Сообщение удалено - показываем alert
            await callback.answer("Сообщение устарело", show_alert=True)
            
        except Exception as e:
            # Логируем ошибку и показываем пользователю
            logging.error(f"Callback error in {func.__name__}: {e}")
            await callback.answer("❌ Ошибка обновления", show_alert=True)
    
    return wrapper


# Альтернативный вариант с более детальным логированием
def optimize_callback_edit_detailed(func: Callable) -> Callable:
    """
    Расширенный декоратор с детальным логированием.
    """
    
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        try:
            return await func(callback, *args, **kwargs)
            
        except MessageNotModified:
            logging.debug(f"Message not modified in {func.__name__} for user {callback.from_user.id}")
            await callback.answer()
            
        except MessageToEditNotFound:
            logging.warning(f"Message to edit not found in {func.__name__} for user {callback.from_user.id}")
            await callback.answer("Сообщение устарело", show_alert=True)
            
        except Exception as e:
            logging.error(f"Callback error in {func.__name__} for user {callback.from_user.id}: {e}")
            await callback.answer("❌ Ошибка обновления", show_alert=True)
    
    return wrapper
