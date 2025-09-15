"""
Message domain handlers - Telegram bot handlers for messages.
"""

import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.types import Message
from domain.message.services import MessageService
from domain.user.keyboards import get_consent_keyboard
from domain.user.services_cached import UserService
from shared.fsm.user_cache import UserCacheData
from shared.helpers.typingIndicator import TypingIndicator
from shared.keyboards.common import get_limit_exceeded_keyboard
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
    cached_user: UserCacheData = None
):
    """Handle incoming text messages with FSM caching."""
    # Skip commands
    if message.text.startswith("/"):
        return

    user_id, username, first_name, last_name = destructure_user(message.from_user)

    # Add user to database (this will update cache if user exists)
    await user_service.add_user(user_id, username, first_name, last_name)

    # Check consent using cache if available
    if cached_user:
        consent_given = cached_user.consent_given
    else:
        consent_given = await user_service.get_consent_status(user_id)
    
    if not consent_given:
        await message.answer(i18n.t("consent.request"), reply_markup=get_consent_keyboard())
        return

    # Check message limit
    if not await message_service.can_send_message(user_id):
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

            # Generate AI response
            answer = await message_service.generate_response(user_id, message.text, gender)

            # Add AI response to database
            await message_service.add_message(user_id, "assistant", answer)

            # Send response
            await message.answer(answer)

        except OpenAIException as e:
            logging.error(f"OpenAI error: {e}")
            await message.answer(i18n.t("messages.processing_error"))
        except MessageException as e:
            logging.error(f"Message error: {e}")
            await message.answer(i18n.t("messages.save_error"))
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            await message.answer(i18n.t("messages.unexpected_error"))
