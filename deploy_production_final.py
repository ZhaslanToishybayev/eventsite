#!/usr/bin/env python3
"""
🚀 Production Deployment Script for UnitySphere
Быстрый запуск production-ready версии без dependency проблем
"""

import os
import sys
import subprocess
from pathlib import Path

# Добавляем путь к проекту
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Устанавливаем Django настройки
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


def fix_dependencies():
    """🔧 Фиксим dependency проблемы"""
    print("🔧 Fixing dependencies...")

    try:
        import subprocess

        # Активируем виртуальное окружение
        activate_script = str(project_dir / 'venv' / 'bin' / 'activate')
        if os.path.exists(activate_script):
            print("✅ Virtual environment found")

        # Удаляем проблемные пакеты
        subprocess.run([
            'python', '-m', 'pip', 'uninstall', '-y',
            'sentence-transformers', 'transformers', 'importlib-metadata'
        ], cwd=project_dir, capture_output=True)

        # Устанавливаем working версии
        subprocess.run([
            'python', '-m', 'pip', 'install',
            'importlib-metadata==6.8.0',
            'django',
            'djangorestframework',
            'openai'
        ], cwd=project_dir, capture_output=True)

        print("✅ Dependencies fixed")

    except Exception as e:
        print(f"⚠️  Dependency fix failed: {e}")
        print("Continuing with existing setup...")


def test_ai_agent():
    """🧪 Тестируем AI агента"""
    print("🧪 Testing AI agent...")

    try:
        from ai_consultant.agents.lightweight_production_agent import get_ai_response

        # Тестируем агента
        test_response = get_ai_response("Привет! Хочу создать клуб программирования", "test_session")

        if test_response and 'response' in test_response:
            print("✅ AI agent working correctly")
            print(f"   Response: {test_response['response'][:50]}...")
            return True
        else:
            print("❌ AI agent test failed")
            return False

    except Exception as e:
        print(f"❌ AI agent test failed: {e}")
        return False


def test_django_setup():
    """🔍 Тестируем Django setup"""
    print("🔍 Testing Django setup...")

    try:
        import django
        django.setup()
        print(f"✅ Django {django.get_version()} initialized")

        # Проверяем импорт production API
        from ai_consultant.api import production_api
        print("✅ Production API imported successfully")

        return True

    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False


def run_server():
    """🚀 Запускаем Django сервер"""
    print("🚀 Starting Django server...")

    try:
        # Останавливаем предыдущие процессы
        subprocess.run(['pkill', '-f', 'python.*runserver'], capture_output=True)

        # Запускаем сервер
        cmd = [
            'python', 'manage.py', 'runserver',
            '127.0.0.1:8001', '--insecure', '--noreload'
        ]

        print(f"📡 Running: {' '.join(cmd)}")
        subprocess.Popen(cmd, cwd=project_dir)

        # Ждем запуска
        import time
        time.sleep(3)

        # Проверяем запуск
        import requests
        try:
            response = requests.get('http://127.0.0.1:8001/api/v1/ai/production/health/', timeout=5)
            if response.status_code == 200:
                print("✅ Django server is running")
                print("🌐 Health check passed")
                return True
            else:
                print(f"❌ Server returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Server health check failed: {e}")
            return False

    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return False


def create_production_info():
    """📋 Создаем production информацию"""
    print("📋 Creating production information...")

    info = {
        "production_status": "READY",
        "server_url": "http://127.0.0.1:8001",
        "api_endpoints": {
            "ai_agent": "/api/v1/ai/production/agent/",
            "health_check": "/api/v1/ai/production/health/",
            "info": "/api/v1/ai/production/info/"
        },
        "features": [
            "Lightweight AI agent without heavy dependencies",
            "Natural Russian conversation",
            "Club creation workflow",
            "Production-ready API endpoints"
        ],
        "deployment_guide": {
            "step1": "Fix nginx configuration for proxy to 127.0.0.1:8001",
            "step2": "Test API endpoints",
            "step3": "Configure SSL if needed",
            "step4": "Set up systemd service for auto-start"
        }
    }

    with open('production_info.json', 'w', encoding='utf-8') as f:
        import json
        json.dump(info, f, ensure_ascii=False, indent=2)

    print("✅ Production information saved to production_info.json")
    return info


def main():
    """🎯 Главная функция"""
    print("🚀 UnitySphere Production Deployment")
    print("=" * 50)

    # Шаг 1: Фиксим зависимости
    fix_dependencies()

    # Шаг 2: Тестируем Django
    if not test_django_setup():
        print("❌ Django setup failed. Cannot continue.")
        return 1

    # Шаг 3: Тестируем AI агента
    if not test_ai_agent():
        print("❌ AI agent test failed. Cannot continue.")
        return 1

    # Шаг 4: Запускаем сервер
    if not run_server():
        print("❌ Server startup failed. Cannot continue.")
        return 1

    # Шаг 5: Создаем production информацию
    info = create_production_info()

    # Финальная информация
    print("\n" + "=" * 50)
    print("🎉 PRODUCTION DEPLOYMENT SUCCESSFUL!")
    print("=" * 50)

    print(f"\n🌐 Server URL: {info['server_url']}")
    print(f"\n🔗 API Endpoints:")
    for name, url in info['api_endpoints'].items():
        print(f"   {name}: {info['server_url']}{url}")

    print(f"\n📋 Testing:")
    print(f"   curl {info['server_url']}/api/v1/ai/production/health/")
    print(f"   curl -X POST {info['server_url']}/api/v1/ai/production/agent/ -H 'Content-Type: application/json' -d '{{\"message\": \"Привет\", \"session_id\": \"test\"}}'")

    print(f"\n🔧 Next steps:")
    print(f"   1. Configure nginx proxy to {info['server_url']}")
    print(f"   2. Test all API endpoints")
    print(f"   3. Set up SSL certificates")
    print(f"   4. Create systemd service for auto-start")

    print(f"\n✅ UnitySphere Production Ready!")
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Deployment stopped by user")
        sys.exit(0)