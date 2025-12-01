#!/usr/bin/env python3
"""
🎯 Widget Checkpoint v1.0 - Сохранение идеального состояния AI консультанта

Этот файл содержит полную копию текущего рабочего состояния виджета
с 5 реализованными функциями и исправленными цветами.

🎯 Особенности:
✅ Анимация появления (widgetEntrance, chatSlideIn/Out)
✅ Звуковые эффекты (messageSound, notificationSound, buttonClickSound)
✅ Умные подсказки (popularQuestions с автозаполнением)
✅ Темная тема (автоопределение + ручное переключение)
✅ Уведомления (notification dot + vibration + sound)

🎨 Дизайн:
✅ Зеленый индикатор онлайн статуса (#10b981)
✅ Светлый текст в поле ввода
✅ Профессиональная цветовая гамма (#2563eb)
✅ Удалены все glassmorphism эффекты
✅ CSS переменные для гибкой темизации
"""

import os
import shutil
from datetime import datetime

def create_widget_checkpoint():
    """Создает резервную копию текущего состояния виджета"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Копируем базовый шаблон с виджетом
    base_template = "/var/www/myapp/eventsite/templates/base.html"
    checkpoint_template = f"/var/www/myapp/eventsite/widget_checkpoint_base_{timestamp}.html"

    # Копируем CSS файл
    css_source = "/var/www/myapp/eventsite/static/css/enhanced-chat-widget.css"
    css_checkpoint = f"/var/www/myapp/eventsite/widget_checkpoint_css_{timestamp}.css"

    # Копируем JS файл
    js_source = "/var/www/myapp/eventsite/static/js/enhanced-chat-widget.js"
    js_checkpoint = f"/var/www/myapp/eventsite/widget_checkpoint_js_{timestamp}.js"

    try:
        # Сохраняем базовый шаблон
        if os.path.exists(base_template):
            shutil.copy2(base_template, checkpoint_template)
            print(f"✅ Шаблон сохранен: {checkpoint_template}")

        # Сохраняем CSS
        if os.path.exists(css_source):
            shutil.copy2(css_source, css_checkpoint)
            print(f"✅ CSS сохранен: {css_checkpoint}")

        # Сохраняем JS
        if os.path.exists(js_source):
            shutil.copy2(js_source, js_checkpoint)
            print(f"✅ JS сохранен: {js_checkpoint}")

        # Создаем README с инструкциями
        readme_content = f"""# Widget Checkpoint v1.0 - {timestamp}

## 🎯 Сохраненное состояние виджета

### 📁 Файлы:
- `{os.path.basename(checkpoint_template)}` - Базовый шаблон с виджетом
- `{os.path.basename(css_checkpoint)}` - CSS стили виджета
- `{os.path.basename(js_checkpoint)}` - JavaScript логика виджета

### 🚀 5 Реализованных функций:
1. **✨ Анимация появления** - Плавное появление виджета и сообщений
2. **🎵 Звуковые эффекты** - Звуки для сообщений, уведомлений и кнопок
3. **💡 Умные подсказки** - Автоматические подсказки с популярными вопросами
4. **🌙 Темная тема** - Автоматическое переключение + ручное управление
5. **🔔 Уведомления** - Визуальные и звуковые уведомления

### 🎨 Дизайн особенности:
- Зеленый индикатор онлайн статуса (#10b981)
- Профессиональная цветовая гамма (#2563eb)
- Светлый текст в поле ввода
- Удалены glassmorphism эффекты
- CSS переменные для темизации

### 🔄 Как восстановить:
```bash
# Восстановление шаблона
cp {os.path.basename(checkpoint_template)} /var/www/myapp/eventsite/templates/base.html

# Восстановление CSS
cp {os.path.basename(css_checkpoint)} /var/www/myapp/eventsite/static/css/enhanced-chat-widget.css

# Восстановление JS
cp {os.path.basename(js_checkpoint)} /var/www/myapp/eventsite/static/js/enhanced-chat-widget.js
```

### 📅 Дата создания: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

        readme_file = f"/var/www/myapp/eventsite/widget_checkpoint_README_{timestamp}.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f"✅ README сохранен: {readme_file}")
        print(f"\n🎉 Checkpoint успешно создан!")
        print(f"📁 Все файлы сохранены с меткой времени: {timestamp}")

    except Exception as e:
        print(f"❌ Ошибка при создании checkpoint: {e}")

def list_checkpoints():
    """Показывает список всех созданных checkpoint'ов"""
    checkpoints_dir = "/var/www/myapp/eventsite/"
    checkpoint_files = []

    try:
        for file in os.listdir(checkpoints_dir):
            if file.startswith("widget_checkpoint"):
                checkpoint_files.append(file)

        if checkpoint_files:
            print("📋 Доступные checkpoint'ы:")
            for file in sorted(checkpoint_files):
                file_path = os.path.join(checkpoints_dir, file)
                file_size = os.path.getsize(file_path)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"   📄 {file} ({file_size} bytes) - {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("❌ Checkpoint'ы не найдены")

    except Exception as e:
        print(f"❌ Ошибка при чтении checkpoint'ов: {e}")

if __name__ == "__main__":
    print("🎯 Widget Checkpoint Manager v1.0")
    print("=" * 50)

    action = input("Выберите действие:\n1. Создать новый checkpoint\n2. Показать существующие checkpoint'ы\n> ")

    if action == "1":
        create_widget_checkpoint()
    elif action == "2":
        list_checkpoints()
    else:
        print("❌ Неверный выбор")