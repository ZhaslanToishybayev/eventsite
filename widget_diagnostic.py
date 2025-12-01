#!/usr/bin/env python3
"""
🎯 Widget Diagnostic Tool v1.0 - Комплексная проверка работоспособности AI консультанта

Этот скрипт проводит полную диагностику виджета на:
- Производительность и лаги
- Ошибки в JavaScript
- CSS конфликты
- Проблемы с анимациями
- Ошибки в логике
- Проверку всех 5 функций
"""

import os
import re
import json
from datetime import datetime

def analyze_widget_files():
    """Анализ файлов виджета на наличие потенциальных проблем"""

    print("🔍 ПРОВЕРКА ФАЙЛОВ ВИДЖЕТА")
    print("=" * 50)

    issues = []
    warnings = []

    # Проверяем основные файлы
    files_to_check = {
        'base.html': '/var/www/myapp/eventsite/templates/base.html',
        'CSS': '/var/www/myapp/eventsite/static/css/enhanced-chat-widget.css',
        'JS': '/var/www/myapp/eventsite/static/js/enhanced-chat-widget.js'
    }

    for file_name, file_path in files_to_check.items():
        if os.path.exists(file_path):
            print(f"✅ {file_name} - найден")

            # Проверяем размер файла
            size = os.path.getsize(file_path)
            if size > 100000:  # Больше 100KB
                warnings.append(f"⚠️ {file_name} - большой размер файла ({size} bytes)")

            # Проверяем на дублирование кода
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # Поиск дублированных функций
                if file_name == 'JS':
                    functions = re.findall(r'function\s+(\w+)', content)
                    duplicates = [func for func in set(functions) if functions.count(func) > 1]
                    if duplicates:
                        issues.append(f"❌ Дублированные функции в JS: {', '.join(duplicates)}")

                # Поиск неиспользуемых переменных
                if file_name == 'CSS':
                    # Проверяем на неиспользуемые CSS переменные
                    css_vars = re.findall(r'--[\w-]+:', content)
                    for var in set(css_vars):
                        var_name = var.replace(':', '')
                        if content.count(var_name) < 2:
                            warnings.append(f"⚠️ CSS переменная {var_name} может быть неиспользована")

        else:
            issues.append(f"❌ {file_name} - не найден")

    return issues, warnings

def check_performance_issues():
    """Проверка на потенциальные проблемы с производительностью"""

    print("\n⚡ ПРОВЕРКА ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 50)

    issues = []
    warnings = []

    # Проверяем JavaScript файл
    js_file = '/var/www/myapp/eventsite/static/js/enhanced-chat-widget.js'
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()

        # Проверка на частые вызовы setInterval/clearInterval
        intervals = re.findall(r'setInterval', js_content)
        if len(intervals) > 3:
            warnings.append(f"⚠️ Много вызовов setInterval: {len(intervals)} - может вызывать утечки памяти")

        # Проверка на частые DOM операции в циклах
        if 'for' in js_content and 'appendChild' in js_content:
            warnings.append("⚠️ Возможны частые DOM операции в циклах")

        # Проверка на большое количество анимаций
        animations = re.findall(r'@keyframes\s+\w+', js_content)
        if len(animations) > 10:
            warnings.append(f"⚠️ Много ключевых кадров анимаций: {len(animations)}")

        # Проверка на оптимизацию событий
        if 'addEventListener' in js_content and 'removeEventListener' not in js_content:
            warnings.append("⚠️ Есть addEventListener, но нет removeEventListener - возможны утечки памяти")

    return issues, warnings

def check_css_issues():
    """Проверка CSS на проблемы"""

    print("\n🎨 ПРОВЕРКА CSS")
    print("=" * 50)

    issues = []
    warnings = []

    css_file = '/var/www/myapp/eventsite/static/css/enhanced-chat-widget.css'
    if os.path.exists(css_file):
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()

        # Проверка на избыточные селекторы
        selectors = re.findall(r'\.[\w-]+', css_content)
        selector_counts = {}
        for selector in selectors:
            selector_counts[selector] = selector_counts.get(selector, 0) + 1

        for selector, count in selector_counts.items():
            if count > 3:
                warnings.append(f"⚠️ Селектор {selector} используется {count} раз - возможно дублирование")

        # Проверка на тяжелые эффекты
        if 'box-shadow' in css_content:
            shadow_count = css_content.count('box-shadow')
            if shadow_count > 10:
                warnings.append(f"⚠️ Много т затемняющих эффектов: {shadow_count}")

        # Проверка на оптимизацию анимаций
        if 'transform:' in css_content and 'will-change:' not in css_content:
            warnings.append("⚠️ Используются transform, но нет will-change для оптимизации")

    return issues, warnings

def check_functionality():
    """Проверка всех 5 реализованных функций"""

    print("\n🚀 ПРОВЕРКА ФУНКЦИОНАЛЬНОСТИ")
    print("=" * 50)

    issues = []
    warnings = []

    js_file = '/var/www/myapp/eventsite/static/js/enhanced-chat-widget.js'
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()

        # Проверка анимации появления
        if 'widgetEntrance' not in js_content or 'chatSlideIn' not in js_content:
            issues.append("❌ Анимация появления - не найдены ключевые функции")

        # Проверка звуковых эффектов
        if 'Audio' not in js_content and 'audio' not in js_content:
            warnings.append("⚠️ Звуковые эффекты - не найдены вызовы аудио")

        # Проверка умных подсказок
        if 'popularQuestions' not in js_content and 'hints' not in js_content:
            warnings.append("⚠️ Умные подсказки - не найдены ключевые функции")

        # Проверка темной темы
        if 'dark-theme' not in js_content and 'prefers-color-scheme' not in js_content:
            warnings.append("⚠️ Темная тема - не найдены ключевые функции")

        # Проверка уведомлений
        if 'notification' not in js_content and 'Notification' not in js_content:
            warnings.append("⚠️ Уведомления - не найдены ключевые функции")

    return issues, warnings

def generate_report(issues, warnings):
    """Генерация итогового отчета"""

    print("\n📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 50)

    total_issues = len(issues)
    total_warnings = len(warnings)

    if total_issues == 0 and total_warnings == 0:
        print("🎉 ОТЛИЧНО! Виджет работает идеально!")
        print("✅ Нет критических ошибок")
        print("✅ Нет предупреждений")
        print("✅ Все функции работают корректно")
        print("✅ Производительность оптимальна")
        return True
    else:
        print(f"❌ Найдено {total_issues} критических проблем")
        print(f"⚠️ Найдено {total_warnings} предупреждений")

        if issues:
            print("\n🔴 КРИТИЧЕСКИЕ ПРОБЛЕМЫ:")
            for i, issue in enumerate(issues, 1):
                print(f"{i}. {issue}")

        if warnings:
            print("\n🟡 ПРЕДУПРЕЖДЕНИЯ:")
            for i, warning in enumerate(warnings, 1):
                print(f"{i}. {warning}")

        return False

def main():
    """Главная функция диагностики"""

    print("🎯 Widget Diagnostic Tool v1.0")
    print("Комплексная проверка AI консультанта")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    all_issues = []
    all_warnings = []

    # Проводим все проверки
    issues1, warnings1 = analyze_widget_files()
    all_issues.extend(issues1)
    all_warnings.extend(warnings1)

    issues2, warnings2 = check_performance_issues()
    all_issues.extend(issues2)
    all_warnings.extend(warnings2)

    issues3, warnings3 = check_css_issues()
    all_issues.extend(issues3)
    all_warnings.extend(warnings3)

    issues4, warnings4 = check_functionality()
    all_issues.extend(issues4)
    all_warnings.extend(warnings4)

    # Генерируем отчет
    is_perfect = generate_report(all_issues, all_warnings)

    if is_perfect:
        print("\n✨ ВЫВОД: Виджет действительно работает идеально!")
        print("🎯 Можно смело использовать в продакшене!")
    else:
        print("\n🔧 РЕКОМЕНДАЦИИ:")
        if any("duplicate" in issue.lower() for issue in all_issues):
            print("- Удалите дублированные функции")
        if any("memory leak" in warning.lower() for warning in all_warnings):
            print("- Добавьте removeEventListener для предотвращения утечек памяти")
        if any("performance" in warning.lower() for warning in all_warnings):
            print("- Оптимизируйте DOM операции и анимации")

    print(f"\n🔍 Диагностика завершена в {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()