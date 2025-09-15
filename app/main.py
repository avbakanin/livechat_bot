import asyncio
import logging
from contextlib import suppress
from typing import Any

from aiogram import Bot, Dispatcher
from config.openai import OPENAI_CONFIG
from config.telegram import TELEGRAM_CONFIG
from domain import setup_routers
from domain.message.handlers import router as message_router
from domain.message.services import MessageService
from domain.payment.handlers import router as payment_router
from domain.user.handlers import router as user_router
from domain.user.services_cached import UserService
from openai import AsyncOpenAI
from services.counter import DailyCounterService
from services.metrics import MetricsService
from services.persona import PersonaService
from shared.fsm.fsm_middleware import FSMMiddleware
from shared.fsm.user_cache import user_cache
from shared.middlewares.i18n_middleware import I18nMiddleware
from shared.tasks import DailyResetTask, PartitionManagementTask

from core.database import db_manager
from core.middleware import AccessMiddleware, LoggingMiddleware, ServiceMiddleware


async def main():
    logging.info("MAIN IS STARTED")

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("bot.log", encoding="utf-8")],
    )

    # Initialize services
    pool = None
    dp = Dispatcher()

    try:
        # Create database pool
        pool = await db_manager.create_pool()

        # Initialize bot and OpenAI client
        bot = Bot(token=TELEGRAM_CONFIG["token"])
        openai_client = AsyncOpenAI(api_key=OPENAI_CONFIG["api_key"], base_url=OPENAI_CONFIG["base_url"])

        # Initialize services
        user_service = UserService(pool)

        # Create metrics service for persistent storage
        metrics_service = MetricsService(pool)

        # Initialize metrics collector with database service
        from shared.metrics.metrics import MetricsCollector

        metrics_collector = MetricsCollector(metrics_service)

        # Update global reference
        import shared.metrics.metrics as metrics_module

        metrics_module.metrics_collector = metrics_collector

        # Create I18n middleware first to use in PersonaService
        i18n_middleware = I18nMiddleware()
        persona_service = PersonaService()

        # Create counter service for efficient message counting
        counter_service = DailyCounterService(pool)

        # Create daily reset task for automatic counter reset at midnight
        daily_reset_task = DailyResetTask(counter_service)

        # Create partition management task for automatic partition creation/deletion
        partition_management_task = PartitionManagementTask(pool)

        message_service = MessageService(pool, openai_client, persona_service, counter_service)

        apply_middlewares(
            dp,
            [
                i18n_middleware,
                FSMMiddleware(),  # Add FSM middleware for caching
                AccessMiddleware(TELEGRAM_CONFIG["allowed_user_ids"]),
                LoggingMiddleware(),
                ServiceMiddleware(user_service, message_service),
            ],
        )

        # Inject additional dependencies
        dp["bot"] = bot
        dp["client"] = openai_client
        dp["pool"] = pool

        # Load metrics from database
        await metrics_collector.load_from_database()

        # Start auto-save for metrics every 15 minutes (optimized for scalability)
        await metrics_collector.start_auto_save(interval_seconds=900)

        # Start FSM cache cleanup task
        await user_cache.start_cleanup_task()

        # Start daily reset task for automatic counter reset at midnight
        await daily_reset_task.start()

        # Start partition management task for automatic partition creation/deletion
        await partition_management_task.start()

        # Include routers
        setup_routers(dp)

        logging.info("Connected to PostgreSQL!")
        logging.info("FSM cache initialized!")
        logging.info("Daily reset task started!")
        logging.info("Partition management task started!")
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

        # Save metrics to database before shutdown
        await metrics_collector.save_to_database()

        # Stop metrics auto-save
        await metrics_collector.stop_auto_save()
        logging.info("Metrics auto-save stopped")

        # Stop FSM cache cleanup task
        await user_cache.stop_cleanup_task()
        logging.info("FSM cache cleanup stopped")

        # Stop daily reset task
        await daily_reset_task.stop()
        logging.info("Daily reset task stopped")

        # Stop partition management task
        await partition_management_task.stop()
        logging.info("Partition management task stopped")

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


# Setup middleware
def apply_middlewares(dp: Dispatcher, services):
    for service in services:
        dp.message.middleware(service)
        dp.callback_query.middleware(service)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Программа завершена пользователем")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
