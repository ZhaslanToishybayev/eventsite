#!/bin/bash

# 📊 UnitySphere Disk Check Script
# Проверка состояния диска после очистки

echo "📊 UnitySphere Disk Check Script"
echo "================================"
echo ""

# 1. Проверяем общий disk usage
echo "🔍 Общий disk usage:"
df -h | grep "/$" | awk '{print "   Используется: " $3 " из " $2 " (" $5 " заполнено)"}'
df -h | grep "/$" | awk '{print "   Свободно: " $4}'

echo ""

# 2. Проверяем /var
echo "📁 /var usage:"
du -sh /var 2>/dev/null | awk '{print "   /var: " $1}'

# 3. Проверяем /var/log
echo ""
echo "📄 /var/log usage:"
du -sh /var/log 2>/dev/null | awk '{print "   /var/log: " $1}'

# 4. Проверяем архивы
echo ""
echo "📦 Архивы:"
ls -lh /var/www/myapp/eventsite/archives/ 2>/dev/null | awk '{print "   " $5 " " $9}'

# 5. Топ-10 самых больших папок в /var/www/myapp/eventsite
echo ""
echo "🔝 Топ-10 по размеру в проекте:"
du -sh /var/www/myapp/eventsite/* 2>/dev/null | sort -hr | head -10

echo ""
echo "✅ Проверка завершена!"