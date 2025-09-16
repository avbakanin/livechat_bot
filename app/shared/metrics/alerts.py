"""
Advanced metrics alerts and notifications system.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
import json


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class AlertRule:
    """Alert rule definition."""
    name: str
    metric_name: str
    condition: str  # ">", "<", ">=", "<=", "==", "!="
    threshold: float
    severity: AlertSeverity
    description: str
    enabled: bool = True
    cooldown_minutes: int = 5  # Minimum time between alerts
    tags: Dict[str, str] = None


@dataclass
class Alert:
    """Alert instance."""
    id: str
    rule_name: str
    metric_name: str
    current_value: float
    threshold: float
    severity: AlertSeverity
    status: AlertStatus
    created_at: datetime
    last_triggered: datetime
    message: str
    tags: Dict[str, str] = None
    metadata: Dict[str, Any] = None


class AlertManager:
    """Advanced alert management system."""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.notification_channels: List[Callable] = []
        self.last_alert_times: Dict[str, datetime] = {}
        
        # Initialize default rules
        self._setup_default_rules()
        
    def _setup_default_rules(self):
        """Setup default alert rules."""
        default_rules = [
            AlertRule(
                name="high_response_time",
                metric_name="response_time_message_ms",
                condition=">",
                threshold=5000.0,  # 5 seconds
                severity=AlertSeverity.HIGH,
                description="Response time is too high",
                cooldown_minutes=10
            ),
            AlertRule(
                name="low_cache_hit_rate",
                metric_name="cache_hit_rate_percent",
                condition="<",
                threshold=70.0,  # 70%
                severity=AlertSeverity.MEDIUM,
                description="Cache hit rate is too low",
                cooldown_minutes=15
            ),
            AlertRule(
                name="high_error_rate",
                metric_name="error_rate_percent",
                condition=">",
                threshold=5.0,  # 5%
                severity=AlertSeverity.CRITICAL,
                description="Error rate is too high",
                cooldown_minutes=5
            ),
            AlertRule(
                name="high_memory_usage",
                metric_name="system_memory_usage_mb",
                condition=">",
                threshold=1000.0,  # 1GB
                severity=AlertSeverity.HIGH,
                description="Memory usage is too high",
                cooldown_minutes=10
            ),
            AlertRule(
                name="high_cpu_usage",
                metric_name="system_cpu_usage_percent",
                condition=">",
                threshold=80.0,  # 80%
                severity=AlertSeverity.HIGH,
                description="CPU usage is too high",
                cooldown_minutes=10
            ),
            AlertRule(
                name="security_attack_detected",
                metric_name="attack_blocked",
                condition=">",
                threshold=0.0,
                severity=AlertSeverity.CRITICAL,
                description="Security attack detected",
                cooldown_minutes=1
            ),
            AlertRule(
                name="low_user_activity",
                metric_name="user_activity",
                condition="<",
                threshold=10.0,  # Less than 10 activities per hour
                severity=AlertSeverity.LOW,
                description="User activity is low",
                cooldown_minutes=60
            )
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
            
    def add_rule(self, rule: AlertRule) -> None:
        """Add alert rule."""
        self.rules[rule.name] = rule
        logging.info(f"Added alert rule: {rule.name}")
        
    def remove_rule(self, rule_name: str) -> None:
        """Remove alert rule."""
        if rule_name in self.rules:
            del self.rules[rule_name]
            logging.info(f"Removed alert rule: {rule_name}")
            
    def add_notification_channel(self, channel: Callable) -> None:
        """Add notification channel."""
        self.notification_channels.append(channel)
        logging.info("Added notification channel")
        
    async def check_metrics(self, metrics_data: Dict[str, Any]) -> List[Alert]:
        """Check metrics against alert rules."""
        triggered_alerts = []
        current_time = datetime.utcnow()
        
        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue
                
            # Check cooldown
            if rule_name in self.last_alert_times:
                time_since_last = current_time - self.last_alert_times[rule_name]
                if time_since_last.total_seconds() < rule.cooldown_minutes * 60:
                    continue
                    
            # Get metric value
            metric_value = self._get_metric_value(metrics_data, rule.metric_name)
            if metric_value is None:
                continue
                
            # Check condition
            if self._evaluate_condition(metric_value, rule.condition, rule.threshold):
                alert = self._create_alert(rule, metric_value, current_time)
                triggered_alerts.append(alert)
                
                # Update last alert time
                self.last_alert_times[rule_name] = current_time
                
                # Store alert
                self.active_alerts[alert.id] = alert
                self.alert_history.append(alert)
                
                # Send notifications
                await self._send_notifications(alert)
                
        return triggered_alerts
        
    def _get_metric_value(self, metrics_data: Dict[str, Any], metric_name: str) -> Optional[float]:
        """Get metric value from metrics data."""
        # Search through all categories
        for category_data in metrics_data.values():
            if isinstance(category_data, dict) and metric_name in category_data:
                metric_info = category_data[metric_name]
                if isinstance(metric_info, dict) and 'latest' in metric_info:
                    return float(metric_info['latest'])
                elif isinstance(metric_info, (int, float)):
                    return float(metric_info)
                    
        return None
        
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition."""
        if condition == ">":
            return value > threshold
        elif condition == "<":
            return value < threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        elif condition == "!=":
            return value != threshold
        else:
            return False
            
    def _create_alert(self, rule: AlertRule, current_value: float, timestamp: datetime) -> Alert:
        """Create alert instance."""
        alert_id = f"{rule.name}_{int(timestamp.timestamp())}"
        
        message = f"{rule.description}: {current_value} {rule.condition} {rule.threshold}"
        
        return Alert(
            id=alert_id,
            rule_name=rule.name,
            metric_name=rule.metric_name,
            current_value=current_value,
            threshold=rule.threshold,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            created_at=timestamp,
            last_triggered=timestamp,
            message=message,
            tags=rule.tags or {},
            metadata={
                "rule_description": rule.description,
                "cooldown_minutes": rule.cooldown_minutes
            }
        )
        
    async def _send_notifications(self, alert: Alert) -> None:
        """Send alert notifications."""
        for channel in self.notification_channels:
            try:
                await channel(alert)
            except Exception as e:
                logging.error(f"Error sending notification: {e}")
                
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert."""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].status = AlertStatus.ACKNOWLEDGED
            logging.info(f"Acknowledged alert: {alert_id}")
            return True
        return False
        
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert."""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].status = AlertStatus.RESOLVED
            del self.active_alerts[alert_id]
            logging.info(f"Resolved alert: {alert_id}")
            return True
        return False
        
    def get_active_alerts(self) -> List[Alert]:
        """Get active alerts."""
        return list(self.active_alerts.values())
        
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.created_at > cutoff]
        
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts by severity."""
        return [alert for alert in self.active_alerts.values() if alert.severity == severity]


class NotificationChannels:
    """Built-in notification channels."""
    
    @staticmethod
    async def console_notification(alert: Alert) -> None:
        """Console notification."""
        severity_emoji = {
            AlertSeverity.LOW: "🟡",
            AlertSeverity.MEDIUM: "🟠", 
            AlertSeverity.HIGH: "🔴",
            AlertSeverity.CRITICAL: "🚨"
        }
        
        emoji = severity_emoji.get(alert.severity, "⚠️")
        print(f"{emoji} ALERT: {alert.message}")
        print(f"   Rule: {alert.rule_name}")
        print(f"   Severity: {alert.severity.value}")
        print(f"   Time: {alert.created_at}")
        print(f"   Value: {alert.current_value} (threshold: {alert.threshold})")
        print()
        
    @staticmethod
    async def log_notification(alert: Alert) -> None:
        """Log notification."""
        log_level = {
            AlertSeverity.LOW: logging.INFO,
            AlertSeverity.MEDIUM: logging.WARNING,
            AlertSeverity.HIGH: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL
        }
        
        level = log_level.get(alert.severity, logging.WARNING)
        logging.log(level, f"ALERT: {alert.message} (Rule: {alert.rule_name})")
        
    @staticmethod
    async def file_notification(alert: Alert, filename: str = "alerts.log") -> None:
        """File notification."""
        alert_data = {
            "timestamp": alert.created_at.isoformat(),
            "rule_name": alert.rule_name,
            "severity": alert.severity.value,
            "message": alert.message,
            "current_value": alert.current_value,
            "threshold": alert.threshold,
            "tags": alert.tags
        }
        
        with open(filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(alert_data) + "\\n")
            
    @staticmethod
    async def webhook_notification(alert: Alert, webhook_url: str) -> None:
        """Webhook notification."""
        import aiohttp
        
        payload = {
            "text": f"🚨 Alert: {alert.message}",
            "attachments": [{
                "color": {
                    AlertSeverity.LOW: "good",
                    AlertSeverity.MEDIUM: "warning", 
                    AlertSeverity.HIGH: "danger",
                    AlertSeverity.CRITICAL: "danger"
                }.get(alert.severity, "warning"),
                "fields": [
                    {"title": "Rule", "value": alert.rule_name, "short": True},
                    {"title": "Severity", "value": alert.severity.value, "short": True},
                    {"title": "Current Value", "value": str(alert.current_value), "short": True},
                    {"title": "Threshold", "value": str(alert.threshold), "short": True}
                ]
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status != 200:
                        logging.error(f"Webhook notification failed: {response.status}")
        except Exception as e:
            logging.error(f"Webhook notification error: {e}")


class AlertDashboard:
    """Alert dashboard for monitoring."""
    
    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager
        
    def generate_html_dashboard(self) -> str:
        """Generate HTML alert dashboard."""
        active_alerts = self.alert_manager.get_active_alerts()
        recent_alerts = self.alert_manager.get_alert_history(24)
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Alert Dashboard</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .dashboard {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{
                    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    text-align: center;
                }}
                .alert-card {{
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 10px 0;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    border-left: 4px solid #ff6b6b;
                }}
                .alert-critical {{ border-left-color: #e74c3c; }}
                .alert-high {{ border-left-color: #f39c12; }}
                .alert-medium {{ border-left-color: #f1c40f; }}
                .alert-low {{ border-left-color: #2ecc71; }}
                .severity-badge {{
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .severity-critical {{ background-color: #e74c3c; }}
                .severity-high {{ background-color: #f39c12; }}
                .severity-medium {{ background-color: #f1c40f; }}
                .severity-low {{ background-color: #2ecc71; }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <div class="header">
                    <h1>🚨 Alert Dashboard</h1>
                    <p>Real-time monitoring alerts</p>
                </div>
                
                <h2>Active Alerts ({len(active_alerts)})</h2>
                {self._generate_active_alerts_html(active_alerts)}
                
                <h2>Recent Alerts ({len(recent_alerts)})</h2>
                {self._generate_recent_alerts_html(recent_alerts)}
            </div>
        </body>
        </html>
        """
        
        return html
        
    def _generate_active_alerts_html(self, alerts: List[Alert]) -> str:
        """Generate active alerts HTML."""
        if not alerts:
            return "<p>No active alerts</p>"
            
        html = ""
        for alert in alerts:
            severity_class = f"alert-{alert.severity.value}"
            html += f"""
            <div class="alert-card {severity_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3>{alert.message}</h3>
                    <span class="severity-badge severity-{alert.severity.value}">
                        {alert.severity.value.upper()}
                    </span>
                </div>
                <p><strong>Rule:</strong> {alert.rule_name}</p>
                <p><strong>Current Value:</strong> {alert.current_value}</p>
                <p><strong>Threshold:</strong> {alert.threshold}</p>
                <p><strong>Time:</strong> {alert.created_at}</p>
            </div>
            """
        return html
        
    def _generate_recent_alerts_html(self, alerts: List[Alert]) -> str:
        """Generate recent alerts HTML."""
        if not alerts:
            return "<p>No recent alerts</p>"
            
        html = ""
        for alert in alerts[-10:]:  # Show last 10
            severity_class = f"alert-{alert.severity.value}"
            html += f"""
            <div class="alert-card {severity_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4>{alert.message}</h4>
                    <span class="severity-badge severity-{alert.severity.value}">
                        {alert.severity.value.upper()}
                    </span>
                </div>
                <p><strong>Rule:</strong> {alert.rule_name} | <strong>Time:</strong> {alert.created_at}</p>
            </div>
            """
        return html


# Global instances
alert_manager = AlertManager()
alert_dashboard = AlertDashboard(alert_manager)

# Add default notification channels
alert_manager.add_notification_channel(NotificationChannels.console_notification)
alert_manager.add_notification_channel(NotificationChannels.log_notification)
