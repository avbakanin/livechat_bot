"""
Daily reset task - автоматический сброс счетчиков сообщений в полночь.
"""

import asyncio
import logging
from datetime import date, datetime, timedelta
from typing import Optional

from services.counter import DailyCounterService


class DailyResetTask:
    """Фоновая задача для автоматического сброса счетчиков в полночь."""
    
    def __init__(self, counter_service: DailyCounterService):
        self.counter_service = counter_service
        self._task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Запустить фоновую задачу сброса."""
        if self._running:
            logging.warning("Daily reset task is already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._reset_loop())
        logging.info("Daily reset task started")
    
    async def stop(self):
        """Остановить фоновую задачу сброса."""
        if not self._running:
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logging.info("Daily reset task stopped")
    
    async def _reset_loop(self):
        """Основной цикл задачи сброса."""
        while self._running:
            try:
                # Вычисляем время до следующей полночи
                now = datetime.now()
                next_midnight = (now + timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                sleep_seconds = (next_midnight - now).total_seconds()
                
                logging.info(f"Daily reset task: waiting {sleep_seconds:.0f} seconds until next midnight")
                
                # Ждем до следующей полночи
                await asyncio.sleep(sleep_seconds)
                
                if not self._running:
                    break
                
                # Сбрасываем счетчики за вчерашний день
                yesterday = date.today() - timedelta(days=1)
                logging.info(f"Daily reset task: resetting counters for {yesterday}")
                
                deleted_count = await self.counter_service.reset_counters_for_date(yesterday)
                logging.info(f"Daily reset task: reset {deleted_count} counters for {yesterday}")
                
                # Reset daily metrics in memory
                from shared.metrics.metrics import metrics_collector
                if metrics_collector:
                    metrics_collector.metrics.reset_daily_metrics()
                    logging.info("Daily reset task: reset daily metrics in memory")
                
                # Record metrics for successful reset
                if metrics_collector:
                    metrics_collector.record_successful_response(0.0)  # Reset operation time
                
            except asyncio.CancelledError:
                logging.info("Daily reset task cancelled")
                break
            except Exception as e:
                logging.error(f"Daily reset task error: {e}")
                # Record error metrics
                from shared.metrics.metrics import metrics_collector
                if metrics_collector:
                    metrics_collector.record_failed_response("database")
                # При ошибке ждем 1 час перед повторной попыткой
                await asyncio.sleep(3600)
    
    async def force_reset(self, target_date: Optional[date] = None):
        """Принудительный сброс счетчиков для указанной даты."""
        if target_date is None:
            target_date = date.today() - timedelta(days=1)
        
        logging.info(f"Force reset: resetting counters for {target_date}")
        deleted_count = await self.counter_service.reset_counters_for_date(target_date)
        logging.info(f"Force reset: reset {deleted_count} counters for {target_date}")
        return deleted_count
    
    async def cleanup_old_counters(self):
        """Очистка старых счетчиков (старше 30 дней)."""
        logging.info("Daily reset task: cleaning up old counters")
        deleted_count = await self.counter_service.cleanup_old_counters()
        logging.info(f"Daily reset task: cleaned up {deleted_count} old counters")
        return deleted_count
