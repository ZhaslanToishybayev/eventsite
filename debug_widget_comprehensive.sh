#!/bin/bash

# 🚀 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ И ДЕБАГГИНГ AI ВИДЖЕТА

echo "🚀 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ И ДЕБАГГИНГ AI ВИДЖЕТА"
echo "======================================================"
echo ""

# 1. Проверка Django сервера
echo "1. ПРОВЕРКА DJANGO СЕРВЕРА:"
echo "=============================="
if curl -s http://localhost:8000/ | grep -q "Центр сообществ"; then
    echo "✅ Django сервер работает"
    django_works=true
else
    echo "❌ Django сервер не работает"
    django_works=false
fi

echo ""

# 2. Проверка AI API
echo "2. ПРОВЕРКА AI API:"
echo "==================="
api_test=$(curl -s -X POST "http://localhost:8000/api/v1/ai/simplified/interactive/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет", "user_email": "test@fan-club.kz", "state_id": null}')

if echo "$api_test" | grep -q "Привет\|здравствуйте\|Добро"; then
    echo "✅ AI API работает"
    echo "   Ответ: $(echo "$api_test" | grep -o '"message":"[^"]*"' | head -1)"
    api_works=true
else
    echo "❌ AI API не работает"
    echo "   Ответ: $api_test"
    api_works=false
fi

echo ""

# 3. Проверка виджета в HTML
echo "3. ПРОВЕРКА ВИДЖЕТА В HTML:"
echo "============================="
html_content=$(curl -s http://localhost:8000/)

if echo "$html_content" | grep -q "ai-chat-widget"; then
    echo "✅ Элемент виджета найден в HTML"
    widget_in_html=true
else
    echo "❌ Элемент виджета не найден в HTML"
    widget_in_html=false
fi

if echo "$html_content" | grep -q "chatToggleBtn"; then
    echo "✅ Кнопка виджета найдена в HTML"
    button_in_html=true
else
    echo "❌ Кнопка виджета не найдена в HTML"
    button_in_html=false
fi

echo ""

# 4. Проверка JavaScript файлов
echo "4. ПРОВЕРКА JAVASCRIPT ФАЙЛОВ:"
echo "==============================="
js_files=(
    "/static/js/ai-chat-widget-v2.js"
    "/static/js/ai-chat-widget-standalone.js"
    "/static/js/ai-chat-widget.js"
)

for js_file in "${js_files[@]}"; do
    if curl -s "http://localhost:8000$js_file" | grep -q "function\|class\|window\.aiChat\|initAIChatWidget"; then
        echo "✅ $js_file загружается и содержит код"
    else
        echo "❌ $js_file не загружается или пустой"
    fi
done

echo ""

# 5. Проверка CSS файлов
echo "5. ПРОВЕРКА CSS ФАЙЛОВ:"
echo "========================"
css_files=(
    "/static/css/ai-chat-widget-v2.css"
    "/static/css/ai-chat-widget.css"
)

for css_file in "${css_files[@]}"; do
    if curl -s "http://localhost:8000$css_file" | grep -q "\.ai-chat-widget\|\.ai-chat-button"; then
        echo "✅ $css_file загружается и содержит стили"
    else
        echo "❌ $css_file не загружается或 не содержит стили"
    fi
done

echo ""

# 6. Проверка статуса элементов через JavaScript
echo "6. ПРОВЕРКА ЭЛЕМЕНТОВ ЧЕРЕЗ JAVASCRIPT:"
echo "========================================"
echo "Создаем тестовую HTML страницу для проверки..."

cat > /tmp/widget_test.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Widget Debug Test</title>
    <script src="http://localhost:8000/static/js/ai-chat-widget-v2.js"></script>
    <link rel="stylesheet" href="http://localhost:8000/static/css/ai-chat-widget-v2.css">
</head>
<body>
    <div id="test-container">
        <!-- Test elements -->
        <div id="ai-chat-widget" class="ai-chat-widget" style="display: none;">
            <div class="ai-chat-widget-header">
                <div class="ai-chat-widget-title">AI Консультант</div>
                <div class="ai-chat-widget-close" id="aiCloseBtn">×</div>
            </div>
        </div>
        <div id="chatToggleBtn" class="ai-chat-trigger-button" style="display: block;">
            Widget Button
        </div>
    </div>

    <script>
        console.log("=== WIDGET DEBUG TEST ===");
        console.log("1. Document ready");

        // Wait for scripts to load
        setTimeout(() => {
            console.log("2. Checking global variables:");
            console.log("   - window.AIChatWidget:", typeof window.AIChatWidget);
            console.log("   - window.initAIChatWidgetV2:", typeof window.initAIChatWidgetV2);
            console.log("   - window.aiChatWidgetV2:", window.aiChatWidgetV2);

            console.log("3. Checking elements:");
            console.log("   - Widget element:", document.getElementById('ai-chat-widget'));
            console.log("   - Button element:", document.getElementById('chatToggleBtn'));

            // Try to init widget
            if (typeof window.initAIChatWidgetV2 === 'function') {
                console.log("4. Trying to init widget...");
                try {
                    const widget = window.initAIChatWidgetV2();
                    console.log("   ✅ Widget created:", widget);
                } catch (error) {
                    console.log("   ❌ Widget creation failed:", error);
                }
            } else {
                console.log("4. ❌ initAIChatWidgetV2 function not found");
            }

            // Check styles
            const button = document.getElementById('chatToggleBtn');
            if (button) {
                const styles = window.getComputedStyle(button);
                console.log("5. Button styles:", {
                    display: styles.display,
                    visibility: styles.visibility,
                    position: styles.position,
                    zIndex: styles.zIndex
                });
            }
        }, 2000);
    </script>
</body>
</html>
EOF

echo "✅ Тестовая страница создана: /tmp/widget_test.html"
echo "   Откройте её в браузере для детальной диагностики"

echo ""

# 7. Проверка видимости элементов
echo "7. ПРОВЕРКА ВИДИМОСТИ ЭЛЕМЕНТОВ:"
echo "=================================="
echo "Проверяем, видны ли элементы виджета на странице..."

if echo "$html_content" | grep -q 'style="display:\s*none"'; then
    echo "⚠️  Некоторые элементы скрыты через display: none"
fi

if echo "$html_content" | grep -q 'style="visibility:\s*hidden"'; then
    echo "⚠️  Некоторые элементы скрыты через visibility: hidden"
fi

# Проверим конкретные элементы
widget_style=$(echo "$html_content" | grep -o 'id="ai-chat-widget"[^>]*style="[^"]*"' | head -1)
button_style=$(echo "$html_content" | grep -o 'id="chatToggleBtn"[^>]*style="[^"]*"' | head -1)

if [ -n "$widget_style" ]; then
    echo "ℹ️  Стили виджета: $widget_style"
fi

if [ -n "$button_style" ]; then
    echo "ℹ️  Стили кнопки: $button_style"
fi

echo ""

# 8. Проверка JavaScript ошибок
echo "8. ПРОВЕРКА JAVASCRIPT ОШИБОК:"
echo "================================"
echo "Проверяем, есть ли ошибки в JavaScript..."

# Проверим наличие try-catch блоков и обработки ошибок
js_content=$(curl -s http://localhost:8000/static/js/ai-chat-widget-v2.js)

if echo "$js_content" | grep -q "console\.log\|console\.error\|debug"; then
    echo "✅ В JavaScript есть отладочные сообщения"
fi

if echo "$js_content" | grep -q "try\s*{\|catch\s*("; then
    echo "✅ В JavaScript есть обработка ошибок"
fi

echo ""

# 9. Проверка CSS видимости
echo "9. ПРОВЕРКА CSS ВИДИМОСТИ:"
echo "============================="
css_content=$(curl -s http://localhost:8000/static/css/ai-chat-widget-v2.css)

echo "Проверяем CSS правила для видимости..."

if echo "$css_content" | grep -q "#chatToggleBtn.*display"; then
    display_rule=$(echo "$css_content" | grep -A 5 -B 5 "#chatToggleBtn.*display")
    echo "Правило display для кнопки:"
    echo "$display_rule"
fi

if echo "$css_content" | grep -q "\.ai-chat-widget.*display"; then
    widget_display=$(echo "$css_content" | grep -A 5 -B 5 "\.ai-chat-widget.*display")
    echo "Правило display для виджета:"
    echo "$widget_display"
fi

echo ""

# 10. Создание финального отчета
echo "10. ФИНАЛЬНЫЙ ОТЧЕТ:"
echo "====================="
echo ""

if [ $django_works = true ]; then
    echo "✅ Django сервер: Работает"
else
    echo "❌ Django сервер: Не работает"
fi

if [ $api_works = true ]; then
    echo "✅ AI API: Работает"
else
    echo "❌ AI API: Не работает"
fi

if [ $widget_in_html = true ]; then
    echo "✅ Виджет в HTML: Присутствует"
else
    echo "❌ Виджет в HTML: Отсутствует"
fi

if [ $button_in_html = true ]; then
    echo "✅ Кнопка в HTML: Присутствует"
else
    echo "❌ Кнопка in HTML: Отсутствует"
fi

echo ""

# Рекомендации
echo "🔧 РЕКОМЕНДАЦИИ ПО ДЕБАГГИНГУ:"
echo "================================="

if [ $django_works = false ]; then
    echo "1. 🔧 Починить Django сервер"
fi

if [ $api_works = false ]; then
    echo "2. 🔧 Починить AI API"
fi

if [ $widget_in_html = false ]; then
    echo "3. 🎨 Добавить виджет в HTML"
fi

echo "4. 🔍 Проверить консоль браузера на ошибки"
echo "5. 📏 Проверить CSS стили элементов"
echo "6. 🎯 Проверить z-index и позиционирование"
echo "7. 📝 Проверить обработчики событий"
echo ""

echo "💡 ДЕТАЛЬНАЯ ДИАГНОСТИКА:"
echo "=========================="
echo "1. Откройте браузер и перейдите на: http://localhost:8000"
echo "2. Нажмите F12 и перейдите в Console"
echo "3. Выполните команды:"
echo "   document.getElementById('chatToggleBtn')"
echo "   document.getElementById('ai-chat-widget')"
echo "   window.getComputedStyle(document.getElementById('chatToggleBtn'))"
echo "4. Проверьте видимость кнопки"
echo "5. Попробуйте вручную вызвать: initAIChatWidgetV2()"

echo ""

echo "🎯 ТЕКУЩИЙ СТАТУС:"
echo "=================="
echo "Django: $([ $django_works = true ] && echo '✅' || echo '❌')"
echo "API: $([ $api_works = true ] && echo '✅' || echo '❌')"
echo "Widget HTML: $([ $widget_in_html = true ] && echo '✅' || echo '❌')"
echo "Button HTML: $([ $button_in_html = true ] && echo '✅' || echo '❌')"

echo ""

echo "🏁 ЗАВЕРШЕНИЕ ТЕСТИРОВАНИЯ"
echo "=========================="