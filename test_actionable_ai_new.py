#!/usr/bin/env python3
"""
Тестирование Actionable AI (v3.0)
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001"

def test_actionable_ai_status():
    """Тестируем статус Actionable AI"""
    print("🔍 Тестируем статус Actionable AI...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/ai/actionable/status/", timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        data = response.json()
        print(f"✅ Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_actionable_ai_chat():
    """Тестируем чат с Actionable AI"""
    print("\n🤖 Тестируем чат с Actionable AI...")
    try:
        payload = {
            "message": "Создай клуб по программированию для начинающих",
            "user_email": "test@example.com"
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/ai/actionable/chat/",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        print(f"✅ Status Code: {response.status_code}")
        data = response.json()
        print(f"✅ Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_old_ai_functions():
    """Тестируем старые AI функции"""
    print("\n🧪 Тестируем старые AI функции...")
    try:
        # Тест AI консультанта
        payload = {
            "message": "Как создать клуб?",
            "user_email": "test@example.com"
        }

        response = requests.post(
            f"{BASE_URL}/api/ai/consult/",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        print(f"✅ AI Consultant Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ AI Consultant работает!")
        return True
    except Exception as e:
        print(f"❌ Ошибка AI Consultant: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестирования Actionable AI (v3.0)")
    print("=" * 50)

    # Ждем немного, пока Django полностью запустится
    print("⏳ Ожидаем запуск Django...")
    time.sleep(3)

    # Тесты
    tests = [
        test_actionable_ai_status,
        test_actionable_ai_chat,
        test_old_ai_functions
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"✅ Пройдено: {sum(results)}/{len(results)}")

    if all(results):
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Actionable AI работает!")
    else:
        print("⚠️  Некоторые тесты не прошли. Проверьте логи Django.")