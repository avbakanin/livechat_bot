import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from domain.subscription.keyboards import get_premium_info_keyboard
from domain.subscription.messages import get_premium_info_text
from domain.user.keyboards import (
    get_consent_given_keyboard,
    get_consent_keyboard,
    get_gender_change_confirmation_keyboard,
    get_gender_keyboard,
    get_help_keyboard,
    get_privacy_info_keyboard,
)
from domain.user.messages import get_consent_given_text, get_gender_change_warning_text, get_gender_selection_text
from domain.user.services import UserService
from shared.messages.common import get_help_text, get_privacy_info_text
from shared.middlewares.i18n_middleware import I18nMiddleware
from shared.middlewares.middlewares import AccessMiddleware
from shared.utils.helpers import destructure_user

from core.exceptions import UserException

router = Router()

router.message.middleware(AccessMiddleware(allowed_ids={627875032, 1512454100}))
router.callback_query.middleware(AccessMiddleware(allowed_ids={627875032, 1512454100}))


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, user_service: UserService, i18n: I18nMiddleware):
    user_id, username, first_name, last_name = destructure_user(message.from_user)

    await user_service.add_user(user_id, username, first_name, last_name)

    consent = await user_service.get_consent_status(user_id)

    if consent:
        await message.answer(i18n.t("messages.bot_already_started"))
        return

    await message.answer(i18n.t("consent.request"), reply_markup=get_consent_keyboard())


@router.message(Command(commands=["choose_gender"]))
async def cmd_choose_gender(message: Message, user_service: UserService):
    user_id, username, first_name, last_name = destructure_user(message.from_user)

    # Add user to database
    await user_service.add_user(user_id, username, first_name, last_name)

    # Check current gender preference
    current_gender = await user_service.get_gender_preference(user_id)

    if current_gender and current_gender != "female":  # 'female' is default
        await message.answer(get_gender_change_warning_text(), reply_markup=get_gender_change_confirmation_keyboard())
    else:
        await message.answer(get_gender_selection_text(), reply_markup=get_gender_keyboard())


@router.callback_query(F.data.in_(["gender_female", "gender_male"]))
async def gender_choice(callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware):
    user = callback.from_user
    preference = "female" if callback.data == "gender_female" else "male"

    try:
        # change translation to dynamic i18n translations
        await user_service.set_gender_preference(user.id, preference)
        response_text = "девушку 😊" if preference == "female" else "молодого человека 😉"
        await callback.message.edit_text(i18n.t("gender.toggle_gender", gender=response_text))
    except UserException as e:
        logging.error(f"Error setting gender preference: {e}")
        await callback.message.edit_text(i18n.t("error.try_again"))
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        await callback.message.edit_text(i18n.t("error.try_again"))

    await callback.answer()


@router.callback_query(F.data == "gender_change_confirm")
async def gender_change_confirm(callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware):
    """Handle gender change confirmation."""
    user = callback.from_user

    try:
        # Delete all user messages
        await user_service.delete_user_messages(user.id)

        await callback.message.edit_text(i18n.t("gender.change_confirm"), reply_markup=get_gender_keyboard())
    except Exception as e:
        logging.error(f"Error in gender change confirmation: {e}")
        await callback.message.edit_text(i18n.t("error.try_again"))

    await callback.answer()


@router.callback_query(F.data == "gender_change_cancel")
async def gender_change_cancel(callback: CallbackQuery, i18n: I18nMiddleware):
    """Handle gender change cancellation."""
    await callback.message.edit_text(i18n.t("gender.change_cancel"))
    await callback.answer()


@router.callback_query(F.data == "consent_agree")
async def consent_agree(callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware):
    """Handle consent agreement."""
    user = callback.from_user

    await user_service.add_user(user.id, user.username, user.first_name, user.last_name)

    try:
        await user_service.set_consent_status(user.id, True)
        await callback.message.edit_text(get_consent_given_text(), reply_markup=get_consent_given_keyboard())
    except Exception as e:
        logging.error(f"Error setting consent: {e}")
        await callback.message.edit_text(i18n.t("error.try_again"))

    await callback.answer()


@router.message(Command(commands=["help"]))
async def cmd_help(message: Message, user_service: UserService):
    user_id, username, first_name, last_name = destructure_user(message.from_user)

    # Add user to database
    await user_service.add_user(user_id, username, first_name, last_name)

    await message.answer(get_help_text(), reply_markup=get_help_keyboard(), parse_mode="HTML")


@router.message(Command(commands=["privacy"]))
async def cmd_privacy(message: Message):
    """Handle /privacy command."""
    await message.answer(get_privacy_info_text(), parse_mode="HTML")


@router.callback_query(F.data == "premium_info_help")
async def premium_info(callback: CallbackQuery):
    """Handle premium info callback."""
    await callback.message.edit_text(get_premium_info_text(), reply_markup=get_premium_info_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "privacy_info_help")
async def privacy_info(callback: CallbackQuery):
    """Handle privacy info callback."""
    await callback.message.edit_text(get_privacy_info_text(), reply_markup=get_privacy_info_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "back_to_help")
async def back_to_help(callback: CallbackQuery):
    """Handle back to help callback."""
    await callback.message.edit_text(get_help_text(), reply_markup=get_help_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "choose_gender_help")
async def gender_help(callback: CallbackQuery, i18n: I18nMiddleware):
    """Handle gender help callback."""
    await callback.message.edit_text(i18n.t("buttons.choose_gender_help"), reply_markup=get_gender_keyboard())
    await callback.answer()
