"""
Payment domain services - business logic layer.
"""
import logging
from datetime import datetime
from typing import Optional

import asyncpg

from core.exceptions import PaymentException


class PaymentService:
    """Payment business logic service."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self.payment_methods = {
            'yookassa': self._create_yookassa_payment,
            'stripe': self._create_stripe_payment,
            'paypal': self._create_paypal_payment
        }

    async def create_payment(self, user_id: int, amount: float, method: str = 'yookassa') -> Optional[str]:
        """
        Create a payment.
        
        Args:
            user_id: User ID
            amount: Payment amount
            method: Payment method
            
        Returns:
            Payment URL or None if failed
        """
        try:
            if method in self.payment_methods:
                return await self.payment_methods[method](user_id, amount)
            else:
                logging.error(f"Unknown payment method: {method}")
                return None
        except Exception as e:
            logging.error(f"Error creating payment for user {user_id}: {e}")
            return None

    async def _create_yookassa_payment(self, user_id: int, amount: float) -> Optional[str]:
        """Create YooKassa payment."""
        try:
            # Configuration.configure(APP_CONFIG['YOOKASSA_SHOP_ID'], APP_CONFIG['YOOKASSA_SECRET_KEY'])
            # payment = Payment.create({
            #     "amount": {"value": str(amount), "currency": "RUB"},
            #     "confirmation": {"type": "redirect", "return_url": "https://your-site.com/return"},
            #     "capture": True,
            #     "description": f"Премиум-подписка для {user_id}"
            # })
            # await self.add_payment(user_id, amount, payment.status, payment.id)
            # logging.info(f"Created payment {payment.id} for user {user_id}")
            # return payment.confirmation.confirmation_url

            # Временная заглушка
            logging.info(f"YooKassa payment creation requested for user {user_id}, amount: {amount}")
            return None
        except Exception as e:
            logging.error(f"Error creating YooKassa payment for user {user_id}: {e}")
            return None

    async def _create_stripe_payment(self, user_id: int, amount: float) -> Optional[str]:
        """Create Stripe payment."""
        try:
            # Stripe implementation would go here
            logging.info(f"Stripe payment creation requested for user {user_id}, amount: {amount}")
            return None
        except Exception as e:
            logging.error(f"Error creating Stripe payment for user {user_id}: {e}")
            return None

    async def _create_paypal_payment(self, user_id: int, amount: float) -> Optional[str]:
        """Create PayPal payment."""
        try:
            # PayPal implementation would go here
            logging.info(f"PayPal payment creation requested for user {user_id}, amount: {amount}")
            return None
        except Exception as e:
            logging.error(f"Error creating PayPal payment for user {user_id}: {e}")
            return None

    async def add_payment(self, user_id: int, amount: float, payment_status: str, payment_id: str) -> None:
        """
        Add payment to database.
        
        Args:
            user_id: User ID
            amount: Payment amount
            payment_status: Payment status
            payment_id: Payment ID
        """
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(
                    """
                    INSERT INTO payments (user_id, amount, payment_status, payment_id, created_at)
                    VALUES ($1, $2, $3, $4, $5)
                """,
                    user_id,
                    amount,
                    payment_status,
                    payment_id,
                    datetime.utcnow()
                )
                logging.info(f"Added payment {payment_id} for user {user_id}, status: {payment_status}")
            except Exception as e:
                logging.error(f"Error in add_payment for user {user_id}: {e}")
                raise PaymentException(f"Error adding payment: {e}")

    async def get_payment_status(self, payment_id: str) -> Optional[str]:
        """
        Get payment status.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Payment status or None if not found
        """
        async with self.pool.acquire() as conn:
            try:
                status = await conn.fetchval(
                    "SELECT payment_status FROM payments WHERE payment_id=$1", payment_id
                )
                logging.info(f"Retrieved payment_status for payment {payment_id}: {status}")
                return status
            except Exception as e:
                logging.error(f"Error in get_payment_status for payment {payment_id}: {e}")
                raise PaymentException(f"Error getting payment status: {e}")

    async def get_user_payments(self, user_id: int) -> list:
        """
        Get user payments.
        
        Args:
            user_id: User ID
            
        Returns:
            List of user payments
        """
        async with self.pool.acquire() as conn:
            try:
                payments = await conn.fetch(
                    "SELECT * FROM payments WHERE user_id=$1 ORDER BY created_at DESC", user_id
                )
                return [dict(payment) for payment in payments]
            except Exception as e:
                logging.error(f"Error getting payments for user {user_id}: {e}")
                return []

    def get_supported_methods(self) -> list:
        """
        Get supported payment methods.
        
        Returns:
            List of supported payment methods
        """
        return list(self.payment_methods.keys())