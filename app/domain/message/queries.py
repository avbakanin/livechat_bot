"""
Message domain queries for PostgreSQL.
"""
import asyncpg
from typing import List, Optional
from datetime import datetime

from shared.models.message import Message, MessageCreate, MessageContext
from core.exceptions import DatabaseException


async def create_message(pool: asyncpg.Pool, message_data: MessageCreate) -> Message:
    """Create a new message."""
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow("""
                INSERT INTO messages (user_id, role, text)
                VALUES ($1, $2, $3)
                RETURNING id, created_at
            """, message_data.user_id, message_data.role, message_data.text)
            
            return Message(
                id=row['id'],
                user_id=message_data.user_id,
                role=message_data.role,
                text=message_data.text,
                created_at=row['created_at']
            )
        except Exception as e:
            raise DatabaseException(f"Error creating message: {e}", e)


async def get_user_messages(pool: asyncpg.Pool, user_id: int, limit: int = 10) -> List[MessageContext]:
    """Get user's recent messages for context."""
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch("""
                SELECT role, text
                FROM messages
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            """, user_id, limit)
            
            # Reverse to get chronological order
            return [MessageContext(role=r["role"], text=r["text"]) for r in reversed(rows)]
        except Exception as e:
            raise DatabaseException(f"Error getting user messages {user_id}: {e}", e)


async def delete_user_messages(pool: asyncpg.Pool, user_id: int) -> int:
    """Delete all messages for a user."""
    async with pool.acquire() as conn:
        try:
            result = await conn.execute("""
                DELETE FROM messages WHERE user_id = $1
            """, user_id)
            
            # Extract number of deleted rows from result
            return int(result.split()[-1]) if result else 0
        except Exception as e:
            raise DatabaseException(f"Error deleting messages for user {user_id}: {e}", e)


async def count_user_messages_today(pool: asyncpg.Pool, user_id: int) -> int:
    """Count user messages sent today."""
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow("""
                SELECT COUNT(*) as count
                FROM messages
                WHERE user_id = $1 
                AND role = 'user'
                AND DATE(created_at) = CURRENT_DATE
            """, user_id)
            
            return row['count'] if row else 0
        except Exception as e:
            raise DatabaseException(f"Error counting user messages {user_id}: {e}", e)
