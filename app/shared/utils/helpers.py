"""
Common utility functions and helpers.
"""
from typing import Tuple, Optional
from aiogram.types import User


def destructure_user(user: User) -> Tuple[int, Optional[str], Optional[str], Optional[str]]:
    """Extract user information from Telegram User object."""
    return (
        user.id,
        user.username,
        user.first_name,
        user.last_name
    )


def format_user_name(user: User) -> str:
    """Format user name for display."""
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    elif user.first_name:
        return user.first_name
    elif user.username:
        return f"@{user.username}"
    else:
        return f"User {user.id}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def is_valid_gender(gender: str) -> bool:
    """Check if gender preference is valid."""
    return gender in ['male', 'female']


def is_valid_role(role: str) -> bool:
    """Check if message role is valid."""
    return role in ['user', 'assistant', 'system']
