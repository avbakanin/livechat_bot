import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class UserService:
    """Service for user management."""
    
    def __init__(self):
        """Initialize user service."""
        self.cache = {}  # Simple cache for user data
        self.cache_ttl = 300  # 5 minutes TTL
    
    async def add_user(self, pool, user_id: int, username: str, first_name: str, last_name: str = None) -> None:
        """
        Add or update user.
        
        Args:
            pool: Database connection pool
            user_id: User ID
            username: Username
            first_name: First name
            last_name: Last name (optional)
        """
        async with pool.acquire() as conn:
            try:
                await conn.execute(
                    """
                    INSERT INTO users (id, username, first_name, last_name, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (id) DO UPDATE SET
                        username = EXCLUDED.username,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        updated_at = EXCLUDED.updated_at
                """,
                    user_id,
                    username,
                    first_name,
                    last_name,
                    datetime.utcnow(),
                    datetime.utcnow()
                )
                logging.info(f"Added or updated user {user_id}")
                
                # Update cache
                self.cache[user_id] = {
                    'data': {
                        'id': user_id,
                        'username': username,
                        'first_name': first_name,
                        'last_name': last_name
                    },
                    'timestamp': datetime.utcnow()
                }
            except Exception as e:
                logging.error(f"Error in add_user for user {user_id}: {e}")
                raise
    
    async def get_user(self, pool, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            pool: Database connection pool
            user_id: User ID
            
        Returns:
            User data or None if not found
        """
        # Check cache first
        if user_id in self.cache:
            cache_data = self.cache[user_id]
            if datetime.utcnow() - cache_data['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cache_data['data']
        
        async with pool.acquire() as conn:
            try:
                user = await conn.fetchrow(
                    "SELECT * FROM users WHERE id = $1", user_id
                )
                
                if user:
                    user_data = dict(user)
                    # Update cache
                    self.cache[user_id] = {
                        'data': user_data,
                        'timestamp': datetime.utcnow()
                    }
                    return user_data
                else:
                    return None
            except Exception as e:
                logging.error(f"Error getting user {user_id}: {e}")
                return None
    
    async def update_user(self, pool, user_id: int, **kwargs) -> bool:
        """
        Update user data.
        
        Args:
            pool: Database connection pool
            user_id: User ID
            **kwargs: Fields to update
            
        Returns:
            True if updated, False otherwise
        """
        if not kwargs:
            return False
        
        # Build update query
        set_clauses = []
        values = []
        param_count = 1
        
        for field, value in kwargs.items():
            set_clauses.append(f"{field} = ${param_count}")
            values.append(value)
            param_count += 1
        
        set_clauses.append(f"updated_at = ${param_count}")
        values.append(datetime.utcnow())
        param_count += 1
        
        values.append(user_id)  # WHERE clause parameter
        
        query = f"""
            UPDATE users 
            SET {', '.join(set_clauses)}
            WHERE id = ${param_count}
        """
        
        async with pool.acquire() as conn:
            try:
                result = await conn.execute(query, *values)
                
                if result:
                    # Clear cache
                    self.cache.pop(user_id, None)
                    logging.info(f"Updated user {user_id}")
                    return True
                else:
                    return False
            except Exception as e:
                logging.error(f"Error updating user {user_id}: {e}")
                return False
    
    async def delete_user(self, pool, user_id: int) -> bool:
        """
        Delete user.
        
        Args:
            pool: Database connection pool
            user_id: User ID
            
        Returns:
            True if deleted, False otherwise
        """
        async with pool.acquire() as conn:
            try:
                result = await conn.execute(
                    "DELETE FROM users WHERE id = $1", user_id
                )
                
                if result:
                    # Clear cache
                    self.cache.pop(user_id, None)
                    logging.info(f"Deleted user {user_id}")
                    return True
                else:
                    return False
            except Exception as e:
                logging.error(f"Error deleting user {user_id}: {e}")
                return False
    
    async def get_users_count(self, pool) -> int:
        """
        Get total users count.
        
        Args:
            pool: Database connection pool
            
        Returns:
            Total users count
        """
        async with pool.acquire() as conn:
            try:
                count = await conn.fetchval("SELECT COUNT(*) FROM users")
                return count or 0
            except Exception as e:
                logging.error(f"Error getting users count: {e}")
                return 0
    
    async def get_active_users_today(self, pool) -> int:
        """
        Get active users count for today.
        
        Args:
            pool: Database connection pool
            
        Returns:
            Active users count for today
        """
        async with pool.acquire() as conn:
            try:
                count = await conn.fetchval(
                    "SELECT COUNT(DISTINCT user_id) FROM messages WHERE DATE(created_at) = CURRENT_DATE"
                )
                return count or 0
            except Exception as e:
                logging.error(f"Error getting active users count: {e}")
                return 0
    
    async def get_premium_users_count(self, pool) -> int:
        """
        Get premium users count.
        
        Args:
            pool: Database connection pool
            
        Returns:
            Premium users count
        """
        async with pool.acquire() as conn:
            try:
                count = await conn.fetchval(
                    "SELECT COUNT(*) FROM users WHERE subscription_status = 'premium'"
                )
                return count or 0
            except Exception as e:
                logging.error(f"Error getting premium users count: {e}")
                return 0
    
    async def get_user_language(self, pool, user_id: int) -> str:
        """
        Get user language preference.
        
        Args:
            pool: Database connection pool
            user_id: User ID
            
        Returns:
            User language code or None if not set (use Telegram language)
        """
        async with pool.acquire() as conn:
            try:
                language = await conn.fetchval(
                    "SELECT language FROM users WHERE id = $1", user_id
                )
                return language  # Return None if not set, meaning use Telegram language
            except Exception as e:
                logging.error(f"Error getting language for user {user_id}: {e}")
                return None  # Return None to use Telegram language as fallback
    
    def clear_cache(self, user_id: int = None) -> None:
        """
        Clear cache.
        
        Args:
            user_id: Specific user ID to clear, or None to clear all
        """
        if user_id:
            self.cache.pop(user_id, None)
        else:
            self.cache.clear()
        logging.info(f"Cleared cache for user {user_id if user_id else 'all'}")


# Глобальный экземпляр сервиса пользователей
user_service = UserService()


# Обратная совместимость - старые функции
async def add_user(pool, user_id, username, first_name, last_name):
    """Legacy function for backward compatibility."""
    await user_service.add_user(pool, user_id, username, first_name, last_name)
