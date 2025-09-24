"""
User domain models.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User model."""

    id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    gender_preference: str = "female"
    language: str = "en"
    subscription_status: str = "free"
    consent_given: bool = False
    subscription_expires_at: Optional[datetime] = None
    personality_profile: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class UserCreate:
    """User creation data."""

    id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]


@dataclass
class UserUpdate:
    """User update data."""

    gender_preference: Optional[str] = None
    language: Optional[str] = None
    subscription_status: Optional[str] = None
    consent_given: Optional[bool] = None
    subscription_expires_at: Optional[datetime] = None
    personality_profile: Optional[dict] = None
