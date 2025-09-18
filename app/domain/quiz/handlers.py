from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from shared.constants import BotCommands

router = Router()


# Начало квиза
@router.message(Command(commands=[BotCommands.QUIZ]))
async def start_quiz(message: Message, state: FSMContext):
    await message.answer(
        "Привет! Давай познакомимся поближе. Я задам тебе несколько необычных вопросов, "
        "чтобы лучше понять твой характер и предпочтения. Это поможет мне общаться с тобой более осмысленно!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Начать квиз ✨", callback_data="start_quiz")]]
        ),
    )
