"""
Message domain handlers - Telegram bot handlers for messages.
"""

import logging
import time

from aiogram import Router
from aiogram.types import Message
from domain.message.services import MessageService
from domain.user.keyboards import get_consent_keyboard
from domain.user.services_cached import UserService
from shared.fsm.user_cache import UserCacheData
from shared.helpers.typingIndicator import TypingIndicator
from shared.keyboards.common import get_limit_exceeded_keyboard
from shared.metrics.metrics import (
    safe_record_metric,
    safe_record_security_metric,
    safe_record_user_interaction,
)
from shared.security import SecurityLogger, SecurityValidator, TextSanitizer
from shared.utils.helpers import destructure_user

from core.exceptions import MessageException, OpenAIException

router = Router()


@router.message()
async def handle_message(
    message: Message,
    message_service: MessageService,
    user_service: UserService,
    bot,
    i18n,
    cached_user: UserCacheData = None,
):
    """Handle incoming text messages with enhanced security validation."""
    user_id, username, first_name, last_name = destructure_user(message.from_user)

    # Record message processing
    safe_record_metric("record_message_processed")

    # Record user interaction (message)
    safe_record_user_interaction(user_id, "message", user_service)

    # Skip commands
    if message.text.startswith("/"):
        return

    # Enhanced security validation
    security_validator = SecurityValidator()
    text_sanitizer = TextSanitizer()
    security_logger = SecurityLogger()

    # Validate user behavior first
    behavior_validation = security_validator.validate_user_behavior(
        user_id, "message"
    )
    
    if not behavior_validation["is_valid"]:
        safe_record_metric("record_failed_response", "security")
        safe_record_security_metric("record_flood_blocked")
        security_logger.log_flood_attempt(
            user_id, 
            behavior_validation.get("rapid_messages", 0), 
            1.0
        )
        await message.answer("⚠️ Слишком много сообщений. Подождите немного.")
        return

    # Validate message content
    if not message.text or len(message.text.strip()) == 0:
        safe_record_metric("record_failed_response", "validation")
        await message.answer(i18n.t("messages.empty_message"))
        return

    # Enhanced content validation
    content_validation = security_validator.validate_message_content(
        message.text, user_id, 2500
    )
    
    if not content_validation["is_valid"]:
        safe_record_metric("record_failed_response", "validation")
        await message.answer(i18n.t("messages.message_too_long"))
        return

    # Log security flags if any
    if content_validation["security_flags"]:
        safe_record_security_metric("record_security_flag")
        for flag in content_validation["security_flags"]:
            if flag == "LONG_MESSAGE":
                security_logger.log_long_message(user_id, len(message.text), 2500)
            elif flag == "REPETITIVE_CONTENT":
                security_logger.log_repetitive_content(user_id, message.text, "character_repetition")
            elif flag == "POTENTIAL_SPAM":
                security_logger.log_potential_spam(user_id, message.text, ["caps", "exclamation"])

    # Sanitize message text
    sanitized_text = text_sanitizer.sanitize_text(message.text, user_id)
    
    # Check if text was significantly modified during sanitization
    if len(sanitized_text) < len(message.text) * 0.8:  # More than 20% removed
        security_logger.log_suspicious_content(
            user_id, message.text, ["sanitization_applied"], sanitized_text
        )
        safe_record_metric("record_failed_response", "security")
        safe_record_security_metric("record_suspicious_content")
        safe_record_security_metric("record_sanitization_applied")
        await message.answer("⚠️ Сообщение содержит недопустимые символы. Попробуйте еще раз.")
        return

    # Use sanitized text for further processing (don't modify message.text)
    original_text = message.text
    message_text = sanitized_text

    # Add user to database (this will update cache if user exists)
    await user_service.add_user(user_id, username, first_name, last_name)

    # Check consent using cache if available
    if cached_user:
        consent_given = cached_user.consent_given
        safe_record_metric("record_cache_hit")
    else:
        consent_given = await user_service.get_consent_status(user_id)
        safe_record_metric("record_cache_miss")

    if not consent_given:
        await message.answer(
            i18n.t("consent.request"), reply_markup=get_consent_keyboard(i18n)
        )
        return

    # Check message limit
    if not await message_service.can_send_message(user_id):
        safe_record_metric("record_limit_exceeded")
        await message.answer(
            i18n.t("messages.limit_exceeded"),
            reply_markup=get_limit_exceeded_keyboard(),
        )
        return

    # Add user message to database
    await message_service.add_message(user_id, "user", message_text)

    # Show typing status during AI response generation
    async with TypingIndicator(bot, message.chat.id):
        try:
            # Get gender preference using cache if available
            if cached_user:
                gender = cached_user.gender_preference
            else:
                gender = await user_service.get_gender_preference(user_id)

            # Generate AI response with timing
            start_time = time.time()
            answer = await message_service.generate_response(
                user_id, message_text, gender
            )
            response_time = time.time() - start_time

            # Record successful response with timing
            safe_record_metric("record_successful_response", response_time)

            # Add AI response to database
            await message_service.add_message(user_id, "assistant", answer)

            # Record AI response sent
            safe_record_security_metric("record_ai_response_sent")

            # Send response
            await message.answer(answer)

        except OpenAIException as e:
            logging.error(f"OpenAI error: {e}")
            safe_record_metric("record_failed_response", "openai")
            await message.answer(i18n.t("messages.processing_error"))
        except MessageException as e:
            logging.error(f"Message error: {e}")
            safe_record_metric("record_failed_response", "database")
            await message.answer(i18n.t("messages.save_error"))
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            safe_record_metric("record_failed_response", "unknown")
            await message.answer(i18n.t("messages.unexpected_error"))
