# app/shared/decorators/error_handler.py
"""
Централизованная обработка ошибок для обработчиков.
"""

import logging
from functools import wraps
from typing import Callable, Any, Awaitable

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message


def handle_telegram_errors(func: Callable) -> Callable:
    """
    Декоратор для централизованной обработки ошибок Telegram.
    
    Args:
        func: Функция-обработчик
        
    Returns:
        Обернутая функция с обработкой ошибок
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TelegramBadRequest as e:
            error_msg = str(e).lower()
            
            # Получаем объект события (Message или CallbackQuery)
            event = None
            for arg in args:
                if isinstance(arg, (Message, CallbackQuery)):
                    event = arg
                    break
            
            if event:
                if "message is not modified" in error_msg:
                    if isinstance(event, CallbackQuery):
                        await event.answer()
                elif "message to edit not found" in error_msg:
                    if isinstance(event, CallbackQuery):
                        await event.answer("Сообщение устарело", show_alert=True)
                else:
                    logging.error(f"Telegram error in {func.__name__}: {e}")
                    if isinstance(event, CallbackQuery):
                        await event.answer("❌ Ошибка обновления", show_alert=True)
                    elif isinstance(event, Message):
                        await event.answer("❌ Произошла ошибка")
            else:
                logging.error(f"Telegram error in {func.__name__}: {e}")
                
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {e}")
            
            # Пытаемся отправить сообщение об ошибке
            event = None
            for arg in args:
                if isinstance(arg, (Message, CallbackQuery)):
                    event = arg
                    break
            
            if event:
                try:
                    if isinstance(event, CallbackQuery):
                        await event.answer("❌ Произошла ошибка", show_alert=True)
                    elif isinstance(event, Message):
                        await event.answer("❌ Произошла ошибка")
                except:
                    pass  # Если не можем отправить сообщение, просто логируем
    
    return wrapper


def handle_database_errors(func: Callable) -> Callable:
    """
    Декоратор для обработки ошибок базы данных.
    
    Args:
        func: Функция-обработчик
        
    Returns:
        Обернутая функция с обработкой ошибок БД
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Database error in {func.__name__}: {e}")
            
            # Получаем объект события
            event = None
            for arg in args:
                if isinstance(arg, (Message, CallbackQuery)):
                    event = arg
                    break
            
            if event:
                try:
                    if isinstance(event, CallbackQuery):
                        await event.answer("❌ Ошибка базы данных", show_alert=True)
                    elif isinstance(event, Message):
                        await event.answer("❌ Ошибка базы данных")
                except:
                    pass
    
    return wrapper


def handle_openai_errors(func: Callable) -> Callable:
    """
    Декоратор для обработки ошибок OpenAI API.
    
    Args:
        func: Функция-обработчик
        
    Returns:
        Обернутая функция с обработкой ошибок OpenAI
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(f"OpenAI error in {func.__name__}: {e}")
            
            # Получаем объект события
            event = None
            for arg in args:
                if isinstance(arg, (Message, CallbackQuery)):
                    event = arg
                    break
            
            if event:
                try:
                    if isinstance(event, CallbackQuery):
                        await event.answer("❌ Ошибка AI сервиса", show_alert=True)
                    elif isinstance(event, Message):
                        await event.answer("❌ Ошибка AI сервиса")
                except:
                    pass
    
    return wrapper
