#!/bin/bash

# 🚀 FINAL WIDGET DIAGNOSIS

echo "🚀 ФИНАЛЬНАЯ ДИАГНОСТИКА ВИДЖЕТА"
echo "=================================="
echo ""

echo "1. Проверка JavaScript функций:"
echo "================================="

html_content=$(curl -s http://localhost:8000/)

# Check what functions are available
echo "🔍 Проверка доступных функций в HTML:"
if echo "$html_content" | grep -q "initAIChatWidgetV2"; then
    echo "✅ initAIChatWidgetV2 найдена"
else
    echo "❌ initAIChatWidgetV2 не найдена"
fi

if echo "$html_content" | grep -q "window.aiChatWidgetV2"; then
    echo "✅ window.aiChatWidgetV2 найден"
else
    echo "❌ window.aiChatWidgetV2 не найден"
fi

if echo "$html_content" | grep -q "AIChatWidget"; then
    echo "✅ AIChatWidget найден"
else
    echo "❌ AIChatWidget не найден"
fi

echo ""
echo "2. Проверка виджет HTML:"
echo "========================="

if echo "$html_content" | grep -q "id=\"ai-chat-widget\""; then
    echo "✅ Виджет контейнер найден"
else
    echo "❌ Виджет контейнер не найден"
fi

if echo "$html_content" | grep -q "id=\"chatContainer\""; then
    echo "✅ Контейнер чата найден"
else
    echo "❌ Контейнер чата не найден"
fi

if echo "$html_content" | grep -q "id=\"chatToggleBtn\""; then
    echo "✅ Кнопка виджета найдена"
else
    echo "❌ Кнопка виджета не найдена"
fi

echo ""
echo "3. Проверка CSS:"
echo "================="

css_content=$(curl -s http://localhost:8000/static/css/ai-chat-widget-v2.css)

if echo "$css_content" | grep -q "background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%)"; then
    echo "✅ Градиентный background найден"
else
    echo "❌ Градиентный background не найден"
fi

if echo "$css_content" | grep -q "position: fixed"; then
    echo "✅ Fixed positioning найдено"
else
    echo "❌ Fixed positioning не найдено"
fi

echo ""
echo "🎯 ФИНАЛЬНЫЕ РЕКОМЕНДАЦИИ:"
echo "============================="
echo ""
echo "🔥 СРОЧНО: СДЕЛАЙТЕ СЛЕДУЮЩЕЕ:"
echo "1. Нажмите Ctrl+F5 (полная перезагрузка)"
echo "2. Откройте консоль браузера (F12 → Console)"
echo "3. Сообщите мне ВСЕ сообщения из консоли"
echo "4. Проверьте, есть ли ошибки (красным цветом)"
echo ""
echo "🔍 ЧТО ДОЛЖНО БЫТЬ В КОНСОЛИ ПОСЛЕ ОБНОВЛЕНИЯ:"
echo "=============================================="
echo "✅ Используем initAIChatWidgetV2 функцию"
echo "✅ AI Chat Widget успешно инициализирован через initAIChatWidgetV2"
echo "✅ Элемент виджета после автоматической инициализации: [object HTMLDivElement]"
echo ""
echo "💡 ЕСЛИ ВИДЖЕТ ВСЕ ЕЩЕ НЕ РАБОТАЕТ:"
echo "======================================"
echo "1. Проверьте консоль браузера"
echo "2. Сообщите мне что видите"
echo "3. Возможно, нужно создать standalone виджет"
echo ""
echo "🚀 ПОПРОБУЙТЕ СЕЙЧАС:"
echo "======================="
echo "После Ctrl+F5 попробуйте нажать на виджет!"