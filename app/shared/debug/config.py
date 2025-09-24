"""
Centralized debug configuration and utilities.
"""

from typing import Any, Dict, Optional, Union
from datetime import datetime


# Debug Configuration
class DebugConfig:
    """Centralized debug configuration."""
    
    # Admin settings
    ADMIN_USER_ID = 627875032
    
    # Debug commands
    DEBUG_COMMAND = "/debug_msg"
    DEBUG_PERSONA = "persona"
    DEBUG_PERSONA_STATS = "persona_stats"
    DEBUG_PERSONA_DATA = "persona_data"
    
    # Message settings
    MAX_MESSAGE_LENGTH = 2500
    SANITIZATION_THRESHOLD = 0.8
    
    # Debug limits
    MAX_DEBUG_TEXT_LENGTH = 100
    MAX_DEBUG_RESPONSE_LENGTH = 4000


class AdminHelper:
    """Helper class for admin operations."""
    
    @staticmethod
    def is_admin(user_id: int) -> bool:
        """Check if user is admin."""
        return user_id == DebugConfig.ADMIN_USER_ID
    
    @staticmethod
    def get_admin_user_id() -> int:
        """Get admin user ID."""
        return DebugConfig.ADMIN_USER_ID


class DebugTextHelper:
    """Helper class for text processing in debug operations."""
    
    @staticmethod
    def truncate_text(text: Optional[str], max_length: int = DebugConfig.MAX_DEBUG_TEXT_LENGTH) -> str:
        """Truncate text for debug output."""
        if not text:
            return "None"
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length] + "..."
    
    @staticmethod
    def format_timestamp(timestamp: Optional[datetime]) -> str:
        """Format timestamp for debug output."""
        if not timestamp:
            return "None"
        
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def safe_get_attr(obj: Any, attr_name: str, default: Any = None) -> Any:
        """Safely get attribute from object."""
        try:
            return getattr(obj, attr_name, default)
        except (AttributeError, TypeError):
            return default


class DebugValidationHelper:
    """Helper class for debug validation."""
    
    @staticmethod
    def validate_debug_command(command: str) -> Optional[str]:
        """Validate debug command format."""
        if not command:
            return "Empty command"
        
        parts = command.split()
        if len(parts) < 1:
            return "Invalid command format"
        
        if parts[0] != DebugConfig.DEBUG_COMMAND:
            return "Not a debug command"
        
        if len(parts) > 2:
            return "Too many command arguments"
        
        return None
    
    @staticmethod
    def get_debug_type(command: str) -> str:
        """Extract debug type from command."""
        parts = command.split()
        if len(parts) > 1:
            return parts[1]
        return "message"  # Default debug type


class DebugPerformanceHelper:
    """Helper class for performance monitoring in debug operations."""
    
    @staticmethod
    def measure_time(func_name: str):
        """Decorator to measure function execution time."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                import time
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Log performance if needed
                if execution_time > 1.0:  # Log slow operations
                    import logging
                    logging.warning(f"Slow debug operation {func_name}: {execution_time:.3f}s")
                
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """Get current memory usage information."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            return {
                "rss": memory_info.rss,  # Resident Set Size
                "vms": memory_info.vms,  # Virtual Memory Size
                "percent": process.memory_percent(),
                "available": psutil.virtual_memory().available
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}


# Export commonly used items
__all__ = [
    "DebugConfig",
    "AdminHelper", 
    "DebugTextHelper",
    "DebugValidationHelper",
    "DebugPerformanceHelper"
]
