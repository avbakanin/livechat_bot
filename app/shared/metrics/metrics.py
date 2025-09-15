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
    
    # User activity metrics (LOGICAL SEPARATION)
    total_interactions_today: int = 0        # Все взаимодействия (команды + сообщения)
    unique_active_users_today: int = 0       # Уникальные активные пользователи
    new_users_today: int = 0                 # Новые пользователи (первый /start)
    messages_sent_today: int = 0             # Сообщения от пользователей
    commands_used_today: int = 0             # Команды (/start, /help, etc.)
    
    # Daily user tracking (for deduplication)
    daily_user_ids: set = field(default_factory=set)  # Set для отслеживания уникальных пользователей
    
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
        # Reset daily counters
        self.total_interactions_today = 0
        self.unique_active_users_today = 0
        self.new_users_today = 0
        self.messages_sent_today = 0
        self.commands_used_today = 0
        
        # Clear daily user tracking
        self.daily_user_ids.clear()
        
        # Update reset timestamp
        self.last_reset = datetime.utcnow()


class MetricsCollector:
    """Collects and manages bot metrics."""
    
    def __init__(self, metrics_service=None):
        self.metrics = BotMetrics()
        self._response_times = []
        self.metrics_service = metrics_service
        self._save_task: Optional[asyncio.Task] = None
        self._auto_save_enabled = False
        
        # Batch optimization for scalability
        self._pending_metrics = {}
        self._batch_size = 100  # Save every 100 metric changes
        self._batch_count = 0
    
    def record_message_processed(self):
        """Record that a message was processed."""
        self.metrics.total_messages_processed += 1
        self._batch_count += 1
        self._check_batch_save()
    
    def record_successful_response(self, response_time: float):
        """Record a successful response."""
        self.metrics.successful_responses += 1
        self.metrics.total_response_time += response_time
        self._response_times.append(response_time)
        
        # Keep only last 100 response times for average calculation
        if len(self._response_times) > 100:
            self._response_times = self._response_times[-100:]
        
        self.metrics.average_response_time = sum(self._response_times) / len(self._response_times)
        self._batch_count += 1
        self._check_batch_save()
    
    def record_failed_response(self, error_type: str = "unknown"):
        """Record a failed response."""
        self.metrics.failed_responses += 1
        
        if error_type == "openai":
            self.metrics.openai_errors += 1
        elif error_type == "database":
            self.metrics.database_errors += 1
        elif error_type == "validation":
            self.metrics.validation_errors += 1
        
        self._batch_count += 1
        self._check_batch_save()
    
    def record_limit_exceeded(self):
        """Record that a user hit the message limit."""
        self.metrics.limit_exceeded_count += 1
    
    def record_cache_hit(self):
        """Record a cache hit."""
        self.metrics.cache_hits += 1
        self._batch_count += 1
        self._check_batch_save()
    
    def record_cache_miss(self):
        """Record a cache miss."""
        self.metrics.cache_misses += 1
        self._batch_count += 1
        self._check_batch_save()
    
    def record_new_user(self):
        """Record a new user registration."""
        self.metrics.new_users_today += 1
        self._batch_count += 1
        self._check_batch_save()
    
    def record_user_interaction(self, user_id: int, interaction_type: str):
        """Record any user interaction with deduplication."""
        # Always increment total interactions
        self.metrics.total_interactions_today += 1
        
        # Track interaction type
        if interaction_type == "message":
            self.metrics.messages_sent_today += 1
        elif interaction_type == "command":
            self.metrics.commands_used_today += 1
        
        # Track unique users
        if user_id not in self.metrics.daily_user_ids:
            self.metrics.daily_user_ids.add(user_id)
            self.metrics.unique_active_users_today += 1
        
        self._batch_count += 1
        self._check_batch_save()
    
    def record_active_user(self):
        """DEPRECATED: Use record_user_interaction instead."""
        # Keep for backward compatibility, but log warning
        logging.warning("record_active_user() is deprecated. Use record_user_interaction(user_id, type) instead.")
        self.metrics.total_interactions_today += 1
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of current metrics."""
        return {
            # System metrics
            "uptime_seconds": self.metrics.get_uptime(),
            "uptime_hours": self.metrics.get_uptime() / 3600,
            
            # Daily user activity metrics (reset at midnight)
            "unique_active_users_today": self.metrics.unique_active_users_today,
            "total_interactions_today": self.metrics.total_interactions_today,
            "messages_sent_today": self.metrics.messages_sent_today,
            "commands_used_today": self.metrics.commands_used_today,
            "new_users_today": self.metrics.new_users_today,
            
            # General metrics (accumulative, never reset)
            "total_messages_processed": self.metrics.total_messages_processed,
            "success_rate": f"{self.metrics.get_success_rate():.1f}%",
            "average_response_time": f"{self.metrics.average_response_time:.2f}s",
            "limit_exceeded_count": self.metrics.limit_exceeded_count,
            
            # Performance and error metrics (accumulative, never reset)
            "cache_hit_rate": f"{self.metrics.get_cache_hit_rate():.1f}%",
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
            
            # Load new user activity metrics
            self.metrics.total_interactions_today = db_metrics.get('total_interactions_today', 0)
            self.metrics.unique_active_users_today = db_metrics.get('unique_active_users_today', 0)
            self.metrics.new_users_today = db_metrics.get('new_users_today', 0)
            self.metrics.messages_sent_today = db_metrics.get('messages_sent_today', 0)
            self.metrics.commands_used_today = db_metrics.get('commands_used_today', 0)
            
            # Load daily user IDs from database (make it persistent)
            daily_user_ids_str = db_metrics.get('daily_user_ids', '')
            if daily_user_ids_str:
                try:
                    # Parse comma-separated user IDs from database
                    user_ids = [int(uid.strip()) for uid in daily_user_ids_str.split(',') if uid.strip()]
                    self.metrics.daily_user_ids = set(user_ids)
                    logging.info(f"📊 Loaded {len(self.metrics.daily_user_ids)} daily user IDs from database")
                except (ValueError, AttributeError) as e:
                    logging.warning(f"Failed to parse daily_user_ids from database: {e}")
                    self.metrics.daily_user_ids.clear()
            else:
                self.metrics.daily_user_ids.clear()
                logging.info("📊 No daily user IDs found in database, starting fresh")
            
            # Load error metrics
            self.metrics.openai_errors = db_metrics.get('openai_errors', 0)
            self.metrics.database_errors = db_metrics.get('database_errors', 0)
            self.metrics.validation_errors = db_metrics.get('validation_errors', 0)
            
            # Load cache metrics
            self.metrics.cache_hits = db_metrics.get('cache_hits', 0)
            self.metrics.cache_misses = db_metrics.get('cache_misses', 0)
            self.metrics.total_response_time = db_metrics.get('total_response_time', 0)
            
            # Load average response time from DB
            self.metrics.average_response_time = db_metrics.get('average_response_time', 0.0)
            
            # Reset uptime on each startup - this is more logical for monitoring
            self.metrics.started_at = datetime.utcnow()
            logging.info(f"📊 Started at (reset on startup): {self.metrics.started_at}")
            
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
                # Basic metrics
                'total_messages_processed': self.metrics.total_messages_processed,
                'successful_responses': self.metrics.successful_responses,
                'failed_responses': self.metrics.failed_responses,
                'limit_exceeded_count': self.metrics.limit_exceeded_count,
                
                # New user activity metrics
                'total_interactions_today': self.metrics.total_interactions_today,
                'unique_active_users_today': self.metrics.unique_active_users_today,
                'new_users_today': self.metrics.new_users_today,
                'messages_sent_today': self.metrics.messages_sent_today,
                'commands_used_today': self.metrics.commands_used_today,
                
                # Save daily user IDs as comma-separated string
                'daily_user_ids': ','.join(map(str, self.metrics.daily_user_ids)),
                
                # Error metrics
                'openai_errors': self.metrics.openai_errors,
                'database_errors': self.metrics.database_errors,
                'validation_errors': self.metrics.validation_errors,
                
                # Cache metrics
                'cache_hits': self.metrics.cache_hits,
                'cache_misses': self.metrics.cache_misses,
                'total_response_time': int(self.metrics.total_response_time),
                'average_response_time': int(self.metrics.average_response_time),
                
                # Timestamps
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
    
    def _check_batch_save(self):
        """Check if we should save metrics due to batch size."""
        if self._batch_count >= self._batch_size and self.metrics_service:
            # Schedule async save
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._async_batch_save())
            except RuntimeError:
                # No event loop running, skip batch save
                pass
            self._batch_count = 0
    
    async def _async_batch_save(self):
        """Async batch save to avoid blocking."""
        try:
            await self.save_to_database()
            logging.debug(f"📊 Batch saved metrics ({self._batch_size} changes)")
        except Exception as e:
            logging.error(f"Error in batch save: {e}")


# Global metrics collector instance (will be initialized in main.py)
metrics_collector = None


def safe_record_metric(method_name: str, *args, **kwargs):
    """Safely record a metric if metrics_collector is available."""
    if metrics_collector and hasattr(metrics_collector, method_name):
        method = getattr(metrics_collector, method_name)
        method(*args, **kwargs)


def safe_record_user_interaction(user_id: int, interaction_type: str):
    """Safely record user interaction with new logical method."""
    if metrics_collector:
        metrics_collector.record_user_interaction(user_id, interaction_type)


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
