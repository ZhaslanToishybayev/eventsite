#!/bin/bash

echo "🧪 ТЕСТ НОВОГО UNITY ВИДЖЕТА"
echo "=============================="

echo ""
echo "🔍 Проверка нового виджета..."

# Проверка наличия нового виджета
if curl -s http://127.0.0.1:8000/ | grep -q 'class="unity-widget-button"'; then
    echo "✅ Кнопка Unity виджета найдена"
else
    echo "❌ Кнопка Unity виджета не найдена"
fi

# Проверка наличия чата
if curl -s http://127.0.0.1:8000/ | grep -q 'id="unityWidgetChat"'; then
    echo "✅ Чат Unity виджета найден"
else
    echo "❌ Чат Unity виджета не найден"
fi

# Проверка JavaScript функций
if curl -s http://127.0.0.1:8000/ | grep -q 'window.unityWidget'; then
    echo "✅ JavaScript функции Unity виджета найдены"
else
    echo "❌ JavaScript функции Unity виджета не найдены"
fi

# Проверка обработчиков
if curl -s http://127.0.0.1:8000/ | grep -q 'button.onclick = openWidget'; then
    echo "✅ Обработчики Unity виджета найдены"
else
    echo "❌ Обработчики Unity виджета не найдены"
fi

echo ""
echo "🔍 Проверка количества виджетов..."

# Подсчет кнопок
unity_buttons=$(curl -s http://127.0.0.1:8000/ | grep -c "unity-widget-button")
guaranteed_buttons=$(curl -s http://127.0.0.1:8000/ | grep -c "guaranteed-widget-button")

echo "🔢 Кнопок Unity виджета: $unity_buttons"
echo "🔢 Кнопок Guaranteed виджета: $guaranteed_buttons"

if [ "$unity_buttons" -eq 1 ] && [ "$guaranteed_buttons" -eq 0 ]; then
    echo "✅ Количество виджетов правильное"
elif [ "$unity_buttons" -gt 1 ]; then
    echo "⚠️  Найдено несколько Unity виджетов"
else
    echo "❌ Проблема с количеством виджетов"
fi

echo ""
echo "🔍 Проверка API..."

# Тест API
response=$(curl -s -X POST http://127.0.0.1:8000/api/v1/ai/production/agent/ \
  -H "Content-Type: application/json" \
  -d '{"message":"Test Unity Widget","session_id":"unity_test"}')

if echo "$response" | grep -q '"success": true'; then
    echo "✅ API работает"
    echo "🤖 Ответ AI: $(echo "$response" | grep -o '"response":"[^"]*"' | head -1 | cut -d'"' -f4 | cut -c1-30)..."
else
    echo "❌ API не работает"
fi

echo ""
echo "🔍 Проверка CSS стилей..."

# Проверка CSS
if curl -s http://127.0.0.1:8000/ | grep -q 'position: fixed'; then
    echo "✅ CSS позиционирование найдено"
else
    echo "❌ CSS позиционирование не найдено"
fi

if curl -s http://127.0.0.1:8000/ | grep -q 'display: none'; then
    echo "✅ CSS скрытия найдено"
else
    echo "❌ CSS скрытия не найдено"
fi

echo ""
echo "🎯 ФИНАЛЬНЫЙ ВЕРДИКТ:"
echo "========================"

error_count=0

if ! curl -s http://127.0.0.1:8000/ | grep -q 'class="unity-widget-button"'; then
    error_count=$((error_count + 1))
fi

if ! curl -s http://127.0.0.1:8000/ | grep -q 'id="unityWidgetChat"'; then
    error_count=$((error_count + 1))
fi

if [ "$unity_buttons" -ne 1 ]; then
    error_count=$((error_count + 1))
fi

if [ "$error_count" -eq 0 ]; then
    echo "🎉 UNITY ВИДЖET ДОЛЖЕН РАБОТАТЬ!"
    echo "🌐 Перейдите на http://127.0.0.1:8000/"
    echo "🤖 Найдите кнопку 🤖 с классом unity-widget-button"
    echo "🔘 Нажмите на кнопку - должен открыться чат"
    echo ""
    echo "🛠️ ДЛЯ ОТЛАДКИ:"
    echo "1. Откройте консоль браузера (F12)"
    echo "2. Проверьте: typeof window.unityWidget"
    echo "3. Проверьте: document.getElementById('unityWidgetButton')"
    echo "4. Попробуйте: window.unityWidget.open()"
else
    echo "❌ Найдено $error_count проблем"
fi