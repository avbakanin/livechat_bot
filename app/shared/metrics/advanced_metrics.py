"""
Advanced metrics and monitoring system with comprehensive categorization.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import json


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"           # Накопительный счетчик
    GAUGE = "gauge"               # Текущее значение
    HISTOGRAM = "histogram"       # Распределение значений
    TIMER = "timer"               # Время выполнения
    RATE = "rate"                 # Скорость изменений


class MetricCategory(Enum):
    """Categories of metrics."""
    SYSTEM = "system"             # Системные метрики
    PERFORMANCE = "performance"   # Метрики производительности
    BUSINESS = "business"         # Бизнес-метрики
    USER = "user"                # Пользовательские метрики
    SECURITY = "security"        # Метрики безопасности
    QUALITY = "quality"          # Метрики качества
    ERROR = "error"              # Метрики ошибок


class TimeWindow(Enum):
    """Time windows for metrics."""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


@dataclass
class MetricData:
    """Individual metric data."""
    name: str
    value: Any
    category: MetricCategory
    metric_type: MetricType
    time_window: TimeWindow
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricAggregation:
    """Metric aggregation data."""
    name: str
    category: MetricCategory
    time_window: TimeWindow
    count: int
    sum: float
    min: float
    max: float
    avg: float
    p50: float  # Median
    p95: float  # 95th percentile
    p99: float  # 99th percentile
    timestamp: datetime


class AdvancedMetricsCollector:
    """Advanced metrics collector with comprehensive categorization."""
    
    def __init__(self):
        self.metrics: Dict[str, List[MetricData]] = {}
        self.aggregations: Dict[str, List[MetricAggregation]] = {}
        self.start_time = datetime.utcnow()
        
        # Initialize metric storage
        for category in MetricCategory:
            for time_window in TimeWindow:
                key = f"{category.value}_{time_window.value}"
                self.metrics[key] = []
                self.aggregations[key] = []
                
    def record_metric(
        self,
        name: str,
        value: Any,
        category: MetricCategory,
        metric_type: MetricType = MetricType.GAUGE,
        time_window: TimeWindow = TimeWindow.DAY,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a metric."""
        metric_data = MetricData(
            name=name,
            value=value,
            category=category,
            metric_type=metric_type,
            time_window=time_window,
            timestamp=datetime.utcnow(),
            tags=tags or {},
            metadata=metadata or {}
        )
        
        key = f"{category.value}_{time_window.value}"
        self.metrics[key].append(metric_data)
        
        # Keep only last 1000 metrics per category/window
        if len(self.metrics[key]) > 1000:
            self.metrics[key] = self.metrics[key][-1000:]
            
    def get_metric_summary(
        self,
        category: Optional[MetricCategory] = None,
        time_window: Optional[TimeWindow] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get metric summary."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        if category and time_window:
            key = f"{category.value}_{time_window.value}"
            metrics = [m for m in self.metrics[key] if m.timestamp > cutoff]
        else:
            metrics = []
            for key, metric_list in self.metrics.items():
                metrics.extend([m for m in metric_list if m.timestamp > cutoff])
                
        # Group by name and calculate aggregations
        grouped_metrics = {}
        for metric in metrics:
            if metric.name not in grouped_metrics:
                grouped_metrics[metric.name] = []
            grouped_metrics[metric.name].append(metric)
            
        summary = {}
        for name, metric_list in grouped_metrics.items():
            values = [float(m.value) for m in metric_list if isinstance(m.value, (int, float))]
            if values:
                summary[name] = {
                    'count': len(values),
                    'sum': sum(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'latest': values[-1] if values else 0
                }
                
        return summary


class SystemMetrics:
    """System performance metrics."""
    
    def __init__(self, collector: AdvancedMetricsCollector):
        self.collector = collector
        
    def record_uptime(self) -> None:
        """Record system uptime."""
        uptime = (datetime.utcnow() - self.collector.start_time).total_seconds()
        self.collector.record_metric(
            name="system_uptime_seconds",
            value=uptime,
            category=MetricCategory.SYSTEM,
            metric_type=MetricType.GAUGE
        )
        
    def record_memory_usage(self, memory_mb: float) -> None:
        """Record memory usage."""
        self.collector.record_metric(
            name="system_memory_usage_mb",
            value=memory_mb,
            category=MetricCategory.SYSTEM,
            metric_type=MetricType.GAUGE
        )
        
    def record_cpu_usage(self, cpu_percent: float) -> None:
        """Record CPU usage."""
        self.collector.record_metric(
            name="system_cpu_usage_percent",
            value=cpu_percent,
            category=MetricCategory.SYSTEM,
            metric_type=MetricType.GAUGE
        )


class PerformanceMetrics:
    """Performance metrics."""
    
    def __init__(self, collector: AdvancedMetricsCollector):
        self.collector = collector
        
    def record_response_time(self, operation: str, response_time_ms: float) -> None:
        """Record response time."""
        self.collector.record_metric(
            name=f"response_time_{operation}_ms",
            value=response_time_ms,
            category=MetricCategory.PERFORMANCE,
            metric_type=MetricType.TIMER,
            tags={"operation": operation}
        )
        
    def record_database_query_time(self, query_type: str, query_time_ms: float) -> None:
        """Record database query time."""
        self.collector.record_metric(
            name="database_query_time_ms",
            value=query_time_ms,
            category=MetricCategory.PERFORMANCE,
            metric_type=MetricType.TIMER,
            tags={"query_type": query_type}
        )
        
    def record_cache_performance(self, cache_type: str, hit: bool) -> None:
        """Record cache performance."""
        self.collector.record_metric(
            name="cache_hit",
            value=1 if hit else 0,
            category=MetricCategory.PERFORMANCE,
            metric_type=MetricType.COUNTER,
            tags={"cache_type": cache_type, "hit": str(hit)}
        )


class BusinessMetrics:
    """Business metrics and KPIs."""
    
    def __init__(self, collector: AdvancedMetricsCollector):
        self.collector = collector
        
    def record_user_registration(self, user_id: int, source: str = "telegram") -> None:
        """Record user registration."""
        self.collector.record_metric(
            name="user_registration",
            value=1,
            category=MetricCategory.BUSINESS,
            metric_type=MetricType.COUNTER,
            tags={"source": source}
        )
        
    def record_subscription_change(self, user_id: int, old_plan: str, new_plan: str) -> None:
        """Record subscription change."""
        self.collector.record_metric(
            name="subscription_change",
            value=1,
            category=MetricCategory.BUSINESS,
            metric_type=MetricType.COUNTER,
            tags={"old_plan": old_plan, "new_plan": new_plan}
        )
        
    def record_revenue(self, amount: float, currency: str = "RUB", source: str = "subscription") -> None:
        """Record revenue."""
        self.collector.record_metric(
            name="revenue",
            value=amount,
            category=MetricCategory.BUSINESS,
            metric_type=MetricType.COUNTER,
            tags={"currency": currency, "source": source}
        )
        
    def record_user_engagement(self, user_id: int, engagement_score: float) -> None:
        """Record user engagement score."""
        self.collector.record_metric(
            name="user_engagement_score",
            value=engagement_score,
            category=MetricCategory.BUSINESS,
            metric_type=MetricType.GAUGE,
            tags={"user_id": str(user_id)}
        )


class UserMetrics:
    """User behavior metrics."""
    
    def __init__(self, collector: AdvancedMetricsCollector):
        self.collector = collector
        
    def record_user_activity(self, user_id: int, activity_type: str) -> None:
        """Record user activity."""
        self.collector.record_metric(
            name="user_activity",
            value=1,
            category=MetricCategory.USER,
            metric_type=MetricType.COUNTER,
            tags={"user_id": str(user_id), "activity_type": activity_type}
        )
        
    def record_session_duration(self, user_id: int, duration_minutes: float) -> None:
        """Record session duration."""
        self.collector.record_metric(
            name="session_duration_minutes",
            value=duration_minutes,
            category=MetricCategory.USER,
            metric_type=MetricType.TIMER,
            tags={"user_id": str(user_id)}
        )
        
    def record_user_satisfaction(self, user_id: int, satisfaction_score: int) -> None:
        """Record user satisfaction score (1-5)."""
        self.collector.record_metric(
            name="user_satisfaction_score",
            value=satisfaction_score,
            category=MetricCategory.USER,
            metric_type=MetricType.GAUGE,
            tags={"user_id": str(user_id)}
        )


class SecurityMetrics:
    """Security metrics."""
    
    def __init__(self, collector: AdvancedMetricsCollector):
        self.collector = collector
        
    def record_security_event(self, event_type: str, severity: str, user_id: Optional[int] = None) -> None:
        """Record security event."""
        self.collector.record_metric(
            name="security_event",
            value=1,
            category=MetricCategory.SECURITY,
            metric_type=MetricType.COUNTER,
            tags={"event_type": event_type, "severity": severity, "user_id": str(user_id) if user_id else "unknown"}
        )
        
    def record_attack_blocked(self, attack_type: str, user_id: Optional[int] = None) -> None:
        """Record blocked attack."""
        self.collector.record_metric(
            name="attack_blocked",
            value=1,
            category=MetricCategory.SECURITY,
            metric_type=MetricType.COUNTER,
            tags={"attack_type": attack_type, "user_id": str(user_id) if user_id else "unknown"}
        )
        
    def record_user_blocked(self, user_id: int, reason: str, duration_hours: int) -> None:
        """Record user block."""
        self.collector.record_metric(
            name="user_blocked",
            value=1,
            category=MetricCategory.SECURITY,
            metric_type=MetricType.COUNTER,
            tags={"user_id": str(user_id), "reason": reason, "duration_hours": str(duration_hours)}
        )


class QualityMetrics:
    """Quality metrics."""
    
    def __init__(self, collector: AdvancedMetricsCollector):
        self.collector = collector
        
    def record_response_quality(self, response_id: str, quality_score: float) -> None:
        """Record response quality score."""
        self.collector.record_metric(
            name="response_quality_score",
            value=quality_score,
            category=MetricCategory.QUALITY,
            metric_type=MetricType.GAUGE,
            tags={"response_id": response_id}
        )
        
    def record_user_feedback(self, user_id: int, feedback_type: str, rating: int) -> None:
        """Record user feedback."""
        self.collector.record_metric(
            name="user_feedback",
            value=rating,
            category=MetricCategory.QUALITY,
            metric_type=MetricType.GAUGE,
            tags={"user_id": str(user_id), "feedback_type": feedback_type}
        )


class ErrorMetrics:
    """Error metrics."""
    
    def __init__(self, collector: AdvancedMetricsCollector):
        self.collector = collector
        
    def record_error(self, error_type: str, error_code: str, component: str) -> None:
        """Record error."""
        self.collector.record_metric(
            name="error_occurred",
            value=1,
            category=MetricCategory.ERROR,
            metric_type=MetricType.COUNTER,
            tags={"error_type": error_type, "error_code": error_code, "component": component}
        )
        
    def record_error_rate(self, component: str, error_rate: float) -> None:
        """Record error rate."""
        self.collector.record_metric(
            name="error_rate_percent",
            value=error_rate,
            category=MetricCategory.ERROR,
            metric_type=MetricType.GAUGE,
            tags={"component": component}
        )


class MetricsManager:
    """Central metrics manager."""
    
    def __init__(self):
        self.collector = AdvancedMetricsCollector()
        self.system = SystemMetrics(self.collector)
        self.performance = PerformanceMetrics(self.collector)
        self.business = BusinessMetrics(self.collector)
        self.user = UserMetrics(self.collector)
        self.security = SecurityMetrics(self.collector)
        self.quality = QualityMetrics(self.collector)
        self.error = ErrorMetrics(self.collector)
        
    def get_comprehensive_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "period_hours": hours,
            "system": self.collector.get_metric_summary(MetricCategory.SYSTEM, TimeWindow.HOUR, hours),
            "performance": self.collector.get_metric_summary(MetricCategory.PERFORMANCE, TimeWindow.HOUR, hours),
            "business": self.collector.get_metric_summary(MetricCategory.BUSINESS, TimeWindow.DAY, hours),
            "user": self.collector.get_metric_summary(MetricCategory.USER, TimeWindow.DAY, hours),
            "security": self.collector.get_metric_summary(MetricCategory.SECURITY, TimeWindow.HOUR, hours),
            "quality": self.collector.get_metric_summary(MetricCategory.QUALITY, TimeWindow.DAY, hours),
            "error": self.collector.get_metric_summary(MetricCategory.ERROR, TimeWindow.HOUR, hours),
        }
        
        return summary


# Global metrics manager
metrics_manager = MetricsManager()
