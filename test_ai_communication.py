#!/usr/bin/env python3
"""
Тестирование AI агента и Django API коммуникации
"""

import requests
import json
import time
import sys

def test_ai_agent():
    """Тестируем AI агента напрямую"""
    print("🔍 Тестирование AI агента напрямую...")

    try:
        # Проверяем health endpoint
        health_response = requests.get('http://127.0.0.1:8001/health/', timeout=5)
        if health_response.status_code == 200:
            print("✅ AI агент доступен на порту 8001")
            print(f"   Health check: {health_response.json()}")
        else:
            print(f"❌ AI агент недоступен, статус: {health_response.status_code}")
            return False

        # Тестируем API агента
        test_data = {
            "message": "Test message for AI agent",
            "session_id": "test_session_123"
        }

        api_response = requests.post(
            'http://127.0.0.1:8001/api/agent/',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if api_response.status_code == 200:
            response_data = api_response.json()
            if response_data.get('success'):
                print("✅ AI агент API работает")
                print(f"   Ответ: {response_data.get('response', 'No response')[:50]}...")
                return True
            else:
                print(f"❌ AI агент API вернул ошибку: {response_data.get('error')}")
                return False
        else:
            print(f"❌ AI агент API недоступен, статус: {api_response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Ошибка при тестировании AI агента: {e}")
        return False

def test_django_api_proxy():
    """Тестируем Django API прокси"""
    print("\n🔍 Тестирование Django API прокси...")

    try:
        # Проверяем Django health endpoint
        django_health_response = requests.get('http://127.0.0.1:8000/api/v1/ai/production/health/', timeout=5)
        if django_health_response.status_code == 200:
            print("✅ Django API health endpoint доступен")
        else:
            print(f"❌ Django API health endpoint недоступен, статус: {django_health_response.status_code}")
            return False

        # Тестируем Django API прокси
        test_data = {
            "message": "Test message through Django proxy",
            "session_id": "django_test_123"
        }

        django_api_response = requests.post(
            'http://127.0.0.1:8000/api/v1/ai/production/agent/',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if django_api_response.status_code == 200:
            response_data = django_api_response.json()
            if response_data.get('success'):
                print("✅ Django API прокси работает")
                print(f"   Ответ: {response_data.get('response', 'No response')[:50]}...")
                return True
            else:
                print(f"❌ Django API прокси вернул ошибку: {response_data.get('error')}")
                return False
        else:
            print(f"❌ Django API прокси недоступен, статус: {django_api_response.status_code}")
            print(f"   Текст ответа: {django_api_response.text}")
            return False

    except Exception as e:
        print(f"❌ Ошибка при тестировании Django API прокси: {e}")
        return False

def test_widget_components():
    """Тестируем компоненты виджета"""
    print("\n🔍 Тестирование компонентов виджета...")

    try:
        # Получаем HTML главной страницы
        response = requests.get('http://127.0.0.1:8000/', timeout=10)

        if response.status_code != 200:
            print(f"❌ Сайт недоступен, статус: {response.status_code}")
            return False

        html_content = response.text

        # Проверяем наличие компонентов виджета
        checks = [
            ('Кнопка виджета', 'class="unity-widget-button"'),
            ('Чат виджета', 'id="unityWidgetChat"'),
            ('JavaScript функции', 'window.unityWidget'),
            ('Обработчики', 'button.onclick = openWidget'),
        ]

        all_found = True
        for name, pattern in checks:
            if pattern in html_content:
                print(f"✅ {name} найден")
            else:
                print(f"❌ {name} не найден")
                all_found = False

        return all_found

    except Exception as e:
        print(f"❌ Ошибка при тестировании компонентов виджета: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ AI СИСТЕМЫ")
    print("=" * 50)

    # Запускаем тесты
    ai_agent_ok = test_ai_agent()
    django_proxy_ok = test_django_api_proxy()
    widget_components_ok = test_widget_components()

    print("\n🎯 ФИНАЛЬНЫЙ ВЕРДИКТ:")
    print("=" * 30)

    if ai_agent_ok and django_proxy_ok and widget_components_ok:
        print("🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ ИДЕАЛЬНО!")
        print("🌐 Перейдите на http://127.0.0.1:8000/")
        print("🔘 Найдите 🤖 кнопку в правом нижнем углу")
        print("💬 Нажмите на кнопку - должен открыться чат")
        print("📝 Напишите сообщение - AI должен ответить")
        return 0
    else:
        print("❌ Найдены проблемы:")
        if not ai_agent_ok:
            print("   - AI агент не работает")
        if not django_proxy_ok:
            print("   - Django API прокси не работает")
        if not widget_components_ok:
            print("   - Компоненты виджета не найдены")
        return 1

if __name__ == "__main__":
    sys.exit(main())