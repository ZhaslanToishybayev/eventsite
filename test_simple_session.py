#!/usr/bin/env python3
"""
Простой тест для проверки сессии
"""

import requests
import json

def test_simple_session():
    """Тестируем простую сессию"""

    base_url = "http://127.0.0.1:8000"

    print("🚀 Тестируем сессию")
    print("=" * 60)

    # Используем постоянные куки для сохранения сессии
    session = requests.Session()

    # Тест 1: Простой запрос
    print("\n📝 Тест 1: Простой запрос")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/interactive/chat/",
            headers={
                'Content-Type': 'application/json'
            },
            json={
                "message": "test",
                "user_email": "test@example.com"
            }
        )

        print(f"Status Code: {response.status_code}")
        print(f"Cookies: {session.cookies}")
        print(f"Response length: {len(response.text)}")

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

if __name__ == "__main__":
    test_simple_session()