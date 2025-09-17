"""
Load testing and performance benchmarking for metrics system.
"""

import asyncio
import logging
import random
import statistics
import time
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class LoadTestResult:
    """Load test result data."""
    test_name: str
    duration_seconds: float
    total_operations: int
    successful_operations: int
    failed_operations: int
    operations_per_second: float
    average_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    max_latency_ms: float
    min_latency_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    errors: List[str]


class MetricsLoadTester:
    """Load tester for metrics system."""
    
    def __init__(self):
        self.results: List[LoadTestResult] = []
        
    def generate_test_metrics(self, count: int) -> List[Dict[str, Any]]:
        """Generate test metrics for load testing."""
        metrics = []
        categories = ['system', 'performance', 'business', 'user', 'security', 'quality', 'error']
        
        for i in range(count):
            metric = {
                'name': f'test_metric_{i % 100}',
                'value': random.uniform(0, 1000),
                'category': random.choice(categories),
                'tags': {
                    'user_id': str(random.randint(1, 10000)),
                    'session_id': f'session_{random.randint(1, 1000)}',
                    'region': random.choice(['us', 'eu', 'asia'])
                },
                'timestamp': time.time()
            }
            metrics.append(metric)
            
        return metrics
        
    def measure_latency(self, func, *args, **kwargs) -> tuple[float, bool]:
        """Measure function execution latency."""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            return latency_ms, True
        except Exception as e:
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            return latency_ms, False
            
    async def test_concurrent_writes(
        self, 
        metrics_manager, 
        concurrent_users: int = 100,
        operations_per_user: int = 1000,
        duration_seconds: int = 60
    ) -> LoadTestResult:
        """Test concurrent metric writes."""
        test_name = f"concurrent_writes_{concurrent_users}users"
        logging.info(f"Starting {test_name}")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        latencies = []
        successful_ops = 0
        failed_ops = 0
        errors = []
        
        async def user_worker(user_id: int):
            """Worker function for each concurrent user."""
            nonlocal successful_ops, failed_ops, latencies, errors
            
            user_metrics = self.generate_test_metrics(operations_per_user)
            user_latencies = []
            user_successful = 0
            user_failed = 0
            
            for metric in user_metrics:
                if time.time() >= end_time:
                    break
                    
                latency_ms, success = self.measure_latency(
                    metrics_manager.record_metric,
                    metric['name'],
                    metric['value'],
                    metric['category'],
                    metric['tags']
                )
                
                user_latencies.append(latency_ms)
                
                if success:
                    user_successful += 1
                else:
                    user_failed += 1
                    errors.append(f"User {user_id}: Failed to record metric")
                    
            # Thread-safe update of shared variables
            latencies.extend(user_latencies)
            successful_ops += user_successful
            failed_ops += user_failed
            
        # Run concurrent users
        tasks = [user_worker(i) for i in range(concurrent_users)]
        await asyncio.gather(*tasks)
        
        actual_duration = time.time() - start_time
        total_ops = successful_ops + failed_ops
        
        # Calculate statistics
        if latencies:
            ops_per_second = total_ops / actual_duration
            avg_latency = statistics.mean(latencies)
            p50_latency = statistics.quantiles(latencies, n=2)[0]
            p95_latency = statistics.quantiles(latencies, n=20)[18]
            p99_latency = statistics.quantiles(latencies, n=100)[98]
            max_latency = max(latencies)
            min_latency = min(latencies)
        else:
            ops_per_second = avg_latency = p50_latency = p95_latency = p99_latency = max_latency = min_latency = 0
            
        result = LoadTestResult(
            test_name=test_name,
            duration_seconds=actual_duration,
            total_operations=total_ops,
            successful_operations=successful_ops,
            failed_operations=failed_ops,
            operations_per_second=ops_per_second,
            average_latency_ms=avg_latency,
            p50_latency_ms=p50_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            max_latency_ms=max_latency,
            min_latency_ms=min_latency,
            memory_usage_mb=self._get_memory_usage(),
            cpu_usage_percent=self._get_cpu_usage(),
            errors=errors[:10]  # Limit errors
        )
        
        self.results.append(result)
        logging.info(f"Completed {test_name}: {ops_per_second:.1f} ops/sec, {avg_latency:.2f}ms avg latency")
        
        return result
        
    def test_burst_load(
        self, 
        metrics_manager, 
        burst_size: int = 10000,
        burst_duration_seconds: float = 1.0
    ) -> LoadTestResult:
        """Test burst load handling."""
        test_name = f"burst_load_{burst_size}ops"
        logging.info(f"Starting {test_name}")
        
        start_time = time.time()
        latencies = []
        successful_ops = 0
        failed_ops = 0
        errors = []
        
        # Generate burst metrics
        burst_metrics = self.generate_test_metrics(burst_size)
        
        # Execute burst
        for metric in burst_metrics:
            latency_ms, success = self.measure_latency(
                metrics_manager.record_metric,
                metric['name'],
                metric['value'],
                metric['category'],
                metric['tags']
            )
            
            latencies.append(latency_ms)
            
            if success:
                successful_ops += 1
            else:
                failed_ops += 1
                errors.append("Failed to record metric")
                
        actual_duration = time.time() - start_time
        total_ops = successful_ops + failed_ops
        
        # Calculate statistics
        if latencies:
            ops_per_second = total_ops / actual_duration
            avg_latency = statistics.mean(latencies)
            p50_latency = statistics.quantiles(latencies, n=2)[0]
            p95_latency = statistics.quantiles(latencies, n=20)[18]
            p99_latency = statistics.quantiles(latencies, n=100)[98]
            max_latency = max(latencies)
            min_latency = min(latencies)
        else:
            ops_per_second = avg_latency = p50_latency = p95_latency = p99_latency = max_latency = min_latency = 0
            
        result = LoadTestResult(
            test_name=test_name,
            duration_seconds=actual_duration,
            total_operations=total_ops,
            successful_operations=successful_ops,
            failed_operations=failed_ops,
            operations_per_second=ops_per_second,
            average_latency_ms=avg_latency,
            p50_latency_ms=p50_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            max_latency_ms=max_latency,
            min_latency_ms=min_latency,
            memory_usage_mb=self._get_memory_usage(),
            cpu_usage_percent=self._get_cpu_usage(),
            errors=errors[:10]
        )
        
        self.results.append(result)
        logging.info(f"Completed {test_name}: {ops_per_second:.1f} ops/sec, {avg_latency:.2f}ms avg latency")
        
        return result
        
    def test_memory_usage(
        self, 
        metrics_manager, 
        metrics_count: int = 100000
    ) -> LoadTestResult:
        """Test memory usage under load."""
        test_name = f"memory_usage_{metrics_count}metrics"
        logging.info(f"Starting {test_name}")
        
        start_time = time.time()
        initial_memory = self._get_memory_usage()
        
        # Generate and record metrics
        metrics = self.generate_test_metrics(metrics_count)
        latencies = []
        successful_ops = 0
        failed_ops = 0
        errors = []
        
        for metric in metrics:
            latency_ms, success = self.measure_latency(
                metrics_manager.record_metric,
                metric['name'],
                metric['value'],
                metric['category'],
                metric['tags']
            )
            
            latencies.append(latency_ms)
            
            if success:
                successful_ops += 1
            else:
                failed_ops += 1
                errors.append("Failed to record metric")
                
        final_memory = self._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        actual_duration = time.time() - start_time
        total_ops = successful_ops + failed_ops
        
        # Calculate statistics
        if latencies:
            ops_per_second = total_ops / actual_duration
            avg_latency = statistics.mean(latencies)
            p50_latency = statistics.quantiles(latencies, n=2)[0]
            p95_latency = statistics.quantiles(latencies, n=20)[18]
            p99_latency = statistics.quantiles(latencies, n=100)[98]
            max_latency = max(latencies)
            min_latency = min(latencies)
        else:
            ops_per_second = avg_latency = p50_latency = p95_latency = p99_latency = max_latency = min_latency = 0
            
        result = LoadTestResult(
            test_name=test_name,
            duration_seconds=actual_duration,
            total_operations=total_ops,
            successful_operations=successful_ops,
            failed_operations=failed_ops,
            operations_per_second=ops_per_second,
            average_latency_ms=avg_latency,
            p50_latency_ms=p50_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            max_latency_ms=max_latency,
            min_latency_ms=min_latency,
            memory_usage_mb=memory_increase,
            cpu_usage_percent=self._get_cpu_usage(),
            errors=errors[:10]
        )
        
        self.results.append(result)
        logging.info(f"Completed {test_name}: {memory_increase:.1f}MB memory increase")
        
        return result
        
    def test_cache_performance(
        self, 
        metrics_manager, 
        cache_operations: int = 100000
    ) -> LoadTestResult:
        """Test cache performance."""
        test_name = f"cache_performance_{cache_operations}ops"
        logging.info(f"Starting {test_name}")
        
        start_time = time.time()
        latencies = []
        successful_ops = 0
        failed_ops = 0
        errors = []
        
        # Test cache operations
        for i in range(cache_operations):
            # Generate test data
            test_data = {
                'metric_name': f'test_metric_{i % 1000}',
                'value': random.uniform(0, 1000),
                'timestamp': time.time()
            }
            
            # Test cache set
            latency_ms, success = self.measure_latency(
                metrics_manager.cache.set,
                f"test_key_{i}",
                test_data
            )
            
            latencies.append(latency_ms)
            
            if success:
                successful_ops += 1
            else:
                failed_ops += 1
                errors.append("Failed to set cache")
                
            # Test cache get
            latency_ms, success = self.measure_latency(
                metrics_manager.cache.get,
                f"test_key_{i}"
            )
            
            latencies.append(latency_ms)
            
            if success:
                successful_ops += 1
            else:
                failed_ops += 1
                errors.append("Failed to get cache")
                
        actual_duration = time.time() - start_time
        total_ops = successful_ops + failed_ops
        
        # Calculate statistics
        if latencies:
            ops_per_second = total_ops / actual_duration
            avg_latency = statistics.mean(latencies)
            p50_latency = statistics.quantiles(latencies, n=2)[0]
            p95_latency = statistics.quantiles(latencies, n=20)[18]
            p99_latency = statistics.quantiles(latencies, n=100)[98]
            max_latency = max(latencies)
            min_latency = min(latencies)
        else:
            ops_per_second = avg_latency = p50_latency = p95_latency = p99_latency = max_latency = min_latency = 0
            
        result = LoadTestResult(
            test_name=test_name,
            duration_seconds=actual_duration,
            total_operations=total_ops,
            successful_operations=successful_ops,
            failed_operations=failed_ops,
            operations_per_second=ops_per_second,
            average_latency_ms=avg_latency,
            p50_latency_ms=p50_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            max_latency_ms=max_latency,
            min_latency_ms=min_latency,
            memory_usage_mb=self._get_memory_usage(),
            cpu_usage_percent=self._get_cpu_usage(),
            errors=errors[:10]
        )
        
        self.results.append(result)
        logging.info(f"Completed {test_name}: {ops_per_second:.1f} ops/sec, {avg_latency:.2f}ms avg latency")
        
        return result
        
    def run_comprehensive_test_suite(self, metrics_manager) -> List[LoadTestResult]:
        """Run comprehensive test suite."""
        logging.info("Starting comprehensive load test suite")
        
        test_results = []
        
        # Test 1: Concurrent writes with different user counts
        for users in [10, 50, 100, 200]:
            result = asyncio.run(self.test_concurrent_writes(
                metrics_manager, 
                concurrent_users=users,
                operations_per_user=100,
                duration_seconds=30
            ))
            test_results.append(result)
            
        # Test 2: Burst load
        for burst_size in [1000, 5000, 10000]:
            result = self.test_burst_load(
                metrics_manager,
                burst_size=burst_size,
                burst_duration_seconds=1.0
            )
            test_results.append(result)
            
        # Test 3: Memory usage
        for metrics_count in [10000, 50000, 100000]:
            result = self.test_memory_usage(
                metrics_manager,
                metrics_count=metrics_count
            )
            test_results.append(result)
            
        # Test 4: Cache performance
        result = self.test_cache_performance(
            metrics_manager,
            cache_operations=50000
        )
        test_results.append(result)
        
        logging.info("Completed comprehensive load test suite")
        return test_results
        
    def generate_report(self) -> str:
        """Generate load test report."""
        if not self.results:
            return "No test results available"
            
        report = []
        report.append("# Load Test Report")
        report.append("=" * 50)
        report.append("")
        
        # Summary table
        report.append("## Test Summary")
        report.append("")
        report.append("| Test Name | Ops/sec | Avg Latency (ms) | P95 Latency (ms) | Success Rate |")
        report.append("|-----------|---------|------------------|------------------|--------------|")
        
        for result in self.results:
            success_rate = (result.successful_operations / result.total_operations * 100) if result.total_operations > 0 else 0
            report.append(f"| {result.test_name} | {result.operations_per_second:.1f} | {result.average_latency_ms:.2f} | {result.p95_latency_ms:.2f} | {success_rate:.1f}% |")
            
        report.append("")
        
        # Detailed results
        report.append("## Detailed Results")
        report.append("")
        
        for result in self.results:
            report.append(f"### {result.test_name}")
            report.append("")
            report.append(f"- **Duration**: {result.duration_seconds:.2f} seconds")
            report.append(f"- **Total Operations**: {result.total_operations:,}")
            report.append(f"- **Successful Operations**: {result.successful_operations:,}")
            report.append(f"- **Failed Operations**: {result.failed_operations:,}")
            report.append(f"- **Operations per Second**: {result.operations_per_second:.1f}")
            report.append(f"- **Average Latency**: {result.average_latency_ms:.2f} ms")
            report.append(f"- **P50 Latency**: {result.p50_latency_ms:.2f} ms")
            report.append(f"- **P95 Latency**: {result.p95_latency_ms:.2f} ms")
            report.append(f"- **P99 Latency**: {result.p99_latency_ms:.2f} ms")
            report.append(f"- **Max Latency**: {result.max_latency_ms:.2f} ms")
            report.append(f"- **Min Latency**: {result.min_latency_ms:.2f} ms")
            report.append(f"- **Memory Usage**: {result.memory_usage_mb:.1f} MB")
            report.append(f"- **CPU Usage**: {result.cpu_usage_percent:.1f}%")
            
            if result.errors:
                report.append("- **Errors**:")
                for error in result.errors:
                    report.append(f"  - {error}")
                    
            report.append("")
            
        return "\\n".join(report)
        
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except ImportError:
            return 0.0
            
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            import psutil
            return psutil.cpu_percent()
        except ImportError:
            return 0.0


class PerformanceBenchmark:
    """Performance benchmark for metrics system."""
    
    def __init__(self):
        self.benchmarks: Dict[str, float] = {}
        
    def benchmark_metric_recording(self, metrics_manager, iterations: int = 10000) -> Dict[str, float]:
        """Benchmark metric recording performance."""
        logging.info(f"Benchmarking metric recording with {iterations} iterations")
        
        # Generate test metrics
        test_metrics = []
        for i in range(iterations):
            test_metrics.append({
                'name': f'benchmark_metric_{i}',
                'value': i * 1.5,
                'category': 'performance',
                'tags': {'iteration': str(i)}
            })
            
        # Benchmark recording
        start_time = time.time()
        
        for metric in test_metrics:
            metrics_manager.record_metric(
                metric['name'],
                metric['value'],
                metric['category'],
                metric['tags']
            )
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate metrics
        ops_per_second = iterations / duration
        avg_latency_ms = (duration / iterations) * 1000
        
        self.benchmarks['metric_recording_ops_per_second'] = ops_per_second
        self.benchmarks['metric_recording_avg_latency_ms'] = avg_latency_ms
        
        logging.info(f"Metric recording: {ops_per_second:.1f} ops/sec, {avg_latency_ms:.3f}ms avg latency")
        
        return {
            'ops_per_second': ops_per_second,
            'avg_latency_ms': avg_latency_ms,
            'duration_seconds': duration
        }
        
    def benchmark_cache_operations(self, metrics_manager, iterations: int = 100000) -> Dict[str, float]:
        """Benchmark cache operations."""
        logging.info(f"Benchmarking cache operations with {iterations} iterations")
        
        # Benchmark cache set
        start_time = time.time()
        
        for i in range(iterations):
            metrics_manager.cache.set(f"benchmark_key_{i}", {"value": i, "timestamp": time.time()})
            
        set_duration = time.time() - start_time
        
        # Benchmark cache get
        start_time = time.time()
        
        for i in range(iterations):
            metrics_manager.cache.get(f"benchmark_key_{i}")
            
        get_duration = time.time() - start_time
        
        # Calculate metrics
        set_ops_per_second = iterations / set_duration
        get_ops_per_second = iterations / get_duration
        set_avg_latency_ms = (set_duration / iterations) * 1000
        get_avg_latency_ms = (get_duration / iterations) * 1000
        
        self.benchmarks['cache_set_ops_per_second'] = set_ops_per_second
        self.benchmarks['cache_get_ops_per_second'] = get_ops_per_second
        self.benchmarks['cache_set_avg_latency_ms'] = set_avg_latency_ms
        self.benchmarks['cache_get_avg_latency_ms'] = get_avg_latency_ms
        
        logging.info(f"Cache set: {set_ops_per_second:.1f} ops/sec, {set_avg_latency_ms:.3f}ms avg latency")
        logging.info(f"Cache get: {get_ops_per_second:.1f} ops/sec, {get_avg_latency_ms:.3f}ms avg latency")
        
        return {
            'set_ops_per_second': set_ops_per_second,
            'get_ops_per_second': get_ops_per_second,
            'set_avg_latency_ms': set_avg_latency_ms,
            'get_avg_latency_ms': get_avg_latency_ms
        }
        
    def benchmark_aggregation(self, metrics_manager, metrics_count: int = 100000) -> Dict[str, float]:
        """Benchmark metrics aggregation."""
        logging.info(f"Benchmarking aggregation with {metrics_count} metrics")
        
        # Generate test metrics
        test_metrics = []
        for i in range(metrics_count):
            test_metrics.append({
                'name': f'aggregation_metric_{i % 100}',
                'value': random.uniform(0, 1000),
                'category': f'category_{i % 10}',
                'timestamp': time.time()
            })
            
        # Benchmark aggregation
        start_time = time.time()
        
        result = metrics_manager.get_aggregated_metrics(hours=1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate metrics
        aggregation_time_ms = duration * 1000
        
        self.benchmarks['aggregation_time_ms'] = aggregation_time_ms
        
        logging.info(f"Aggregation: {aggregation_time_ms:.2f}ms for {metrics_count} metrics")
        
        return {
            'aggregation_time_ms': aggregation_time_ms,
            'metrics_count': metrics_count
        }
        
    def run_all_benchmarks(self, metrics_manager) -> Dict[str, Any]:
        """Run all benchmarks."""
        logging.info("Starting performance benchmarks")
        
        results = {}
        
        # Benchmark metric recording
        results['metric_recording'] = self.benchmark_metric_recording(metrics_manager)
        
        # Benchmark cache operations
        results['cache_operations'] = self.benchmark_cache_operations(metrics_manager)
        
        # Benchmark aggregation
        results['aggregation'] = self.benchmark_aggregation(metrics_manager)
        
        logging.info("Completed performance benchmarks")
        
        return results


# Global instances
load_tester = MetricsLoadTester()
performance_benchmark = PerformanceBenchmark()
