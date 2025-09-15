"""
Daily message counter service - efficient counting of user messages per day.
"""

import logging
from datetime import date, datetime
from typing import Optional

import asyncpg
from core.exceptions import DatabaseException


class DailyCounterService:
    """Service for managing daily message counters efficiently."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def increment_user_count(self, user_id: int, target_date: Optional[date] = None) -> int:
        """
        Increment user's daily message count and return new count.
        
        Args:
            user_id: User ID
            target_date: Date to increment (defaults to today)
            
        Returns:
            New message count for the day
        """
        if target_date is None:
            target_date = date.today()
            
        async with self.pool.acquire() as conn:
            try:
                count = await conn.fetchval(
                    "SELECT public.increment_user_daily_count($1, $2)",
                    user_id, target_date
                )
                return count or 0
            except Exception as e:
                logging.error(f"Error incrementing counter for user {user_id}: {e}")
                raise DatabaseException(f"Error incrementing counter: {e}", e)
    
    async def get_user_count(self, user_id: int, target_date: Optional[date] = None) -> int:
        """
        Get user's daily message count.
        
        Args:
            user_id: User ID
            target_date: Date to check (defaults to today)
            
        Returns:
            Message count for the day
        """
        if target_date is None:
            target_date = date.today()
            
        async with self.pool.acquire() as conn:
            try:
                count = await conn.fetchval(
                    "SELECT public.get_user_daily_count($1, $2)",
                    user_id, target_date
                )
                return count or 0
            except Exception as e:
                logging.error(f"Error getting counter for user {user_id}: {e}")
                raise DatabaseException(f"Error getting counter: {e}", e)
    
    async def can_send_message(self, user_id: int, daily_limit: int, target_date: Optional[date] = None) -> bool:
        """
        Check if user can send a message (hasn't exceeded daily limit).
        
        Args:
            user_id: User ID
            daily_limit: Maximum messages per day
            target_date: Date to check (defaults to today)
            
        Returns:
            True if user can send message, False otherwise
        """
        current_count = await self.get_user_count(user_id, target_date)
        return current_count < daily_limit
    
    async def get_remaining_messages(self, user_id: int, daily_limit: int, target_date: Optional[date] = None) -> int:
        """
        Get remaining messages for the day.
        
        Args:
            user_id: User ID
            daily_limit: Maximum messages per day
            target_date: Date to check (defaults to today)
            
        Returns:
            Number of remaining messages
        """
        current_count = await self.get_user_count(user_id, target_date)
        remaining = daily_limit - current_count
        return max(0, remaining)
    
    async def reset_counters_for_date(self, target_date: date) -> int:
        """
        Reset all counters for a specific date.
        
        Args:
            target_date: Date to reset counters for
            
        Returns:
            Number of deleted counter records
        """
        async with self.pool.acquire() as conn:
            try:
                deleted_count = await conn.fetchval(
                    "SELECT public.reset_daily_counters_for_date($1)",
                    target_date
                )
                logging.info(f"Reset {deleted_count} counters for date {target_date}")
                return deleted_count or 0
            except Exception as e:
                logging.error(f"Error resetting counters for date {target_date}: {e}")
                raise DatabaseException(f"Error resetting counters: {e}", e)
    
    async def cleanup_old_counters(self) -> int:
        """
        Cleanup counters older than 30 days.
        
        Returns:
            Number of deleted counter records
        """
        async with self.pool.acquire() as conn:
            try:
                deleted_count = await conn.fetchval(
                    "SELECT public.cleanup_old_counters()"
                )
                logging.info(f"Cleaned up {deleted_count} old counter records")
                return deleted_count or 0
            except Exception as e:
                logging.error(f"Error cleaning up old counters: {e}")
                raise DatabaseException(f"Error cleaning up counters: {e}", e)
    
    async def get_user_stats(self, user_id: int, days: int = 7) -> list:
        """
        Get user's message statistics for the last N days.
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            List of dicts with date and count
        """
        async with self.pool.acquire() as conn:
            try:
                rows = await conn.fetch(
                    """
                    SELECT date, message_count
                    FROM public.user_daily_counters
                    WHERE user_id = $1 
                    AND date >= CURRENT_DATE - INTERVAL '%s days'
                    ORDER BY date DESC
                    """,
                    user_id, days
                )
                return [{"date": row["date"], "count": row["message_count"]} for row in rows]
            except Exception as e:
                logging.error(f"Error getting stats for user {user_id}: {e}")
                raise DatabaseException(f"Error getting user stats: {e}", e)
