"""
Centralized user service for user-related operations.
"""

from typing import Optional, Dict, Any
import asyncpg
from shared.models.user import User, UserCreate, UserUpdate
from shared.services.validation_service import validation_service
from shared.services.config_service import config_service
from domain.user.queries import (
    create_user as db_create_user,
    get_user as db_get_user,
    update_user as db_update_user,
    delete_user_messages as db_delete_user_messages
)


class UserService:
    """Centralized user service."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def create_user(self, user_data: UserCreate) -> bool:
        """Create a new user with validation."""
        # Validate user data
        validation_result = validation_service.validate_multiple_fields({
            "user_id": user_data.id,
            "username": user_data.username,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name
        })
        
        if not validation_result["is_valid"]:
            raise ValueError(f"Invalid user data: {validation_result['errors']}")
        
        try:
            await db_create_user(self.pool, user_data)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to create user: {e}")
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID with validation."""
        if not validation_service.validate_user_id(user_id):
            raise ValueError(f"Invalid user ID: {user_id}")
        
        try:
            return await db_get_user(self.pool, user_id)
        except Exception as e:
            raise RuntimeError(f"Failed to get user {user_id}: {e}")
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> bool:
        """Update user data with validation."""
        if not validation_service.validate_user_id(user_id):
            raise ValueError(f"Invalid user ID: {user_id}")
        
        # Validate update data
        validation_fields = {}
        if user_data.gender_preference is not None:
            validation_fields["gender_preference"] = user_data.gender_preference
        if user_data.language is not None:
            validation_fields["language"] = user_data.language
        if user_data.subscription_status is not None:
            validation_fields["subscription_status"] = user_data.subscription_status
        
        if validation_fields:
            validation_result = validation_service.validate_multiple_fields(validation_fields)
            if not validation_result["is_valid"]:
                raise ValueError(f"Invalid update data: {validation_result['errors']}")
        
        try:
            await db_update_user(self.pool, user_id, user_data)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to update user {user_id}: {e}")
    
    async def delete_user_messages(self, user_id: int) -> bool:
        """Delete all user messages with validation."""
        if not validation_service.validate_user_id(user_id):
            raise ValueError(f"Invalid user ID: {user_id}")
        
        try:
            await db_delete_user_messages(self.pool, user_id)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete messages for user {user_id}: {e}")
    
    async def get_user_language(self, user_id: int) -> str:
        """Get user language with fallback."""
        user = await self.get_user(user_id)
        if user and user.language:
            return user.language
        return config_service.get_default_language()
    
    async def get_user_gender_preference(self, user_id: int) -> str:
        """Get user gender preference with fallback."""
        user = await self.get_user(user_id)
        if user and user.gender_preference:
            return user.gender_preference
        return "female"  # Default
    
    async def get_user_consent_status(self, user_id: int) -> bool:
        """Get user consent status."""
        user = await self.get_user(user_id)
        return user.consent_given if user else False
    
    async def get_user_subscription_info(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user subscription information."""
        user = await self.get_user(user_id)
        if not user:
            return {
                "status": "free",
                "is_premium": False,
                "expires_at": None,
                "is_expired": True
            }
        
        from shared.utils.datetime_utils import DateTimeUtils
        
        is_premium = (
            user.subscription_status == "premium" and 
            user.subscription_expires_at and 
            not DateTimeUtils.is_expired(user.subscription_expires_at)
        )
        
        return {
            "status": user.subscription_status or "free",
            "is_premium": is_premium,
            "expires_at": user.subscription_expires_at,
            "is_expired": DateTimeUtils.is_expired(user.subscription_expires_at) if user.subscription_expires_at else True
        }
    
    async def is_user_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to use the bot."""
        return config_service.is_user_allowed(user_id)
    
    async def get_user_personality_profile(self, user_id: int) -> Optional[Dict[str, float]]:
        """Get user personality profile."""
        user = await self.get_user(user_id)
        return user.personality_profile if user else None
    
    async def update_user_personality_profile(self, user_id: int, profile: Dict[str, float]) -> bool:
        """Update user personality profile with validation."""
        validation_result = validation_service.validate_personality_profile(profile)
        if not validation_result["is_valid"]:
            raise ValueError(validation_result["error"])
        
        user_data = UserUpdate(personality_profile=profile)
        return await self.update_user(user_id, user_data)
