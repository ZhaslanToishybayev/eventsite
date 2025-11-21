#!/bin/bash
#
# Скрипт восстановления базы данных из бэкапа
# Использование: ./scripts/restore_database.sh <backup_file>
#

set -e

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🔄 UnitySphere Database Restore${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Проверка аргументов
if [ -z "$1" ]; then
    echo -e "${RED}❌ Ошибка: Укажите файл бэкапа${NC}"
    echo ""
    echo "Использование: $0 <backup_file>"
    echo ""
    echo "Доступные бэкапы:"
    ls -lh /backups/postgres/unitysphere_backup_*.sql.gz 2>/dev/null || echo "  Нет бэкапов"
    exit 1
fi

BACKUP_FILE="$1"

# Проверка существования файла
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Ошибка: Файл не найден: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️  ВНИМАНИЕ: Это действие перезапишет текущую базу данных!${NC}"
echo -e "${YELLOW}   Файл бэкапа: $BACKUP_FILE${NC}"
echo ""
read -p "Вы уверены? (введите 'YES' для продолжения): " CONFIRM

if [ "$CONFIRM" != "YES" ]; then
    echo -e "${YELLOW}❌ Отменено${NC}"
    exit 0
fi

# Проверка контейнера
if ! docker compose ps fnclub-db | grep -q "Up"; then
    echo -e "${RED}❌ Ошибка: Контейнер fnclub-db не запущен!${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}📝 Создание бэкапа текущей БД перед восстановлением...${NC}"
SAFETY_BACKUP="/tmp/unitysphere_before_restore_$(date +%Y%m%d_%H%M%S).sql.gz"
docker compose exec -T fnclub-db pg_dump -U postgres postgres | gzip > "$SAFETY_BACKUP"
echo -e "${GREEN}✅ Страховочный бэкап создан: $SAFETY_BACKUP${NC}"

echo ""
echo -e "${YELLOW}🗑️  Очистка базы данных...${NC}"
docker compose exec -T fnclub-db psql -U postgres -c "DROP DATABASE IF EXISTS postgres WITH (FORCE);" 2>/dev/null || true
docker compose exec -T fnclub-db psql -U postgres -c "CREATE DATABASE postgres;"
echo -e "${GREEN}✅ База данных очищена${NC}"

echo ""
echo -e "${YELLOW}📥 Восстановление из бэкапа...${NC}"

if [[ "$BACKUP_FILE" == *.gz ]]; then
    # Разархивируем и восстанавливаем
    gunzip -c "$BACKUP_FILE" | docker compose exec -T fnclub-db psql -U postgres postgres
else
    # Восстанавливаем напрямую
    cat "$BACKUP_FILE" | docker compose exec -T fnclub-db psql -U postgres postgres
fi

echo -e "${GREEN}✅ База данных восстановлена${NC}"

echo ""
echo -e "${YELLOW}🔍 Проверка восстановления...${NC}"

# Проверяем таблицы
TABLES=$(docker compose exec -T fnclub-db psql -U postgres postgres -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
USERS=$(docker compose exec -T fnclub-db psql -U postgres postgres -t -c "SELECT COUNT(*) FROM accounts_user;" 2>/dev/null | tr -d ' ' || echo "0")
CLUBS=$(docker compose exec -T fnclub-db psql -U postgres postgres -t -c "SELECT COUNT(*) FROM clubs_club;" 2>/dev/null | tr -d ' ' || echo "0")

echo "   Таблиц в БД: $(echo $TABLES | tr -d ' ')"
echo "   Пользователей: $USERS"
echo "   Клубов: $CLUBS"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Восстановление завершено успешно!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}📝 Страховочный бэкап сохранен: $SAFETY_BACKUP${NC}"
echo ""
