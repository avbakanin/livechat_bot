"""
Subscription domain services - business logic for subscription management.
"""

import logging
from datetime import datetime
from typing import Optional

import asyncpg
from shared.utils.datetime_utils import DateTimeUtils


class SubscriptionService:
    """Subscription business logic service."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def check_subscription_status(self, user_id: int) -> str:
        """Check user subscription status."""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT subscription_status FROM users WHERE id = $1",
                    user_id
                )
                if row:
                    return row['subscription_status'] or "free"
                return "free"
        except Exception as e:
            logging.error(f"Error checking subscription status for user {user_id}: {e}")
            return "free"

    async def is_premium_user(self, user_id: int) -> bool:
        """Check if user has active premium subscription."""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT subscription_status, subscription_expires_at 
                    FROM users 
                    WHERE id = $1
                    """,
                    user_id
                )
                if not row:
                    return False
                
                if row['subscription_status'] != 'premium':
                    return False
                
                expires_at = row['subscription_expires_at']
                if not expires_at:
                    return False
                
                return not DateTimeUtils.is_expired(expires_at)
                
        except Exception as e:
            logging.error(f"Error checking premium status for user {user_id}: {e}")
            return False

    async def get_subscription_expires_at(self, user_id: int) -> Optional[datetime]:
        """Get subscription expiration date."""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT subscription_expires_at FROM users WHERE id = $1",
                    user_id
                )
                if row:
                    return row['subscription_expires_at']
                return None
        except Exception as e:
            logging.error(f"Error getting subscription expiration for user {user_id}: {e}")
            return None

    async def update_subscription_status(self, user_id: int, status: str, expires_at: Optional[datetime] = None) -> bool:
        """Update user subscription status."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE users 
                    SET subscription_status = $1, subscription_expires_at = $2, updated_at = $3
                    WHERE id = $4
                    """,
                    status, expires_at, DateTimeUtils.utc_now_naive(), user_id
                )
                return True
        except Exception as e:
            logging.error(f"Error updating subscription status for user {user_id}: {e}")
            return False

    async def get_subscription_info(self, user_id: int) -> dict:
        """Get comprehensive subscription information."""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT subscription_status, subscription_expires_at, created_at
                    FROM users 
                    WHERE id = $1
                    """,
                    user_id
                )
                if not row:
                    return {
                        "status": "free",
                        "expires_at": None,
                        "is_active": False,
                        "days_remaining": 0,
                        "hours_remaining": 0
                    }
                
                status = row['subscription_status'] or "free"
                expires_at = row['subscription_expires_at']
                
                is_active = False
                days_remaining = 0
                hours_remaining = 0
                
                if status == "premium" and expires_at:
                    is_active = not DateTimeUtils.is_expired(expires_at)
                    if is_active:
                        days_remaining = DateTimeUtils.days_remaining(expires_at)
                        hours_remaining = DateTimeUtils.hours_remaining(expires_at)
                
                return {
                    "status": status,
                    "expires_at": expires_at,
                    "is_active": is_active,
                    "days_remaining": days_remaining,
                    "hours_remaining": hours_remaining
                }
                
        except Exception as e:
            logging.error(f"Error getting subscription info for user {user_id}: {e}")
            return {
                "status": "free",
                "expires_at": None,
                "is_active": False,
                "days_remaining": 0,
                "hours_remaining": 0
            }
