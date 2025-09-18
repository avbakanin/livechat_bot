import asyncio
import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from domain.user.constants import Callbacks
from domain.user.decorators import error_decorator
from shared.constants.config import LANGUAGE_NAMES
from domain.user.keyboards import (
    get_consent_given_keyboard,
    get_gender_keyboard,
    get_help_keyboard,
    get_privacy_info_keyboard,
)
from domain.user.messages import (
    get_consent_given_text,
    get_format_clean_metrics_response,
    get_format_reset_daily_metrics_response,
)
from domain.user.services_cached import UserService
from shared.decorators import optimize_callback_edit
from shared.i18n import i18n
from shared.keyboards.language import get_language_keyboard_with_current
from shared.messages.common import get_help_text, get_privacy_info_text
from shared.metrics.metrics import (
    safe_record_security_metric,
    safe_record_user_interaction,
)
from shared.middlewares.i18n_middleware import I18nMiddleware
from shared.middlewares.middlewares import AccessMiddleware

router = Router()

router.message.middleware(AccessMiddleware(allowed_ids={627875032, 1512454100}))
router.callback_query.middleware(AccessMiddleware(allowed_ids={627875032, 1512454100}))


@router.callback_query(F.data.in_([Callbacks.GENDER_FEMALE, Callbacks.GENDER_MALE]))
@error_decorator
async def gender_choice(
    callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware
):
    user = callback.from_user
    preference = "female" if callback.data == "gender_female" else "male"

    safe_record_security_metric("record_callback_query")

    current_gender = await user_service.get_gender_preference(user.id)
    is_first_selection = current_gender is None

    await user_service.set_gender_preference(user.id, preference)

    gender_name = (
        i18n.t("buttons.female") if preference == "female" else i18n.t("buttons.male")
    )

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
        text=i18n.t("gender.change_confirmed"), reply_markup=get_gender_keyboard(i18n)
    )
    await callback.answer()


@router.callback_query(F.data == Callbacks.GENDER_CHANGE_CANCEL)
@error_decorator
async def gender_change_cancel(callback: CallbackQuery, i18n: I18nMiddleware):
    await callback.message.edit_text(text=i18n.t("gender.change_cancelled"))
    await callback.answer()


@router.callback_query(F.data == "consent_agree")
@error_decorator
async def consent_agree(
    callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware
):
    user = callback.from_user

    await user_service.add_user(user.id, user.username, user.first_name, user.last_name)

    await user_service.set_consent_status(user.id, True)
    await callback.message.edit_text(
        get_consent_given_text(), reply_markup=get_consent_given_keyboard(i18n)
    )
    await callback.answer()


@router.callback_query(F.data == Callbacks.PRIVACY_INFO_HELP)
@error_decorator
async def privacy_info(callback: CallbackQuery):
    await callback.message.edit_text(
        text=get_privacy_info_text(),
        reply_markup=get_privacy_info_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == Callbacks.BACK_TO_HELP)
@error_decorator
async def back_to_help(callback: CallbackQuery):
    await callback.message.edit_text(
        text=get_help_text(), reply_markup=get_help_keyboard(), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith(Callbacks.LANG_PREFIX))
@error_decorator
async def handle_language_selection(callback: CallbackQuery, **kwargs):
    language_code = callback.data.split("_")[1]

    available_languages = i18n.get_available_languages()
    if language_code not in available_languages:
        await callback.answer("❌ Неподдерживаемый язык", show_alert=True)
        return

    i18n.set_language(language_code)

    user_id = callback.from_user.id
    try:
        from services.user.user import user_service

        pool = kwargs.get("pool")
        if pool:
            await user_service.update_user(
                pool=pool, user_id=user_id, language=language_code
            )
            logging.info(
                f"Saved language preference '{language_code}' for user {user_id}"
            )
        else:
            logging.warning(
                f"No database pool available to save language for user {user_id}"
            )
    except Exception as e:
        logging.warning(f"Failed to save language preference for user {user_id}: {e}")

    language_name = LANGUAGE_NAMES.get(language_code, language_code.upper())

    success_text = i18n.t("commands.language.changed", language=language_name)
    await callback.message.edit_text(
        text=success_text,
        reply_markup=get_language_keyboard_with_current(language_code),
        parse_mode="HTML",
    )

    await callback.answer(
        text=i18n.t("commands.language.changed", language=language_name)
    )

    async def delete_message():
        await asyncio.sleep(2)
        try:
            await callback.message.delete()
        except Exception as e:
            logging.warning(f"Failed to delete language change message: {e}")

    asyncio.create_task(delete_message())

    safe_record_user_interaction(
        callback.from_user.id, f"language_changed_{language_code}"
    )


@router.message(F.text == Callbacks.CLEAN_METRICS)
@error_decorator
async def cmd_clean_metrics(message: Message, user_service: UserService):
    from shared.metrics.metrics import metrics_collector

    if metrics_collector is None:
        await message.answer(
            "❌ Metrics system not initialized yet. Please try again later."
        )
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

    response = get_format_clean_metrics_response(
        removed_count, cleaned_ids, real_user_ids
    )
    await message.answer(response)


@router.message(F.text == Callbacks.RESET_DAILY_METRICS)
@error_decorator
async def cmd_reset_daily_metrics(message: Message):
    from shared.metrics.metrics import metrics_collector

    if metrics_collector is None:
        await message.answer(
            "❌ Metrics system not initialized yet. Please try again later."
        )
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

    current_language_name = LANGUAGE_NAMES.get(
        current_language, current_language.upper()
    )

    title = i18n.t("commands.language.title")
    description = i18n.t("commands.language.description")
    current_text = i18n.t("commands.language.current", language=current_language_name)

    text = f"{title}\n\n{description}\n{current_text}"

    keyboard = get_language_keyboard_with_current(current_language)

    await callback.message.edit_text(
        text=text, reply_markup=keyboard, parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == Callbacks.CHOOSE_GENDER_HELP)
@error_decorator
async def gender_help(callback: CallbackQuery):
    await callback.message.edit_text(
        text=i18n.t("buttons.choose_gender_help"),
        reply_markup=get_gender_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == Callbacks.RESTART_CONFIRM)
@optimize_callback_edit
@error_decorator
async def restart_confirm(callback: CallbackQuery, user_service: UserService):
    user_id = callback.from_user.id

    await user_service.restart_user_state(user_id)

    await callback.message.edit_text(
        i18n.t("commands.restart.success"), parse_mode="HTML"
    )

    await asyncio.sleep(2)
    await callback.message.answer(
        text=i18n.t("gender.choose_gender"),
        reply_markup=get_gender_keyboard(),
        parse_mode="HTML",
    )

    await callback.answer()


@router.callback_query(F.data == Callbacks.RESTART_CANCEL)
@error_decorator
async def restart_cancel(callback: CallbackQuery):
    await callback.message.edit_text(
        text=get_help_text(),
        reply_markup=get_help_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer(text=i18n.t("commands.restart.cancelled"))


@router.callback_query(F.data == Callbacks.STOP_CONFIRM)
@optimize_callback_edit
@error_decorator
async def stop_confirm(callback: CallbackQuery, user_service: UserService):
    user_id = callback.from_user.id

    await user_service.reset_user_state(user_id)

    await callback.message.edit_text(
        text=i18n.t("commands.stop.success"), parse_mode="HTML"
    )

    await callback.answer()


@router.callback_query(F.data == Callbacks.STOP_CANCEL)
@error_decorator
async def stop_cancel(callback: CallbackQuery):
    await callback.message.edit_text(
        text=get_help_text(),
        reply_markup=get_help_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer(text=i18n.t("commands.stop.cancelled"))
