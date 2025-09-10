"""
Subscription domain models.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Subscription:
    """Subscription model."""
    user_id: int
    status: str
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SubscriptionCreate:
    """Subscription creation data."""
    user_id: int
    status: str
    expires_at: Optional[datetime] = None


@dataclass
class SubscriptionUpdate:
    """Subscription update data."""
    status: Optional[str] = None
    expires_at: Optional[datetime] = None
