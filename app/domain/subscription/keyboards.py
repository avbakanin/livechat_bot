"""
Subscription domain keyboards - placeholder for future implementation.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_premium_info_keyboard() -> InlineKeyboardMarkup:
    """Get premium info keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Купить премиум", callback_data="subscribe_premium")],
        [InlineKeyboardButton(text="↩️ Назад к справке", callback_data="back_to_help")]
    ])


def get_premium_keyboard() -> InlineKeyboardMarkup:
    """Get premium subscription keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Купить премиум 💳", callback_data="subscribe_premium")]
    ])
