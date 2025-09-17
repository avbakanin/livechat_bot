"""
Real-time security monitoring system.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time


class SecurityLevel(Enum):
    """Security alert levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityAlert:
    """Security alert data."""
    alert_id: str
    timestamp: datetime
    level: SecurityLevel
    category: str
    description: str
    user_id: Optional[int]
    ip_address: Optional[str]
    details: Dict[str, Any]
    resolved: bool = False


class SecurityMetrics:
    """Security metrics collector."""
    
    def __init__(self):
        self.metrics = {
            'total_attacks': 0,
            'attacks_by_type': {},
            'attacks_by_hour': {},
            'blocked_users': 0,
            'failed_logins': 0,
            'suspicious_activities': 0,
            'security_score': 100,
        }
        self.start_time = datetime.utcnow()
        
    def record_attack(self, attack_type: str) -> None:
        """Record attack metric."""
        self.metrics['total_attacks'] += 1
        self.metrics['attacks_by_type'][attack_type] = \
            self.metrics['attacks_by_type'].get(attack_type, 0) + 1
            
        # Record by hour
        hour = datetime.utcnow().hour
        self.metrics['attacks_by_hour'][hour] = \
            self.metrics['attacks_by_hour'].get(hour, 0) + 1
            
    def record_blocked_user(self) -> None:
        """Record blocked user."""
        self.metrics['blocked_users'] += 1
        
    def record_failed_login(self) -> None:
        """Record failed login."""
        self.metrics['failed_logins'] += 1
        
    def record_suspicious_activity(self) -> None:
        """Record suspicious activity."""
        self.metrics['suspicious_activities'] += 1
        
    def calculate_security_score(self) -> int:
        """Calculate overall security score."""
        score = 100
        
        # Deduct points for attacks
        score -= min(self.metrics['total_attacks'] * 2, 50)
        
        # Deduct points for blocked users
        score -= min(self.metrics['blocked_users'] * 5, 30)
        
        # Deduct points for failed logins
        score -= min(self.metrics['failed_logins'] * 1, 20)
        
        return max(score, 0)
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        self.metrics['security_score'] = self.calculate_security_score()
        return self.metrics.copy()


class SecurityMonitor:
    """Real-time security monitoring."""
    
    def __init__(self):
        self.alerts: List[SecurityAlert] = []
        self.metrics = SecurityMetrics()
        self.monitoring_active = False
        self.alert_callbacks: List[callable] = []
        self._lock = threading.Lock()
        
    def start_monitoring(self) -> None:
        """Start security monitoring."""
        self.monitoring_active = True
        logging.info("Security monitoring started")
        
    def stop_monitoring(self) -> None:
        """Stop security monitoring."""
        self.monitoring_active = False
        logging.info("Security monitoring stopped")
        
    def add_alert_callback(self, callback: callable) -> None:
        """Add alert callback function."""
        self.alert_callbacks.append(callback)
        
    def create_alert(
        self,
        level: SecurityLevel,
        category: str,
        description: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> SecurityAlert:
        """Create security alert."""
        alert = SecurityAlert(
            alert_id=f"alert_{int(time.time())}_{len(self.alerts)}",
            timestamp=datetime.utcnow(),
            level=level,
            category=category,
            description=description,
            user_id=user_id,
            ip_address=ip_address,
            details=details or {}
        )
        
        with self._lock:
            self.alerts.append(alert)
            
        # Trigger callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logging.error(f"Alert callback error: {e}")
                
        return alert
        
    def get_recent_alerts(self, hours: int = 24) -> List[SecurityAlert]:
        """Get recent alerts."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        with self._lock:
            return [
                alert for alert in self.alerts
                if alert.timestamp > cutoff
            ]
            
    def get_alerts_by_level(self, level: SecurityLevel) -> List[SecurityAlert]:
        """Get alerts by security level."""
        with self._lock:
            return [alert for alert in self.alerts if alert.level == level]
            
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve security alert."""
        with self._lock:
            for alert in self.alerts:
                if alert.alert_id == alert_id:
                    alert.resolved = True
                    return True
        return False
        
    def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Get data for security dashboard."""
        recent_alerts = self.get_recent_alerts(24)
        
        return {
            'metrics': self.metrics.get_metrics(),
            'recent_alerts': [
                asdict(alert) for alert in recent_alerts[-10:]
            ],
            'alert_counts': {
                level.value: len(self.get_alerts_by_level(level))
                for level in SecurityLevel
            },
            'top_threats': self._get_top_threats(),
            'security_trend': self._get_security_trend(),
        }
        
    def _get_top_threats(self) -> List[Dict[str, Any]]:
        """Get top security threats."""
        threat_counts = {}
        
        for alert in self.alerts:
            category = alert.category
            threat_counts[category] = threat_counts.get(category, 0) + 1
            
        return [
            {'threat': threat, 'count': count}
            for threat, count in sorted(
                threat_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        ]
        
    def _get_security_trend(self) -> List[Dict[str, Any]]:
        """Get security trend over time."""
        now = datetime.utcnow()
        trend_data = []
        
        for i in range(7):  # Last 7 days
            day_start = now - timedelta(days=i+1)
            day_end = now - timedelta(days=i)
            
            day_alerts = [
                alert for alert in self.alerts
                if day_start <= alert.timestamp < day_end
            ]
            
            trend_data.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'alerts': len(day_alerts),
                'critical': len([a for a in day_alerts if a.level == SecurityLevel.CRITICAL])
            })
            
        return list(reversed(trend_data))


class SecurityNotifier:
    """Security notification system."""
    
    def __init__(self):
        self.notification_channels = []
        
    def add_notification_channel(self, channel: callable) -> None:
        """Add notification channel."""
        self.notification_channels.append(channel)
        
    async def send_alert_notification(self, alert: SecurityAlert) -> None:
        """Send alert notification."""
        if alert.level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            for channel in self.notification_channels:
                try:
                    await channel(alert)
                except Exception as e:
                    logging.error(f"Notification error: {e}")
                    
    def send_immediate_alert(self, message: str) -> None:
        """Send immediate alert."""
        logging.critical(f"🚨 IMMEDIATE SECURITY ALERT: {message}")


class SecurityDashboard:
    """Security dashboard for monitoring."""
    
    def __init__(self, monitor: SecurityMonitor):
        self.monitor = monitor
        
    def get_dashboard_html(self) -> str:
        """Generate security dashboard HTML."""
        data = self.monitor.get_security_dashboard_data()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ background: #f0f0f0; padding: 10px; margin: 10px 0; }}
                .alert {{ border-left: 4px solid #ff0000; padding: 10px; margin: 5px 0; }}
                .critical {{ border-color: #ff0000; }}
                .high {{ border-color: #ff8800; }}
                .medium {{ border-color: #ffaa00; }}
                .low {{ border-color: #00aa00; }}
            </style>
        </head>
        <body>
            <h1>Security Dashboard</h1>
            
            <div class="metric">
                <h3>Security Score: {data['metrics']['security_score']}/100</h3>
                <p>Total Attacks: {data['metrics']['total_attacks']}</p>
                <p>Blocked Users: {data['metrics']['blocked_users']}</p>
                <p>Failed Logins: {data['metrics']['failed_logins']}</p>
            </div>
            
            <h2>Recent Alerts</h2>
            {self._generate_alerts_html(data['recent_alerts'])}
            
            <h2>Top Threats</h2>
            {self._generate_threats_html(data['top_threats'])}
        </body>
        </html>
        """
        
        return html
        
    def _generate_alerts_html(self, alerts: List[Dict]) -> str:
        """Generate alerts HTML."""
        html = ""
        for alert in alerts:
            level_class = alert['level']
            html += f"""
            <div class="alert {level_class}">
                <strong>{alert['category']}</strong> - {alert['description']}
                <br><small>{alert['timestamp']}</small>
            </div>
            """
        return html
        
    def _generate_threats_html(self, threats: List[Dict]) -> str:
        """Generate threats HTML."""
        html = "<ul>"
        for threat in threats:
            html += f"<li>{threat['threat']}: {threat['count']} occurrences</li>"
        html += "</ul>"
        return html


# Global instances
security_monitor = SecurityMonitor()
security_notifier = SecurityNotifier()
security_dashboard = SecurityDashboard(security_monitor)
