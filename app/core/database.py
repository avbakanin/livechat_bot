"""
Database connection and pool management for PostgreSQL using asyncpg.
"""
import asyncpg
import logging
from typing import Optional
from contextlib import asynccontextmanager

from config.database import DATABASE_CONFIG


class DatabaseManager:
    """Manages PostgreSQL connection pool."""
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
    
    async def create_pool(self) -> asyncpg.Pool:
        """Create and return a new connection pool."""
        try:
            self._pool = await asyncpg.create_pool(**DATABASE_CONFIG)
            logging.info("Successfully created database pool")
            return self._pool
        except Exception as e:
            logging.error(f"Error creating database pool: {e}")
            raise
    
    async def close_pool(self):
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            logging.info("Database pool closed")
    
    @property
    def pool(self) -> asyncpg.Pool:
        """Get the current pool."""
        if not self._pool:
            raise RuntimeError("Database pool not initialized. Call create_pool() first.")
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
