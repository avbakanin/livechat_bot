import os
from dotenv import load_dotenv
import asyncio
import asyncpg
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import logging
import openai

load_dotenv() 

# --- Логирование ---
logging.basicConfig(level=logging.INFO)

# --- Настройки бота и OpenAI ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FREE_MESSAGE_LIMIT = 100

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT"))
}

# --- Настройка OpenAI ---
openai.api_key = OPENAI_API_KEY

# --- Настройка бота ---
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# --- Подключение к PostgreSQL ---
async def create_pool():
    return await asyncpg.create_pool(
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )

# --- Обработчик команды /start ---
@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer(f"Привет! У тебя {FREE_MESSAGE_LIMIT} бесплатных сообщений.")

# --- Обработчик текстовых сообщений ---
@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""

    async with dp.pool.acquire() as conn:
        # Добавляем пользователя в таблицу users
        await conn.execute("""
            INSERT INTO users(id, username, first_name, last_name)
            VALUES($1, $2, $3, $4)
            ON CONFLICT (id) DO NOTHING
        """, user_id, username, first_name, last_name)

        # Проверяем лимит сообщений
        row = await conn.fetchrow(
            "SELECT COUNT(*) AS cnt FROM messages WHERE user_id=$1", user_id
        )
        used = row["cnt"] if row else 0
        if used >= FREE_MESSAGE_LIMIT:
            await message.answer("Превышен лимит бесплатных сообщений.")
            return

        # Сохраняем сообщение пользователя
        await conn.execute(
            "INSERT INTO messages(user_id, text, role) VALUES($1, $2, 'user')",
            user_id, message.text
        )

        # --- Запрос к OpenAI GPT-5 Nano ---
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-5-nano",
                messages=[{"role": "user", "content": message.text}],
                max_completion_tokens=1000
            )
            raw_answer = response.choices[0].message.content
            answer = raw_answer.strip() if raw_answer and raw_answer.strip() else "OpenAI вернул пустой ответ."
        except Exception as e:
            answer = f"Ошибка при обращении к OpenAI: {e}"
            logging.error(f"Ошибка GPT: {e}")

        # Сохраняем ответ
        await conn.execute(
            "INSERT INTO messages(user_id, text, role) VALUES($1, $2, 'assistant')",
            user_id, answer
        )

        # Отправляем ответ пользователю
        await message.answer(answer)

# --- Основная функция ---
async def main():
    dp.pool = await create_pool()
    logging.info("Connected to PostgreSQL!")
    try:
        logging.info("Bot started!")
        await dp.start_polling(bot)
    finally:
        await dp.pool.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
