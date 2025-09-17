"""
Advanced caching and batching system for metrics optimization.
"""

import asyncio
import logging
import time
import threading
from collections import defaultdict, OrderedDict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable
import json
import pickle
import hashlib


class CacheStrategy:
    """Cache strategies for different metric types."""
    LRU = "lru"           # Least Recently Used
    TTL = "ttl"           # Time To Live
    WRITE_THROUGH = "write_through"  # Write through cache
    WRITE_BACK = "write_back"        # Write back cache


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    timestamp: float
    ttl: Optional[float] = None
    access_count: int = 0
    last_access: float = 0
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl
        
    def touch(self):
        """Update access information."""
        self.access_count += 1
        self.last_access = time.time()


class MetricsCache:
    """High-performance metrics cache with multiple strategies."""
    
    def __init__(self, max_size: int = 10000, default_ttl: float = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired': 0
        }
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                
                if entry.is_expired():
                    del self._cache[key]
                    self._stats['expired'] += 1
                    self._stats['misses'] += 1
                    return None
                    
                # Move to end (LRU)
                self._cache.move_to_end(key)
                entry.touch()
                self._stats['hits'] += 1
                return entry.value
            else:
                self._stats['misses'] += 1
                return None
                
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set value in cache."""
        with self._lock:
            # Remove existing entry
            if key in self._cache:
                del self._cache[key]
                
            # Add new entry
            entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl or self.default_ttl
            )
            self._cache[key] = entry
            
            # Evict if over limit
            while len(self._cache) > self.max_size:
                self._cache.popitem(last=False)  # Remove oldest
                self._stats['evictions'] += 1
                
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
            
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            hit_rate = self._stats['hits'] / max(1, self._stats['hits'] + self._stats['misses'])
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hit_rate': hit_rate,
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'evictions': self._stats['evictions'],
                'expired': self._stats['expired']
            }
            
    def cleanup_expired(self) -> int:
        """Cleanup expired entries."""
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
                    
            for key in expired_keys:
                del self._cache[key]
                self._stats['expired'] += 1
                
            return len(expired_keys)


class MetricsBatcher:
    """High-performance metrics batcher."""
    
    def __init__(self, batch_size: int = 100, flush_interval: float = 1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batches: Dict[str, List[Any]] = defaultdict(list)
        self.batch_timestamps: Dict[str, float] = {}
        self._lock = threading.RLock()
        self._flush_callbacks: List[Callable] = []
        
    def add_metric(self, batch_key: str, metric: Any) -> bool:
        """Add metric to batch. Returns True if batch should be flushed."""
        with self._lock:
            if batch_key not in self.batch_timestamps:
                self.batch_timestamps[batch_key] = time.time()
                
            self.batches[batch_key].append(metric)
            
            # Check if batch is ready
            if len(self.batches[batch_key]) >= self.batch_size:
                return True
                
            # Check if batch is too old
            if time.time() - self.batch_timestamps[batch_key] >= self.flush_interval:
                return True
                
            return False
            
    def flush_batch(self, batch_key: str) -> List[Any]:
        """Flush batch and return metrics."""
        with self._lock:
            if batch_key not in self.batches:
                return []
                
            metrics = self.batches[batch_key].copy()
            del self.batches[batch_key]
            del self.batch_timestamps[batch_key]
            
            # Notify callbacks
            for callback in self._flush_callbacks:
                try:
                    callback(batch_key, metrics)
                except Exception as e:
                    logging.error(f"Error in flush callback: {e}")
                    
            return metrics
            
    def flush_all(self) -> Dict[str, List[Any]]:
        """Flush all batches."""
        with self._lock:
            all_batches = {}
            for batch_key in list(self.batches.keys()):
                all_batches[batch_key] = self.flush_batch(batch_key)
            return all_batches
            
    def add_flush_callback(self, callback: Callable) -> None:
        """Add callback for batch flush events."""
        self._flush_callbacks.append(callback)
        
    def get_stats(self) -> Dict[str, Any]:
        """Get batcher statistics."""
        with self._lock:
            total_pending = sum(len(batch) for batch in self.batches.values())
            return {
                'active_batches': len(self.batches),
                'total_pending_metrics': total_pending,
                'batch_size': self.batch_size,
                'flush_interval': self.flush_interval
            }


class MetricsAggregator:
    """High-performance metrics aggregator with caching."""
    
    def __init__(self, cache: MetricsCache):
        self.cache = cache
        self.aggregation_cache_ttl = 60  # 1 minute
        
    def aggregate_metrics(
        self, 
        metrics: List[Dict[str, Any]], 
        group_by: str = "name",
        cache_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Aggregate metrics with caching."""
        if cache_key:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
                
        # Perform aggregation
        grouped = defaultdict(list)
        for metric in metrics:
            key = metric.get(group_by, "unknown")
            grouped[key].append(metric)
            
        result = {}
        for key, metric_list in grouped.items():
            values = [m.get('value', 0) for m in metric_list if isinstance(m.get('value'), (int, float))]
            
            if values:
                result[key] = {
                    'count': len(values),
                    'sum': sum(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'latest': values[-1]
                }
                
        # Cache result
        if cache_key:
            self.cache.set(cache_key, result, self.aggregation_cache_ttl)
            
        return result
        
    def calculate_percentiles(
        self, 
        values: List[float], 
        percentiles: List[float] = [50, 90, 95, 99]
    ) -> Dict[str, float]:
        """Calculate percentiles with caching."""
        if not values:
            return {}
            
        # Create cache key
        cache_key = f"percentiles_{hashlib.md5(str(sorted(values)).encode()).hexdigest()}"
        
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
            
        # Calculate percentiles
        sorted_values = sorted(values)
        result = {}
        
        for p in percentiles:
            index = int((p / 100) * (len(sorted_values) - 1))
            result[f"p{p}"] = sorted_values[index]
            
        # Cache result
        self.cache.set(cache_key, result, self.aggregation_cache_ttl)
        return result


class MetricsCompressor:
    """Metrics compression for storage optimization."""
    
    @staticmethod
    def compress_metrics(metrics: List[Dict[str, Any]]) -> bytes:
        """Compress metrics data."""
        return pickle.dumps(metrics, protocol=pickle.HIGHEST_PROTOCOL)
        
    @staticmethod
    def decompress_metrics(data: bytes) -> List[Dict[str, Any]]:
        """Decompress metrics data."""
        return pickle.loads(data)
        
    @staticmethod
    def compress_json(metrics: Dict[str, Any]) -> bytes:
        """Compress JSON metrics."""
        json_str = json.dumps(metrics, separators=(',', ':'))
        return json_str.encode('utf-8')
        
    @staticmethod
    def decompress_json(data: bytes) -> Dict[str, Any]:
        """Decompress JSON metrics."""
        json_str = data.decode('utf-8')
        return json.loads(json_str)


class MetricsSampler:
    """Metrics sampling for high-volume scenarios."""
    
    def __init__(self, sample_rate: float = 1.0):
        self.sample_rate = sample_rate
        self._counter = 0
        
    def should_sample(self) -> bool:
        """Determine if current metric should be sampled."""
        if self.sample_rate >= 1.0:
            return True
            
        self._counter += 1
        return (self._counter % int(1 / self.sample_rate)) == 0
        
    def adjust_sample_rate(self, current_load: float, target_load: float) -> None:
        """Dynamically adjust sample rate based on load."""
        if current_load > target_load * 1.5:
            # Reduce sample rate
            self.sample_rate = max(0.1, self.sample_rate * 0.8)
        elif current_load < target_load * 0.5:
            # Increase sample rate
            self.sample_rate = min(1.0, self.sample_rate * 1.2)


class MetricsRateLimiter:
    """Rate limiter for metrics to prevent overload."""
    
    def __init__(self, max_metrics_per_second: int = 1000):
        self.max_metrics_per_second = max_metrics_per_second
        self.metrics_timestamps: List[float] = []
        self._lock = threading.Lock()
        
    def can_record_metric(self) -> bool:
        """Check if metric can be recorded without exceeding rate limit."""
        with self._lock:
            current_time = time.time()
            
            # Remove old timestamps
            cutoff = current_time - 1.0
            self.metrics_timestamps = [t for t in self.metrics_timestamps if t > cutoff]
            
            # Check if under limit
            if len(self.metrics_timestamps) < self.max_metrics_per_second:
                self.metrics_timestamps.append(current_time)
                return True
                
            return False
            
    def get_current_rate(self) -> float:
        """Get current metrics per second rate."""
        with self._lock:
            current_time = time.time()
            cutoff = current_time - 1.0
            recent_timestamps = [t for t in self.metrics_timestamps if t > cutoff]
            return len(recent_timestamps)


class OptimizedMetricsManager:
    """Optimized metrics manager with all performance features."""
    
    def __init__(self):
        # Core components
        self.cache = MetricsCache(max_size=50000, default_ttl=300)
        self.batcher = MetricsBatcher(batch_size=200, flush_interval=0.5)
        self.aggregator = MetricsAggregator(self.cache)
        self.compressor = MetricsCompressor()
        self.sampler = MetricsSampler(sample_rate=1.0)
        self.rate_limiter = MetricsRateLimiter(max_metrics_per_second=2000)
        
        # Metrics storage
        self.metrics_buffer: List[Dict[str, Any]] = []
        self._buffer_lock = threading.Lock()
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._flush_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Statistics
        self._stats = {
            'total_metrics': 0,
            'sampled_metrics': 0,
            'rate_limited_metrics': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
    async def start(self):
        """Start background processing."""
        if self._running:
            return
            
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._flush_task = asyncio.create_task(self._flush_loop())
        
        # Add flush callback
        self.batcher.add_flush_callback(self._on_batch_flush)
        
        logging.info("Optimized metrics manager started")
        
    async def stop(self):
        """Stop background processing."""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
        if self._flush_task:
            self._flush_task.cancel()
            
        # Flush remaining batches
        self.batcher.flush_all()
        
        logging.info("Optimized metrics manager stopped")
        
    def record_metric(
        self,
        name: str,
        value: float,
        category: str,
        tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """Record metric with all optimizations."""
        # Rate limiting
        if not self.rate_limiter.can_record_metric():
            self._stats['rate_limited_metrics'] += 1
            return False
            
        # Sampling
        if not self.sampler.should_sample():
            return False
            
        self._stats['sampled_metrics'] += 1
        
        # Create metric
        metric = {
            'name': name,
            'value': value,
            'category': category,
            'tags': tags or {},
            'timestamp': time.time()
        }
        
        # Add to batch
        batch_key = f"{category}_{name}"
        should_flush = self.batcher.add_metric(batch_key, metric)
        
        if should_flush:
            self.batcher.flush_batch(batch_key)
            
        self._stats['total_metrics'] += 1
        return True
        
    def _on_batch_flush(self, batch_key: str, metrics: List[Any]):
        """Handle batch flush."""
        with self._buffer_lock:
            self.metrics_buffer.extend(metrics)
            
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(30)  # Cleanup every 30 seconds
                
                # Cleanup cache
                expired_count = self.cache.cleanup_expired()
                if expired_count > 0:
                    logging.debug(f"Cleaned up {expired_count} expired cache entries")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in cleanup loop: {e}")
                
    async def _flush_loop(self):
        """Background flush loop."""
        while self._running:
            try:
                await asyncio.sleep(1.0)  # Flush every second
                
                # Flush batches
                flushed_batches = self.batcher.flush_all()
                if flushed_batches:
                    logging.debug(f"Flushed {len(flushed_batches)} batches")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in flush loop: {e}")
                
    def get_aggregated_metrics(self, hours: int = 1) -> Dict[str, Any]:
        """Get aggregated metrics with caching."""
        cache_key = f"aggregated_metrics_{hours}h"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            self._stats['cache_hits'] += 1
            return cached_result
            
        self._stats['cache_misses'] += 1
        
        # Get metrics from buffer
        with self._buffer_lock:
            cutoff_time = time.time() - (hours * 3600)
            recent_metrics = [
                m for m in self.metrics_buffer 
                if m.get('timestamp', 0) > cutoff_time
            ]
            
        # Aggregate metrics
        result = self.aggregator.aggregate_metrics(recent_metrics, group_by="category")
        
        # Cache result
        self.cache.set(cache_key, result, ttl=60)
        
        return result
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'cache_stats': self.cache.get_stats(),
            'batcher_stats': self.batcher.get_stats(),
            'rate_limiter_rate': self.rate_limiter.get_current_rate(),
            'sampler_rate': self.sampler.sample_rate,
            'manager_stats': self._stats.copy()
        }


# Global optimized instance
optimized_metrics_manager = OptimizedMetricsManager()
