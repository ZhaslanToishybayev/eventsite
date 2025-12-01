#!/bin/bash

# 🚀 ГЛУБОКИЙ АНАЛИЗ И ЛОГИРОВАНИЕ AI ВИДЖЕТА

echo "🚀 ГЛУБОКИЙ АНАЛИЗ И ЛОГИРОВАНИЕ AI ВИДЖЕТА"
echo "==============================================="
echo ""

# 1. Проверка Django сервера
echo "1. ПРОВЕРКА DJANGO СЕРВЕРА:"
echo "=============================="
if curl -s http://localhost:8000/ | grep -q "Центр сообществ"; then
    echo "✅ Django сервер работает"
    django_status="working"
else
    echo "❌ Django сервер не работает"
    django_status="not_working"
fi

echo ""

# 2. Проверка AI API с детальным логированием
echo "2. ПРОВЕРКА AI API С ДЕТАЛЬНЫМ ЛОГИРОВАНИЕМ:"
echo "=============================================="
echo "Тестовый запрос к AI API..."

api_response=$(curl -v -s -X POST "http://localhost:8000/api/v1/ai/simplified/interactive/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет", "user_email": "test@fan-club.kz", "state_id": null}' 2>&1)

echo "🔍 Детальный ответ API:"
echo "$api_response" | head -20

# Проверим статус ответа
if echo "$api_response" | grep -q "200 OK"; then
    echo "✅ API возвращает статус 200"
    api_status="working"
else
    echo "❌ API не возвращает статус 200"
    api_status="not_working"
fi

# Проверим содержимое ответа
response_body=$(echo "$api_response" | tail -10)
if echo "$response_body" | grep -q "Привет\|здравствуйте\|success.*true"; then
    echo "✅ API возвращает корректный ответ"
    api_content="valid"
else
    echo "❌ API возвращает некорректный ответ"
    echo "Тело ответа: $response_body"
    api_content="invalid"
fi

echo ""

# 3. Проверка HTML структуры виджета
echo "3. ПРОВЕРКА HTML СТРУКТУРЫ ВИДЖЕТА:"
echo "======================================="
html_content=$(curl -s http://localhost:8000/)

echo "🔍 Поиск элементов виджета в HTML..."

# Проверим все элементы виджета
widget_elements=(
    "ai-chat-widget"
    "chatToggleBtn"
    "chatContainer"
    "chatMessages"
    "chatInput"
    "ai-chat-trigger-button"
)

for element in "${widget_elements[@]}"; do
    if echo "$html_content" | grep -q "$element"; then
        echo "✅ Элемент '$element' найден в HTML"
    else
        echo "❌ Элемент '$element' не найден в HTML"
    fi
done

echo ""

# 4. Проверка JavaScript файлов
echo "4. ПРОВЕРКА JAVASCRIPT ФАЙЛОВ:"
echo "==============================="
js_files=(
    "/static/js/ai-chat-widget-v2.js"
    "/static/js/ai-chat-widget-standalone.js"
)

for js_file in "${js_files[@]}"; do
    echo "🔍 Проверка файла: $js_file"

    js_content=$(curl -s "http://localhost:8000$js_file")

    # Проверим наличие ключевых функций
    if echo "$js_content" | grep -q "initAIChatWidgetV2"; then
        echo "   ✅ Функция initAIChatWidgetV2 найдена"
    else
        echo "   ❌ Функция initAIChatWidgetV2 не найдена"
    fi

    if echo "$js_content" | grep -q "chatToggleBtn"; then
        echo "   ✅ Упоминание chatToggleBtn найдено"
    else
        echo "   ❌ Упоминание chatToggleBtn не найдено"
    fi

    if echo "$js_content" | grep -q "addEventListener.*click"; then
        echo "   ✅ Обработчики событий найдены"
    else
        echo "   ❌ Обработчики событий не найдены"
    fi

    # Проверим наличие ошибок
    if echo "$js_content" | grep -q "console\.error\|throw.*Error"; then
        echo "   ⚠️  Найдены потенциальные ошибки в коде"
    fi

    echo ""
done

echo ""

# 5. Проверка CSS файлов
echo "5. ПРОВЕРКА CSS ФАЙЛОВ:"
echo "========================"
css_content=$(curl -s http://localhost:8000/static/css/ai-chat-widget-v2.css)

echo "🔍 Проверка CSS стилей для виджета..."

# Проверим стили для кнопки
if echo "$css_content" | grep -A 20 "#chatToggleBtn" | grep -q "position: fixed"; then
    echo "✅ Кнопка имеет position: fixed"
else
    echo "❌ Кнопка не имеет position: fixed"
fi

if echo "$css_content" | grep -A 20 "#chatToggleBtn" | grep -q "display.*flex"; then
    echo "✅ Кнопка имеет display: flex"
else
    echo "❌ Кнопка не имеет display: flex"
fi

if echo "$css_content" | grep -A 20 "#chatToggleBtn" | grep -q "bottom.*30px"; then
    echo "✅ Кнопка позиционирована bottom: 30px"
else
    echo "❌ Кнопка не позиционирована bottom: 30px"
fi

if echo "$css_content" | grep -A 20 "#chatToggleBtn" | grep -q "right.*30px"; then
    echo "✅ Кнопка позиционирована right: 30px"
else
    echo "❌ Кнопка не позиционирована right: 30px"
fi

echo ""

# 6. Проверка видимости элементов
echo "6. ПРОВЕРКА ВИДИМОСТИ ЭЛЕМЕНТОВ:"
echo "==================================="
echo "Проверка стилей элементов в HTML..."

# Проверим, есть ли inline стили, скрывающие элементы
if echo "$html_content" | grep -q 'style="display:\s*none"'; then
    echo "❌ Найдены элементы со style='display: none'"
    hidden_elements=$(echo "$html_content" | grep -o 'id="[^"]*"[^>]*style="display:\s*none[^"]*"')
    echo "   Скрытые элементы: $hidden_elements"
fi

if echo "$html_content" | grep -q 'style="visibility:\s*hidden'; then
    echo "❌ Найдены элементы со style='visibility: hidden'"
fi

# Проверим конкретные стили кнопки
button_styles=$(echo "$html_content" | grep -o 'id="chatToggleBtn"[^>]*style="[^"]*"' | head -1)
if [ -n "$button_styles" ]; then
    echo "ℹ️  Стили кнопки: $button_styles"
else
    echo "ℹ️  У кнопки нет inline стилей"
fi

echo ""

# 7. Проверка JavaScript инициализации
echo "7. ПРОВЕРКА JAVASCRIPT ИНИЦИАЛИЗАЦИИ:"
echo "======================================"
echo "Проверка скриптов инициализации..."

# Проверим наличие debug скрипта
if echo "$html_content" | grep -q "DEBUG AI WIDGET"; then
    echo "✅ Debug скрипт присутствует"
else
    echo "❌ Debug скрипт отсутствует"
fi

# Проверим вызов функции инициализации
if echo "$html_content" | grep -q "initAIChatWidgetV2()"; then
    echo "✅ Функция инициализации вызывается"
else
    echo "❌ Функция инициализации не вызывается"
fi

echo ""

# 8. Создание тестовой страницы для анализа
echo "8. СОЗДАНИЕ ТЕСТОВОЙ СТРАНИЦЫ ДЛЯ АНАЛИЗА:"
echo "============================================"
echo "Создаем тестовую страницу для детального анализа..."

cat > /tmp/widget_analysis.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Widget Analysis</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .test-section { margin: 20px 0; padding: 15px; border: 1px solid #ccc; }
        .error { color: red; }
        .success { color: green; }
        .info { color: blue; }
    </style>
</head>
<body>
    <h1>AI Widget Analysis</h1>

    <div class="test-section">
        <h2>1. Проверка глобальных переменных</h2>
        <div id="globals-test"></div>
    </div>

    <div class="test-section">
        <h2>2. Проверка элементов DOM</h2>
        <div id="dom-test"></div>
    </div>

    <div class="test-section">
        <h2>3. Проверка стилей</h2>
        <div id="styles-test"></div>
    </div>

    <div class="test-section">
        <h2>4. Проверка функций</h2>
        <div id="functions-test"></div>
    </div>

    <!-- Подключаем оригинальные файлы -->
    <script src="http://localhost:8000/static/js/ai-chat-widget-v2.js"></script>
    <link rel="stylesheet" href="http://localhost:8000/static/css/ai-chat-widget-v2.css">

    <script>
        // Ждем загрузки всех ресурсов
        window.addEventListener('load', function() {
            console.log('=== WIDGET ANALYSIS START ===');

            // 1. Проверка глобальных переменных
            const globalsDiv = document.getElementById('globals-test');
            globalsDiv.innerHTML = '<h3>Глобальные переменные:</h3>';

            const globals = [
                'window.AIChatWidget',
                'window.initAIChatWidgetV2',
                'window.aiChatWidgetV2',
                'window.aiChat'
            ];

            globals.forEach(global => {
                try {
                    const value = eval(global);
                    const status = typeof value !== 'undefined' ? 'success' : 'error';
                    globalsDiv.innerHTML += `<p class="${status}">${global}: ${typeof value}</p>`;
                    console.log(`${global}:`, value);
                } catch (e) {
                    globalsDiv.innerHTML += `<p class="error">${global}: ERROR - ${e.message}</p>`;
                    console.error(`${global}:`, e);
                }
            });

            // 2. Проверка элементов DOM
            const domDiv = document.getElementById('dom-test');
            domDiv.innerHTML = '<h3>Элементы DOM:</h3>';

            const elements = [
                'document.getElementById("chatToggleBtn")',
                'document.getElementById("ai-chat-widget")',
                'document.getElementById("chatContainer")'
            ];

            elements.forEach(element => {
                try {
                    const el = eval(element);
                    const status = el ? 'success' : 'error';
                    domDiv.innerHTML += `<p class="${status}">${element}: ${el ? 'FOUND' : 'NOT FOUND'}</p>`;
                    console.log(`${element}:`, el);
                } catch (e) {
                    domDiv.innerHTML += `<p class="error">${element}: ERROR - ${e.message}</p>`;
                    console.error(`${element}:`, e);
                }
            });

            // 3. Проверка стилей
            const stylesDiv = document.getElementById('styles-test');
            stylesDiv.innerHTML = '<h3>Стили элементов:</h3>';

            const button = document.getElementById('chatToggleBtn');
            if (button) {
                const styles = window.getComputedStyle(button);
                stylesDiv.innerHTML += `<p>display: ${styles.display}</p>`;
                stylesDiv.innerHTML += `<p>position: ${styles.position}</p>`;
                stylesDiv.innerHTML += `<p>bottom: ${styles.bottom}</p>`;
                stylesDiv.innerHTML += `<p>right: ${styles.right}</p>`;
                stylesDiv.innerHTML += `<p>z-index: ${styles.zIndex}</p>`;
                stylesDiv.innerHTML += `<p>visibility: ${styles.visibility}</p>`;
                stylesDiv.innerHTML += `<p>opacity: ${styles.opacity}</p>`;

                console.log('Button styles:', {
                    display: styles.display,
                    position: styles.position,
                    bottom: styles.bottom,
                    right: styles.right,
                    zIndex: styles.zIndex,
                    visibility: styles.visibility,
                    opacity: styles.opacity
                });
            } else {
                stylesDiv.innerHTML += '<p class="error">Кнопка не найдена</p>';
            }

            // 4. Проверка функций
            const functionsDiv = document.getElementById('functions-test');
            functionsDiv.innerHTML = '<h3>Функции:</h3>';

            if (typeof window.initAIChatWidgetV2 === 'function') {
                functionsDiv.innerHTML += '<p class="success">initAIChatWidgetV2: FUNCTION FOUND</p>';

                // Попробуем вызвать функцию
                try {
                    console.log('Trying to init widget...');
                    const widget = window.initAIChatWidgetV2();
                    functionsDiv.innerHTML += '<p class="success">Widget init: SUCCESS</p>';
                    functionsDiv.innerHTML += `<p>Widget object: ${typeof widget}</p>`;
                    console.log('Widget created:', widget);
                } catch (e) {
                    functionsDiv.innerHTML += `<p class="error">Widget init: ERROR - ${e.message}</p>`;
                    console.error('Widget creation error:', e);
                }
            } else {
                functionsDiv.innerHTML += '<p class="error">initAIChatWidgetV2: FUNCTION NOT FOUND</p>';
            }

            console.log('=== WIDGET ANALYSIS END ===');
        });
    </script>
</body>
</html>
EOF

echo "✅ Тестовая страница создана: /tmp/widget_analysis.html"
echo "   Откройте её в браузере для детального анализа"

echo ""

# 9. Финальный анализ
echo "9. ФИНАЛЬНЫЙ АНАЛИЗ:"
echo "====================="
echo ""

echo "📊 Статус компонентов:"
echo "Django сервер: $django_status"
echo "API статус: $api_status"
echo "API содержимое: $api_content"

echo ""

echo "🔍 Возможные причины проблем:"
echo "1. ❌ CSS стили не загружаются"
echo "2. ❌ JavaScript функции не определены"
echo "3. ❌ Элементы скрыты через display: none"
echo "4. ❌ Ошибки в JavaScript коде"
echo "5. ❌ Неправильная инициализация виджета"
echo "6. ❌ Проблемы с DOM элементами"

echo ""

echo "🛠️ Рекомендуемые действия:"
echo "1. Проверить консоль браузера на ошибки"
echo "2. Открыть /tmp/widget_analysis.html для анализа"
echo "3. Проверить, загружаются ли CSS и JS файлы"
echo "4. Проверить стили элементов через getComputedStyle()"
echo "5. Проверить, вызывается ли initAIChatWidgetV2()"

echo ""

echo "🎯 Для детального анализа:"
echo "1. Откройте браузер: http://localhost:8000"
echo "2. Нажмите F12 → Console"
echo "3. Выполните: document.getElementById('chatToggleBtn')"
echo "4. Выполните: window.getComputedStyle(document.getElementById('chatToggleBtn'))"
echo "5. Выполните: typeof window.initAIChatWidgetV2"

echo ""

echo "🏁 АНАЛИЗ ЗАВЕРШЕН"
echo "==================="