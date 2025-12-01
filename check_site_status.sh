#!/bin/bash
# 🚀 Простое решение - Проверка и фикс сайта

echo "🔍 Проверяем текущее состояние сайта..."
echo "====================================="

# Проверяем что возвращает Django
echo "1. Проверяем ответ Django на порту 8001:"
curl -s http://127.0.0.1:8001/ | head -5

echo ""
echo "2. Проверяем URL-маршруты Django..."

# Проверяем основные URL-файлы
if [ -f "/var/www/myapp/eventsite/core/urls.py" ]; then
    echo "✅ core/urls.py существует"
    grep -n "urlpatterns" /var/www/myapp/eventsite/core/urls.py | head -3
else
    echo "❌ core/urls.py не найден"
fi

if [ -f "/var/www/myapp/eventsite/core/urls_ai_enhanced.py" ]; then
    echo "✅ core/urls_ai_enhanced.py существует"
    grep -n "urlpatterns" /var/www/myapp/eventsite/core/urls_ai_enhanced.py | head -3
else
    echo "❌ core/urls_ai_enhanced.py не найден"
fi

echo ""
echo "3. Проверяем settings.py настройки..."

# Проверяем основные настройки
if [ -f "/var/www/myapp/eventsite/core/settings.py" ]; then
    echo "✅ core/settings.py существует"
    grep -n "ROOT_URLCONF" /var/www/myapp/eventsite/core/settings.py
else
    echo "❌ core/settings.py не найден"
fi

echo ""
echo "4. Решение:"
echo "============"
echo ""
echo "Проблема: Django возвращает JSON API вместо HTML сайта"
echo ""
echo "Возможные причины:"
echo "• URL-маршруты настроены на API"
echo "• Отсутствует корневой маршрут '/'"
echo "• Templates не настроены"
echo ""
echo "Что делать:"
echo "1. Откройте https://fan-club.kz в браузере"
echo "2. Если видите JSON - это нормально для API-режима"
echo "3. Проверьте файлы URL-маршрутов в core/urls*.py"
echo "4. Убедитесь что есть маршрут '/' который возвращает HTML"
echo ""
echo "💡 Для быстрого решения:"
echo "• Проверьте templates/base.html"
echo "• Убедитесь что URL '/' ведет на view с рендерингом HTML"
echo "• Или используйте сайт как API (если это ваша цель)"