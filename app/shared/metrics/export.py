"""
Advanced metrics export system for external monitoring tools.
"""

import csv
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional

from .advanced_metrics import metrics_manager


class MetricsExporter:
    """Advanced metrics export system."""
    
    def __init__(self):
        self.metrics_manager = metrics_manager
        
    def export_to_json(self, hours: int = 24, filename: Optional[str] = None) -> str:
        """Export metrics to JSON format."""
        summary = self.metrics_manager.get_comprehensive_summary(hours)
        
        export_data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "period_hours": hours,
            "metrics": summary
        }
        
        json_str = json.dumps(export_data, indent=2, default=str)
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(json_str)
                
        return json_str
        
    def export_to_csv(self, hours: int = 24, filename: Optional[str] = None) -> str:
        """Export metrics to CSV format."""
        summary = self.metrics_manager.get_comprehensive_summary(hours)
        
        csv_data = []
        csv_data.append(["Category", "Metric", "Value", "Count", "Min", "Max", "Avg", "Latest"])
        
        for category_name, category_data in summary.items():
            if isinstance(category_data, dict):
                for metric_name, metric_info in category_data.items():
                    if isinstance(metric_info, dict):
                        csv_data.append([
                            category_name,
                            metric_name,
                            metric_info.get('sum', ''),
                            metric_info.get('count', ''),
                            metric_info.get('min', ''),
                            metric_info.get('max', ''),
                            metric_info.get('avg', ''),
                            metric_info.get('latest', '')
                        ])
                        
        csv_str = "\\n".join([",".join(map(str, row)) for row in csv_data])
        
        if filename:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(csv_data)
                
        return csv_str
        
    def export_to_xml(self, hours: int = 24, filename: Optional[str] = None) -> str:
        """Export metrics to XML format."""
        summary = self.metrics_manager.get_comprehensive_summary(hours)
        
        root = ET.Element("metrics")
        root.set("export_timestamp", datetime.utcnow().isoformat())
        root.set("period_hours", str(hours))
        
        for category_name, category_data in summary.items():
            category_elem = ET.SubElement(root, "category")
            category_elem.set("name", category_name)
            
            if isinstance(category_data, dict):
                for metric_name, metric_info in category_data.items():
                    metric_elem = ET.SubElement(category_elem, "metric")
                    metric_elem.set("name", metric_name)
                    
                    if isinstance(metric_info, dict):
                        for key, value in metric_info.items():
                            metric_elem.set(key, str(value))
                            
        xml_str = ET.tostring(root, encoding='unicode')
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(xml_str)
                
        return xml_str
        
    def export_to_prometheus(self, hours: int = 1) -> str:
        """Export metrics to Prometheus format."""
        summary = self.metrics_manager.get_comprehensive_summary(hours)
        
        prometheus_lines = []
        prometheus_lines.append("# HELP bot_metrics Bot metrics in Prometheus format")
        prometheus_lines.append("# TYPE bot_metrics gauge")
        prometheus_lines.append("")
        
        # System metrics
        system_metrics = summary.get('system', {})
        for metric_name, metric_info in system_metrics.items():
            if isinstance(metric_info, dict) and 'latest' in metric_info:
                value = metric_info['latest']
                prometheus_lines.append(f"bot_system_{metric_name} {value}")
                
        prometheus_lines.append("")
        
        # Performance metrics
        performance_metrics = summary.get('performance', {})
        for metric_name, metric_info in performance_metrics.items():
            if isinstance(metric_info, dict) and 'avg' in metric_info:
                value = metric_info['avg']
                prometheus_lines.append(f"bot_performance_{metric_name} {value}")
                
        prometheus_lines.append("")
        
        # Business metrics
        business_metrics = summary.get('business', {})
        for metric_name, metric_info in business_metrics.items():
            if isinstance(metric_info, dict) and 'sum' in metric_info:
                value = metric_info['sum']
                prometheus_lines.append(f"bot_business_{metric_name} {value}")
                
        prometheus_lines.append("")
        
        # Security metrics
        security_metrics = summary.get('security', {})
        for metric_name, metric_info in security_metrics.items():
            if isinstance(metric_info, dict) and 'sum' in metric_info:
                value = metric_info['sum']
                prometheus_lines.append(f"bot_security_{metric_name} {value}")
                
        return "\\n".join(prometheus_lines)
        
    def export_to_influxdb(self, hours: int = 24) -> str:
        """Export metrics to InfluxDB line protocol format."""
        summary = self.metrics_manager.get_comprehensive_summary(hours)
        
        influx_lines = []
        timestamp = int(datetime.utcnow().timestamp() * 1000000000)  # nanoseconds
        
        for category_name, category_data in summary.items():
            if isinstance(category_data, dict):
                for metric_name, metric_info in category_data.items():
                    if isinstance(metric_info, dict):
                        # Create measurement name
                        measurement = f"bot_{category_name}"
                        
                        # Add fields
                        fields = []
                        for key, value in metric_info.items():
                            if isinstance(value, (int, float)):
                                fields.append(f"{key}={value}")
                                
                        if fields:
                            line = f"{measurement},metric={metric_name} {','.join(fields)} {timestamp}"
                            influx_lines.append(line)
                            
        return "\\n".join(influx_lines)
        
    def export_to_grafana_json(self, hours: int = 24) -> str:
        """Export metrics in Grafana JSON format."""
        summary = self.metrics_manager.get_comprehensive_summary(hours)
        
        grafana_data = {
            "dashboard": {
                "id": None,
                "title": "LiveChat Bot Metrics",
                "tags": ["bot", "metrics"],
                "timezone": "browser",
                "panels": [],
                "time": {
                    "from": f"now-{hours}h",
                    "to": "now"
                },
                "refresh": "5s"
            }
        }
        
        # Add panels for each category
        panel_id = 1
        for category_name, category_data in summary.items():
            if isinstance(category_data, dict):
                panel = {
                    "id": panel_id,
                    "title": f"{category_name.title()} Metrics",
                    "type": "stat",
                    "targets": []
                }
                
                for metric_name, metric_info in category_data.items():
                    if isinstance(metric_info, dict) and 'latest' in metric_info:
                        target = {
                            "expr": f"bot_{category_name}_{metric_name}",
                            "legendFormat": metric_name
                        }
                        panel["targets"].append(target)
                        
                grafana_data["dashboard"]["panels"].append(panel)
                panel_id += 1
                
        return json.dumps(grafana_data, indent=2)
        
    def export_to_datadog(self, hours: int = 24) -> str:
        """Export metrics to Datadog format."""
        summary = self.metrics_manager.get_comprehensive_summary(hours)
        
        datadog_metrics = []
        timestamp = int(datetime.utcnow().timestamp())
        
        for category_name, category_data in summary.items():
            if isinstance(category_data, dict):
                for metric_name, metric_info in category_data.items():
                    if isinstance(metric_info, dict) and 'latest' in metric_info:
                        value = metric_info['latest']
                        
                        metric_data = {
                            "metric": f"bot.{category_name}.{metric_name}",
                            "points": [[timestamp, value]],
                            "type": "gauge",
                            "tags": [f"category:{category_name}"]
                        }
                        
                        datadog_metrics.append(metric_data)
                        
        return json.dumps(datadog_metrics, indent=2)
        
    def export_to_newrelic(self, hours: int = 24) -> str:
        """Export metrics to New Relic format."""
        summary = self.metrics_manager.get_comprehensive_summary(hours)
        
        newrelic_data = {
            "metrics": []
        }
        
        timestamp = int(datetime.utcnow().timestamp() * 1000)  # milliseconds
        
        for category_name, category_data in summary.items():
            if isinstance(category_data, dict):
                for metric_name, metric_info in category_data.items():
                    if isinstance(metric_info, dict) and 'latest' in metric_info:
                        value = metric_info['latest']
                        
                        metric_data = {
                            "name": f"Custom/Bot/{category_name}/{metric_name}",
                            "value": value,
                            "timestamp": timestamp,
                            "attributes": {
                                "category": category_name,
                                "metric": metric_name
                            }
                        }
                        
                        newrelic_data["metrics"].append(metric_data)
                        
        return json.dumps(newrelic_data, indent=2)
        
    def export_to_splunk(self, hours: int = 24) -> str:
        """Export metrics to Splunk format."""
        summary = self.metrics_manager.get_comprehensive_summary(hours)
        
        splunk_events = []
        timestamp = datetime.utcnow().isoformat()
        
        for category_name, category_data in summary.items():
            if isinstance(category_data, dict):
                for metric_name, metric_info in category_data.items():
                    if isinstance(metric_info, dict):
                        event_data = {
                            "timestamp": timestamp,
                            "category": category_name,
                            "metric": metric_name,
                            "data": metric_info
                        }
                        
                        splunk_events.append(json.dumps(event_data))
                        
        return "\\n".join(splunk_events)
        
    def export_to_elasticsearch(self, hours: int = 24) -> str:
        """Export metrics to Elasticsearch format."""
        summary = self.metrics_manager.get_comprehensive_summary(hours)
        
        elasticsearch_docs = []
        timestamp = datetime.utcnow().isoformat()
        
        for category_name, category_data in summary.items():
            if isinstance(category_data, dict):
                for metric_name, metric_info in category_data.items():
                    if isinstance(metric_info, dict):
                        doc = {
                            "@timestamp": timestamp,
                            "category": category_name,
                            "metric_name": metric_name,
                            "metric_data": metric_info
                        }
                        
                        elasticsearch_docs.append(json.dumps(doc))
                        
        return "\\n".join(elasticsearch_docs)
        
    def export_custom_format(self, hours: int = 24, format_template: str = None) -> str:
        """Export metrics in custom format."""
        summary = self.metrics_manager.get_comprehensive_summary(hours)
        
        if not format_template:
            format_template = "Metric: {category}.{metric} = {value} (avg: {avg}, count: {count})"
            
        output_lines = []
        output_lines.append(f"# Metrics Export - {datetime.utcnow().isoformat()}")
        output_lines.append(f"# Period: {hours} hours")
        output_lines.append("")
        
        for category_name, category_data in summary.items():
            if isinstance(category_data, dict):
                output_lines.append(f"## {category_name.title()} Metrics")
                
                for metric_name, metric_info in category_data.items():
                    if isinstance(metric_info, dict):
                        line = format_template.format(
                            category=category_name,
                            metric=metric_name,
                            value=metric_info.get('latest', 'N/A'),
                            avg=metric_info.get('avg', 'N/A'),
                            count=metric_info.get('count', 'N/A'),
                            min=metric_info.get('min', 'N/A'),
                            max=metric_info.get('max', 'N/A'),
                            sum=metric_info.get('sum', 'N/A')
                        )
                        output_lines.append(line)
                        
                output_lines.append("")
                
        return "\\n".join(output_lines)
        
    def get_export_formats(self) -> List[str]:
        """Get list of available export formats."""
        return [
            "json",
            "csv", 
            "xml",
            "prometheus",
            "influxdb",
            "grafana",
            "datadog",
            "newrelic",
            "splunk",
            "elasticsearch",
            "custom"
        ]
        
    def export(self, format_type: str, hours: int = 24, filename: Optional[str] = None, **kwargs) -> str:
        """Export metrics in specified format."""
        format_methods = {
            "json": self.export_to_json,
            "csv": self.export_to_csv,
            "xml": self.export_to_xml,
            "prometheus": self.export_to_prometheus,
            "influxdb": self.export_to_influxdb,
            "grafana": self.export_to_grafana_json,
            "datadog": self.export_to_datadog,
            "newrelic": self.export_to_newrelic,
            "splunk": self.export_to_splunk,
            "elasticsearch": self.export_to_elasticsearch,
            "custom": self.export_custom_format
        }
        
        if format_type not in format_methods:
            raise ValueError(f"Unsupported format: {format_type}")
            
        method = format_methods[format_type]
        
        if format_type == "custom":
            return method(hours, kwargs.get('format_template'))
        else:
            return method(hours, filename)


# Global exporter instance
metrics_exporter = MetricsExporter()
