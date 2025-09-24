"""
Message domain handlers - Telegram bot handlers for messages.
Optimized version with refactored debug functionality.
"""

import logging
import time
from typing import Optional, Dict, Any

from aiogram import Router
from aiogram.types import Message
from domain.message.services import MessageService
from domain.user.keyboards import get_consent_keyboard
from domain.user.services_cached import UserService
from services.person.person_service import PersonService
from shared.fsm.user_cache import UserCacheData
from shared.helpers.typingIndicator import TypingIndicator
from shared.keyboards.common import get_limit_exceeded_keyboard
from shared.metrics.metrics import (
    safe_record_metric,
    safe_record_security_metric,
    safe_record_user_interaction,
)
from shared.metrics.debug_info import get_user_debug_info, get_error_debug_info, get_general_debug_info
from shared.debug import DebugConfig, AdminHelper, DebugTextHelper, DebugValidationHelper
from shared.security import SecurityLogger, SecurityValidator, TextSanitizer
from shared.helpers import destructure_user

from core.exceptions import MessageException, OpenAIException

router = Router()


class MessageDebugHelper:
    """Helper class for message debugging functionality."""
    
    @staticmethod
    def is_admin(user_id: int) -> bool:
        """Check if user is admin."""
        return AdminHelper.is_admin(user_id)
    
    @staticmethod
    async def get_message_debug_data(message: Message, message_service: MessageService, 
                                   user_service: UserService, cached_user: Optional[UserCacheData]) -> Dict[str, Any]:
        """Get comprehensive message debug data."""
        user_id = message.from_user.id
        
        # Prepare debug data
        debug_data = {
            "message_id": message.message_id,
            "text_length": len(message.text) if message.text else 0,
            "text_preview": message.text[:100] + "..." if message.text and len(message.text) > 100 else message.text,
            "chat_id": message.chat.id,
            "chat_type": message.chat.type,
            "timestamp": message.date,
            "can_send_message": await message_service.can_send_message(user_id),
            "remaining_messages": await message_service.get_remaining_messages(user_id),
        }
        
        # Add user-specific data (use cache when available)
        if cached_user:
            debug_data.update({
                "consent_given": cached_user.consent_given,
                "gender_preference": cached_user.gender_preference,
                "user_language": cached_user.language
            })
        else:
            # Get user data in single query for efficiency
            user = await user_service.get_user(user_id)
            if user:
                debug_data.update({
                    "consent_given": user.consent_given,
                    "gender_preference": user.gender_preference,
                    "user_language": user.language
                })
            else:
                debug_data.update({
                    "consent_given": None,
                    "gender_preference": None,
                    "user_language": None
                })
        
        return debug_data
    
    @staticmethod
    async def send_debug_info(message: Message, debug_data: Dict[str, Any], 
                            user: Optional[Any], cached_user: Optional[UserCacheData]):
        """Send comprehensive debug information to admin."""
        user_id = message.from_user.id
        
        # Generate user debug info
        user_debug = get_user_debug_info(user_id, user, cached_user)
        
        # Generate message debug info
        message_debug = get_general_debug_info("Отладка сообщения", debug_data)
        
        # Combine and send
        full_debug = f"{user_debug}\n\n{message_debug}"
        await message.answer(full_debug)
    
    @staticmethod
    async def send_error_debug(message: Message, error: Exception, context: Dict[str, Any]):
        """Send error debug information to admin."""
        error_info = get_error_debug_info(error, context)
        await message.answer(f"🔍 Debug Error:\n{error_info}")


class MessageValidationHelper:
    """Helper class for message validation logic."""
    
    @staticmethod
    def validate_message_basic(message: Message) -> Optional[str]:
        """Basic message validation. Returns error message if invalid, None if valid."""
        if not message.text or len(message.text.strip()) == 0:
            return "empty_message"
        
        if message.text.startswith("/"):
            return "command"  # Not an error, just skip
        
        return None
    
    @staticmethod
    async def validate_security(message: Message, user_id: int, security_validator: SecurityValidator) -> Optional[Dict[str, Any]]:
        """Validate message security. Returns validation result or None if valid."""
        # Behavior validation
        behavior_validation = security_validator.validate_user_behavior(user_id, "message")
        if not behavior_validation["is_valid"]:
            return {"type": "behavior", "data": behavior_validation}
        
        # Content validation
        content_validation = security_validator.validate_message_content(message.text, user_id, DebugConfig.MAX_MESSAGE_LENGTH)
        if not content_validation["is_valid"]:
            return {"type": "content", "data": content_validation}
        
        return None
    
    @staticmethod
    def sanitize_message(message: Message, user_id: int, text_sanitizer: TextSanitizer, 
                        security_logger: SecurityLogger) -> Optional[str]:
        """Sanitize message text. Returns sanitized text or None if invalid."""
        sanitized_text = text_sanitizer.sanitize_text(message.text, user_id)
        
        # Check if text was significantly modified
        if len(sanitized_text) < len(message.text) * DebugConfig.SANITIZATION_THRESHOLD:
            security_logger.log_suspicious_content(
                user_id, message.text, ["sanitization_applied"], sanitized_text
            )
            return None
        
        return sanitized_text


async def handle_debug_command(message: Message, message_service: MessageService, 
                              user_service: UserService, cached_user: Optional[UserCacheData]) -> bool:
    """Handle debug command. Returns True if handled, False otherwise."""
    user_id = message.from_user.id
    
    # Validate command format
    command_validation = DebugValidationHelper.validate_debug_command(message.text)
    if command_validation:
        await message.answer(f"❌ Ошибка команды: {command_validation}")
        return True
    
    if not MessageDebugHelper.is_admin(user_id):
        return False
    
    try:
        # Get debug type
        debug_type = DebugValidationHelper.get_debug_type(message.text)
        
        if debug_type == DebugConfig.DEBUG_PERSONA:
            await _handle_persona_debug(message, user_service, cached_user)
            
        elif debug_type == DebugConfig.DEBUG_PERSONA_STATS:
            await _handle_persona_stats_debug(message)
            
        elif debug_type == DebugConfig.DEBUG_PERSONA_DATA:
            await _handle_persona_data_debug(message)
            
        else:
            # Default message debug
            await _handle_message_debug(message, message_service, user_service, cached_user)
        
        return True
        
    except Exception as e:
        await MessageDebugHelper.send_error_debug(message, e, {
            "user_id": user_id,
            "command": message.text,
            "message_text": DebugTextHelper.truncate_text(message.text)
        })
        return True


async def _handle_persona_debug(message: Message, user_service: UserService, cached_user: Optional[UserCacheData]):
    """Handle persona debug command."""
    user_id = message.from_user.id
    person_service = PersonService()
    
    # Get user gender preference efficiently
    user_gender = cached_user.gender_preference if cached_user else await user_service.get_gender_preference(user_id)
    
    # Generate comprehensive debug info
    persona_debug = person_service.generate_persona_debug_info(user_gender, user_id)
    persona_stats = person_service.get_persona_statistics()
    persons_data_debug = person_service.get_persons_data_debug_info()
    
    # Combine debug information
    debug_info = get_general_debug_info("Отладка персонажей", {
        "user_gender": user_gender,
        "persona_generation": persona_debug,
        "statistics": persona_stats,
        "data_status": persons_data_debug
    })
    
    await message.answer(debug_info)


async def _handle_persona_stats_debug(message: Message):
    """Handle persona statistics debug command."""
    person_service = PersonService()
    stats = person_service.get_persona_statistics()
    
    debug_info = get_general_debug_info("Статистика персонажей", stats)
    await message.answer(debug_info)


async def _handle_persona_data_debug(message: Message):
    """Handle persona data debug command."""
    person_service = PersonService()
    data_debug = person_service.get_persons_data_debug_info()
    
    debug_info = get_general_debug_info("Данные персонажей", data_debug)
    await message.answer(debug_info)


async def _handle_message_debug(message: Message, message_service: MessageService, 
                               user_service: UserService, cached_user: Optional[UserCacheData]):
    """Handle default message debug command."""
    user_id = message.from_user.id
    
    # Get user and debug data
    user = await user_service.get_user(user_id)
    debug_data = await MessageDebugHelper.get_message_debug_data(message, message_service, user_service, cached_user)
    
    # Send debug info
    await MessageDebugHelper.send_debug_info(message, debug_data, user, cached_user)


async def handle_security_validation(message: Message, user_id: int, i18n, 
                                   security_validator: SecurityValidator, 
                                   security_logger: SecurityLogger) -> Optional[str]:
    """Handle security validation. Returns error message if validation failed, None if passed."""
    validation_result = await MessageValidationHelper.validate_security(message, user_id, security_validator)
    
    if not validation_result:
        return None
    
    validation_type = validation_result["type"]
    validation_data = validation_result["data"]
    
    if validation_type == "behavior":
        # Flood detection
        safe_record_metric("record_failed_response", "security")
        safe_record_security_metric("record_flood_blocked")
        security_logger.log_flood_attempt(user_id, validation_data.get("rapid_messages", 0), 1.0)
        
        if MessageDebugHelper.is_admin(user_id):
            flood_debug = get_general_debug_info("Отладка флуда", {
                "rapid_messages": validation_data.get("rapid_messages", 0),
                "validation_result": validation_data,
                "message_text": DebugTextHelper.truncate_text(message.text),
                "timestamp": message.date
            })
            await message.answer(f"🔍 Debug Flood Detection:\n{flood_debug}")
        else:
            await message.answer("⚠️ Слишком много сообщений. Подождите немного.")
        
        return "flood_detected"
    
    elif validation_type == "content":
        # Content validation failed
        safe_record_metric("record_failed_response", "validation")
        
        # Log security flags
        if validation_data.get("security_flags"):
            safe_record_security_metric("record_security_flag")
            for flag in validation_data["security_flags"]:
                if flag == "LONG_MESSAGE":
                    security_logger.log_long_message(user_id, len(message.text), DebugConfig.MAX_MESSAGE_LENGTH)
                elif flag == "REPETITIVE_CONTENT":
                    security_logger.log_repetitive_content(user_id, message.text, "character_repetition")
                elif flag == "POTENTIAL_SPAM":
                    security_logger.log_potential_spam(user_id, message.text, ["caps", "exclamation"])
        
        await message.answer(i18n.t("messages.message_too_long"))
        return "content_invalid"
    
    return None


async def handle_user_validation(message: Message, user_id: int, message_service: MessageService, 
                                user_service: UserService, cached_user: Optional[UserCacheData], 
                                i18n) -> Optional[str]:
    """Handle user validation (consent, limits). Returns error message if validation failed, None if passed."""
    # Check consent
    if cached_user:
        consent_given = cached_user.consent_given
        safe_record_metric("record_cache_hit")
    else:
        consent_given = await user_service.get_consent_status(user_id)
        safe_record_metric("record_cache_miss")
    
    if not consent_given:
        await message.answer(i18n.t("consent.request"), reply_markup=get_consent_keyboard())
        return "consent_required"
    
    # Check message limit
    if not await message_service.can_send_message(user_id):
        safe_record_metric("record_limit_exceeded")
        
        if MessageDebugHelper.is_admin(user_id):
            limit_debug = get_general_debug_info("Отладка лимита сообщений", {
                "can_send_message": False,
                "remaining_messages": await message_service.get_remaining_messages(user_id),
                "message_text": DebugTextHelper.truncate_text(message.text),
                "user_id": user_id,
                "timestamp": message.date
            })
            await message.answer(f"🔍 Debug Limit Exceeded:\n{limit_debug}")
        else:
            await message.answer(
                i18n.t("messages.limit_exceeded"),
                reply_markup=get_limit_exceeded_keyboard(),
            )
        return "limit_exceeded"
    
    return None


async def handle_ai_response(message: Message, user_id: int, message_text: str, 
                           message_service: MessageService, user_service: UserService, 
                           cached_user: Optional[UserCacheData], bot, i18n):
    """Handle AI response generation with comprehensive error handling."""
    try:
        # Get user preferences efficiently
        if cached_user:
            gender = cached_user.gender_preference
            user_language = cached_user.language
        else:
            gender = await user_service.get_gender_preference(user_id)
            user_language = await user_service.get_language(user_id)
        
        # Get personality profile
        personality_profile = await user_service.get_personality_profile(user_id)
        
        # Generate AI response with timing
        start_time = time.time()
        answer = await message_service.generate_response(
            user_id, message_text, gender, personality_profile, user_language
        )
        response_time = time.time() - start_time
        
        # Record success
        safe_record_metric("record_successful_response", response_time)
        
        # Save AI response
        await message_service.add_message(user_id, "assistant", answer)
        safe_record_security_metric("record_ai_response_sent")
        
        # Send response
        await message.answer(answer)
        
    except OpenAIException as e:
        logging.error(f"OpenAI error: {e}")
        safe_record_metric("record_failed_response", "openai")
        
        if MessageDebugHelper.is_admin(user_id):
            await MessageDebugHelper.send_error_debug(message, e, {
                "user_id": user_id,
                "message_text": DebugTextHelper.truncate_text(message_text),
                "error_type": "OpenAIException",
                "response_time": response_time if 'response_time' in locals() else "N/A"
            })
        else:
            await message.answer(i18n.t("messages.processing_error"))
            
    except MessageException as e:
        logging.error(f"Message error: {e}")
        safe_record_metric("record_failed_response", "database")
        
        if MessageDebugHelper.is_admin(user_id):
            await MessageDebugHelper.send_error_debug(message, e, {
                "user_id": user_id,
                "message_text": DebugTextHelper.truncate_text(message_text),
                "error_type": "MessageException",
                "operation": "database_save"
            })
        else:
            await message.answer(i18n.t("messages.save_error"))
            
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        safe_record_metric("record_failed_response", "unknown")
        
        if MessageDebugHelper.is_admin(user_id):
            await MessageDebugHelper.send_error_debug(message, e, {
                "user_id": user_id,
                "message_text": DebugTextHelper.truncate_text(message_text),
                "error_type": "UnexpectedException",
                "response_time": response_time if 'response_time' in locals() else "N/A"
            })
        else:
            await message.answer(i18n.t("messages.unexpected_error"))


@router.message()
async def handle_message(
    message: Message,
    message_service: MessageService,
    user_service: UserService,
    bot,
    i18n,
    cached_user: UserCacheData = None,
):
    """Handle incoming text messages with enhanced security validation and optimized debug functionality."""
    user_id, username, first_name, last_name = destructure_user(message.from_user)
    
    # Handle debug command first
    if await handle_debug_command(message, message_service, user_service, cached_user):
        return
    
    # Record message processing
    safe_record_metric("record_message_processed")
    safe_record_user_interaction(user_id, "message", user_service)
    
    # Basic validation
    basic_error = MessageValidationHelper.validate_message_basic(message)
    if basic_error == "empty_message":
        safe_record_metric("record_failed_response", "validation")
        await message.answer(i18n.t("messages.empty_message"))
        return
    elif basic_error == "command":
        return  # Skip commands
    
    # Initialize security components
    security_validator = SecurityValidator()
    text_sanitizer = TextSanitizer()
    security_logger = SecurityLogger()
    
    # Security validation
    security_error = await handle_security_validation(message, user_id, i18n, security_validator, security_logger)
    if security_error:
        return
    
    # Message sanitization
    message_text = MessageValidationHelper.sanitize_message(message, user_id, text_sanitizer, security_logger)
    if not message_text:
        safe_record_metric("record_failed_response", "security")
        safe_record_security_metric("record_suspicious_content")
        safe_record_security_metric("record_sanitization_applied")
        await message.answer("⚠️ Сообщение содержит недопустимые символы. Попробуйте еще раз.")
        return
    
    # Add user to database
    await user_service.add_user(user_id, username, first_name, last_name)
    
    # User validation (consent, limits)
    user_error = await handle_user_validation(message, user_id, message_service, user_service, cached_user, i18n)
    if user_error:
        return
    
    # Add user message to database
    await message_service.add_message(user_id, "user", message_text)
    
    # Generate and send AI response
    async with TypingIndicator(bot, message.chat.id):
        await handle_ai_response(message, user_id, message_text, message_service, user_service, cached_user, bot, i18n)
