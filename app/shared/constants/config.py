"""
Unified configuration settings for the application.
"""
import os
import sys
from typing import Any, Dict, List, Optional, TypedDict

from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig(TypedDict):
    """Database configuration type."""
    user: Optional[str]
    password: Optional[str]
    host: Optional[str]
    port: int
    database: Optional[str]


class OpenAIConfig(TypedDict):
    """OpenAI configuration type."""
    api_key: Optional[str]
    model: str
    temperature: float
    max_tokens: int
    base_url: Optional[str]
    FREE_MESSAGE_LIMIT: int


class TelegramConfig(TypedDict):
    """Telegram bot configuration type."""
    token: Optional[str]
    allowed_user_ids: set[int]


class AppConfig(TypedDict):
    """Application configuration type."""
    TELEGRAM_TOKEN: Optional[str]
    OPENAI_API_KEY: Optional[str]
    YOOKASSA_SHOP_ID: Optional[str]
    YOOKASSA_SECRET_KEY: Optional[str]
    FREE_MESSAGE_LIMIT: int


# Database configuration
DATABASE_CONFIG: DatabaseConfig = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME"),
}

# OpenAI configuration
OPENAI_CONFIG: OpenAIConfig = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 1000,
    "base_url": None,  # Use default OpenAI API URL
    "FREE_MESSAGE_LIMIT": 50,
}

# Telegram configuration
TELEGRAM_CONFIG: TelegramConfig = {
    "token": os.getenv("TELEGRAM_TOKEN"),
    "allowed_user_ids": {627875032, 1512454100, 826795306, 284506756},  # Allowed user IDs
}

# Application configuration (legacy compatibility)
APP_CONFIG: AppConfig = {
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "YOOKASSA_SHOP_ID": os.getenv("YOOKASSA_SHOP_ID"),
    "YOOKASSA_SECRET_KEY": os.getenv("YOOKASSA_SECRET_KEY"),
    "FREE_MESSAGE_LIMIT": 50,
}

# Database configuration (legacy compatibility)
DB_CONFIG = DATABASE_CONFIG

# Language names mapping
LANGUAGE_NAMES = {
    "ru": "Русский",
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
    "sr": "Српски",
    "fr": "Français",
    "it": "Italiano",
    "tr": "Türkçe",
    "pl": "Polski",
}

# OpenAI client instance
openai_client = None


def initialize_openai_client():
    """Initialize OpenAI client."""
    global openai_client
    
    try:
        from openai import OpenAI
        
        if OPENAI_CONFIG["api_key"]:
            openai_client = OpenAI(
                api_key=OPENAI_CONFIG["api_key"],
                base_url=OPENAI_CONFIG["base_url"]
            )
            print("✅ OpenAI client initialized successfully")
        else:
            print("⚠️ OpenAI API key not found, client not initialized")
            openai_client = None
    except ImportError:
        print("❌ OpenAI library not installed")
        openai_client = None
    except Exception as e:
        print(f"❌ Error initializing OpenAI client: {e}")
        openai_client = None


# Initialize client on import
initialize_openai_client()


class ConfigValidator:
    """Configuration validator."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_required_env_vars(self, required_vars: List[str]) -> bool:
        """
        Validates required environment variables.
        
        Args:
            required_vars: List of required variables
            
        Returns:
            True if all variables found, False otherwise
        """
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.errors.append(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True
    
    def validate_database_config(self, config: Dict[str, Any]) -> bool:
        """
        Validates database configuration.
        
        Args:
            config: Database configuration
            
        Returns:
            True if configuration is valid, False otherwise
        """
        required_db_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME"]
        
        if not self.validate_required_env_vars(required_db_vars):
            return False
        
        # Check port
        port = config.get("port", 5432)
        if not isinstance(port, int) or port < 1 or port > 65535:
            self.errors.append(f"Invalid database port: {port}")
            return False
        
        return True
    
    def validate_telegram_config(self, config: Dict[str, Any]) -> bool:
        """
        Validates Telegram configuration.
        
        Args:
            config: Telegram configuration
            
        Returns:
            True if configuration is valid, False otherwise
        """
        if not config.get("token"):
            self.errors.append("Telegram token is required")
            return False
        
        # Check token format
        token = config["token"]
        if not token.startswith(("1", "2", "3", "4", "5", "6", "7", "8", "9")):
            self.errors.append("Invalid Telegram token format")
            return False
        
        if len(token.split(":")) != 2:
            self.errors.append("Invalid Telegram token format")
            return False
        
        return True
    
    def validate_openai_config(self, config: Dict[str, Any]) -> bool:
        """
        Validates OpenAI configuration.
        
        Args:
            config: OpenAI configuration
            
        Returns:
            True if configuration is valid, False otherwise
        """
        if not config.get("api_key"):
            self.errors.append("OpenAI API key is required")
            return False
        
        # Check API key format
        api_key = config["api_key"]
        if not api_key.startswith("sk-"):
            self.errors.append("Invalid OpenAI API key format")
            return False
        
        # Check message limit
        limit = config.get("FREE_MESSAGE_LIMIT", 50)
        if not isinstance(limit, int) or limit < 1:
            self.errors.append(f"Invalid FREE_MESSAGE_LIMIT: {limit}")
            return False
        
        return True
    
    def validate_all(self, db_config: Dict[str, Any], telegram_config: Dict[str, Any], 
                   openai_config: Dict[str, Any]) -> bool:
        """
        Validates all configuration.
        
        Args:
            db_config: Database configuration
            telegram_config: Telegram configuration
            openai_config: OpenAI configuration
            
        Returns:
            True if all configuration is valid, False otherwise
        """
        self.errors.clear()
        self.warnings.clear()
        
        db_valid = self.validate_database_config(db_config)
        telegram_valid = self.validate_telegram_config(telegram_config)
        openai_valid = self.validate_openai_config(openai_config)
        
        return db_valid and telegram_valid and openai_valid
    
    def print_errors(self) -> None:
        """Prints configuration errors."""
        if self.errors:
            print("❌ Configuration errors:")
            for error in self.errors:
                print(f"  - {error}")
    
    def print_warnings(self) -> None:
        """Prints configuration warnings."""
        if self.warnings:
            print("⚠️ Configuration warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
    
    def exit_on_errors(self) -> None:
        """Exits program on errors."""
        if self.errors:
            self.print_errors()
            print("\n💥 Application cannot start due to configuration errors!")
            sys.exit(1)


def validate_configuration(db_config: Dict[str, Any], telegram_config: Dict[str, Any], 
                          openai_config: Dict[str, Any]) -> bool:
    """
    Validates application configuration.
    
    Args:
        db_config: Database configuration
        telegram_config: Telegram configuration
        openai_config: OpenAI configuration
        
    Returns:
        True if configuration is valid, False otherwise
    """
    validator = ConfigValidator()
    
    if not validator.validate_all(db_config, telegram_config, openai_config):
        validator.print_errors()
        validator.print_warnings()
        validator.exit_on_errors()
        return False
    
    validator.print_warnings()
    print("✅ Configuration validation passed")
    return True