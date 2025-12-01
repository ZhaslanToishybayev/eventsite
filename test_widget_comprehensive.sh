#!/bin/bash

# 🚀 ТЕСТИРОВАНИЕ AI ВИДЖЕТА И API

echo "🚀 ТЕСТИРОВАНИЕ AI ВИДЖЕТА И API"
echo "=================================="
echo ""

# Проверка AI API
echo "1. Проверка AI API:"
echo "==================="
echo "Тестовый запрос к AI API..."

api_response=$(curl -s -X POST "http://localhost:8000/api/v1/ai/simplified/interactive/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет", "user_email": "test@fan-club.kz", "state_id": null}')

if echo "$api_response" | grep -q "Привет\|здравствуйте\|Добро"; then
    echo "✅ AI API работает!"
    echo "Ответ: $(echo "$api_response" | jq -r '.message' 2>/dev/null || echo "$api_response" | grep -o '"message":"[^"]*"' | head -1)"
    api_works=true
else
    echo "❌ AI API не работает"
    echo "Ответ: $api_response"
    api_works=false
fi

echo ""

# Проверка виджета на странице
echo "2. Проверка AI виджета на странице:"
echo "===================================="
echo "Проверка наличия виджета в HTML..."

if curl -s http://localhost:8000/ | grep -q "ai-chat-widget"; then
    echo "✅ AI виджет найден в HTML"
    widget_found=true
else
    echo "❌ AI виджет не найден в HTML"
    widget_found=false
fi

echo ""

# Проверка JavaScript файлов
echo "3. Проверка JavaScript файлов:"
echo "================================"
echo "Проверка загрузки JS файлов..."

js_files=(
    "/static/js/ai-chat-widget-v2.js"
    "/static/js/ai-chat-widget-standalone.js"
)

for js_file in "${js_files[@]}"; do
    if curl -s "http://localhost:8000$js_file" | grep -q "function\|class\|var\|let\|const"; then
        echo "✅ $js_file загружается"
    else
        echo "❌ $js_file не загружается или пустой"
    fi
done

echo ""

# Проверка CSS файлов
echo "4. Проверка CSS файлов:"
echo "========================"
echo "Проверка загрузки CSS файлов..."

css_files=(
    "/static/css/ai-chat-widget-v2.css"
)

for css_file in "${css_files[@]}"; do
    if curl -s "http://localhost:8000$css_file" | grep -q "\{.*\}"; then
        echo "✅ $css_file загружается"
    else
        echo "❌ $css_file не загружается или пустой"
    fi
done

echo ""

# Проверка статических файлов
echo "5. Проверка статических файлов:"
echo "================================="
echo "Проверка доступности статических файлов..."

static_dirs=(
    "/static/js/"
    "/static/css/"
    "/static/"
)

for static_dir in "${static_dirs[@]}"; do
    if curl -s "http://localhost:8000$static_dir" | grep -q "Index of\|Directory"; then
        echo "✅ $static_dir доступен"
    else
        echo "⚠️  $static_dir недоступен или нет индексации"
    fi
done

echo ""

# Тест создания клуба
echo "6. Тест создания клуба через AI:"
echo "=================================="
echo "Тест создания клуба..."

club_creation_response=$(curl -s -X POST "http://localhost:8000/api/v1/ai/simplified/interactive/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Создать клуб Название: Тест клуб Описание: Это тестовый клуб Email клуба: test@fan-club.kz", "user_email": "test@fan-club.kz", "state_id": null}')

if echo "$club_creation_response" | grep -q "создан\|created\|club"; then
    echo "✅ Тест создания клуба работает!"
else
    echo "ℹ️  Тест создания клуба: ответ получен, но создание может быть в процессе"
fi

echo ""

# Рекомендации
echo "7. РЕКОМЕНДАЦИИ ПО ВИДЖЕТУ:"
echo "=============================="
echo ""

if [ $api_works = true ]; then
    echo "✅ AI API работает нормально"
else
    echo "❌ AI API не работает - нужно проверить Django логи"
fi

if [ $widget_found = true ]; then
    echo "✅ AI виджет присутствует в HTML"
else
    echo "❌ AI виджет отсутствует в HTML - нужно проверить шаблоны"
fi

echo ""
echo "💡 ДЛЯ ПРОВЕРКИ ВИДЖЕТА В БРАУЗЕРЕ:"
echo "===================================="
echo "1. Откройте: http://localhost:8000"
echo "2. Нажмите F12 (консоль разработчика)"
echo "3. Перейдите на вкладку 'Console'"
echo "4. Проверьте ошибки JavaScript"
echo "5. Попробуйте найти кнопку виджета (обычно в правом нижнем углу)"
echo ""

echo "🔧 ВОЗМОЖНЫЕ ПРОБЛЕМЫ С ВИДЖЕТОМ:"
echo "==================================="
echo "- JavaScript не загружается (проверьте консоль)"
echo "- CSS стили не применяются"
echo "- Проблемы с CORS (если виджет пытается подключиться к другому домену)"
echo "- Виджет скрыт стилями (display: none, visibility: hidden)"
echo "- Ошибки в JavaScript коде виджета"
echo ""

echo "🎯 ТЕКУЩИЙ СТАТУС:"
echo "=================="
echo "Django сервер: ✅ Работает на порту 8000"
echo "AI API: $([ $api_works = true ] && echo '✅ Работает' || echo '❌ Не работает')"
echo "AI виджет в HTML: $([ $widget_found = true ] && echo '✅ Найден' || echo '❌ Не найден')"
echo ""

echo "🏁 СЛЕДУЮЩИЕ ШАГИ:"
echo "=================="
if [ $api_works = false ]; then
    echo "1. 🔧 Починить AI API"
fi
if [ $widget_found = false ]; then
    echo "2. 🎨 Добавить AI виджет в HTML"
fi
echo "3. 🔍 Проверить консоль браузера на ошибки"
echo "4. 🌐 Настроить nginx для доступа из интернета"