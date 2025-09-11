"""
Internationalization (i18n) system for the Telegram bot.
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class I18nManager:
    """Internationalization manager for handling translations."""
    
    def __init__(self, translations_file: str = None):
        """Initialize the i18n manager."""
        if translations_file is None:
            # Default path to translations file
            current_dir = Path(__file__).parent
            translations_file = current_dir / "i18n" / "translations.json"
        
        self.translations_file = Path(translations_file)
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.default_language = "ru"
        self.current_language = self.default_language
        
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Load translations from JSON file."""
        try:
            if self.translations_file.exists():
                with open(self.translations_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            else:
                raise FileNotFoundError(f"Translations file not found: {self.translations_file}")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading translations: {e}")
            self.translations = {}
    
    def set_language(self, language: str) -> None:
        """Set the current language."""
        if language in self.translations:
            self.current_language = language
        else:
            print(f"Language '{language}' not found, using default: {self.default_language}")
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
            i18n.t("commands.start.welcome", free_limit=100)
        """
        try:
            # Split the key by dots to navigate the nested structure
            keys = key.split('.')
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
        base_language = user_language_code.split('-')[0].lower()
        
        # Map to supported languages
        language_mapping = {
            'ru': 'ru',
            'en': 'en',
            'uk': 'ru',  # Ukrainian -> Russian (closest)
            'be': 'ru',  # Belarusian -> Russian (closest)
            'kk': 'ru',  # Kazakh -> Russian (closest)
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
