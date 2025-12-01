#!/usr/bin/env python3
"""
Тестирование правильного интерактивного AI endpoint
"""

import requests
import json
import time

def test_correct_interactive_endpoint():
    """Тестируем правильный интерактивный endpoint"""

    base_url = "http://127.0.0.1:8000"

    print("🚀 Тестируем правильный интерактивный AI endpoint")
    print("=" * 60)

    # Тест 1: Начало создания клуба
    print("\n📝 Тест 1: Запрос на создание клуба (интерактивный endpoint)")
    try:
        response = requests.post(
            f"{base_url}/api/v1/ai/interactive/chat/",
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': 'test-token'
            },
            json={
                "message": "хочу создать клуб",
                "user_email": "test@example.com"
            }
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ответ получен: {len(data.get('message', ''))} символов")
            print(f"📝 Сообщение: {data.get('message', '')[:150]}...")
            if "📝 Вопрос 1" in data.get('message', ''):
                print("✅ Начался интерактивный процесс создания клуба")
                return True
            else:
                print("❌ Не начался интерактивный процесс")
                return False
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def test_session_preservation():
    """Тестируем сохранение сессии между запросами"""

    base_url = "http://127.0.0.1:8000"

    print("\n🚀 Тестируем сохранение сессии между запросами")
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

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ответ получен: {len(data.get('message', ''))} символов")
            if "📝 Вопрос 1" in data.get('message', ''):
                print("✅ Начался интерактивный процесс")
            else:
                print("❌ Не начался интерактивный процесс")
                print(f"Полный ответ: {data.get('message', '')[:300]}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(response.text)
            return

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return

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

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ответ получен: {len(data.get('message', ''))} символов")
            if "📝 Вопрос 2" in data.get('message', ''):
                print("✅ Переход к вопросу 2 (описание)")
                print("✅ СЕССИЯ СОХРАНЯЕТСЯ!")
            else:
                print("❌ Не перешел к вопросу 2")
                print(f"Полный ответ: {data.get('message', '')[:300]}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

    # Тест 3: Ответ на второй вопрос
    print("\n📝 Тест 3: Ответ на второй вопрос (описание)")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/interactive/chat/",
            headers={
                'Content-Type': 'application/json'
            },
            json={
                "message": "Это место где любители шахмат могут развивать мастерство, участвовать в турнирах и общаться с единомышленниками. Мы проводим регулярные встречи, турниры и обучение для начинающих игроков.",
                "user_email": "test@example.com"
            }
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ответ получен: {len(data.get('message', ''))} символов")
            if "📝 Вопрос 3" in data.get('message', ''):
                print("✅ Переход к вопросу 3 (категория)")
                print("✅ СЕССИЯ СОХРАНЯЕТСЯ!")
            else:
                print("❌ Не перешел к вопросу 3")
                print(f"Полный ответ: {data.get('message', '')[:300]}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

    print("\n" + "=" * 60)
    print("✅ Тестирование сессии завершено")

if __name__ == "__main__":
    # Сначала проверим, что endpoint работает
    if test_correct_interactive_endpoint():
        test_session_preservation()
    else:
        print("❌ Интерактивный endpoint не работает")