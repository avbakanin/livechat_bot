"""
Security logging utilities.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class SecurityEvent:
    """Security event data structure."""
    
    timestamp: datetime
    event_type: str
    user_id: Optional[int]
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class SecurityLogger:
    """Enhanced security logging with structured events."""
    
    def __init__(self, log_file: str = "security.log"):
        """
        Initialize security logger.
        
        Args:
            log_file: Path to security log file
        """
        self.log_file = log_file
        self._setup_logger()
        
    def _setup_logger(self) -> None:
        """Setup security logger."""
        self.logger = logging.getLogger("security")
        self.logger.setLevel(logging.WARNING)
        
        # Удаляем существующие обработчики
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Файловый обработчик для безопасности
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.WARNING)
        
        # Форматтер для структурированных логов
        formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        
        # Консольный обработчик для критических событий
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.CRITICAL)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log_suspicious_content(
        self, 
        user_id: int, 
        content: str, 
        patterns_found: list,
        sanitized_content: str
    ) -> None:
        """Log suspicious content detection."""
        event = SecurityEvent(
            timestamp=datetime.utcnow(),
            event_type="SUSPICIOUS_CONTENT",
            user_id=user_id,
            severity="MEDIUM",
            description=f"Suspicious content detected from user {user_id}",
            details={
                "patterns_found": patterns_found,
                "original_length": len(content),
                "sanitized_length": len(sanitized_content),
                "content_preview": content[:100] + "..." if len(content) > 100 else content
            }
        )
        
        self._log_event(event)

    def log_flood_attempt(
        self, 
        user_id: int, 
        message_count: int, 
        time_window: float
    ) -> None:
        """Log flood attempt."""
        event = SecurityEvent(
            timestamp=datetime.utcnow(),
            event_type="FLOOD_ATTEMPT",
            user_id=user_id,
            severity="HIGH",
            description=f"Flood attempt detected from user {user_id}",
            details={
                "message_count": message_count,
                "time_window_seconds": time_window,
                "messages_per_second": message_count / time_window if time_window > 0 else 0
            }
        )
        
        self._log_event(event)

    def log_long_message(
        self, 
        user_id: int, 
        message_length: int, 
        limit: int
    ) -> None:
        """Log suspiciously long message."""
        severity = "HIGH" if message_length > limit * 2 else "MEDIUM"
        
        event = SecurityEvent(
            timestamp=datetime.utcnow(),
            event_type="LONG_MESSAGE",
            user_id=user_id,
            severity=severity,
            description=f"Very long message from user {user_id}",
            details={
                "message_length": message_length,
                "limit": limit,
                "excess": message_length - limit
            }
        )
        
        self._log_event(event)

    def log_repetitive_content(
        self, 
        user_id: int, 
        content: str, 
        repetition_type: str
    ) -> None:
        """Log repetitive content."""
        event = SecurityEvent(
            timestamp=datetime.utcnow(),
            event_type="REPETITIVE_CONTENT",
            user_id=user_id,
            severity="MEDIUM",
            description=f"Repetitive content from user {user_id}",
            details={
                "repetition_type": repetition_type,
                "content_length": len(content),
                "content_preview": content[:50] + "..." if len(content) > 50 else content
            }
        )
        
        self._log_event(event)

    def log_multiple_security_flags(
        self, 
        user_id: int, 
        flags: list, 
        security_score: int
    ) -> None:
        """Log user with multiple security flags."""
        severity = "CRITICAL" if security_score < 30 else "HIGH"
        
        event = SecurityEvent(
            timestamp=datetime.utcnow(),
            event_type="MULTIPLE_SECURITY_FLAGS",
            user_id=user_id,
            severity=severity,
            description=f"User {user_id} has multiple security flags",
            details={
                "flags": flags,
                "security_score": security_score,
                "flag_count": len(flags)
            }
        )
        
        self._log_event(event)

    def log_potential_spam(
        self, 
        user_id: int, 
        content: str, 
        spam_indicators: list
    ) -> None:
        """Log potential spam."""
        event = SecurityEvent(
            timestamp=datetime.utcnow(),
            event_type="POTENTIAL_SPAM",
            user_id=user_id,
            severity="MEDIUM",
            description=f"Potential spam from user {user_id}",
            details={
                "spam_indicators": spam_indicators,
                "content_length": len(content),
                "content_preview": content[:100] + "..." if len(content) > 100 else content
            }
        )
        
        self._log_event(event)

    def log_security_metric(
        self, 
        metric_name: str, 
        value: Any, 
        threshold: Optional[Any] = None
    ) -> None:
        """Log security-related metrics."""
        severity = "MEDIUM"
        if threshold is not None:
            if isinstance(value, (int, float)) and isinstance(threshold, (int, float)):
                if value > threshold * 2:
                    severity = "HIGH"
                elif value > threshold:
                    severity = "MEDIUM"
                else:
                    severity = "LOW"
        
        event = SecurityEvent(
            timestamp=datetime.utcnow(),
            event_type="SECURITY_METRIC",
            user_id=None,
            severity=severity,
            description=f"Security metric: {metric_name}",
            details={
                "metric_name": metric_name,
                "value": value,
                "threshold": threshold
            }
        )
        
        self._log_event(event)

    def log_access_denied(
        self, 
        user_id: int, 
        reason: str, 
        attempted_action: str
    ) -> None:
        """Log access denied event."""
        event = SecurityEvent(
            timestamp=datetime.utcnow(),
            event_type="ACCESS_DENIED",
            user_id=user_id,
            severity="MEDIUM",
            description=f"Access denied for user {user_id}",
            details={
                "reason": reason,
                "attempted_action": attempted_action
            }
        )
        
        self._log_event(event)

    def _log_event(self, event: SecurityEvent) -> None:
        """Log security event."""
        # Преобразуем в словарь для JSON логирования
        event_dict = asdict(event)
        event_dict['timestamp'] = event.timestamp.isoformat()
        
        # Логируем в зависимости от уровня серьезности
        if event.severity == "CRITICAL":
            self.logger.critical(json.dumps(event_dict, ensure_ascii=False))
        elif event.severity == "HIGH":
            self.logger.error(json.dumps(event_dict, ensure_ascii=False))
        elif event.severity == "MEDIUM":
            self.logger.warning(json.dumps(event_dict, ensure_ascii=False))
        else:
            self.logger.info(json.dumps(event_dict, ensure_ascii=False))

    def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get security summary for the last N hours.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Security summary dictionary
        """
        # В реальной реализации здесь был бы анализ лог-файла
        # Для демонстрации возвращаем заглушку
        return {
            "period_hours": hours,
            "total_events": 0,
            "critical_events": 0,
            "high_events": 0,
            "medium_events": 0,
            "low_events": 0,
            "most_active_users": [],
            "common_threats": []
        }


# Глобальный экземпляр логгера безопасности
security_logger = SecurityLogger()
