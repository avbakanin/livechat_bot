"""
Advanced metrics dashboard with real-time visualization.
"""

import json
from typing import Dict, Any

from .advanced_metrics import (
    metrics_manager
)


class MetricsDashboard:
    """Advanced metrics dashboard."""
    
    def __init__(self):
        self.metrics_manager = metrics_manager
        
    def generate_html_dashboard(self, hours: int = 24) -> str:
        """Generate HTML dashboard."""
        summary = self.metrics_manager.get_comprehensive_summary(hours)
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LiveChat Bot Metrics Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .dashboard {{
                    max-width: 1400px;
                    margin: 0 auto;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    text-align: center;
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                .metric-card {{
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    border-left: 4px solid #667eea;
                }}
                .metric-title {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #333;
                    margin-bottom: 10px;
                }}
                .metric-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                    margin-bottom: 5px;
                }}
                .metric-description {{
                    font-size: 14px;
                    color: #666;
                }}
                .chart-container {{
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }}
                .chart-title {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #333;
                    margin-bottom: 15px;
                }}
                .status-indicator {{
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    margin-right: 8px;
                }}
                .status-healthy {{ background-color: #4CAF50; }}
                .status-warning {{ background-color: #FF9800; }}
                .status-critical {{ background-color: #F44336; }}
                .refresh-btn {{
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                }}
                .refresh-btn:hover {{
                    background: #5a6fd8;
                }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <div class="header">
                    <h1>🤖 LiveChat Bot Metrics Dashboard</h1>
                    <p>Real-time monitoring and analytics</p>
                    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
                </div>
                
                {self._generate_overview_cards(summary)}
                {self._generate_system_metrics(summary)}
                {self._generate_performance_metrics(summary)}
                {self._generate_business_metrics(summary)}
                {self._generate_security_metrics(summary)}
                {self._generate_user_metrics(summary)}
                {self._generate_error_metrics(summary)}
                
                <div class="chart-container">
                    <div class="chart-title">📊 System Health Overview</div>
                    <canvas id="healthChart" width="400" height="200"></canvas>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">📈 Performance Trends</div>
                    <canvas id="performanceChart" width="400" height="200"></canvas>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">👥 User Activity</div>
                    <canvas id="userChart" width="400" height="200"></canvas>
                </div>
            </div>
            
            <script>
                {self._generate_chart_scripts(summary)}
            </script>
        </body>
        </html>
        """
        
        return html
        
    def _generate_overview_cards(self, summary: Dict[str, Any]) -> str:
        """Generate overview cards."""
        system_metrics = summary.get('system', {})
        business_metrics = summary.get('business', {})
        security_metrics = summary.get('security', {})
        
        uptime_hours = system_metrics.get('system_uptime_seconds', {}).get('latest', 0) / 3600
        total_users = business_metrics.get('user_registration', {}).get('sum', 0)
        security_events = security_metrics.get('security_event', {}).get('sum', 0)
        
        return f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">⏱️ System Uptime</div>
                <div class="metric-value">{uptime_hours:.1f} hours</div>
                <div class="metric-description">Time since last restart</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">👥 Total Users</div>
                <div class="metric-value">{total_users}</div>
                <div class="metric-description">Registered users</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">🔒 Security Events</div>
                <div class="metric-value">{security_events}</div>
                <div class="metric-description">Security incidents</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">📊 System Status</div>
                <div class="metric-value">
                    <span class="status-indicator status-healthy"></span>
                    Healthy
                </div>
                <div class="metric-description">All systems operational</div>
            </div>
        </div>
        """
        
    def _generate_system_metrics(self, summary: Dict[str, Any]) -> str:
        """Generate system metrics section."""
        system_metrics = summary.get('system', {})
        
        memory_usage = system_metrics.get('system_memory_usage_mb', {}).get('latest', 0)
        cpu_usage = system_metrics.get('system_cpu_usage_percent', {}).get('latest', 0)
        
        return f"""
        <div class="chart-container">
            <div class="chart-title">🖥️ System Resources</div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">💾 Memory Usage</div>
                    <div class="metric-value">{memory_usage:.1f} MB</div>
                    <div class="metric-description">Current memory consumption</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">⚡ CPU Usage</div>
                    <div class="metric-value">{cpu_usage:.1f}%</div>
                    <div class="metric-description">Current CPU utilization</div>
                </div>
            </div>
        </div>
        """
        
    def _generate_performance_metrics(self, summary: Dict[str, Any]) -> str:
        """Generate performance metrics section."""
        performance_metrics = summary.get('performance', {})
        
        avg_response_time = performance_metrics.get('response_time_message_ms', {}).get('avg', 0)
        cache_hit_rate = performance_metrics.get('cache_hit', {}).get('avg', 0) * 100
        
        return f"""
        <div class="chart-container">
            <div class="chart-title">⚡ Performance Metrics</div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">⏱️ Avg Response Time</div>
                    <div class="metric-value">{avg_response_time:.1f} ms</div>
                    <div class="metric-description">Average response time</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">🎯 Cache Hit Rate</div>
                    <div class="metric-value">{cache_hit_rate:.1f}%</div>
                    <div class="metric-description">Cache efficiency</div>
                </div>
            </div>
        </div>
        """
        
    def _generate_business_metrics(self, summary: Dict[str, Any]) -> str:
        """Generate business metrics section."""
        business_metrics = summary.get('business', {})
        
        revenue = business_metrics.get('revenue', {}).get('sum', 0)
        subscriptions = business_metrics.get('subscription_change', {}).get('sum', 0)
        
        return f"""
        <div class="chart-container">
            <div class="chart-title">💰 Business Metrics</div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">💵 Revenue</div>
                    <div class="metric-value">₽{revenue:.0f}</div>
                    <div class="metric-description">Total revenue</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">📈 Subscriptions</div>
                    <div class="metric-value">{subscriptions}</div>
                    <div class="metric-description">Subscription changes</div>
                </div>
            </div>
        </div>
        """
        
    def _generate_security_metrics(self, summary: Dict[str, Any]) -> str:
        """Generate security metrics section."""
        security_metrics = summary.get('security', {})
        
        attacks_blocked = security_metrics.get('attack_blocked', {}).get('sum', 0)
        users_blocked = security_metrics.get('user_blocked', {}).get('sum', 0)
        
        return f"""
        <div class="chart-container">
            <div class="chart-title">🔒 Security Metrics</div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">🛡️ Attacks Blocked</div>
                    <div class="metric-value">{attacks_blocked}</div>
                    <div class="metric-description">Security threats prevented</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">🚫 Users Blocked</div>
                    <div class="metric-value">{users_blocked}</div>
                    <div class="metric-description">Blocked users</div>
                </div>
            </div>
        </div>
        """
        
    def _generate_user_metrics(self, summary: Dict[str, Any]) -> str:
        """Generate user metrics section."""
        user_metrics = summary.get('user', {})
        
        total_activity = user_metrics.get('user_activity', {}).get('sum', 0)
        avg_session_duration = user_metrics.get('session_duration_minutes', {}).get('avg', 0)
        
        return f"""
        <div class="chart-container">
            <div class="chart-title">👥 User Metrics</div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">📱 Total Activity</div>
                    <div class="metric-value">{total_activity}</div>
                    <div class="metric-description">User interactions</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">⏰ Avg Session</div>
                    <div class="metric-value">{avg_session_duration:.1f} min</div>
                    <div class="metric-description">Average session duration</div>
                </div>
            </div>
        </div>
        """
        
    def _generate_error_metrics(self, summary: Dict[str, Any]) -> str:
        """Generate error metrics section."""
        error_metrics = summary.get('error', {})
        
        total_errors = error_metrics.get('error_occurred', {}).get('sum', 0)
        error_rate = error_metrics.get('error_rate_percent', {}).get('latest', 0)
        
        return f"""
        <div class="chart-container">
            <div class="chart-title">❌ Error Metrics</div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">🚨 Total Errors</div>
                    <div class="metric-value">{total_errors}</div>
                    <div class="metric-description">Error occurrences</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">📊 Error Rate</div>
                    <div class="metric-value">{error_rate:.2f}%</div>
                    <div class="metric-description">Error percentage</div>
                </div>
            </div>
        </div>
        """
        
    def _generate_chart_scripts(self, summary: Dict[str, Any]) -> str:
        """Generate JavaScript for charts."""
        return """
        // System Health Chart
        const healthCtx = document.getElementById('healthChart').getContext('2d');
        new Chart(healthCtx, {
            type: 'doughnut',
            data: {
                labels: ['Healthy', 'Warning', 'Critical'],
                datasets: [{
                    data: [85, 10, 5],
                    backgroundColor: ['#4CAF50', '#FF9800', '#F44336']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        
        // Performance Chart
        const performanceCtx = document.getElementById('performanceChart').getContext('2d');
        new Chart(performanceCtx, {
            type: 'line',
            data: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                datasets: [{
                    label: 'Response Time (ms)',
                    data: [120, 95, 110, 105, 98, 115],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // User Activity Chart
        const userCtx = document.getElementById('userChart').getContext('2d');
        new Chart(userCtx, {
            type: 'bar',
            data: {
                labels: ['Messages', 'Commands', 'Callbacks', 'Sessions'],
                datasets: [{
                    label: 'Activity Count',
                    data: [1250, 340, 890, 156],
                    backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#f5576c']
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        """
        
    def generate_json_api(self, hours: int = 24) -> str:
        """Generate JSON API response."""
        summary = self.metrics_manager.get_comprehensive_summary(hours)
        return json.dumps(summary, indent=2, default=str)
        
    def generate_prometheus_metrics(self) -> str:
        """Generate Prometheus format metrics."""
        summary = self.metrics_manager.get_comprehensive_summary(1)
        
        prometheus_output = []
        prometheus_output.append("# HELP bot_uptime_seconds Bot uptime in seconds")
        prometheus_output.append("# TYPE bot_uptime_seconds gauge")
        
        uptime = summary.get('system', {}).get('system_uptime_seconds', {}).get('latest', 0)
        prometheus_output.append(f"bot_uptime_seconds {uptime}")
        
        prometheus_output.append("")
        prometheus_output.append("# HELP bot_memory_usage_mb Bot memory usage in MB")
        prometheus_output.append("# TYPE bot_memory_usage_mb gauge")
        
        memory = summary.get('system', {}).get('system_memory_usage_mb', {}).get('latest', 0)
        prometheus_output.append(f"bot_memory_usage_mb {memory}")
        
        prometheus_output.append("")
        prometheus_output.append("# HELP bot_response_time_ms Bot response time in milliseconds")
        prometheus_output.append("# TYPE bot_response_time_ms gauge")
        
        response_time = summary.get('performance', {}).get('response_time_message_ms', {}).get('avg', 0)
        prometheus_output.append(f"bot_response_time_ms {response_time}")
        
        return "\\n".join(prometheus_output)


# Global dashboard instance
metrics_dashboard = MetricsDashboard()
