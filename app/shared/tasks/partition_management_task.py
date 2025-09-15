"""
Partition management task - автоматическое создание и удаление партиций сообщений.
"""

import asyncio
import logging
from datetime import date, datetime, timedelta
from typing import Optional

import asyncpg
from shared.metrics.metrics import metrics_collector

from core.exceptions import DatabaseException


class PartitionManagementTask:
    """Фоновая задача для автоматического управления партициями сообщений."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Запустить фоновую задачу управления партициями."""
        if self._running:
            logging.warning("Partition management task is already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._partition_loop())
        logging.info("Partition management task started")

    async def stop(self):
        """Остановить фоновую задачу управления партициями."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logging.info("Partition management task stopped")

    async def _partition_loop(self):
        """Основной цикл задачи управления партициями."""
        while self._running:
            try:
                # Вычисляем время до следующего 25 числа (создание партиций)
                now = datetime.now()
                next_25th = self._get_next_25th()
                sleep_seconds = (next_25th - now).total_seconds()

                logging.info(
                    f"Partition management task: waiting {sleep_seconds:.0f} seconds until next partition creation"
                )

                # Ждем до 25 числа
                await asyncio.sleep(sleep_seconds)

                if not self._running:
                    break

                # Создаем партицию на следующий месяц
                await self._create_next_month_partition()

                # Ждем до 1 числа следующего месяца (удаление партиций)
                next_1st = self._get_next_1st()
                sleep_seconds = (next_1st - datetime.now()).total_seconds()

                logging.info(
                    f"Partition management task: waiting {sleep_seconds:.0f} seconds until next partition cleanup"
                )

                await asyncio.sleep(sleep_seconds)

                if not self._running:
                    break

                # Удаляем партицию за 2 месяца назад
                await self._drop_old_partition()

            except asyncio.CancelledError:
                logging.info("Partition management task cancelled")
                break
            except Exception as e:
                logging.error(f"Partition management task error: {e}")
                # При ошибке ждем 1 час перед повторной попыткой
                await asyncio.sleep(3600)

    def _get_next_25th(self) -> datetime:
        """Получить дату следующего 25 числа."""
        now = datetime.now()
        current_month_25th = now.replace(
            day=25, hour=5, minute=0, second=0, microsecond=0
        )

        if now.day >= 25:
            # Если уже прошло 25 число, берем следующий месяц
            if now.month == 12:
                next_month_25th = now.replace(
                    year=now.year + 1,
                    month=1,
                    day=25,
                    hour=5,
                    minute=0,
                    second=0,
                    microsecond=0,
                )
            else:
                next_month_25th = now.replace(
                    month=now.month + 1,
                    day=25,
                    hour=5,
                    minute=0,
                    second=0,
                    microsecond=0,
                )
            return next_month_25th
        else:
            return current_month_25th

    def _get_next_1st(self) -> datetime:
        """Получить дату следующего 1 числа."""
        now = datetime.now()
        if now.month == 12:
            next_month_1st = now.replace(
                year=now.year + 1,
                month=1,
                day=1,
                hour=5,
                minute=0,
                second=0,
                microsecond=0,
            )
        else:
            next_month_1st = now.replace(
                month=now.month + 1, day=1, hour=5, minute=0, second=0, microsecond=0
            )
        return next_month_1st

    async def _create_next_month_partition(self):
        """Создать партицию на следующий месяц."""
        async with self.pool.acquire() as conn:
            try:
                # Создаем партицию на следующий месяц
                next_month = (datetime.now() + timedelta(days=32)).replace(day=1)
                partition_date = next_month.date()

                logging.info(
                    f"Partition management task: creating partition for {partition_date}"
                )

                result = await conn.fetchval(
                    "SELECT public.ensure_messages_partition($1)", partition_date
                )

                logging.info(
                    f"Partition management task: partition creation result: {result}"
                )

                # Record metrics for successful partition creation
                metrics_collector.record_successful_response(0.0)

            except Exception as e:
                logging.error(
                    f"Partition management task: error creating partition: {e}"
                )
                # Record error metrics
                metrics_collector.record_failed_response("database")
                raise DatabaseException(f"Error creating partition: {e}", e)

    async def _drop_old_partition(self):
        """Удалить старую партицию (за 2 месяца назад)."""
        async with self.pool.acquire() as conn:
            try:
                # Удаляем партицию за 2 месяца назад
                two_months_ago = (datetime.now() - timedelta(days=60)).replace(day=1)
                partition_date = two_months_ago.date()

                logging.info(
                    f"Partition management task: dropping partition for {partition_date}"
                )

                result = await conn.fetchval(
                    "SELECT public.drop_messages_partition($1)", partition_date
                )

                logging.info(
                    f"Partition management task: partition drop result: {result}"
                )

                # Record metrics for successful partition drop
                metrics_collector.record_successful_response(0.0)

            except Exception as e:
                logging.error(
                    f"Partition management task: error dropping partition: {e}"
                )
                # Record error metrics
                metrics_collector.record_failed_response("database")
                raise DatabaseException(f"Error dropping partition: {e}", e)

    async def force_create_partition(self, target_date: date):
        """Принудительное создание партиции для указанной даты."""
        async with self.pool.acquire() as conn:
            try:
                logging.info(
                    f"Force partition creation: creating partition for {target_date}"
                )

                result = await conn.fetchval(
                    "SELECT public.ensure_messages_partition($1)", target_date
                )

                logging.info(f"Force partition creation: result: {result}")
                return result

            except Exception as e:
                logging.error(f"Force partition creation: error: {e}")
                raise DatabaseException(f"Error creating partition: {e}", e)

    async def force_drop_partition(self, target_date: date):
        """Принудительное удаление партиции для указанной даты."""
        async with self.pool.acquire() as conn:
            try:
                logging.info(
                    f"Force partition drop: dropping partition for {target_date}"
                )

                result = await conn.fetchval(
                    "SELECT public.drop_messages_partition($1)", target_date
                )

                logging.info(f"Force partition drop: result: {result}")
                return result

            except Exception as e:
                logging.error(f"Force partition drop: error: {e}")
                raise DatabaseException(f"Error dropping partition: {e}", e)

    async def get_partition_status(self) -> list:
        """Получить статус всех партиций."""
        async with self.pool.acquire() as conn:
            try:
                rows = await conn.fetch(
                    """
                    SELECT 
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                    FROM pg_tables 
                    WHERE tablename LIKE 'messages_%'
                    ORDER BY tablename;
                """
                )

                partitions = []
                for row in rows:
                    partitions.append(
                        {
                            "schema": row["schemaname"],
                            "table": row["tablename"],
                            "size": row["size"],
                        }
                    )

                logging.info(
                    f"Partition management task: found {len(partitions)} partitions"
                )
                return partitions

            except Exception as e:
                logging.error(
                    f"Partition management task: error getting partition status: {e}"
                )
                raise DatabaseException(f"Error getting partition status: {e}", e)
