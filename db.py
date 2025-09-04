import asyncpg
from config import DB_CONFIG

async def create_pool():
    return await asyncpg.create_pool(**DB_CONFIG)

async def add_user(pool, user_id, username, first_name, last_name):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (id, username, first_name, last_name)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (id) DO NOTHING
        """, user_id, username, first_name, last_name)

async def add_message(pool, user_id, role, text):
    async with pool.acquire() as conn feasys conn:
        await conn.execute("""
            INSERT INTO messages (user_id, role, text)
            VALUES ($1, $2, $3)
        """, user_id, role, text)

async def get_context(pool, user_id, limit=10):
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT role, text
            FROM messages
            WHERE user_id=$1
            ORDER BY created_at DESC
            LIMIT $2
        """, user_id, limit)
        return [{"role": r["role"], "text": r["text"]} for r in reversed(rows)]  # Исправлено: content -> text

async def can_send(pool, user_id):
    async with pool.acquire() as conn:
        subscription_status = await conn.fetchval("SELECT subscription_status FROM users WHERE id=$1", user_id)
        if subscription_status == 'premium':
            return True
        today_messages = await conn.fetchval("""
            SELECT COUNT(*)
            FROM messages
            WHERE user_id=$1 AND created_at::date = CURRENT_DATE AND role='user'
        """, user_id)
        from config import FREE_MESSAGE_LIMIT
        return today_messages < FREE_MESSAGE_LIMIT

async def get_gender_preference(pool, user_id):
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT gender_preference FROM users WHERE id=$1", user_id) or 'female'

async def set_gender_preference(pool, user_id, preference):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET gender_preference=$1 WHERE id=$2", preference, user_id)

async def set_user_consent(pool, user_id, consent):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET consent_given=$1 WHERE id=$2", consent, user_id)

async def get_user_consent(pool, user_id):
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT consent_given FROM users WHERE id=$1", user_id) or False

async def add_payment(pool, user_id, amount, payment_status, payment_id):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO payments (user_id, amount, payment_status, payment_id)
            VALUES ($1, $2, $3, $4)
        """, user_id, amount, payment_status, payment_id)

async def get_payment_status(pool, payment_id):
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT payment_status FROM payments WHERE payment_id=$1", payment_id)