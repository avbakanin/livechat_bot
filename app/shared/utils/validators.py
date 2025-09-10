"""
Data validation utilities.
"""
from typing import Any, Optional
from core.exceptions import ValidationException


def validate_user_id(user_id: Any) -> int:
    """Validate and convert user ID."""
    if not isinstance(user_id, (int, str)):
        raise ValidationException("User ID must be integer or string")
    
    try:
        user_id = int(user_id)
        if user_id <= 0:
            raise ValidationException("User ID must be positive")
        return user_id
    except (ValueError, TypeError):
        raise ValidationException("Invalid user ID format")


def validate_message_text(text: Any) -> str:
    """Validate message text."""
    if not isinstance(text, str):
        raise ValidationException("Message text must be string")
    
    if not text.strip():
        raise ValidationException("Message text cannot be empty")
    
    if len(text) > 4000:  # Telegram message limit
        raise ValidationException("Message text too long")
    
    return text.strip()


def validate_gender_preference(gender: Any) -> str:
    """Validate gender preference."""
    if not isinstance(gender, str):
        raise ValidationException("Gender preference must be string")
    
    if gender not in ['male', 'female']:
        raise ValidationException("Invalid gender preference")
    
    return gender


def validate_amount(amount: Any) -> float:
    """Validate payment amount."""
    if not isinstance(amount, (int, float, str)):
        raise ValidationException("Amount must be number or string")
    
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValidationException("Amount must be positive")
        if amount > 1000000:  # Reasonable upper limit
            raise ValidationException("Amount too large")
        return amount
    except (ValueError, TypeError):
        raise ValidationException("Invalid amount format")
