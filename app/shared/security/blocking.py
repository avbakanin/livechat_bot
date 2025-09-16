"""
Blocking service for user management.
"""

import logging
from typing import Set, Dict, Any
from datetime import datetime, timedelta


class BlockingService:
    """Service for blocking and unblocking users."""
    
    def __init__(self):
        """Initialize blocking service."""
        self.blocked_users: Set[int] = set()
        self.block_reasons: Dict[int, str] = {}
        self.block_timestamps: Dict[int, datetime] = {}
        self.temporary_blocks: Dict[int, datetime] = {}
    
    def block_user(self, user_id: int, reason: str = "Manual block") -> None:
        """
        Block a user.
        
        Args:
            user_id: User ID to block
            reason: Reason for blocking
        """
        self.blocked_users.add(user_id)
        self.block_reasons[user_id] = reason
        self.block_timestamps[user_id] = datetime.utcnow()
        
        logging.warning(f"🚫 User {user_id} blocked. Reason: {reason}")
    
    def unblock_user(self, user_id: int) -> None:
        """
        Unblock a user.
        
        Args:
            user_id: User ID to unblock
        """
        self.blocked_users.discard(user_id)
        self.block_reasons.pop(user_id, None)
        self.block_timestamps.pop(user_id, None)
        self.temporary_blocks.pop(user_id, None)
        
        logging.info(f"✅ User {user_id} unblocked")
    
    def is_user_blocked(self, user_id: int) -> bool:
        """
        Check if user is blocked.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if user is blocked, False otherwise
        """
        # Check permanent blocks
        if user_id in self.blocked_users:
            return True
        
        # Check temporary blocks
        if user_id in self.temporary_blocks:
            if datetime.utcnow() < self.temporary_blocks[user_id]:
                return True
            else:
                # Temporary block expired
                del self.temporary_blocks[user_id]
                return False
        
        return False
    
    def temporary_block_user(self, user_id: int, duration_minutes: int, reason: str = "Temporary block") -> None:
        """
        Temporarily block a user.
        
        Args:
            user_id: User ID to block
            duration_minutes: Block duration in minutes
            reason: Reason for blocking
        """
        block_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.temporary_blocks[user_id] = block_until
        self.block_reasons[user_id] = reason
        
        logging.warning(f"⏰ User {user_id} temporarily blocked for {duration_minutes} minutes. Reason: {reason}")
    
    def get_block_info(self, user_id: int) -> Dict[str, Any]:
        """
        Get blocking information for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Block information dictionary
        """
        if user_id not in self.blocked_users and user_id not in self.temporary_blocks:
            return {"is_blocked": False}
        
        info = {
            "is_blocked": True,
            "reason": self.block_reasons.get(user_id, "Unknown"),
            "blocked_at": self.block_timestamps.get(user_id),
            "is_temporary": user_id in self.temporary_blocks
        }
        
        if user_id in self.temporary_blocks:
            info["blocked_until"] = self.temporary_blocks[user_id]
            info["remaining_minutes"] = max(0, int((self.temporary_blocks[user_id] - datetime.utcnow()).total_seconds() / 60))
        
        return info
    
    def get_blocked_users_count(self) -> int:
        """
        Get count of blocked users.
        
        Returns:
            Number of blocked users
        """
        return len(self.blocked_users) + len(self.temporary_blocks)
    
    def cleanup_expired_blocks(self) -> None:
        """Clean up expired temporary blocks."""
        current_time = datetime.utcnow()
        expired_users = [
            user_id for user_id, block_until in self.temporary_blocks.items()
            if current_time >= block_until
        ]
        
        for user_id in expired_users:
            del self.temporary_blocks[user_id]
            self.block_reasons.pop(user_id, None)
            logging.info(f"🕒 Temporary block expired for user {user_id}")


# Глобальный экземпляр сервиса блокировки
blocking_service = BlockingService()