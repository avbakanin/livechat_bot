#!/usr/bin/env python3
"""
Network connectivity checker for Telegram Bot.
Tests connection to Telegram API and other required services.
"""
import asyncio
import aiohttp
import time
from datetime import datetime


async def check_telegram_api():
    """Check connectivity to Telegram API."""
    print("🔍 Checking Telegram API connectivity...")
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.get("https://api.telegram.org/bot/getMe") as response:
                if response.status == 401:  # Unauthorized is expected without token
                    print("✅ Telegram API is reachable (401 Unauthorized - expected)")
                    return True
                elif response.status == 200:
                    print("✅ Telegram API is reachable and responding")
                    return True
                else:
                    print(f"⚠️ Telegram API responded with status: {response.status}")
                    return False
    except asyncio.TimeoutError:
        print("❌ Telegram API timeout - network may be slow")
        return False
    except aiohttp.ClientConnectorError:
        print("❌ Cannot connect to Telegram API - check internet connection")
        return False
    except Exception as e:
        print(f"❌ Telegram API error: {e}")
        return False


async def check_openai_api():
    """Check connectivity to OpenAI API."""
    print("🔍 Checking OpenAI API connectivity...")
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.get("https://api.openai.com/v1/models") as response:
                if response.status == 401:  # Unauthorized is expected without API key
                    print("✅ OpenAI API is reachable (401 Unauthorized - expected)")
                    return True
                elif response.status == 200:
                    print("✅ OpenAI API is reachable and responding")
                    return True
                else:
                    print(f"⚠️ OpenAI API responded with status: {response.status}")
                    return False
    except asyncio.TimeoutError:
        print("❌ OpenAI API timeout - network may be slow")
        return False
    except aiohttp.ClientConnectorError:
        print("❌ Cannot connect to OpenAI API - check internet connection")
        return False
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False


async def check_dns_resolution():
    """Check DNS resolution for required domains."""
    print("🔍 Checking DNS resolution...")
    
    domains = ["api.telegram.org", "api.openai.com"]
    
    for domain in domains:
        try:
            import socket
            socket.gethostbyname(domain)
            print(f"✅ DNS resolution for {domain}: OK")
        except socket.gaierror:
            print(f"❌ DNS resolution for {domain}: FAILED")
            return False
    
    return True


async def measure_latency():
    """Measure latency to Telegram API."""
    print("🔍 Measuring latency to Telegram API...")
    
    try:
        start_time = time.time()
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.get("https://api.telegram.org/bot/getMe") as response:
                latency = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                if latency < 100:
                    print(f"✅ Latency: {latency:.0f}ms (excellent)")
                elif latency < 500:
                    print(f"✅ Latency: {latency:.0f}ms (good)")
                elif latency < 1000:
                    print(f"⚠️ Latency: {latency:.0f}ms (slow)")
                else:
                    print(f"❌ Latency: {latency:.0f}ms (very slow)")
                
                return latency < 1000  # Consider under 1 second as acceptable
    except Exception as e:
        print(f"❌ Latency measurement failed: {e}")
        return False


async def main():
    """Main network check function."""
    print("🌐 Network Connectivity Checker")
    print("=" * 50)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = []
    
    # Run all checks
    checks.append(await check_dns_resolution())
    checks.append(await check_telegram_api())
    checks.append(await check_openai_api())
    checks.append(await measure_latency())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Network Check Summary")
    print("=" * 50)
    
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print("🎉 All network checks passed!")
        print("💡 Your network connection should work fine with the bot")
        return 0
    else:
        print(f"⚠️ {passed}/{total} checks passed")
        print("💡 Network issues detected - this may cause timeout errors")
        print("💡 Try:")
        print("   - Restarting your router/modem")
        print("   - Checking firewall settings")
        print("   - Using a different internet connection")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ Check cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
