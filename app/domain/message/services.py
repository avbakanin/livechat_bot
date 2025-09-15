"""
Message domain services - business logic and OpenAI integration.
"""

import logging
from typing import List

import asyncpg
from config.openai import OPENAI_CONFIG
from domain.message.queries import count_user_messages_today as db_count_user_messages_today
from domain.message.queries import create_message as db_create_message
from domain.message.queries import delete_user_messages as db_delete_user_messages
from domain.message.queries import get_user_messages as db_get_user_messages
from openai import AsyncOpenAI
from shared.i18n import i18n
from shared.models.message import MessageContext, MessageCreate
from services.persona import PersonaService
from services.counter import DailyCounterService

from core.exceptions import OpenAIException


class MessageService:
    """Message business logic service."""

    def __init__(self, pool: asyncpg.Pool, openai_client: AsyncOpenAI, persona_service: PersonaService = None, counter_service: DailyCounterService = None):
        self.pool = pool
        self.openai_client = openai_client
        self.persona_service = persona_service
        self.counter_service = counter_service

    async def add_message(self, user_id: int, role: str, text: str) -> None:
        """Add a message to the database and update counter if it's a user message."""
        message_data = MessageCreate(user_id=user_id, role=role, text=text)
        await db_create_message(self.pool, message_data)
        
        # Increment counter for user messages
        if role == "user" and self.counter_service:
            await self.counter_service.increment_user_count(user_id)

    async def get_chat_history(self, user_id: int, limit: int = 10) -> List[MessageContext]:
        """Get user's chat history."""
        return await db_get_user_messages(self.pool, user_id, limit)

    async def delete_user_messages(self, user_id: int) -> int:
        """Delete all messages for a user."""
        return await db_delete_user_messages(self.pool, user_id)

    async def can_send_message(self, user_id: int) -> bool:
        """Check if user can send messages (not exceeded daily limit)."""
        # Get daily limit from config
        daily_limit = OPENAI_CONFIG.get("FREE_MESSAGE_LIMIT", 100)

        # Use efficient counter service if available, otherwise fallback to old method
        if self.counter_service:
            return await self.counter_service.can_send_message(user_id, daily_limit)
        else:
            # Fallback to old method
            messages_today = await db_count_user_messages_today(self.pool, user_id)
            return messages_today < daily_limit

    async def get_remaining_messages(self, user_id: int) -> int:
        """Get remaining messages for the day."""
        daily_limit = OPENAI_CONFIG.get("FREE_MESSAGE_LIMIT", 100)
        
        if self.counter_service:
            return await self.counter_service.get_remaining_messages(user_id, daily_limit)
        else:
            # Fallback calculation
            messages_today = await db_count_user_messages_today(self.pool, user_id)
            remaining = daily_limit - messages_today
            return max(0, remaining)

    async def generate_response(self, user_id: int, user_message: str, gender_preference: str) -> str:
        """Generate AI response using OpenAI with dynamic personas."""
        try:
            # Get chat history
            history = await self.get_chat_history(user_id, limit=10)

            # Create system prompt - use persona service if available, otherwise fallback
            if self.persona_service:
                system_prompt = self.persona_service.get_persona_for_gender(gender_preference)
            else:
                system_prompt = self._get_system_prompt(gender_preference)

            # Prepare messages for OpenAI
            messages = [{"role": "system", "content": system_prompt}]

            # Add history
            for msg in history:
                messages.append({"role": msg.role, "content": msg.text})

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Call OpenAI API
            response = await self.openai_client.chat.completions.create(
                model=OPENAI_CONFIG["model"],
                messages=messages,
                temperature=OPENAI_CONFIG["temperature"],
                max_tokens=OPENAI_CONFIG["max_tokens"],
            )

            return response.choices[0].message.content.strip() or i18n.t("messages.empty_response")

        except Exception as e:
            logging.error(f"OpenAI error: {e}")
            raise OpenAIException(f"Error generating response: {e}", e)

    def _get_system_prompt(self, gender_preference: str) -> str:
        """Get system prompt based on gender preference (fallback method)."""
        # Fallback prompts - should be replaced by PersonaService
        fallback_prompts = {
            "female": "You are an AI companion. Be friendly, empathetic and supportive.",
            "male": "You are an AI companion. Be friendly, empathetic and supportive.",
        }
        return fallback_prompts.get(gender_preference, fallback_prompts["female"])
