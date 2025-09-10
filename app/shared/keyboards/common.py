"""
Common keyboards used across different domains.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Get back button keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back")]
    ])


def get_yes_no_keyboard(yes_callback: str = "yes", no_callback: str = "no") -> InlineKeyboardMarkup:
    """Get yes/no confirmation keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data=yes_callback),
            InlineKeyboardButton(text="❌ Нет", callback_data=no_callback)
        ]
    ])


def get_cancel_keyboard(cancel_callback: str = "cancel") -> InlineKeyboardMarkup:
    """Get cancel button keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data=cancel_callback)]
    ])


def get_limit_exceeded_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for when message limit is exceeded."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Купить премиум 💳", callback_data="subscribe_premium")]
    ])
