#!/bin/bash

echo "🔧 Исправляем конфигурацию Nginx..."

# Останавливаем Nginx
echo "🛑 Останавливаем Nginx..."
systemctl stop nginx

# Отключаем default сайт
echo "🚫 Отключаем default сайт..."
rm -f /etc/nginx/sites-enabled/default

# Делаем наш сайт default_server
echo "🎯 Настраиваем fan-club.kz как основной сайт..."
cp /etc/nginx/sites-available/fan-club.kz /tmp/fan-club.kz.backup
sed 's/server_name fan-club.kz www.fan-club.kz;/server_name fan-club.kz www.fan-club.kz;\n    listen 80 default_server;\n    listen [::]:80 default_server;/' /etc/nginx/sites-available/fan-club.kz > /tmp/fan-club.kz.new
cp /tmp/fan-club.kz.new /etc/nginx/sites-available/fan-club.kz

# Перезагружаем конфигурацию
echo "🔄 Перезагружаем конфигурацию Nginx..."
systemctl start nginx
systemctl reload nginx

# Проверяем статус
echo "✅ Проверяем статус Nginx..."
systemctl status nginx --no-pager -l

echo "🎉 Конфигурация Nginx исправлена!"
echo "🌐 Проверьте сайт по адресу: http://fan-club.kz"