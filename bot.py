import os
from dotenv import load_dotenv
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from openai import AsyncOpenAI
from db import create_pool, add_user, add_message, can_send, get_context, get_gender_preference, set_gender_preference
from config import TELEGRAM_TOKEN, OPENAI_API_KEY, FREE_MESSAGE_LIMIT

load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer(f"Привет! У тебя {FREE_MESSAGE_LIMIT} бесплатных сообщений в день. Выбери пол компаньона: /choose_gender female или male.")

@dp.message(Command(commands=["choose_gender"]))
async def cmd_choose_gender(message: Message):
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    if not args or args[0] not in ['female', 'male']:
        await message.answer("Укажи пол: /choose_gender female или /choose_gender male")
        return
    preference = args[0]
    user_id = message.from_user.id
    await set_gender_preference(dp.pool, user_id, preference)
    await message.answer(f"Пол компаньона изменен на {preference == 'female' and 'девушку' or 'молодого человека'}.")

@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""

    await add_user(dp.pool, user_id, username, first_name, last_name)

    if not await can_send(dp.pool, user_id):
        await message.answer("Превышен ежедневный лимит бесплатных сообщений.")
        return

    await add_message(dp.pool, user_id, 'user', message.text)

    try:
        gender = await get_gender_preference(dp.pool, user_id)
        system_prompt = {
            'female': "Ты ИИ-девушка, флиртующая и supportive для одиноких людей. Будь милой, empathetic и игривой.",
            'male': "Ты ИИ-молодой человек, флиртующий и supportive для одиноких людей. Будь уверенным, empathetic и игривым."
        }[gender]

        history = await get_context(dp.pool, user_id, limit=10)
        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message.text}]

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_completion_tokens=1000
        )
        answer = response.choices[0].message.content.strip() or "OpenAI вернул пустой ответ."
    except Exception as e:
        answer = f"Ошибка: {e}"
        logging.error(f"OpenAI error: {e}")

    await add_message(dp.pool, user_id, 'assistant', answer)
    await message.answer(answer)

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