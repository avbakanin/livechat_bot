"""
Centralized datetime utilities with timezone-aware operations.
Replaces deprecated datetime.utcnow() and datetime.now() calls.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union


class DateTimeUtils:
    """Centralized datetime utilities with timezone awareness."""
    
    @staticmethod
    def utc_now() -> datetime:
        """
        Get current UTC datetime (replaces deprecated datetime.utcnow()).
        
        Returns:
            Current UTC datetime with timezone info
        """
        return datetime.now(timezone.utc)
    
    @staticmethod
    def local_now() -> datetime:
        """
        Get current local datetime.
        
        Returns:
            Current local datetime
        """
        return datetime.now()
    
    @staticmethod
    def utc_now_naive() -> datetime:
        """
        Get current UTC datetime without timezone info (for backward compatibility).
        
        Returns:
            Current UTC datetime without timezone info
        """
        return datetime.now(timezone.utc).replace(tzinfo=None)
    
    @staticmethod
    def from_timestamp(timestamp: float) -> datetime:
        """
        Create datetime from timestamp.
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Datetime object
        """
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    
    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        """
        Convert datetime to UTC timezone.
        
        Args:
            dt: Datetime object
            
        Returns:
            UTC datetime
        """
        if dt.tzinfo is None:
            # Assume naive datetime is in UTC
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    
    @staticmethod
    def format_iso(dt: Optional[datetime] = None) -> str:
        """
        Format datetime as ISO string.
        
        Args:
            dt: Datetime object (defaults to current UTC time)
            
        Returns:
            ISO formatted datetime string
        """
        if dt is None:
            dt = DateTimeUtils.utc_now()
        return dt.isoformat()
    
    @staticmethod
    def format_readable(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Format datetime as readable string.
        
        Args:
            dt: Datetime object (defaults to current UTC time)
            format_str: Format string
            
        Returns:
            Formatted datetime string
        """
        if dt is None:
            dt = DateTimeUtils.utc_now()
        return dt.strftime(format_str)
    
    @staticmethod
    def is_expired(expires_at: Optional[datetime], current_time: Optional[datetime] = None) -> bool:
        """
        Check if datetime is expired.
        
        Args:
            expires_at: Expiration datetime
            current_time: Current time (defaults to UTC now)
            
        Returns:
            True if expired, False otherwise
        """
        if expires_at is None:
            return True
        
        if current_time is None:
            current_time = DateTimeUtils.utc_now()
        
        return current_time > expires_at
    
    @staticmethod
    def time_until(expires_at: Optional[datetime], current_time: Optional[datetime] = None) -> Optional[timedelta]:
        """
        Get time until expiration.
        
        Args:
            expires_at: Expiration datetime
            current_time: Current time (defaults to UTC now)
            
        Returns:
            Time delta until expiration, or None if expired
        """
        if expires_at is None:
            return None
        
        if current_time is None:
            current_time = DateTimeUtils.utc_now()
        
        if current_time >= expires_at:
            return None
        
        return expires_at - current_time
    
    @staticmethod
    def days_remaining(expires_at: Optional[datetime], current_time: Optional[datetime] = None) -> int:
        """
        Get days remaining until expiration.
        
        Args:
            expires_at: Expiration datetime
            current_time: Current time (defaults to UTC now)
            
        Returns:
            Days remaining, or 0 if expired
        """
        time_delta = DateTimeUtils.time_until(expires_at, current_time)
        if time_delta is None:
            return 0
        return time_delta.days
    
    @staticmethod
    def hours_remaining(expires_at: Optional[datetime], current_time: Optional[datetime] = None) -> int:
        """
        Get hours remaining until expiration.
        
        Args:
            expires_at: Expiration datetime
            current_time: Current time (defaults to UTC now)
            
        Returns:
            Hours remaining, or 0 if expired
        """
        time_delta = DateTimeUtils.time_until(expires_at, current_time)
        if time_delta is None:
            return 0
        return int(time_delta.total_seconds() // 3600)


# Convenience functions for backward compatibility
def utc_now() -> datetime:
    """Get current UTC datetime (replaces deprecated datetime.utcnow())."""
    return DateTimeUtils.utc_now()


def local_now() -> datetime:
    """Get current local datetime."""
    return DateTimeUtils.local_now()


def utc_now_naive() -> datetime:
    """Get current UTC datetime without timezone info (for backward compatibility)."""
    return DateTimeUtils.utc_now_naive()


# Export commonly used items
__all__ = [
    "DateTimeUtils",
    "utc_now",
    "local_now", 
    "utc_now_naive"
]
