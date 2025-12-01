#!/bin/bash

# 🚀 TEST WIDGET FUNCTIONALITY

echo "🚀 ТЕСТ ФУНКЦИОНАЛЬНОСТИ ВИДЖЕТА"
echo "=================================="
echo ""

echo "1. Проверка JavaScript инициализации:"
echo "======================================"

html_content=$(curl -s http://localhost:8000/)

if echo "$html_content" | grep -q "initAIChatWidgetV2"; then
    echo "✅ Функция initAIChatWidgetV2 найдена в коде"
else
    echo "❌ Функция initAIChatWidgetV2 не найдена"
fi

if echo "$html_content" | grep -q "AIChatWidget"; then
    echo "✅ Класс AIChatWidget найден в коде"
else
    echo "❌ Класс AIChatWidget не найден"
fi

echo ""
echo "2. Проверка виджет контейнера:"
echo "================================"

if echo "$html_content" | grep -q "ai-chat-widget"; then
    echo "✅ Контейнер виджета найден"
else
    echo "❌ Контейнер виджета не найден"
fi

if echo "$html_content" | grep -q "chatContainer"; then
    echo "✅ Контейнер чата найден"
else
    echo "❌ Контейнер чата не найден"
fi

echo ""
echo "3. Проверка API endpoint:"
echo "=========================="

if echo "$html_content" | grep -q "/api/v1/ai/simplified/interactive/chat/"; then
    echo "✅ API endpoint найден"
else
    echo "❌ API endpoint не найден"
fi

# Test API endpoint
api_response=$(curl -s -X POST "http://localhost:8000/api/v1/ai/simplified/interactive/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет", "user_email": "test@fan-club.kz", "state_id": null}' 2>/dev/null)

if echo "$api_response" | grep -q '"success": true'; then
    echo "✅ API endpoint работает"
else
    echo "❌ API endpoint не работает"
    echo "   Проверим ответ: $(echo "$api_response" | head -100)"
fi

echo ""
echo "🎯 РЕКОМЕНДАЦИИ:"
echo "=================="

echo "1. 🔥 ОБНОВИТЕ СТРАНИЦУ: Ctrl+F5"
echo "2. Откройте консоль браузера (F12 → Console)"
echo "3. Должны увидеть сообщения об инициализации виджета"
echo "4. Попробуйте нажать на виджет"
echo ""

echo "🔍 ЧТО ДОЛЖНО БЫТЬ В КОНСОЛИ:"
echo "================================"
echo "✅ Используем initAIChatWidgetV2 функцию"
echo "✅ AI Chat Widget успешно инициализирован через initAIChatWidgetV2"
echo "✅ Элемент виджета после автоматической инициализации: [object HTMLDivElement]"
echo ""

echo "💡 ЕСЛИ ВИДЖЕТ ВСЕ ЕЩЕ НЕ РАБОТАЕТ:"
echo "======================================="
echo "1. Проверьте консоль браузера на ошибки"
echo "2. Сообщите мне что видите в консоли"
echo "3. Проверьте, есть ли виджет контейнер в HTML"