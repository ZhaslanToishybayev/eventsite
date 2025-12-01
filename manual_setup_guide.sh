#!/bin/bash

# 🚀 Ручная настройка nginx для fan-club.kz
echo "🚀 РУЧНАЯ НАСТРОЙКА NGINX И SSL"
echo "=================================="

echo ""
echo "📋 Выполните следующие команды вручную:"
echo "========================================"
echo ""

echo "1. Копируем nginx конфигурацию:"
echo "sudo cp /var/www/myapp/eventsite/nginx_complete_config /etc/nginx/sites-available/fan-club.kz"
echo ""

echo "2. Создаем символическую ссылку для активации сайта:"
echo "sudo ln -sf /etc/nginx/sites-available/fan-club.kz /etc/nginx/sites-enabled/"
echo ""

echo "3. Проверяем конфигурацию nginx:"
echo "sudo nginx -t"
echo ""

echo "4. Перезагружаем nginx:"
echo "sudo systemctl reload nginx"
echo ""

echo "5. Проверяем статус nginx:"
echo "sudo systemctl status nginx"
echo ""

echo "6. Если домен fan-club.kz указывает на этот сервер, получаем SSL сертификат:"
echo "sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz --agree-tos --email admin@fan-club.kz"
echo ""

echo "7. Проверяем SSL сертификат:"
echo "sudo certbot certificates"
echo ""

echo "8. Проверяем работоспособность сайта:"
echo "curl -I https://fan-club.kz"
echo ""

echo "🔧 АЛЬТЕРНАТИВНОЕ РЕШЕНИЕ (если проблемы с SSL):"
echo "================================================"
echo ""

echo "1. Используем простую конфигурацию без SSL:"
echo "sudo cp /var/www/myapp/eventsite/nginx_simple_config /etc/nginx/sites-available/fan-club.kz"
echo ""

echo "2. Перезагружаем nginx:"
echo "sudo systemctl reload nginx"
echo ""

echo "3. Сайт будет доступен по HTTP:"
echo "http://fan-club.kz"
echo ""

echo "📝 ПРОВЕРКА ПОСЛЕ НАСТРОЙКИ:"
echo "=============================="
echo ""

echo "Проверьте, что сайт работает:"
echo "curl -I http://fan-club.kz"
echo "curl -I https://fan-club.kz (если SSL настроен)"
echo ""

echo "Проверьте AI API:"
echo "curl -X POST 'http://fan-club.kz/api/v1/ai/simplified/interactive/chat/' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"Привет\", \"user_email\": \"test@fan-club.kz\", \"state_id\": null}'"
echo ""

echo "🎯 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ:"
echo "==========================="
echo ""
echo "После настройки сайт будет доступен:"
echo "✅ https://fan-club.kz (с SSL)"
echo "✅ http://fan-club.kz (без SSL, если не настроен)"
echo "✅ AI консультант будет работать"
echo "✅ AI чат-виджет будет работать на всех страницах"
echo "✅ Все функции Django будут доступны"
echo ""

echo "💡 Если что-то не работает, проверьте логи:"
echo "sudo tail -f /var/log/nginx/error.log"
echo "sudo journalctl -u django-fanclub -f"
echo ""

echo "🏁 СКОПИРУЙТЕ И ВЫПОЛНИТЕ КОМАНДЫ ВЫШЕ"
echo "========================================"