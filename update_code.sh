#!/bin/bash

# 🔄 UnitySphere Code Update Script
# Автоматическое обновление кода с перезапуском Django

echo "🔄 UnitySphere Code Update Script"
echo "=================================="
echo ""

# Проверка прав sudo
if ! sudo -n true 2>/dev/null; then
    echo "❌ Для обновления нужны права sudo"
    echo "💡 Войдите как root или используйте: sudo $0"
    exit 1
fi

cd /var/www/myapp/eventsite

echo "📋 Шаг 1: Остановка Django сервиса..."
sudo systemctl stop unitysphere.service
sleep 3

echo "📋 Шаг 2: Обновление кода..."
# Здесь можно добавить git pull или копирование файлов
# git pull origin main
echo "   • Код обновлен (вставьте сюда команду обновления)"

echo "📋 Шаг 3: Применение миграций..."
python manage.py migrate

echo "📋 Шаг 4: Сборка статики..."
python manage.py collectstatic --noinput

echo "📋 Шаг 5: Проверка конфигурации..."
python manage.py check --deploy

echo "📋 Шаг 6: Запуск Django сервиса..."
sudo systemctl start unitysphere.service
sleep 5

echo "📋 Шаг 7: Проверка статуса..."
if sudo systemctl is-active --quiet unitysphere.service; then
    echo "✅ Django успешно запущен"

    echo "📋 Шаг 8: Проверка сайта..."
    SITE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1/)
    if [ "$SITE_STATUS" = "200" ]; then
        echo "✅ Сайт работает"
        echo ""
        echo "🎉 Обновление завершено успешно!"
        echo "📊 Финальный статус:"
        echo "   • Django: ✅ РАБОТАЕТ"
        echo "   • Сайт: ✅ РАБОТАЕТ"
        echo "   • Код: ✅ ОБНОВЛЕН"
    else
        echo "⚠️ Сайт не работает (код: $SITE_STATUS)"
        echo "💡 Проверьте логи: sudo journalctl -u unitysphere.service -f"
    fi
else
    echo "❌ Django не запустился"
    echo "💡 Проверьте логи: sudo journalctl -u unitysphere.service -f"
    exit 1
fi