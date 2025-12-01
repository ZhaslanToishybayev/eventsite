#!/usr/bin/env python3
"""
🧪 AI Consultant API Test Suite - Тестирование AI консультанта

Этот скрипт тестирует все endpoints AI консультанта для проверки работоспособности
и корректности ответов. Используется для валидации интеграции GPT-4o mini с Django.
"""

import requests
import json
import time
import sys
import os

# Настройки
BASE_URL = "http://127.0.0.1:8000"  # Измените на ваш URL
API_BASE = f"{BASE_URL}/api/ai"

# Тестовые данные
TEST_USER_ID = 123
TEST_LOCATION = "Алматы"
TEST_INTERESTS = ["музыка", "пение", "инструменты"]

def print_header(title):
    """Печать заголовка теста"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_test(test_name):
    """Печать названия теста"""
    print(f"\n📋 {test_name}")
    print("-" * 40)

def print_success(message):
    """Печать успешного результата"""
    print(f"✅ {message}")

def print_error(message):
    """Печать ошибки"""
    print(f"❌ {message}")

def print_info(message):
    """Печать информационного сообщения"""
    print(f"ℹ️ {message}")

def test_health_check():
    """Тест: Проверка работоспособности API"""
    print_test("Health Check Test")

    try:
        response = requests.get(f"{API_BASE}/health/")
        print_info(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print_success("Health check successful")
            print_info(f"AI Available: {data.get('ai_available', False)}")
            print_info(f"Models: {data.get('models', [])}")
            print_info(f"Features: {data.get('features', [])}")
            print_info(f"Database Status: {data.get('database_status', 'unknown')}")
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Health check error: {e}")
        return False

def test_ai_consultation():
    """Тест: AI консультация"""
    print_test("AI Consultation Test")

    test_cases = [
        {
            "name": "Приветствие",
            "message": "Привет! Как дела?",
            "expected_type": "greeting"
        },
        {
            "name": "Поиск клубов",
            "message": "Найди музыкальные клубы в Алматы",
            "expected_type": "recommendations"
        },
        {
            "name": "Поиск клубов",
            "message": "Ищу танцевальные секции для начинающих",
            "expected_type": "recommendations"
        },
        {
            "name": "Создание клуба",
            "message": "Хочу создать новый клуб",
            "expected_type": "club_creation"
        },
        {
            "name": "Общий вопрос",
            "message": "Расскажи о возможностях сайта",
            "expected_type": "general"
        }
    ]

    results = []

    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        print(f"Message: {test_case['message']}")

        try:
            payload = {
                "message": test_case["message"],
                "user_id": TEST_USER_ID,
                "location": TEST_LOCATION
            }

            response = requests.post(f"{API_BASE}/consult/", json=payload)
            print_info(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    response_data = data.get("response", {})
                    response_type = response_data.get("type", "unknown")

                    print_success(f"Response type: {response_type}")
                    print_info(f"Content length: {len(response_data.get('content', ''))} chars")

                    # Проверка ожидаемого типа ответа
                    if response_type == test_case["expected_type"]:
                        print_success("✅ Response type matches expected")
                        results.append(True)
                    else:
                        print_error(f"❌ Response type mismatch. Expected: {test_case['expected_type']}, Got: {response_type}")
                        results.append(False)

                    # Показать первые 200 символов ответа
                    content = response_data.get("content", "")
                    if content:
                        print_info(f"Response preview: {content[:200]}...")

                else:
                    print_error(f"❌ API returned error: {data.get('message', 'Unknown error')}")
                    results.append(False)
            else:
                print_error(f"❌ HTTP error: {response.status_code}")
                results.append(False)

        except Exception as e:
            print_error(f"❌ Exception: {e}")
            results.append(False)

        # Задержка между запросами
        time.sleep(1)

    return all(results)

def test_club_search():
    """Тест: Поиск клубов"""
    print_test("Club Search Test")

    search_queries = [
        {"q": "музыка", "city": "Алматы"},
        {"q": "спорт", "city": "Алматы"},
        {"q": "танцы", "limit": 5},
        {"q": "ит", "city": "Алматы", "limit": 3}
    ]

    results = []

    for query in search_queries:
        print(f"\n🔍 Testing search: {query}")

        try:
            params = "&".join([f"{k}={v}" for k, v in query.items()])
            url = f"{API_BASE}/clubs/search/?{params}"

            response = requests.get(url)
            print_info(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    clubs_data = data.get("data", {})
                    clubs = clubs_data.get("clubs", [])
                    total = clubs_data.get("total", 0)

                    print_success(f"Found {len(clubs)} clubs out of {total} total")

                    if clubs:
                        # Показать первый клуб
                        first_club = clubs[0]
                        print_info(f"First club: {first_club.get('name', 'Unknown')}")
                        print_info(f"Description: {first_club.get('description', '')[:100]}...")
                        results.append(True)
                    else:
                        print_info("No clubs found (this might be expected)")
                        results.append(True)
                else:
                    print_error(f"❌ API error: {data.get('message', 'Unknown error')}")
                    results.append(False)
            else:
                print_error(f"❌ HTTP error: {response.status_code}")
                results.append(False)

        except Exception as e:
            print_error(f"❌ Exception: {e}")
            results.append(False)

        time.sleep(1)

    return all(results)

def test_club_recommendations():
    """Тест: Рекомендации клубов"""
    print_test("Club Recommendations Test")

    test_cases = [
        {
            "name": "Музыкальные интересы",
            "interests": ["музыка", "пение"],
            "location": TEST_LOCATION
        },
        {
            "name": "Спортивные интересы",
            "interests": ["спорт", "фитнес"],
            "location": TEST_LOCATION
        },
        {
            "name": "Технологические интересы",
            "interests": ["программирование", "it"],
            "location": TEST_LOCATION
        }
    ]

    results = []

    for test_case in test_cases:
        print(f"\n🔍 Testing recommendations: {test_case['name']}")
        print(f"Interests: {test_case['interests']}")

        try:
            payload = {
                "interests": test_case["interests"],
                "location": test_case["location"],
                "user_id": TEST_USER_ID,
                "preferences": {
                    "age_group": "18-35",
                    "experience_level": "начинающий"
                }
            }

            response = requests.post(f"{API_BASE}/clubs/recommend/", json=payload)
            print_info(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    recommendations = data.get("recommendations", [])
                    total_found = data.get("total_found", 0)

                    print_success(f"Got {len(recommendations)} recommendations out of {total_found} found")

                    if recommendations:
                        # Проверка структуры рекомендации
                        first_rec = recommendations[0]
                        club = first_rec.get("club", {})
                        relevance_score = first_rec.get("relevance_score", 0)
                        reasons = first_rec.get("reasons", [])

                        print_info(f"Top club: {club.get('name', 'Unknown')}")
                        print_info(f"Relevance score: {relevance_score}")
                        print_info(f"Match reasons: {len(reasons)}")

                        # Проверка обязательных полей
                        required_fields = ["club", "relevance_score", "reasons", "suggested_questions"]
                        missing_fields = [field for field in required_fields if field not in first_rec]

                        if not missing_fields:
                            print_success("✅ All required fields present")
                            results.append(True)
                        else:
                            print_error(f"❌ Missing fields: {missing_fields}")
                            results.append(False)
                    else:
                        print_info("No recommendations found")
                        results.append(True)
                else:
                    print_error(f"❌ API error: {data.get('message', 'Unknown error')}")
                    results.append(False)
            else:
                print_error(f"❌ HTTP error: {response.status_code}")
                results.append(False)

        except Exception as e:
            print_error(f"❌ Exception: {e}")
            results.append(False)

        time.sleep(1)

    return all(results)

def test_club_creation():
    """Тест: Создание клубов"""
    print_test("Club Creation Test")

    # Тестирование потока создания клуба
    creation_steps = [
        {
            "action": "start",
            "expected_stage": "name",
            "data": {}
        },
        {
            "action": "continue",
            "expected_stage": "description",
            "data": {"name": "Тестовый музыкальный клуб"}
        },
        {
            "action": "continue",
            "expected_stage": "city",
            "data": {
                "name": "Тестовый музыкальный клуб",
                "description": "Занятия музыкой для начинающих"
            }
        },
        {
            "action": "continue",
            "expected_stage": "category",
            "data": {
                "name": "Тестовый музыкальный клуб",
                "description": "Занятия музыкой для начинающих",
                "city": "Алматы"
            }
        },
        {
            "action": "continue",
            "expected_stage": "target_audience",
            "data": {
                "name": "Тестовый музыкальный клуб",
                "description": "Занятия музыкой для начинающих",
                "city": "Алматы",
                "category": "Музыка"
            }
        },
        {
            "action": "continue",
            "expected_stage": "confirmation",
            "data": {
                "name": "Тестовый музыкальный клуб",
                "description": "Занятия музыкой для начинающих",
                "city": "Алматы",
                "category": "Музыка",
                "target_audience": "Для начинающих музыкантов"
            }
        },
        {
            "action": "cancel",
            "expected_stage": "cancelled",
            "data": {}
        }
    ]

    results = []

    for step in creation_steps:
        print(f"\n🔍 Testing creation step: {step['action']}")
        print(f"Expected stage: {step['expected_stage']}")

        try:
            payload = {
                "action": step["action"],
                "user_id": TEST_USER_ID,
                "data": step["data"]
            }

            response = requests.post(f"{API_BASE}/club/create/", json=payload)
            print_info(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    response_data = data.get("response", {})
                    stage = response_data.get("stage", "")

                    print_info(f"Actual stage: {stage}")

                    if stage == step["expected_stage"]:
                        print_success("✅ Stage matches expected")
                        results.append(True)
                    else:
                        print_error(f"❌ Stage mismatch. Expected: {step['expected_stage']}, Got: {stage}")
                        results.append(False)

                    # Показать контент ответа
                    content = response_data.get("content", "")
                    if content:
                        print_info(f"Response: {content[:150]}...")

                else:
                    print_error(f"❌ API error: {data.get('message', 'Unknown error')}")
                    results.append(False)
            else:
                print_error(f"❌ HTTP error: {response.status_code}")
                results.append(False)

        except Exception as e:
            print_error(f"❌ Exception: {e}")
            results.append(False)

        time.sleep(1)

    return all(results)

def run_all_tests():
    """Запуск всех тестов"""
    print_header("AI Consultant API Test Suite")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Test User ID: {TEST_USER_ID}")
    print_info(f"Test Location: {TEST_LOCATION}")

    start_time = time.time()

    # Запуск тестов
    test_results = []

    test_results.append(test_health_check())
    test_results.append(test_ai_consultation())
    test_results.append(test_club_search())
    test_results.append(test_club_recommendations())
    test_results.append(test_club_creation())

    # Итоги
    end_time = time.time()
    duration = end_time - start_time

    print_header("Test Results Summary")

    test_names = [
        "Health Check",
        "AI Consultation",
        "Club Search",
        "Club Recommendations",
        "Club Creation"
    ]

    passed_tests = 0
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {name}: {status}")
        if result:
            passed_tests += 1

    print(f"\n📊 Summary:")
    print(f"Passed: {passed_tests}/{len(test_results)}")
    print(f"Failed: {len(test_results) - passed_tests}/{len(test_results)}")
    print(f"Success Rate: {(passed_tests/len(test_results)*100):.1f}%")
    print(f"Duration: {duration:.2f} seconds")

    if all(test_results):
        print_success("🎉 All tests passed! AI Consultant API is working correctly.")
        return 0
    else:
        print_error("⚠️ Some tests failed. Please check the API implementation.")
        return 1

def main():
    """Главная функция"""
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()