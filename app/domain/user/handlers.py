import asyncio
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
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
    get_restart_confirmation_keyboard,
    get_stop_confirmation_keyboard,
)
from domain.user.messages import get_consent_given_text
from domain.user.services_cached import UserService
from shared.decorators import optimize_callback_edit
from shared.fsm.user_cache import UserCacheData
from shared.i18n import i18n as global_i18n
from shared.keyboards.language import get_language_keyboard_with_current
from shared.messages.common import get_help_text, get_privacy_info_text
from shared.metrics.metrics import (
    safe_record_metric,
    safe_record_security_metric,
    safe_record_user_interaction,
)
from shared.middlewares.i18n_middleware import I18nMiddleware
from shared.middlewares.middlewares import AccessMiddleware
from shared.utils.helpers import destructure_user

router = Router()

router.message.middleware(AccessMiddleware(allowed_ids={627875032, 1512454100}))
router.callback_query.middleware(AccessMiddleware(allowed_ids={627875032, 1512454100}))


@router.message(Command(commands=["start"]))
async def cmd_start(
    message: Message,
    user_service: UserService,
    i18n: I18nMiddleware,
    cached_user: UserCacheData = None,
):
    user_id, username, first_name, last_name = destructure_user(message.from_user)

    # Check if user is new before adding
    user_exists = await user_service.get_user(user_id) is not None

    await user_service.add_user(user_id, username, first_name, last_name)

    # Record new user if this is their first time
    if not user_exists:
        safe_record_metric("record_new_user")

    # Record user interaction (command)
    safe_record_user_interaction(user_id, "command", user_service)

    # Check consent using cache if available
    if cached_user:
        consent = cached_user.consent_given
    else:
        consent = await user_service.get_consent_status(user_id)

    if consent:
        await message.answer(i18n.t("commands.start.already_started"))
        return

    await message.answer(
        i18n.t("consent.request"), reply_markup=get_consent_keyboard(i18n)
    )


@router.message(Command(commands=["choose_gender"]))
async def cmd_choose_gender(
    message: Message,
    user_service: UserService,
    i18n: I18nMiddleware,
    cached_user: UserCacheData = None,
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
        await message.answer(
            i18n.t("gender.change_warning"),
            reply_markup=get_gender_change_confirmation_keyboard(i18n),
        )
    else:
        # First time choosing gender - no warning needed
        await message.answer(
            i18n.t("gender.choose"), reply_markup=get_gender_keyboard(i18n)
        )


@router.callback_query(F.data.in_(["gender_female", "gender_male"]))
async def gender_choice(
    callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware
):
    user = callback.from_user
    preference = "female" if callback.data == "gender_female" else "male"

    # Record callback query
    safe_record_security_metric("record_callback_query")

    try:
        # Check if user already had a gender preference set
        current_gender = await user_service.get_gender_preference(user.id)
        # Consider it first selection if user hasn't made a choice yet (None) or if it's the default
        is_first_selection = current_gender is None
        
        # change translation to dynamic i18n translations
        await user_service.set_gender_preference(user.id, preference)

        # Use translated gender names
        gender_name = (
            i18n.t("buttons.female")
            if preference == "female"
            else i18n.t("buttons.male")
        )
        
        # Choose appropriate message based on whether this is first selection or change
        if is_first_selection:
            message_text = i18n.t("gender.gender_selected", gender=gender_name)
        else:
            message_text = i18n.t("gender.toggle_gender", gender=gender_name)
            
        await callback.message.edit_text(message_text)
    except UserException as e:
        logging.error(f"Error setting gender preference: {e}")
        await callback.message.edit_text(i18n.t("error.try_again"))
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        await callback.message.edit_text(i18n.t("error.try_again"))

    await callback.answer()


@router.callback_query(F.data == "gender_change_confirm")
async def gender_change_confirm(
    callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware
):
    """Handle gender change confirmation."""
    user = callback.from_user

    try:
        # Delete all user messages
        await user_service.delete_user_messages(user.id)

        await callback.message.edit_text(
            i18n.t("gender.change_confirmed"), reply_markup=get_gender_keyboard(i18n)
        )
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
async def consent_agree(
    callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware
):
    """Handle consent agreement."""
    user = callback.from_user

    await user_service.add_user(user.id, user.username, user.first_name, user.last_name)

    try:
        await user_service.set_consent_status(user.id, True)
        await callback.message.edit_text(
            get_consent_given_text(), reply_markup=get_consent_given_keyboard(i18n)
        )
    except Exception as e:
        logging.error(f"Error setting consent: {e}")
        await callback.message.edit_text(i18n.t("error.try_again"))

    await callback.answer()


@router.message(Command(commands=["help"]))
async def cmd_help(message: Message, user_service: UserService, i18n: I18nMiddleware):
    user_id, username, first_name, last_name = destructure_user(message.from_user)

    # Add user to database
    await user_service.add_user(user_id, username, first_name, last_name)

    await message.answer(
        get_help_text(), reply_markup=get_help_keyboard(i18n), parse_mode="HTML"
    )


@router.message(Command(commands=["privacy"]))
async def cmd_privacy(message: Message):
    """Handle /privacy command."""
    await message.answer(get_privacy_info_text(), parse_mode="HTML")


@router.callback_query(F.data == "premium_info_help")
async def premium_info(callback: CallbackQuery):
    """Handle premium info callback with optimal performance."""
    try:
        await callback.message.edit_text(
            text=get_premium_info_text(),
            reply_markup=get_premium_info_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()
        
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            await callback.answer()
        elif "message to edit not found" in str(e).lower():
            await callback.answer("Сообщение устарело", show_alert=True)
        else:
            logging.error(f"Premium info error: {e}")
            await callback.answer("❌ Ошибка обновления", show_alert=True)


@router.callback_query(F.data == "privacy_info_help")
async def privacy_info(callback: CallbackQuery, i18n: I18nMiddleware):
    """Handle privacy info callback with optimal performance."""
    try:
        await callback.message.edit_text(
            text=get_privacy_info_text(),
            reply_markup=get_privacy_info_keyboard(i18n),
            parse_mode="HTML",
        )
        await callback.answer()
        
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            await callback.answer()
        elif "message to edit not found" in str(e).lower():
            await callback.answer("Сообщение устарело", show_alert=True)
        else:
            logging.error(f"Privacy info error: {e}")
            await callback.answer("❌ Ошибка обновления", show_alert=True)


@router.callback_query(F.data == "back_to_help")
async def back_to_help(callback: CallbackQuery, i18n: I18nMiddleware):
    """Handle back to help callback with optimal performance."""
    try:
        # Получаем контент один раз
        help_text = get_help_text()
        help_keyboard = get_help_keyboard(i18n)
        
        # Редактируем сообщение
        await callback.message.edit_text(
            text=help_text,
            reply_markup=help_keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            await callback.answer()
        elif "message to edit not found" in str(e).lower():
            await callback.answer("Сообщение устарело", show_alert=True)
        else:
            logging.error(f"Back to help error: {e}")
            await callback.answer("❌ Ошибка обновления", show_alert=True)


@router.message(Command(commands=["language"]))
async def cmd_language(message: Message, i18n: I18nMiddleware):
    """Handle /language command to change interface language."""
    try:
        # Get current language
        current_language = i18n.get_language()
        
        # Get language names for display
        language_names = {
            "ru": "Русский",
            "en": "English",
            "sr": "Српски", 
            "de": "Deutsch",
            "es": "Español"
        }
        
        current_language_name = language_names.get(current_language, current_language.upper())
        
        # Get language selection text
        title = i18n.t("commands.language.title")
        description = i18n.t("commands.language.description")
        current_text = i18n.t("commands.language.current", language=current_language_name)
        
        # Create message text
        text = f"{title}\n\n{description}\n{current_text}"
        
        # Create keyboard with current language marked
        keyboard = get_language_keyboard_with_current(current_language)
        
        # Send message
        await message.answer(
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        # Record command usage
        safe_record_user_interaction(message.from_user.id, "language_command")
        
    except Exception as e:
        logging.error(f"Error in language command: {e}")
        await message.answer(i18n.t("errors.general"))


@router.callback_query(F.data.startswith("lang_"))
async def handle_language_selection(callback: CallbackQuery, i18n: I18nMiddleware, **kwargs):
    """Handle language selection callback."""
    try:
        # Extract language code from callback data
        language_code = callback.data.split("_")[1]  # "lang_ru" -> "ru"
        
        # Validate language code
        available_languages = global_i18n.get_available_languages()
        if language_code not in available_languages:
            await callback.answer("❌ Неподдерживаемый язык", show_alert=True)
            return
        
        # Set new language
        global_i18n.set_language(language_code)
        i18n.set_language(language_code)
        
        # Save user language preference to database
        user_id = callback.from_user.id
        try:
            from services.user.user import user_service

            # Get pool from dependency injection
            pool = kwargs.get('pool')
            if pool:
                await user_service.update_user(
                    pool=pool,
                    user_id=user_id,
                    language=language_code
                )
                logging.info(f"Saved language preference '{language_code}' for user {user_id}")
            else:
                logging.warning(f"No database pool available to save language for user {user_id}")
        except Exception as e:
            logging.warning(f"Failed to save language preference for user {user_id}: {e}")
        
        # Get language name for display
        language_names = {
            "ru": "Русский",
            "en": "English",
            "sr": "Српски", 
            "de": "Deutsch",
            "es": "Español"
        }
        
        language_name = language_names.get(language_code, language_code.upper())
        
        # Send success message that will auto-delete
        success_text = i18n.t("commands.language.changed", language=language_name)
        await callback.message.edit_text(
            text=success_text,
            reply_markup=get_language_keyboard_with_current(language_code),
            parse_mode="HTML"
        )
        
        # Show checkmark with language change info and schedule message deletion
        await callback.answer(i18n.t('commands.language.changed', language=language_name))
        
        # Schedule message deletion after 2 seconds
        async def delete_message():
            await asyncio.sleep(2)
            try:
                await callback.message.delete()
            except Exception as e:
                logging.warning(f"Failed to delete language change message: {e}")
        
        # Start deletion task
        asyncio.create_task(delete_message())
        
        # Record language change
        safe_record_user_interaction(callback.from_user.id, f"language_changed_{language_code}")
        
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            await callback.answer()
        elif "message to edit not found" in str(e).lower():
            await callback.answer("Сообщение устарело", show_alert=True)
        else:
            logging.error(f"Language selection error: {e}")
            await callback.answer("❌ Ошибка обновления", show_alert=True)
    except Exception as e:
        logging.error(f"Language selection error: {e}")
        await callback.answer("❌ Ошибка обновления", show_alert=True)


@router.message(Command(commands=["status"]))
async def cmd_status(
    message: Message,
    message_service: MessageService,
    user_service: UserService,
    i18n: I18nMiddleware,
    cached_user: UserCacheData = None,
):
    """Show user status including subscription info and remaining messages."""
    user_id = message.from_user.id

    # Check if user has premium subscription
    if cached_user:
        subscription_status = cached_user.subscription_status
        subscription_expires_at = cached_user.subscription_expires_at
    else:
        subscription_status = await user_service.get_subscription_status(user_id)
        subscription_expires_at = await user_service.get_subscription_expires_at(
            user_id
        )

    # Check if premium subscription is active
    if subscription_status == "premium" and subscription_expires_at:
        from datetime import datetime

        if subscription_expires_at > datetime.utcnow():
            # User has active premium - calculate days remaining
            days_remaining = (subscription_expires_at - datetime.utcnow()).days
            hours_remaining = (subscription_expires_at - datetime.utcnow()).seconds // 3600
            
            if days_remaining > 0:
                premium_info = i18n.t('commands.status.premium_days', days=days_remaining)
            elif hours_remaining > 0:
                premium_info = i18n.t('commands.status.premium_hours', hours=hours_remaining)
            else:
                premium_info = i18n.t('commands.status.premium_expiring')
            
            await message.answer(
                f"{i18n.t('commands.status.title')}\n\n"
                f"{i18n.t('commands.status.unlimited')}\n\n"
                f"{premium_info}"
            )
            return

    # Get daily limit from config
    from config.openai import OPENAI_CONFIG

    daily_limit = OPENAI_CONFIG.get("FREE_MESSAGE_LIMIT", 50)

    # Get remaining messages
    remaining = await message_service.get_remaining_messages(user_id)
    used = daily_limit - remaining

    # Prepare response based on remaining messages
    if remaining == 0:
        response = f"{i18n.t('commands.status.title')}\n\n{i18n.t('commands.status.used_all', total=daily_limit)}"
    else:
        response = f"{i18n.t('commands.status.title')}\n\n{i18n.t('commands.status.remaining_free', remaining=remaining, total=daily_limit)}"

    # Add reset info
    response += f"\n\n{i18n.t('commands.status.reset_info')}"

    await message.answer(response)


# Cache for metrics command (optimization for scalability)
_metrics_cache = {"response": None, "last_update": 0, "ttl": 30}  # Cache for 30 seconds


@router.message(Command(commands=["security"]))
async def cmd_security(message: Message, i18n: I18nMiddleware):
    """Show security metrics (admin only)."""
    user_id = message.from_user.id

    # Check if user is admin (hardcoded for now)
    if user_id not in {627875032, 1512454100}:
        await message.answer("Access denied.")
        return

    # Get security validator
    from shared.security import SecurityValidator
    security_validator = SecurityValidator()
    
    # Get user security score
    security_score = security_validator.get_user_security_score(user_id)
    
    response = "🔒 Security Metrics\n\n"
    response += f"Your Security Score: {security_score['score']}/100\n"
    response += f"Risk Level: {security_score['risk_level']}\n"
    response += f"Security Flags: {len(security_score['flags'])}\n"
    response += f"Message Count: {security_score['message_count']}\n"
    response += f"Rapid Messages: {security_score['rapid_messages']}\n\n"
    
    if security_score['flags']:
        response += "Flags:\n"
        for flag in security_score['flags']:
            response += f"  - {flag}\n"
    else:
        response += "No security flags detected ✅"

    await message.answer(response)


@router.message(Command(commands=["reset_metrics"]))
async def cmd_reset_metrics(message: Message, i18n: I18nMiddleware):
    """Reset daily metrics (admin only, for testing)."""
    user_id = message.from_user.id

    # Check if user is admin (hardcoded for now)
    if user_id not in {627875032, 1512454100}:
        await message.answer("Access denied.")
        return

    # Get metrics collector
    from shared.metrics.metrics import metrics_collector
    
    if metrics_collector is None:
        await message.answer("Metrics not available.")
        return

    # Reset daily metrics
    metrics_collector.metrics.reset_daily_metrics()
    
    # Save to database
    await metrics_collector.save_to_database()
    
    await message.answer("✅ Daily metrics reset successfully!")


@router.message(Command(commands=["restart"]))
async def cmd_restart(message: Message, i18n: I18nMiddleware):
    """Restart command with confirmation."""
    await message.answer(
        i18n.t("commands.restart.confirmation"),
        reply_markup=get_restart_confirmation_keyboard(i18n),
        parse_mode="HTML"
    )


@router.message(Command(commands=["stop"]))
async def cmd_stop(message: Message, i18n: I18nMiddleware):
    """Stop command with confirmation."""
    await message.answer(
        i18n.t("commands.stop.confirmation"),
        reply_markup=get_stop_confirmation_keyboard(i18n),
        parse_mode="HTML"
    )


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
    if (
        _metrics_cache["response"]
        and (current_time - _metrics_cache["last_update"]) < _metrics_cache["ttl"]
    ):
        await message.answer(_metrics_cache["response"])
        return

    # Generate fresh metrics
    metrics_summary = metrics_collector.get_metrics_summary()

    response = "📊 Bot Metrics\n\n"

    # System metrics
    response += f"uptime_seconds: {metrics_summary['uptime_seconds']}\n"
    response += f"uptime_minutes: {metrics_summary['uptime_minutes']}\n\n"

    # Daily user activity metrics (reset at midnight)
    response += f"👥 USERS TODAY:\n"
    response += f"  unique_active_users: {metrics_summary['unique_active_users_today']}\n"
    response += f"  new_users: {metrics_summary['new_users_today']}\n"
    response += f"  retention_rate: {metrics_summary['retention_rate']}\n"
    response += f"  avg_messages_per_user: {metrics_summary['avg_messages_per_user']}\n\n"
    
    response += f"📊 ACTIVITY TODAY:\n"
    response += f"  total_interactions: {metrics_summary['total_interactions_today']}\n"
    response += f"  messages_sent: {metrics_summary['messages_sent_today']}\n"
    response += f"  commands_used: {metrics_summary['commands_used_today']}\n"
    response += f"  callback_queries: {metrics_summary['callback_queries_today']}\n"
    response += f"  ai_responses_sent: {metrics_summary['ai_responses_sent_today']}\n"
    response += f"  premium_users_active: {metrics_summary['premium_users_active_today']}\n\n"

    # General metrics (accumulative, never reset)
    response += (
        f"total_messages_processed: {metrics_summary['total_messages_processed']}\n"
    )
    response += f"success_rate: {metrics_summary['success_rate']}\n"
    response += f"average_response_time: {metrics_summary['average_response_time']}\n"
    response += f"limit_exceeded_count: {metrics_summary['limit_exceeded_count']}\n\n"

    # Performance and error metrics (accumulative, never reset)
    response += f"cache_hit_rate: {metrics_summary['cache_hit_rate']}\n"
    response += f"openai_errors: {metrics_summary['openai_errors']}\n"
    response += f"database_errors: {metrics_summary['database_errors']}\n"
    response += f"validation_errors: {metrics_summary['validation_errors']}\n\n"
    
    # Security metrics (accumulative, never reset)
    response += f"security_flags: {metrics_summary['security_flags']}\n"
    response += f"suspicious_content_detected: {metrics_summary['suspicious_content_detected']}\n"
    response += f"flood_attempts_blocked: {metrics_summary['flood_attempts_blocked']}\n"
    response += f"sanitization_applied: {metrics_summary['sanitization_applied']}\n"
    response += f"access_denied_count: {metrics_summary['access_denied_count']}\n\n"
    
    # Debug info
    response += f"DEBUG - Daily user IDs count: {len(metrics_collector.metrics.daily_user_ids)}\n"
    response += f"DEBUG - Daily user IDs: {list(metrics_collector.metrics.daily_user_ids)}"

    # Update cache
    _metrics_cache["response"] = response
    _metrics_cache["last_update"] = current_time

    await message.answer(response)


@router.message(F.text == "/clean_metrics")
async def cmd_clean_metrics(message: Message, user_service: UserService):
    """Clean test data from metrics and sync with real users."""
    try:
        # Get metrics_collector dynamically
        from shared.metrics.metrics import metrics_collector

        # Check if metrics_collector is initialized
        if metrics_collector is None:
            await message.answer("❌ Metrics system not initialized yet. Please try again later.")
            return
            
        # Get real user IDs from database
        async with user_service.pool.acquire() as conn:
            rows = await conn.fetch("SELECT id FROM users")
            real_user_ids = {row['id'] for row in rows}
            
        if not real_user_ids:
            await message.answer("❌ No real users found in database!")
            return
            
        # Get current daily user IDs from metrics
        current_daily_ids = metrics_collector.metrics.daily_user_ids.copy()
        
        # Filter to only real users
        cleaned_ids = current_daily_ids.intersection(real_user_ids)
        removed_count = len(current_daily_ids) - len(cleaned_ids)
        
        if removed_count > 0:
            # Update metrics with cleaned data
            metrics_collector.metrics.daily_user_ids = cleaned_ids
            metrics_collector.metrics.unique_active_users_today = len(cleaned_ids)
            
            # Save to database
            await metrics_collector.save_to_database()
            
            response = f"🧹 **METRICS CLEANED**\n\n"
            response += f"✅ Removed {removed_count} test/fake user IDs\n"
            response += f"✅ Kept {len(cleaned_ids)} real user IDs\n\n"
            response += f"**Real users:** {sorted(real_user_ids)}\n"
            response += f"**Cleaned daily IDs:** {sorted(cleaned_ids) if cleaned_ids else 'None'}"
            
        else:
            response = f"✅ **NO TEST DATA FOUND**\n\n"
            response += f"All {len(current_daily_ids)} daily user IDs are real users\n"
            response += f"**Daily IDs:** {sorted(current_daily_ids) if current_daily_ids else 'None'}"
            
        await message.answer(response)
        
    except Exception as e:
        logging.error(f"Error cleaning metrics: {e}")
        await message.answer(f"❌ Error cleaning metrics: {str(e)}")


@router.message(F.text == "/reset_daily_metrics")
async def cmd_reset_daily_metrics(message: Message):
    """Reset all daily metrics to start fresh."""
    try:
        # Get metrics_collector dynamically
        from shared.metrics.metrics import metrics_collector

        # Check if metrics_collector is initialized
        if metrics_collector is None:
            await message.answer("❌ Metrics system not initialized yet. Please try again later.")
            return
            
        # Reset daily counters
        metrics_collector.metrics.total_interactions_today = 0
        metrics_collector.metrics.unique_active_users_today = 0
        metrics_collector.metrics.new_users_today = 0
        metrics_collector.metrics.messages_sent_today = 0
        metrics_collector.metrics.commands_used_today = 0
        metrics_collector.metrics.ai_responses_sent_today = 0
        metrics_collector.metrics.callback_queries_today = 0
        metrics_collector.metrics.premium_users_active_today = 0
        
        # Clear daily user IDs
        metrics_collector.metrics.daily_user_ids.clear()
        
        # Save to database
        await metrics_collector.save_to_database()
        
        response = "🔄 **DAILY METRICS RESET**\n\n"
        response += "✅ All daily counters reset to 0\n"
        response += "✅ Daily user IDs cleared\n"
        response += "✅ Fresh start for today's metrics"
        
        await message.answer(response)
        
    except Exception as e:
        logging.error(f"Error resetting daily metrics: {e}")
        await message.answer(f"❌ Error resetting metrics: {str(e)}")


@router.callback_query(F.data == "choose_language")
async def choose_language_help(callback: CallbackQuery, i18n: I18nMiddleware):
    """Handle choose language help callback."""
    try:
        # Get current language
        current_language = i18n.get_language()
        
        # Get language names for display
        language_names = {
            "ru": "Русский",
            "en": "English",
            "sr": "Српски", 
            "de": "Deutsch",
            "es": "Español"
        }
        
        current_language_name = language_names.get(current_language, current_language.upper())
        
        # Get language selection text
        title = i18n.t("commands.language.title")
        description = i18n.t("commands.language.description")
        current_text = i18n.t("commands.language.current", language=current_language_name)
        
        # Create message text
        text = f"{title}\n\n{description}\n{current_text}"
        
        # Create keyboard with current language marked
        keyboard = get_language_keyboard_with_current(current_language)
        
        # Edit message
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            await callback.answer()
        elif "message to edit not found" in str(e).lower():
            await callback.answer("Сообщение устарело", show_alert=True)
        else:
            logging.error(f"Choose language help error: {e}")
            await callback.answer("❌ Ошибка обновления", show_alert=True)
    except Exception as e:
        logging.error(f"Choose language help error: {e}")
        await callback.answer("❌ Ошибка обновления", show_alert=True)


@router.callback_query(F.data == "choose_gender_help")
async def gender_help(callback: CallbackQuery, i18n: I18nMiddleware):
    """Handle gender help callback with optimal performance."""
    try:
        await callback.message.edit_text(
            text=i18n.t("buttons.choose_gender_help"),
            reply_markup=get_gender_keyboard(i18n)
        )
        await callback.answer()
        
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            await callback.answer()
        elif "message to edit not found" in str(e).lower():
            await callback.answer("Сообщение устарело", show_alert=True)
        else:
            logging.error(f"Gender help error: {e}")
            await callback.answer("❌ Ошибка обновления", show_alert=True)


@router.callback_query(F.data == "restart_confirm")
@optimize_callback_edit
async def restart_confirm(callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware):
    """Confirm restart - clear messages and show gender selection."""
    user_id = callback.from_user.id
    
    # Restart user state (clear messages but keep consent)
    await user_service.restart_user_state(user_id)
    
    # Send restart message
    await callback.message.edit_text(
        i18n.t("commands.restart.success"),
        parse_mode="HTML"
    )
    
    # Show gender selection after delay
    await asyncio.sleep(2)
    await callback.message.answer(
        i18n.t("gender.choose_gender"),
        reply_markup=get_gender_keyboard(i18n),
        parse_mode="HTML"
    )
    
    await callback.answer()


@router.callback_query(F.data == "restart_cancel")
async def restart_cancel(callback: CallbackQuery, i18n: I18nMiddleware):
    """Cancel restart - return to help."""
    try:
        await callback.message.edit_text(
            text=get_help_text(),
            reply_markup=get_help_keyboard(i18n),
            parse_mode="HTML"
        )
        await callback.answer(i18n.t("commands.restart.cancelled"))
        
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            await callback.answer()
        elif "message to edit not found" in str(e).lower():
            await callback.answer("Сообщение устарело", show_alert=True)
        else:
            logging.error(f"Restart cancel error: {e}")
            await callback.answer("❌ Ошибка обновления", show_alert=True)
    except Exception as e:
        logging.error(f"Restart cancel error: {e}")
        await callback.answer("❌ Ошибка обновления", show_alert=True)


@router.callback_query(F.data == "stop_confirm")
@optimize_callback_edit
async def stop_confirm(callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware):
    """Confirm stop - clear all data and deactivate."""
    user_id = callback.from_user.id
    
    # Reset user state completely (messages, consent, gender preference)
    await user_service.reset_user_state(user_id)
    
    # Send goodbye message
    await callback.message.edit_text(
        i18n.t("commands.stop.success"),
        parse_mode="HTML"
    )
    
    await callback.answer()


@router.callback_query(F.data == "stop_cancel")
async def stop_cancel(callback: CallbackQuery, i18n: I18nMiddleware):
    """Cancel stop - return to help."""
    try:
        await callback.message.edit_text(
            text=get_help_text(),
            reply_markup=get_help_keyboard(i18n),
            parse_mode="HTML"
        )
        await callback.answer(i18n.t("commands.stop.cancelled"))
        
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            await callback.answer()
        elif "message to edit not found" in str(e).lower():
            await callback.answer("Сообщение устарело", show_alert=True)
        else:
            logging.error(f"Stop cancel error: {e}")
            await callback.answer("❌ Ошибка обновления", show_alert=True)
    except Exception as e:
        logging.error(f"Stop cancel error: {e}")
        await callback.answer("❌ Ошибка обновления", show_alert=True)
