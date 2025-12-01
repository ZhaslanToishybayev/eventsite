#!/usr/bin/env python3
"""
Final test of main widget functionality
"""

import requests
import json

def test_main_widget_functionality():
    """Test the main widget with proper CSRF handling"""

    base_url = "http://127.0.0.1:8000"

    print("🚀 Тестируем главный виджет - финальная проверка")
    print("=" * 60)

    # Используем постоянные куки для сохранения CSRF токена
    session = requests.Session()

    # Получаем CSRF токен с главной страницы
    print("\n📝 Шаг 1: Получение CSRF токена с главной страницы")
    try:
        response = session.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Главная страница доступна")

            # Ищем CSRF токен в meta теге
            import re
            match = re.search(r'<meta name="csrf-token" content="([^\"]+)"', response.text)
            if match:
                csrf_token = match.group(1)
                print(f"✅ CSRF токен найден: {csrf_token[:20]}...")
            else:
                print("❌ CSRF токен не найден в meta теге")
                return
        else:
            print(f"❌ Ошибка доступа к главной странице: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Ошибка получения CSRF токена: {e}")
        return

    # Тест 1: Начало создания клуба через виджет
    print("\n📝 Тест 1: Запрос на создание клуба через виджет")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/simplified/interactive/chat/",
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            json={
                "message": "хочу создать клуб",
                "user_email": "testuser@fan-club.kz",
                "state_id": None
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
            else:
                print("❌ Не начался интерактивный процесс")
                print(f"Полный ответ: {data.get('message', '')}")
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
    print("\n📝 Тест 2: Ответ на первый вопрос (название клуба)")
    try:
        response = session.post(
            f"{base_url}/api/v1/ai/simplified/interactive/chat/",
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            json={
                "message": "Шахматный клуб Элит",
                "user_email": "testuser@fan-club.kz",
                "state_id": state_id
            }
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ответ получен: {len(data.get('message', ''))} символов")

            if "📝 Вопрос 2" in data.get('message', ''):
                print("✅ Переход к вопросу 2 (описание)")
                print("✅ СОСТОЯНИЕ СОХРАНЯЕТСЯ В ВИДЖЕТЕ!")
                new_state_id = data.get('state_id')
                if new_state_id != state_id:
                    print(f"📝 state_id обновлен: {new_state_id}")
                    state_id = new_state_id
            else:
                print("❌ Не перешел к вопросу 2")
                print(f"Полный ответ: {data.get('message', '')[:300]}...")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

    print("\n" + "=" * 60)
    print("✅ Финальное тестирование главного виджета завершено")
    print("🎯 Главный виджет теперь должен работать с интерактивным AI!")

if __name__ == "__main__":
    test_main_widget_functionality()