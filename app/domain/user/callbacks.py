import asyncio

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from domain.subscription.keyboards import get_premium_info_keyboard
from domain.subscription.messages import get_premium_info_text


from shared.constants import LANGUAGE_NAMES, Callbacks
from shared.decorators import error_decorator
from shared.i18n import i18n
from shared.keyboards.language import get_language_keyboard_with_current
from shared.messages.common import get_help_text, get_privacy_info_text
from shared.middlewares.i18n_middleware import I18nMiddleware
from shared.metrics.metrics import (
    safe_record_security_metric,
    safe_record_user_interaction,
)
from shared.utils.logger import get_logger

from .keyboards import (
    get_command_already_executed_keyboard,
    get_consent_given_keyboard,
    get_gender_keyboard,
    get_help_keyboard,
    get_privacy_info_keyboard,
)
from .services_cached import UserService
from .messages import (
    get_consent_given_text,
    get_format_clean_metrics_response,
    get_format_reset_daily_metrics_response,
)

router = Router()


@router.callback_query(F.data.in_([Callbacks.GENDER_FEMALE, Callbacks.GENDER_MALE]))
@error_decorator
async def gender_choice(callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware):
    user = callback.from_user
    preference = "female" if callback.data == "gender_female" else "male"

    safe_record_security_metric("record_callback_query")

    current_gender = await user_service.get_gender_preference(user.id)
    is_first_selection = current_gender is None

    await user_service.set_gender_preference(user.id, preference)

    gender_name = i18n.t("buttons.female") if preference == "female" else i18n.t("buttons.male")

    if is_first_selection:
        message_text = i18n.t("gender.gender_selected", gender=gender_name)
    else:
        message_text = i18n.t("gender.toggle_gender", gender=gender_name)

    await callback.message.edit_text(message_text)
    await callback.answer()


@router.callback_query(F.data == Callbacks.GENDER_CHANGE_CONFIRM)
@error_decorator
async def gender_change_confirm(
    callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware
):
    user = callback.from_user

    await user_service.delete_user_messages(user.id)

    await callback.message.edit_text(
        text=i18n.t("gender.change_confirmed"), reply_markup=get_gender_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == Callbacks.GENDER_CHANGE_CANCEL)
@error_decorator
async def gender_change_cancel(callback: CallbackQuery, i18n: I18nMiddleware):
    await callback.message.edit_text(text=i18n.t("gender.change_cancelled"))
    await callback.answer()


@router.callback_query(F.data == "consent_agree")
@error_decorator
async def consent_agree(callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware):
    user = callback.from_user

    await user_service.add_user(user.id, user.username, user.first_name, user.last_name)

    await user_service.set_consent_status(user.id, True)
    await callback.message.edit_text(
        get_consent_given_text(), reply_markup=get_consent_given_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == Callbacks.PRIVACY_INFO_HELP)
@error_decorator
async def privacy_info(callback: CallbackQuery, i18n: I18nMiddleware):
    await callback.message.edit_text(
        text=get_privacy_info_text(),
        reply_markup=get_privacy_info_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == Callbacks.PREMIUM_INFO_HELP)
@error_decorator
async def premium_info(callback: CallbackQuery, i18n: I18nMiddleware):
    await callback.message.edit_text(
        text=get_premium_info_text(),
        reply_markup=get_premium_info_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == Callbacks.BACK_TO_HELP)
@error_decorator
async def back_to_help(callback: CallbackQuery, i18n: I18nMiddleware):
    await callback.message.edit_text(
        text=get_help_text(), reply_markup=get_help_keyboard(), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith(Callbacks.LANG_PREFIX))
@error_decorator
async def handle_language_selection(callback: CallbackQuery, user_service: UserService, **kwargs):
    language_code = callback.data.split("_")[1]

    available_languages = i18n.get_available_languages()
    if language_code not in available_languages:
        await callback.answer("❌ Неподдерживаемый язык", show_alert=True)
        return

    user_id = callback.from_user.id
    
    # Save language to database
    logger = get_logger("language_selection")
    try:
        await user_service.set_language(user_id, language_code)
        logger.info(f"Language saved to database for user {user_id}: {language_code}")
    except Exception as e:
        logger.error(f"Failed to save language for user {user_id}: {e}")
        await callback.answer("❌ Ошибка сохранения языка", show_alert=True)
        return

    # Set language for current session
    i18n.set_language(language_code)

    language_name = LANGUAGE_NAMES.get(language_code, language_code.upper())

    success_text = i18n.t("commands.language.changed", language=language_name)
    await callback.message.edit_text(
        text=success_text,
        reply_markup=get_language_keyboard_with_current(language_code),
        parse_mode="HTML",
    )

    await callback.answer(text=i18n.t("commands.language.changed", language=language_name))

    async def delete_message():
        await asyncio.sleep(2)
        try:
            await callback.message.delete()
        except Exception as e:
            logger.warning(f"Failed to delete language change message: {e}")

    asyncio.create_task(delete_message())

    safe_record_user_interaction(callback.from_user.id, f"language_changed_{language_code}")


@router.message(F.text == Callbacks.CLEAN_METRICS)
@error_decorator
async def cmd_clean_metrics(message: Message, user_service: UserService):
    from shared.metrics.metrics import metrics_collector

    if metrics_collector is None:
        await message.answer("❌ Metrics system not initialized yet. Please try again later.")
        return

    async with user_service.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id FROM users")
        real_user_ids = {row["id"] for row in rows}

    if not real_user_ids:
        await message.answer("❌ No real users found in database!")
        return

    current_daily_ids = metrics_collector.metrics.daily_user_ids.copy()
    cleaned_ids = current_daily_ids.intersection(real_user_ids)
    removed_count = len(current_daily_ids) - len(cleaned_ids)

    if removed_count > 0:
        metrics_collector.metrics.daily_user_ids = cleaned_ids
        metrics_collector.metrics.unique_active_users_today = len(cleaned_ids)
        await metrics_collector.save_to_database()

    response = get_format_clean_metrics_response(removed_count, cleaned_ids, real_user_ids)
    await message.answer(response)


@router.message(F.text == Callbacks.RESET_DAILY_METRICS)
@error_decorator
async def cmd_reset_daily_metrics(message: Message):
    from shared.metrics.metrics import metrics_collector

    if metrics_collector is None:
        await message.answer("❌ Metrics system not initialized yet. Please try again later.")
        return

    # Список полей метрик для обнуления
    daily_metric_fields = [
        "total_interactions_today",
        "unique_active_users_today",
        "new_users_today",
        "messages_sent_today",
        "commands_used_today",
        "ai_responses_sent_today",
        "callback_queries_today",
        "premium_users_active_today",
    ]

    for metric_field in daily_metric_fields:
        setattr(metrics_collector.metrics, metric_field, 0)

    metrics_collector.metrics.daily_user_ids.clear()

    await metrics_collector.save_to_database()

    response = get_format_reset_daily_metrics_response()
    await message.answer(response)


@router.callback_query(F.data == Callbacks.CHOOSE_LANGUAGE)
@error_decorator
async def choose_language_help(callback: CallbackQuery):
    current_language = i18n.get_language()

    current_language_name = LANGUAGE_NAMES.get(current_language, current_language.upper())

    title = i18n.t("commands.language.title")
    description = i18n.t("commands.language.description")
    current_text = i18n.t("commands.language.current", language=current_language_name)

    text = f"{title}\n\n{description}\n{current_text}"

    keyboard = get_language_keyboard_with_current(current_language)

    await callback.message.edit_text(text=text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == Callbacks.CHOOSE_GENDER_HELP)
@error_decorator
async def gender_help(callback: CallbackQuery, i18n: I18nMiddleware):
    await callback.message.edit_text(
        text=i18n.t("buttons.choose_gender_help"),
        reply_markup=get_gender_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == Callbacks.RESTART_CONFIRM)
@error_decorator
async def restart_confirm(callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware):
    user_id = callback.from_user.id

    # Check if bot is already restarted
    from shared.fsm.user_cache import user_cache
    cached_data = await user_cache.get(user_id)
    if cached_data and cached_data.is_restarted:
        await callback.message.edit_text(
            i18n.t("commands.restart.already_restarted"),
            reply_markup=get_command_already_executed_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    await user_service.restart_user_state(user_id)

    # Update cache to mark as restarted
    if cached_data:
        cached_data.is_restarted = True
        cached_data.is_stopped = False  # Reset stop state
        await user_cache.set(user_id, cached_data)

    await callback.message.edit_text(i18n.t("commands.restart.success"), parse_mode="HTML")

    await asyncio.sleep(2)
    await callback.message.answer(
        text=i18n.t("gender.choose_gender"),
        reply_markup=get_gender_keyboard(),
        parse_mode="HTML",
    )

    await callback.answer()


@router.callback_query(F.data == Callbacks.RESTART_CANCEL)
@error_decorator
async def restart_cancel(callback: CallbackQuery, i18n: I18nMiddleware):
    await callback.message.edit_text(
        text=get_help_text(),
        reply_markup=get_help_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer(text=i18n.t("commands.restart.cancelled"))


@router.callback_query(F.data == Callbacks.DELETE_ME_CONFIRM)
@error_decorator
async def delete_me_confirm(callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware):
    user_id = callback.from_user.id

    # Check if bot is already stopped
    from shared.fsm.user_cache import user_cache
    cached_data = await user_cache.get(user_id)
    if cached_data and cached_data.is_stopped:
        await callback.message.edit_text(
            i18n.t("commands.delete_me.already_stopped"),
            reply_markup=get_command_already_executed_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    # Update cache to mark as stopped BEFORE deleting user
    if cached_data:
        cached_data.is_stopped = True
        cached_data.is_restarted = False  # Reset restart state
        await user_cache.set(user_id, cached_data)

    await user_service.reset_user_state(user_id)

    await callback.message.edit_text(text=i18n.t("commands.delete_me.success"), parse_mode="HTML")

    await callback.answer()


@router.callback_query(F.data == Callbacks.DELETE_ME_CANCEL)
@error_decorator
async def delete_me_cancel(callback: CallbackQuery, i18n: I18nMiddleware):
    await callback.message.edit_text(
        text=get_help_text(),
        reply_markup=get_help_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer(text=i18n.t("commands.delete_me.cancelled"))


@router.callback_query(F.data == Callbacks.BUY_PREMIUM)
@error_decorator
async def buy_premium(callback: CallbackQuery, i18n: I18nMiddleware):
    """Обработчик кнопки 'Купить премиум'."""
    await callback.message.edit_text(
        text=get_premium_info_text(),
        reply_markup=get_premium_info_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()
