from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message


from domain.message.services import MessageService
from .keyboards import (
    get_command_already_executed_keyboard,
    get_consent_keyboard,
    get_gender_change_confirmation_keyboard,
    get_gender_keyboard,
    get_help_keyboard,
    get_restart_confirmation_keyboard,
    get_delete_me_confirmation_keyboard,
    get_status_keyboard,
)
from .messages import (
    get_format_metrics_summary,
    get_format_security_metrics,
)
from .services_cached import UserService

from shared.constants import LANGUAGE_NAMES, BotCommands
from shared.decorators import error_decorator
from shared.fsm.user_cache import UserCacheData
from shared.i18n import i18n
from shared.keyboards.language import get_language_keyboard_with_current
from shared.messages.common import get_help_text, get_privacy_info_text
from shared.middlewares.i18n_middleware import I18nMiddleware
from shared.metrics.metrics import (
    safe_record_metric,
    safe_record_user_interaction,
)
from shared.metrics.debug_info import get_user_debug_info

# AccessMiddleware imported in setup_routers
from shared.helpers import destructure_user


router = Router()

# AccessMiddleware now applied globally in setup_routers


@router.message(Command(commands=[BotCommands.START]))
@error_decorator
async def cmd_start(
    message: Message,
    user_service: UserService,
    i18n: I18nMiddleware,
    cached_user: UserCacheData = None,
):
    user_id, username, first_name, last_name = destructure_user(message.from_user)

    user_exists = await user_service.get_user(user_id) is not None

    await user_service.add_user(user_id, username, first_name, last_name)

    if not user_exists:
        safe_record_metric("record_new_user")

    safe_record_user_interaction(user_id, "command", user_service)

    # Reset command states when user starts bot
    if cached_user:
        cached_user.is_restarted = False
        cached_user.is_stopped = False
        from shared.fsm.user_cache import user_cache
        await user_cache.set(user_id, cached_user)

    if cached_user:
        consent = cached_user.consent_given
    else:
        consent = await user_service.get_consent_status(user_id)

    if consent:
        await message.answer(i18n.t("commands.start.already_started"))
        return

    await message.answer(i18n.t("consent.request"), reply_markup=get_consent_keyboard())


@router.message(Command(commands=[BotCommands.CHOOSE_GENDER]))
@error_decorator
async def cmd_choose_gender(
    message: Message,
    user_service: UserService,
    i18n: I18nMiddleware,
    cached_user: UserCacheData = None,
):
    user_id, username, first_name, last_name = destructure_user(message.from_user)

    await user_service.add_user(user_id, username, first_name, last_name)

    if cached_user:
        current_gender = cached_user.gender_preference
    else:
        current_gender = await user_service.get_gender_preference(user_id)

    if current_gender:
        await message.answer(
            i18n.t("gender.change_warning"),
            reply_markup=get_gender_change_confirmation_keyboard(),
        )
    else:
        await message.answer(i18n.t("gender.choose"), reply_markup=get_gender_keyboard())


@router.message(Command(commands=[BotCommands.HELP]))
@error_decorator
async def cmd_help(message: Message, user_service: UserService, i18n: I18nMiddleware):
    user_id, username, first_name, last_name = destructure_user(message.from_user)

    await user_service.add_user(user_id, username, first_name, last_name)

    # Check premium status to show appropriate button
    subscription_status = await user_service.get_subscription_status(user_id)
    subscription_expires_at = await user_service.get_subscription_expires_at(user_id)
    
    # Determine if user has active premium subscription
    is_premium = False
    if subscription_status == "premium" and subscription_expires_at:
        from shared.utils.datetime_utils import DateTimeUtils
        if not DateTimeUtils.is_expired(subscription_expires_at):
            is_premium = True

    await message.answer(
        text=get_help_text(),
        reply_markup=get_help_keyboard(is_premium=is_premium),
        parse_mode="HTML",
    )


@router.message(Command(commands=[BotCommands.PRIVACY]))
@error_decorator
async def cmd_privacy(message: Message):
    await message.answer(get_privacy_info_text(), parse_mode="HTML")


@router.message(Command(commands=["language"]))
@error_decorator
async def cmd_language(message: Message):
    current_language = i18n.get_language()

    current_language_name = LANGUAGE_NAMES.get(current_language, current_language.upper())

    title = i18n.t("commands.language.title")
    description = i18n.t("commands.language.description")
    current_text = i18n.t("commands.language.current", language=current_language_name)

    text = f"{title}\n\n{description}\n{current_text}"

    keyboard = get_language_keyboard_with_current(current_language)

    await message.answer(text=text, reply_markup=keyboard, parse_mode="HTML")

    safe_record_user_interaction(message.from_user.id, "language_command")


@router.message(Command(commands=[BotCommands.STATUS]))
@error_decorator
async def cmd_status(
    message: Message,
    message_service: MessageService,
    user_service: UserService,
    cached_user: UserCacheData = None,
):
    user_id = message.from_user.id

    # Always invalidate cache to get fresh subscription data
    await user_service.invalidate_cache(user_id)
    
    # Get fresh data from database
    subscription_status = await user_service.get_subscription_status(user_id)
    subscription_expires_at = await user_service.get_subscription_expires_at(user_id)

    if subscription_status == "premium" and subscription_expires_at:
        from shared.utils.datetime_utils import DateTimeUtils

        if not DateTimeUtils.is_expired(subscription_expires_at):
            days_remaining = DateTimeUtils.days_remaining(subscription_expires_at)
            hours_remaining = DateTimeUtils.hours_remaining(subscription_expires_at)

            if days_remaining > 0:
                premium_info = i18n.t("commands.status.premium_days", days=days_remaining)
            elif hours_remaining > 0:
                premium_info = i18n.t("commands.status.premium_hours", hours=hours_remaining)
            else:
                premium_info = i18n.t("commands.status.premium_expiring")

            await message.answer(
                f"{i18n.t('commands.status.title')}\n\n"
                f"{i18n.t('commands.status.unlimited')}\n\n"
                f"{premium_info}",
                reply_markup=get_status_keyboard(is_premium=True),
            )
            return

    from shared.constants import OPENAI_CONFIG

    daily_limit = OPENAI_CONFIG.get("FREE_MESSAGE_LIMIT", 50)

    remaining = await message_service.get_remaining_messages(user_id)
    used = daily_limit - remaining

    if remaining == 0:
        response = f"{i18n.t('commands.status.title')}\n\n{i18n.t('commands.status.used_all', total=daily_limit)}"
    else:
        response = f"{i18n.t('commands.status.title')}\n\n{i18n.t('commands.status.remaining_free', remaining=remaining, total=daily_limit)}"

    response += f"\n\n{i18n.t('commands.status.reset_info')}"
    response += f"\n\n{i18n.t('commands.status.premium_promo')}"

    await message.answer(response, reply_markup=get_status_keyboard(is_premium=False))


# ЧТО ЭТО??
_metrics_cache = {"response": None, "last_update": 0, "ttl": 30}


@router.message(Command(commands=[BotCommands.SECURITY]))
@error_decorator
async def cmd_security(message: Message):
    user_id = message.from_user.id

    # Check if user is admin (hardcoded for now)
    if user_id not in {627875032, 1512454100, 826795306, 284506756, 443852052}:
        await message.answer("Access denied.")
        return

    from shared.security import SecurityValidator

    security_validator = SecurityValidator()

    security_score = security_validator.get_user_security_score(user_id)

    response = get_format_security_metrics(security_score)

    await message.answer(response)


@router.message(Command(commands=[BotCommands.RESET_METRICS]))
@error_decorator
async def cmd_reset_metrics(message: Message):
    user_id = message.from_user.id

    if user_id not in {627875032, 1512454100, 826795306, 284506756, 443852052}:
        await message.answer("Access denied.")
        return

    from shared.metrics.metrics import metrics_collector

    if metrics_collector is None:
        await message.answer("Metrics not available.")
        return

    metrics_collector.metrics.reset_daily_metrics()

    await metrics_collector.save_to_database()

    await message.answer("✅ Daily metrics reset successfully!")


@router.message(Command(commands=[BotCommands.RESTART]))
@error_decorator
async def cmd_restart(message: Message, i18n: I18nMiddleware, cached_user: UserCacheData = None):
    user_id = message.from_user.id
    
    # Check if bot is already restarted
    if cached_user and cached_user.is_restarted:
        await message.answer(
            i18n.t("commands.restart.already_restarted"),
            reply_markup=get_command_already_executed_keyboard(),
            parse_mode="HTML",
        )
        return
    
    await message.answer(
        i18n.t("commands.restart.confirmation"),
        reply_markup=get_restart_confirmation_keyboard(),
        parse_mode="HTML",
    )


@router.message(Command(commands=[BotCommands.DELETE_ME]))
@error_decorator
async def cmd_delete_me(message: Message, i18n: I18nMiddleware, cached_user: UserCacheData = None):
    user_id = message.from_user.id
    
    # Check if bot is already stopped
    if cached_user and cached_user.is_stopped:
        await message.answer(
            i18n.t("commands.delete_me.already_stopped"),
            reply_markup=get_command_already_executed_keyboard(),
            parse_mode="HTML",
        )
        return
    
    await message.answer(
        i18n.t("commands.delete_me.confirmation"),
        reply_markup=get_delete_me_confirmation_keyboard(),
        parse_mode="HTML",
    )


@router.message(Command(commands=[BotCommands.METRICS]))
@error_decorator
async def cmd_metrics(message: Message):
    user_id = message.from_user.id

    if user_id not in {627875032, 1512454100, 826795306, 284506756, 443852052}:
        await message.answer("Access denied.")
        return

    from shared.metrics.metrics import metrics_collector

    if metrics_collector is None:
        await message.answer("Metrics not available.")
        return

    import time

    current_time = time.time()
    if (
        _metrics_cache["response"]
        and (current_time - _metrics_cache["last_update"]) < _metrics_cache["ttl"]
    ):
        await message.answer(_metrics_cache["response"])
        return

    metrics_summary = metrics_collector.get_metrics_summary()

    response = get_format_metrics_summary(metrics_summary, metrics_collector)

    _metrics_cache["response"] = response
    _metrics_cache["last_update"] = current_time

    await message.answer(response)


@router.message(Command(commands=["debug_user"]))
@error_decorator
async def cmd_debug_user(
    message: Message,
    user_service: UserService,
    i18n: I18nMiddleware,
    cached_user: UserCacheData = None,
):
    """Debug user data - admin command."""
    user_id = message.from_user.id
    
    # Only allow for specific user (admin)
    if user_id != 627875032:
        await message.answer("❌ Доступ запрещен")
        return
    
    try:
        # Get user from database
        user = await user_service.get_user(user_id)
        
        # Generate debug info using the new module
        debug_info = get_user_debug_info(user_id, user, cached_user)
        
        await message.answer(debug_info)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении данных: {e}")


@router.message(Command(commands=[BotCommands.CLEAR_CACHE]))
@error_decorator
async def cmd_clear_cache(
    message: Message,
    user_service: UserService,
    i18n: I18nMiddleware,
    cached_user: UserCacheData = None,
):
    """Clear user cache - admin command for debugging."""
    user_id = message.from_user.id
    
    # Only allow for specific user (admin)
    if user_id != 627875032:
        await message.answer("❌ Доступ запрещен")
        return
    
    try:
        # Clear cache for this user
        await user_service.invalidate_cache(user_id)
        
        await message.answer(
            f"✅ Кэш пользователя {user_id} очищен!\n\n"
            "Теперь попробуйте команду /status"
        )
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при очистке кэша: {e}")