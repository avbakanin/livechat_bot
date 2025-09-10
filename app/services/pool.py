import asyncpg
import logging

async def create_pool():
    from shared.constants import DB_CONFIG
    try:
        pool = await asyncpg.create_pool(**DB_CONFIG)
        logging.info("Successfully created database pool")
        return pool
    except Exception as e:
        logging.error(f"Error creating database pool: {e}")
        raise