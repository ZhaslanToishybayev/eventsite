#!/usr/bin/env python3
"""
Тестирование сессии с отладкой
"""

import requests
import json

def test_session_debug():
    """Тестируем сессию с подробной отладкой"""

    base_url = "http://127.0.0.1:8000"

    print("🚀 Тестируем сессию с отладкой")
    print("=" * 60)

    # Используем постоянные куки для сохранения сессии
    session = requests.Session()

    # Тест 1: Начало создания клуба
    print("\n📝 Тест 1: Начало создания клуба")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/interactive/chat/",
            headers={
                'Content-Type': 'application/json'
            },
            json={
                "message": "создать клуб",
                "user_email": "test@example.com"
            }
        )

        print(f"Status Code: {response.status_code}")
        print(f"Cookies: {session.cookies}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ответ получен: {len(data.get('message', ''))} символов")
            if "📝 Вопрос 1" in data.get('message', ''):
                print("✅ Начался интерактивный процесс")
            else:
                print("❌ Не начался интерактивный процесс")

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

    # Тест 2: Ответ на первый вопрос
    print("\n📝 Тест 2: Ответ на первый вопрос (название)")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/interactive/chat/",
            headers={
                'Content-Type': 'application/json'
            },
            json={
                "message": "Шахматный клуб",
                "user_email": "test@example.com"
            }
        )

        print(f"Status Code: {response.status_code}")
        print(f"Cookies: {session.cookies}")
        print(f"Response: {response.text[:500]}...")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ответ получен: {len(data.get('message', ''))} символов")
            if "📝 Вопрос 2" in data.get('message', ''):
                print("✅ Переход к вопросу 2")
            else:
                print("❌ Не перешел к вопросу 2")

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

if __name__ == "__main__":
    test_session_debug()