from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from shared.middlewares.i18n_middleware import I18nMiddleware


def get_consent_keyboard(i18n: I18nMiddleware) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=i18n.t("buttons.agree_privacy"), callback_data="consent_agree")],
            [InlineKeyboardButton(text=i18n.t("buttons.read_privacy"), url="https://your-site.com/privacy")],
        ]
    )


def get_consent_given_keyboard(i18n: I18nMiddleware) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=i18n.t("buttons.choose_female"), callback_data="gender_female"),
                InlineKeyboardButton(text=i18n.t("buttons.choose_male"), callback_data="gender_male"),
            ],
            [InlineKeyboardButton(text=i18n.t("buttons.buy_premium"), callback_data="subscribe_premium")],
        ]
    )


def get_gender_keyboard(i18n: I18nMiddleware) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=i18n.t("buttons.choose_female"), callback_data="gender_female"),
                InlineKeyboardButton(text=i18n.t("buttons.choose_male"), callback_data="gender_male"),
            ]
        ]
    )


def get_gender_change_confirmation_keyboard(i18n: I18nMiddleware) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=i18n.t("buttons.yes_change"), callback_data="gender_change_confirm"),
                InlineKeyboardButton(text=i18n.t("buttons.cancel"), callback_data="gender_change_cancel"),
            ]
        ]
    )


def get_help_keyboard(i18n: I18nMiddleware) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=i18n.t("buttons.choose_gender_help"), callback_data="choose_gender_help")],
            [InlineKeyboardButton(text=i18n.t("buttons.premium_info_help"), callback_data="premium_info_help")],
            [InlineKeyboardButton(text=i18n.t("buttons.privacy_info_help"), callback_data="privacy_info_help")],
        ]
    )


def get_privacy_info_keyboard(i18n: I18nMiddleware) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=i18n.t("buttons.buy_premium"), callback_data="back_to_help")]]
    )
