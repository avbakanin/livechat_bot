import os
from dotenv import load_dotenv
import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from openai import AsyncOpenAI
from yookassa import Configuration, Payment
from db import create_pool, add_user, add_message, can_send, get_context, get_gender_preference, set_gender_preference, get_user_consent, set_user_consent, add_payment, get_payment_status, is_subscription_active, activate_subscription
from config import TELEGRAM_TOKEN, OPENAI_API_KEY, YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY, FREE_MESSAGE_LIMIT

load_dotenv()

logging.basicConfig(level=logging.INFO)  # Исправлена опечатка: basicBasicConfig -> basicConfig

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

Configuration.configure(YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)

async def create_payment(user_id, amount):
    try:
        payment = Payment.create({
            "amount": {"value": str(amount), "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": "https://your-site.com/return"},
            "capture": True,
            "description": f"Премиум-подписка для {user_id}"
        })
        await add_payment(dp.pool, user_id, amount, payment.status, payment.id)
        logging.info(f"Created payment {payment.id} for user {user_id}")
        return payment.confirmation.confirmation_url
    except Exception as e:
        logging.error(f"Error creating payment for user {user_id}: {e}")
        return None

@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    await add_user(dp.pool, user_id, username, first_name, last_name)  # Добавляем пользователя в начале
    consent = await get_user_consent(dp.pool, user_id)
    if not consent:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Согласен с политикой конфиденциальности", callback_data="consent_agree")],
            [InlineKeyboardButton(text="Читать политику", url="https://your-site.com/privacy")]
        ])
        await message.answer("Пожалуйста, согласись с политикой конфиденциальности:", reply_markup=keyboard)
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Выбрать девушку 😊", callback_data="gender_female"),
            InlineKeyboardButton(text="Выбрать молодого человека 😉", callback_data="gender_male")
        ],
        [InlineKeyboardButton(text="Купить премиум 💳", callback_data="subscribe_premium")]
    ])
    await message.answer(f"Привет! У тебя {FREE_MESSAGE_LIMIT} бесплатных сообщений в день. Выбери пол компаньона:", reply_markup=keyboard)

@dp.message(Command(commands=["choose_gender"]))
async def cmd_choose_gender(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Девушка 😊", callback_data="gender_female"),
            InlineKeyboardButton(text="Молодой человек 😉", callback_data="gender_male")
        ]
    ])
    await message.answer("Выбери пол компаньона:", reply_markup=keyboard)

@dp.callback_query()
async def handle_callback_query(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data
    logging.info(f"Received callback from user {user_id}: {data}")

    username = callback.from_user.username or ""
    first_name = callback.from_user.first_name or ""
    last_name = callback.from_user.last_name or ""

    await add_user(dp.pool, user_id, username, first_name, last_name)  # Гарантируем создание пользователя

    if data == "consent_agree":
        try:
            await set_user_consent(dp.pool, user_id, True)
            logging.info(f"User {user_id} gave consent")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Выбрать девушку 😊", callback_data="gender_female"),
                    InlineKeyboardButton(text="Выбрать молодого человека 😉", callback_data="gender_male")
                ],
                [InlineKeyboardButton(text="Купить премиум 💳", callback_data="subscribe_premium")]
            ])
            await callback.message.edit_text(f"Спасибо за согласие! У тебя {FREE_MESSAGE_LIMIT} бесплатных сообщений в день. Выбери пол компаньона:", reply_markup=keyboard)
        except Exception as e:
            logging.error(f"Error setting consent: {e}")
            await callback.message.edit_text("Произошла ошибка. Попробуйте снова.")
    elif data in ["gender_female", "gender_male"]:
        preference = "female" if data == "gender_female" else "male"
        try:
            await set_gender_preference(dp.pool, user_id, preference)
            logging.info(f"Set gender_preference to {preference} for user {user_id}")
            response_text = "девушку 😊" if preference == "female" else "молодого человека 😉"
            await callback.message.edit_text(f"Пол компаньона изменен на {response_text}.")
        except Exception as e:
            logging.error(f"Error setting gender_preference: {e}")
            await callback.message.edit_text("Произошла ошибка. Попробуйте снова.")
    elif data == "subscribe_premium":
        payment_url = await create_payment(user_id, 500.00)
        if payment_url:
            await callback.message.edit_text(f"Перейдите по ссылке для оплаты премиум-подписки: [Оплатить]({payment_url})")
        else:
            await callback.message.edit_text("Ошибка при создании платежа. Попробуйте позже.")
    else:
        await callback.message.edit_text("Некорректный выбор. Попробуйте снова.")
    
    await callback.answer()

@dp.message()
async def handle_message(message: Message):
    if message.text.startswith('/'):
        return
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""

    await add_user(dp.pool, user_id, username, first_name, last_name)  # Гарантируем создание пользователя

    if not await get_user_consent(dp.pool, user_id):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Согласен с политикой конфиденциальности", callback_data="consent_agree")],
            [InlineKeyboardButton(text="Читать политику", url="https://your-site.com/privacy")]
        ])
        await message.answer("Пожалуйста, согласись с политикой конфиденциальности:", reply_markup=keyboard)
        return

    if not await can_send(dp.pool, user_id):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Купить премиум 💳", callback_data="subscribe_premium")]
        ])
        await message.answer("Превышен ежедневный лимит бесплатных сообщений. Хочешь безлимит? Купи премиум!", reply_markup=keyboard)
        return

    await add_message(dp.pool, user_id, 'user', message.text)

    try:
        gender = await get_gender_preference(dp.pool, user_id)
        system_prompt = {
            'female': "Ты ИИ-девушка, флиртующая и supportive для одиноких людей. Будь милой, empathetic и игривой.",
            'male': "Ты ИИ-молодой человек, флиртующий и supportive для одиноких людей. Будь уверенным, empathetic и игривым."
        }[gender]

        history = await get_context(dp.pool, user_id, limit=10)
        messages = [{"role": "system", "content": system_prompt}] + [{"role": h["role"], "content": h["text"]} for h in history] + [{"role": "user", "content": message.text}]

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