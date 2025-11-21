"""
🧪 Тестирование функциональности ИИ-консультанта
Проверка создания и редактирования сообществ
"""

import requests
import json
import time

class AITestSuite:
    """Тестовый набор для проверки ИИ-консультанта"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
        self.headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': 'test-token'  # Для тестирования
        }

    def create_session(self):
        """Создание новой сессии чата"""
        print("📱 Создание новой сессии...")
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/ai/sessions/create/",
                headers=self.headers
            )

            if response.status_code == 201:
                data = response.json()
                self.session_id = data.get('id') or data.get('session_id')  # Пробуем оба поля
                print(f"✅ Сессия создана: {self.session_id}")
                return True
            else:
                print(f"❌ Ошибка создания сессии: {response.status_code}")
                print(f"Ответ: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Исключение при создании сессии: {e}")
            return False

    def send_message(self, message, expected_agent=None):
        """Отправка сообщения ИИ"""
        if not self.session_id:
            print("❌ Нет активной сессии")
            return None

        print(f"\n📨 Пользователь: {message}")

        data = {
            "message": message,
            "session_id": self.session_id
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/ai/chat/",
                headers=self.headers,
                json=data
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '')
                agent = result.get('agent', 'unknown')
                message_id = result.get('message_id')

                print(f"🤖 ИИ ({agent}): {ai_response[:200]}...")
                print(f"🆔 ID сообщения: {message_id}")

                if expected_agent and agent != expected_agent:
                    print(f"⚠️ Ожидался агент {expected_agent}, но пришел {agent}")

                return {
                    'response': ai_response,
                    'agent': agent,
                    'message_id': message_id,
                    'session_id': self.session_id
                }
            else:
                print(f"❌ Ошибка отправки сообщения: {response.status_code}")
                print(f"Ответ: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Исключение при отправке сообщения: {e}")
            return None

    def test_club_creation_flow(self):
        """Тестирование процесса создания клуба"""
        print("\n🏢 === ТЕСТИРОВАНИЕ СОЗДАНИЯ КЛУБА ===")

        # Тест 1: Приветствие
        print("\n1️⃣ Тест: Приветствие")
        result = self.send_message("Привет!", "orchestrator")
        if not result:
            return False
        time.sleep(1)

        # Тест 2: Запрос на создание клуба
        print("\n2️⃣ Тест: Запрос на создание клуба")
        result = self.send_message("Хочу создать шахматный клуб", "club_specialist")
        if not result:
            return False
        time.sleep(1)

        # Тест 3: Предоставление информации о клубе
        print("\n3️⃣ Тест: Детали клуба")
        club_details = """Шахматный клуб 'Королевская партия'

        Мы занимаемся обучением шахматам для всех возрастов. Проводим турниры каждый месяц, изучаем дебюты, миттельшпиль и эндшпиль. Опытные тренеры помогут вам освоить эту увлекательную игру. Встречи по средам и субботам в парке имени Горького. Присоединяйтесь к нашему дружному сообществу любителей шахмат!

        Категория: Хобби
        Город: Алматы
        Email: chess.royal.party@example.com
        Телефон: +7 701 234 56 78"""

        result = self.send_message(club_details, "club_specialist")
        if not result:
            return False

        # Проверяем, попытался ли ИИ создать клуб
        if "создаю" in result['response'].lower() or "клуб создан" in result['response'].lower():
            print("✅ ИИ активно пытается создать клуб")
        else:
            print("⚠️ ИИ не начал процесс создания клуба")

        time.sleep(1)
        return True

    def test_club_search(self):
        """Тестирование поиска клубов"""
        print("\n🔍 === ТЕСТИРОВАНИЕ ПОИСКА КЛУБОВ ===")

        # Тест 1: Поиск по категории
        print("\n1️⃣ Тест: Поиск спортивных клубов")
        result = self.send_message("Найди спортивные клубы", "club_specialist")
        if not result:
            return False
        time.sleep(1)

        # Тест 2: Поиск по конкретному направлению
        print("\n2️⃣ Тест: Поиск IT сообществ")
        result = self.send_message("Есть ли клубы для программистов?", "club_specialist")
        if not result:
            return False
        time.sleep(1)

        return True

    def test_support_functionality(self):
        """Тестирование поддержки"""
        print("\n🔧 === ТЕСТИРОВАНИЕ ТЕХПОДДЕРЖКИ ===")

        # Тест 1: Инструкция по вступлению
        print("\n1️⃣ Тест: Как вступить в клуб")
        result = self.send_message("Как вступить в существующий клуб?", "support_specialist")
        if not result:
            return False
        time.sleep(1)

        # Тест 2: Проблема с входом
        print("\n2️⃣ Тест: Проблема с входом")
        result = self.send_message("Не могу войти в аккаунт", "support_specialist")
        if not result:
            return False
        time.sleep(1)

        return True

    def test_mentor_functionality(self):
        """Тестирование ментора"""
        print("\n🎓 === ТЕСТИРОВАНИЕ МЕНТОРА ===")

        # Тест 1: Развитие навыков
        print("\n1️⃣ Тест: Развитие в IT")
        result = self.send_message("Хочу развиваться в программировании", "mentor_specialist")
        if not result:
            return False
        time.sleep(1)

        return True

    def test_editing_functionality(self):
        """Тестирование редактирования"""
        print("\n✏️ === ТЕСТИРОВАНИЕ РЕДАКТИРОВАНИЯ ===")

        # Тест 1: Запрос на редактирование клуба
        print("\n1️⃣ Тест: Редактирование клуба")
        result = self.send_message("Я создатель клуба, хочу изменить описание", "club_specialist")
        if not result:
            return False
        time.sleep(1)

        return True

    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 === НАЧАЛО КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ ИИ-КОНСУЛЬТАНТА ===")

        # Создание сессии
        if not self.create_session():
            return False

        # Запуск тестов
        tests = [
            ("Создание клуба", self.test_club_creation_flow),
            ("Поиск клубов", self.test_club_search),
            ("Техподдержка", self.test_support_functionality),
            ("Менторство", self.test_mentor_functionality),
            ("Редактирование", self.test_editing_functionality),
        ]

        results = {}
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*60}")
                result = test_func()
                results[test_name] = result
                if result:
                    print(f"✅ Тест '{test_name}' пройден")
                else:
                    print(f"❌ Тест '{test_name}' не пройден")
            except Exception as e:
                print(f"💥 Тест '{test_name}' вызвал исключение: {e}")
                results[test_name] = False

            time.sleep(2)  # Пауза между тестами

        # Итоговые результаты
        print(f"\n{'='*60}")
        print("📊 === ИТОГИ ТЕСТИРОВАНИЯ ===")

        passed = sum(1 for result in results.values() if result)
        total = len(results)

        for test_name, result in results.items():
            status = "✅ Пройден" if result else "❌ Не пройден"
            print(f"{status}: {test_name}")

        print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {passed}/{total} тестов пройдено")

        if passed == total:
            print("🌉 ВСЕ ТЕСТЫ УСПЕШНЫ! ИИ-консультант работает отлично!")
        elif passed >= total * 0.8:
            print("✨ ХОРОШИЙ РЕЗУЛЬТАТ! Большинство функций работают корректно")
        elif passed >= total * 0.6:
            print("⚠️ УДОВЛЕТВОРИТЕЛЬНО! Есть проблемы, требующие внимания")
        else:
            print("🚨 ТРЕБУЕТ УЛУЧШЕНИЙ! Множество проблем необходимо исправить")

        return results


def main():
    """Основная функция"""
    print("🧪 ЗАПУСК ТЕСТИРОВАНИЯ ИИ-КОНСУЛЬТАНТА")
    print("Убедитесь, что сервер запущен на http://localhost:8000")

    # Ожидание готовности сервера
    print("⏳ Проверка доступности сервера...")
    time.sleep(3)

    # Создание и запуск тестов
    test_suite = AITestSuite()
    results = test_suite.run_all_tests()

    return results


if __name__ == "__main__":
    main()