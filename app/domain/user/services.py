"""
User domain services - business logic layer.
"""

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
from shared.models.user import User, UserCreate, UserUpdate

from core.exceptions import UserException


class UserService:
    """User business logic service."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def add_user(
        self,
        user_id: int,
        username: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str],
    ) -> None:
        """Add or update user information."""
        user_data = UserCreate(
            id=user_id, username=username, first_name=first_name, last_name=last_name
        )
        await db_create_user(self.pool, user_data)

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await db_get_user(self.pool, user_id)

    async def delete_user_messages(self, user_id: int) -> None:
        """Delete all user messages."""
        await db_delete_user_messages(self.pool, user_id)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> None:
        """Update user data."""
        await db_update_user(self.pool, user_id, user_data)

    async def get_consent_status(self, user_id: int) -> bool:
        """Get user consent status."""
        return await db_get_user_consent(self.pool, user_id)

    async def set_consent_status(self, user_id: int, consent: bool) -> None:
        """Set user consent status."""
        await db_set_user_consent(self.pool, user_id, consent)

    async def get_gender_preference(self, user_id: int) -> str:
        """Get user gender preference."""
        return await db_get_gender_preference(self.pool, user_id)

    async def set_gender_preference(self, user_id: int, preference: str) -> None:
        """Set user gender preference."""
        if preference not in ["male", "female"]:
            raise UserException(f"Invalid gender preference: {preference}")

        await db_set_gender_preference(self.pool, user_id, preference)

    async def can_send_message(self, user_id: int) -> bool:
        """Check if user can send messages (not exceeded daily limit)."""
        # This would need to be implemented with message counting
        # For now, return True - this should be moved to message service
        return True

    async def get_subscription_status(self, user_id: int) -> str:
        """Get user subscription status."""
        from domain.user.queries import get_user_subscription_status

        return await get_user_subscription_status(self.pool, user_id)

    async def get_subscription_expires_at(self, user_id: int):
        """Get user subscription expiration date."""
        from domain.user.queries import get_user_subscription_expires_at

        return await get_user_subscription_expires_at(self.pool, user_id)

    async def reset_user_state(self, user_id: int) -> None:
        """Reset user state completely - clear consent, gender preference, and messages."""
        # Delete all user messages
        await self.delete_user_messages(user_id)
        
        # Reset consent status to False
        await self.set_consent_status(user_id, False)
        
        # Reset gender preference to default
        await self.set_gender_preference(user_id, "female")