import asyncpg
from config import DB_CONFIG

async def create_pool():
    return await asyncpg.create_pool(**DB_CONFIG)

async def add_user(pool, tg_id, username):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (tg_id, username)
            VALUES ($1, $2)
            ON CONFLICT (tg_id) DO NOTHING
        """, tg_id, username)

async def add_message(pool, tg_id, role, content):
    async with pool.acquire() as conn:
        user_id = await conn.fetchval("SELECT id FROM users WHERE tg_id=$1", tg_id)
        if user_id:
            await conn.execute("""
                INSERT INTO messages (user_id, role, content)
                VALUES ($1, $2, $3)
            """, user_id, role, content)

async def get_context(pool, tg_id, limit=5):
    async with pool.acquire() as conn:
        user_id = await conn.fetchval("SELECT id FROM users WHERE tg_id=$1", tg_id)
        if not user_id:
            return []
        rows = await conn.fetch("""
            SELECT role, content
            FROM messages
            WHERE user_id=$1
            ORDER BY created_at DESC
            LIMIT $2
        """, user_id, limit)
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

# Проверка подписки (простая, без оплаты)
async def can_send(pool, tg_id):
    async with pool.acquire() as conn:
        user_id = await conn.fetchval("SELECT id FROM users WHERE tg_id=$1", tg_id)
        if not user_id:
            return True
        today_messages = await conn.fetchval("""
            SELECT COUNT(*)
            FROM messages
            WHERE user_id=$1 AND created_at::date = CURRENT_DATE
        """, user_id)
        from config import FREE_MESSAGE_LIMIT
        return today_messages < FREE_MESSAGE_LIMIT

