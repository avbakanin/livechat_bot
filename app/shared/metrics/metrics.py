"""
Metrics and monitoring utilities for the bot.
"""

import time
from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging


@dataclass
class BotMetrics:
    """Bot performance and usage metrics."""
    
    # Message metrics
    total_messages_processed: int = 0
    successful_responses: int = 0
    failed_responses: int = 0
    limit_exceeded_count: int = 0
    
    # Performance metrics
    average_response_time: float = 0.0
    total_response_time: float = 0.0
    
    # User metrics
    active_users_today: int = 0
    new_users_today: int = 0
    
    # Error metrics
    openai_errors: int = 0
    database_errors: int = 0
    validation_errors: int = 0
    
    # Cache metrics
    cache_hits: int = 0
    cache_misses: int = 0
    
    # Timestamps
    last_reset: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime = field(default_factory=datetime.utcnow)
    
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0.0
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage."""
        total = self.successful_responses + self.failed_responses
        return (self.successful_responses / total * 100) if total > 0 else 0.0
    
    def get_uptime(self) -> float:
        """Get uptime in seconds."""
        return (datetime.utcnow() - self.started_at).total_seconds()
    
    def reset_daily_metrics(self):
        """Reset daily metrics (called at midnight)."""
        self.active_users_today = 0
        self.new_users_today = 0
        self.last_reset = datetime.utcnow()


class MetricsCollector:
    """Collects and manages bot metrics."""
    
    def __init__(self):
        self.metrics = BotMetrics()
        self._response_times = []
    
    def record_message_processed(self):
        """Record that a message was processed."""
        self.metrics.total_messages_processed += 1
    
    def record_successful_response(self, response_time: float):
        """Record a successful response."""
        self.metrics.successful_responses += 1
        self.metrics.total_response_time += response_time
        self._response_times.append(response_time)
        
        # Keep only last 100 response times for average calculation
        if len(self._response_times) > 100:
            self._response_times = self._response_times[-100:]
        
        self.metrics.average_response_time = sum(self._response_times) / len(self._response_times)
    
    def record_failed_response(self, error_type: str = "unknown"):
        """Record a failed response."""
        self.metrics.failed_responses += 1
        
        if error_type == "openai":
            self.metrics.openai_errors += 1
        elif error_type == "database":
            self.metrics.database_errors += 1
        elif error_type == "validation":
            self.metrics.validation_errors += 1
    
    def record_limit_exceeded(self):
        """Record that a user hit the message limit."""
        self.metrics.limit_exceeded_count += 1
    
    def record_cache_hit(self):
        """Record a cache hit."""
        self.metrics.cache_hits += 1
    
    def record_cache_miss(self):
        """Record a cache miss."""
        self.metrics.cache_misses += 1
    
    def record_new_user(self):
        """Record a new user registration."""
        self.metrics.new_users_today += 1
    
    def record_active_user(self):
        """Record an active user."""
        self.metrics.active_users_today += 1
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of current metrics."""
        return {
            "uptime_seconds": self.metrics.get_uptime(),
            "uptime_hours": self.metrics.get_uptime() / 3600,
            "total_messages": self.metrics.total_messages_processed,
            "success_rate": f"{self.metrics.get_success_rate():.1f}%",
            "cache_hit_rate": f"{self.metrics.get_cache_hit_rate():.1f}%",
            "average_response_time": f"{self.metrics.average_response_time:.2f}s",
            "active_users_today": self.metrics.active_users_today,
            "new_users_today": self.metrics.new_users_today,
            "limit_exceeded_count": self.metrics.limit_exceeded_count,
            "openai_errors": self.metrics.openai_errors,
            "database_errors": self.metrics.database_errors,
            "validation_errors": self.metrics.validation_errors,
        }
    
    def log_metrics_summary(self):
        """Log current metrics summary."""
        summary = self.get_metrics_summary()
        logging.info("📊 Bot Metrics Summary:")
        for key, value in summary.items():
            logging.info(f"  {key}: {value}")


# Global metrics collector instance
metrics_collector = MetricsCollector()


def record_response_time(func):
    """Decorator to record response time for functions."""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            response_time = time.time() - start_time
            metrics_collector.record_successful_response(response_time)
            return result
        except Exception as e:
            response_time = time.time() - start_time
            metrics_collector.record_failed_response()
            raise e
    return wrapper
