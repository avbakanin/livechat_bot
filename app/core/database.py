"""
Database connection and pool management for PostgreSQL using asyncpg.
"""
from contextlib import asynccontextmanager
from typing import Optional

import asyncpg
from shared.constants import DATABASE_CONFIG
from shared.utils.logger import get_logger


class DatabaseManager:
    """Manages PostgreSQL connection pool."""

    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
        self.logger = get_logger("database")

    async def create_pool(self) -> asyncpg.Pool:
        """Create and return a new connection pool."""
        try:
            self._pool = await asyncpg.create_pool(**DATABASE_CONFIG)
            self.logger.info("Successfully created database pool")
            return self._pool
        except Exception as e:
            self.logger.error(f"Error creating database pool: {e}")
            raise

    async def close_pool(self):
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            self.logger.info("Database pool closed")

    @property
    def pool(self) -> asyncpg.Pool:
        """Get the current pool."""
        if not self._pool:
            raise RuntimeError(
                "Database pool not initialized. Call create_pool() first."
            )
        return self._pool

    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool."""
        if not self._pool:
            raise RuntimeError("Database pool not initialized")

        async with self._pool.acquire() as connection:
            yield connection


# Global database manager instance
db_manager = DatabaseManager()


async def create_pool() -> asyncpg.Pool:
    """Create database pool - backward compatibility function."""
    return await db_manager.create_pool()


async def close_pool():
    """Close database pool - backward compatibility function."""
    await db_manager.close_pool()
