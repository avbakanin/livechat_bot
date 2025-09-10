import logging
from domain.user.keyboards import get_consent_given_keyboard, get_consent_keyboard, get_gender_change_confirmation_keyboard, get_gender_keyboard, get_help_keyboard, get_privacy_info_keyboard
from shared.keyboards.keyboards import get_consent_given_text, get_help_text, get_limit_exceeded_keyboard, get_premium_info_keyboard, get_premium_info_text, get_privacy_info_text
import asyncpg
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatAction
from typing import Union, List, Dict
from openai import AsyncOpenAI

from services import add_user, add_message, get_context, get_gender_preference, set_gender_preference, can_send, get_user_consent, set_user_consent, delete_user_messages

from shared.helpers import destructure_user

from shared.middlewares.middlewares import AccessMiddleware

router = Router()

# allow only specific Telegram user IDs
router.message.middleware(AccessMiddleware(allowed_ids={627875032, 1512454100}))
router.callback_query.middleware(AccessMiddleware(allowed_ids={627875032, 1512454100}))

# Types to arguments
# pool: asyncpg.Pool, client: AsyncOpenAI

@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, pool: asyncpg.Pool):
    user_id, username, first_name, last_name = destructure_user(message.from_user)
    await add_user(pool, user_id, username, first_name, last_name)
    
    consent = await get_user_consent(pool, user_id)
    # Разрешаем /start только при первом запуске (пока нет согласия)
    if consent:
        await message.answer("Бот уже запущен - просто напиши сообщение 😊")
        return
    if not consent:
        await message.answer(
            "Пожалуйста, согласись с политикой конфиденциальности:",
            reply_markup=get_consent_keyboard()
        )
        return
    
    # Первый запуск: показали клавиатуру согласия выше и выходим

# GENDER handlers
@router.message(Command(commands=["choose_gender"]))
async def cmd_choose_gender(message: Message, pool: asyncpg.Pool):
    user_id, username, first_name, last_name = destructure_user(message.from_user)
    await add_user(pool, user_id, username, first_name, last_name)
    
    # Check if gender is already set
    current_gender = await get_gender_preference(pool, user_id)
    if current_gender and current_gender != 'female':  # 'female' is default, so if it's not default, it was set
        await message.answer(
            "⚠️ Вы уверены, что хотите сменить пол компаньона?\n\n"
            "Вся история переписки будет удалена!",
            reply_markup=get_gender_change_confirmation_keyboard()
        )
    else:
        await message.answer(
            "Выбери пол компаньона:",
            reply_markup=get_gender_keyboard()
        )

@router.callback_query(F.data.in_(["gender_female", "gender_male"]))
async def gender_choice(callback: CallbackQuery, pool: asyncpg.Pool):
    user = callback.from_user
    preference = "female" if callback.data == "gender_female" else "male"
    
    try:
        await set_gender_preference(pool, user.id, preference)
        response_text = "девушку 😊" if preference == "female" else "молодого человека 😉"
        await callback.message.edit_text(f"Пол компаньона изменен на {response_text}.")
    except Exception as e:
        logging.error(f"Error setting gender_preference: {e}")
        await callback.message.edit_text("Произошла ошибка. Попробуйте снова.")
    await callback.answer()

@router.callback_query(F.data == "gender_change_confirm")
async def gender_change_confirm(callback: CallbackQuery, pool: asyncpg.Pool):
    user = callback.from_user
    
    try:
        # Delete all user messages
        await delete_user_messages(pool, user.id)
        
        # Show gender selection
        await callback.message.edit_text(
            "История переписки удалена. Выбери пол компаньона:",
            reply_markup=get_gender_keyboard()
        )
    except Exception as e:
        logging.error(f"Error in gender change confirmation: {e}")
        await callback.message.edit_text("Произошла ошибка. Попробуйте снова.")
    await callback.answer()

@router.callback_query(F.data == "gender_change_cancel")
async def gender_change_cancel(callback: CallbackQuery):
    await callback.message.edit_text("Смена пола отменена. Можете продолжить общение.")
    await callback.answer()

@router.callback_query(F.data == "choose_gender_help")
async def gender_help(callback: CallbackQuery):
    await callback.message.edit_text("Выбери пол компаньона для общения:", reply_markup=get_gender_keyboard())
    await callback.answer()

# PREMIUM handlers
@router.callback_query(F.data == "subscribe_premium")
async def premium_subscribe(callback: CallbackQuery):
    await callback.message.edit_text("Функция оплаты временно недоступна. Попробуйте позже.")
    await callback.answer()

# HELP handlers
@router.message(Command(commands=["help"]))
async def cmd_help(message: Message, pool: asyncpg.Pool):
    user_id, username, first_name, last_name = destructure_user(message.from_user)
    await add_user(pool, user_id, username, first_name, last_name)
    
    await message.answer(
        get_help_text(),
        reply_markup=get_help_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "premium_info_help")
async def premium_info(callback: CallbackQuery):
    await callback.message.edit_text(get_premium_info_text(), reply_markup=get_premium_info_keyboard(), parse_mode="HTML")
    await callback.answer()

# CONSENT handlers
@router.callback_query(F.data == "consent_agree")
async def consent_agree(callback: CallbackQuery, pool):
    user = callback.from_user
    await add_user(pool, user.id, user.username, user.first_name, user.last_name)
    
    try:
        await set_user_consent(pool, user.id, True)
        await callback.message.edit_text(get_consent_given_text(), reply_markup=get_consent_given_keyboard())
    except Exception as e:
        logging.error(f"Error setting consent: {e}")
        await callback.message.edit_text("Произошла ошибка. Попробуйте снова.")
    await callback.answer()

@router.callback_query(F.data == "privacy_info_help")
async def privacy_info(callback: CallbackQuery):
    await callback.message.edit_text(get_privacy_info_text(), reply_markup=get_privacy_info_keyboard(), parse_mode="HTML")
    await callback.answer()

# shared
@router.callback_query(F.data == "back_to_help")
async def back_to_help(callback: CallbackQuery):
    await callback.message.edit_text(get_help_text(), reply_markup=get_help_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.message()
async def handle_message(message: Message, pool: asyncpg.Pool, client: AsyncOpenAI, bot):
    if message.text.startswith('/'):
        return
        
    user_id, username, first_name, last_name = destructure_user(message.from_user)
    await add_user(pool, user_id, username, first_name, last_name)

    if not await get_user_consent(pool, user_id):
        await message.answer(
            "Пожалуйста, согласись с политикой конфиденциальности:",
            reply_markup=get_consent_keyboard()
        )
        return

    if not await can_send(pool, user_id):
        await message.answer(
            "Превышен ежедневный лимит бесплатных сообщений. Хочешь безлимит? Купи премиум!",
            reply_markup=get_limit_exceeded_keyboard()
        )
        return

    await add_message(pool, user_id, 'user', message.text)
    
    # Show typing status
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    
    try:
        gender = await get_gender_preference(pool, user_id)
        system_prompt = {
            'female': "Ты ИИ-девушка, флиртующая и supportive для одиноких людей. Будь милой, empathetic и игривой.",
            'male': "Ты ИИ-молодой человек, флиртующий и supportive для одиноких людей. Будь уверенным, empathetic и игривым."
        }[gender]

        history = await get_context(pool, user_id, limit=10)
        messages = [{"role": "system", "content": system_prompt}] + [{"role": h["role"], "content": h["text"]} for h in history] + [{"role": "user", "content": message.text}]

        answer = await get_openapi_response(messages=messages, client=client)
    except Exception as e:
        answer = f"Ошибка: {e}"
        logging.error(f"OpenAI error: {e}")

    await add_message(pool, user_id, 'assistant', answer)
    await message.answer(answer)


# Вынести в другой файл, хелперы?
async def get_openapi_response(messages: List[Dict[str, Union[str, None]]], client: AsyncOpenAI) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=1000  # Используй старый параметр
        # max_completion_tokens=1000  # Изменилось название параметра
        # max_completion_tokens=1000
    )

    return response.choices[0].message.content.strip() or "OpenAI вернул пустой ответ."


@router.message(Command(commands=["privacy"]))
async def privacy_policy(message: Message):
    text = (
        "🔐 <b>Политика конфиденциальности</b>\n\n"
        "Здесь ваш текст политики конфиденциальности...\n\n"
        "Полная версия: https://yourwebsite.com/privacy"
    )
    await message.answer(text)
