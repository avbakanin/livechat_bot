"""
Centralized message service for message-related operations.
"""

from typing import List, Optional, Dict, Any
import asyncpg
from openai import AsyncOpenAI
from shared.models.message import MessageContext, MessageCreate
from shared.services.validation_service import validation_service
from shared.services.config_service import config_service
from domain.message.queries import (
    create_message as db_create_message,
    get_user_messages as db_get_user_messages,
    delete_user_messages as db_delete_user_messages,
    count_user_messages_today as db_count_user_messages_today
)
from services.counter import DailyCounterService
from services.person import PersonService
from shared.i18n import i18n
from domain.personality.prompts import personality_prompt_generator
from core.exceptions import OpenAIException


class MessageService:
    """Centralized message service."""
    
    def __init__(
        self,
        pool: asyncpg.Pool,
        openai_client: AsyncOpenAI,
        persona_service: Optional[PersonService] = None,
        counter_service: Optional[DailyCounterService] = None,
    ):
        self.pool = pool
        self.openai_client = openai_client
        self.persona_service = persona_service
        self.counter_service = counter_service
    
    async def add_message(self, user_id: int, role: str, text: str) -> bool:
        """Add a message to the database with validation."""
        # Validate inputs
        if not validation_service.validate_user_id(user_id):
            raise ValueError(f"Invalid user ID: {user_id}")
        
        text_validation = validation_service.validate_message_text(text)
        if not text_validation["is_valid"]:
            raise ValueError(text_validation["error"])
        
        if role not in ["user", "assistant"]:
            raise ValueError(f"Invalid role: {role}")
        
        try:
            message_data = MessageCreate(user_id=user_id, role=role, text=text)
            await db_create_message(self.pool, message_data)
            
            # Increment counter for user messages
            if role == "user" and self.counter_service:
                await self.counter_service.increment_user_count(user_id)
            
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to add message: {e}")
    
    async def get_chat_history(self, user_id: int, limit: int = 10) -> List[MessageContext]:
        """Get user's chat history with validation."""
        if not validation_service.validate_user_id(user_id):
            raise ValueError(f"Invalid user ID: {user_id}")
        
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer")
        
        try:
            return await db_get_user_messages(self.pool, user_id, limit)
        except Exception as e:
            raise RuntimeError(f"Failed to get chat history for user {user_id}: {e}")
    
    async def delete_user_messages(self, user_id: int) -> bool:
        """Delete all messages for a user with validation."""
        if not validation_service.validate_user_id(user_id):
            raise ValueError(f"Invalid user ID: {user_id}")
        
        try:
            await db_delete_user_messages(self.pool, user_id)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete messages for user {user_id}: {e}")
    
    async def can_send_message(self, user_id: int) -> bool:
        """Check if user can send messages (not exceeded daily limit)."""
        if not validation_service.validate_user_id(user_id):
            return False
        
        daily_limit = config_service.get_free_message_limit()
        
        # Use efficient counter service if available
        if self.counter_service:
            return await self.counter_service.can_send_message(user_id, daily_limit)
        else:
            # Fallback to database query
            try:
                messages_today = await db_count_user_messages_today(self.pool, user_id)
                return messages_today < daily_limit
            except Exception as e:
                raise RuntimeError(f"Failed to check message limit for user {user_id}: {e}")
    
    async def get_remaining_messages(self, user_id: int) -> int:
        """Get remaining messages for the day."""
        if not validation_service.validate_user_id(user_id):
            return 0
        
        daily_limit = config_service.get_free_message_limit()
        
        if self.counter_service:
            return await self.counter_service.get_remaining_messages(user_id, daily_limit)
        else:
            # Fallback calculation
            try:
                messages_today = await db_count_user_messages_today(self.pool, user_id)
                remaining = daily_limit - messages_today
                return max(0, remaining)
            except Exception as e:
                raise RuntimeError(f"Failed to get remaining messages for user {user_id}: {e}")
    
    async def generate_response(
        self, 
        user_id: int, 
        user_message: str, 
        gender_preference: str, 
        personality_profile: Optional[Dict[str, float]] = None, 
        user_language: str = "en"
    ) -> str:
        """Generate AI response with validation and error handling."""
        # Validate inputs
        if not validation_service.validate_user_id(user_id):
            raise ValueError(f"Invalid user ID: {user_id}")
        
        text_validation = validation_service.validate_message_text(user_message)
        if not text_validation["is_valid"]:
            raise ValueError(text_validation["error"])
        
        if not validation_service.validate_gender_preference(gender_preference):
            raise ValueError(f"Invalid gender preference: {gender_preference}")
        
        if not validation_service.validate_language(user_language):
            raise ValueError(f"Invalid language: {user_language}")
        
        if personality_profile:
            profile_validation = validation_service.validate_personality_profile(personality_profile)
            if not profile_validation["is_valid"]:
                raise ValueError(profile_validation["error"])
        
        try:
            # Get chat history
            chat_history = await self.get_chat_history(user_id, limit=10)
            
            # Generate personality prompt
            if self.persona_service:
                persona_prompt = await self.persona_service.generate_persona_prompt(
                    gender_preference, personality_profile, user_language
                )
            else:
                persona_prompt = personality_prompt_generator.generate_prompt(
                    gender_preference, personality_profile, user_language
                )
            
            # Prepare messages for OpenAI
            messages = [{"role": "system", "content": persona_prompt}]
            
            # Add chat history
            for msg in chat_history:
                messages.append({"role": msg.role, "content": msg.text})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Generate response
            response = await self.openai_client.chat.completions.create(
                model=config_service.get_openai_config().get("model", "gpt-3.5-turbo"),
                messages=messages,
                max_tokens=config_service.get_openai_config().get("max_tokens", 1000),
                temperature=config_service.get_openai_config().get("temperature", 0.7),
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Validate response length
            max_length = config_service.get_max_message_length()
            if len(ai_response) > max_length:
                ai_response = ai_response[:max_length] + "..."
            
            # Save AI response to database
            await self.add_message(user_id, "assistant", ai_response)
            
            return ai_response
            
        except Exception as e:
            if "rate limit" in str(e).lower():
                raise OpenAIException("Rate limit exceeded. Please try again later.")
            elif "quota" in str(e).lower():
                raise OpenAIException("API quota exceeded. Please try again later.")
            else:
                raise OpenAIException(f"Failed to generate response: {e}")
    
    async def get_message_stats(self, user_id: int) -> Dict[str, Any]:
        """Get message statistics for a user."""
        if not validation_service.validate_user_id(user_id):
            raise ValueError(f"Invalid user ID: {user_id}")
        
        try:
            daily_limit = config_service.get_free_message_limit()
            remaining = await self.get_remaining_messages(user_id)
            used = daily_limit - remaining
            
            return {
                "daily_limit": daily_limit,
                "used_today": used,
                "remaining_today": remaining,
                "can_send_more": remaining > 0
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get message stats for user {user_id}: {e}")
