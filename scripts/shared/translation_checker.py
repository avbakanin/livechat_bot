#!/usr/bin/env python3
"""
Универсальный модуль для проверки переводов.
Устраняет дублирование кода в скриптах maintenance.
"""

import json
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class TranslationCheckResult:
    """Результат проверки перевода для одного языка."""
    language: str
    found: bool
    value: Optional[str] = None
    error: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None


@dataclass
class TranslationCheckSummary:
    """Сводка результатов проверки переводов."""
    total_languages: int
    successful_checks: int
    missing_translations: List[str]
    errors: List[str]
    results: List[TranslationCheckResult]


class TranslationChecker:
    """Универсальный класс для проверки переводов."""
    
    # Список поддерживаемых языков
    SUPPORTED_LANGUAGES = ['de', 'en', 'es', 'fr', 'it', 'pl', 'ru', 'sr', 'tr']
    
    def __init__(self, languages: Optional[List[str]] = None):
        """
        Инициализация проверщика переводов.
        
        Args:
            languages: Список языков для проверки. Если None, используется полный список.
        """
        self.languages = languages or self.SUPPORTED_LANGUAGES
    
    def check_translation_path(
        self, 
        path: str, 
        expected_value: Optional[str] = None,
        check_emoji: Optional[str] = None,
        check_keywords: Optional[List[str]] = None
    ) -> TranslationCheckSummary:
        """
        Проверить переводы по заданному пути в JSON.
        
        Args:
            path: Путь к значению в JSON (например, 'commands.status.premium_promo')
            expected_value: Ожидаемое значение (для проверки точного совпадения)
            check_emoji: Эмодзи, которое должно содержаться в переводе
            check_keywords: Ключевые слова, которые должны содержаться в переводе
            
        Returns:
            TranslationCheckSummary с результатами проверки
        """
        results = []
        missing_translations = []
        errors = []
        
        for lang in self.languages:
            result = self._check_single_translation(
                lang, path, expected_value, check_emoji, check_keywords
            )
            results.append(result)
            
            if not result.found:
                missing_translations.append(lang)
            if result.error:
                errors.append(f"{lang}: {result.error}")
        
        return TranslationCheckSummary(
            total_languages=len(self.languages),
            successful_checks=len(self.languages) - len(missing_translations) - len(errors),
            missing_translations=missing_translations,
            errors=errors,
            results=results
        )
    
    def _check_single_translation(
        self,
        language: str,
        path: str,
        expected_value: Optional[str] = None,
        check_emoji: Optional[str] = None,
        check_keywords: Optional[List[str]] = None
    ) -> TranslationCheckResult:
        """Проверить перевод для одного языка."""
        file_path = f"locales/{language}/translations.json"
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            return TranslationCheckResult(
                language=language,
                found=False,
                error=f"Файл {file_path} не найден"
            )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Получаем значение по пути
            value = self._get_nested_value(data, path)
            
            if value is None:
                return TranslationCheckResult(
                    language=language,
                    found=False,
                    error=f"Путь {path} не найден в JSON"
                )
            
            # Дополнительные проверки
            additional_info = {}
            
            if check_emoji and check_emoji not in value:
                additional_info['missing_emoji'] = check_emoji
            
            if check_keywords:
                missing_keywords = [
                    kw for kw in check_keywords 
                    if kw.lower() not in value.lower()
                ]
                if missing_keywords:
                    additional_info['missing_keywords'] = missing_keywords
            
            if expected_value and value != expected_value:
                additional_info['value_mismatch'] = {
                    'expected': expected_value,
                    'actual': value
                }
            
            return TranslationCheckResult(
                language=language,
                found=True,
                value=value,
                additional_info=additional_info if additional_info else None
            )
            
        except Exception as e:
            return TranslationCheckResult(
                language=language,
                found=False,
                error=f"Ошибка при чтении {file_path}: {e}"
            )
    
    def _get_nested_value(self, data: Dict, path: str) -> Optional[str]:
        """Получить значение по вложенному пути в JSON."""
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def print_summary(self, summary: TranslationCheckSummary, title: str = "Проверка переводов"):
        """Вывести сводку результатов проверки."""
        print(f"🔍 {title}...")
        print()
        
        for result in summary.results:
            if result.found:
                print(f"✅ {result.language.upper()}: {result.value}")
                
                if result.additional_info:
                    if 'missing_emoji' in result.additional_info:
                        print(f"   ❌ НЕ содержит эмодзи {result.additional_info['missing_emoji']}")
                    elif 'missing_keywords' in result.additional_info:
                        print(f"   ❌ НЕ содержит ключевые слова: {', '.join(result.additional_info['missing_keywords'])}")
                    elif 'value_mismatch' in result.additional_info:
                        print(f"   ⚠️ Значение не совпадает с ожидаемым")
            else:
                print(f"❌ {result.language.upper()}: {result.error}")
        
        print()
        print(f"📊 Результат проверки:")
        print(f"✅ Проверено: {summary.successful_checks}/{summary.total_languages}")
        
        if summary.missing_translations:
            print(f"❌ Отсутствуют переводы для: {', '.join(summary.missing_translations)}")
        
        if summary.errors:
            print(f"⚠️ Ошибки: {len(summary.errors)}")
            for error in summary.errors:
                print(f"   • {error}")
        
        if not summary.missing_translations and not summary.errors:
            print("🎉 Все переводы корректны!")
    
    def check_premium_promo(self, check_emoji: bool = False) -> TranslationCheckSummary:
        """Проверить переводы premium_promo."""
        path = "commands.status.premium_promo"
        check_emoji_str = "💎" if check_emoji else None
        
        summary = self.check_translation_path(path, check_emoji=check_emoji_str)
        
        title = "Проверяем переводы premium_promo с эмодзи во всех языках" if check_emoji else "Проверяем переводы premium_promo во всех языках"
        self.print_summary(summary, title)
        
        if check_emoji:
            print("💎 Все переводы теперь содержат эмодзи алмаза для привлечения внимания!")
        
        return summary
    
    def check_stop_success(self) -> TranslationCheckSummary:
        """Проверить переводы stop.success."""
        path = "commands.stop.success"
        check_emoji_str = "😢"
        check_keywords = ['return', 'ritorno', 'regreso', 'retour', 'powrót', 'возвращ', 'повратак', 'dönüş']
        
        summary = self.check_translation_path(
            path, 
            check_emoji=check_emoji_str,
            check_keywords=check_keywords
        )
        
        self.print_summary(summary, "Проверяем переводы stop.success во всех языках")
        print("😢 Все переводы теперь содержат сообщение о том, что нам жаль и мы ждем возвращения!")
        
        return summary
    
    def check_button_translation(self, button_key: str) -> TranslationCheckSummary:
        """Проверить переводы кнопки."""
        path = f"buttons.{button_key}"
        
        summary = self.check_translation_path(path)
        
        self.print_summary(summary, f"Проверяем переводы для кнопки '{button_key}'")
        
        if not summary.missing_translations:
            print("🎉 Все переводы добавлены корректно!")
        
        return summary
    
    def check_gender_buttons(self) -> TranslationCheckSummary:
        """Проверить кнопки выбора пола."""
        print("🔍 Проверяем кнопки выбора пола во всех языках...")
        print()
        
        female_summary = self.check_translation_path("buttons.choose_female")
        male_summary = self.check_translation_path("buttons.choose_male")
        
        for i, lang in enumerate(self.languages):
            female_result = female_summary.results[i]
            male_result = male_summary.results[i]
            
            print(f"✅ {lang.upper()}:")
            if female_result.found:
                print(f"  Девушка: {female_result.value}")
            else:
                print(f"  ❌ Девушка: {female_result.error}")
                
            if male_result.found:
                print(f"  Мужчина: {male_result.value}")
            else:
                print(f"  ❌ Мужчина: {male_result.error}")
            print()
        
        print("✅ Проверка завершена!")
        
        return female_summary
    
    def check_reset_info_with_emoji(self) -> TranslationCheckSummary:
        """Проверить переводы reset_info с эмодзи часов."""
        path = "commands.status.reset_info"
        check_emoji_str = "⏰"
        
        summary = self.check_translation_path(path, check_emoji=check_emoji_str)
        
        self.print_summary(summary, "Проверяем переводы reset_info с эмодзи часов во всех языках")
        print("⏰ Все переводы теперь содержат эмодзи часов для указания времени сброса лимита!")
        
        return summary


# Удобные функции для обратной совместимости
def check_premium_promo():
    """Проверить переводы premium_promo во всех языках."""
    checker = TranslationChecker()
    checker.check_premium_promo(check_emoji=False)


def check_premium_promo_with_emoji():
    """Проверить переводы premium_promo с эмодзи во всех языках."""
    checker = TranslationChecker()
    checker.check_premium_promo(check_emoji=True)


def check_stop_success_translations():
    """Проверить переводы stop.success во всех языках."""
    checker = TranslationChecker()
    checker.check_stop_success()


def check_translations():
    """Проверить переводы для кнопки 'extend_premium'."""
    checker = TranslationChecker()
    checker.check_button_translation('extend_premium')


def check_gender_buttons():
    """Проверить кнопки выбора пола во всех языках."""
    checker = TranslationChecker()
    checker.check_gender_buttons()


def check_reset_info_with_emoji():
    """Проверить переводы reset_info с эмодзи часов во всех языках."""
    checker = TranslationChecker()
    checker.check_reset_info_with_emoji()


if __name__ == "__main__":
    # Демонстрация использования
    checker = TranslationChecker()
    
    print("=== Демонстрация TranslationChecker ===")
    print()
    
    # Проверка premium_promo
    checker.check_premium_promo(check_emoji=False)
    print()
    
    # Проверка stop.success
    checker.check_stop_success()
    print()
    
    # Проверка кнопки
    checker.check_button_translation('extend_premium')
