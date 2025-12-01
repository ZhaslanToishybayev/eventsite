#!/usr/bin/env python3
"""
Комprehensive тест для отладки сессии и ключей
"""

import requests
import json

def comprehensive_session_test():
    """Комprehensive тест сессии"""

    base_url = "http://127.0.0.1:8000"

    print("🚀 Комprehensive тест сессии и ключей")
    print("=" * 60)

    # Используем постоянные куки для сохранения сессии
    session = requests.Session()

    # Тест 1: Проверяем создание сессии и генерацию ключа
    print("\n📝 Тест 1: Проверка создания сессии")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/interactive/chat/",
            headers={
                'Content-Type': 'application/json'
            },
            json={
                "message": "test session creation",
                "user_email": "test@example.com"
            }
        )

        print(f"Status Code: {response.status_code}")
        print(f"Cookies: {session.cookies}")
        print(f"Response length: {len(response.text)}")
        print(f"Response starts with: {response.text[:100]}")

        # Сохраняем сессию
        first_session_id = session.cookies.get('sessionid')
        print(f"First session ID: {first_session_id}")

    except Exception as e:
        print(f"❌ Ошибка запроса 1: {e}")
        return

    # Тест 2: Проверяем сохранение состояния
    print("\n📝 Тест 2: Проверка сохранения состояния")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/interactive/chat/",
            headers={
                'Content-Type': 'application/json'
            },
            json={
                "message": "another test message",
                "user_email": "test@example.com"
            }
        )

        print(f"Status Code: {response.status_code}")
        print(f"Cookies: {session.cookies}")
        print(f"Response length: {len(response.text)}")
        print(f"Response starts with: {response.text[:100]}")

        # Проверяем, что сессия осталась той же
        second_session_id = session.cookies.get('sessionid')
        print(f"Second session ID: {second_session_id}")
        print(f"Session IDs match: {first_session_id == second_session_id}")

    except Exception as e:
        print(f"❌ Ошибка запроса 2: {e}")

    # Тест 3: Проверяем запрос на создание клуба
    print("\n📝 Тест 3: Проверка запроса на создание клуба")
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
        print(f"Response length: {len(response.text)}")
        print(f"Response starts with: {response.text[:200]}")

        if "📝 Вопрос 1" in response.text:
            print("✅ Начался интерактивный процесс")
        else:
            print("❌ Не начался интерактивный процесс")

    except Exception as e:
        print(f"❌ Ошибка запроса 3: {e}")

    # Тест 4: Ответ на первый вопрос
    print("\n📝 Тест 4: Ответ на первый вопрос")
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
        print(f"Response length: {len(response.text)}")
        print(f"Response starts with: {response.text[:200]}")

        if "📝 Вопрос 2" in response.text:
            print("✅ Переход к вопросу 2")
        else:
            print("❌ Не перешел к вопросу 2")

    except Exception as e:
        print(f"❌ Ошибка запроса 4: {e}")

if __name__ == "__main__":
    comprehensive_session_test()