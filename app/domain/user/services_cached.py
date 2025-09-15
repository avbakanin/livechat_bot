"""
Enhanced User Service with FSM caching support.
"""

from datetime import datetime
from typing import Optional

import asyncpg
from domain.user.queries import create_user as db_create_user
from domain.user.queries import delete_user_messages as db_delete_user_messages
from domain.user.queries import get_gender_preference as db_get_gender_preference
from domain.user.queries import get_user as db_get_user
from domain.user.queries import get_user_consent as db_get_user_consent
from domain.user.queries import set_gender_preference as db_set_gender_preference
from domain.user.queries import set_user_consent as db_set_user_consent
from domain.user.queries import update_user as db_update_user
from shared.fsm.user_cache import UserCacheData, user_cache
from shared.models.user import User, UserCreate, UserUpdate

from core.exceptions import UserException


class UserService:
    """Enhanced User business logic service with FSM caching."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def add_user(
        self, user_id: int, username: Optional[str], first_name: Optional[str], last_name: Optional[str]
    ) -> None:
        """Add or update user information."""
        user_data = UserCreate(id=user_id, username=username, first_name=first_name, last_name=last_name)
        await db_create_user(self.pool, user_data)
        
        # Update cache if user exists
        cached_data = await user_cache.get(user_id)
        if cached_data:
            cached_data.username = username
            cached_data.first_name = first_name
            cached_data.last_name = last_name
            await user_cache.set(user_id, cached_data)

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await db_get_user(self.pool, user_id)

    async def get_user_with_cache(self, user_id: int) -> Optional[UserCacheData]:
        """Get user data with caching support."""
        # Try cache first
        cached_data = await user_cache.get(user_id)
        if cached_data:
            return cached_data
        
        # Fetch from database
        user = await db_get_user(self.pool, user_id)
        if user:
            cached_data = UserCacheData.from_user(user)
            await user_cache.set(user_id, cached_data)
            return cached_data
        
        return None

    async def delete_user_messages(self, user_id: int) -> None:
        """Delete all user messages."""
        await db_delete_user_messages(self.pool, user_id)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> None:
        """Update user data."""
        await db_update_user(self.pool, user_id, user_data)
        
        # Update cache
        cached_data = await user_cache.get(user_id)
        if cached_data:
            if user_data.gender_preference is not None:
                cached_data.gender_preference = user_data.gender_preference
            if user_data.subscription_status is not None:
                cached_data.subscription_status = user_data.subscription_status
            if user_data.consent_given is not None:
                cached_data.consent_given = user_data.consent_given
            if user_data.subscription_expires_at is not None:
                cached_data.subscription_expires_at = user_data.subscription_expires_at
            
            await user_cache.set(user_id, cached_data)

    async def get_consent_status(self, user_id: int) -> bool:
        """Get user consent status with caching."""
        cached_data = await user_cache.get(user_id)
        if cached_data:
            return cached_data.consent_given
        
        # Fallback to database
        return await db_get_user_consent(self.pool, user_id)

    async def set_consent_status(self, user_id: int, consent: bool) -> None:
        """Set user consent status."""
        await db_set_user_consent(self.pool, user_id, consent)
        
        # Update cache
        await user_cache.update_field(user_id, "consent_given", consent)

    async def get_gender_preference(self, user_id: int) -> str:
        """Get user gender preference with caching."""
        cached_data = await user_cache.get(user_id)
        if cached_data:
            return cached_data.gender_preference
        
        # Fallback to database
        return await db_get_gender_preference(self.pool, user_id)

    async def set_gender_preference(self, user_id: int, preference: str) -> None:
        """Set user gender preference."""
        if preference not in ["male", "female"]:
            raise UserException(f"Invalid gender preference: {preference}")

        await db_set_gender_preference(self.pool, user_id, preference)
        
        # Update cache
        await user_cache.update_field(user_id, "gender_preference", preference)

    async def get_subscription_status(self, user_id: int) -> str:
        """Get user subscription status with caching."""
        cached_data = await user_cache.get(user_id)
        if cached_data:
            return cached_data.subscription_status
        
        # Fallback to database
        from domain.user.queries import get_user_subscription_status
        return await get_user_subscription_status(self.pool, user_id)

    async def get_subscription_expires_at(self, user_id: int):
        """Get user subscription expiration date with caching."""
        cached_data = await user_cache.get(user_id)
        if cached_data:
            return cached_data.subscription_expires_at
        
        # Fallback to database
        from domain.user.queries import get_user_subscription_expires_at
        return await get_user_subscription_expires_at(self.pool, user_id)

    async def can_send_message(self, user_id: int) -> bool:
        """Check if user can send messages (not exceeded daily limit)."""
        # This would need to be implemented with message counting
        # For now, return True - this should be moved to message service
        return True

    async def invalidate_cache(self, user_id: int) -> None:
        """Invalidate user cache."""
        await user_cache.invalidate(user_id)
