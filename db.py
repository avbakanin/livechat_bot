import asyncpg
import logging
from config import DB_CONFIG, FREE_MESSAGE_LIMIT

async def create_pool():
    try:
        pool = await asyncpg.create_pool(**DB_CONFIG)
        logging.info("Successfully created database pool")
        return pool
    except Exception as e:
        logging.error(f"Error creating database pool: {e}")
        raise

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

async def add_message(pool, user_id, role, text):
    async with pool.acquire() as conn:
        try:
            await conn.execute("""
                INSERT INTO messages (user_id, role, text)
                VALUES ($1, $2, $3)
            """, user_id, role, text)
            logging.info(f"Added message for user {user_id} with role {role}")
        except Exception as e:
            logging.error(f"Error in add_message for user {user_id}: {e}")
            raise

async def get_context(pool, user_id, limit=10):
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch("""
                SELECT role, text
                FROM messages
                WHERE user_id=$1
                ORDER BY created_at DESC
                LIMIT $2
            """, user_id, limit)
            logging.info(f"Retrieved context for user {user_id}, {len(rows)} messages")
            return [{"role": r["role"], "text": r["text"]} for r in reversed(rows)]
        except Exception as e:
            logging.error(f"Error in get_context for user {user_id}: {e}")
            raise

async def can_send(pool, user_id):
    async with pool.acquire() as conn:
        try:
            if await is_subscription_active(pool, user_id):
                logging.info(f"User {user_id} has active premium subscription, can send messages")
                return True
            today_messages = await conn.fetchval("""
                SELECT COUNT(*)
                FROM messages
                WHERE user_id=$1 AND created_at::date = CURRENT_DATE AND role='user'
            """, user_id)
            can_send = today_messages < FREE_MESSAGE_LIMIT
            logging.info(f"User {user_id} has sent {today_messages}/{FREE_MESSAGE_LIMIT} messages today, can_send={can_send}")
            return can_send
        except Exception as e:
            logging.error(f"Error in can_send for user {user_id}: {e}")
            raise

async def get_gender_preference(pool, user_id):
    async with pool.acquire() as conn:
        try:
            preference = await conn.fetchval("SELECT gender_preference FROM users WHERE id=$1", user_id) or 'female'
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

async def add_payment(pool, user_id, amount, payment_status, payment_id):
    async with pool.acquire() as conn:
        try:
            await conn.execute("""
                INSERT INTO payments (user_id, amount, payment_status, payment_id)
                VALUES ($1, $2, $3, $4)
            """, user_id, amount, payment_status, payment_id)
            logging.info(f"Added payment {payment_id} for user {user_id}, status: {payment_status}")
        except Exception as e:
            logging.error(f"Error in add_payment for user {user_id}: {e}")
            raise

async def get_payment_status(pool, payment_id):
    async with pool.acquire() as conn:
        try:
            status = await conn.fetchval("SELECT payment_status FROM payments WHERE payment_id=$1", payment_id)
            logging.info(f"Retrieved payment_status for payment {payment_id}: {status}")
            return status
        except Exception as e:
            logging.error(f"Error in get_payment_status for payment {payment_id}: {e}")
            raise

async def is_subscription_active(pool, user_id):
    async with pool.acquire() as conn:
        try:
            status = await conn.fetchval(
                "SELECT subscription_status FROM users WHERE id=$1 AND (subscription_expires_at IS NULL OR subscription_expires_at > CURRENT_TIMESTAMP)",
                user_id
            )
            is_active = status == 'premium'
            logging.info(f"Checked subscription for user {user_id}: is_active={is_active}")
            return is_active
        except Exception as e:
            logging.error(f"Error in is_subscription_active for user {user_id}: {e}")
            raise