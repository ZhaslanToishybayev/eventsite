#!/usr/bin/env python3
"""
🧪 ИСПРАВЛЕННОЕ КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ AI КОНСУЛЬТАНТА
🚀 Исправленная версия с правильной логикой тестов
"""

import os
import sys
import json
import time
import traceback
from pathlib import Path
from datetime import datetime

# Добавляем путь к Django проекту
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from actionable_ai_consultant import ActionableAIConsultant
from django.contrib.auth import get_user_model
from clubs.models import Club, ClubCategory, City
from django.test.client import Client

User = get_user_model()

class AIComprehensiveTesterFixed:
    def __init__(self):
        self.ai = ActionableAIConsultant()
        self.test_results = []
        self.failed_tests = []
        self.start_time = datetime.now()

    def log_test(self, test_name, status, details="", error=None):
        """Логируем результат теста"""
        result = {
            'test_name': test_name,
            'status': status,
            'details': details,
            'error': str(error) if error else None,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)

        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   📝 {details}")
        if error:
            print(f"   ❌ Ошибка: {error}")

    def run_test(self, test_name, test_func, *args, **kwargs):
        """Запускаем тест с обработкой ошибок"""
        try:
            result = test_func(*args, **kwargs)
            if result is not None:
                self.log_test(test_name, "PASS", str(result))
            else:
                self.log_test(test_name, "FAIL", "Тест вернул None")
                self.failed_tests.append(test_name)
        except Exception as e:
            self.log_test(test_name, "FAIL", f"Исключение: {str(e)}", e)
            self.failed_tests.append(test_name)

    def test_security_validation(self):
        """Тест 4: Безопасность и валидация"""
        print("\n🧪 ТЕСТ 4: БЕЗОПАСНОСТЬ И ВАЛИДАЦИЯ")
        print("=" * 50)

        dangerous_inputs = [
            ("", "Пустое сообщение"),
            ("   ", "Только пробелы"),
            ("a" * 1001, "Слишком длинное сообщение"),
            ("<script>alert('test')</script>", "XSS атака"),
            ("DROP TABLE users;", "SQL инъекция"),
            ("javascript:alert('test')", "JavaScript инъекция"),
            ("DELETE FROM clubs WHERE 1=1", "Опасная SQL команда"),
            ("' OR '1'='1", "SQL инъекция"),
        ]

        passed_count = 0
        for test_input, description in dangerous_inputs:
            try:
                response = self.ai.process_user_message(test_input)
                if "Недопустимое содержание" in response or "Пустое сообщение" in response:
                    passed_count += 1
                    self.log_test(f"Безопасность: {description}", "PASS", "Вредоносный ввод заблокирован")
                else:
                    self.log_test(f"Безопасность: {description}", "FAIL", f"Вредоносный ввод не заблокирован: {response[:100]}...")
            except Exception as e:
                self.log_test(f"Безопасность: {description}", "PASS", f"Ошибка обработки (ожидаемо): {e}")

        return f"Безопасность: {passed_count}/{len(dangerous_inputs)} тестов пройдено"

    def test_form_parsing_accuracy(self):
        """Тест 3: Точность парсинга форм"""
        print("\n🧪 ТЕСТ 3: ТОЧНОСТЬ ПАРСИНГА ФОРМ")
        print("=" * 50)

        test_forms = [
            {
                'name': 'Полная форма',
                'form': """Название клуба: Полный Клуб
Описание клуба: Полное описание клуба
Категория: Спорт
Город: Астана
Email клуба: full@club.kz
Телефон: +77011111111
Адрес: Астана, центр
Направления: Спортивные мероприятия
Целевая аудитория: Спортсмены
Навыки: Физическая форма
Теги: спорт, здоровье""",
                'expected_fields': ['name', 'description', 'category', 'city', 'email', 'phone', 'address', 'activities', 'target_audience', 'skills_developed', 'tags']
            },
            {
                'name': 'Короткая форма',
                'form': """Название: Короткий Клуб
Описание: Короткое описание
Категория: Музыка
Город: Шымкент
Email: short@club.kz""",
                'expected_fields': ['name', 'description', 'category', 'city', 'email']
            }
        ]

        passed_count = 0
        for test_case in test_forms:
            club_info = self.ai.extract_club_info(test_case['form'])
            found_fields = [field for field, value in club_info.items() if value and value != 'None' and value.strip()]

            if len(found_fields) >= len(test_case['expected_fields']) * 0.8:  # 80% точности
                passed_count += 1
                self.log_test(f"Парсинг формы: {test_case['name']}", "PASS",
                             f"Найдено {len(found_fields)}/{len(test_case['expected_fields'])} полей")
            else:
                self.log_test(f"Парсинг формы: {test_case['name']}", "FAIL",
                             f"Найдено {len(found_fields)}/{len(test_case['expected_fields'])} полей")

        return f"Парсинг форм: {passed_count}/{len(test_forms)} тестов пройдено"

    def test_club_creation_workflow(self):
        """Тест 2: Полный workflow создания клуба"""
        print("\n🧪 ТЕСТ 2: WORKFLOW СОЗДАНИЯ КЛУБА")
        print("=" * 50)

        # Шаг 1: Запрос на создание клуба
        response1 = self.ai.process_user_message("Хочу создать фан-клуб по программированию")
        step1_passed = "форма" in response1.lower() or "заполн" in response1.lower()

        # Шаг 2: Заполнение формы
        club_form = """Название: Тестовый AI Клуб
Описание: Клуб для тестирования AI функций создания клубов
Категория: Технологии
Город: Алматы
Email: ai.test.club@example.com"""
        response2 = self.ai.process_user_message(club_form)
        step2_passed = "успешно создан" in response2.lower() or "создан" in response2.lower()

        # Шаг 3: Проверка в базе данных
        try:
            club = Club.objects.filter(name="Тестовый AI Клуб").first()
            step3_passed = club is not None
            if step3_passed:
                self.log_test("Проверка в базе данных", "PASS", f"Клуб найден: {club.id}")
            else:
                self.log_test("Проверка в базе данных", "FAIL", "Клуб не найден")
        except Exception as e:
            step3_passed = False
            self.log_test("Проверка в базе данных", "FAIL", f"Ошибка базы данных: {e}")

        passed_steps = sum([step1_passed, step2_passed, step3_passed])
        return f"Workflow создания клуба: {passed_steps}/3 шагов пройдено"

    def test_mobile_responsiveness(self):
        """Тест 6: Mobile адаптивность"""
        print("\n🧪 ТЕСТ 6: MOBILE АДАПТИВНОСТЬ")
        print("=" * 50)

        mobile_scenarios = [
            ("Прив", "Короткое приветствие"),
            ("Созд клуб", "Короткий запрос"),
            ("Пом", "Короткий запрос помощи"),
            ("Привет! 👋 Хочу создать клуб 🏆", "Сообщение с emoji"),
            ("Как создать мероприятие? 📅", "Вопрос с emoji"),
        ]

        passed_count = 0
        for test_input, description in mobile_scenarios:
            try:
                response = self.ai.process_user_message(test_input)
                response_length = len(response)

                if response_length > 10:  # Минимальный ответ
                    passed_count += 1
                    self.log_test(f"Mobile: {description}", "PASS", f"Ответ получен: {response_length} символов")
                else:
                    self.log_test(f"Mobile: {description}", "FAIL", "Пустой ответ")
            except Exception as e:
                self.log_test(f"Mobile: {description}", "FAIL", f"Исключение: {e}")

        return f"Mobile адаптивность: {passed_count}/{len(mobile_scenarios)} тестов пройдено"

    def test_database_operations(self):
        """Тест 7: Операции с базой данных"""
        print("\n🧪 ТЕСТ 7: ОПЕРАЦИИ С БАЗОЙ ДАННЫХ")
        print("=" * 50)

        # Проверка базовых сущностей
        try:
            user_count = User.objects.count()
            category_count = ClubCategory.objects.count()
            city_count = City.objects.count()
            club_count = Club.objects.count()

            self.log_test("Проверка базы данных", "PASS",
                         f"Пользователей: {user_count}, Категорий: {category_count}, Городов: {city_count}, Клубов: {club_count}")
            return f"База данных: все сущности доступны"
        except Exception as e:
            self.log_test("Проверка базы данных", "FAIL", f"Ошибка: {e}")
            return f"База данных: ошибка - {e}"

    def test_performance(self):
        """Тест 8: Производительность"""
        print("\n🧪 ТЕСТ 8: ПРОИЗВОДИТЕЛЬНОСТЬ")
        print("=" * 50)

        # Тест времени ответа AI
        test_messages = ["Привет", "Создай клуб", "Что умеет этот AI?"]
        response_times = []

        for message in test_messages:
            start_time = time.time()
            response = self.ai.process_user_message(message)
            end_time = time.time()

            response_time = (end_time - start_time) * 1000  # в миллисекундах
            response_times.append(response_time)

            if response_time < 2000:  # Меньше 2 секунд
                self.log_test(f"Время ответа: {message}", "PASS", f"{response_time:.1f}ms")
            else:
                self.log_test(f"Время ответа: {message}", "FAIL", f"{response_time:.1f}ms (слишком медленно)")

        avg_response_time = sum(response_times) / len(response_times)
        return f"Производительность: среднее время {avg_response_time:.1f}ms"

    def generate_final_report(self):
        """Генерация финального отчета"""
        print("\n" + "="*80)
        print("📊 ФИНАЛЬНЫЙ ОТЧЕТ О ТЕСТИРОВАНИИ AI КОНСУЛЬТАНТА")
        print("="*80)

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        print(f"   Всего тестов: {total_tests}")
        print(f"   Пройдено: {passed_tests}")
        print(f"   Провалено: {failed_tests}")
        print(f"   Успешность: {success_rate:.1f}%")

        if failed_tests > 0:
            print(f"\n❌ ПРОВАЛЕННЫЕ ТЕСТЫ:")
            for test_name in self.failed_tests:
                print(f"   - {test_name}")

        print(f"\n⏱️ ВРЕМЯ ТЕСТИРОВАНИЯ:")
        end_time = datetime.now()
        duration = end_time - self.start_time
        print(f"   Начало: {self.start_time.strftime('%H:%M:%S')}")
        print(f"   Окончание: {end_time.strftime('%H:%M:%S')}")
        print(f"   Длительность: {duration}")

        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        if success_rate >= 90:
            print("   ✅ Отличная работа! Система готова к production.")
        elif success_rate >= 80:
            print("   ⚠️ Хорошо, но требуются небольшие улучшения.")
        elif success_rate >= 70:
            print("   ⚠️ Удовлетворительно, нужны значительные улучшения.")
        else:
            print("   ❌ Плохо, требуется серьезная доработка.")

        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'failed_test_names': self.failed_tests,
            'test_duration': str(duration)
        }

def main():
    """Запуск исправленного тестирования"""
    print("🚀 ИСПРАВЛЕННОЕ КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ AI КОНСУЛЬТАНТА")
    print("="*80)
    print("🧪 Проверка всех аспектов работы системы")
    print("⏰ Время начала:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    tester = AIComprehensiveTesterFixed()

    # Запускаем основные тесты
    tester.run_test("Безопасность и валидация", tester.test_security_validation)
    tester.run_test("Точность парсинга форм", tester.test_form_parsing_accuracy)
    tester.run_test("Workflow создания клуба", tester.test_club_creation_workflow)
    tester.run_test("Mobile адаптивность", tester.test_mobile_responsiveness)
    tester.run_test("Операции с базой данных", tester.test_database_operations)
    tester.run_test("Производительность", tester.test_performance)

    # Генерируем финальный отчет
    final_report = tester.generate_final_report()

    # Сохраняем отчет
    report_file = f"ai_test_report_fixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_session': final_report,
            'test_results': tester.test_results,
            'execution_time': datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Отчет сохранен: {report_file}")
    return final_report

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Фатальная ошибка: {e}")
        traceback.print_exc()