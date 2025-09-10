import logging

async def add_user(pool, user_id, username, first_name, last_name):
    async with pool.acquire() as conn:
        try:
            await conn.execute("""
                INSERT INTO users (id, username, first_name, last_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO NOTHING
            """, user_id, username, first_name, last_name)
            logging.info(f"Added or updated user {user_id}")
        except Exception as e:
            logging.error(f"Error in add_user for user {user_id}: {e}")
            raise

