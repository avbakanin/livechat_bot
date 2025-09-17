"""
High-performance scalable metrics system optimized for massive user loads.
"""

import asyncio
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"


class MetricCategory(Enum):
    """Categories of metrics."""
    SYSTEM = "system"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    USER = "user"
    SECURITY = "security"
    QUALITY = "quality"
    ERROR = "error"


class TimeWindow(Enum):
    """Time windows for metrics."""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


@dataclass
class MetricPoint:
    """High-performance metric point."""
    timestamp: float  # Unix timestamp for fast sorting
    value: float
    tags: Optional[Dict[str, str]] = None


@dataclass
class MetricBuffer:
    """High-performance metric buffer."""
    name: str
    category: MetricCategory
    metric_type: MetricType
    time_window: TimeWindow
    max_size: int = 10000  # Maximum points per buffer
    points: deque = field(default_factory=deque)
    _lock: threading.RLock = field(default_factory=threading.RLock)
    
    def add_point(self, value: float, tags: Optional[Dict[str, str]] = None):
        """Add metric point with thread safety."""
        with self._lock:
            self.points.append(MetricPoint(time.time(), value, tags))
            
            # Maintain max size
            if len(self.points) > self.max_size:
                self.points.popleft()
                
    def get_recent_points(self, seconds: int = 3600) -> List[MetricPoint]:
        """Get recent points within time window."""
        cutoff = time.time() - seconds
        with self._lock:
            return [p for p in self.points if p.timestamp >= cutoff]
            
    def clear_old_points(self, seconds: int = 3600):
        """Clear old points to free memory."""
        cutoff = time.time() - seconds
        with self._lock:
            while self.points and self.points[0].timestamp < cutoff:
                self.points.popleft()


class HighPerformanceMetricsCollector:
    """High-performance metrics collector optimized for scale."""
    
    def __init__(self, max_buffers: int = 1000):
        self.max_buffers = max_buffers
        self.buffers: Dict[str, MetricBuffer] = {}
        self.buffer_locks: Dict[str, threading.RLock] = {}
        
        # Performance optimization
        self._write_queue = asyncio.Queue(maxsize=10000)
        self._batch_size = 100
        self._batch_timeout = 1.0  # seconds
        self._last_batch_time = time.time()
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._batch_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Statistics
        self._stats = {
            'total_points': 0,
            'buffers_created': 0,
            'memory_usage_mb': 0,
            'write_queue_size': 0,
            'batch_count': 0
        }
        
    async def start(self):
        """Start background processing."""
        if self._running:
            return
            
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._batch_task = asyncio.create_task(self._batch_loop())
        logging.info("High-performance metrics collector started")
        
    async def stop(self):
        """Stop background processing."""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
        if self._batch_task:
            self._batch_task.cancel()
            
        # Process remaining items
        await self._process_batch()
        logging.info("High-performance metrics collector stopped")
        
    def record_metric(
        self,
        name: str,
        value: float,
        category: MetricCategory,
        metric_type: MetricType = MetricType.GAUGE,
        time_window: TimeWindow = TimeWindow.HOUR,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record metric with high performance."""
        buffer_key = f"{category.value}_{name}_{time_window.value}"
        
        # Get or create buffer
        if buffer_key not in self.buffers:
            if len(self.buffers) >= self.max_buffers:
                # Remove oldest buffer
                oldest_key = min(self.buffers.keys(), key=lambda k: self.buffers[k].points[0].timestamp if self.buffers[k].points else 0)
                del self.buffers[oldest_key]
                
            self.buffers[buffer_key] = MetricBuffer(
                name=name,
                category=category,
                metric_type=metric_type,
                time_window=time_window
            )
            self._stats['buffers_created'] += 1
            
        # Add point to buffer
        self.buffers[buffer_key].add_point(value, tags)
        self._stats['total_points'] += 1
        
        # Queue for async processing
        try:
            self._write_queue.put_nowait((buffer_key, value, tags))
        except asyncio.QueueFull:
            # Drop metric if queue is full (backpressure)
            logging.warning(f"Metrics queue full, dropping metric: {name}")
            
    async def _batch_loop(self):
        """Background batch processing loop."""
        while self._running:
            try:
                await asyncio.sleep(0.1)  # Check every 100ms
                
                current_time = time.time()
                queue_size = self._write_queue.qsize()
                
                # Process batch if conditions are met
                if (queue_size >= self._batch_size or 
                    (queue_size > 0 and current_time - self._last_batch_time >= self._batch_timeout)):
                    await self._process_batch()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in batch loop: {e}")
                
    async def _process_batch(self):
        """Process batch of metrics."""
        batch_items = []
        
        # Collect batch items
        while len(batch_items) < self._batch_size and not self._write_queue.empty():
            try:
                item = self._write_queue.get_nowait()
                batch_items.append(item)
            except asyncio.QueueEmpty:
                break
                
        if batch_items:
            # Process batch (could be database writes, external API calls, etc.)
            await self._write_batch(batch_items)
            self._stats['batch_count'] += 1
            self._last_batch_time = time.time()
            
    async def _write_batch(self, batch_items: List[tuple]):
        """Write batch of metrics (placeholder for actual implementation)."""
        # This would typically write to database, external systems, etc.
        # For now, just log the batch size
        logging.debug(f"Processed batch of {len(batch_items)} metrics")
        
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(60)  # Cleanup every minute
                await self._cleanup_old_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in cleanup loop: {e}")
                
    async def _cleanup_old_data(self):
        """Cleanup old metric data."""
        cleanup_count = 0
        current_time = time.time()
        
        # Cleanup buffers older than 24 hours
        for buffer_key, buffer in list(self.buffers.items()):
            buffer.clear_old_points(86400)  # 24 hours
            
            # Remove empty buffers
            if not buffer.points:
                del self.buffers[buffer_key]
                cleanup_count += 1
                
        if cleanup_count > 0:
            logging.info(f"Cleaned up {cleanup_count} empty buffers")
            
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary with performance stats."""
        cutoff_time = time.time() - (hours * 3600)
        
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'period_hours': hours,
            'performance_stats': self._stats.copy(),
            'metrics': {}
        }
        
        # Aggregate metrics by category
        for buffer_key, buffer in self.buffers.items():
            recent_points = buffer.get_recent_points(hours * 3600)
            
            if not recent_points:
                continue
                
            category = buffer.category.value
            if category not in summary['metrics']:
                summary['metrics'][category] = {}
                
            # Calculate aggregations
            values = [p.value for p in recent_points]
            if values:
                summary['metrics'][category][buffer.name] = {
                    'count': len(values),
                    'sum': sum(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'latest': values[-1]
                }
                
        return summary
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'total_buffers': len(self.buffers),
            'total_points': self._stats['total_points'],
            'queue_size': self._write_queue.qsize(),
            'memory_usage_mb': self._estimate_memory_usage(),
            'batch_count': self._stats['batch_count'],
            'buffers_created': self._stats['buffers_created']
        }
        
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB."""
        total_points = sum(len(buffer.points) for buffer in self.buffers.values())
        # Rough estimate: 100 bytes per point
        return (total_points * 100) / (1024 * 1024)


class ScalableUserMetrics:
    """Scalable user metrics optimized for massive user loads."""
    
    def __init__(self, collector: HighPerformanceMetricsCollector):
        self.collector = collector
        self.user_buckets = defaultdict(int)  # User ID -> bucket
        self.bucket_size = 1000  # Users per bucket
        
    def record_user_activity(self, user_id: int, activity_type: str):
        """Record user activity with bucketing for scale."""
        # Use bucketing to reduce cardinality
        bucket = user_id // self.bucket_size
        bucket_key = f"bucket_{bucket}"
        
        self.collector.record_metric(
            name="user_activity",
            value=1,
            category=MetricCategory.USER,
            metric_type=MetricType.COUNTER,
            tags={"bucket": bucket_key, "activity_type": activity_type}
        )
        
    def record_user_session(self, user_id: int, duration_minutes: float):
        """Record user session with bucketing."""
        bucket = user_id // self.bucket_size
        bucket_key = f"bucket_{bucket}"
        
        self.collector.record_metric(
            name="session_duration_minutes",
            value=duration_minutes,
            category=MetricCategory.USER,
            metric_type=MetricType.TIMER,
            tags={"bucket": bucket_key}
        )


class DistributedMetricsCollector:
    """Distributed metrics collector for horizontal scaling."""
    
    def __init__(self, node_id: str, collector: HighPerformanceMetricsCollector):
        self.node_id = node_id
        self.collector = collector
        self.remote_collectors: Dict[str, Callable] = {}
        
    def add_remote_collector(self, node_id: str, collector_func: Callable):
        """Add remote collector for distributed metrics."""
        self.remote_collectors[node_id] = collector_func
        
    async def get_cluster_metrics(self, hours: int = 1) -> Dict[str, Any]:
        """Get metrics from entire cluster."""
        cluster_metrics = {
            'node_id': self.node_id,
            'timestamp': datetime.utcnow().isoformat(),
            'nodes': {}
        }
        
        # Get local metrics
        cluster_metrics['nodes'][self.node_id] = self.collector.get_metrics_summary(hours)
        
        # Get remote metrics
        for remote_node_id, collector_func in self.remote_collectors.items():
            try:
                remote_metrics = await collector_func(hours)
                cluster_metrics['nodes'][remote_node_id] = remote_metrics
            except Exception as e:
                logging.error(f"Failed to get metrics from {remote_node_id}: {e}")
                cluster_metrics['nodes'][remote_node_id] = {'error': str(e)}
                
        return cluster_metrics
        
    def aggregate_cluster_metrics(self, cluster_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate metrics across cluster nodes."""
        aggregated = {
            'timestamp': cluster_metrics['timestamp'],
            'total_nodes': len(cluster_metrics['nodes']),
            'metrics': defaultdict(lambda: defaultdict(lambda: {
                'count': 0, 'sum': 0, 'min': float('inf'), 'max': float('-inf'), 'avg': 0
            }))
        }
        
        # Aggregate metrics from all nodes
        for node_id, node_metrics in cluster_metrics['nodes'].items():
            if 'error' in node_metrics:
                continue
                
            node_data = node_metrics.get('metrics', {})
            for category, metrics in node_data.items():
                for metric_name, metric_data in metrics.items():
                    agg = aggregated['metrics'][category][metric_name]
                    
                    agg['count'] += metric_data.get('count', 0)
                    agg['sum'] += metric_data.get('sum', 0)
                    agg['min'] = min(agg['min'], metric_data.get('min', float('inf')))
                    agg['max'] = max(agg['max'], metric_data.get('max', float('-inf')))
                    
        # Calculate averages
        for category_metrics in aggregated['metrics'].values():
            for metric_data in category_metrics.values():
                if metric_data['count'] > 0:
                    metric_data['avg'] = metric_data['sum'] / metric_data['count']
                    
        return aggregated


class MetricsLoadBalancer:
    """Load balancer for metrics processing."""
    
    def __init__(self, collectors: List[HighPerformanceMetricsCollector]):
        self.collectors = collectors
        self.current_index = 0
        self._lock = threading.Lock()
        
    def get_collector(self) -> HighPerformanceMetricsCollector:
        """Get next collector using round-robin."""
        with self._lock:
            collector = self.collectors[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.collectors)
            return collector
            
    def record_metric(self, *args, **kwargs):
        """Record metric using load balancing."""
        collector = self.get_collector()
        collector.record_metric(*args, **kwargs)


# Global instances
high_perf_collector = HighPerformanceMetricsCollector()
scalable_user_metrics = ScalableUserMetrics(high_perf_collector)
distributed_collector = DistributedMetricsCollector("node_1", high_perf_collector)
