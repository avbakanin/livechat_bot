import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from domain.message.services import MessageService
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
from domain.user.messages import get_consent_given_text
from domain.user.services_cached import UserService
from shared.fsm.user_cache import UserCacheData
from shared.messages.common import get_help_text, get_privacy_info_text
from shared.metrics.metrics import safe_record_metric, safe_record_user_interaction
from shared.middlewares.i18n_middleware import I18nMiddleware
from shared.middlewares.middlewares import AccessMiddleware
from shared.utils.helpers import destructure_user

from core.exceptions import UserException

router = Router()

router.message.middleware(AccessMiddleware(allowed_ids={627875032, 1512454100}))
router.callback_query.middleware(AccessMiddleware(allowed_ids={627875032, 1512454100}))


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, user_service: UserService, i18n: I18nMiddleware, cached_user: UserCacheData = None):
    user_id, username, first_name, last_name = destructure_user(message.from_user)

    # Check if user is new before adding
    user_exists = await user_service.get_user(user_id) is not None

    await user_service.add_user(user_id, username, first_name, last_name)

    # Record new user if this is their first time
    if not user_exists:
        safe_record_metric("record_new_user")

    # Record user interaction (command)
    safe_record_user_interaction(user_id, "command")

    # Check consent using cache if available
    if cached_user:
        consent = cached_user.consent_given
    else:
        consent = await user_service.get_consent_status(user_id)

    if consent:
        await message.answer(i18n.t("commands.start.already_started"))
        return

    await message.answer(i18n.t("consent.request"), reply_markup=get_consent_keyboard(i18n))


@router.message(Command(commands=["choose_gender"]))
async def cmd_choose_gender(
    message: Message, user_service: UserService, i18n: I18nMiddleware, cached_user: UserCacheData = None
):
    user_id, username, first_name, last_name = destructure_user(message.from_user)

    # Add user to database
    await user_service.add_user(user_id, username, first_name, last_name)

    # Check current gender preference using cache if available
    if cached_user:
        current_gender = cached_user.gender_preference
    else:
        current_gender = await user_service.get_gender_preference(user_id)

    # Always show warning when changing gender (regardless of current gender)
    if current_gender:
        await message.answer(i18n.t("gender.change_warning"), reply_markup=get_gender_change_confirmation_keyboard(i18n))
    else:
        # First time choosing gender - no warning needed
        await message.answer(i18n.t("gender.choose"), reply_markup=get_gender_keyboard(i18n))


@router.callback_query(F.data.in_(["gender_female", "gender_male"]))
async def gender_choice(callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware):
    user = callback.from_user
    preference = "female" if callback.data == "gender_female" else "male"

    try:
        # change translation to dynamic i18n translations
        await user_service.set_gender_preference(user.id, preference)

        # Use translated gender names
        gender_name = i18n.t("buttons.female") if preference == "female" else i18n.t("buttons.male")
        await callback.message.edit_text(i18n.t("gender.toggle_gender", gender=gender_name))
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

        await callback.message.edit_text(i18n.t("gender.change_confirmed"), reply_markup=get_gender_keyboard(i18n))
    except Exception as e:
        logging.error(f"Error in gender change confirmation: {e}")
        await callback.message.edit_text(i18n.t("error.try_again"))

    await callback.answer()


@router.callback_query(F.data == "gender_change_cancel")
async def gender_change_cancel(callback: CallbackQuery, i18n: I18nMiddleware):
    """Handle gender change cancellation."""
    await callback.message.edit_text(i18n.t("gender.change_cancelled"))
    await callback.answer()


@router.callback_query(F.data == "consent_agree")
async def consent_agree(callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware):
    """Handle consent agreement."""
    user = callback.from_user

    await user_service.add_user(user.id, user.username, user.first_name, user.last_name)

    try:
        await user_service.set_consent_status(user.id, True)
        await callback.message.edit_text(get_consent_given_text(), reply_markup=get_consent_given_keyboard(i18n))
    except Exception as e:
        logging.error(f"Error setting consent: {e}")
        await callback.message.edit_text(i18n.t("error.try_again"))

    await callback.answer()


@router.message(Command(commands=["help"]))
async def cmd_help(message: Message, user_service: UserService, i18n: I18nMiddleware):
    user_id, username, first_name, last_name = destructure_user(message.from_user)

    # Add user to database
    await user_service.add_user(user_id, username, first_name, last_name)

    await message.answer(get_help_text(), reply_markup=get_help_keyboard(i18n), parse_mode="HTML")


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
async def back_to_help(callback: CallbackQuery, i18n: I18nMiddleware):
    """Handle back to help callback."""
    await callback.message.edit_text(get_help_text(), reply_markup=get_help_keyboard(i18n), parse_mode="HTML")
    await callback.answer()


@router.message(Command(commands=["check_messages"]))
async def cmd_check_messages(
    message: Message,
    message_service: MessageService,
    user_service: UserService,
    i18n: I18nMiddleware,
    cached_user: UserCacheData = None,
):
    """Check remaining free messages for the user."""
    user_id = message.from_user.id

    # Check if user has premium subscription
    if cached_user:
        subscription_status = cached_user.subscription_status
        subscription_expires_at = cached_user.subscription_expires_at
    else:
        subscription_status = await user_service.get_subscription_status(user_id)
        subscription_expires_at = await user_service.get_subscription_expires_at(user_id)

    # Check if premium subscription is active
    if subscription_status == "premium" and subscription_expires_at:
        from datetime import datetime

        if subscription_expires_at > datetime.utcnow():
            # User has active premium
            await message.answer(f"{i18n.t('commands.check_messages.title')}\n\n{i18n.t('commands.check_messages.unlimited')}")
            return

    # Get daily limit from config
    from config.openai import OPENAI_CONFIG

    daily_limit = OPENAI_CONFIG.get("FREE_MESSAGE_LIMIT", 100)

    # Get remaining messages
    remaining = await message_service.get_remaining_messages(user_id)
    used = daily_limit - remaining

    # Prepare response based on remaining messages
    if remaining == 0:
        response = (
            f"{i18n.t('commands.check_messages.title')}\n\n{i18n.t('commands.check_messages.used_all', total=daily_limit)}"
        )
    else:
        response = f"{i18n.t('commands.check_messages.title')}\n\n{i18n.t('commands.check_messages.remaining_free', remaining=remaining, total=daily_limit)}"

    # Add reset info
    response += f"\n\n{i18n.t('commands.check_messages.reset_info')}"

    await message.answer(response)


# Cache for metrics command (optimization for scalability)
_metrics_cache = {"response": None, "last_update": 0, "ttl": 30}  # Cache for 30 seconds


@router.message(Command(commands=["metrics"]))
async def cmd_metrics(message: Message, i18n: I18nMiddleware):
    """Show bot metrics (admin only) with caching for scalability."""
    user_id = message.from_user.id

    # Check if user is admin (hardcoded for now)
    if user_id not in {627875032, 1512454100}:
        await message.answer("Access denied.")
        return

    # Get metrics collector from global reference
    from shared.metrics.metrics import metrics_collector

    if metrics_collector is None:
        await message.answer("Metrics not available.")
        return

    # Check cache first (optimization for scalability)
    import time

    current_time = time.time()
    if _metrics_cache["response"] and (current_time - _metrics_cache["last_update"]) < _metrics_cache["ttl"]:
        await message.answer(_metrics_cache["response"])
        return

    # Generate fresh metrics
    metrics_summary = metrics_collector.get_metrics_summary()

    response = "📊 Bot Metrics\n\n"

    # System metrics
    response += f"uptime_seconds: {metrics_summary['uptime_seconds']}\n"
    response += f"uptime_hours: {metrics_summary['uptime_hours']}\n\n"

    # Daily user activity metrics (reset at midnight)
    response += f"unique_active_users_today: {metrics_summary['unique_active_users_today']}\n"
    response += f"total_interactions_today: {metrics_summary['total_interactions_today']}\n"
    response += f"messages_sent_today: {metrics_summary['messages_sent_today']}\n"
    response += f"commands_used_today: {metrics_summary['commands_used_today']}\n"
    response += f"new_users_today: {metrics_summary['new_users_today']}\n\n"

    # General metrics (accumulative, never reset)
    response += f"total_messages_processed: {metrics_summary['total_messages_processed']}\n"
    response += f"success_rate: {metrics_summary['success_rate']}\n"
    response += f"average_response_time: {metrics_summary['average_response_time']}\n"
    response += f"limit_exceeded_count: {metrics_summary['limit_exceeded_count']}\n\n"

    # Performance and error metrics (accumulative, never reset)
    response += f"cache_hit_rate: {metrics_summary['cache_hit_rate']}\n"
    response += f"openai_errors: {metrics_summary['openai_errors']}\n"
    response += f"database_errors: {metrics_summary['database_errors']}\n"
    response += f"validation_errors: {metrics_summary['validation_errors']}"

    # Update cache
    _metrics_cache["response"] = response
    _metrics_cache["last_update"] = current_time

    await message.answer(response)


@router.callback_query(F.data == "choose_gender_help")
async def gender_help(callback: CallbackQuery, i18n: I18nMiddleware):
    """Handle gender help callback."""
    await callback.message.edit_text(i18n.t("buttons.choose_gender_help"), reply_markup=get_gender_keyboard(i18n))
    await callback.answer()
