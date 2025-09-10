"""
User domain queries for PostgreSQL.
"""
import asyncpg
from typing import Optional
from datetime import datetime

from shared.models.user import User, UserCreate, UserUpdate
from core.exceptions import DatabaseException


async def create_user(pool: asyncpg.Pool, user_data: UserCreate) -> None:
    """Create a new user."""
    async with pool.acquire() as conn:
        try:
            await conn.execute("""
                INSERT INTO users (id, username, first_name, last_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO NOTHING
            """, user_data.id, user_data.username, user_data.first_name, user_data.last_name)
        except Exception as e:
            raise DatabaseException(f"Error creating user {user_data.id}: {e}", e)


async def get_user(pool: asyncpg.Pool, user_id: int) -> Optional[User]:
    """Get user by ID."""
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow("""
                SELECT id, username, first_name, last_name, gender_preference,
                       subscription_status, consent_given, subscription_expires_at,
                       created_at, updated_at
                FROM users
                WHERE id = $1
            """, user_id)
            
            if not row:
                return None
            
            return User(
                id=row['id'],
                username=row['username'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                gender_preference=row['gender_preference'],
                subscription_status=row['subscription_status'],
                consent_given=row['consent_given'],
                subscription_expires_at=row['subscription_expires_at'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        except Exception as e:
            raise DatabaseException(f"Error getting user {user_id}: {e}", e)


async def update_user(pool: asyncpg.Pool, user_id: int, user_data: UserUpdate) -> None:
    """Update user data."""
    async with pool.acquire() as conn:
        try:
            # Build dynamic query based on provided fields
            fields = []
            values = []
            param_count = 1
            
            if user_data.gender_preference is not None:
                fields.append(f"gender_preference = ${param_count}")
                values.append(user_data.gender_preference)
                param_count += 1
            
            if user_data.subscription_status is not None:
                fields.append(f"subscription_status = ${param_count}")
                values.append(user_data.subscription_status)
                param_count += 1
            
            if user_data.consent_given is not None:
                fields.append(f"consent_given = ${param_count}")
                values.append(user_data.consent_given)
                param_count += 1
            
            if user_data.subscription_expires_at is not None:
                fields.append(f"subscription_expires_at = ${param_count}")
                values.append(user_data.subscription_expires_at)
                param_count += 1
            
            if not fields:
                return  # Nothing to update
            
            fields.append(f"updated_at = ${param_count}")
            values.append(datetime.utcnow())
            values.append(user_id)
            
            query = f"""
                UPDATE users 
                SET {', '.join(fields)}
                WHERE id = ${param_count + 1}
            """
            
            await conn.execute(query, *values)
        except Exception as e:
            raise DatabaseException(f"Error updating user {user_id}: {e}", e)


async def get_user_consent(pool: asyncpg.Pool, user_id: int) -> bool:
    """Get user consent status."""
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow("""
                SELECT consent_given FROM users WHERE id = $1
            """, user_id)
            return row['consent_given'] if row else False
        except Exception as e:
            raise DatabaseException(f"Error getting user consent {user_id}: {e}", e)


async def set_user_consent(pool: asyncpg.Pool, user_id: int, consent: bool) -> None:
    """Set user consent status."""
    async with pool.acquire() as conn:
        try:
            await conn.execute("""
                UPDATE users 
                SET consent_given = $1, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """, consent, user_id)
        except Exception as e:
            raise DatabaseException(f"Error setting user consent {user_id}: {e}", e)


async def get_gender_preference(pool: asyncpg.Pool, user_id: int) -> str:
    """Get user gender preference."""
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow("""
                SELECT gender_preference FROM users WHERE id = $1
            """, user_id)
            return row['gender_preference'] if row else 'female'
        except Exception as e:
            raise DatabaseException(f"Error getting gender preference {user_id}: {e}", e)


async def set_gender_preference(pool: asyncpg.Pool, user_id: int, preference: str) -> None:
    """Set user gender preference."""
    async with pool.acquire() as conn:
        try:
            await conn.execute("""
                UPDATE users 
                SET gender_preference = $1, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """, preference, user_id)
        except Exception as e:
            raise DatabaseException(f"Error setting gender preference {user_id}: {e}", e)
