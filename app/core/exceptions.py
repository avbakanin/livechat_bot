"""
Custom exceptions for the bot application.
"""
from typing import Optional


class BotException(Exception):
    """Base exception for bot-related errors."""


class DatabaseException(BotException):
    """Database-related exceptions."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


class UserException(BotException):
    """User-related exceptions."""


class SubscriptionException(BotException):
    """Subscription-related exceptions."""


class PaymentException(BotException):
    """Payment-related exceptions."""


class MessageException(BotException):
    """Message-related exceptions."""


class OpenAIException(BotException):
    """OpenAI API-related exceptions."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


class ValidationException(BotException):
    """Data validation exceptions."""


class ConfigurationException(BotException):
    """Configuration-related exceptions."""
