import asyncio
import logging
from contextlib import suppress
from openai import AsyncOpenAI
from aiogram import Bot, Dispatcher

from services import create_pool
from shared.constants import APP_CONFIG
from handlers.handlers import router

async def main():
    print('MAIN IS STARTED')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('bot.log')
        ]
    )
    
    pool = None
    dp = Dispatcher()
    
    try:
        # bot, client, pool add to handlers automaticaly
        dp['bot'] = Bot(token=APP_CONFIG['TELEGRAM_TOKEN'])
        dp['client'] = AsyncOpenAI(api_key=APP_CONFIG['OPENAI_API_KEY'])
        
        pool = await create_pool()
        dp['pool'] = pool

        dp.include_router(router)

        logging.info("Connected to PostgreSQL!")
        logging.info("Bot started!")
        
        # Запускаем polling
        await dp.start_polling(dp['bot'])
        
    except (KeyboardInterrupt, SystemExit):
        logging.info("KeyboardInterrupt: бот остановлен пользователем (Ctrl+C)")
    except asyncio.CancelledError:
        logging.info("Polling был отменен")
    except Exception as e:
        logging.error(f"Bot polling error: {e}")
    finally:
        logging.info("Завершаем работу...")
        
        # Закрываем pool только если он был создан
        if pool is not None:
            with suppress(Exception):
                await pool.close()
            logging.info("PostgreSQL pool закрыт")
        
        # Закрываем сессию бота
        with suppress(Exception):
            await dp['bot'].session.close()
        logging.info("Сессия бота закрыта")
        
        logging.info("✅ Бот полностью остановлен")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")