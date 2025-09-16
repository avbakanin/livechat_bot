"""
Domain events for loose coupling and event-driven architecture.
"""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


class DomainEvent(ABC):
    """Base class for domain events."""
    
    def __init__(self):
        self.event_id: UUID = uuid4()
        self.occurred_at: datetime = datetime.utcnow()
        self.event_version: int = 1


@dataclass
class UserCreatedEvent(DomainEvent):
    """Event raised when user is created."""
    user_id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@dataclass
class UserUpdatedEvent(DomainEvent):
    """Event raised when user is updated."""
    user_id: int
    telegram_id: int
    changes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserDeletedEvent(DomainEvent):
    """Event raised when user is deleted."""
    user_id: int
    telegram_id: int


@dataclass
class MessageSentEvent(DomainEvent):
    """Event raised when message is sent."""
    user_id: int
    message_id: int
    role: str
    text: str
    response_time_ms: Optional[float] = None


@dataclass
class MessageLimitExceededEvent(DomainEvent):
    """Event raised when user exceeds message limit."""
    user_id: int
    current_count: int
    limit: int


@dataclass
class SubscriptionCreatedEvent(DomainEvent):
    """Event raised when subscription is created."""
    user_id: int
    subscription_id: int
    plan_type: str
    expires_at: datetime


@dataclass
class SubscriptionExpiredEvent(DomainEvent):
    """Event raised when subscription expires."""
    user_id: int
    subscription_id: int
    plan_type: str


@dataclass
class PaymentCreatedEvent(DomainEvent):
    """Event raised when payment is created."""
    user_id: int
    payment_id: int
    amount: float
    currency: str = "RUB"


@dataclass
class PaymentCompletedEvent(DomainEvent):
    """Event raised when payment is completed."""
    user_id: int
    payment_id: int
    amount: float
    subscription_id: Optional[int] = None


@dataclass
class SecurityAlertEvent(DomainEvent):
    """Event raised when security alert is triggered."""
    user_id: int
    alert_type: str
    severity: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BotMetricsUpdatedEvent(DomainEvent):
    """Event raised when bot metrics are updated."""
    metric_name: str
    metric_value: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
