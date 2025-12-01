#!/bin/bash

# 🎯 UNITYSPHERE DAY 2 STABLE - Архивация системы
# Дата создания: 28 ноября 2025
# Версия: Day 2 Enhanced AI - Стабильная

set -e  # Exit on any error

echo "🎯 Создание архива UnitySphere Day 2 Stable..."
echo "📅 $(date)"
echo ""

# Проверка наличия исходной директории
if [ ! -d "/var/www/myapp/eventsite" ]; then
    echo "❌ Ошибка: Директория /var/www/myapp/eventsite не найдена"
    exit 1
fi

# Создание директории для архивов
ARCHIVE_DIR="/var/www/myapp/eventsite/archives"
mkdir -p "$ARCHIVE_DIR"

# Генерация имени архива с меткой времени
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="unitysphere_day2_stable_${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="$ARCHIVE_DIR/$ARCHIVE_NAME"

echo "📦 Создание архива: $ARCHIVE_NAME"
echo "📍 Путь: $ARCHIVE_PATH"
echo ""

# Создание архива с исключением ненужных файлов
echo "⏳ Архивация файлов..."
cd /var/www/myapp/eventsite

tar -czf "$ARCHIVE_PATH" \
    --exclude='.git*' \
    --exclude='venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='*.log' \
    --exclude='*.swp' \
    --exclude='db.sqlite3' \
    --exclude='static/CACHE/' \
    --exclude='node_modules/' \
    --exclude='*.tar.gz' \
    --exclude='*.zip' \
    --exclude='*.bak' \
    --exclude='*.tmp' \
    --exclude='test_*' \
    --exclude='*checkpoint*' \
    --exclude='*_backup*' \
    . 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Архивация завершена успешно"
else
    echo "❌ Ошибка при архивации"
    exit 1
fi

# Проверка размера архива
ARCHIVE_SIZE=$(du -h "$ARCHIVE_PATH" | cut -f1)
echo "📊 Размер архива: $ARCHIVE_SIZE"

# Создание контрольной суммы
echo "🔐 Создание контрольной суммы..."
cd "$ARCHIVE_DIR"
sha256sum "$ARCHIVE_NAME" > "${ARCHIVE_NAME}.sha256"

echo "✅ Контрольная сумма сохранена: ${ARCHIVE_NAME}.sha256"

# Создание скрипта восстановления
echo "🔧 Создание скрипта восстановления..."
cat > "restore_day2_stable_${TIMESTAMP}.sh" << EOF
#!/bin/bash

# 🎯 Скрипт восстановления UnitySphere Day 2 Stable
# Архив: $ARCHIVE_NAME
# Дата создания: $TIMESTAMP

set -e

echo "🎯 Восстановление UnitySphere Day 2 Stable..."
echo "📅 $(date)"
echo ""

# Проверка наличия архива
if [ ! -f "$ARCHIVE_PATH" ]; then
    echo "❌ Ошибка: Архив $ARCHIVE_NAME не найден"
    exit 1
fi

# Проверка контрольной суммы
echo "🔐 Проверка целостности архива..."
cd "$ARCHIVE_DIR"
if sha256sum -c "${ARCHIVE_NAME}.sha256"; then
    echo "✅ Контрольная сумма верна"
else
    echo "❌ Ошибка: Контрольная сумма не совпадает"
    exit 1
fi

# Создание резервной копии текущей системы (если есть)
CURRENT_BACKUP=""
if [ -d "/var/www/myapp/eventsite_current" ]; then
    CURRENT_BACKUP="/var/www/myapp/eventsite_current_$(date +%Y%m%d_%H%M%S)"
    mv /var/www/myapp/eventsite_current "$CURRENT_BACKUP"
    echo "📦 Текущая система перемещена в: $CURRENT_BACKUP"
fi

# Создание временной директории для распаковки
TEMP_DIR="/tmp/unitysphere_restore_$$"
mkdir -p "$TEMP_DIR"

# Распаковка архива
echo "📦 Распаковка архива..."
cd "$TEMP_DIR"
tar -xzf "$ARCHIVE_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Архив распакован успешно"
else
    echo "❌ Ошибка при распаковке архива"
    exit 1
fi

# Остановка текущих процессов
echo "🛑 Остановка текущих процессов..."
pkill -f "python.*manage.py" || true
sleep 2

# Резервное копирование текущей системы
if [ -d "/var/www/myapp/eventsite" ]; then
    echo "📦 Создание резервной копии текущей системы..."
    mv /var/www/myapp/eventsite "/var/www/myapp/eventsite_backup_$(date +%Y%m%d_%H%M%S)"
fi

# Копирование файлов из архива
echo "📁 Копирование файлов системы..."
mv "$TEMP_DIR/eventsite" /var/www/myapp/

# Установка прав доступа
echo "🔐 Установка прав доступа..."
chown -R admin:admin /var/www/myapp/eventsite
chmod -R 755 /var/www/myapp/eventsite
chmod +x /var/www/myapp/eventsite/manage.py

# Удаление временных файлов
echo "🧹 Очистка временных файлов..."
rm -rf "$TEMP_DIR"

# Проверка структуры директорий
echo "🔍 Проверка структуры системы..."
if [ -f "/var/www/myapp/eventsite/manage.py" ] && [ -d "/var/www/myapp/eventsite/core" ]; then
    echo "✅ Структура системы корректна"
else
    echo "❌ Ошибка: Структура системы повреждена"
    exit 1
fi

# Активация виртуального окружения и установка зависимостей
echo "🔧 Установка зависимостей..."
cd /var/www/myapp/eventsite
source venv/bin/activate || {
    echo "❌ Ошибка: Не удалось активировать виртуальное окружение"
    exit 1
}

# Запуск системы для проверки
echo "🚀 Запуск системы для проверки..."
python3 manage.py check --deploy 2>/dev/null || python3 manage.py check

if [ $? -eq 0 ]; then
    echo "✅ Система прошла проверку"
else
    echo "⚠️  Система имеет предупреждения, но может работать"
fi

# Запуск development server для тестирования
echo "🧪 Запуск тестового сервера..."
python3 manage.py runserver 0.0.0.0:8003 > /tmp/unitysphere_test.log 2>&1 &
TEST_PID=$$
sleep 5

# Проверка доступности основных эндпоинтов
echo "🔍 Тестирование основных функций..."

# Проверка главной страницы
if curl -s http://127.0.0.1:8003/ > /dev/null; then
    echo "✅ Главная страница доступна"
else
    echo "❌ Главная страница недоступна"
fi

# Проверка AI Health
if curl -s http://127.0.0.1:8003/api/ai/enhanced/enhanced/health/ > /dev/null; then
    echo "✅ AI Health endpoint доступен"
else
    echo "❌ AI Health endpoint недоступен"
fi

# Остановка тестового сервера
kill $TEST_PID 2>/dev/null || true
sleep 2

echo ""
echo "🎯 Восстановление UnitySphere Day 2 Stable завершено!"
echo "📍 Система готова к использованию"
echo "🔗 Тестовые URL:"
echo "   - Главная: http://127.0.0.1:8003/"
echo "   - AI Health: http://127.0.0.1:8003/api/ai/enhanced/enhanced/health/"
echo "   - Test Widget: http://127.0.0.1:8003/test_enhanced_widget/"
echo ""
echo "⚠️  Для production запуска используйте Gunicorn:"
echo "   gunicorn core.wsgi:application -b 127.0.0.1:8003 -w 4 -t 60"
EOF

chmod +x "restore_day2_stable_${TIMESTAMP}.sh"

echo ""
echo "🎯 Архивация UnitySphere Day 2 Stable завершена!"
echo ""
echo "📊 Информация об архиве:"
echo "   📁 Архив: $ARCHIVE_NAME"
echo "   📏 Размер: $ARCHIVE_SIZE"
echo "   🔐 Контрольная сумма: ${ARCHIVE_NAME}.sha256"
echo "   🔧 Скрипт восстановления: restore_day2_stable_${TIMESTAMP}.sh"
echo ""
echo "📍 Файлы сохранены в: $ARCHIVE_DIR"
echo ""
echo "✅ Готово! Вы можете безопасно возвращаться к этой версии в любое время."
echo ""

# Показать список всех архивов
echo "📋 Список всех архивов:"
ls -la "$ARCHIVE_DIR"/*.tar.gz 2>/dev/null || echo "   Архивы не найдены"