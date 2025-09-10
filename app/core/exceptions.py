"""
Custom exceptions for the bot application.
"""
from typing import Optional


class BotException(Exception):
    """Base exception for bot-related errors."""
    pass


class DatabaseException(BotException):
    """Database-related exceptions."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


class UserException(BotException):
    """User-related exceptions."""
    pass


class SubscriptionException(BotException):
    """Subscription-related exceptions."""
    pass


class PaymentException(BotException):
    """Payment-related exceptions."""
    pass


class MessageException(BotException):
    """Message-related exceptions."""
    pass


class OpenAIException(BotException):
    """OpenAI API-related exceptions."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


class ValidationException(BotException):
    """Data validation exceptions."""
    pass


class ConfigurationException(BotException):
    """Configuration-related exceptions."""
    pass
