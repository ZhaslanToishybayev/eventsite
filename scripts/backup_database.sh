#!/bin/bash
#
# Скрипт автоматического бэкапа PostgreSQL базы данных
# Использование: ./scripts/backup_database.sh
#

set -e

# Конфигурация
BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/unitysphere_backup_$TIMESTAMP.sql"

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🗄️  UnitySphere Database Backup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Создаем директорию для бэкапов если её нет
mkdir -p "$BACKUP_DIR"

# Проверяем что контейнер работает
if ! docker compose ps fnclub-db | grep -q "Up"; then
    echo -e "${RED}❌ Ошибка: Контейнер fnclub-db не запущен!${NC}"
    exit 1
fi

echo -e "${YELLOW}📝 Создание бэкапа...${NC}"
echo "   Файл: $BACKUP_FILE"
echo ""

# Создаем бэкап
if docker compose exec -T fnclub-db pg_dump -U postgres postgres > "$BACKUP_FILE"; then
    echo -e "${GREEN}✅ Бэкап создан успешно${NC}"
    
    # Сжимаем бэкап
    echo -e "${YELLOW}🗜️  Сжатие бэкапа...${NC}"
    gzip -f "$BACKUP_FILE"
    BACKUP_FILE="$BACKUP_FILE.gz"
    
    # Размер файла
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Бэкап сжат: $SIZE${NC}"
    
    # Удаляем старые бэкапы
    echo -e "${YELLOW}🧹 Очистка старых бэкапов (старше $RETENTION_DAYS дней)...${NC}"
    OLD_BACKUPS=$(find "$BACKUP_DIR" -name "unitysphere_backup_*.sql.gz" -mtime +$RETENTION_DAYS -type f)
    
    if [ -n "$OLD_BACKUPS" ]; then
        echo "$OLD_BACKUPS" | while read -r file; do
            echo "   Удаление: $(basename "$file")"
            rm -f "$file"
        done
        echo -e "${GREEN}✅ Старые бэкапы удалены${NC}"
    else
        echo "   Нет старых бэкапов для удаления"
    fi
    
    # Статистика
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}📊 Статистика бэкапов${NC}"
    echo -e "${GREEN}========================================${NC}"
    BACKUP_COUNT=$(find "$BACKUP_DIR" -name "unitysphere_backup_*.sql.gz" -type f | wc -l)
    TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
    echo "   Всего бэкапов: $BACKUP_COUNT"
    echo "   Общий размер: $TOTAL_SIZE"
    echo "   Последний бэкап: $(basename "$BACKUP_FILE")"
    echo ""
    
    # Проверка целостности
    echo -e "${YELLOW}🔍 Проверка целостности архива...${NC}"
    if gzip -t "$BACKUP_FILE" 2>/dev/null; then
        echo -e "${GREEN}✅ Архив целостный${NC}"
    else
        echo -e "${RED}❌ Ошибка: Архив поврежден!${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ Бэкап завершен успешно!${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    # Отправка уведомления (опционально)
    if [ -n "$BACKUP_NOTIFICATION_URL" ]; then
        curl -s -X POST "$BACKUP_NOTIFICATION_URL" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"✅ Database backup completed: $BACKUP_FILE\"}" > /dev/null 2>&1 || true
    fi
    
else
    echo -e "${RED}❌ Ошибка при создании бэкапа!${NC}"
    
    # Отправка уведомления об ошибке
    if [ -n "$BACKUP_NOTIFICATION_URL" ]; then
        curl -s -X POST "$BACKUP_NOTIFICATION_URL" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"❌ Database backup FAILED!\"}" > /dev/null 2>&1 || true
    fi
    
    exit 1
fi
