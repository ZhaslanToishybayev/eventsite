#!/usr/bin/env python3
"""
Финальное тестирование - полный процесс создания клуба
"""

import requests
import json

def test_complete_club_creation_process():
    """Тестируем полный процесс создания клуба"""

    base_url = "http://127.0.0.1:8000"

    print("🚀 Финальное тестирование - полный процесс создания клуба")
    print("=" * 70)

    # Используем постоянные куки для сохранения CSRF токена
    session = requests.Session()

    # Получаем CSRF токен
    try:
        response = session.get(f"{base_url}/")
        csrf_token = session.cookies.get('csrftoken')
        if not csrf_token:
            import re
            match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
            if match:
                csrf_token = match.group(1)
    except:
        csrf_token = 'test-csrf-token'

    state_id = None

    # Шаг 1: Начало создания клуба
    print("\n📝 Шаг 1: Начало создания клуба")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/simplified/interactive/chat/",
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            json={
                "message": "создать клуб",
                "user_email": "testuser@example.com"
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
            return

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    if not state_id:
        print("❌ Не получен state_id")
        return

    # Шаг 2: Название клуба
    print("\n📝 Шаг 2: Название клуба")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/simplified/interactive/chat/",
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            json={
                "message": "Шахматный клуб Элит",
                "user_email": "testuser@example.com",
                "state_id": state_id
            }
        )

        if response.status_code == 200:
            data = response.json()
            if "📝 Вопрос 2" in data.get('message', ''):
                print("✅ Переход к вопросу 2 (описание)")
                state_id = data.get('state_id', state_id)
            else:
                print("❌ Не перешел к вопросу 2")
                return
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # Шаг 3: Описание клуба
    print("\n📝 Шаг 3: Описание клуба")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/simplified/interactive/chat/",
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            json={
                "message": "Это место где любители шахмат могут развивать мастерство, участвовать в турнирах и общаться с единомышленниками. Мы проводим регулярные встречи, турниры и обучение для начинающих игроков. Клуб открыт для всех возрастов и уровней подготовки.",
                "user_email": "testuser@example.com",
                "state_id": state_id
            }
        )

        if response.status_code == 200:
            data = response.json()
            if "📝 Вопрос 3" in data.get('message', ''):
                print("✅ Переход к вопросу 3 (категория)")
                state_id = data.get('state_id', state_id)
            else:
                print("❌ Не перешел к вопросу 3")
                return
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # Шаг 4: Категория
    print("\n📝 Шаг 4: Категория")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/simplified/interactive/chat/",
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            json={
                "message": "Спорт",
                "user_email": "testuser@example.com",
                "state_id": state_id
            }
        )

        if response.status_code == 200:
            data = response.json()
            if "📝 Вопрос 4" in data.get('message', ''):
                print("✅ Переход к вопросу 4 (город)")
                state_id = data.get('state_id', state_id)
            else:
                print("❌ Не перешел к вопросу 4")
                return
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # Шаг 5: Город
    print("\n📝 Шаг 5: Город")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/simplified/interactive/chat/",
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            json={
                "message": "Алматы",
                "user_email": "testuser@example.com",
                "state_id": state_id
            }
        )

        if response.status_code == 200:
            data = response.json()
            if "📝 Вопрос 5" in data.get('message', ''):
                print("✅ Переход к вопросу 5 (email)")
                state_id = data.get('state_id', state_id)
            else:
                print("❌ Не перешел к вопросу 5")
                return
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # Шаг 6: Email
    print("\n📝 Шаг 6: Email")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/simplified/interactive/chat/",
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            json={
                "message": "chess.elite@example.com",
                "user_email": "testuser@example.com",
                "state_id": state_id
            }
        )

        if response.status_code == 200:
            data = response.json()
            if "📝 Вопрос 6" in data.get('message', ''):
                print("✅ Переход к вопросу 6 (телефон)")
                state_id = data.get('state_id', state_id)
            else:
                print("❌ Не перешел к вопросу 6")
                return
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # Шаг 7: Телефон
    print("\n📝 Шаг 7: Телефон")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/simplified/interactive/chat/",
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            json={
                "message": "+7 (701) 123-45-67",
                "user_email": "testuser@example.com",
                "state_id": state_id
            }
        )

        if response.status_code == 200:
            data = response.json()
            if "📝 Вопрос 7" in data.get('message', ''):
                print("✅ Переход к вопросу 7 (адрес)")
                state_id = data.get('state_id', state_id)
            else:
                print("❌ Не перешел к вопросу 7")
                return
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # Шаг 8: Адрес
    print("\n📝 Шаг 8: Адрес")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/simplified/interactive/chat/",
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            json={
                "message": "нет",
                "user_email": "testuser@example.com",
                "state_id": state_id
            }
        )

        if response.status_code == 200:
            data = response.json()
            if "🎉 Отлично! Клуб" in data.get('message', ''):
                print("✅ КЛУБ УСПЕШНО СОЗДАН!")
                print(f"📝 Ответ: {data.get('message', '')[:200]}...")
            else:
                print("❌ Клуб не был создан")
                print(f"📝 Ответ: {data.get('message', '')[:300]}...")
                return
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    print("\n" + "=" * 70)
    print("🎉 ПОЛНЫЙ ПРОЦЕСС СОЗДАНИЯ КЛУБА УСПЕШНО ЗАВЕРШЕН!")
    print("✅ Главный виджет теперь работает с сохранением состояния!")
    print("✅ Интерактивный AI консультант полностью функционирует!")

if __name__ == "__main__":
    test_complete_club_creation_process()