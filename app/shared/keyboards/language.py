"""
Language selection keyboard.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from shared.i18n import i18n


def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Create language selection keyboard.
    
    Returns:
        InlineKeyboardMarkup with language options
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=i18n.t("buttons.language_ru"),
                callback_data="lang_ru"
            ),
            InlineKeyboardButton(
                text=i18n.t("buttons.language_en"),
                callback_data="lang_en"
            )
        ],
        [
            InlineKeyboardButton(
                text=i18n.t("buttons.language_sr"),
                callback_data="lang_sr"
            ),
            InlineKeyboardButton(
                text=i18n.t("buttons.language_de"),
                callback_data="lang_de"
            )
        ],
        [
            InlineKeyboardButton(
                text=i18n.t("buttons.language_es"),
                callback_data="lang_es"
            )
        ],
        [
            InlineKeyboardButton(
                text=i18n.t("buttons.back"),
                callback_data="back_to_help"
            )
        ]
    ])
    
    return keyboard


def get_language_keyboard_with_current(current_language: str) -> InlineKeyboardMarkup:
    """
    Create language selection keyboard with current language marked.
    
    Args:
        current_language: Current language code
        
    Returns:
        InlineKeyboardMarkup with language options
    """
    # Language names mapping
    language_names = {
        "ru": "🇷🇺 Русский",
        "en": "🇬🇧 English", 
        "sr": "🇷🇸 Српски",
        "de": "🇩🇪 Deutsch",
        "es": "🇪🇸 Español"
    }
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{language_names['ru']} {'✅' if current_language == 'ru' else ''}",
                callback_data="lang_ru"
            ),
            InlineKeyboardButton(
                text=f"{language_names['en']} {'✅' if current_language == 'en' else ''}",
                callback_data="lang_en"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{language_names['sr']} {'✅' if current_language == 'sr' else ''}",
                callback_data="lang_sr"
            ),
            InlineKeyboardButton(
                text=f"{language_names['de']} {'✅' if current_language == 'de' else ''}",
                callback_data="lang_de"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{language_names['es']} {'✅' if current_language == 'es' else ''}",
                callback_data="lang_es"
            )
        ],
        [
            InlineKeyboardButton(
                text=i18n.t("buttons.back"),
                callback_data="back_to_help"
            )
        ]
    ])
    
    return keyboard
