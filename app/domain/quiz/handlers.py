from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from shared.constants import BotCommands
from shared.decorators import error_decorator

from .keyboards import get_quiz_start_keyboard
from .messages import get_quiz_start_text

router = Router()


@router.message(Command(commands=[BotCommands.QUIZ]))
@error_decorator
async def start_quiz(
    message: Message,
    # second argument state: FSMContext
):
    print(f"🎯 Quiz handler called for user {message.from_user.id}")
    try:
        await message.answer(text=get_quiz_start_text(), reply_markup=get_quiz_start_keyboard())
        print(f"✅ Quiz message sent to user {message.from_user.id}")
    except Exception as e:
        print(f"❌ Error sending quiz message: {e}")
