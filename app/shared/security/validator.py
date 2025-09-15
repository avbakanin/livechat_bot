"""
Security validation utilities.
"""

import re
import logging
from typing import Optional, Dict, Any
from datetime import datetime


class SecurityValidator:
    """Validates user input and behavior for security threats."""

    def __init__(self):
        """Initialize security validator."""
        self.suspicious_activities = {}
        self.rate_limits = {}

    def validate_message_content(
        self, 
        text: str, 
        user_id: int, 
        message_length_limit: int = 2500
    ) -> Dict[str, Any]:
        """
        Validate message content for security threats.
        
        Args:
            text: Message text to validate
            user_id: User ID
            message_length_limit: Maximum allowed message length
            
        Returns:
            Validation result dictionary
        """
        result = {
            "is_valid": True,
            "sanitized_text": text,
            "warnings": [],
            "security_flags": []
        }

        if not text:
            result["is_valid"] = False
            result["warnings"].append("Empty message")
            return result

        # Проверка длины сообщения
        if len(text) > message_length_limit:
            result["is_valid"] = False
            result["warnings"].append(f"Message too long: {len(text)} > {message_length_limit}")
            result["security_flags"].append("LONG_MESSAGE")

        # Проверка на очень длинные сообщения (подозрительно)
        if len(text) > 1000:
            result["security_flags"].append("VERY_LONG_MESSAGE")
            self._log_suspicious_length(user_id, len(text))

        # Проверка на повторяющиеся символы (возможный спам)
        if self._has_repetitive_content(text):
            result["security_flags"].append("REPETITIVE_CONTENT")
            self._log_repetitive_content(user_id, text)

        # Проверка на подозрительные паттерны
        suspicious_patterns = self._detect_suspicious_patterns(text)
        if suspicious_patterns:
            result["security_flags"].extend(suspicious_patterns)
            self._log_suspicious_patterns(user_id, text, suspicious_patterns)

        # Проверка на потенциальный спам
        if self._is_potential_spam(text):
            result["security_flags"].append("POTENTIAL_SPAM")
            self._log_potential_spam(user_id, text)

        return result

    def validate_user_behavior(
        self, 
        user_id: int, 
        action_type: str,
        additional_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Validate user behavior for suspicious patterns.
        
        Args:
            user_id: User ID
            action_type: Type of action (message, command, etc.)
            additional_data: Additional data for validation
            
        Returns:
            Validation result dictionary
        """
        result = {
            "is_valid": True,
            "warnings": [],
            "security_flags": []
        }

        current_time = datetime.utcnow()

        # Инициализация данных пользователя
        if user_id not in self.suspicious_activities:
            self.suspicious_activities[user_id] = {
                "message_count": 0,
                "last_message_time": None,
                "rapid_messages": 0,
                "suspicious_flags": [],
                "first_seen": current_time
            }

        user_data = self.suspicious_activities[user_id]

        # Проверка на быстрые сообщения (флуд)
        if action_type == "message":
            user_data["message_count"] += 1
            
            if user_data["last_message_time"]:
                time_diff = (current_time - user_data["last_message_time"]).total_seconds()
                if time_diff < 1:  # Менее секунды между сообщениями
                    user_data["rapid_messages"] += 1
                    result["security_flags"].append("RAPID_MESSAGES")
                    
                    if user_data["rapid_messages"] > 5:
                        result["is_valid"] = False
                        result["warnings"].append("Too many rapid messages")
                        self._log_flood_attempt(user_id, user_data["rapid_messages"])

            user_data["last_message_time"] = current_time

        # Проверка на подозрительную активность
        if len(user_data["suspicious_flags"]) > 3:
            result["security_flags"].append("MULTIPLE_SUSPICIOUS_FLAGS")
            self._log_multiple_flags(user_id, user_data["suspicious_flags"])

        return result

    def _has_repetitive_content(self, text: str) -> bool:
        """Check for repetitive content patterns."""
        # Проверка на повторяющиеся символы (только для длинных сообщений)
        if len(text) > 20:
            char_counts = {}
            for char in text:
                char_counts[char] = char_counts.get(char, 0) + 1
            
            # Если какой-то символ составляет более 60% текста
            for char, count in char_counts.items():
                if count / len(text) > 0.6 and char not in ' \n\t':
                    return True

        # Проверка на повторяющиеся слова (только для сообщений с несколькими словами)
        words = text.split()
        if len(words) > 5:  # Увеличил порог
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            # Если какое-то слово повторяется более 70% раз
            for word, count in word_counts.items():
                if count / len(words) > 0.7 and len(word) > 3:  # Увеличил пороги
                    return True

        return False

    def _detect_suspicious_patterns(self, text: str) -> list:
        """Detect suspicious patterns in text."""
        patterns = []
        
        # Проверка на потенциальные команды
        if re.search(r'[<>`|]', text):
            patterns.append("SUSPICIOUS_SYMBOLS")
        
        # Проверка на URL
        if re.search(r'https?://', text):
            patterns.append("CONTAINS_URL")
        
        # Проверка на email
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            patterns.append("CONTAINS_EMAIL")
        
        # Проверка на телефон
        if re.search(r'\+?[1-9]\d{1,14}', text):
            patterns.append("CONTAINS_PHONE")
        
        return patterns

    def _is_potential_spam(self, text: str) -> bool:
        """Check if text might be spam."""
        # Проверка на капс (только для длинных сообщений)
        if len(text) > 20 and text.isupper():
            return True
        
        # Проверка на много восклицательных знаков (более 20% текста)
        if len(text) > 10 and text.count('!') > len(text) * 0.2:
            return True
        
        # Проверка на много вопросительных знаков (более 20% текста)
        if len(text) > 10 and text.count('?') > len(text) * 0.2:
            return True
        
        # Проверка на повторяющиеся символы (более 50% текста)
        if len(text) > 5:
            char_counts = {}
            for char in text:
                char_counts[char] = char_counts.get(char, 0) + 1
            
            for char, count in char_counts.items():
                if count / len(text) > 0.5 and char not in ' \n\t':
                    return True
        
        return False

    def _log_suspicious_length(self, user_id: int, length: int) -> None:
        """Log suspicious message length."""
        logging.warning(
            f"🚨 SECURITY: User {user_id} sent very long message: {length} characters"
        )

    def _log_repetitive_content(self, user_id: int, text: str) -> None:
        """Log repetitive content."""
        logging.warning(
            f"🚨 SECURITY: User {user_id} sent repetitive content: {text[:50]}..."
        )

    def _log_suspicious_patterns(self, user_id: int, text: str, patterns: list) -> None:
        """Log suspicious patterns."""
        logging.warning(
            f"🚨 SECURITY: User {user_id} sent text with suspicious patterns {patterns}: {text[:100]}..."
        )

    def _log_potential_spam(self, user_id: int, text: str) -> None:
        """Log potential spam."""
        logging.warning(
            f"🚨 SECURITY: User {user_id} sent potential spam: {text[:50]}..."
        )

    def _log_flood_attempt(self, user_id: int, rapid_count: int) -> None:
        """Log flood attempt."""
        logging.warning(
            f"🚨 SECURITY: User {user_id} attempted flood with {rapid_count} rapid messages"
        )

    def _log_multiple_flags(self, user_id: int, flags: list) -> None:
        """Log multiple suspicious flags."""
        logging.warning(
            f"🚨 SECURITY: User {user_id} has multiple suspicious flags: {flags}"
        )

    def get_user_security_score(self, user_id: int) -> Dict[str, Any]:
        """
        Get security score for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Security score dictionary
        """
        if user_id not in self.suspicious_activities:
            return {
                "score": 100,
                "flags": [],
                "risk_level": "LOW"
            }

        user_data = self.suspicious_activities[user_id]
        flags = user_data["suspicious_flags"]
        
        # Расчет скора (100 - количество флагов * 10)
        score = max(0, 100 - len(flags) * 10)
        
        # Определение уровня риска
        if score >= 80:
            risk_level = "LOW"
        elif score >= 50:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        return {
            "score": score,
            "flags": flags,
            "risk_level": risk_level,
            "message_count": user_data["message_count"],
            "rapid_messages": user_data["rapid_messages"]
        }


# Глобальный экземпляр валидатора
security_validator = SecurityValidator()
