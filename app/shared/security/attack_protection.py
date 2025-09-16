"""
Advanced attack protection system.
"""

import re
import time
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class AttackType(Enum):
    """Types of attacks to protect against."""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    BRUTE_FORCE = "brute_force"
    DDOS = "ddos"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"


@dataclass
class AttackAttempt:
    """Attack attempt data."""
    attack_type: AttackType
    user_id: Optional[int]
    ip_address: Optional[str]
    timestamp: datetime
    payload: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL


class SQLInjectionProtection:
    """Protection against SQL injection attacks."""
    
    def __init__(self):
        self.sql_patterns = [
            r"union\s+select",
            r"drop\s+table",
            r"delete\s+from",
            r"insert\s+into",
            r"update\s+set",
            r"alter\s+table",
            r"create\s+table",
            r"exec\s*\(",
            r"execute\s*\(",
            r"sp_executesql",
            r"xp_cmdshell",
            r"';.*--",
            r"'.*or.*'1'='1",
            r"'.*or.*1=1",
            r"'.*union.*select",
        ]
        
    def detect_sql_injection(self, input_text: str) -> bool:
        """Detect SQL injection attempts."""
        input_lower = input_text.lower()
        
        for pattern in self.sql_patterns:
            if re.search(pattern, input_lower, re.IGNORECASE):
                return True
                
        return False
        
    def sanitize_sql_input(self, input_text: str) -> str:
        """Sanitize input for SQL queries."""
        # Remove SQL injection patterns
        sanitized = input_text
        for pattern in self.sql_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
            
        # Escape single quotes
        sanitized = sanitized.replace("'", "''")
        
        return sanitized


class XSSProtection:
    """Protection against XSS attacks."""
    
    def __init__(self):
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"expression\s*\(",
            r"url\s*\(",
        ]
        
    def detect_xss(self, input_text: str) -> bool:
        """Detect XSS attempts."""
        for pattern in self.xss_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                return True
                
        return False
        
    def sanitize_xss_input(self, input_text: str) -> str:
        """Sanitize input to prevent XSS."""
        sanitized = input_text
        
        # Remove script tags and dangerous attributes
        for pattern in self.xss_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
            
        # HTML encode dangerous characters
        sanitized = sanitized.replace('<', '&lt;')
        sanitized = sanitized.replace('>', '&gt;')
        sanitized = sanitized.replace('"', '&quot;')
        sanitized = sanitized.replace("'", '&#x27;')
        sanitized = sanitized.replace('&', '&amp;')
        
        return sanitized


class RateLimiter:
    """Rate limiting protection."""
    
    def __init__(self):
        self.requests: Dict[str, List[datetime]] = {}
        self.limits = {
            'messages_per_minute': 10,
            'commands_per_minute': 5,
            'api_calls_per_hour': 1000,
        }
        
    def is_rate_limited(
        self, 
        identifier: str, 
        limit_type: str,
        window_minutes: int = 1
    ) -> bool:
        """Check if identifier is rate limited."""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        if identifier not in self.requests:
            self.requests[identifier] = []
            
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        # Check limit
        limit = self.limits.get(limit_type, 10)
        return len(self.requests[identifier]) >= limit
        
    def record_request(self, identifier: str) -> None:
        """Record a request."""
        if identifier not in self.requests:
            self.requests[identifier] = []
            
        self.requests[identifier].append(datetime.utcnow())


class CSRFProtection:
    """CSRF protection."""
    
    def __init__(self):
        self.tokens: Dict[str, str] = {}
        
    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token."""
        import secrets
        token = secrets.token_urlsafe(32)
        self.tokens[session_id] = token
        return token
        
    def validate_token(self, session_id: str, token: str) -> bool:
        """Validate CSRF token."""
        stored_token = self.tokens.get(session_id)
        return stored_token == token and stored_token is not None
        
    def revoke_token(self, session_id: str) -> None:
        """Revoke CSRF token."""
        self.tokens.pop(session_id, None)


class AttackDetector:
    """Main attack detection system."""
    
    def __init__(self):
        self.sql_protection = SQLInjectionProtection()
        self.xss_protection = XSSProtection()
        self.rate_limiter = RateLimiter()
        self.csrf_protection = CSRFProtection()
        self.attack_history: List[AttackAttempt] = []
        
    def detect_attacks(
        self, 
        input_text: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> List[AttackAttempt]:
        """Detect various types of attacks."""
        attacks = []
        
        # SQL Injection detection
        if self.sql_protection.detect_sql_injection(input_text):
            attacks.append(AttackAttempt(
                attack_type=AttackType.SQL_INJECTION,
                user_id=user_id,
                ip_address=ip_address,
                timestamp=datetime.utcnow(),
                payload=input_text,
                severity="HIGH"
            ))
            
        # XSS detection
        if self.xss_protection.detect_xss(input_text):
            attacks.append(AttackAttempt(
                attack_type=AttackType.XSS,
                user_id=user_id,
                ip_address=ip_address,
                timestamp=datetime.utcnow(),
                payload=input_text,
                severity="HIGH"
            ))
            
        # Rate limiting
        identifier = str(user_id) if user_id else ip_address
        if identifier and self.rate_limiter.is_rate_limited(identifier, 'messages_per_minute'):
            attacks.append(AttackAttempt(
                attack_type=AttackType.DDOS,
                user_id=user_id,
                ip_address=ip_address,
                timestamp=datetime.utcnow(),
                payload="Rate limit exceeded",
                severity="MEDIUM"
            ))
            
        # Record attacks
        self.attack_history.extend(attacks)
        
        return attacks
        
    def sanitize_input(self, input_text: str) -> str:
        """Sanitize input against all attack types."""
        sanitized = input_text
        
        # SQL injection protection
        sanitized = self.sql_protection.sanitize_sql_input(sanitized)
        
        # XSS protection
        sanitized = self.xss_protection.sanitize_xss_input(sanitized)
        
        return sanitized
        
    def get_attack_statistics(self, hours: int = 24) -> Dict[str, int]:
        """Get attack statistics."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent_attacks = [
            attack for attack in self.attack_history
            if attack.timestamp > cutoff
        ]
        
        stats = {}
        for attack in recent_attacks:
            attack_type = attack.attack_type.value
            stats[attack_type] = stats.get(attack_type, 0) + 1
            
        return stats


# Global instance
attack_detector = AttackDetector()
