import logging

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

async def delete_user_messages(pool, user_id):
    async with pool.acquire() as conn:
        try:
            result = await conn.execute("""
                DELETE FROM messages
                WHERE user_id=$1
            """, user_id)
            logging.info(f"Deleted messages for user {user_id}")
            return result
        except Exception as e:
            logging.error(f"Error deleting messages for user {user_id}: {e}")
            raise