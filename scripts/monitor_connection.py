#!/usr/bin/env python3
"""
Connection quality monitor for Telegram Bot.
Continuously monitors network stability and provides statistics.
"""
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
import statistics


class ConnectionMonitor:
    def __init__(self):
        self.latencies = []
        self.errors = []
        self.start_time = datetime.now()
        self.total_requests = 0
        self.successful_requests = 0
    
    async def test_connection(self):
        """Test connection to Telegram API."""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                async with session.get("https://api.telegram.org/bot/getMe") as response:
                    latency = (time.time() - start_time) * 1000
                    self.latencies.append(latency)
                    self.total_requests += 1
                    self.successful_requests += 1
                    return latency, True, response.status
        except Exception as e:
            self.total_requests += 1
            self.errors.append(str(e))
            return None, False, str(e)
    
    def get_statistics(self):
        """Get connection statistics."""
        if not self.latencies:
            return "No successful connections yet"
        
        avg_latency = statistics.mean(self.latencies)
        min_latency = min(self.latencies)
        max_latency = max(self.latencies)
        success_rate = (self.successful_requests / self.total_requests) * 100
        
        uptime = datetime.now() - self.start_time
        
        return {
            "uptime": str(uptime).split('.')[0],  # Remove microseconds
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "success_rate": f"{success_rate:.1f}%",
            "avg_latency": f"{avg_latency:.0f}ms",
            "min_latency": f"{min_latency:.0f}ms",
            "max_latency": f"{max_latency:.0f}ms",
            "error_count": len(self.errors)
        }
    
    def get_quality_assessment(self):
        """Assess connection quality."""
        if not self.latencies:
            return "Unknown", "🔍"
        
        avg_latency = statistics.mean(self.latencies)
        success_rate = (self.successful_requests / self.total_requests) * 100
        
        if success_rate >= 95 and avg_latency < 500:
            return "Excellent", "🟢"
        elif success_rate >= 90 and avg_latency < 1000:
            return "Good", "🟡"
        elif success_rate >= 80 and avg_latency < 2000:
            return "Fair", "🟠"
        else:
            return "Poor", "🔴"


async def monitor_connection(duration_minutes=10):
    """Monitor connection for specified duration."""
    monitor = ConnectionMonitor()
    
    print("🌐 Connection Quality Monitor")
    print("=" * 50)
    print(f"⏰ Monitoring for {duration_minutes} minutes...")
    print("Press Ctrl+C to stop early")
    print()
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    try:
        while time.time() < end_time:
            latency, success, status = await monitor.test_connection()
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if success:
                quality = "🟢" if latency < 500 else "🟡" if latency < 1000 else "🟠"
                print(f"{timestamp} {quality} Latency: {latency:.0f}ms (Status: {status})")
            else:
                print(f"{timestamp} 🔴 Error: {status}")
            
            # Show statistics every 30 seconds
            if len(monitor.latencies) % 10 == 0 and len(monitor.latencies) > 0:
                stats = monitor.get_statistics()
                quality, emoji = monitor.get_quality_assessment()
                
                print(f"\n📊 Statistics ({quality} {emoji}):")
                print(f"   Uptime: {stats['uptime']}")
                print(f"   Success Rate: {stats['success_rate']}")
                print(f"   Avg Latency: {stats['avg_latency']}")
                print(f"   Errors: {stats['error_count']}")
                print()
            
            await asyncio.sleep(3)  # Test every 3 seconds
            
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")
    
    # Final statistics
    print("\n" + "=" * 50)
    print("📊 Final Connection Report")
    print("=" * 50)
    
    stats = monitor.get_statistics()
    quality, emoji = monitor.get_quality_assessment()
    
    print(f"Quality Assessment: {quality} {emoji}")
    print(f"Total Runtime: {stats['uptime']}")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Successful Requests: {stats['successful_requests']}")
    print(f"Success Rate: {stats['success_rate']}")
    print(f"Average Latency: {stats['avg_latency']}")
    print(f"Min Latency: {stats['min_latency']}")
    print(f"Max Latency: {stats['max_latency']}")
    print(f"Total Errors: {stats['error_count']}")
    
    if monitor.errors:
        print("\n🔍 Recent Errors:")
        for error in monitor.errors[-5:]:  # Show last 5 errors
            print(f"   - {error}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if quality == "Poor":
        print("   - Check your internet connection")
        print("   - Try changing DNS servers")
        print("   - Restart your router/modem")
        print("   - Contact your ISP if issues persist")
    elif quality == "Fair":
        print("   - Connection is acceptable but could be better")
        print("   - Consider optimizing network settings")
        print("   - Monitor during different times of day")
    else:
        print("   - Connection quality is good!")
        print("   - Timeout errors in bot logs are normal")
        print("   - Bot should work reliably")


async def main():
    """Main monitoring function."""
    print("🤖 Telegram Bot Connection Monitor")
    print("=" * 50)
    
    try:
        # Quick initial test
        print("🔍 Running initial connection test...")
        monitor = ConnectionMonitor()
        latency, success, status = await monitor.test_connection()
        
        if success:
            print(f"✅ Initial test successful: {latency:.0f}ms")
        else:
            print(f"❌ Initial test failed: {status}")
            print("💡 Check your internet connection before monitoring")
            return 1
        
        # Ask for monitoring duration
        try:
            duration = input("\n⏰ How many minutes to monitor? (default: 5): ").strip()
            duration = int(duration) if duration else 5
        except ValueError:
            duration = 5
        
        # Start monitoring
        await monitor_connection(duration)
        
        return 0
        
    except Exception as e:
        print(f"❌ Monitoring error: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ Monitoring cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
