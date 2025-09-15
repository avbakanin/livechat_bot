"""
Metrics and monitoring utilities for the bot.
"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging
import asyncio


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
    
    def __init__(self, metrics_service=None):
        self.metrics = BotMetrics()
        self._response_times = []
        self.metrics_service = metrics_service
        self._save_task: Optional[asyncio.Task] = None
        self._auto_save_enabled = False
    
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
    
    async def load_from_database(self):
        """Load metrics from database."""
        if not self.metrics_service:
            return
        
        try:
            db_metrics = await self.metrics_service.load_metrics()
            
            # Load basic metrics
            self.metrics.total_messages_processed = db_metrics.get('total_messages_processed', 0)
            self.metrics.successful_responses = db_metrics.get('successful_responses', 0)
            self.metrics.failed_responses = db_metrics.get('failed_responses', 0)
            self.metrics.limit_exceeded_count = db_metrics.get('limit_exceeded_count', 0)
            self.metrics.active_users_today = db_metrics.get('active_users_today', 0)
            self.metrics.new_users_today = db_metrics.get('new_users_today', 0)
            self.metrics.openai_errors = db_metrics.get('openai_errors', 0)
            self.metrics.database_errors = db_metrics.get('database_errors', 0)
            self.metrics.validation_errors = db_metrics.get('validation_errors', 0)
            self.metrics.cache_hits = db_metrics.get('cache_hits', 0)
            self.metrics.cache_misses = db_metrics.get('cache_misses', 0)
            self.metrics.total_response_time = db_metrics.get('total_response_time', 0)
            
            # Load timestamps
            started_at_epoch = db_metrics.get('started_at', 0)
            if started_at_epoch > 0:
                # Use UTC timestamp directly
                loaded_started_at = datetime.utcfromtimestamp(started_at_epoch)
                # Only use loaded timestamp if it's not in the future
                current_time = datetime.utcnow()
                if loaded_started_at <= current_time:
                    self.metrics.started_at = loaded_started_at
                else:
                    logging.warning(f"Loaded started_at ({loaded_started_at}) is in future, using current time")
                    self.metrics.started_at = current_time
            else:
                logging.info("No started_at found in database, using current time")
                self.metrics.started_at = datetime.utcnow()
            
            last_reset_epoch = db_metrics.get('last_reset', 0)
            if last_reset_epoch > 0:
                # Use UTC timestamp directly
                loaded_last_reset = datetime.utcfromtimestamp(last_reset_epoch)
                current_time = datetime.utcnow()
                if loaded_last_reset <= current_time:
                    self.metrics.last_reset = loaded_last_reset
                else:
                    logging.warning(f"Loaded last_reset ({loaded_last_reset}) is in future, using current time")
                    self.metrics.last_reset = current_time
            else:
                self.metrics.last_reset = datetime.utcnow()
            
            logging.info("📊 Loaded metrics from database")
            logging.info(f"📊 Started at: {self.metrics.started_at}")
            logging.info(f"📊 Current uptime: {self.get_uptime():.2f} seconds")
            
        except Exception as e:
            logging.error(f"Error loading metrics from database: {e}")
    
    async def save_to_database(self):
        """Save current metrics to database."""
        if not self.metrics_service:
            return
        
        try:
            metrics_to_save = {
                'total_messages_processed': self.metrics.total_messages_processed,
                'successful_responses': self.metrics.successful_responses,
                'failed_responses': self.metrics.failed_responses,
                'limit_exceeded_count': self.metrics.limit_exceeded_count,
                'active_users_today': self.metrics.active_users_today,
                'new_users_today': self.metrics.new_users_today,
                'openai_errors': self.metrics.openai_errors,
                'database_errors': self.metrics.database_errors,
                'validation_errors': self.metrics.validation_errors,
                'cache_hits': self.metrics.cache_hits,
                'cache_misses': self.metrics.cache_misses,
                'total_response_time': int(self.metrics.total_response_time),
                'average_response_time': int(self.metrics.average_response_time),
                'uptime_seconds': int(self.get_uptime()),
                'started_at': int(self.metrics.started_at.timestamp()),
                'last_reset': int(self.metrics.last_reset.timestamp()),
            }
            
            await self.metrics_service.save_metrics(metrics_to_save)
            logging.info("📊 Saved metrics to database")
            
        except Exception as e:
            logging.error(f"Error saving metrics to database: {e}")
    
    def get_uptime(self) -> float:
        """Get uptime in seconds."""
        return (datetime.utcnow() - self.metrics.started_at).total_seconds()
    
    async def start_auto_save(self, interval_seconds: int = 300):
        """Start automatic saving of metrics every interval_seconds."""
        if self._auto_save_enabled:
            return
        
        self._auto_save_enabled = True
        
        async def _auto_save_loop():
            while self._auto_save_enabled:
                try:
                    await asyncio.sleep(interval_seconds)
                    if self._auto_save_enabled:
                        await self.save_to_database()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logging.error(f"Error in auto-save loop: {e}")
        
        self._save_task = asyncio.create_task(_auto_save_loop())
        logging.info(f"📊 Started auto-save every {interval_seconds} seconds")
    
    async def stop_auto_save(self):
        """Stop automatic saving of metrics."""
        self._auto_save_enabled = False
        if self._save_task:
            self._save_task.cancel()
            try:
                await self._save_task
            except asyncio.CancelledError:
                pass
        logging.info("📊 Stopped auto-save")


# Global metrics collector instance (will be initialized in main.py)
metrics_collector = None


def safe_record_metric(method_name: str, *args, **kwargs):
    """Safely record a metric if metrics_collector is available."""
    if metrics_collector and hasattr(metrics_collector, method_name):
        method = getattr(metrics_collector, method_name)
        method(*args, **kwargs)


def record_response_time(func):
    """Decorator to record response time for functions."""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            response_time = time.time() - start_time
            safe_record_metric('record_successful_response', response_time)
            return result
        except Exception as e:
            response_time = time.time() - start_time
            safe_record_metric('record_failed_response')
            raise e
    return wrapper
