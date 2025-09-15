"""
Text sanitization utilities for security.
"""

import re
import logging
from typing import Optional


class TextSanitizer:
    """Sanitizes user input text for security."""

    # Подозрительные паттерны для обнаружения потенциальных атак
    SUSPICIOUS_PATTERNS = [
        # HTML/JavaScript инъекции
        r'<script.*?>.*?</script>',
        r'<iframe.*?>.*?</iframe>',
        r'<object.*?>.*?</object>',
        r'<embed.*?>.*?</embed>',
        r'<link.*?>.*?</link>',
        r'<meta.*?>.*?</meta>',
        
        # JavaScript протоколы
        r'javascript:',
        r'vbscript:',
        r'data:text/html',
        r'data:text/javascript',
        
        # SQL инъекции (дополнительная защита)
        r'union\s+select',
        r'drop\s+table',
        r'delete\s+from',
        r'insert\s+into',
        r'update\s+set',
        r'alter\s+table',
        
        # Команды системы
        r'<\|.*?\|>',  # Команды в угловых скобках
        r'`.*?`',      # Команды в обратных кавычках
        
        # Подозрительные символы
        r'[<>"\']',    # HTML символы
        r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]',  # Контрольные символы
        
        # Ссылки на внешние ресурсы
        r'https?://[^\s]+',
        r'ftp://[^\s]+',
        r'file://[^\s]+',
    ]

    # Разрешенные HTML теги (только для статического контента)
    ALLOWED_HTML_TAGS = {
        'b', 'strong', 'i', 'em', 'u', 'ins', 's', 'strike', 'del',
        'a', 'code', 'pre', 'tg-spoiler'
    }

    def __init__(self, log_suspicious: bool = True):
        """
        Initialize sanitizer.
        
        Args:
            log_suspicious: Whether to log suspicious content detection
        """
        self.log_suspicious = log_suspicious
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for pattern in self.SUSPICIOUS_PATTERNS
        ]

    def sanitize_text(self, text: str, user_id: Optional[int] = None) -> str:
        """
        Sanitize user input text.
        
        Args:
            text: Input text to sanitize
            user_id: User ID for logging (optional)
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""

        original_text = text
        sanitized_text = text

        # Проверка на подозрительные паттерны
        suspicious_found = []
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                suspicious_found.append(pattern.pattern)
                # Удаляем найденные подозрительные элементы
                sanitized_text = pattern.sub('', sanitized_text)

        # Удаление HTML тегов (кроме разрешенных)
        sanitized_text = self._remove_html_tags(sanitized_text)

        # Очистка от лишних пробелов
        sanitized_text = re.sub(r'\s+', ' ', sanitized_text).strip()

        # Логирование подозрительной активности
        if suspicious_found and self.log_suspicious:
            self._log_suspicious_activity(
                user_id, original_text, sanitized_text, suspicious_found
            )

        return sanitized_text

    def _remove_html_tags(self, text: str) -> str:
        """Remove HTML tags except allowed ones."""
        # Сначала защищаем разрешенные теги
        protected_tags = {}
        tag_counter = 0
        
        for tag in self.ALLOWED_HTML_TAGS:
            pattern = f'<{tag}[^>]*>.*?</{tag}>'
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                placeholder = f"__PROTECTED_TAG_{tag_counter}__"
                protected_tags[placeholder] = match.group()
                text = text.replace(match.group(), placeholder)
                tag_counter += 1

        # Удаляем все оставшиеся HTML теги
        text = re.sub(r'<[^>]+>', '', text)

        # Восстанавливаем защищенные теги
        for placeholder, original_tag in protected_tags.items():
            text = text.replace(placeholder, original_tag)

        return text

    def _log_suspicious_activity(
        self, 
        user_id: Optional[int], 
        original_text: str, 
        sanitized_text: str, 
        patterns_found: list
    ) -> None:
        """Log suspicious activity."""
        logging.warning(
            f"🚨 SECURITY ALERT: Suspicious content detected from user {user_id}. "
            f"Patterns: {patterns_found}. "
            f"Original length: {len(original_text)}, "
            f"Sanitized length: {len(sanitized_text)}"
        )

    def is_safe_text(self, text: str) -> bool:
        """
        Check if text is safe (no suspicious patterns).
        
        Args:
            text: Text to check
            
        Returns:
            True if text is safe, False otherwise
        """
        if not text:
            return True

        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return False
        return True

    def get_text_stats(self, text: str) -> dict:
        """
        Get statistics about text content.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with text statistics
        """
        if not text:
            return {
                "length": 0,
                "has_html": False,
                "has_suspicious": False,
                "suspicious_patterns": []
            }

        stats = {
            "length": len(text),
            "has_html": bool(re.search(r'<[^>]+>', text)),
            "has_suspicious": False,
            "suspicious_patterns": []
        }

        for pattern in self.compiled_patterns:
            if pattern.search(text):
                stats["has_suspicious"] = True
                stats["suspicious_patterns"].append(pattern.pattern)

        return stats


# Глобальный экземпляр санитайзера
text_sanitizer = TextSanitizer()
