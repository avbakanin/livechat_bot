"""
Base model classes and common data structures.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class BaseModel:
    """Base model class with common fields."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class UserData:
    """User data structure."""
    id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    gender_preference: str = 'female'
    subscription_status: str = 'free'
    consent_given: bool = False
    subscription_expires_at: Optional[datetime] = None


@dataclass
class MessageData:
    """Message data structure."""
    id: Optional[int]
    user_id: int
    role: str
    text: str
    created_at: Optional[datetime] = None


@dataclass
class PaymentData:
    """Payment data structure."""
    id: Optional[int]
    user_id: int
    amount: float
    payment_status: str
    payment_id: Optional[str]
    created_at: Optional[datetime] = None


@dataclass
class SubscriptionData:
    """Subscription data structure."""
    user_id: int
    status: str
    expires_at: Optional[datetime] = None
