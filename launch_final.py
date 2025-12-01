#!/usr/bin/env python3
"""
🚀 Финальный запуск Django с исправленной конфигурацией

Этот скрипт запускает Django с правильными настройками и ALLOWED_HOSTS.
"""

import os
import sys
import subprocess
from pathlib import Path

# Добавляем путь к проекту
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def main():
    """🎯 Главная функция запуска"""

    print("🚀 Финальный запуск Django с исправленной конфигурацией...")
    print("=" * 60)

    # Устанавливаем правильные переменные окружения
    os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

    try:
        # Проверяем, что Django доступен
        import django
        print("✅ Django доступен")

        # Инициализируем Django
        django.setup()
        print("✅ Django инициализирован")

        # Проверяем настройки
        from django.conf import settings
        print(f"✅ Debug mode: {settings.DEBUG}")
        print(f"✅ Allowed hosts: {settings.ALLOWED_HOSTS}")

        # Проверяем подключение к базе данных
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ База данных доступна")

        # Проверяем AI агент
        from ai_consultant.agents.lightweight_agent import get_lightweight_agent
        agent = get_lightweight_agent()
        test_result = agent.process_message("Тест", "test")
        print("✅ AI агент работает")

        print("\n🚀 Запускаем Django development сервер...")
        print("📡 Сервер будет доступен на:")
        print("• http://127.0.0.1:8000/")
        print("• http://localhost:8000/")
        print("• http://fan-club.kz:8000/ (если nginx настроен)")

        print("\n🔧 Для использования с nginx:")
        print("1. Убедитесь, что nginx настроен на проксирование на 127.0.0.1:8000")
        print("2. Перезапустите nginx после изменений конфигурации")

        # Запускаем сервер
        subprocess.run([
            'python', 'manage.py', 'runserver',
            '0.0.0.0:8000',  # Слушаем все интерфейсы
            '--insecure',
            '--noreload'     # Отключаем auto-reload для стабильности
        ])

    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Попробуйте: source venv/bin/activate")
        return 1
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Запуск остановлен пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Ошибка: {e}")
        sys.exit(1)