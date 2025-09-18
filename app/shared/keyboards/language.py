"""
Language selection keyboard.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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
                text="🇷🇺 Русский",
                callback_data="lang_ru"
            ),
            InlineKeyboardButton(
                text="🇬🇧 English",
                callback_data="lang_en"
            )
        ],
        [
            InlineKeyboardButton(
                text="🇩🇪 Deutsch",
                callback_data="lang_de"
            ),
            InlineKeyboardButton(
                text="🇪🇸 Español",
                callback_data="lang_es"
            )
        ],
        [
            InlineKeyboardButton(
                text="🇷🇸 Српски",
                callback_data="lang_sr"
            ),
            InlineKeyboardButton(
                text="🇫🇷 Français",
                callback_data="lang_fr"
            )
        ],
        [
            InlineKeyboardButton(
                text="🇮🇹 Italiano",
                callback_data="lang_it"
            ),
            InlineKeyboardButton(
                text="🇹🇷 Türkçe",
                callback_data="lang_tr"
            )
        ],
        [
            InlineKeyboardButton(
                text="🇵🇱 Polski",
                callback_data="lang_pl"
            )
        ],
        [
            InlineKeyboardButton(
                text=i18n.t("buttons.back_to_help"),
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
        "de": "🇩🇪 Deutsch",
        "es": "🇪🇸 Español",
        "sr": "🇷🇸 Српски",
        "fr": "🇫🇷 Français",
        "it": "🇮🇹 Italiano",
        "tr": "🇹🇷 Türkçe",
        "pl": "🇵🇱 Polski"
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
                text=f"{language_names['de']} {'✅' if current_language == 'de' else ''}",
                callback_data="lang_de"
            ),
            InlineKeyboardButton(
                text=f"{language_names['es']} {'✅' if current_language == 'es' else ''}",
                callback_data="lang_es"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{language_names['sr']} {'✅' if current_language == 'sr' else ''}",
                callback_data="lang_sr"
            ),
            InlineKeyboardButton(
                text=f"{language_names['fr']} {'✅' if current_language == 'fr' else ''}",
                callback_data="lang_fr"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{language_names['it']} {'✅' if current_language == 'it' else ''}",
                callback_data="lang_it"
            ),
            InlineKeyboardButton(
                text=f"{language_names['tr']} {'✅' if current_language == 'tr' else ''}",
                callback_data="lang_tr"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{language_names['pl']} {'✅' if current_language == 'pl' else ''}",
                callback_data="lang_pl"
            )
        ],
        [
            InlineKeyboardButton(
                text=i18n.t("buttons.back_to_help"),
                callback_data="back_to_help"
            )
        ]
    ])
    
    return keyboard
