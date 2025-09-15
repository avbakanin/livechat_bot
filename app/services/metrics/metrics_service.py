"""
Metrics service for persistent storage of bot metrics.
"""

import logging
from typing import Any, Dict

import asyncpg

from core.exceptions import DatabaseException


class MetricsService:
    """Service for managing persistent bot metrics in database."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_metric(self, metric_name: str) -> int:
        """Get a metric value from database."""
        try:
            async with self.pool.acquire() as conn:
                value = await conn.fetchval("SELECT public.get_metric($1)", metric_name)
                return value or 0
        except Exception as e:
            self.logger.error(f"Error getting metric {metric_name}: {e}")
            raise DatabaseException(f"Error getting metric {metric_name}", e)

    async def set_metric(self, metric_name: str, value: int) -> None:
        """Set a metric value in database."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    "SELECT public.set_metric($1, $2)", metric_name, value
                )
        except Exception as e:
            self.logger.error(f"Error setting metric {metric_name}={value}: {e}")
            raise DatabaseException(f"Error setting metric {metric_name}", e)

    async def increment_metric(self, metric_name: str, increment: int = 1) -> None:
        """Increment a metric value in database."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    "SELECT public.increment_metric($1, $2)", metric_name, increment
                )
        except Exception as e:
            self.logger.error(
                f"Error incrementing metric {metric_name}+{increment}: {e}"
            )
            raise DatabaseException(f"Error incrementing metric {metric_name}", e)

    async def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics from database."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT metric_name, metric_value, metric_text FROM public.bot_metrics"
                )
                result = {}
                for row in rows:
                    # Use metric_text if available, otherwise metric_value
                    if row["metric_text"] is not None:
                        result[row["metric_name"]] = row["metric_text"]
                    else:
                        result[row["metric_name"]] = row["metric_value"]
                return result
        except Exception as e:
            self.logger.error(f"Error getting all metrics: {e}")
            raise DatabaseException("Error getting all metrics", e)

    async def save_metrics(self, metrics: Dict[str, Any]) -> None:
        """Save multiple metrics to database."""
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    for metric_name, value in metrics.items():
                        if metric_name == "daily_user_ids":
                            # Save as text
                            await conn.execute(
                                "INSERT INTO public.bot_metrics (metric_name, metric_text, updated_at) "
                                "VALUES ($1, $2, CURRENT_TIMESTAMP) "
                                "ON CONFLICT (metric_name) DO UPDATE SET "
                                "metric_text = $2, updated_at = CURRENT_TIMESTAMP",
                                metric_name,
                                value,
                            )
                        else:
                            # Convert float to int for storage
                            if isinstance(value, float):
                                value = int(value)
                            await conn.execute(
                                "SELECT public.set_metric($1, $2)", metric_name, value
                            )
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")
            raise DatabaseException("Error saving metrics", e)

    async def load_metrics(self) -> Dict[str, Any]:
        """Load all metrics from database."""
        try:
            return await self.get_all_metrics()
        except Exception as e:
            self.logger.error(f"Error loading metrics: {e}")
            # Return empty metrics if database error
            return {}
