#!/usr/bin/env python3
"""
Тестирование упрощенного интерактивного AI endpoint
"""

import requests
import json

def test_simplified_interactive_endpoint():
    """Тестируем упрощенный интерактивный endpoint без сессий"""

    base_url = "http://127.0.0.1:8000"

    print("🚀 Тестируем упрощенный интерактивный AI endpoint")
    print("=" * 60)

    # Используем постоянные куки для сохранения CSRF токена
    session = requests.Session()

    # Тест 1: Начало создания俱乐部
    print("\n📝 Тест 1: Запрос на создание клуба (упрощенный endpoint)")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/simplified/interactive/chat/",
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
            print(f"📝 Сообщение: {data.get('message', '')[:150]}...")
            if "📝 Вопрос 1" in data.get('message', ''):
                print("✅ Начался интерактивный процесс")
                state_id = data.get('state_id')
                print(f"🔑 Получен state_id: {state_id}")
                return state_id
            else:
                print("❌ Не начался интерактивный процесс")
                return None
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return None

def test_simplified_session_preservation():
    """Тестируем сохранение состояния в упрощенном решении"""

    base_url = "http://127.0.0.1:8000"

    print("\n🚀 Тестируем сохранение состояния в упрощенном решении")
    print("=" * 60)

    # Используем постоянные куки для сохранения CSRF токена
    session = requests.Session()
    state_id = None

    # Тест 1: Начало создания клуба
    print("\n📝 Тест 1: Начало создания клуба")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/simplified/interactive/chat/",
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
                state_id = data.get('state_id')
                print(f"🔑 state_id: {state_id}")
            else:
                print("❌ Не начался интерактивный процесс")
                return
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(response.text)
            return

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return

    if not state_id:
        print("❌ Не получен state_id, не можем продолжить тест")
        return

    # Тест 2: Ответ на первый вопрос
    print("\n📝 Тест 2: Ответ на первый вопрос (название)")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/simplified/interactive/chat/",
            headers={
                'Content-Type': 'application/json'
            },
            json={
                "message": "Шахматный клуб",
                "user_email": "test@example.com",
                "state_id": state_id  # Передаем state_id
            }
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ответ получен: {len(data.get('message', ''))} символов")
            if "📝 Вопрос 2" in data.get('message', ''):
                print("✅ Переход к вопросу 2 (описание)")
                print("✅ СОСТОЯНИЕ СОХРАНЯЕТСЯ!")
                # Проверяем, что state_id изменился или остался тем же
                new_state_id = data.get('state_id')
                print(f"🔑 Новый state_id: {new_state_id}")
                if new_state_id != state_id:
                    print("📝 state_id был обновлен")
                    state_id = new_state_id
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
            f"{base_url}/api/v1/ai/simplified/interactive/chat/",
            headers={
                'Content-Type': 'application/json'
            },
            json={
                "message": "Это место где любители шахмат могут развивать мастерство, участвовать в турнирах и общаться с единомышленниками. Мы проводим регулярные встречи, турниры и обучение для начинающих игроков.",
                "user_email": "test@example.com",
                "state_id": state_id  # Передаем state_id
            }
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ответ получен: {len(data.get('message', ''))} символов")
            if "📝 Вопрос 3" in data.get('message', ''):
                print("✅ Переход к вопросу 3 (категория)")
                print("✅ СОСТОЯНИЕ СОХРАНЯЕТСЯ!")
            else:
                print("❌ Не перешел к вопросу 3")
                print(f"Полный ответ: {data.get('message', '')[:300]}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

    print("\n" + "=" * 60)
    print("✅ Тестирование упрощенного решения завершено")

if __name__ == "__main__":
    test_simplified_session_preservation()