#!/bin/bash

# 🔧 Quick Fix Script for SSL Certificate Permissions
# Быстрое исправление прав доступа к SSL сертификатам

echo "🔧 Исправление прав доступа к SSL сертификатам..."
echo "================================================================"

# Функция для сообщений
success_msg() {
    echo -e "✅ $1"
}

error_msg() {
    echo -e "❌ $1"
}

warning_msg() {
    echo -e "⚠️  $1"
}

info_msg() {
    echo -e "ℹ️  $1"
}

# Проверка наличия SSL сертификатов
cert_path="/etc/letsencrypt/live/fan-club.kz"
fullchain_cert="$cert_path/fullchain.pem"
privkey_cert="$cert_path/privkey.pem"

if [[ -f "$fullchain_cert" ]] && [[ -f "$privkey_cert" ]]; then
    success_msg "SSL сертификаты найдены"
    success_msg "Путь: $cert_path"

    echo ""
    echo "🔧 Исправление прав доступа..."

    # Исправление прав доступа
    echo "1. Установка прав 755 на директорию..."
    sudo chmod -R 755 "$cert_path"

    echo "2. Установка прав 644 на файлы сертификатов..."
    sudo chmod 644 "$fullchain_cert" "$privkey_cert"

    echo "3. Проверка прав..."
    ls -la "$cert_path/"

    # Проверка конфигурации nginx
    echo ""
    echo "📋 Проверка конфигурации nginx..."
    if nginx -t; then
        success_msg "Конфигурация nginx корректна"
        echo ""
        echo "🚀 Перезапуск nginx..."
        sudo systemctl restart nginx
        if systemctl is-active --quiet nginx; then
            success_msg "nginx успешно перезапущен"
            echo ""
            echo "🌐 Проверка доступности сайта..."
            if curl -s --connect-timeout 10 https://fan-club.kz > /dev/null; then
                success_msg "✅ Сайт доступен по HTTPS!"
                echo ""
                echo "🎉 ПРОБЛЕМА РЕШЕНА!"
                echo "Теперь сайт должен работать нормально по https://fan-club.kz"
            else
                warning_msg "Сайт пока недоступен, но nginx перезапущен"
                echo "Попробуйте проверить через несколько секунд"
            fi
        else
            error_msg "nginx не запустился после перезагрузки"
            echo "Проверьте статус: sudo systemctl status nginx"
        fi
    else
        error_msg "Ошибка в конфигурации nginx"
        nginx -t
    fi

else
    error_msg "SSL сертификаты не найдены"
    warning_msg "Запустите диагностику снова для настройки SSL с нуля"
fi

echo ""
echo "🏁 Готово!"