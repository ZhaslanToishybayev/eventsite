"""
📊 Prometheus + Grafana Monitoring Stack для UnitySphere AI
Production-ready monitoring с AI-specific метриками
"""

# 📊 Prometheus Configuration
prometheus_config = """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "unitysphere_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # 🐍 Django Application
  - job_name: 'unitysphere-django'
    static_configs:
      - targets: ['host.docker.internal:8000']
    metrics_path: '/metrics/'
    scrape_interval: 30s

  # 🦄 Gunicorn
  - job_name: 'unitysphere-gunicorn'
    static_configs:
      - targets: ['host.docker.internal:8001']
    metrics_path: '/gunicorn/metrics'
    scrape_interval: 30s

  # 📝 Nginx
  - job_name: 'unitysphere-nginx'
    static_configs:
      - targets: ['host.docker.internal:9113']
    metrics_path: '/metrics'
    scrape_interval: 30s

  # 🚀 Redis (если используется)
  - job_name: 'unitysphere-redis'
    static_configs:
      - targets: ['redis:6379']
    metrics_path: '/metrics'
    scrape_interval: 30s

  # 🐍 Python application metrics
  - job_name: 'unitysphere-app'
    static_configs:
      - targets: ['host.docker.internal:8000']
    metrics_path: '/api/v1/ai/metrics/'
    scrape_interval: 60s
"""

# 📈 Grafana Dashboard Configuration
grafana_dashboard = {
    "dashboard": {
        "id": None,
        "title": "UnitySphere AI Monitoring",
        "tags": ["unitysphere", "ai", "django"],
        "timezone": "browser",
        "panels": [
            {
                "id": 1,
                "title": "AI Requests Rate",
                "type": "graph",
                "targets": [
                    {
                        "expr": "rate(ai_requests_total[5m])",
                        "legendFormat": "Requests/sec"
                    }
                ],
                "yAxes": [
                    {
                        "label": "Requests per second",
                        "min": 0
                    }
                ],
                "xAxis": {
                    "show": True
                }
            },
            {
                "id": 2,
                "title": "AI Response Time",
                "type": "graph",
                "targets": [
                    {
                        "expr": "histogram_quantile(0.95, rate(ai_response_time_seconds_bucket[5m]))",
                        "legendFormat": "95th percentile"
                    },
                    {
                        "expr": "histogram_quantile(0.50, rate(ai_response_time_seconds_bucket[5m]))",
                        "legendFormat": "50th percentile"
                    }
                ],
                "yAxes": [
                    {
                        "label": "Seconds",
                        "min": 0
                    }
                ]
            },
            {
                "id": 3,
                "title": "AI Chat Sessions",
                "type": "stat",
                "targets": [
                    {
                        "expr": "ai_active_sessions",
                        "legendFormat": "Active Sessions"
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "color": {
                            "mode": "palette-classic"
                        },
                        "custom": {
                            "displayMode": "lcd"
                        }
                    }
                }
            },
            {
                "id": 4,
                "title": "Django Application Health",
                "type": "singlestat",
                "targets": [
                    {
                        "expr": "up{job=\"unitysphere-django\"}",
                        "legendFormat": "Django Status"
                    }
                ],
                "valueMaps": [
                    {"op": "=", "value": "1", "text": "UP"},
                    {"op": "=", "value": "0", "text": "DOWN"}
                ],
                "colorBackground": True,
                "colors": ["red", "yellow", "green"]
            },
            {
                "id": 5,
                "title": "Database Connections",
                "type": "graph",
                "targets": [
                    {
                        "expr": "django_db_connections_total",
                        "legendFormat": "DB Connections"
                    }
                ]
            },
            {
                "id": 6,
                "title": "Error Rate",
                "type": "graph",
                "targets": [
                    {
                        "expr": "rate(ai_errors_total[5m])",
                        "legendFormat": "Errors/sec"
                    }
                ],
                "yAxes": [
                    {
                        "label": "Errors per second",
                        "min": 0
                    }
                ]
            },
            {
                "id": 7,
                "title": "Club Creation Requests",
                "type": "graph",
                "targets": [
                    {
                        "expr": "rate(club_creation_requests_total[5m])",
                        "legendFormat": "Club Creation/sec"
                    }
                ]
            },
            {
                "id": 8,
                "title": "Memory Usage",
                "type": "graph",
                "targets": [
                    {
                        "expr": "process_resident_memory_bytes{job=\"unitysphere-django\"} / 1024 / 1024",
                        "legendFormat": "Memory (MB)"
                    }
                ],
                "yAxes": [
                    {
                        "label": "MB",
                        "min": 0
                    }
                ]
            }
        ],
        "time": {
            "from": "now-1h",
            "to": "now"
        },
        "refresh": "30s"
    }
}

# 🚨 Alert Rules
alert_rules = """
groups:
- name: unitysphere_ai
  rules:
    # 🚨 High Error Rate
    - alert: HighAIErrorRate
      expr: rate(ai_errors_total[5m]) > 0.1
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: "High AI error rate detected"
        description: "AI error rate is {{ $value }} errors/sec for more than 2 minutes"

    # 🚨 High Response Time
    - alert: HighAIResponseTime
      expr: histogram_quantile(0.95, rate(ai_response_time_seconds_bucket[5m])) > 5
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High AI response time detected"
        description: "95th percentile response time is {{ $value }} seconds"

    # 🚨 Django Down
    - alert: DjangoDown
      expr: up{job="unitysphere-django"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Django application is down"
        description: "Django application has been down for more than 1 minute"

    # 🚨 High Memory Usage
    - alert: HighMemoryUsage
      expr: process_resident_memory_bytes{job="unitysphere-django"} / 1024 / 1024 > 512
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High memory usage detected"
        description: "Memory usage is {{ $value }} MB"

    # 🚨 No AI Requests (Unusual inactivity)
    - alert: NoAIRequests
      expr: rate(ai_requests_total[5m]) == 0
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "No AI requests detected"
        description: "No AI requests have been processed for more than 10 minutes"

    # 🚨 Database Connection Issues
    - alert: DatabaseConnectionIssues
      expr: django_db_connections_total > 20
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: "High database connection count"
        description: "Database connection count is {{ $value }}"
"""

# 🐳 Docker Compose для Monitoring Stack
docker_compose_monitoring = """
version: '3.8'

services:
  # 📊 Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: unitysphere-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./unitysphere_rules.yml:/etc/prometheus/unitysphere_rules.yml:ro
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  # 📈 Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: unitysphere-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - grafana-storage:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources

  # 🚨 AlertManager
  alertmanager:
    image: prom/alertmanager:latest
    container_name: unitysphere-alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro

  # 📝 Node Exporter
  node-exporter:
    image: prom/node-exporter:latest
    container_name: unitysphere-node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'

  # 📝 Nginx Exporter
  nginx-exporter:
    image: nginx/nginx-prometheus-exporter:latest
    container_name: unitysphere-nginx-exporter
    ports:
      - "9113:9113"
    command:
      - -nginx.scrape-uri=http://nginx:80/nginx_status

volumes:
  grafana-storage:

networks:
  default:
    name: unitysphere-monitoring
"""

# 🔔 AlertManager Configuration
alertmanager_config = """
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@fan-club.kz'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
    - match:
        severity: warning
      receiver: 'warning-alerts'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://127.0.0.1:5001/'

  - name: 'critical-alerts'
    email_configs:
      - to: 'admin@fan-club.kz'
        subject: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
        body: |
          Alert: {{ .GroupLabels.alertname }}
          Description: {{ .GroupLabels.description }}
          Severity: {{ .GroupLabels.severity }}
          Time: {{ .GroupLabels.time }}

  - name: 'warning-alerts'
    email_configs:
      - to: 'admin@fan-club.kz'
        subject: '⚠️ WARNING: {{ .GroupLabels.alertname }}'
        body: |
          Alert: {{ .GroupLabels.alertname }}
          Description: {{ .GroupLabels.description }}
          Severity: {{ .GroupLabels.severity }}
          Time: {{ .GroupLabels.time }}
"""

# 💾 Grafana Dashboard Provisioning
grafana_dashboard_config = """
apiVersion: 1

providers:
  - name: 'unitysphere'
    orgId: 1
    folder: 'UnitySphere'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
"""

grafana_datasource_config = """
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
"""
"""