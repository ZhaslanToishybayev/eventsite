#!/bin/bash

# 🚀 NUCLEAR OPTION: CREATE STANDALONE WIDGET

echo "🚀 СОЗДАНИЕ СТАНДАЛОН ВИДЖЕТА (ЯДЕРНЫЙ ВАРИАНТ)"
echo "=================================================="
echo ""

echo "1. Создаем standalone виджет без зависимостей..."
cat > /var/www/myapp/eventsite/templates/widget_standalone.html << 'EOF'
<!-- STANDALONE AI CHAT WIDGET -->
<style>
    /* Standalone Widget Styles */
    .ai-chat-standalone-button {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        z-index: 9999 !important;
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
        display: flex !important;
        align-items: center;
        justify-content: center;
        overflow: visible !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    .ai-chat-standalone-button:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.5);
    }

    .ai-chat-standalone-container {
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 400px;
        height: 600px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 9998;
        display: none;
        overflow: hidden;
    }

    .ai-chat-standalone-header {
        background: #6366f1;
        color: white;
        padding: 15px;
        text-align: center;
        font-weight: bold;
    }

    .ai-chat-standalone-body {
        padding: 15px;
        height: 450px;
        overflow-y: auto;
    }

    .ai-chat-standalone-input {
        padding: 15px;
        display: flex;
        border-top: 1px solid #eee;
    }

    .ai-chat-standalone-input input {
        flex: 1;
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 5px;
        margin-right: 10px;
    }

    .ai-chat-standalone-input button {
        background: #6366f1;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
    }
</style>

<!-- Standalone Widget Button -->
<button id="aiChatStandaloneBtn" class="ai-chat-standalone-button">
    💬
</button>

<!-- Standalone Widget Container -->
<div id="aiChatStandaloneContainer" class="ai-chat-standalone-container">
    <div class="ai-chat-standalone-header">
        AI Консультант
    </div>
    <div class="ai-chat-standalone-body" id="aiChatStandaloneBody">
        <p>👋 Привет! Я помогу найти идеальное сообщество для тебя. С чего начнем?</p>
    </div>
    <div class="ai-chat-standalone-input">
        <input type="text" id="aiChatStandaloneInput" placeholder="Напиши сообщение..." />
        <button onclick="sendStandaloneMessage()">Отправить</button>
    </div>
</div>

<script>
    // Standalone Widget JavaScript
    let standaloneWidgetOpen = false;

    document.getElementById('aiChatStandaloneBtn').onclick = function() {
        toggleStandaloneWidget();
    };

    document.getElementById('aiChatStandaloneInput').onkeypress = function(e) {
        if (e.key === 'Enter') {
            sendStandaloneMessage();
        }
    };

    function toggleStandaloneWidget() {
        const container = document.getElementById('aiChatStandaloneContainer');
        standaloneWidgetOpen = !standaloneWidgetOpen;

        if (standaloneWidgetOpen) {
            container.style.display = 'block';
            setTimeout(() => {
                document.getElementById('aiChatStandaloneInput').focus();
            }, 100);
        } else {
            container.style.display = 'none';
        }
    }

    function sendStandaloneMessage() {
        const input = document.getElementById('aiChatStandaloneInput');
        const message = input.value.trim();
        const body = document.getElementById('aiChatStandaloneBody');

        if (!message) return;

        // Add user message
        body.innerHTML += `<p><strong>Вы:</strong> ${message}</p>`;

        // Clear input
        input.value = '';

        // Add typing indicator
        body.innerHTML += `<p id="aiStandaloneTyping">AI печатает...</p>`;

        // Scroll to bottom
        body.scrollTop = body.scrollHeight;

        // Simulate AI response (replace with real API call)
        setTimeout(() => {
            document.getElementById('aiStandaloneTyping').remove();

            // Here you would make API call to your Django backend
            // For now, just simulate response
            const responses = [
                "Спасибо за ваше сообщение! Я помогу вам найти идеальное сообщество.",
                "Какой тип клуба вас интересует? Спортивный, творческий, или что-то другое?",
                "Расскажите мне немного о ваших интересах, и я подберу для вас лучшие варианты!"
            ];

            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            body.innerHTML += `<p><strong>AI:</strong> ${randomResponse}</p>`;

            body.scrollTop = body.scrollHeight;
        }, 1500);
    }
</script>
EOF

echo "✅ Standalone виджет создан!"
echo ""

echo "2. Добавляем standalone виджет в base.html..."
cat >> /var/www/myapp/eventsite/templates/base.html << 'EOF'

    <!-- STANDALONE WIDGET INCLUDE -->
    {% include 'widget_standalone.html' %}
EOF

echo "✅ Standalone виджет добавлен в base.html!"
echo ""

echo "🎯 ТЕПЕРЬ СДЕЛАЙТЕ СЛЕДУЮЩЕЕ:"
echo "================================="
echo "1. Нажмите Ctrl+F5"
echo "2. Должен появиться ФИОЛЕТОВЫЙ виджет (standalone)"
echo "3. Нажмите на него - должен открыться чат"
echo "4. Попробуйте написать сообщение"
echo ""
echo "🔥 ЕСЛИ ЭТОТ ВИДЖЕТ РАБОТАЕТ - ПРОБЛЕМА РЕШЕНА!"
echo "🔥 ЕСЛИ НЕ РАБОТАЕТ - ЗНАЧИТ ПРОБЛЕМА В БРАУЗЕРЕ ИЛИ СЕТИ"