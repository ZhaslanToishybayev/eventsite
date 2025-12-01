#!/usr/bin/env python3
"""
Простой тест для проверки распознавания форм
"""

import requests
import json

def test_simple_form():
    """Тестируем простую форму"""

    base_url = "http://127.0.0.1:8000"

    print("🚀 Тестируем простую форму")
    print("=" * 50)

    # Используем постоянные куки для сохранения CSRF токена
    session = requests.Session()

    # Получаем CSRF токен
    try:
        response = session.get(f"{base_url}/")
        if response.status_code == 200:
            import re
            match = re.search(r'<meta name="csrf-token" content="([^\"]+)"', response.text)
            if match:
                csrf_token = match.group(1)
                print(f"✅ CSRF токен получен")
            else:
                print("❌ CSRF токен не найден")
                return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # Простая форма
    simple_form = """Название клуба: Шахматный клуб
Описание: Клуб для любителей шахмат
Категория: Хобби
Город: Алматы
Email: chess@example.com"""

    print(f"\n📝 Отправляем форму:\n{simple_form}\n")

    try:
        response = session.post(
            f"{base_url}/api/v1/ai/simplified/interactive/chat/",
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            json={
                "message": simple_form,
                "user_email": "test@example.com",
                "state_id": None
            }
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ответ: {data.get('message', '')[:200]}...")
            if "DEBUG:" in data.get('message', ''):
                print("✅ DEBUG сообщение найдено в ответе")
        else:
            print(f"❌ Ошибка: {response.status_code}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_simple_form()