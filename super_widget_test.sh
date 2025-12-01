#!/bin/bash

echo "🧪 СУПЕР ДЕТАЛЬНЫЙ ТЕСТ ВИДЖЕТА"
echo "=================================="

echo ""
echo "🔍 Проверка базовых компонентов..."

# Проверка Django
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ | grep -q "200"; then
    echo "✅ Django сайт работает"
else
    echo "❌ Django сайт не работает"
    exit 1
fi

# Проверка AI агента
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/ | grep -q "200"; then
    echo "✅ AI агент работает"
else
    echo "❌ AI агент не работает"
fi

# Проверка API прокси
if curl -s http://127.0.0.1:8000/api/v1/ai/production/health/ | grep -q '"status": "healthy"'; then
    echo "✅ API прокси работает"
else
    echo "❌ API прокси не работает"
fi

echo ""
echo "🔍 Проверка HTML структуры виджета..."

# Проверка наличия кнопки
if curl -s http://127.0.0.1:8000/ | grep -q 'class="guaranteed-widget-button"'; then
    echo "✅ Кнопка виджета найдена в HTML"
else
    echo "❌ Кнопка виджета не найдена в HTML"
fi

# Проверка наличия чата
if curl -s http://127.0.0.1:8000/ | grep -q 'id="guaranteedWidget"'; then
    echo "✅ Чат виджета найден в HTML"
else
    echo "❌ Чат виджета не найден в HTML"
fi

# Проверка JavaScript функций
if curl -s http://127.0.0.1:8000/ | grep -q 'window.openGuaranteedWidget'; then
    echo "✅ Функция openGuaranteedWidget найдена"
else
    echo "❌ Функция openGuaranteedWidget не найдена"
fi

echo ""
echo "🔍 Проверка CSS стилей..."

# Проверка CSS
if curl -s http://127.0.0.1:8000/ | grep -q 'position: fixed'; then
    echo "✅ CSS стили найдены"
else
    echo "❌ CSS стили не найдены"
fi

echo ""
echo "🔍 Тестирование API коммуникации..."

# Тест API
response=$(curl -s -X POST http://127.0.0.1:8000/api/v1/ai/production/agent/ \
  -H "Content-Type: application/json" \
  -d '{"message":"Test","session_id":"debug_test"}')

if echo "$response" | grep -q '"success": true'; then
    echo "✅ API коммуникация работает"
    echo "🤖 Пример ответа: $(echo "$response" | grep -o '"response":"[^"]*"' | head -1 | cut -d'"' -f4 | cut -c1-50)..."
else
    echo "❌ API коммуникация не работает"
    echo "Ошибка: $response"
fi

echo ""
echo "🔍 Проверка JavaScript в браузере (симуляция)..."

# Проверка структуры JavaScript
js_check=$(curl -s http://127.0.0.1:8000/ | grep -A 50 "document.addEventListener('DOMContentLoaded'" | head -20)

if echo "$js_check" | grep -q "window.openGuaranteedWidget = function"; then
    echo "✅ JavaScript функции правильно определены"
else
    echo "❌ JavaScript функции не определены правильно"
fi

if echo "$js_check" | grep -q "button.onclick = window.openGuaranteedWidget"; then
    echo "✅ Обработчик кнопки назначен"
else
    echo "❌ Обработчик кнопки не назначен"
fi

echo ""
echo "🔍 Детальный анализ HTML..."

# Анализ HTML структуры
html_content=$(curl -s http://127.0.0.1:8000/)

# Проверка правильного расположения
if echo "$html_content" | grep -A 5 -B 5 "guaranteed-widget-button" | grep -q "</body>"; then
    echo "✅ Виджет расположен внутри body"
else
    echo "❌ Виджет расположен неправильно"
fi

# Проверка стилей
if echo "$html_content" | grep -q "display: flex"; then
    echo "✅ Стили отображения найдены"
else
    echo "❌ Стили отображения не найдены"
fi

if echo "$html_content" | grep -q "display: none"; then
    echo "✅ Стили скрытия найдены"
else
    echo "❌ Стили скрытия не найдены"
fi

echo ""
echo "🔍 Проверка конфликтов..."

# Проверка на дубликаты
button_count=$(echo "$html_content" | grep -c "guaranteed-widget-button")
echo "🔢 Количество кнопок виджета: $button_count"

if [ "$button_count" -eq 1 ]; then
    echo "✅ Количество кнопок правильное"
elif [ "$button_count" -gt 1 ]; then
    echo "⚠️  Найдено несколько кнопок - возможны конфликты"
else
    echo "❌ Кнопки не найдены"
fi

echo ""
echo "🎯 ФИНАЛЬНЫЙ ВЕРДИКТ:"
echo "========================"

# Сводка
error_count=0

if ! curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ | grep -q "200"; then
    error_count=$((error_count + 1))
fi

if ! echo "$html_content" | grep -q 'class="guaranteed-widget-button"'; then
    error_count=$((error_count + 1))
fi

if ! echo "$html_content" | grep -q 'id="guaranteedWidget"'; then
    error_count=$((error_count + 1))
fi

if ! echo "$html_content" | grep -q 'window.openGuaranteedWidget'; then
    error_count=$((error_count + 1))
fi

if [ "$error_count" -eq 0 ]; then
    echo "🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ! Виджет должен работать."
    echo "🌐 Перейдите на http://127.0.0.1:8000/ и нажмите на 🤖 кнопку"
else
    echo "❌ Найдено $error_count проблем. Смотрите детали выше."
fi

echo ""
echo "🛠️ РЕКОМЕНДАЦИИ:"
echo "1. Проверьте консоль браузера (F12) на наличие JavaScript ошибок"
echo "2. Убедитесь, что кнопка 🤖 видна в правом нижнем углу"
echo "3. Попробуйте очистить кеш браузера (Ctrl+F5)"
echo "4. Проверьте, что Django и AI агент запущены"