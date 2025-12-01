#!/bin/bash

# 🚀 DIAGNOSTIC SCRIPT FOR WIDGET APPEARANCE

echo "🚀 ДИАГНОСТИКА ОТОБРАЖЕНИЯ ВИДЖЕТА"
echo "===================================="
echo ""

echo "🔍 Проверяем, что именно отображается на сайте..."
echo ""

# 1. Check current widget appearance
echo "1. ТЕКУЩИЙ ВИД ВИДЖЕТА:"
echo "========================="

# Check if there are multiple widget buttons
html_content=$(curl -s http://localhost:8000/)
button_count=$(echo "$html_content" | grep -c "chatToggleBtn")

echo "Количество кнопок виджета: $button_count"

if [ "$button_count" -gt 1 ]; then
    echo "⚠️  Найдено несколько кнопок виджета!"
    echo "   Это может вызывать конфликты отображения"
fi

# 2. Check CSS styles
echo ""
echo "2. ПРОВЕРКА CSS СТИЛЕЙ:"
echo "========================"

css_content=$(curl -s http://localhost:8000/static/css/ai-chat-widget-v2.css)

# Check if gradient is present
if echo "$css_content" | grep -q "#6366f1.*#a855f7"; then
    echo "✅ Основной градиент (сине-фиолетовый) найден"
else
    echo "❌ Основной градиент не найден"
fi

# Check for background styles
if echo "$css_content" | grep -q "background: var(--primary-gradient)"; then
    echo "✅ Используется CSS переменная для градиента"
else
    echo "❌ CSS переменная градиента не используется"
fi

# 3. Check for conflicting styles
echo ""
echo "3. ПРОВЕРКА КОНФЛИКТУЮЩИХ СТИЛЕЙ:"
echo "===================================="

# Check if there are any !important overrides
important_count=$(echo "$css_content" | grep -c "!important")
echo "Количество !important стилей: $important_count"

if [ "$important_count" -gt 0 ]; then
    echo "✅ Найдены важные стили для переопределения"
    echo "$css_content" | grep "!important" | head -5
fi

# 4. Check for FontAwesome
echo ""
echo "4. ПРОВЕРКА FONTAWESOME:"
echo "========================="

if echo "$html_content" | grep -q "kit.fontawesome.com"; then
    echo "✅ FontAwesome Kit подключен"
else
    echo "❌ FontAwesome Kit не найден"
fi

if echo "$html_content" | grep -q "fas fa-comments"; then
    echo "✅ Иконка fa-comments найдена"
else
    echo "❌ Иконка fa-comments не найдена"
fi

# 5. Possible issues analysis
echo ""
echo "5. АНАЛИЗ ВОЗМОЖНЫХ ПРОБЛЕМ:"
echo "==============================="

# Check for template CSS conflicts
if echo "$html_content" | grep -q "template_css"; then
    echo "ℹ️  На сайте используются шаблонные CSS файлы"
    echo "   Возможно конфликт стилей с основным шаблоном"
fi

# Check for multiple CSS files
css_files=$(echo "$html_content" | grep -c "\.css")
echo "Количество CSS файлов на странице: $css_files"

if [ "$css_files" -gt 10 ]; then
    echo "⚠️  Много CSS файлов - возможны конфликты стилей"
fi

# 6. Solutions
echo ""
echo "6. РЕКОМЕНДАЦИИ:"
echo "=================="

echo "🎯 Чтобы точно определить проблему:"
echo "1. Откройте http://localhost:8000/widget_test_page.html"
echo "2. Сравните что вы видите с примерами на тестовой странице"
echo "3. Сообщите мне номер варианта, который вы видите"
echo ""

echo "🛠️  Возможные решения:"
echo "1. Очистите кэш браузера (Ctrl+F5)"
echo "2. Проверьте консоль браузера на ошибки"
echo "3. Убедитесь, что все CSS файлы загружаются"
echo "4. Проверьте, нет ли других виджетов на сайте"
echo ""

echo "💡 ВАЖНО:"
echo "Если вы видите черный виджет - проблема с CSS"
echo "Если вы видите фиолетовый со звездочкой - это другой виджет"
echo "Правильный виджет должен быть сине-фиолетовым градиентом с иконкой 💬"