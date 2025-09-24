"""
Centralized configuration service for application settings.
"""

from typing import Dict, Any, Optional
from shared.constants import OPENAI_CONFIG, TELEGRAM_CONFIG, DATABASE_CONFIG


class ConfigService:
    """Centralized configuration service."""
    
    @staticmethod
    def get_openai_config() -> Dict[str, Any]:
        """Get OpenAI configuration."""
        return OPENAI_CONFIG.copy()
    
    @staticmethod
    def get_telegram_config() -> Dict[str, Any]:
        """Get Telegram configuration."""
        return TELEGRAM_CONFIG.copy()
    
    @staticmethod
    def get_database_config() -> Dict[str, Any]:
        """Get database configuration."""
        return DATABASE_CONFIG.copy()
    
    @staticmethod
    def get_free_message_limit() -> int:
        """Get free message limit per day."""
        return OPENAI_CONFIG.get("FREE_MESSAGE_LIMIT", 50)
    
    @staticmethod
    def get_max_message_length() -> int:
        """Get maximum message length."""
        return OPENAI_CONFIG.get("MAX_MESSAGE_LENGTH", 2500)
    
    @staticmethod
    def get_admin_user_id() -> int:
        """Get admin user ID."""
        return TELEGRAM_CONFIG.get("admin_user_id", 627875032)
    
    @staticmethod
    def is_user_allowed(user_id: int) -> bool:
        """Check if user is allowed to use the bot."""
        allowed_users = TELEGRAM_CONFIG.get("allowed_user_ids", set())
        return len(allowed_users) == 0 or user_id in allowed_users
    
    @staticmethod
    def get_sanitization_threshold() -> float:
        """Get text sanitization threshold."""
        return OPENAI_CONFIG.get("SANITIZATION_THRESHOLD", 0.8)
    
    @staticmethod
    def get_debug_command() -> str:
        """Get debug command prefix."""
        return "/debug_msg"
    
    @staticmethod
    def get_supported_languages() -> list:
        """Get list of supported languages."""
        return ["en", "ru", "de", "es", "fr", "it", "pl", "sr", "tr"]
    
    @staticmethod
    def get_default_language() -> str:
        """Get default language."""
        return "en"


# Global instance
config_service = ConfigService()
