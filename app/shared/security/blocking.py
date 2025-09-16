"""
Advanced user blocking and security enforcement system.
"""

import time
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class BlockReason(Enum):
    """Reasons for blocking users."""
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    MULTIPLE_VIOLATIONS = "multiple_violations"
    SPAM_DETECTED = "spam_detected"
    ATTACK_ATTEMPT = "attack_attempt"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    MANUAL_BLOCK = "manual_block"
    SECURITY_THREAT = "security_threat"


class BlockType(Enum):
    """Types of blocks."""
    TEMPORARY = "temporary"
    PERMANENT = "permanent"
    IP_BLOCK = "ip_block"
    USER_BLOCK = "user_block"


@dataclass
class BlockRecord:
    """Block record data."""
    user_id: Optional[int]
    ip_address: Optional[str]
    block_type: BlockType
    reason: BlockReason
    blocked_at: datetime
    expires_at: Optional[datetime]
    blocked_by: Optional[int]  # Admin who blocked
    description: str
    is_active: bool = True


class BlockingService:
    """Advanced blocking service."""
    
    def __init__(self):
        self.blocked_users: Set[int] = set()
        self.blocked_ips: Set[str] = set()
        self.block_records: List[BlockRecord] = []
        self.violation_counts: Dict[int, int] = {}
        self.auto_block_threshold = 5
        
    def block_user(
        self,
        user_id: int,
        reason: BlockReason,
        block_type: BlockType = BlockType.TEMPORARY,
        duration_hours: Optional[int] = None,
        blocked_by: Optional[int] = None,
        description: str = ""
    ) -> BlockRecord:
        """Block user."""
        now = datetime.utcnow()
        expires_at = None
        
        if block_type == BlockType.TEMPORARY and duration_hours:
            expires_at = now + timedelta(hours=duration_hours)
            
        block_record = BlockRecord(
            user_id=user_id,
            ip_address=None,
            block_type=block_type,
            reason=reason,
            blocked_at=now,
            expires_at=expires_at,
            blocked_by=blocked_by,
            description=description
        )
        
        self.block_records.append(block_record)
        self.blocked_users.add(user_id)
        
        return block_record
        
    def block_ip(
        self,
        ip_address: str,
        reason: BlockReason,
        block_type: BlockType = BlockType.TEMPORARY,
        duration_hours: Optional[int] = None,
        blocked_by: Optional[int] = None,
        description: str = ""
    ) -> BlockRecord:
        """Block IP address."""
        now = datetime.utcnow()
        expires_at = None
        
        if block_type == BlockType.TEMPORARY and duration_hours:
            expires_at = now + timedelta(hours=duration_hours)
            
        block_record = BlockRecord(
            user_id=None,
            ip_address=ip_address,
            block_type=block_type,
            reason=reason,
            blocked_at=now,
            expires_at=expires_at,
            blocked_by=blocked_by,
            description=description
        )
        
        self.block_records.append(block_record)
        self.blocked_ips.add(ip_address)
        
        return block_record
        
    def is_user_blocked(self, user_id: int) -> bool:
        """Check if user is blocked."""
        if user_id not in self.blocked_users:
            return False
            
        # Check if block has expired
        for record in reversed(self.block_records):
            if (record.user_id == user_id and 
                record.is_active and 
                record.block_type == BlockType.USER_BLOCK):
                
                if record.expires_at and datetime.utcnow() > record.expires_at:
                    self.unblock_user(user_id)
                    return False
                    
                return True
                
        return False
        
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked."""
        if ip_address not in self.blocked_ips:
            return False
            
        # Check if block has expired
        for record in reversed(self.block_records):
            if (record.ip_address == ip_address and 
                record.is_active and 
                record.block_type == BlockType.IP_BLOCK):
                
                if record.expires_at and datetime.utcnow() > record.expires_at:
                    self.unblock_ip(ip_address)
                    return False
                    
                return True
                
        return False
        
    def unblock_user(self, user_id: int) -> bool:
        """Unblock user."""
        if user_id in self.blocked_users:
            self.blocked_users.remove(user_id)
            
            # Mark records as inactive
            for record in self.block_records:
                if record.user_id == user_id and record.is_active:
                    record.is_active = False
                    
            return True
        return False
        
    def unblock_ip(self, ip_address: str) -> bool:
        """Unblock IP address."""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            
            # Mark records as inactive
            for record in self.block_records:
                if record.ip_address == ip_address and record.is_active:
                    record.is_active = False
                    
            return True
        return False
        
    def record_violation(self, user_id: int, violation_type: str) -> None:
        """Record user violation."""
        self.violation_counts[user_id] = self.violation_counts.get(user_id, 0) + 1
        
        # Auto-block if threshold exceeded
        if self.violation_counts[user_id] >= self.auto_block_threshold:
            self.block_user(
                user_id=user_id,
                reason=BlockReason.MULTIPLE_VIOLATIONS,
                block_type=BlockType.TEMPORARY,
                duration_hours=24,
                description=f"Auto-blocked after {self.violation_counts[user_id]} violations"
            )
            
    def get_user_violations(self, user_id: int) -> int:
        """Get user violation count."""
        return self.violation_counts.get(user_id, 0)
        
    def clear_violations(self, user_id: int) -> None:
        """Clear user violations."""
        self.violation_counts.pop(user_id, None)
        
    def get_blocked_users(self) -> List[BlockRecord]:
        """Get all blocked users."""
        return [
            record for record in self.block_records
            if record.user_id is not None and record.is_active
        ]
        
    def get_blocked_ips(self) -> List[BlockRecord]:
        """Get all blocked IPs."""
        return [
            record for record in self.block_records
            if record.ip_address is not None and record.is_active
        ]
        
    def get_block_statistics(self) -> Dict[str, int]:
        """Get blocking statistics."""
        return {
            'total_blocks': len(self.block_records),
            'active_user_blocks': len(self.blocked_users),
            'active_ip_blocks': len(self.blocked_ips),
            'total_violations': sum(self.violation_counts.values()),
            'users_with_violations': len(self.violation_counts)
        }


class SecurityEnforcer:
    """Security enforcement service."""
    
    def __init__(self, blocking_service: BlockingService):
        self.blocking_service = blocking_service
        self.enforcement_rules = {
            'max_violations_per_hour': 10,
            'max_failed_logins': 5,
            'max_suspicious_activities': 3,
            'auto_block_duration_hours': 24,
        }
        
    def enforce_security_policy(
        self,
        user_id: Optional[int],
        ip_address: Optional[str],
        action: str,
        context: Dict[str, Any]
    ) -> bool:
        """Enforce security policy."""
        # Check if user/IP is already blocked
        if user_id and self.blocking_service.is_user_blocked(user_id):
            return False
            
        if ip_address and self.blocking_service.is_ip_blocked(ip_address):
            return False
            
        # Apply enforcement rules
        if action == 'failed_login':
            return self._handle_failed_login(user_id, ip_address)
        elif action == 'suspicious_activity':
            return self._handle_suspicious_activity(user_id, ip_address)
        elif action == 'attack_attempt':
            return self._handle_attack_attempt(user_id, ip_address)
        elif action == 'spam_detected':
            return self._handle_spam(user_id, ip_address)
            
        return True
        
    def _handle_failed_login(
        self, 
        user_id: Optional[int], 
        ip_address: Optional[str]
    ) -> bool:
        """Handle failed login attempts."""
        if user_id:
            violations = self.blocking_service.get_user_violations(user_id)
            if violations >= self.enforcement_rules['max_failed_logins']:
                self.blocking_service.block_user(
                    user_id=user_id,
                    reason=BlockReason.SECURITY_THREAT,
                    block_type=BlockType.TEMPORARY,
                    duration_hours=self.enforcement_rules['auto_block_duration_hours']
                )
                return False
                
        return True
        
    def _handle_suspicious_activity(
        self, 
        user_id: Optional[int], 
        ip_address: Optional[str]
    ) -> bool:
        """Handle suspicious activity."""
        if user_id:
            self.blocking_service.record_violation(user_id, 'suspicious_activity')
            
        return True
        
    def _handle_attack_attempt(
        self, 
        user_id: Optional[int], 
        ip_address: Optional[str]
    ) -> bool:
        """Handle attack attempts."""
        if user_id:
            self.blocking_service.block_user(
                user_id=user_id,
                reason=BlockReason.ATTACK_ATTEMPT,
                block_type=BlockType.TEMPORARY,
                duration_hours=self.enforcement_rules['auto_block_duration_hours']
            )
            
        if ip_address:
            self.blocking_service.block_ip(
                ip_address=ip_address,
                reason=BlockReason.ATTACK_ATTEMPT,
                block_type=BlockType.TEMPORARY,
                duration_hours=self.enforcement_rules['auto_block_duration_hours']
            )
            
        return False
        
    def _handle_spam(
        self, 
        user_id: Optional[int], 
        ip_address: Optional[str]
    ) -> bool:
        """Handle spam detection."""
        if user_id:
            self.blocking_service.block_user(
                user_id=user_id,
                reason=BlockReason.SPAM_DETECTED,
                block_type=BlockType.TEMPORARY,
                duration_hours=12
            )
            
        return False


# Global instances
blocking_service = BlockingService()
security_enforcer = SecurityEnforcer(blocking_service)
