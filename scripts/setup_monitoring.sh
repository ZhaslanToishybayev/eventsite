#!/bin/bash
#
# Скрипт установки мониторинга и cron jobs
# Использование: sudo ./scripts/setup_monitoring.sh
#

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}📊 Установка системы мониторинга${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Проверка root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Этот скрипт должен запускаться от root${NC}"
    echo "   Используйте: sudo $0"
    exit 1
fi

# Конфигурация
PROJECT_DIR="/opt/unitysphere"
USER="unitysphere"

echo -e "${YELLOW}1️⃣  Установка cron job для health check...${NC}"

# Создаем cron job для health check каждые 5 минут
CRON_JOB="*/5 * * * * cd $PROJECT_DIR && /bin/bash $PROJECT_DIR/scripts/health_check.sh >> /var/log/unitysphere/health_check.log 2>&1"

# Добавляем в crontab пользователя
(crontab -u $USER -l 2>/dev/null | grep -v "health_check.sh"; echo "$CRON_JOB") | crontab -u $USER -

echo -e "${GREEN}✅ Health check cron job установлен (каждые 5 минут)${NC}"

echo ""
echo -e "${YELLOW}2️⃣  Установка cron job для бэкапа БД...${NC}"

# Создаем cron job для ежедневного бэкапа в 2:00
BACKUP_JOB="0 2 * * * cd $PROJECT_DIR && /bin/bash $PROJECT_DIR/scripts/backup_database.sh >> /var/log/unitysphere/backup.log 2>&1"

(crontab -u $USER -l 2>/dev/null | grep -v "backup_database.sh"; echo "$BACKUP_JOB") | crontab -u $USER -

echo -e "${GREEN}✅ Backup cron job установлен (ежедневно в 2:00)${NC}"

echo ""
echo -e "${YELLOW}3️⃣  Установка cron job для очистки логов...${NC}"

# Создаем cron job для еженедельной очистки старых логов
CLEANUP_JOB="0 3 * * 0 find /var/log/unitysphere -name '*.log' -mtime +30 -delete"

(crontab -u $USER -l 2>/dev/null | grep -v "find /var/log/unitysphere"; echo "$CLEANUP_JOB") | crontab -u $USER -

echo -e "${GREEN}✅ Log cleanup cron job установлен (еженедельно)${NC}"

echo ""
echo -e "${YELLOW}4️⃣  Настройка logrotate...${NC}"

# Создаем конфигурацию logrotate
cat > /etc/logrotate.d/unitysphere << 'EOF'
/var/log/unitysphere/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 unitysphere unitysphere
    sharedscripts
    postrotate
        systemctl reload unitysphere 2>/dev/null || true
    endscript
}

/var/log/unitysphere/ai_monitoring.log {
    daily
    rotate 60
    compress
    delaycompress
    missingok
    notifempty
    create 0644 unitysphere unitysphere
    size 100M
}
EOF

echo -e "${GREEN}✅ Logrotate настроен${NC}"

echo ""
echo -e "${YELLOW}5️⃣  Создание скрипта ежедневного отчета...${NC}"

# Создаем скрипт для ежедневного отчета
cat > $PROJECT_DIR/scripts/daily_report.sh << 'EOFSCRIPT'
#!/bin/bash
# Ежедневный отчет о состоянии системы

REPORT_DATE=$(date '+%Y-%m-%d')
REPORT_FILE="/tmp/unitysphere_daily_report_${REPORT_DATE}.txt"

{
    echo "========================================="
    echo "UnitySphere Daily Report - $REPORT_DATE"
    echo "========================================="
    echo ""
    
    echo "📊 Статистика системы:"
    echo "----------------------"
    
    # Статистика БД
    USERS=$(docker compose exec -T fnclub-db psql -U postgres -d postgres -t -c "SELECT COUNT(*) FROM accounts_user;" 2>/dev/null | tr -d ' ')
    CLUBS=$(docker compose exec -T fnclub-db psql -U postgres -d postgres -t -c "SELECT COUNT(*) FROM clubs_club;" 2>/dev/null | tr -d ' ')
    SESSIONS=$(docker compose exec -T fnclub-db psql -U postgres -d postgres -t -c "SELECT COUNT(*) FROM ai_consultant_chatsession;" 2>/dev/null | tr -d ' ')
    NEW_USERS=$(docker compose exec -T fnclub-db psql -U postgres -d postgres -t -c "SELECT COUNT(*) FROM accounts_user WHERE date_joined >= CURRENT_DATE;" 2>/dev/null | tr -d ' ')
    
    echo "Всего пользователей: $USERS"
    echo "Новых пользователей за день: $NEW_USERS"
    echo "Всего клубов: $CLUBS"
    echo "Всего AI сессий: $SESSIONS"
    echo ""
    
    echo "💾 Ресурсы:"
    echo "----------------------"
    echo "Использование диска:"
    df -h / | tail -1
    echo ""
    echo "Использование памяти:"
    free -h | grep Mem
    echo ""
    echo "Docker контейнеры:"
    docker compose ps
    echo ""
    
    echo "🔍 Последние ошибки в логах:"
    echo "----------------------"
    docker compose logs --since 24h fnclub 2>&1 | grep -i "error\|exception" | tail -10 || echo "Нет ошибок"
    echo ""
    
    echo "📈 Последние бэкапы:"
    echo "----------------------"
    ls -lht /backups/postgres/*.gz 2>/dev/null | head -5 || echo "Нет бэкапов"
    echo ""
    
    echo "========================================="
    echo "Отчет сгенерирован: $(date)"
    echo "========================================="
    
} > $REPORT_FILE

# Отправка отчета если настроен email
if [ -n "$DAILY_REPORT_EMAIL" ] && command -v mail &> /dev/null; then
    cat $REPORT_FILE | mail -s "UnitySphere Daily Report - $REPORT_DATE" $DAILY_REPORT_EMAIL
fi

cat $REPORT_FILE
EOFSCRIPT

chmod +x $PROJECT_DIR/scripts/daily_report.sh
chown $USER:$USER $PROJECT_DIR/scripts/daily_report.sh

# Добавляем в cron (ежедневно в 8:00)
REPORT_JOB="0 8 * * * cd $PROJECT_DIR && /bin/bash $PROJECT_DIR/scripts/daily_report.sh >> /var/log/unitysphere/daily_report.log 2>&1"
(crontab -u $USER -l 2>/dev/null | grep -v "daily_report.sh"; echo "$REPORT_JOB") | crontab -u $USER -

echo -e "${GREEN}✅ Daily report скрипт установлен (ежедневно в 8:00)${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Мониторинг настроен!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${YELLOW}📋 Установленные cron jobs:${NC}"
crontab -u $USER -l
echo ""

echo -e "${YELLOW}📝 Файлы логов:${NC}"
echo "   Health checks: /var/log/unitysphere/health_check.log"
echo "   Backups: /var/log/unitysphere/backup.log"
echo "   Daily reports: /var/log/unitysphere/daily_report.log"
echo ""

echo -e "${YELLOW}🧪 Тестирование:${NC}"
echo "   Health check: sudo -u $USER bash $PROJECT_DIR/scripts/health_check.sh"
echo "   Backup: sudo -u $USER bash $PROJECT_DIR/scripts/backup_database.sh"
echo "   Daily report: sudo -u $USER bash $PROJECT_DIR/scripts/daily_report.sh"
echo ""
