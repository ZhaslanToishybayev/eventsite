#!/bin/bash

# 🎯 БЫСТРЫЙ ВОЗВРАТ К DAY 2 STABLE
# Простой скрипт для мгновенного восстановления стабильной версии

set -e

echo "🎯 БЫСТРЫЙ ВОЗВРАТ К DAY 2 STABLE"
echo "📅 $(date)"
echo ""

# Проверка наличия архива
ARCHIVE_DIR="/var/www/myapp/eventsite/archives"
LATEST_ARCHIVE=$(ls -t "$ARCHIVE_DIR"/unitysphere_day2_stable_*.tar.gz 2>/dev/null | head -1)

if [ -z "$LATEST_ARCHIVE" ]; then
    echo "❌ Ошибка: Архив Day 2 Stable not найден"
    echo "   Проверьте директорию: $ARCHIVE_DIR"
    exit 1
fi

echo "📦 Найден архив: $(basename "$LATEST_ARCHIVE")"
echo "   Путь: $LATEST_ARCHIVE"
echo ""

# Подтверждение действия
echo "⚠️  ВНИМАНИЕ: Это действие:"
echo "   1. Остановит все текущие процессы Django"
echo "   2. Создаст резервную копию текущей системы"
echo "   3. Восстановит систему из архива Day 2 Stable"
echo "   4. Запустит тестирование системы"
echo ""
read -p "Продолжить? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Отменено пользователем"
    exit 1
fi

# Остановка текущих процессов
echo "🛑 Остановка текущих процессов..."
pkill -f "python.*manage.py" || true
sleep 2

# Резервное копирование текущей системы
if [ -d "/var/www/myapp/eventsite" ]; then
    echo "📦 Создание резервной копии текущей системы..."
    BACKUP_DIR="/var/www/myapp/eventsite_backup_$(date +%Y%m%d_%H%M%S)"
    mv /var/www/myapp/eventsite "$BACKUP_DIR"
    echo "   Резервная копия: $BACKUP_DIR"
fi

# Создание временной директории
TEMP_DIR="/tmp/unitysphere_quick_restore_$$"
mkdir -p "$TEMP_DIR"

# Распаковка архива
echo "📦 Распаковка архива..."
cd "$TEMP_DIR"
tar -xzf "$LATEST_ARCHIVE"

if [ $? -eq 0 ]; then
    echo "✅ Архив распакован успешно"
else
    echo "❌ Ошибка при распаковке архива"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Восстановление системы
echo "🔄 Восстановление системы..."
mv "$TEMP_DIR/eventsite" /var/www/myapp/

# Установка прав доступа
echo "🔐 Установка прав доступа..."
chown -R admin:admin /var/www/myapp/eventsite
chmod -R 755 /var/www/myapp/eventsite
chmod +x /var/www/myapp/eventsite/manage.py

# Удаление временных файлов
echo "🧹 Очистка временных файлов..."
rm -rf "$TEMP_DIR"

# Проверка структуры
echo "🔍 Проверка структуры системы..."
if [ -f "/var/www/myapp/eventsite/manage.py" ] && [ -d "/var/www/myapp/eventsite/core" ]; then
    echo "✅ Структура системы корректна"
else
    echo "❌ Ошибка: Структура системы повреждена"
    exit 1
fi

# Тестирование системы
echo "🧪 Тестирование системы..."

# Активация виртуального окружения
cd /var/www/myapp/eventsite
source venv/bin/activate

# Запуск Django check
echo "   Проверка Django конфигурации..."
python3 manage.py check > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Django конфигурация корректна"
else
    echo "   ⚠️  Django конфигурация имеет предупреждения"
fi

# Запуск тестового сервера
echo "   Запуск тестового сервера..."
python3 manage.py runserver 0.0.0.0:8003 > /tmp/quick_restore_test.log 2>&1 &
TEST_PID=$!
sleep 5

# Проверка основных эндпоинтов
echo "   Тестирование основных функций..."

# Главная страница
if curl -s http://127.0.0.1:8003/ > /dev/null; then
    echo "   ✅ Главная страница доступна"
else
    echo "   ❌ Главная страница недоступна"
fi

# AI Health
if curl -s http://127.0.0.1:8003/api/ai/enhanced/enhanced/health/ > /dev/null; then
    echo "   ✅ AI Health endpoint доступен"
else
    echo "   ❌ AI Health endpoint недоступен"
fi

# Остановка тестового сервера
kill $TEST_PID 2>/dev/null || true
sleep 2

echo ""
echo "🎯 БЫСТРЫЙ ВОЗВРАТ К DAY 2 STABLE ЗАВЕРШЕН!"
echo ""
echo "📍 Система готова к использованию:"
echo "   🔗 Главная: http://127.0.0.1:8003/"
echo "   🔗 AI Health: http://127.0.0.1:8003/api/ai/enhanced/enhanced/health/"
echo "   🔗 Test Widget: http://127.0.0.1:8003/test_enhanced_widget/"
echo ""
echo "⚠️  Для production запуска:"
echo "   cd /var/www/myapp/eventsite"
echo "   source venv/bin/activate"
echo "   gunicorn core.wsgi:application -b 127.0.0.1:8003 -w 4 -t 60"
echo ""
echo "💾 Текущая система сохранена в: $BACKUP_DIR"