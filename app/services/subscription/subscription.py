import logging

from shared.constants import APP_CONFIG


async def is_subscription_active(pool, user_id):
    async with pool.acquire() as conn:
        try:
            status = await conn.fetchval(
                "SELECT subscription_status FROM users WHERE id=$1 AND (subscription_expires_at IS NULL OR subscription_expires_at > CURRENT_TIMESTAMP)",
                user_id,
            )
            is_active = status == "premium"
            logging.info(
                f"Checked subscription for user {user_id}: is_active={is_active}"
            )
            return is_active
        except Exception as e:
            logging.error(f"Error in is_subscription_active for user {user_id}: {e}")
            raise


async def activate_subscription(pool, user_id, expires_at):
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                """
                UPDATE users SET subscription_status='premium', subscription_expires_at=$1 WHERE id=$2
            """,
                expires_at,
                user_id,
            )
            logging.info(
                f"Activated premium subscription for user {user_id}, expires at {expires_at}"
            )
        except Exception as e:
            logging.error(f"Error in activate_subscription for user {user_id}: {e}")
            raise


async def can_send(pool, user_id):
    async with pool.acquire() as conn:
        try:
            if await is_subscription_active(pool, user_id):
                logging.info(
                    f"User {user_id} has active premium subscription, can send messages"
                )
                return True
            today_messages = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM messages
                WHERE user_id=$1 AND created_at::date = CURRENT_DATE AND role='user'
            """,
                user_id,
            )
            can_send = today_messages < APP_CONFIG["FREE_MESSAGE_LIMIT"]
            logging.info(
                f"User {user_id} has sent {today_messages}/{APP_CONFIG['FREE_MESSAGE_LIMIT']} messages today, can_send={can_send}"
            )
            return can_send
        except Exception as e:
            logging.error(f"Error in can_send for user {user_id}: {e}")
            raise
