"""
Пример использования оптимизированных callback обработчиков.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery
from domain.user.keyboards import get_help_keyboard
from shared.decorators import optimize_callback_edit
from shared.messages.common import get_help_text

router = Router()


# Пример 1: Простое использование декоратора
@router.callback_query(F.data == "back_to_help")
@optimize_callback_edit
async def back_to_help(callback: CallbackQuery, i18n):
    """Handle back to help callback - оптимизированная версия."""
    await callback.message.edit_text(
        text=get_help_text(),
        reply_markup=get_help_keyboard(i18n),
        parse_mode="HTML"
    )
    await callback.answer()


# Пример 2: Без декоратора (ручная обработка)
@router.callback_query(F.data == "back_to_help_manual")
async def back_to_help_manual(callback: CallbackQuery, i18n):
    """Handle back to help callback - ручная обработка ошибок."""
    try:
        await callback.message.edit_text(
            text=get_help_text(),
            reply_markup=get_help_keyboard(i18n),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except MessageNotModified:
        await callback.answer()
    except MessageToEditNotFound:
        await callback.answer("Сообщение устарело", show_alert=True)
    except Exception as e:
        logging.error(f"Back to help error: {e}")
        await callback.answer("❌ Ошибка обновления", show_alert=True)


# Пример 3: С предварительной проверкой контента
@router.callback_query(F.data == "back_to_help_smart")
async def back_to_help_smart(callback: CallbackQuery, i18n):
    """Handle back to help callback - с проверкой контента."""
    try:
        help_text = get_help_text()
        help_keyboard = get_help_keyboard(i18n)
        
        # Проверяем, изменился ли контент
        current_text = callback.message.text or callback.message.caption or ""
        current_markup = callback.message.reply_markup
        
        if (current_text == help_text and 
            str(current_markup) == str(help_keyboard)):
            await callback.answer()  # Контент не изменился
            return
            
        await callback.message.edit_text(
            text=help_text,
            reply_markup=help_keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except MessageNotModified:
        await callback.answer()
    except MessageToEditNotFound:
        await callback.answer("Сообщение устарело", show_alert=True)
    except Exception as e:
        logging.error(f"Back to help error: {e}")
        await callback.answer("❌ Ошибка обновления", show_alert=True)
