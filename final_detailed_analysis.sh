#!/bin/bash

# 🚀 ФИНАЛЬНЫЙ ДЕТАЛЬНЫЙ АНАЛИЗ: СВЕТЯЩАЯСЯ ПАЛОЧКА И ПРОБЛЕМЫ ВИДЖЕТА

echo "🚀 ФИНАЛЬНЫЙ ДЕТАЛЬНЫЙ АНАЛИЗ: СВЕТЯЩАЯСЯ ПАЛОЧКА И ПРОБЛЕМЫ ВИДЖЕТА"
echo "======================================================================"
echo ""

# 1. Проверка всех элементов виджета в HTML
echo "1. ДЕТАЛЬНАЯ ПРОВЕРКА ВСЕХ ЭЛЕМЕНТОВ ВИДЖЕТА В HTML:"
echo "======================================================"
html_content=$(curl -s http://localhost:8000/)

echo "🔍 Поиск всех возможных элементов виджета..."

# Ищем все возможные элементы
widget_patterns=(
    "chatToggleBtn"
    "ai-chat-widget"
    "chatContainer"
    "chatMessages"
    "chatInput"
    "ai-chat-trigger-button"
    "ai-chat-button"
    "aiCloseBtn"
    "chatSendBtn"
    "aiThemeBtn"
    "fas fa-comments"
    "fas fa-paper-plane"
)

for pattern in "${widget_patterns[@]}"; do
    matches=$(echo "$html_content" | grep -o "id=\"[^\"]*$pattern[^\"]*\" class=\"[^\"]*\"[^>]*>.*</div>" | head -1)
    if [ -n "$matches" ]; then
        echo "✅ Найдено: $pattern"
        echo "   HTML: $matches"
    else
        # Попробуем другой формат
        matches2=$(echo "$html_content" | grep -o "class=\"[^\"]*$pattern[^\"]*\"[^>]*>.*</div>" | head -1)
        if [ -n "$matches2" ]; then
            echo "✅ Найдено (class): $pattern"
            echo "   HTML: $matches2"
        else
            echo "❌ Не найдено: $pattern"
        fi
    fi
    echo ""
done

echo ""

# 2. Проверка CSS анимаций
echo "2. ПРОВЕРКА CSS АНИМАЦИЙ И ЭФФЕКТОВ:"
echo "========================================="
css_content=$(curl -s http://localhost:8000/static/css/ai-chat-widget-v2.css)

echo "🔍 Поиск анимаций и эффектов..."

animations=$(echo "$css_content" | grep -E "@keyframes|animation:|::before|::after" | head -10)
if [ -n "$animations" ]; then
    echo "🎨 Найдены анимации:"
    echo "$animations"
else
    echo "❌ Анимации не найдены"
fi

echo ""

# 3. Проверка возможных "палочек" в CSS
echo "3. ПРОВЕРКА ЭЛЕМЕНТОВ, КОТОРЫЕ МОГУТ ВЫГЛЯДЕТЬ КАК ПАЛОЧКА:"
echo "============================================================"
echo "🔍 Поиск элементов, похожих на палочку..."

# Ищем возможные "палочки"
stick_patterns=(
    "height.*[0-9]px"
    "width.*[0-9]px"
    "border"
    "after"
    "before"
    "linear-gradient"
    "transform.*rotate"
    "skew"
)

for pattern in "${stick_patterns[@]}"; do
    results=$(echo "$css_content" | grep -i "$pattern" | head -3)
    if [ -n "$results" ]; then
        echo "🔍 $pattern:"
        echo "$results"
        echo ""
    fi
done

echo ""

# 4. Проверка JavaScript инициализации
echo "4. ПРОВЕРКА JAVASCRIPT ИНИЦИАЛИЗАЦИИ:"
echo "======================================="
echo "🔍 Проверка вызова функций инициализации..."

# Проверим, есть ли вызовы функций в HTML
init_calls=$(echo "$html_content" | grep -o "initAIChatWidget.*()" | head -5)
if [ -n "$init_calls" ]; then
    echo "✅ Найдены вызовы инициализации:"
    echo "$init_calls"
else
    echo "❌ Вызовы инициализации не найдены"
fi

# Проверим наличие глобальных переменных
global_vars=$(echo "$html_content" | grep -o "window\.[a-zA-Z]*" | head -5)
if [ -n "$global_vars" ]; then
    echo "🔍 Найдены глобальные переменные:"
    echo "$global_vars"
fi

echo ""

# 5. Создание детальной тестовой страницы
echo "5. СОЗДАНИЕ ДЕТАЛЬНОЙ ТЕСТОВОЙ СТРАНИЦЫ:"
echo "=========================================="
echo "Создаем страницу для анализа светящейся палочки..."

cat > /tmp/detailed_widget_analysis.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Detailed Widget Analysis</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f0f0f0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .test-section {
            margin: 20px 0;
            padding: 15px;
            border: 2px solid #ccc;
            background: white;
            border-radius: 10px;
        }
        .error { color: red; font-weight: bold; }
        .success { color: green; font-weight: bold; }
        .info { color: blue; font-weight: bold; }
        .warning { color: orange; font-weight: bold; }
        .widget-preview {
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            border: 2px solid #333;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.3);
            z-index: 9999;
        }
        .glowing-stick {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 2px;
            height: 100px;
            background: linear-gradient(180deg, transparent, #6366f1, #a855f7, transparent);
            transform: translate(-50%, -50%) rotate(45deg);
            animation: glow 2s ease-in-out infinite alternate;
            border-radius: 2px;
        }
        @keyframes glow {
            0% { opacity: 0.3; box-shadow: 0 0 10px #6366f1; }
            100% { opacity: 1; box-shadow: 0 0 30px #a855f7, 0 0 60px #6366f1; }
        }
        .button-test {
            width: 64px;
            height: 64px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            border: none;
            color: white;
            font-size: 28px;
            cursor: pointer;
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4);
            transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: visible;
            margin: 20px auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Detailed Widget Analysis</h1>

        <!-- Пример светящейся палочки -->
        <div class="widget-preview">
            <h3>🎯 Possible Glowing Stick</h3>
            <div class="glowing-stick"></div>
            <p>This could be the "glowing stick at 45 degrees" you mentioned</p>
        </div>

        <!-- Пример кнопки виджета -->
        <div style="text-align: center;">
            <h3>🔘 Widget Button Test</h3>
            <button class="button-test">💬</button>
            <p>This is how the widget button should look</p>
        </div>

        <div class="test-section">
            <h2>1. DOM Elements Analysis</h2>
            <div id="dom-analysis"></div>
        </div>

        <div class="test-section">
            <h2>2. CSS Styles Analysis</h2>
            <div id="css-analysis"></div>
        </div>

        <div class="test-section">
            <h2>3. JavaScript Functions Analysis</h2>
            <div id="js-analysis"></div>
        </div>

        <div class="test-section">
            <h2>4. Widget State Analysis</h2>
            <div id="widget-state"></div>
        </div>
    </div>

    <!-- Подключаем оригинальные файлы -->
    <script src="http://localhost:8000/static/js/ai-chat-widget-v2.js"></script>
    <link rel="stylesheet" href="http://localhost:8000/static/css/ai-chat-widget-v2.css">

    <script>
        window.addEventListener('load', function() {
            console.log('=== DETAILED WIDGET ANALYSIS START ===');

            // 1. DOM Elements Analysis
            const domDiv = document.getElementById('dom-analysis');
            domDiv.innerHTML = '<h3>🔍 DOM Elements:</h3>';

            const elementsToCheck = [
                'chatToggleBtn',
                'ai-chat-widget',
                'chatContainer',
                'chatMessages',
                'chatInput',
                'aiCloseBtn',
                'chatSendBtn',
                'aiThemeBtn'
            ];

            elementsToCheck.forEach(id => {
                const element = document.getElementById(id);
                if (element) {
                    const styles = window.getComputedStyle(element);
                    domDiv.innerHTML += `
                        <div style="margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                            <strong>${id}:</strong> FOUND
                            <br>Display: ${styles.display}
                            <br>Position: ${styles.position}
                            <br>Visibility: ${styles.visibility}
                            <br>Opacity: ${styles.opacity}
                            <br>Content: ${element.innerHTML.substring(0, 100)}...
                        </div>
                    `;
                    console.log(`${id}:`, {
                        element: element,
                        styles: {
                            display: styles.display,
                            position: styles.position,
                            visibility: styles.visibility,
                            opacity: styles.opacity
                        }
                    });
                } else {
                    domDiv.innerHTML += `<p class="error">${id}: NOT FOUND</p>`;
                    console.log(`${id}: NOT FOUND`);
                }
            });

            // 2. CSS Styles Analysis
            const cssDiv = document.getElementById('css-analysis');
            cssDiv.innerHTML = '<h3>🎨 CSS Analysis:</h3>';

            const chatToggleBtn = document.getElementById('chatToggleBtn');
            if (chatToggleBtn) {
                const styles = window.getComputedStyle(chatToggleBtn);
                cssDiv.innerHTML += `
                    <div style="background: #f9f9f9; padding: 15px; border-radius: 5px;">
                        <h4>chatToggleBtn Styles:</h4>
                        <p><strong>Display:</strong> ${styles.display}</p>
                        <p><strong>Position:</strong> ${styles.position}</p>
                        <p><strong>Top/Right/Bottom/Left:</strong> ${styles.top} / ${styles.right} / ${styles.bottom} / ${styles.left}</p>
                        <p><strong>Z-index:</strong> ${styles.zIndex}</p>
                        <p><strong>Background:</strong> ${styles.background}</p>
                        <p><strong>Width/Height:</strong> ${styles.width} / ${styles.height}</p>
                        <p><strong>Border-radius:</strong> ${styles.borderRadius}</p>
                        <p><strong>Box-shadow:</strong> ${styles.boxShadow}</p>
                        <p><strong>Overflow:</strong> ${styles.overflow}</p>
                        <p><strong>Opacity:</strong> ${styles.opacity}</p>
                        <p><strong>Visibility:</strong> ${styles.visibility}</p>
                        <p><strong>Cursor:</strong> ${styles.cursor}</p>
                        <p><strong>Content:</strong> ${chatToggleBtn.innerHTML}</p>
                    </div>
                `;
            } else {
                cssDiv.innerHTML += '<p class="error">chatToggleBtn not found for CSS analysis</p>';
            }

            // 3. JavaScript Functions Analysis
            const jsDiv = document.getElementById('js-analysis');
            jsDiv.innerHTML = '<h3>⚙️ JavaScript Functions:</h3>';

            const functionsToCheck = [
                'window.AIChatWidget',
                'window.initAIChatWidgetV2',
                'window.aiChatWidgetV2',
                'window.aiChat'
            ];

            functionsToCheck.forEach(func => {
                try {
                    const value = eval(func);
                    const type = typeof value;
                    if (type === 'function') {
                        jsDiv.innerHTML += `<p class="success">${func}: FUNCTION - ${type}</p>`;
                    } else if (type === 'object') {
                        jsDiv.innerHTML += `<p class="info">${func}: OBJECT - ${type}</p>`;
                    } else {
                        jsDiv.innerHTML += `<p class="warning">${func}: ${type}</p>`;
                    }
                    console.log(`${func}:`, value);
                } catch (e) {
                    jsDiv.innerHTML += `<p class="error">${func}: ERROR - ${e.message}</p>`;
                    console.error(`${func}:`, e);
                }
            });

            // 4. Widget State Analysis
            const stateDiv = document.getElementById('widget-state');
            stateDiv.innerHTML = '<h3>📊 Widget State:</h3>';

            // Проверим, есть ли какие-то видимые элементы виджета
            const allElements = document.querySelectorAll('*');
            let widgetElementsFound = 0;
            let visibleElements = [];

            allElements.forEach(el => {
                if (el.id && el.id.includes('chat') || el.className && el.className.includes('ai-chat')) {
                    widgetElementsFound++;
                    const styles = window.getComputedStyle(el);
                    if (styles.display !== 'none' && styles.visibility !== 'hidden' && styles.opacity !== '0') {
                        visibleElements.push({
                            id: el.id,
                            className: el.className,
                            display: styles.display,
                            visibility: styles.visibility,
                            opacity: styles.opacity,
                            content: el.innerHTML.substring(0, 50)
                        });
                    }
                }
            });

            stateDiv.innerHTML += `<p><strong>Widget elements found:</strong> ${widgetElementsFound}</p>`;
            stateDiv.innerHTML += `<p><strong>Visible elements:</strong> ${visibleElements.length}</p>`;

            if (visibleElements.length > 0) {
                stateDiv.innerHTML += '<h4>Visible Elements:</h4>';
                visibleElements.forEach(el => {
                    stateDiv.innerHTML += `
                        <div style="margin: 5px 0; padding: 10px; background: #e8f4fd; border-radius: 5px;">
                            <strong>ID:</strong> ${el.id}<br>
                            <strong>Class:</strong> ${el.className}<br>
                            <strong>Display:</strong> ${el.display}<br>
                            <strong>Content:</strong> ${el.content}
                        </div>
                    `;
                });
            }

            console.log('Visible widget elements:', visibleElements);

            // Поиск "палочки"
            const possibleStick = document.querySelector('[style*="rotate(45deg)"], [style*="transform: rotate"], .glow, .stick');
            if (possibleStick) {
                console.log('🎯 Possible glowing stick found:', possibleStick);
                stateDiv.innerHTML += '<div class="success"><strong>🎯 Possible glowing stick found!</strong> Check console for details.</div>';
            }

            console.log('=== DETAILED WIDGET ANALYSIS END ===');
        });
    </script>
</body>
</html>
EOF

echo "✅ Детальная тестовая страница создана: /tmp/detailed_widget_analysis.html"
echo "   Откройте её в браузере для анализа светящейся палочки"

echo ""

# 6. Финальные рекомендации
echo "6. ФИНАЛЬНЫЕ РЕКОМЕНДАЦИИ:"
echo "============================"
echo ""

echo "🔍 Возможные причины светящейся палочки:"
echo "1. Часть виджета, которая работает (например, анимация ::before или ::after)"
echo "2. Ошибка в CSS, создающая неожиданный элемент"
echo "3. Остатки от другого виджета или плагина"
echo "4. Элемент, который должен быть частью кнопки, но отображается отдельно"
echo ""

echo "🛠️ Что можно сделать:"
echo "1. Открыть /tmp/detailed_widget_analysis.html для детального анализа"
echo "2. Проверить консоль браузера на наличие ошибок"
echo "3. Проверить, есть ли другие CSS файлы, влияющие на виджет"
echo "4. Проверить, не конфликтует ли FontAwesome с другими стилями"
echo "5. Попробовать временно упростить CSS виджета"
echo ""

echo "🎯 Для немедленного решения:"
echo "1. Откройте браузер: http://localhost:8000"
echo "2. Нажмите F12 → Elements"
echo "3. Найдите светящуюся палочку"
echo "4. Посмотрите её HTML и CSS стили"
echo "5. Найдите кнопку виджета (если она есть)"
echo "6. Сравните стили"

echo ""

echo "🏁 АНАЛИЗ ЗАВЕРШЕН"
echo "==================="
echo "Детальная тестовая страница поможет понять, что именно отображается"
echo "и почему основная кнопка виджета не работает."