"""
Common keyboards used across different domains.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Get back button keyboard."""
    from shared.i18n import i18n

    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=i18n.t("buttons.back"), callback_data="back")]])


def get_yes_no_keyboard(yes_callback: str = "yes", no_callback: str = "no") -> InlineKeyboardMarkup:
    """Get yes/no confirmation keyboard."""
    from shared.i18n import i18n

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=i18n.t("buttons.yes"), callback_data=yes_callback),
                InlineKeyboardButton(text=i18n.t("buttons.no"), callback_data=no_callback),
            ]
        ]
    )


def get_cancel_keyboard(cancel_callback: str = "cancel") -> InlineKeyboardMarkup:
    """Get cancel button keyboard."""
    from shared.i18n import i18n

    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=i18n.t("buttons.cancel"), callback_data=cancel_callback)]]
    )


def get_limit_exceeded_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for when message limit is exceeded."""
    from shared.i18n import i18n

    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=i18n.t("buttons.buy_premium"), callback_data="subscribe_premium")]]
    )
