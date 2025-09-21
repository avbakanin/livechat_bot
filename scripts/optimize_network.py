#!/usr/bin/env python3
"""
Network optimization script for Telegram Bot.
Provides recommendations and settings for unstable network connections.
"""
import platform
import subprocess
import sys


def check_os():
    """Check operating system and provide OS-specific recommendations."""
    os_name = platform.system().lower()
    print(f"🖥️ Operating System: {platform.system()} {platform.release()}")
    return os_name


def windows_optimizations():
    """Windows-specific network optimizations."""
    print("\n🪟 Windows Network Optimizations:")
    print("=" * 40)
    
    optimizations = [
        "1. Disable Windows Defender Firewall temporarily (if safe)",
        "2. Run as Administrator for better network access",
        "3. Disable Windows Update delivery optimization",
        "4. Set network profile to 'Private' instead of 'Public'",
        "5. Disable Windows Network Discovery if not needed"
    ]
    
    for opt in optimizations:
        print(f"   {opt}")
    
    print("\n💻 PowerShell commands to run (as Administrator):")
    print("   Set-NetConnectionProfile -InterfaceAlias '*' -NetworkCategory Private")
    print("   netsh winsock reset")
    print("   netsh int ip reset")


def linux_optimizations():
    """Linux-specific network optimizations."""
    print("\n🐧 Linux Network Optimizations:")
    print("=" * 40)
    
    optimizations = [
        "1. Increase network buffer sizes",
        "2. Optimize TCP settings",
        "3. Check DNS configuration",
        "4. Disable IPv6 if not needed",
        "5. Check firewall (iptables/ufw)"
    ]
    
    for opt in optimizations:
        print(f"   {opt}")
    
    print("\n💻 Commands to run (as root):")
    print("   echo 'net.core.rmem_max = 16777216' >> /etc/sysctl.conf")
    print("   echo 'net.core.wmem_max = 16777216' >> /etc/sysctl.conf")
    print("   echo 'net.ipv4.tcp_rmem = 4096 87380 16777216' >> /etc/sysctl.conf")
    print("   sysctl -p")


def general_recommendations():
    """General network optimization recommendations."""
    print("\n🌐 General Network Recommendations:")
    print("=" * 40)
    
    recommendations = [
        "1. Use wired connection instead of WiFi if possible",
        "2. Move closer to router/access point",
        "3. Restart router/modem",
        "4. Change DNS servers to faster ones:",
        "   - Cloudflare: 1.1.1.1, 1.0.0.1",
        "   - Google: 8.8.8.8, 8.8.4.4",
        "5. Disable VPN/proxy temporarily",
        "6. Check for bandwidth-heavy applications",
        "7. Contact ISP if issues persist"
    ]
    
    for rec in recommendations:
        print(f"   {rec}")


def check_dns_servers():
    """Check current DNS servers and suggest improvements."""
    print("\n🔍 Current DNS Configuration:")
    print("=" * 40)
    
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(['nslookup', 'google.com'], 
                                  capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(['nslookup', 'google.com'], 
                                  capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("   ✅ DNS resolution working")
        else:
            print("   ❌ DNS resolution issues detected")
    except Exception as e:
        print(f"   ⚠️ Could not test DNS: {e}")
    
    print("\n💡 Recommended DNS servers for better performance:")
    print("   Primary: 1.1.1.1 (Cloudflare)")
    print("   Secondary: 8.8.8.8 (Google)")
    print("   Alternative: 9.9.9.9 (Quad9)")


def bot_specific_settings():
    """Bot-specific settings for unstable connections."""
    print("\n🤖 Bot-Specific Settings for Unstable Connections:")
    print("=" * 50)
    
    settings = [
        "✅ Timeouts increased to 120 seconds (already applied)",
        "✅ Limited update types to reduce load (already applied)",
        "✅ Added drop_pending_updates for clean start",
        "💡 Consider running bot with lower priority:",
        "   Windows: start /low python app/main.py",
        "   Linux: nice -n 10 python app/main.py"
    ]
    
    for setting in settings:
        print(f"   {setting}")


def monitor_network():
    """Provide network monitoring commands."""
    print("\n📊 Network Monitoring Commands:")
    print("=" * 40)
    
    if platform.system().lower() == "windows":
        print("   ping api.telegram.org -t")
        print("   tracert api.telegram.org")
        print("   netsh interface ip show config")
    else:
        print("   ping -c 10 api.telegram.org")
        print("   traceroute api.telegram.org")
        print("   ip addr show")


def main():
    """Main optimization function."""
    print("🚀 Network Optimization for Telegram Bot")
    print("=" * 50)
    
    os_name = check_os()
    
    # OS-specific optimizations
    if os_name == "windows":
        windows_optimizations()
    elif os_name == "linux":
        linux_optimizations()
    else:
        print(f"\n⚠️ OS-specific optimizations not available for {platform.system()}")
    
    # General recommendations
    general_recommendations()
    
    # DNS check
    check_dns_servers()
    
    # Bot settings
    bot_specific_settings()
    
    # Monitoring
    monitor_network()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("=" * 50)
    print("1. Your network has latency issues (detected by check_network.py)")
    print("2. Bot timeouts have been increased to handle this")
    print("3. Apply the recommendations above for better stability")
    print("4. Monitor network performance regularly")
    print("5. Consider contacting your ISP if issues persist")
    
    print("\n🎯 Next Steps:")
    print("- Try the DNS changes first (easiest)")
    print("- Restart your router/modem")
    print("- Run the bot and monitor for improvements")
    print("- Use network monitoring commands if issues persist")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Optimization cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
