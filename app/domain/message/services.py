"""
Message domain services - business logic and OpenAI integration.
"""
import logging
from typing import Any, Dict, List

import asyncpg
from config.openai import OPENAI_CONFIG
from domain.message.queries import count_user_messages_today as db_count_user_messages_today
from domain.message.queries import create_message as db_create_message
from domain.message.queries import delete_user_messages as db_delete_user_messages
from domain.message.queries import get_user_messages as db_get_user_messages
from openai import AsyncOpenAI
from shared.models.message import ChatHistory, MessageContext, MessageCreate, OpenAIMessage

from core.exceptions import MessageException, OpenAIException


class MessageService:
    """Message business logic service."""

    def __init__(self, pool: asyncpg.Pool, openai_client: AsyncOpenAI):
        self.pool = pool
        self.openai_client = openai_client

    async def add_message(self, user_id: int, role: str, text: str) -> None:
        """Add a message to the database."""
        message_data = MessageCreate(user_id=user_id, role=role, text=text)
        await db_create_message(self.pool, message_data)

    async def get_chat_history(self, user_id: int, limit: int = 10) -> List[MessageContext]:
        """Get user's chat history."""
        return await db_get_user_messages(self.pool, user_id, limit)

    async def delete_user_messages(self, user_id: int) -> int:
        """Delete all messages for a user."""
        return await db_delete_user_messages(self.pool, user_id)

    async def can_send_message(self, user_id: int) -> bool:
        """Check if user can send messages (not exceeded daily limit)."""
        # This should be moved to a separate service or config
        daily_limit = 100  # Should come from config

        messages_today = await db_count_user_messages_today(self.pool, user_id)
        return messages_today < daily_limit

    async def generate_response(self, user_id: int, user_message: str, gender_preference: str) -> str:
        """Generate AI response using OpenAI."""
        try:
            # Get chat history
            history = await self.get_chat_history(user_id, limit=10)

            # Create system prompt based on gender preference
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

            return response.choices[0].message.content.strip() or "OpenAI вернул пустой ответ."

        except Exception as e:
            logging.error(f"OpenAI error: {e}")
            raise OpenAIException(f"Error generating response: {e}", e)

    def _get_system_prompt(self, gender_preference: str) -> str:
        """Get system prompt based on gender preference."""
        prompts = {
            "female": "Ты ИИ-девушка, флиртующая и supportive для одиноких людей. Будь милой, empathetic и игривой.",
            "male": "Ты ИИ-молодой человек, флиртующий и supportive для одиноких людей. Будь уверенным, empathetic и игривым.",
        }
        return prompts.get(gender_preference, prompts["female"])
