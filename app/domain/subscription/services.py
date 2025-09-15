"""
Subscription domain services - placeholder for future implementation.
"""
import asyncpg


class SubscriptionService:
    """Subscription business logic service."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def check_subscription_status(self, user_id: int) -> str:
        """Check user subscription status."""
        # Placeholder implementation
        return "free"

    async def is_premium_user(self, user_id: int) -> bool:
        """Check if user has premium subscription."""
        # Placeholder implementation
        return False
