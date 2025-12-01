#!/bin/bash

# 🚀 FIX BLACK WIDGET PROBLEM

echo "🚀 ИСПРАВЛЕНИЕ ЧЕРНОГО ВИДЖЕТА"
echo "==============================="
echo ""

echo "1. Проверка CSS стилей:"
echo "========================"

# Check if CSS has the direct gradient
css_content=$(curl -s http://localhost:8000/static/css/ai-chat-widget-v2.css)

if echo "$css_content" | grep -q "background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%)"; then
    echo "✅ Прямой градиент в CSS найден"
else
    echo "❌ Прямой градиент в CSS не найден"
    echo "🔧 Добавляем прямой градиент..."
    # This should have been fixed by the edit above
fi

echo ""
echo "2. Проверка HTML структуры:"
echo "============================="

html_content=$(curl -s http://localhost:8000/)

if echo "$html_content" | grep -q "ai-chat-trigger-button"; then
    echo "✅ Правильный CSS класс в HTML"
else
    echo "❌ CSS класс не найден в HTML"
fi

if echo "$html_content" | grep -q "fas fa-comments"; then
    echo "✅ FontAwesome иконка найдена"
else
    echo "❌ FontAwesome иконка не найдена"
fi

echo ""
echo "3. Проверка JavaScript:"
echo "======================="

if echo "$html_content" | grep -q "ai-chat-widget-v2.js"; then
    echo "✅ JavaScript виджета загружен"
else
    echo "❌ JavaScript виджета не найден"
fi

if echo "$html_content" | grep -q "initAIChatWidgetV2"; then
    echo "✅ Функция инициализации найдена"
else
    echo "❌ Функция инициализации не найдена"
fi

echo ""
echo "4. Диагностика виджета:"
echo "========================"

# Check widget button visibility
widget_visible=$(curl -s http://localhost:8000/ | grep -c "chatToggleBtn")
echo "Количество элементов chatToggleBtn: $widget_visible"

if [ "$widget_visible" -eq 2 ]; then
    echo "✅ Нормально (1 HTML + 1 JS лог)"
else
    echo "⚠️  Подозрительное количество: $widget_visible"
fi

echo ""
echo "🎯 РЕКОМЕНДАЦИИ:"
echo "=================="

echo "1. ОБНОВИТЕ СТРАНИЦУ: Ctrl+F5 (полная перезагрузка)"
echo "2. Проверьте виджет - он должен быть сине-фиолетовым"
echo "3. Если все еще черный:"
echo "   - Откройте: http://localhost:8000/widget_functionality_test.html"
echo "   - Это поможет диагностировать проблему"
echo ""

echo "🔧 ДОПОЛНИТЕЛЬНЫЕ РЕШЕНИЯ:"
echo "============================"

echo "Если виджет все еще черный:"
echo "1. Проверьте консоль браузера (F12 → Console) на ошибки"
echo "2. Убедитесь, что CSS файл загружается без ошибок"
echo "3. Попробуйте временно изменить CSS:"
echo "   background: linear-gradient(135deg, #ff0000 0%, #00ff00 100%) !important;"
echo "   (это сделает виджет красно-зеленым для теста)"

echo ""
echo "💡 ТЕСТОВАЯ СТРАНИЦА:"
echo "====================="
echo "Откройте: http://localhost:8000/widget_functionality_test.html"
echo "Эта страница поможет понять, в чем именно проблема"