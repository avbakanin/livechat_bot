"""
Payment domain services - placeholder for future implementation.
"""
import asyncpg
from core.exceptions import PaymentException


class PaymentService:
    """Payment business logic service."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def create_payment(self, user_id: int, amount: float) -> str:
        """Create payment - placeholder implementation."""
        # Placeholder implementation
        raise PaymentException("Payment system not implemented yet")
