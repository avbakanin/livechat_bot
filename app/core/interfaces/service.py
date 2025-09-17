"""
Service interfaces for business logic abstraction.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional



class IService(ABC):
    """Base service interface."""
    
    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute service operation."""


class IUserService(IService):
    """User service interface."""
    
    @abstractmethod
    async def create_user(
        self, 
        telegram_id: int, 
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Any:
        """Create new user."""
    
    @abstractmethod
    async def get_user(self, telegram_id: int) -> Optional[Any]:
        """Get user by Telegram ID."""
    
    @abstractmethod
    async def update_user_preferences(
        self, 
        telegram_id: int, 
        preferences: Dict[str, Any]
    ) -> Any:
        """Update user preferences."""
    
    @abstractmethod
    async def delete_user(self, telegram_id: int) -> bool:
        """Delete user and all related data."""


class IMessageService(IService):
    """Message service interface."""
    
    @abstractmethod
    async def send_message(
        self, 
        user_id: int, 
        text: str
    ) -> str:
        """Send message and get AI response."""
    
    @abstractmethod
    async def get_chat_history(
        self, 
        user_id: int, 
        limit: int = 10
    ) -> List[Any]:
        """Get user chat history."""
    
    @abstractmethod
    async def clear_chat_history(self, user_id: int) -> bool:
        """Clear user chat history."""
    
    @abstractmethod
    async def can_send_message(self, user_id: int) -> bool:
        """Check if user can send message."""


class ISubscriptionService(IService):
    """Subscription service interface."""
    
    @abstractmethod
    async def create_subscription(
        self, 
        user_id: int, 
        plan_type: str,
        duration_days: int
    ) -> Any:
        """Create new subscription."""
    
    @abstractmethod
    async def get_user_subscription(self, user_id: int) -> Optional[Any]:
        """Get user subscription."""
    
    @abstractmethod
    async def is_premium_user(self, user_id: int) -> bool:
        """Check if user has premium subscription."""
    
    @abstractmethod
    async def renew_subscription(
        self, 
        user_id: int, 
        duration_days: int
    ) -> Any:
        """Renew user subscription."""


class IPaymentService(IService):
    """Payment service interface."""
    
    @abstractmethod
    async def create_payment(
        self, 
        user_id: int, 
        amount: float,
        description: str
    ) -> Any:
        """Create payment."""
    
    @abstractmethod
    async def process_payment(self, payment_id: str) -> bool:
        """Process payment."""
    
    @abstractmethod
    async def get_payment_status(self, payment_id: str) -> str:
        """Get payment status."""
    
    @abstractmethod
    async def refund_payment(self, payment_id: str) -> bool:
        """Refund payment."""


class INotificationService(IService):
    """Notification service interface."""
    
    @abstractmethod
    async def send_notification(
        self, 
        user_id: int, 
        message: str,
        notification_type: str = "info"
    ) -> bool:
        """Send notification to user."""
    
    @abstractmethod
    async def send_bulk_notification(
        self, 
        user_ids: List[int], 
        message: str
    ) -> int:
        """Send notification to multiple users."""
