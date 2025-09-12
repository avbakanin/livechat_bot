import logging


async def set_user_consent(pool, user_id, consent):
    async with pool.acquire() as conn:
        try:
            await conn.execute("UPDATE users SET consent_given=$1 WHERE id=$2", consent, user_id)
            logging.info(f"Set consent_given to {consent} for user {user_id}")
        except Exception as e:
            logging.error(f"Error in set_user_consent for user {user_id}: {e}")
            raise


async def get_user_consent(pool, user_id):
    async with pool.acquire() as conn:
        try:
            consent = await conn.fetchval("SELECT consent_given FROM users WHERE id=$1", user_id) or False
            logging.info(f"Retrieved consent_given for user {user_id}: {consent}")
            return consent
        except Exception as e:
            logging.error(f"Error in get_user_consent for user {user_id}: {e}")
            raise
