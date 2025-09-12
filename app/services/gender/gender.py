import logging


async def get_gender_preference(pool, user_id):
    async with pool.acquire() as conn:
        try:
            preference = await conn.fetchval("SELECT gender_preference FROM users WHERE id=$1", user_id) or "female"
            logging.info(f"Retrieved gender_preference for user {user_id}: {preference}")
            return preference
        except Exception as e:
            logging.error(f"Error in get_gender_preference for user {user_id}: {e}")
            raise


async def set_gender_preference(pool, user_id, preference):
    async with pool.acquire() as conn:
        try:
            await conn.execute("UPDATE users SET gender_preference=$1 WHERE id=$2", preference, user_id)
            logging.info(f"Set gender_preference to {preference} for user {user_id}")
        except Exception as e:
            logging.error(f"Error in set_gender_preference for user {user_id}: {e}")
            raise
