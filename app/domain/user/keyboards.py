"""
User domain keyboards - Telegram inline keyboards.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_consent_keyboard() -> InlineKeyboardMarkup:
    """Get consent agreement keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Согласен с политикой конфиденциальности", callback_data="consent_agree")],
        [InlineKeyboardButton(text="Читать политику", url="https://your-site.com/privacy")]
    ])


def get_consent_given_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard after consent is given."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Выбрать девушку 😊", callback_data="gender_female"),
            InlineKeyboardButton(text="Выбрать молодого человека 😉", callback_data="gender_male")
        ],
        [InlineKeyboardButton(text="Купить премиум 💳", callback_data="subscribe_premium")]
    ])


def get_gender_keyboard() -> InlineKeyboardMarkup:
    """Get gender selection keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Девушка 😊", callback_data="gender_female"),
            InlineKeyboardButton(text="Молодой человек 😉", callback_data="gender_male")
        ]
    ])


def get_gender_change_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Get gender change confirmation keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, сменить пол", callback_data="gender_change_confirm"),
            InlineKeyboardButton(text="Отмена", callback_data="gender_change_cancel")
        ]
    ])


def get_help_keyboard() -> InlineKeyboardMarkup:
    """Get help keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎭 Выбрать пол компаньона", callback_data="choose_gender_help")],
        [InlineKeyboardButton(text="💎 Информация о премиуме", callback_data="premium_info_help")],
        [InlineKeyboardButton(text="📝 Политика конфиденциальности", callback_data="privacy_info_help")]
    ])


def get_privacy_info_keyboard() -> InlineKeyboardMarkup:
    """Get privacy info keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад к справке", callback_data="back_to_help")]
    ])
