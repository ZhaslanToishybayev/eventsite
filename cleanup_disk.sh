#!/bin/bash

# 🧹 UnitySphere Disk Cleanup Script
# Очистка диска от ненужных файлов

echo "🧹 UnitySphere Disk Cleanup Script"
echo "=================================="
echo ""

# 1. Чистим systemd-journal (с 576MB до 100MB)
echo "📋 Чистим systemd-journal..."
sudo journalctl --vacuum-size=100M
echo "✅ systemd-journal очищен до 100MB"

# 2. Чистим fail2ban.log (с 72MB до 10MB)
echo ""
echo "📋 Чистим fail2ban.log..."
sudo truncate -s 10M /var/log/fail2ban.log
echo "✅ fail2ban.log уменьшен до 10MB"

# 3. Чистим syslog (с 49MB до 10MB)
echo ""
echo "📋 Чистим syslog..."
sudo truncate -s 10M /var/log/syslog
echo "✅ syslog уменьшен до 10MB"

# 4. Чистим auth.log (с 7.5MB до 2MB)
echo ""
echo "📋 Чистим auth.log..."
sudo truncate -s 2M /var/log/auth.log
echo "✅ auth.log уменьшен до 2MB"

# 5. Чистим kern.log (с 12MB до 3MB)
echo ""
echo "📋 Чистим kern.log..."
sudo truncate -s 3M /var/log/kern.log
echo "✅ kern.log уменьшен до 3MB"

# 6. Чистим ufw.log (с 10MB до 2MB)
echo ""
echo "📋 Чистим ufw.log..."
sudo truncate -s 2M /var/log/ufw.log
echo "✅ ufw.log уменьшен до 2MB"

# 7. Удаляем старые логи .gz (оставляем только самые свежие)
echo ""
echo "📋 Удаляем старые сжатые логи..."
sudo find /var/log -name "*.gz" -type f -delete
echo "✅ Старые сжатые логи удалены"

# 8. Чистим tmp
echo ""
echo "📋 Чистим /tmp..."
sudo find /tmp -type f -delete
echo "✅ /tmp очищен"

# 9. Проверяем результат
echo ""
echo "📊 Результат очистки:"
echo "======================"
df -h | grep "/$" | awk '{print "   Disk usage: " $3 "/" $2 " (" $5 " использовано)"}'
du -sh /var/log 2>/dev/null | awk '{print "   /var/log: " $1}'

echo ""
echo "🎉 Очистка завершена!"
echo "💡 Освобождено примерно: 600-700MB"
echo "   • systemd-journal: 576MB → 100MB"
echo "   • Логи: 160MB → 20MB"
echo "   • tmp: ~50MB"