"""
Main entry point for the Telegram bot application.
"""
import asyncio
import logging
from contextlib import suppress
from openai import AsyncOpenAI
from aiogram import Bot, Dispatcher

from core.database import db_manager
from core.middleware import AccessMiddleware, LoggingMiddleware, DatabaseMiddleware, ServiceMiddleware
from config.telegram import TELEGRAM_CONFIG
from config.openai import OPENAI_CONFIG
from domain.user.handlers import router as user_router
from domain.message.handlers import router as message_router
from domain.payment.handlers import router as payment_router
from domain.user.services import UserService
from domain.message.services import MessageService


async def main():
    """Main application entry point."""
    print('MAIN IS STARTED')
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('bot.log')
        ]
    )
    
    # Initialize services
    pool = None
    dp = Dispatcher()
    
    try:
        # Create database pool
        pool = await db_manager.create_pool()
        
        # Initialize bot and OpenAI client
        bot = Bot(token=TELEGRAM_CONFIG['token'])
        openai_client = AsyncOpenAI(
            api_key=OPENAI_CONFIG['api_key'],
            base_url=OPENAI_CONFIG['base_url']
        )
        
        # Initialize services
        user_service = UserService(pool)
        message_service = MessageService(pool, openai_client)
        
        # Setup middleware
        dp.message.middleware(AccessMiddleware(TELEGRAM_CONFIG['allowed_user_ids']))
        dp.callback_query.middleware(AccessMiddleware(TELEGRAM_CONFIG['allowed_user_ids']))
        dp.message.middleware(LoggingMiddleware())
        dp.callback_query.middleware(LoggingMiddleware())
        dp.message.middleware(DatabaseMiddleware(pool))
        dp.callback_query.middleware(DatabaseMiddleware(pool))
        dp.message.middleware(ServiceMiddleware(user_service, message_service))
        dp.callback_query.middleware(ServiceMiddleware(user_service, message_service))
        
        # Inject additional dependencies
        dp['bot'] = bot
        dp['client'] = openai_client
        dp['pool'] = pool
        
        # Include routers
        dp.include_router(user_router)
        dp.include_router(message_router)
        dp.include_router(payment_router)
        
        logging.info("Connected to PostgreSQL!")
        logging.info("Bot started!")
        
        # Start polling
        await dp.start_polling(bot)
        
    except (KeyboardInterrupt, SystemExit):
        logging.info("KeyboardInterrupt: бот остановлен пользователем (Ctrl+C)")
    except asyncio.CancelledError:
        logging.info("Polling был отменен")
    except Exception as e:
        logging.error(f"Bot polling error: {e}")
    finally:
        logging.info("Завершаем работу...")
        
        # Close database pool
        if pool is not None:
            with suppress(Exception):
                await db_manager.close_pool()
            logging.info("PostgreSQL pool закрыт")
        
        # Close bot session
        with suppress(Exception):
            await bot.session.close()
        logging.info("Сессия бота закрыта")
        
        logging.info("✅ Бот полностью остановлен")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
