# app/config/validator.py
"""
Валидация конфигурации приложения.
"""

import os
import sys
from typing import Dict, Any, List


class ConfigValidator:
    """Валидатор конфигурации приложения."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_required_env_vars(self, required_vars: List[str]) -> bool:
        """
        Проверяет наличие обязательных переменных окружения.
        
        Args:
            required_vars: Список обязательных переменных
            
        Returns:
            True если все переменные найдены, False иначе
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
        Проверяет конфигурацию базы данных.
        
        Args:
            config: Конфигурация БД
            
        Returns:
            True если конфигурация валидна, False иначе
        """
        required_db_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME"]
        
        if not self.validate_required_env_vars(required_db_vars):
            return False
        
        # Проверяем порт
        port = config.get("port", 5432)
        if not isinstance(port, int) or port < 1 or port > 65535:
            self.errors.append(f"Invalid database port: {port}")
            return False
        
        return True
    
    def validate_telegram_config(self, config: Dict[str, Any]) -> bool:
        """
        Проверяет конфигурацию Telegram.
        
        Args:
            config: Конфигурация Telegram
            
        Returns:
            True если конфигурация валидна, False иначе
        """
        if not config.get("token"):
            self.errors.append("Telegram token is required")
            return False
        
        # Проверяем формат токена
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
        Проверяет конфигурацию OpenAI.
        
        Args:
            config: Конфигурация OpenAI
            
        Returns:
            True если конфигурация валидна, False иначе
        """
        if not config.get("api_key"):
            self.errors.append("OpenAI API key is required")
            return False
        
        # Проверяем формат API ключа
        api_key = config["api_key"]
        if not api_key.startswith("sk-"):
            self.errors.append("Invalid OpenAI API key format")
            return False
        
        # Проверяем лимит сообщений
        limit = config.get("FREE_MESSAGE_LIMIT", 50)
        if not isinstance(limit, int) or limit < 1:
            self.errors.append(f"Invalid FREE_MESSAGE_LIMIT: {limit}")
            return False
        
        return True
    
    def validate_all(self, db_config: Dict[str, Any], telegram_config: Dict[str, Any], 
                   openai_config: Dict[str, Any]) -> bool:
        """
        Проверяет всю конфигурацию.
        
        Args:
            db_config: Конфигурация БД
            telegram_config: Конфигурация Telegram
            openai_config: Конфигурация OpenAI
            
        Returns:
            True если вся конфигурация валидна, False иначе
        """
        self.errors.clear()
        self.warnings.clear()
        
        db_valid = self.validate_database_config(db_config)
        telegram_valid = self.validate_telegram_config(telegram_config)
        openai_valid = self.validate_openai_config(openai_config)
        
        return db_valid and telegram_valid and openai_valid
    
    def print_errors(self) -> None:
        """Выводит ошибки конфигурации."""
        if self.errors:
            print("❌ Configuration errors:")
            for error in self.errors:
                print(f"  - {error}")
    
    def print_warnings(self) -> None:
        """Выводит предупреждения конфигурации."""
        if self.warnings:
            print("⚠️ Configuration warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
    
    def exit_on_errors(self) -> None:
        """Завершает программу при наличии ошибок."""
        if self.errors:
            self.print_errors()
            print("\n💥 Application cannot start due to configuration errors!")
            sys.exit(1)


def validate_configuration(db_config: Dict[str, Any], telegram_config: Dict[str, Any], 
                          openai_config: Dict[str, Any]) -> bool:
    """
    Валидирует конфигурацию приложения.
    
    Args:
        db_config: Конфигурация БД
        telegram_config: Конфигурация Telegram
        openai_config: Конфигурация OpenAI
        
    Returns:
        True если конфигурация валидна, False иначе
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
