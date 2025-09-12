"""
Subscription domain queries - placeholder for future implementation.
"""
import asyncpg

from core.exceptions import DatabaseException


async def get_subscription_status(pool: asyncpg.Pool, user_id: int) -> str:
    """Get user subscription status."""
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                """
                SELECT subscription_status FROM users WHERE id = $1
            """,
                user_id,
            )
            return row["subscription_status"] if row else "free"
        except Exception as e:
            raise DatabaseException(f"Error getting subscription status {user_id}: {e}", e)
