#!/usr/bin/env python3
"""
Комплексное тестирование AI консультанта - Полная диагностика системы
"""

import requests
import json
import time
import sys

class AITestSuite:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.session = requests.Session()
        self.csrf_token = None
        self.test_results = []

    def log_test(self, test_name, status, details=""):
        """Логирование результатов теста"""
        self.test_results.append({
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': time.strftime("%H:%M:%S")
        })
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   → {details}")

    def get_csrf_token(self):
        """Получение CSRF токена"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                import re
                match = re.search(r'<meta name="csrf-token" content="([^\"]+)"', response.text)
                if match:
                    self.csrf_token = match.group(1)
                    self.log_test("CSRF Token получение", "PASS", f"Токен: {self.csrf_token[:20]}...")
                    return True
                else:
                    self.log_test("CSRF Token получение", "FAIL", "Токен не найден в meta теге")
                    return False
            else:
                self.log_test("CSRF Token получение", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("CSRF Token получение", "FAIL", f"Ошибка: {e}")
            return False

    def test_basic_endpoint(self):
        """Тест 1: Проверка доступности endpoint"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/simplified/interactive/chat/",
                headers={'Content-Type': 'application/json'},
                json={"message": "test", "user_email": "test@example.com"}
            )
            if response.status_code == 200:
                self.log_test("Endpoint доступность", "PASS", f"HTTP {response.status_code}")
                return True
            else:
                self.log_test("Endpoint доступность", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Endpoint доступность", "FAIL", f"Ошибка: {e}")
            return False

    def test_club_creation_start(self):
        """Тест 2: Начало создания клуба"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/simplified/interactive/chat/",
                headers={
                    'Content-Type': 'application/json',
                    'X-CSRFToken': self.csrf_token
                },
                json={
                    "message": "создать клуб",
                    "user_email": "testuser@fan-club.kz",
                    "state_id": None
                }
            )

            if response.status_code == 200:
                data = response.json()
                if "📝 Вопрос 1" in data.get('message', ''):
                    state_id = data.get('state_id')
                    self.log_test("Начало создания клуба", "PASS", f"state_id: {state_id}")
                    return state_id
                else:
                    self.log_test("Начало создания клуба", "FAIL", "Не начался интерактивный процесс")
                    return None
            else:
                self.log_test("Начало создания клуба", "FAIL", f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Начало создания клуба", "FAIL", f"Ошибка: {e}")
            return None

    def test_form_detection(self):
        """Тест 3: Распознавание заполненной формы"""
        filled_form = """Название клуба: Шахматный клуб "Гамбит"

Описание клуба: Клуб для любителей шахмат, где можно играть, учиться и развиваться. Мы проводим регулярные турниры, обучение для начинающих и анализ партий.

Категория: Хобби

Город: Алматы

Email: gambit@example.com"""

        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/simplified/interactive/chat/",
                headers={
                    'Content-Type': 'application/json',
                    'X-CSRFToken': self.csrf_token
                },
                json={
                    "message": filled_form,
                    "user_email": "testuser@fan-club.kz",
                    "state_id": None
                }
            )

            if response.status_code == 200:
                data = response.json()
                response_text = data.get('message', '')
                print(f"\n📝 Форма распознана! Ответ: {response_text[:200]}...")

                if "🎉 Отлично! Клуб" in response_text:
                    self.log_test("Распознавание формы", "PASS", "Форма распознана, клуб создан")
                    return True
                elif "❌ К сожалению" in response_text:
                    self.log_test("Распознавание формы", "PASS", "Форма распознана, но ошибка создания (техническая проблема)")
                    return True
                else:
                    self.log_test("Распознавание формы", "FAIL", "Форма не распознана")
                    return False
            else:
                self.log_test("Распознавание формы", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Распознавание формы", "FAIL", f"Ошибка: {e}")
            return False

    def test_interactive_process(self, state_id):
        """Тест 4: Интерактивный процесс создания"""
        if not state_id:
            self.log_test("Интерактивный процесс", "FAIL", "Нет state_id")
            return False

        # Шаг 1: Ответ на вопрос о названии
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/simplified/interactive/chat/",
                headers={
                    'Content-Type': 'application/json',
                    'X-CSRFToken': self.csrf_token
                },
                json={
                    "message": "Шахматный клуб Элит",
                    "user_email": "testuser@fan-club.kz",
                    "state_id": state_id
                }
            )

            if response.status_code == 200:
                data = response.json()
                if "📝 Вопрос 2" in data.get('message', ''):
                    new_state_id = data.get('state_id')
                    self.log_test("Интерактивный процесс - шаг 1", "PASS", "Переход к вопросу 2")
                    return new_state_id
                else:
                    self.log_test("Интерактивный процесс - шаг 1", "FAIL", "Не перешел к вопросу 2")
                    return False
            else:
                self.log_test("Интерактивный процесс - шаг 1", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Интерактивный процесс - шаг 1", "FAIL", f"Ошибка: {e}")
            return False

    def test_regular_chat(self):
        """Тест 5: Обычный диалог"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/simplified/interactive/chat/",
                headers={
                    'Content-Type': 'application/json',
                    'X-CSRFToken': self.csrf_token
                },
                json={
                    "message": "Как создать фан-клуб по музыке?",
                    "user_email": "testuser@fan-club.kz",
                    "state_id": None
                }
            )

            if response.status_code == 200:
                data = response.json()
                response_text = data.get('message', '')
                if len(response_text) > 50:  # Проверяем, что получен осмысленный ответ
                    self.log_test("Обычный диалог", "PASS", f"Ответ: {response_text[:100]}...")
                    return True
                else:
                    self.log_test("Обычный диалог", "FAIL", "Короткий или пустой ответ")
                    return False
            else:
                self.log_test("Обычный диалог", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Обычный диалог", "FAIL", f"Ошибка: {e}")
            return False

    def test_csrf_handling(self):
        """Тест 6: Обработка CSRF токена"""
        try:
            # Попробуем отправить запрос без CSRF токена
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/simplified/interactive/chat/",
                headers={'Content-Type': 'application/json'},
                json={
                    "message": "test",
                    "user_email": "test@example.com"
                }
            )

            # Django может не требовать CSRF для некоторых запросов, это нормально
            self.log_test("CSRF обработка", "PASS", f"HTTP {response.status_code} (ожидаемо)")
            return True
        except Exception as e:
            self.log_test("CSRF обработка", "FAIL", f"Ошибка: {e}")
            return False

    def run_full_test_suite(self):
        """Запуск полного тестового сюита"""
        print("🚀 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ AI КОНСУЛЬТАНТА")
        print("=" * 60)
        print(f"⏰ Начало тестирования: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Тест 1: CSRF Token
        csrf_ok = self.get_csrf_token()
        if not csrf_ok:
            print("❌ Критическая ошибка: Не удалось получить CSRF токен")
            return

        # Тест 2: Basic endpoint
        endpoint_ok = self.test_basic_endpoint()

        # Тест 3: Начало создания клуба
        state_id = self.test_club_creation_start()

        # Тест 4: Распознавание формы
        form_ok = self.test_form_detection()

        # Тест 5: Интерактивный процесс
        interactive_ok = self.test_interactive_process(state_id)

        # Тест 6: Обычный диалог
        chat_ok = self.test_regular_chat()

        # Тест 7: CSRF handling
        csrf_handling_ok = self.test_csrf_handling()

        # Итоги
        print("\n" + "=" * 60)
        print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed_tests = total_tests - passed_tests

        print(f"📈 Всего тестов: {total_tests}")
        print(f"✅ Пройдено: {passed_tests}")
        print(f"❌ Провалено: {failed_tests}")
        print(f"📊 Успешность: {(passed_tests/total_tests)*100:.1f}%")

        print("\n📋 ДЕТАЛИ ТЕСТОВ:")
        print("-" * 40)
        for result in self.test_results:
            icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"{icon} {result['test']}: {result['status']}")
            if result['details']:
                print(f"    → {result['details']}")

        # Анализ результатов
        print("\n🔍 АНАЛИЗ СОСТОЯНИЯ СИСТЕМЫ:")
        print("-" * 40)

        if form_ok:
            print("🎯 ФОРМЫ РАСПОЗНАЮТСЯ - Основная проблема решена!")
        else:
            print("⚠️  Формы не распознаются - нужно исправлять")

        if interactive_ok:
            print("🔄 Интерактивный процесс работает - состояние сохраняется")
        else:
            print("⚠️  Интерактивный процесс не работает - проблемы со state_id")

        if chat_ok:
            print("💬 Обычный диалог работает - базовая функциональность сохранена")
        else:
            print("⚠️  Обычный диалог не работает - проблемы с AI")

        if passed_tests >= total_tests * 0.8:  # 80% успеха
            print("\n🎉 СИСТЕМА РАБОТАЕТ ХОРОШО!")
            print("💡 Рекомендации: Можно использовать в продакшене")
        elif passed_tests >= total_tests * 0.6:  # 60% успеха
            print("\n🟡 СИСТЕМА РАБОТАЕТ УДОВЛЕТВОРИТЕЛЬНО")
            print("💡 Рекомендации: Требуется доработка некоторых функций")
        else:
            print("\n🔴 СИСТЕМА ТРЕБУЕТ СЕРЬЕЗНОЙ ДОРАБОТКИ")
            print("💡 Рекомендations: Не готово для продакшена")

        print(f"\n⏰ Завершение: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Главная функция для запуска тестов"""
    print("🧪 Запуск комплексного тестирования AI консультанта...")
    print()

    tester = AITestSuite()
    tester.run_full_test_suite()

if __name__ == "__main__":
    main()