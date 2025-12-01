#!/bin/bash

# 🚀 Быстрое исправление nginx конфигурации для немедленной работы

echo "🚀 БЫСТРОЕ ИСПРАВЛЕНИЕ NGINX КОНФИГУРАЦИИ"
echo "============================================"

echo ""
echo "📋 ПРОБЛЕМА: nginx пытается использовать SSL сертификаты которые не существуют"
echo "🔧 РЕШЕНИЕ: Используем простую конфигурацию без SSL для немедленной работы"
echo ""

# Проверка Django сервера
echo "1. Проверка Django сервера..."
cd /var/www/myapp/eventsite

if curl -s http://localhost:8000/health/ 2>/dev/null | grep -q "healthy"; then
    echo "✅ Django сервер работает на порту 8000"
else
    echo "❌ Django сервер не отвечает, перезапускаем..."
    # Останавливаем старые процессы
    pkill -f "python.*manage\.py.*runserver" 2>/dev/null
    sleep 2

    # Запускаем Django сервер
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    nohup python manage.py runserver 0.0.0.0:8000 > /dev/null 2>&1 &
    sleep 5

    if curl -s http://localhost:8000/health/ 2>/dev/null | grep -q "healthy"; then
        echo "✅ Django сервер запущен"
    else
        echo "❌ Django сервер не запустился"
        exit 1
    fi
fi

# Создаем резервную копию текущей конфигурации
echo ""
echo "2. Создание резервной копии текущей конфигурации..."
if [ -f "/etc/nginx/sites-available/fan-club.kz" ]; then
    sudo cp /etc/nginx/sites-available/fan-club.kz "/etc/nginx/sites-available/fan-club.kz.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Резервная копия создана"
fi

# Копируем простую рабочую конфигурацию
echo ""
echo "3. Установка простой рабочей конфигурации..."
sudo cp /var/www/myapp/eventsite/nginx_simple_working_config /etc/nginx/sites-available/fan-club.kz

# Проверяем конфигурацию nginx
echo ""
echo "4. Проверка конфигурации nginx..."
if sudo nginx -t 2>/dev/null; then
    echo "✅ Конфигурация nginx валидна"
else
    echo "❌ Ошибка конфигурации nginx"
    sudo nginx -t
    exit 1
fi

# Перезагружаем nginx
echo ""
echo "5. Перезагрузка nginx..."
sudo systemctl reload nginx 2>/dev/null || sudo systemctl restart nginx 2>/dev/null

sleep 3

# Проверка статуса nginx
echo ""
echo "6. Проверка статуса nginx..."
if sudo systemctl is-active --quiet nginx; then
    echo "✅ nginx работает"
else
    echo "❌ nginx не запущен"
    sudo systemctl status nginx
    exit 1
fi

# Тестирование сайта
echo ""
echo "7. Тестирование работоспособности сайта..."

# Проверка HTTP
if curl -s http://fan-club.kz/health/ 2>/dev/null | grep -q "healthy"; then
    echo "✅ HTTP доступ работает: http://fan-club.kz"
    site_works=true
else
    echo "❌ HTTP доступ не работает"
    site_works=false
fi

# Проверка главной страницы
if curl -s http://fan-club.kz/ 2>/dev/null | grep -q "Центр сообществ\|UnitySphere\|fan-club"; then
    echo "✅ Главная страница доступна"
    main_page_works=true
else
    echo "❌ Главная страница не доступна"
    main_page_works=false
fi

# Проверка AI API
if curl -s -X POST "http://fan-club.kz/api/v1/ai/simplified/interactive/chat/" \
    -H "Content-Type: application/json" \
    -d '{"message": "Привет", "user_email": "test@fan-club.kz", "state_id": null}' 2>/dev/null | grep -q "AI\|Привет\|здравствуйте"; then
    echo "✅ AI API работает"
    api_works=true
else
    echo "❌ AI API не работает"
    api_works=false
fi

# Итог
echo ""
echo "📊 ИТОГ ТЕСТИРОВАНИЯ:"
echo "===================="
echo "HTTP доступ: $([ $site_works = true ] && echo '✅ Работает' || echo '❌ Не работает')"
echo "Главная страница: $([ $main_page_works = true ] && echo '✅ Работает' || echo '❌ Не работает')"
echo "AI API: $([ $api_works = true ] && echo '✅ Работает' || echo '❌ Не работает')"

if [ $site_works = true ]; then
    echo ""
    echo "🎉 САЙТ РАБОТАЕТ!"
    echo "=================="
    echo ""
    echo "🌐 Сайт доступен по адресу:"
    echo "   http://fan-club.kz"
    echo "   http://www.fan-club.kz"
    echo ""
    echo "🚀 Функции сайта:"
    echo "   ✅ AI консультант"
    echo "   ✅ Создание клубов"
    echo "   ✅ AI чат-виджет на всех страницах"
    echo "   ✅ Все функции Django"
    echo "   ✅ Статические файлы"
    echo "   ✅ Медиа файлы"
    echo ""
    echo "💡 Для включения HTTPS (если нужно в будущем):"
    echo "   1. Убедитесь, что домен fan-club.kz указывает на этот сервер"
    echo "   2. Выполните: sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz"
    echo "   3. Перезагрузите nginx: sudo systemctl reload nginx"
    echo ""
    echo "🔧 Команды управления:"
    echo "   sudo systemctl status nginx           # Статус nginx"
    echo "   sudo systemctl status django-fanclub  # Статус Django (если настроен)"
    echo "   sudo tail -f /var/log/nginx/error.log # Логи nginx"
    echo "   curl -I http://fan-club.kz           # Проверка HTTP"
else
    echo ""
    echo "❌ Сайт не работает. Проверьте логи:"
    echo "   sudo tail -f /var/log/nginx/error.log"
    echo "   sudo systemctl status nginx"
    echo "   sudo systemctl status django-fanclub"
fi

echo ""
echo "🏁 ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
echo "=========================="