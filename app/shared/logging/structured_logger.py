# app/shared/logging/structured_logger.py
"""
Структурированное логирование с контекстом.
"""

import json
import logging
import time
from datetime import datetime
from functools import wraps
from typing import Any, Dict, Optional


class StructuredLogger:
    """Структурированный логгер с контекстом."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs) -> None:
        """Устанавливает контекст для логов."""
        self.context.update(kwargs)
    
    def clear_context(self) -> None:
        """Очищает контекст."""
        self.context.clear()
    
    def _format_message(self, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """Форматирует сообщение с контекстом."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "context": self.context.copy()
        }
        
        if extra:
            log_data["extra"] = extra
        
        return json.dumps(log_data, ensure_ascii=False)
    
    def info(self, message: str, **kwargs) -> None:
        """Логирует информационное сообщение."""
        self.logger.info(self._format_message(message, kwargs))
    
    def warning(self, message: str, **kwargs) -> None:
        """Логирует предупреждение."""
        self.logger.warning(self._format_message(message, kwargs))
    
    def error(self, message: str, **kwargs) -> None:
        """Логирует ошибку."""
        self.logger.error(self._format_message(message, kwargs))
    
    def debug(self, message: str, **kwargs) -> None:
        """Логирует отладочное сообщение."""
        self.logger.debug(self._format_message(message, kwargs))


def log_function_call(func_name: str = None):
    """
    Декоратор для логирования вызовов функций.
    
    Args:
        func_name: Имя функции (если не указано, берется из функции)
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = func_name or func.__name__
            logger = StructuredLogger(f"function.{name}")
            
            start_time = time.time()
            
            logger.info(f"Function {name} started", 
                       args_count=len(args), 
                       kwargs_keys=list(kwargs.keys()))
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(f"Function {name} completed successfully",
                           execution_time=execution_time)
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                logger.error(f"Function {name} failed",
                           error=str(e),
                           error_type=type(e).__name__,
                           execution_time=execution_time)
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = func_name or func.__name__
            logger = StructuredLogger(f"function.{name}")
            
            start_time = time.time()
            
            logger.info(f"Function {name} started",
                       args_count=len(args),
                       kwargs_keys=list(kwargs.keys()))
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(f"Function {name} completed successfully",
                           execution_time=execution_time)
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                logger.error(f"Function {name} failed",
                           error=str(e),
                           error_type=type(e).__name__,
                           execution_time=execution_time)
                
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def log_user_action(action: str):
    """
    Декоратор для логирования действий пользователя.
    
    Args:
        action: Тип действия пользователя
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Ищем user_id в аргументах
            user_id = None
            for arg in args:
                if hasattr(arg, 'from_user') and hasattr(arg.from_user, 'id'):
                    user_id = arg.from_user.id
                    break
            
            logger = StructuredLogger(f"user_action.{action}")
            logger.set_context(user_id=user_id, action=action)
            
            start_time = time.time()
            
            logger.info(f"User action {action} started")
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(f"User action {action} completed successfully",
                           execution_time=execution_time)
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                logger.error(f"User action {action} failed",
                           error=str(e),
                           error_type=type(e).__name__,
                           execution_time=execution_time)
                
                raise
        
        return wrapper
    
    return decorator


# Глобальные логгеры
user_logger = StructuredLogger("user")
system_logger = StructuredLogger("system")
security_logger = StructuredLogger("security")
performance_logger = StructuredLogger("performance")
