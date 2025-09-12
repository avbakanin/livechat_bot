"""
Payment domain models.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Payment:
    """Payment model."""

    id: Optional[int]
    user_id: int
    amount: float
    payment_status: str
    payment_id: Optional[str]
    created_at: Optional[datetime] = None


@dataclass
class PaymentCreate:
    """Payment creation data."""

    user_id: int
    amount: float
    payment_status: str
    payment_id: Optional[str] = None


@dataclass
class PaymentUpdate:
    """Payment update data."""

    payment_status: Optional[str] = None
    payment_id: Optional[str] = None
