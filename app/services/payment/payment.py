import logging
from shared.constants import APP_CONFIG
# from yookassa import Configuration, Payment  # Закомментировано, раскомментируйте после установки yookassa


async def create_payment(pool, user_id, amount):
    try:
        # Configuration.configure(APP_CONFIG['YOOKASSA_SHOP_ID'], APP_CONFIG['YOOKASSA_SECRET_KEY'])
        # payment = Payment.create({
        #     "amount": {"value": str(amount), "currency": "RUB"},
        #     "confirmation": {"type": "redirect", "return_url": "https://your-site.com/return"},
        #     "capture": True,
        #     "description": f"Премиум-подписка для {user_id}"
        # })
        # await add_payment(pool, user_id, amount, payment.status, payment.id)
        # logging.info(f"Created payment {payment.id} for user {user_id}")
        # return payment.confirmation.confirmation_url
        
        # Временная заглушка
        logging.info(f"Payment creation requested for user {user_id}, amount: {amount}")
        return None
    except Exception as e:
        logging.error(f"Error creating payment for user {user_id}: {e}")
        return None
    


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
