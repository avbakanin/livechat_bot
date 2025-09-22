"""
Centralized logging utilities for the bot.
"""
import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime


class BotLogger:
    """Centralized logging for the bot application."""
    
    def __init__(self, name: str = "livechat_bot"):
        self.logger = logging.getLogger(name)
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        if not self.logger.handlers:
            # Create formatter
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            
            # File handler (only file logging to avoid duplication)
            file_handler = logging.FileHandler("bot.log", encoding="utf-8")
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            
            # Security log handler
            security_handler = logging.FileHandler("security.log", encoding="utf-8")
            security_handler.setFormatter(formatter)
            security_handler.setLevel(logging.WARNING)
            
            # Add handlers (only file handlers)
            self.logger.addHandler(file_handler)
            self.logger.addHandler(security_handler)
            
            # Set level
            self.logger.setLevel(logging.DEBUG)
            
            # Prevent propagation to root logger to avoid duplication
            self.logger.propagate = False
            
            # Also setup root logger to capture all logging calls
            root_logger = logging.getLogger()
            if not root_logger.handlers:
                root_file_handler = logging.FileHandler("bot.log", encoding="utf-8")
                root_file_handler.setFormatter(formatter)
                root_file_handler.setLevel(logging.DEBUG)
                root_logger.addHandler(root_file_handler)
                root_logger.setLevel(logging.DEBUG)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self.logger.info(message, extra=extra)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self.logger.debug(message, extra=extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message."""
        self.logger.error(message, extra=extra)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        self.logger.critical(message, extra=extra)
    
    def log_user_action(self, user_id: int, action: str, details: Optional[str] = None):
        """Log user action with structured data."""
        extra = {
            "user_id": user_id,
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.info(f"User action: {action}", extra=extra)
    
    def log_security_event(self, event_type: str, user_id: Optional[int] = None, 
                          details: Optional[str] = None, severity: str = "warning"):
        """Log security-related event."""
        extra = {
            "event_type": event_type,
            "user_id": user_id,
            "details": details,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        
        if severity == "critical":
            self.critical(f"Security event: {event_type}", extra=extra)
        elif severity == "error":
            self.error(f"Security event: {event_type}", extra=extra)
        else:
            self.warning(f"Security event: {event_type}", extra=extra)
    
    def log_database_operation(self, operation: str, table: str, 
                              success: bool, duration_ms: Optional[float] = None):
        """Log database operation."""
        status = "success" if success else "failed"
        message = f"Database {operation} on {table}: {status}"
        
        extra = {
            "operation": operation,
            "table": table,
            "success": success,
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            self.debug(message, extra=extra)
        else:
            self.error(message, extra=extra)
    
    def log_api_call(self, service: str, endpoint: str, success: bool, 
                    response_time_ms: Optional[float] = None, error: Optional[str] = None):
        """Log API call."""
        status = "success" if success else "failed"
        message = f"API call to {service}/{endpoint}: {status}"
        
        extra = {
            "service": service,
            "endpoint": endpoint,
            "success": success,
            "response_time_ms": response_time_ms,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            self.debug(message, extra=extra)
        else:
            self.error(f"{message} - {error}", extra=extra)


# Global logger instance
bot_logger = BotLogger()


def get_logger(name: Optional[str] = None) -> BotLogger:
    """Get logger instance."""
    if name:
        return BotLogger(name)
    return bot_logger
