"""
User domain handlers - Telegram bot handlers.
"""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatAction

from shared.models.user import UserCreate
from domain.user.services import UserService
from domain.user.keyboards import (
    get_consent_keyboard,
    get_consent_given_keyboard,
    get_gender_keyboard,
    get_gender_change_confirmation_keyboard
)
from domain.user.messages import (
    get_consent_given_text,
    get_gender_change_warning_text,
    get_gender_selection_text
)
from domain.subscription.keyboards import get_premium_info_keyboard
from domain.subscription.messages import get_premium_info_text
from shared.messages.common import get_help_text, get_privacy_info_text
from shared.keyboards.common import get_back_keyboard
from shared.utils.helpers import destructure_user
from core.exceptions import UserException


router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, user_service: UserService):
    """Handle /start command."""
    user_id, username, first_name, last_name = destructure_user(message.from_user)
    
    # Add user to database
    await user_service.add_user(user_id, username, first_name, last_name)
    
    # Check consent status
    consent = await user_service.get_consent_status(user_id)
    
    if consent:
        await message.answer("Бот уже запущен - просто напиши сообщение 😊")
        return
    
    # Show consent keyboard
    await message.answer(
        "Пожалуйста, согласись с политикой конфиденциальности:",
        reply_markup=get_consent_keyboard()
    )


@router.message(Command(commands=["choose_gender"]))
async def cmd_choose_gender(message: Message, user_service: UserService):
    """Handle /choose_gender command."""
    user_id, username, first_name, last_name = destructure_user(message.from_user)
    
    # Add user to database
    await user_service.add_user(user_id, username, first_name, last_name)
    
    # Check current gender preference
    current_gender = await user_service.get_gender_preference(user_id)
    
    if current_gender and current_gender != 'female':  # 'female' is default
        await message.answer(
            get_gender_change_warning_text(),
            reply_markup=get_gender_change_confirmation_keyboard()
        )
    else:
        await message.answer(
            get_gender_selection_text(),
            reply_markup=get_gender_keyboard()
        )


@router.callback_query(F.data.in_(["gender_female", "gender_male"]))
async def gender_choice(callback: CallbackQuery, user_service: UserService):
    """Handle gender selection."""
    user = callback.from_user
    preference = "female" if callback.data == "gender_female" else "male"
    
    try:
        await user_service.set_gender_preference(user.id, preference)
        response_text = "девушку 😊" if preference == "female" else "молодого человека 😉"
        await callback.message.edit_text(f"Пол компаньона изменен на {response_text}.")
    except UserException as e:
        logging.error(f"Error setting gender preference: {e}")
        await callback.message.edit_text("Произошла ошибка. Попробуйте снова.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        await callback.message.edit_text("Произошла ошибка. Попробуйте снова.")
    
    await callback.answer()


@router.callback_query(F.data == "gender_change_confirm")
async def gender_change_confirm(callback: CallbackQuery, user_service: UserService):
    """Handle gender change confirmation."""
    user = callback.from_user
    
    try:
        # This would need to be implemented with message service
        # await message_service.delete_user_messages(user.id)
        
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
    """Handle gender change cancellation."""
    await callback.message.edit_text("Смена пола отменена. Можете продолжить общение.")
    await callback.answer()


@router.callback_query(F.data == "consent_agree")
async def consent_agree(callback: CallbackQuery, user_service: UserService):
    """Handle consent agreement."""
    user = callback.from_user
    
    # Add user to database
    await user_service.add_user(user.id, user.username, user.first_name, user.last_name)
    
    try:
        await user_service.set_consent_status(user.id, True)
        await callback.message.edit_text(
            get_consent_given_text(),
            reply_markup=get_consent_given_keyboard()
        )
    except Exception as e:
        logging.error(f"Error setting consent: {e}")
        await callback.message.edit_text("Произошла ошибка. Попробуйте снова.")
    
    await callback.answer()


@router.message(Command(commands=["help"]))
async def cmd_help(message: Message, user_service: UserService):
    """Handle /help command."""
    user_id, username, first_name, last_name = destructure_user(message.from_user)
    
    # Add user to database
    await user_service.add_user(user_id, username, first_name, last_name)
    
    await message.answer(
        get_help_text(),
        reply_markup=get_help_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command(commands=["privacy"]))
async def cmd_privacy(message: Message):
    """Handle /privacy command."""
    await message.answer(get_privacy_info_text(), parse_mode="HTML")


@router.callback_query(F.data == "premium_info_help")
async def premium_info(callback: CallbackQuery):
    """Handle premium info callback."""
    await callback.message.edit_text(
        get_premium_info_text(), 
        reply_markup=get_premium_info_keyboard(), 
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "privacy_info_help")
async def privacy_info(callback: CallbackQuery):
    """Handle privacy info callback."""
    await callback.message.edit_text(
        get_privacy_info_text(), 
        reply_markup=get_privacy_info_keyboard(), 
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_help")
async def back_to_help(callback: CallbackQuery):
    """Handle back to help callback."""
    await callback.message.edit_text(
        get_help_text(), 
        reply_markup=get_help_keyboard(), 
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "choose_gender_help")
async def gender_help(callback: CallbackQuery):
    """Handle gender help callback."""
    await callback.message.edit_text(
        "Выбери пол компаньона для общения:", 
        reply_markup=get_gender_keyboard()
    )
    await callback.answer()
