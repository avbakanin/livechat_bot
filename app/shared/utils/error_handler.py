"""
Centralized error handling utilities for the bot.
"""
import logging
from typing import Any, Callable, Optional, Union
from functools import wraps

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message

from core.exceptions import BotException, DatabaseException, MessageException, OpenAIException


class ErrorHandler:
    """Centralized error handling for the bot."""
    
    @staticmethod
    def handle_telegram_error(error: TelegramBadRequest, context: Any = None) -> str:
        """Handle Telegram-specific errors."""
        error_message = str(error).lower()
        
        if "message is not modified" in error_message:
            return "message_not_modified"
        elif "message to edit not found" in error_message:
            return "message_not_found"
        elif "chat not found" in error_message:
            return "chat_not_found"
        elif "bot was blocked" in error_message:
            return "bot_blocked"
        elif "user is deactivated" in error_message:
            return "user_deactivated"
        else:
            return "telegram_error"
    
    @staticmethod
    def handle_database_error(error: Exception) -> str:
        """Handle database-specific errors."""
        error_message = str(error).lower()
        
        if "connection" in error_message:
            return "database_connection_error"
        elif "timeout" in error_message:
            return "database_timeout_error"
        elif "permission denied" in error_message:
            return "database_permission_error"
        else:
            return "database_error"
    
    @staticmethod
    async def send_error_response(
        context: Union[CallbackQuery, Message], 
        error_type: str,
        show_alert: bool = True
    ) -> None:
        """Send appropriate error response to user."""
        error_messages = {
            "message_not_modified": "Сообщение не изменилось",
            "message_not_found": "Сообщение устарело",
            "chat_not_found": "Чат не найден",
            "bot_blocked": "Бот заблокирован",
            "user_deactivated": "Пользователь деактивирован",
            "telegram_error": "❌ Ошибка обновления",
            "database_connection_error": "❌ Ошибка подключения к базе данных",
            "database_timeout_error": "❌ Таймаут базы данных",
            "database_permission_error": "❌ Ошибка доступа к базе данных",
            "database_error": "❌ Ошибка базы данных",
            "openai_error": "❌ Ошибка AI сервиса",
            "message_error": "❌ Ошибка обработки сообщения",
            "general_error": "❌ Произошла ошибка"
        }
        
        message = error_messages.get(error_type, error_messages["general_error"])
        
        if isinstance(context, CallbackQuery):
            if show_alert:
                await context.answer(message, show_alert=True)
            else:
                await context.answer(message)
        elif isinstance(context, Message):
            await context.answer(message)


def error_decorator(func: Callable) -> Callable:
    """
    Enhanced error decorator with centralized error handling.
    
    Args:
        func: The function to wrap with error handling
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TelegramBadRequest as e:
            logging.error(f"Telegram error in {func.__name__}: {e}")
            
            # Get context (first argument should be Message or CallbackQuery)
            context = None
            if args and isinstance(args[0], (CallbackQuery, Message)):
                context = args[0]
            
            error_type = ErrorHandler.handle_telegram_error(e, context)
            
            if context:
                # Special handling for message_not_modified
                if error_type == "message_not_modified" and isinstance(context, CallbackQuery):
                    await context.answer()
                else:
                    await ErrorHandler.send_error_response(context, error_type)
                    
        except DatabaseException as e:
            logging.error(f"Database error in {func.__name__}: {e}")
            
            context = None
            if args and isinstance(args[0], (CallbackQuery, Message)):
                context = args[0]
            
            error_type = ErrorHandler.handle_database_error(e)
            
            if context:
                await ErrorHandler.send_error_response(context, error_type)
                
        except (OpenAIException, MessageException) as e:
            logging.error(f"Service error in {func.__name__}: {e}")
            
            context = None
            if args and isinstance(args[0], (CallbackQuery, Message)):
                context = args[0]
            
            error_type = "openai_error" if isinstance(e, OpenAIException) else "message_error"
            
            if context:
                await ErrorHandler.send_error_response(context, error_type)
                
        except BotException as e:
            logging.error(f"Bot error in {func.__name__}: {e}")
            
            context = None
            if args and isinstance(args[0], (CallbackQuery, Message)):
                context = args[0]
            
            if context:
                await ErrorHandler.send_error_response(context, "general_error")
                
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {e}")
            
            context = None
            if args and isinstance(args[0], (CallbackQuery, Message)):
                context = args[0]
            
            if context:
                await ErrorHandler.send_error_response(context, "general_error")

    return wrapper


def safe_execute(func: Callable, *args, **kwargs) -> Optional[Any]:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or None if error occurred
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logging.error(f"Error in safe_execute for {func.__name__}: {e}")
        return None


async def safe_execute_async(func: Callable, *args, **kwargs) -> Optional[Any]:
    """
    Safely execute an async function with error handling.
    
    Args:
        func: Async function to execute
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or None if error occurred
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logging.error(f"Error in safe_execute_async for {func.__name__}: {e}")
        return None
