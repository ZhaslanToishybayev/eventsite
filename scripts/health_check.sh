#!/bin/bash
#
# Скрипт проверки здоровья UnitySphere
# Использование: ./scripts/health_check.sh
# Для cron: */5 * * * * /opt/unitysphere/scripts/health_check.sh
#

set -e

# Конфигурация
APP_URL="${APP_URL:-http://localhost:8001}"
HEALTH_ENDPOINT="${APP_URL}/api/v1/ai/health/"
ALERT_EMAIL="${ALERT_EMAIL:-admin@example.com}"
ALERT_WEBHOOK="${ALERT_WEBHOOK:-}"
LOG_FILE="${LOG_FILE:-/var/log/unitysphere/health_check.log}"

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Функция логирования
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Функция отправки алертов
send_alert() {
    local message=$1
    local severity=$2
    
    # Email alert
    if [ -n "$ALERT_EMAIL" ] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "[$severity] UnitySphere Health Alert" $ALERT_EMAIL
    fi
    
    # Webhook alert (Slack, Discord, etc.)
    if [ -n "$ALERT_WEBHOOK" ]; then
        curl -X POST "$ALERT_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"[$severity] $message\"}" \
            > /dev/null 2>&1 || true
    fi
}

# Начало проверки
log "🔍 Начало health check..."

# Счетчики
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# 1. Проверка Docker контейнеров
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
log "Проверка Docker контейнеров..."

if docker compose ps | grep -q "fnclub.*Up" && docker compose ps | grep -q "fnclub-db.*Up"; then
    log "✅ Docker контейнеры работают"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    log "❌ ОШИБКА: Docker контейнеры не работают!"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    send_alert "Docker контейнеры не работают!" "CRITICAL"
fi

# 2. Проверка HTTP health endpoint
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
log "Проверка HTTP health endpoint..."

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$HEALTH_ENDPOINT" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    log "✅ Health endpoint доступен (HTTP $HTTP_CODE)"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    
    # Проверяем детали health response
    HEALTH_RESPONSE=$(curl -s --max-time 10 "$HEALTH_ENDPOINT" 2>/dev/null)
    
    if echo "$HEALTH_RESPONSE" | grep -q '"overall_status":"healthy"'; then
        log "✅ Все компоненты здоровы"
    else
        log "⚠️  Предупреждение: Некоторые компоненты нездоровы"
        log "   Response: $HEALTH_RESPONSE"
        send_alert "Health check показывает проблемы: $HEALTH_RESPONSE" "WARNING"
    fi
else
    log "❌ ОШИБКА: Health endpoint недоступен (HTTP $HTTP_CODE)"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    send_alert "Health endpoint недоступен! HTTP $HTTP_CODE" "CRITICAL"
fi

# 3. Проверка PostgreSQL
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
log "Проверка PostgreSQL..."

if docker compose exec -T fnclub-db psql -U postgres -d postgres -c "SELECT 1" > /dev/null 2>&1; then
    log "✅ PostgreSQL доступен"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    
    # Проверка размера БД
    DB_SIZE=$(docker compose exec -T fnclub-db psql -U postgres -d postgres -t -c "SELECT pg_size_pretty(pg_database_size('postgres'));" 2>/dev/null | tr -d ' ')
    log "   Размер БД: $DB_SIZE"
    
    # Проверка количества подключений
    CONNECTIONS=$(docker compose exec -T fnclub-db psql -U postgres -d postgres -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | tr -d ' ')
    log "   Активных подключений: $CONNECTIONS"
    
    if [ "$CONNECTIONS" -gt 90 ]; then
        log "⚠️  Предупреждение: Много активных подключений ($CONNECTIONS)"
        send_alert "Много активных подключений к БД: $CONNECTIONS" "WARNING"
    fi
else
    log "❌ ОШИБКА: PostgreSQL недоступен!"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    send_alert "PostgreSQL недоступен!" "CRITICAL"
fi

# 4. Проверка места на диске
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
log "Проверка места на диске..."

DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

if [ "$DISK_USAGE" -lt 80 ]; then
    log "✅ Место на диске: ${DISK_USAGE}%"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
elif [ "$DISK_USAGE" -lt 90 ]; then
    log "⚠️  Предупреждение: Место на диске: ${DISK_USAGE}%"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    send_alert "Место на диске: ${DISK_USAGE}%" "WARNING"
else
    log "❌ КРИТИЧНО: Место на диске: ${DISK_USAGE}%"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    send_alert "Критический уровень места на диске: ${DISK_USAGE}%" "CRITICAL"
fi

# 5. Проверка использования памяти
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
log "Проверка использования памяти..."

MEM_USAGE=$(free | awk 'NR==2 {printf "%.0f", $3/$2 * 100}')

if [ "$MEM_USAGE" -lt 80 ]; then
    log "✅ Использование памяти: ${MEM_USAGE}%"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
elif [ "$MEM_USAGE" -lt 90 ]; then
    log "⚠️  Предупреждение: Использование памяти: ${MEM_USAGE}%"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    send_alert "Высокое использование памяти: ${MEM_USAGE}%" "WARNING"
else
    log "❌ КРИТИЧНО: Использование памяти: ${MEM_USAGE}%"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    send_alert "Критическое использование памяти: ${MEM_USAGE}%" "CRITICAL"
fi

# 6. Проверка логов на ошибки
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
log "Проверка логов на ошибки..."

ERROR_COUNT=$(docker compose logs --since 5m fnclub 2>&1 | grep -i "error\|exception\|critical" | wc -l)

if [ "$ERROR_COUNT" -eq 0 ]; then
    log "✅ Нет ошибок в логах (последние 5 минут)"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
elif [ "$ERROR_COUNT" -lt 5 ]; then
    log "⚠️  Предупреждение: Найдено $ERROR_COUNT ошибок в логах"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    log "❌ ВНИМАНИЕ: Найдено $ERROR_COUNT ошибок в логах!"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    send_alert "Много ошибок в логах: $ERROR_COUNT" "WARNING"
fi

# 7. Проверка времени ответа
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
log "Проверка времени ответа..."

RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}\n' --max-time 10 "$APP_URL" 2>/dev/null || echo "999")
RESPONSE_MS=$(echo "$RESPONSE_TIME * 1000" | bc | cut -d. -f1)

if [ "$RESPONSE_MS" -lt 1000 ]; then
    log "✅ Время ответа: ${RESPONSE_MS}ms"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
elif [ "$RESPONSE_MS" -lt 3000 ]; then
    log "⚠️  Предупреждение: Медленный ответ: ${RESPONSE_MS}ms"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    log "❌ КРИТИЧНО: Очень медленный ответ: ${RESPONSE_MS}ms"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    send_alert "Медленный ответ сервера: ${RESPONSE_MS}ms" "WARNING"
fi

# Итоговая статистика
log "========================================="
log "Итоги health check:"
log "Всего проверок: $TOTAL_CHECKS"
log "Успешно: $PASSED_CHECKS"
log "Провалено: $FAILED_CHECKS"
log "========================================="

# Определяем общий статус
if [ "$FAILED_CHECKS" -eq 0 ]; then
    log "✅ Все проверки пройдены успешно!"
    exit 0
elif [ "$FAILED_CHECKS" -le 2 ]; then
    log "⚠️  Некоторые проверки провалены"
    exit 1
else
    log "❌ Критические проблемы обнаружены!"
    send_alert "Критические проблемы в health check! Провалено: $FAILED_CHECKS из $TOTAL_CHECKS" "CRITICAL"
    exit 2
fi
