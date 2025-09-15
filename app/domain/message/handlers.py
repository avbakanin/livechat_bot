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
from shared.metrics.metrics import record_response_time, safe_record_metric, safe_record_user_interaction
from shared.utils.helpers import destructure_user

from core.exceptions import MessageException, OpenAIException

router = Router()


@router.message()
async def handle_message(
    message: Message, message_service: MessageService, user_service: UserService, bot, i18n, cached_user: UserCacheData = None
):
    """Handle incoming text messages with FSM caching."""
    user_id, username, first_name, last_name = destructure_user(message.from_user)

    # Record message processing
    safe_record_metric("record_message_processed")

    # Record user interaction (message)
    safe_record_user_interaction(user_id, "message")

    # Skip commands
    if message.text.startswith("/"):
        return

    # Validate message content
    if not message.text or len(message.text.strip()) == 0:
        safe_record_metric("record_failed_response", "validation")
        await message.answer(i18n.t("messages.empty_message"))
        return

    if len(message.text) > 4000:  # Telegram message limit
        safe_record_metric("record_failed_response", "validation")
        await message.answer(i18n.t("messages.message_too_long"))
        return

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
        await message.answer(i18n.t("consent.request"), reply_markup=get_consent_keyboard(i18n))
        return

    # Check message limit
    if not await message_service.can_send_message(user_id):
        safe_record_metric("record_limit_exceeded")
        await message.answer(i18n.t("messages.limit_exceeded"), reply_markup=get_limit_exceeded_keyboard())
        return

    # Add user message to database
    await message_service.add_message(user_id, "user", message.text)

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
            answer = await message_service.generate_response(user_id, message.text, gender)
            response_time = time.time() - start_time

            # Record successful response with timing
            safe_record_metric("record_successful_response", response_time)

            # Add AI response to database
            await message_service.add_message(user_id, "assistant", answer)

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
