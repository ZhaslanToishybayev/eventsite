#!/usr/bin/env python3
"""
🎯 Быстрый запуск Django на порту 8001 для nginx

Простой запуск с минимальными настройками.
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

    print("🚀 Быстрый запуск Django на порту 8001...")
    print("=" * 50)

    # Устанавливаем переменные окружения
    os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
    os.environ['ALLOWED_HOSTS'] = 'fan-club.kz,www.fan-club.kz,127.0.0.1,localhost'

    try:
        # Импортируем Django
        import django
        django.setup()

        print("✅ Django инициализирован")
        print("✅ ALLOWED_HOSTS: ['fan-club.kz', 'www.fan-club.kz', '127.0.0.1', 'localhost']")

        # Проверяем AI агент
        from ai_consultant.agents.lightweight_agent import get_lightweight_agent
        agent = get_lightweight_agent()
        test_result = agent.process_message("Тест", "test")
        print("✅ AI агент работает")

        print("\n🚀 Запускаем Django на порту 8001...")
        print("📡 nginx теперь должен работать!")
        print("🌐 Проверьте: curl http://127.0.0.1:8001/")

        # Запускаем сервер
        subprocess.run([
            'python', 'manage.py', 'runserver',
            '127.0.0.1:8001',
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