#!/usr/bin/env python3
"""
Скрипт для тестирования AI виджета на главной странице
"""

import requests
import re
from bs4 import BeautifulSoup

def test_main_page_widget():
    """Проверяем наличие виджета на главной странице"""
    url = "http://localhost:8003/"

    print("🔍 Тестируем главную страницу...")

    try:
        # Получаем HTML главной страницы
        response = requests.get(url)
        response.raise_for_status()

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        print(f"✅ Страница загружена (статус: {response.status_code})")

        # Проверяем наличие CSS стилей виджета
        css_links = soup.find_all('link', href=re.compile(r'ai-chat-widget'))
        if css_links:
            print(f"✅ CSS виджета найден: {len(css_links)} файлов")
            for css in css_links:
                print(f"   - {css['href']}")
        else:
            print("❌ CSS виджета не найден")

        # Проверяем наличие JavaScript файла виджета
        js_scripts = soup.find_all('script', src=re.compile(r'ai-chat-widget'))
        if js_scripts:
            print(f"✅ JS виджета найден: {len(js_scripts)} файлов")
            for js in js_scripts:
                print(f"   - {js['src']}")
        else:
            print("❌ JS виджета не найден")

        # Проверяем наличие отладочного скрипта
        debug_scripts = soup.find_all('script', string=re.compile(r'DEBUG AI WIDGET'))
        if debug_scripts:
            print(f"✅ Отладочный скрипт найден: {len(debug_scripts)} скриптов")
        else:
            print("❌ Отладочный скрипт не найден")

        # Ищем создание виджета в JavaScript
        creation_methods = []

        # Проверяем разные методы создания
        if re.search(r'initAIChatWidgetV2', html):
            creation_methods.append("initAIChatWidgetV2")

        if re.search(r'AIChatWidget', html):
            creation_methods.append("AIChatWidget")

        if re.search(r'aiChatWidgetV2', html):
            creation_methods.append("aiChatWidgetV2")

        if re.search(r'createWidgetManually', html):
            creation_methods.append("createWidgetManually")

        if creation_methods:
            print(f"✅ Методы создания виджета найдены: {', '.join(creation_methods)}")
        else:
            print("❌ Методы создания виджета не найдены")

        # Проверяем версию виджета
        version_matches = re.findall(r'\?v=(\d+\.\d+\.\d+)', html)
        if version_matches:
            print(f"✅ Версии виджета найдены: {', '.join(set(version_matches))}")
        else:
            print("⚠️ Версии виджета не найдены")

        # Проверяем наличие элементов после загрузки (прогноз)
        print("\n🎯 Прогноз результатов:")
        print("- Скрипт должен выполниться после загрузки страницы")
        print("- Отладочные сообщения должны появиться в консоли браузера")
        print("- Виджет должен быть создан с помощью агрессивного метода")

        return True

    except requests.RequestException as e:
        print(f"❌ Ошибка при запросе: {e}")
        return False
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        return False

def test_widget_files():
    """Проверяем доступность файлов виджета"""
    base_url = "http://localhost:8003"
    files_to_check = [
        "/static/css/ai-chat-widget-v2.css",
        "/static/js/ai-chat-widget-v2.js",
    ]

    print(f"\n📁 Проверяем доступность файлов виджета...")

    for file_path in files_to_check:
        url = base_url + file_path
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"✅ {file_path} - доступен ({len(response.text)} bytes)")
            else:
                print(f"❌ {file_path} - ошибка {response.status_code}")
        except Exception as e:
            print(f"❌ {file_path} - недоступен ({e})")

if __name__ == "__main__":
    print("🚀 Тестирование AI виджета на главной странице")
    print("=" * 50)

    # Тестируем главную страницу
    success = test_main_page_widget()

    # Тестируем файлы
    test_widget_files()

    print("\n" + "=" * 50)
    if success:
        print("✅ Тестирование завершено. Проверьте консоль браузера на http://localhost:8003/")
        print("💡 Ищите сообщения 'DEBUG AI WIDGET' в консоли разработчика")
    else:
        print("❌ Тестирование не удалось")