"""
User domain queries for PostgreSQL.
"""

from datetime import datetime
from typing import Optional, Dict, Any

import asyncpg
from shared.models.user import User, UserCreate, UserUpdate
from shared.utils.datetime_utils import DateTimeUtils

from core.exceptions import DatabaseException

# Cache for column existence checks
_column_cache = {}


async def _check_columns_exist(conn: asyncpg.Connection, table: str, columns: list) -> bool:
    """Check if columns exist with caching."""
    cache_key = f"{table}:{','.join(columns)}"
    
    if cache_key not in _column_cache:
        result = await conn.fetchval(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = $1 AND column_name = ANY($2)
            )
            """,
            table, columns
        )
        _column_cache[cache_key] = result
    
    return _column_cache[cache_key]


async def create_user(pool: asyncpg.Pool, user_data: UserCreate) -> None:
    """Create a new user."""
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                """
                INSERT INTO users (id, username, first_name, last_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO NOTHING
            """,
                user_data.id,
                user_data.username,
                user_data.first_name,
                user_data.last_name,
            )
        except Exception as e:
            raise DatabaseException(f"Error creating user {user_data.id}: {e}", e)


async def get_user(pool: asyncpg.Pool, user_id: int) -> Optional[User]:
    """Get user by ID."""
    async with pool.acquire() as conn:
        try:
            # Check if timestamp columns exist (with caching)
            timestamp_columns_exist = await _check_columns_exist(conn, 'users', ['created_at', 'updated_at'])

            if timestamp_columns_exist:
                row = await conn.fetchrow(
                    """
                    SELECT id, username, first_name, last_name, gender_preference, language,
                           subscription_status, consent_given, subscription_expires_at,
                           personality_profile, created_at, updated_at
                    FROM users
                    WHERE id = $1
                    """,
                    user_id,
                )
            else:
                row = await conn.fetchrow(
                    """
                    SELECT id, username, first_name, last_name, gender_preference, language,
                           subscription_status, consent_given, subscription_expires_at,
                           personality_profile
                    FROM users
                    WHERE id = $1
                    """,
                    user_id,
                )

            if not row:
                return None

            return User(
                id=row["id"],
                username=row["username"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                gender_preference=row["gender_preference"],
                language=row.get("language", "en"),
                subscription_status=row["subscription_status"],
                consent_given=row["consent_given"],
                subscription_expires_at=row["subscription_expires_at"],
                personality_profile=row.get("personality_profile"),
                created_at=row.get("created_at"),
                updated_at=row.get("updated_at"),
            )
        except Exception as e:
            raise DatabaseException(f"Error getting user {user_id}: {e}", e)


async def delete_user_messages(pool: asyncpg.Pool, user_id: int) -> None:
    """Delete all user messages."""
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                """
                DELETE FROM messages
                WHERE user_id = $1
            """,
                user_id,
            )
        except Exception as e:
            raise DatabaseException(f"Error deleting user messages {user_id}: {e}", e)


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

            if user_data.language is not None:
                fields.append(f"language = ${param_count}")
                values.append(user_data.language)
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

            if user_data.personality_profile is not None:
                fields.append(f"personality_profile = ${param_count}")
                values.append(user_data.personality_profile)
                param_count += 1

            if not fields:
                return  # Nothing to update

            # Check if updated_at column exists (with caching)
            column_exists = await _check_columns_exist(conn, 'users', ['updated_at'])

            if column_exists:
                fields.append(f"updated_at = ${param_count}")
                values.append(DateTimeUtils.utc_now_naive())

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
            row = await conn.fetchrow(
                """
                SELECT consent_given FROM users WHERE id = $1
            """,
                user_id,
            )
            return row["consent_given"] if row else False
        except Exception as e:
            raise DatabaseException(f"Error getting user consent {user_id}: {e}", e)


async def set_user_consent(pool: asyncpg.Pool, user_id: int, consent: bool) -> None:
    """Set user consent status."""
    async with pool.acquire() as conn:
        try:
            # Check if updated_at column exists
            column_exists = await conn.fetchval(
                """
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'updated_at'
                )
            """
            )

            if column_exists:
                await conn.execute(
                    """
                    UPDATE users 
                    SET consent_given = $1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = $2
                """,
                    consent,
                    user_id,
                )
            else:
                # Fallback without updated_at column
                await conn.execute(
                    """
                    UPDATE users 
                    SET consent_given = $1
                    WHERE id = $2
                """,
                    consent,
                    user_id,
                )
        except Exception as e:
            raise DatabaseException(f"Error setting user consent {user_id}: {e}", e)


async def get_gender_preference(pool: asyncpg.Pool, user_id: int) -> str:
    """Get user gender preference."""
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                """
                SELECT gender_preference FROM users WHERE id = $1
            """,
                user_id,
            )
            return row["gender_preference"] if row else "female"
        except Exception as e:
            raise DatabaseException(
                f"Error getting gender preference {user_id}: {e}", e
            )


async def get_user_subscription_status(pool: asyncpg.Pool, user_id: int) -> str:
    """Get user subscription status."""
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                """
                SELECT subscription_status FROM users WHERE id = $1
            """,
                user_id,
            )
            return row["subscription_status"] if row else "free"
        except Exception as e:
            raise DatabaseException(
                f"Error getting subscription status for user {user_id}: {e}", e
            )


async def get_user_subscription_expires_at(pool: asyncpg.Pool, user_id: int):
    """Get user subscription expiration date."""
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                """
                SELECT subscription_expires_at FROM users WHERE id = $1
            """,
                user_id,
            )
            return row["subscription_expires_at"] if row else None
        except Exception as e:
            raise DatabaseException(
                f"Error getting subscription expiration for user {user_id}: {e}", e
            )


async def set_gender_preference(
    pool: asyncpg.Pool, user_id: int, preference: str
) -> None:
    """Set user gender preference."""
    async with pool.acquire() as conn:
        try:
            # Check if updated_at column exists
            column_exists = await conn.fetchval(
                """
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'updated_at'
                )
            """
            )

            if column_exists:
                await conn.execute(
                    """
                    UPDATE users 
                    SET gender_preference = $1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = $2
                """,
                    preference,
                    user_id,
                )
            else:
                # Fallback without updated_at column
                await conn.execute(
                    """
                    UPDATE users 
                    SET gender_preference = $1
                    WHERE id = $2
                """,
                    preference,
                    user_id,
                )
        except Exception as e:
            raise DatabaseException(
                f"Error setting gender preference {user_id}: {e}", e
            )


async def update_user_personality_profile(
    pool: asyncpg.Pool, user_id: int, personality_profile: Dict[str, Any]
) -> None:
    """Update user personality profile."""
    import json
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                """
                SELECT public.update_user_personality_profile($1, $2)
                """,
                user_id,
                json.dumps(personality_profile),
            )
        except Exception as e:
            raise DatabaseException(
                f"Error updating personality profile {user_id}: {e}", e
            )


async def get_user_personality_profile(
    pool: asyncpg.Pool, user_id: int
) -> Optional[Dict[str, Any]]:
    """Get user personality profile."""
    async with pool.acquire() as conn:
        try:
            result = await conn.fetchval(
                """
                SELECT public.get_user_personality_profile($1)
                """,
                user_id,
            )
            return result if result else None
        except Exception as e:
            raise DatabaseException(
                f"Error getting personality profile {user_id}: {e}", e
            )
