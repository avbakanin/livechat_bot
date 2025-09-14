"""
Subscription domain keyboards - placeholder for future implementation.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from shared.i18n import i18n


def get_premium_info_keyboard() -> InlineKeyboardMarkup:
    """Get premium info keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=i18n.t("buttons.buy_premium"), callback_data="subscribe_premium")],
            [InlineKeyboardButton(text=i18n.t("buttons.back_to_help"), callback_data="back_to_help")],
        ]
    )


def get_premium_keyboard() -> InlineKeyboardMarkup:
    """Get premium subscription keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=i18n.t("buttons.buy_premium"), callback_data="subscribe_premium")]]
    )
