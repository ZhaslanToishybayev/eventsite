#!/usr/bin/env python3
"""
🎯 Простой запуск Django на порту 8002 для быстрой демонстрации
"""

import os
import sys
import subprocess
from pathlib import Path

# Добавляем путь к проекту
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def main():
    """🎯 Главная функция"""

    print("🚀 Запуск Django на порту 8002 для демонстрации...")
    print("=" * 60)

    # Устанавливаем переменные окружения
    os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

    try:
        # Импортируем Django
        import django
        django.setup()

        print("✅ Django инициализирован")

        # Проверяем AI агент
        from ai_consultant.agents.lightweight_agent import get_lightweight_agent
        agent = get_lightweight_agent()
        test_result = agent.process_message("Тест", "test")
        print("✅ AI агент работает")

        print("\n🚀 Запускаем Django на порту 8002...")
        print("🌐 Проверьте: http://127.0.0.1:8002/")
        print("🔧 Для nginx: нужно перенастроить на порт 8002")

        # Запускаем сервер на порту 8002
        subprocess.run([
            'python', 'manage.py', 'runserver',
            '127.0.0.1:8002',
            '--insecure',
            '--noreload'
        ])

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
        print("\n👋 Запуск остановлен")
        sys.exit(0)