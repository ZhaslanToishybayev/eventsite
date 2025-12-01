#!/bin/bash
# 🚀 UnitySphere AI Monitoring Stack Deployment Script
# Быстрое развертывание Prometheus + Grafana + Sentry

set -e

echo "🚀 UnitySphere AI Monitoring Stack Deployment"
echo "=============================================="

# 🔧 Конфигурация
MONITORING_DIR="./monitoring"
GRAFANA_DIR="./monitoring/grafana"
PROMETHEUS_DIR="./monitoring/prometheus"

# 📁 Создание директорий
setup_directories() {
    echo "📁 Создание директорий для monitoring..."

    mkdir -p $MONITORING_DIR/{prometheus,grafana/{dashboards,provisioning/{dashboards,datasources}},alertmanager}
    mkdir -p $MONITORING_DIR/{loki,promtail,tempo,jaeger}
    mkdir -p $GRAFANA_DIR/{dashboards,provisioning/{dashboards,datasources}}

    echo "✅ Директории созданы"
}

# 📊 Prometheus Configuration
setup_prometheus() {
    echo "📊 Настройка Prometheus..."

    cat > $PROMETHEUS_DIR/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'unitysphere-monitor'

rule_files:
  - "alert_rules.yml"

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
    scrape_timeout: 10s

  # 🦄 Gunicorn (если используется)
  - job_name: 'unitysphere-gunicorn'
    static_configs:
      - targets: ['host.docker.internal:8001']
    metrics_path: '/metrics'
    scrape_interval: 30s

  # 📝 Nginx
  - job_name: 'unitysphere-nginx'
    static_configs:
      - targets: ['host.docker.internal:80']
    metrics_path: '/nginx_status'
    scrape_interval: 30s

  # 📝 Node Exporter
  - job_name: 'unitysphere-node'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 30s

  # 📊 cAdvisor
  - job_name: 'unitysphere-cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
    scrape_interval: 30s

  # 📝 Blackbox Exporter для uptime monitoring
  - job_name: 'unitysphere-blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - https://fan-club.kz
        - https://www.fan-club.kz
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
EOF

    # 🚨 Alert Rules
    cat > $PROMETHEUS_DIR/alert_rules.yml << 'EOF'
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

    # 🚨 No AI Requests
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
      expr: django_db_queries_total[5m] > 100
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: "High database query rate"
        description: "Database query rate is {{ $value }} queries/5min"

    # 🚨 High CPU Usage
    - alert: HighCPUUsage
      expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High CPU usage detected"
        description: "CPU usage is {{ $value }}%"

    # 🚨 Disk Space Low
    - alert: DiskSpaceLow
      expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 90
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "Disk space is low"
        description: "Disk usage is {{ $value }}%"
EOF

    echo "✅ Prometheus настроен"
}

# 📈 Grafana Configuration
setup_grafana() {
    echo "📈 Настройка Grafana..."

    # 📊 Datasource Configuration
    cat > $GRAFANA_DIR/provisioning/datasources/datasources.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: true

  - name: Jaeger
    type: jaeger
    access: proxy
    url: http://jaeger:16686
    editable: true
EOF

    # 📊 Dashboard Provisioning
    cat > $GRAFANA_DIR/provisioning/dashboards/dashboards.yml << 'EOF'
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
      path: /var/lib/grafana/dashboards
EOF

    # 🎯 UnitySphere AI Dashboard
    cat > $GRAFANA_DIR/dashboards/unitysphere-ai.json << 'EOF'
{
  "dashboard": {
    "id": null,
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
          "show": true
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
        ]
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
        "colorBackground": true,
        "colors": ["red", "yellow", "green"]
      },
      {
        "id": 5,
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
        "id": 6,
        "title": "Club Creation Requests",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(club_requests_total[5m])",
            "legendFormat": "Club Creation/sec"
          }
        ]
      },
      {
        "id": 7,
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
      },
      {
        "id": 8,
        "title": "Database Queries",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(django_db_queries_total[5m])",
            "legendFormat": "Queries/sec"
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
EOF

    echo "✅ Grafana настроена"
}

# 🚨 AlertManager Configuration
setup_alertmanager() {
    echo "🚨 Настройка AlertManager..."

    cat > $MONITORING_DIR/alertmanager/alertmanager.yml << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@fan-club.kz'
  smtp_auth_username: 'alerts@fan-club.kz'
  smtp_auth_password: 'your-email-password'

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
      - url: 'http://127.0.0.1:5001/webhook'

  - name: 'critical-alerts'
    email_configs:
      - to: 'admin@fan-club.kz'
        subject: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
        body: |
          Alert: {{ .GroupLabels.alertname }}
          Description: {{ .GroupLabels.description }}
          Severity: {{ .GroupLabels.severity }}
          Time: {{ .GroupLabels.time }}
          Instance: {{ .GroupLabels.instance }}

  - name: 'warning-alerts'
    email_configs:
      - to: 'admin@fan-club.kz'
        subject: '⚠️ WARNING: {{ .GroupLabels.alertname }}'
        body: |
          Alert: {{ .GroupLabels.alertname }}
          Description: {{ .GroupLabels.description }}
          Severity: {{ .GroupLabels.severity }}
          Time: {{ .GroupLabels.time }}
          Instance: {{ .GroupLabels.instance }}
EOF

    echo "✅ AlertManager настроен"
}

# 📝 Loki Configuration
setup_loki() {
    echo "📝 Настройка Loki..."

    cat > $MONITORING_DIR/loki/config.yml << 'EOF'
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://alertmanager:9093

# By default, Loki will send anonymous, but uniquely-identifiable usage and configuration
# analytics to Grafana Labs. These statistics are sent to https://stats.grafana.org/
#
# Statistics help us better understand how Loki is used, and they show us performance
# characteristics across different workloads. Please consider leaving these enabled
# since this data helps us improve the product for all users.
#
# If you would like to disable reporting, uncomment the following lines:
#analytics:
#  reporting_enabled: false
EOF

    echo "✅ Loki настроен"
}

# 📝 Promtail Configuration
setup_promtail() {
    echo "📝 Настройка Promtail..."

    cat > $MONITORING_DIR/promtail/config.yml << 'EOF'
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: unitysphere
    static_configs:
      - targets:
          - localhost
        labels:
          job: unitysphere-django
          __path__: /app/logs/*.log

  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: node-exporter
          __path__: /var/log/*log

  - job_name: docker
    docker_sd_config:
      host: unix:///var/run/docker.sock
      refresh_interval: 5s
    relabel_configs:
      - source_labels: ['__meta_docker_container_name']
        regex: '/(.*)'
        target_label: 'container'
    pipeline_stages:
      - json:
          expressions:
            output: log
            stream: stream
            attrs: attrs
      - json:
          source: attrs
          expressions:
            tag: tag
      - regex:
          source: tag
          regex: (?P<key>[^=]+)="(?P<value>[^"]+)"
      - timestamp:
          source: time
          format: RFC3339Nano
      - output:
          source: output
EOF

    echo "✅ Promtail настроен"
}

# 🚀 Запуск Monitoring Stack
start_monitoring() {
    echo "🚀 Запуск Monitoring Stack..."

    cd $MONITORING_DIR/..
    docker-compose -f docker-compose.monitoring.yml up -d

    echo "✅ Monitoring Stack запущен"
    echo ""
    echo "🌐 Доступные сервисы:"
    echo "📊 Grafana: http://localhost:3000 (admin/unitysphere_admin_2024)"
    echo "📊 Prometheus: http://localhost:9090"
    echo "🚨 AlertManager: http://localhost:9093"
    echo "📝 Loki: http://localhost:3100"
    echo "🔍 Jaeger: http://localhost:16686"
    echo ""
    echo "🔄 Для остановки: docker-compose -f docker-compose.monitoring.yml down"
}

# 🎯 Основной процесс
main() {
    echo "🎯 Начинаем развертывание Monitoring Stack..."

    setup_directories
    setup_prometheus
    setup_grafana
    setup_alertmanager
    setup_loki
    setup_promtail

    echo ""
    echo "✅ Monitoring Stack конфигурация завершена!"
    echo ""
    echo "🛠️ Команды для управления:"
    echo "cd $MONITORING_DIR/.. && docker-compose -f docker-compose.monitoring.yml up -d"
    echo "cd $MONITORING_DIR/.. && docker-compose -f docker-compose.monitoring.yml down"
    echo ""
    echo "💡 Не забудьте:"
    echo "1. Настроить email в alertmanager.yml"
    echo "2. Добавить Sentry DSN в environment variables"
    echo "3. Настроить Django middleware для метрик"
}

# 🚀 Запуск
main "$@"