#!/bin/bash

# НАСТРОЙКА HTTPS ДЛЯ fan-club.kz
echo "🔒 НАСТРОЙКА HTTPS ДЛЯ fan-club.kz"
echo "====================================="

echo "1. Проверка наличия SSL сертификатов..."
if [ -f /etc/ssl/certs/fan-club.kz.crt ]; then
    echo "✅ SSL сертификат найден"
else
    echo "❌ SSL сертификат не найден, нужно получить"
fi

echo ""
echo "2. Предлагаю 2 варианта:"

echo ""
echo "🔴 Вариант 1: Let's Encrypt (рекомендуется)"
echo "Бесплатные SSL сертификаты, автоматическое обновление"
echo ""
echo "Команды для Let's Encrypt:"
echo "sudo apt update"
echo "sudo apt install certbot python3-certbot-nginx"
echo "sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz"
echo ""

echo "🔴 Вариант 2: Self-signed сертификат (временно)"
echo "Для тестирования, но браузеры будут показывать предупреждения"
echo ""
echo "Команды для self-signed:"
echo "sudo mkdir -p /etc/ssl/fan-club.kz"
echo "sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\"
echo "    -keyout /etc/ssl/fan-club.kz/private.key \\"
echo "    -out /etc/ssl/fan-club.kz/cert.pem \\"
echo "    -subj '/CN=fan-club.kz'"
echo ""

echo "🔴 Вариант 3: Отключить HTTPS (не рекомендуется)"
echo "Оставить как есть, но исправить CSRF_TRUSTED_ORIGINS"
echo ""

echo "3. После получения SSL сертификата нужно:"
echo "- Обновить конфигурацию Nginx для HTTPS"
echo "- Настроить редирект с HTTP на HTTPS"
echo "- Обновить CSRF_TRUSTED_ORIGINS"
echo "- Обновить ALLOWED_HOSTS"
echo ""

echo "4. Текущая проблема:"
echo "CSRF_TRUSTED_ORIGINS ожидает HTTPS, но сайт работает по HTTP"
echo ""
echo "5. Быстрое временное решение:"
echo "Изменить в settings.py:"
echo "CSRF_TRUSTED_ORIGINS = ['http://fan-club.kz', 'http://www.fan-club.kz']"
echo ""

echo "====================================="
echo "Выберите вариант и я помогу настроить"