"""
User data cache for FSM - stores frequently accessed user data in memory.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional

from shared.models.user import User


@dataclass
class UserCacheData:
    """Cached user data structure."""

    # Basic user info
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    # Frequently accessed data
    consent_given: bool = False
    gender_preference: str = "female"
    subscription_status: str = "free"
    subscription_expires_at: Optional[datetime] = None

    # Daily message counter cache
    daily_message_count: int = 0
    last_message_date: str = ""

    # Cache metadata
    cached_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)

    def is_expired(self, ttl_minutes: int = 30) -> bool:
        """Check if cache data is expired."""
        return datetime.utcnow() - self.cached_at > timedelta(minutes=ttl_minutes)

    def update_access_time(self) -> None:
        """Update last accessed time."""
        self.last_accessed = datetime.utcnow()

    @classmethod
    def from_user(cls, user: User) -> "UserCacheData":
        """Create cache data from User model."""
        return cls(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            consent_given=user.consent_given,
            gender_preference=user.gender_preference,
            subscription_status=user.subscription_status,
            subscription_expires_at=user.subscription_expires_at,
        )


class UserCache:
    """In-memory cache for user data with TTL and cleanup."""

    def __init__(self, ttl_minutes: int = 30, max_size: int = 10000):
        self.ttl_minutes = ttl_minutes
        self.max_size = max_size
        self._cache: Dict[int, UserCacheData] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start_cleanup_task(self) -> None:
        """Start background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_cleanup_task(self) -> None:
        """Stop background cleanup task."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in cache cleanup: {e}")

    async def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        async with self._lock:
            expired_keys = [user_id for user_id, data in self._cache.items() if data.is_expired(self.ttl_minutes)]

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                logging.info(f"Cleaned up {len(expired_keys)} expired cache entries")

    async def get(self, user_id: int) -> Optional[UserCacheData]:
        """Get user data from cache."""
        async with self._lock:
            data = self._cache.get(user_id)
            if data and not data.is_expired(self.ttl_minutes):
                data.update_access_time()
                return data
            elif data:
                # Remove expired data
                del self._cache[user_id]
            return None

    async def set(self, user_id: int, data: UserCacheData) -> None:
        """Set user data in cache."""
        async with self._lock:
            # Check cache size limit
            if len(self._cache) >= self.max_size:
                # Remove least recently accessed entry
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)
                del self._cache[oldest_key]

            self._cache[user_id] = data

    async def update_field(self, user_id: int, field_name: str, value) -> None:
        """Update specific field in cached data."""
        async with self._lock:
            data = self._cache.get(user_id)
            if data and not data.is_expired(self.ttl_minutes):
                setattr(data, field_name, value)
                data.cached_at = datetime.utcnow()  # Reset TTL

    async def invalidate(self, user_id: int) -> None:
        """Remove user data from cache."""
        async with self._lock:
            self._cache.pop(user_id, None)

    async def clear(self) -> None:
        """Clear all cached data."""
        async with self._lock:
            self._cache.clear()

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "total_entries": len(self._cache),
            "max_size": self.max_size,
            "ttl_minutes": self.ttl_minutes,
        }


# Global cache instance
user_cache = UserCache()
