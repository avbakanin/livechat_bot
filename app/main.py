import asyncio
from contextlib import suppress

from aiogram import Bot, Dispatcher
from shared.constants import OPENAI_CONFIG, TELEGRAM_CONFIG
from domain import setup_routers
from domain.message.services import MessageService
from domain.user.services_cached import UserService
from openai import AsyncOpenAI
from services.counter import DailyCounterService
from services.metrics import MetricsService
from services.person import PersonService
from shared.fsm.fsm_middleware import FSMMiddleware
from shared.fsm.user_cache import user_cache
from shared.middlewares.i18n_middleware import I18nMiddleware
from shared.tasks import DailyResetTask, PartitionManagementTask
from shared.utils.logger import get_logger

from core.database import db_manager
from core.middleware import LoggingMiddleware, ServiceMiddleware


async def main():
    print("🚀 Starting bot...")
    logger = get_logger("main")
    logger.info("MAIN IS STARTED")

    # Initialize services
    pool = None
    dp = Dispatcher()

    try:
        # Create database pool
        print("📊 Creating database pool...")
        pool = await db_manager.create_pool()
        print("✅ Database pool created")

        # Initialize bot and OpenAI client with conservative timeout settings for unstable connections
        bot = Bot(
            token=TELEGRAM_CONFIG["token"],
            session_timeout=120,  # Very high session timeout for unstable connections
            connect_timeout=120,  # Very high connection timeout
            read_timeout=120,     # Very high read timeout
            write_timeout=120     # Very high write timeout
        )
        openai_client = AsyncOpenAI(
            api_key=OPENAI_CONFIG["api_key"], base_url=OPENAI_CONFIG["base_url"]
        )

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

        # Create I18n middleware first to use in PersonService
        i18n_middleware = I18nMiddleware()
        persona_service = PersonService()

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
                FSMMiddleware(),  # Add FSM middleware for caching
                LoggingMiddleware(),
                ServiceMiddleware(user_service, message_service, pool),
                i18n_middleware,  # I18n middleware should come after ServiceMiddleware
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
        print("🔗 Setting up routers...")
        setup_routers(dp)
        print("✅ Routers setup complete")

        print("📝 Logging startup messages...")
        logger.info("Connected to PostgreSQL!")
        logger.info("FSM cache initialized!")
        logger.info("Daily reset task started!")
        logger.info("Partition management task started!")
        logger.info("Bot started!")
        logger.info("Network timeout settings: 300s (optimized for unstable connections)")
        print("✅ All startup messages logged")

        # Start polling with increased timeout settings
        print("🔄 Starting polling...")
        await dp.start_polling(
            bot,
            timeout=300,  # 5 minutes timeout for very unstable connections
            request_timeout=300,  # 5 minutes for individual requests
            drop_pending_updates=True,  # Drop pending updates to avoid conflicts
            allowed_updates=["message", "callback_query"],  # Limit updates to reduce load
            close_bot_session=False,  # Keep session alive between requests
            fast=False  # Use slower but more reliable polling
        )

    except (KeyboardInterrupt, SystemExit):
        logger.info("KeyboardInterrupt: бот остановлен пользователем (Ctrl+C)")
    except asyncio.CancelledError:
        logger.info("Polling был отменен")
    except Exception as e:
        logger.error(f"Bot polling error: {e}")
        # Log specific network errors for debugging
        if "timeout" in str(e).lower():
            logger.warning("Network timeout detected - this is usually temporary")
        elif "connection" in str(e).lower():
            logger.warning("Connection error detected - check internet connectivity")
    finally:
        logger.info("Завершаем работу...")

        # Save metrics to database before shutdown
        await metrics_collector.save_to_database()

        # Stop metrics auto-save
        await metrics_collector.stop_auto_save()
        logger.info("Metrics auto-save stopped")

        # Stop FSM cache cleanup task
        await user_cache.stop_cleanup_task()
        logger.info("FSM cache cleanup stopped")

        # Stop daily reset task
        await daily_reset_task.stop()
        logger.info("Daily reset task stopped")

        # Stop partition management task
        await partition_management_task.stop()
        logger.info("Partition management task stopped")

        # Close database pool
        if pool is not None:
            with suppress(Exception):
                await db_manager.close_pool()
            logger.info("PostgreSQL pool закрыт")

        # Close bot session
        with suppress(Exception):
            await bot.session.close()
        logger.info("Сессия бота закрыта")

        logger.info("✅ Бот полностью остановлен")


# Setup middleware
def apply_middlewares(dp: Dispatcher, services):
    for service in services:
        dp.message.middleware(service)
        dp.callback_query.middleware(service)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Программа завершена пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
