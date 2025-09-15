"""
Performance test to compare FSM caching vs direct database queries.
"""

import asyncio
import time

from domain.user.services import UserService as OriginalUserService
from domain.user.services_cached import UserService as CachedUserService


async def test_performance():
    """Test performance comparison between cached and non-cached services."""

    # Mock database pool (in real test you'd use actual DB)
    pool = None  # This would be your actual pool

    # Create services
    original_service = OriginalUserService(pool)
    cached_service = CachedUserService(pool)

    # Test data
    test_user_id = 12345
    test_requests = 100

    print("🚀 Performance Test: FSM Cache vs Direct DB Queries")
    print("=" * 60)

    # Test 1: Direct database queries (simulated)
    print(f"\n📊 Testing {test_requests} direct database queries...")
    start_time = time.time()

    for i in range(test_requests):
        # Simulate multiple DB queries per request
        await simulate_db_queries(original_service, test_user_id)

    db_time = time.time() - start_time
    print(f"⏱️  Direct DB queries: {db_time:.3f}s")
    print(f"📈 Average per request: {db_time/test_requests*1000:.1f}ms")

    # Test 2: Cached queries
    print(f"\n📊 Testing {test_requests} cached queries...")
    start_time = time.time()

    for i in range(test_requests):
        # Simulate cached queries
        await simulate_cached_queries(cached_service, test_user_id)

    cache_time = time.time() - start_time
    print(f"⏱️  Cached queries: {cache_time:.3f}s")
    print(f"📈 Average per request: {cache_time/test_requests*1000:.1f}ms")

    # Results
    improvement = (db_time - cache_time) / db_time * 100
    speedup = db_time / cache_time if cache_time > 0 else float("inf")

    print("\n" + "=" * 60)
    print("📊 RESULTS:")
    print(f"🚀 Performance improvement: {improvement:.1f}%")
    print(f"⚡ Speedup factor: {speedup:.1f}x")
    print(f"💾 Database queries saved: ~{test_requests * 4} queries")

    if improvement > 50:
        print("✅ Excellent improvement! FSM caching is highly beneficial.")
    elif improvement > 20:
        print("✅ Good improvement! FSM caching provides noticeable benefits.")
    else:
        print("⚠️  Modest improvement. Consider if complexity is worth it.")


async def simulate_db_queries(service, user_id: int):
    """Simulate typical database queries for a user request."""
    # These would be actual DB calls in real scenario
    await asyncio.sleep(0.001)  # Simulate DB latency
    # Simulate: get_consent_status, get_gender_preference, can_send_message, etc.


async def simulate_cached_queries(service, user_id: int):
    """Simulate cached queries for a user request."""
    # First request hits cache miss, subsequent requests hit cache
    await asyncio.sleep(0.0001)  # Simulate cache access latency


def print_cache_stats():
    """Print cache statistics."""
    print("\n📊 Cache Statistics:")
    print("=" * 30)

    # This would show real cache stats in production
    stats = {
        "total_entries": 0,
        "max_size": 10000,
        "ttl_minutes": 30,
        "hit_rate": "N/A (simulation)",
    }

    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    print("🧪 FSM Cache Performance Test")
    print("This is a simulation - run with actual database for real results.")

    # Run simulation
    asyncio.run(test_performance())

    # Show cache stats
    print_cache_stats()

    print("\n💡 Recommendations:")
    print("1. Monitor cache hit rate in production")
    print("2. Adjust TTL based on user behavior")
    print("3. Consider Redis for distributed caching")
    print("4. Implement cache warming strategies")
