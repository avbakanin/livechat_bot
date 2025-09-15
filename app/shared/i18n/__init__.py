import json
from pathlib import Path
from typing import Any, Dict, Optional

"""Internationalization manager for handling translations."""


class I18nManager:
    def __init__(self):
        # Default path to locales directory
        current_dir = Path(__file__).parent.parent.parent.parent
        locales_dir = current_dir / "locales"

        self.locales_dir = Path(locales_dir)
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.default_language = "ru"
        self.current_language = self.default_language

        self._load_translations()

    def _load_translations(self) -> None:
        try:
            if not self.locales_dir.exists():
                raise FileNotFoundError(
                    f"Locales directory not found: {self.locales_dir}"
                )

            # Load translations for each language
            for language_dir in self.locales_dir.iterdir():
                if language_dir.is_dir():
                    translation_file = language_dir / "translations.json"
                    if translation_file.exists():
                        with open(translation_file, "r", encoding="utf-8") as f:
                            self.translations[language_dir.name] = json.load(f)
                    else:
                        print(
                            f"Warning: Translation file not found: {translation_file}"
                        )

            if not self.translations:
                raise FileNotFoundError(
                    f"No translation files found in: {self.locales_dir}"
                )

        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading translations: {e}")
            self.translations = {}

    def set_language(self, language: str) -> None:
        """Set the current language."""
        if language in self.translations:
            self.current_language = language
        else:
            print(
                f"Language '{language}' not found, using default: {self.default_language}"
            )
            self.current_language = self.default_language

    def get_language(self) -> str:
        """Get the current language."""
        return self.current_language

    def get_available_languages(self) -> list:
        """Get list of available languages."""
        return list(self.translations.keys())

    def t(self, key: str, **kwargs) -> str:
        """
        Get translation for a key.

        Args:
            key: Translation key in format "section.subsection.key"
            **kwargs: Variables to format into the translation

        Returns:
            Translated string

        Example:
            i18n.t("commands.start.welcome", free_limit=50)
        """
        try:
            # Split the key by dots to navigate the nested structure
            keys = key.split(".")
            translation = self.translations[self.current_language]

            # Navigate through the nested structure
            for k in keys:
                if isinstance(translation, dict) and k in translation:
                    translation = translation[k]
                else:
                    # Fallback to default language if key not found
                    if self.current_language != self.default_language:
                        translation = self.translations[self.default_language]
                        for k in keys:
                            if isinstance(translation, dict) and k in translation:
                                translation = translation[k]
                            else:
                                return f"[{key}]"  # Key not found
                    else:
                        return f"[{key}]"  # Key not found

            # Format the translation with provided variables
            if isinstance(translation, str):
                try:
                    return translation.format(**kwargs)
                except KeyError as e:
                    print(f"Missing variable {e} for key '{key}'")
                    return translation
            else:
                return str(translation)

        except Exception as e:
            print(f"Error getting translation for key '{key}': {e}")
            return f"[{key}]"

    def get_user_language(self, user_language_code: Optional[str] = None) -> str:
        """
        Determine user language from Telegram language code.

        Args:
            user_language_code: Telegram user language code (e.g., 'en', 'ru', 'en-US')

        Returns:
            Supported language code
        """
        if not user_language_code:
            return self.default_language

        # Extract base language code (e.g., 'en' from 'en-US')
        base_language = user_language_code.split("-")[0].lower()

        # Map to supported languages
        language_mapping = {
            "ru": "ru",
            "en": "en",
            "uk": "ru",  # Ukrainian -> Russian (closest)
            "be": "ru",  # Belarusian -> Russian (closest)
            "kk": "ru",  # Kazakh -> Russian (closest)
        }

        return language_mapping.get(base_language, self.default_language)


# Global i18n instance
i18n = I18nManager()


def get_translation(key: str, **kwargs) -> str:
    """
    Convenience function to get translation.

    Args:
        key: Translation key
        **kwargs: Variables to format into the translation

    Returns:
        Translated string
    """
    return i18n.t(key, **kwargs)


def set_user_language(user_language_code: Optional[str] = None) -> str:
    """
    Convenience function to set user language.

    Args:
        user_language_code: Telegram user language code

    Returns:
        Set language code
    """
    language = i18n.get_user_language(user_language_code)
    i18n.set_language(language)
    return language
