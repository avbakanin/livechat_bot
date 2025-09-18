from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from domain.user.constants import Callbacks

from shared.i18n import i18n


def get_consent_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.agree_privacy"),
                    callback_data=Callbacks.CONSENT_AGREE,
                )
            ],
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.read_privacy"),
                    url="https://your-site.com/privacy",
                )
            ],
        ]
    )


def get_consent_given_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.choose_female"),
                    callback_data=Callbacks.GENDER_FEMALE,
                ),
                InlineKeyboardButton(
                    text=i18n.t("buttons.choose_male"),
                    callback_data=Callbacks.GENDER_MALE,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.buy_premium"),
                    callback_data=Callbacks.SUBSCRIBE_PREMIUM,
                )
            ],
        ]
    )


def get_gender_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.choose_female"),
                    callback_data=Callbacks.GENDER_FEMALE,
                ),
                InlineKeyboardButton(
                    text=i18n.t("buttons.choose_male"),
                    callback_data=Callbacks.GENDER_MALE,
                ),
            ]
        ]
    )


def get_gender_change_confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.yes_change"),
                    callback_data=Callbacks.GENDER_CHANGE_CONFIRM,
                ),
                InlineKeyboardButton(
                    text=i18n.t("buttons.cancel"),
                    callback_data=Callbacks.GENDER_CHANGE_CANCEL,
                ),
            ]
        ]
    )


def get_help_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.choose_gender_help"),
                    callback_data=Callbacks.CHOOSE_GENDER_HELP,
                )
            ],
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.premium_info_help"),
                    callback_data=Callbacks.PREMIUM_INFO_HELP,
                )
            ],
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.buy_premium"),
                    callback_data=Callbacks.SUBSCRIBE_PREMIUM,
                )
            ],
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.privacy_info_help"),
                    callback_data=Callbacks.PRIVACY_INFO_HELP,
                )
            ],
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.choose_language"),
                    callback_data=Callbacks.CHOOSE_LANGUAGE,
                )
            ],
        ]
    )


def get_privacy_info_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.back_to_help"),
                    callback_data=Callbacks.BACK_TO_HELP,
                )
            ]
        ]
    )


def get_restart_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for restart confirmation."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.yes"), callback_data=Callbacks.RESTART_CONFIRM
                ),
                InlineKeyboardButton(
                    text=i18n.t("buttons.no"), callback_data=Callbacks.RESTART_CANCEL
                ),
            ]
        ]
    )


def get_stop_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for stop confirmation."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.t("buttons.yes"), callback_data=Callbacks.STOP_CONFIRM
                ),
                InlineKeyboardButton(
                    text=i18n.t("buttons.no"), callback_data=Callbacks.STOP_CANCEL
                ),
            ]
        ]
    )
