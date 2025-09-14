"""
Payment domain keyboards - placeholder for future implementation.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from shared.i18n import i18n


def get_payment_keyboard() -> InlineKeyboardMarkup:
    """Get payment keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=i18n.t("buttons.pay"), callback_data="make_payment")]]
    )
