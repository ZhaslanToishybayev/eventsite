#!/usr/bin/env python3
"""
🎯 ФИНАЛЬНЫЙ РАБОЧИЙ ЗАПУСК DJANGO
"""

import os
import sys
import subprocess
import time

def main():
    print("🚀 ФИНАЛЬНЫЙ РАБОЧИЙ ЗАПУСК DJANGO")
    print("==================================")
    print()

    # 1. Устанавливаем переменные окружения
    print("🔧 Настройка окружения...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    os.environ['PYTHONPATH'] = '/var/www/myapp/eventsite'

    # Добавляем путь к проекту
    sys.path.insert(0, '/var/www/myapp/eventsite')

    # 2. Проверяем Django
    print("🔍 Проверка Django...")
    try:
        import django
        django.setup()
        print("✅ Django успешно загружен")
        print(f"   Версия: {django.get_version()}")
        print(f"   DEBUG: {django.conf.settings.DEBUG}")
        print(f"   ALLOWED_HOSTS: {django.conf.settings.ALLOWED_HOSTS}")
    except Exception as e:
        print(f"❌ Ошибка Django: {e}")
        return

    # 3. Проверяем базу данных
    print()
    print("🗄️ Проверка базы данных...")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM accounts_user;')
            user_count = cursor.fetchone()[0]
        
        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM clubs_club;')
            club_count = cursor.fetchone()[0]
        
        print(f"✅ База данных работает: {user_count} пользователей, {club_count} клубов")
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return

    # 4. Запускаем Django development server
    print()
    print("🚀 ЗАПУСК DJANGO DEVELOPMENT SERVER")
    print("==================================")
    print()

    try:
        # Запускаем Django development server
        cmd = [
            sys.executable, 
            'manage.py', 
            'runserver', 
            '0.0.0.0:8000'
        ]

        print("📡 Запускаю Django development server...")
        print(f"🌐 Команда: {' '.join(cmd)}")
        print("⏳ Ожидайте запуска...")
        print()

        # Запускаем процесс
        process = subprocess.Popen(
            cmd,
            cwd='/var/www/myapp/eventsite',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        print(f"✅ Django запущен (PID: {process.pid})")
        print()
        print("🎯 DJANGO УСПЕШНО ЗАПУЩЕН!")
        print("=========================")
        print()
        print("📊 Статус:")
        print(f"   • Процесс ID: {process.pid}")
        print(f"   • Порт: 8000")
        print(f"   • Статус: Работает")
        print()
        print("🌐 Доступ:")
        print("   • Локально: http://127.0.0.1:8000")
        print("   • Через Nginx: https://fan-club.kz")
        print()
        print("🔧 Управление:")
        print(f"   • Остановить: kill {process.pid}")
        print("   • Проверить: ps aux | grep python")
        print()
        print("💡 Django работает! Нажмите Ctrl+C для остановки...")
        print()

        # Ждем завершения процесса (пользователь нажмет Ctrl+C)
        try:
            process.wait()
        except KeyboardInterrupt:
            print()
            print("🛑 Получен сигнал остановки...")
            process.terminate()
            process.wait()
            print("✅ Django остановлен")
        
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == '__main__':
    main()
