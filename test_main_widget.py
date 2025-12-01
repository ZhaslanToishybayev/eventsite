#!/usr/bin/env python3
"""
Тестирование основного виджета на главной странице
"""

import requests
import json
import time

def test_main_widget_conversation():
    """Тестируем сохранение состояния разговора в основном виджете"""

    base_url = "http://127.0.0.1:8000"

    print("🚀 Тестируем основной AI виджет на главной странице")
    print("=" * 60)

    # Тест 1: Начало создания клуба
    print("\n📝 Тест 1: Запрос на создание клуба")
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
            print(f"📝 Сообщение: {data.get('message', '')[:100]}...")
            if "📝 Вопрос 1" in data.get('message', ''):
                print("✅ Начался интерактивный процесс создания клуба")
            else:
                print("❌ Не начался интерактивный процесс")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

    # Тест 2: Ответ на первый вопрос (название)
    print("\n📝 Тест 2: Ответ на первый вопрос (название клуба)")
    try:
        response = requests.post(
            f"{base_url}/api/v1/ai/interactive/chat/",
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': 'test-token'
            },
            json={
                "message": "Шахматный клуб",
                "user_email": "test@example.com"
            }
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ответ получен: {len(data.get('message', ''))} символов")
            print(f"📝 Сообщение: {data.get('message', '')[:100]}...")
            if "📝 Вопрос 2" in data.get('message', ''):
                print("✅ Переход к следующему вопросу (описание)")
            else:
                print("❌ Не перешел к следующему вопросу")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

    # Тест 3: Ответ на второй вопрос (описание)
    print("\n📝 Тест 3: Ответ на второй вопрос (описание клуба)")
    try:
        response = requests.post(
            f"{base_url}/api/v1/ai/interactive/chat/",
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': 'test-token'
            },
            json={
                "message": "Это место где любители шахмат могут развивать мастерство, участвовать в турнирах и общаться с единомышленниками. Мы проводим регулярные встречи, турниры и обучение для начинающих игроков.",
                "user_email": "test@example.com"
            }
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ответ получен: {len(data.get('message', ''))} символов")
            print(f"📝 Сообщение: {data.get('message', '')[:100]}...")
            if "📝 Вопрос 3" in data.get('message', ''):
                print("✅ Переход к следующему вопросу (категория)")
            else:
                print("❌ Не перешел к следующему вопросу")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

    # Тест 4: Ответ на третий вопрос (категория)
    print("\n📝 Тест 4: Ответ на третий вопрос (категория)")
    try:
        response = requests.post(
            f"{base_url}/api/v1/ai/interactive/chat/",
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': 'test-token'
            },
            json={
                "message": "Спорт",
                "user_email": "test@example.com"
            }
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ответ получен: {len(data.get('message', ''))} символов")
            print(f"📝 Сообщение: {data.get('message', '')[:100]}...")
            if "📝 Вопрос 4" in data.get('message', ''):
                print("✅ Переход к следующему вопросу (город)")
            else:
                print("❌ Не перешел к следующему вопросу")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

    print("\n" + "=" * 60)
    print("✅ Тестирование основного виджета завершено")
    print("🔍 Проверьте, что состояние сохраняется между запросами")

if __name__ == "__main__":
    test_main_widget_conversation()