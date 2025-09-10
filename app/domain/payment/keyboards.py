"""
Payment domain keyboards - placeholder for future implementation.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_payment_keyboard() -> InlineKeyboardMarkup:
    """Get payment keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", callback_data="make_payment")]
    ])
