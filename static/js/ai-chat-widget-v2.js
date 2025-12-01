/**
 * 🤖 AI Consultant Chat Widget - PREMIUM VERSION v2.1
 * Glassmorphism Design + Markdown Support + Smooth Animations
 */

class AIChatWidget {
    constructor(options = {}) {
        this.options = {
            apiUrl: '/api/ai/chat/',
            widgetTitle: 'AI Консультант',
            welcomeMessage: '👋 Привет! Я помогу найти идеальное сообщество для тебя. С чего начнем?',
            placeholder: 'Напиши сообщение...',
            ...options
        };

        this.isOpen = false;
        this.isTyping = false;
        this.currentSessionId = 'simple_session_123'; // Use fixed session ID for simple API
        this.currentTheme = 'light';

        this.init();
    }

    async init() {
        await this.loadDependencies();
        this.detectTheme();
        this.createWidget();
        this.attachEvents();
        this.checkAuth();
    }

    async loadDependencies() {
        // Load Marked.js for Markdown rendering
        if (!window.marked) {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
            document.head.appendChild(script);
            await new Promise(resolve => script.onload = resolve);
        }
    }

    createWidget() {
        const html = `
            <div class="ai-chat-widget ${this.currentTheme}-theme" id="ai-chat-widget">
                <button class="ai-chat-button" id="chatToggleBtn">
                    <span class="ai-btn-icon">✨</span>
                </button>

                <div class="ai-chat-container" id="chatContainer">
                    <!-- Header -->
                    <div class="ai-chat-header">
                        <div class="ai-header-info">
                            <div class="ai-avatar-bot">🤖</div>
                            <div class="ai-header-text">
                                <h3>${this.options.widgetTitle}</h3>
                                <div class="ai-chat-status">
                                    <span class="ai-status-dot"></span>
                                    Online
                                </div>
                            </div>
                        </div>
                        <div class="ai-controls">
                            <button class="ai-control-btn" id="aiThemeBtn">🌙</button>
                            <button class="ai-control-btn ai-close-btn" id="aiCloseBtn">✕</button>
                        </div>
                    </div>

                    <!-- Messages -->
                    <div class="ai-chat-messages" id="chatMessages">
                        <div class="ai-message assistant">
                            <div class="ai-message-row">
                                <div class="ai-message-avatar">🤖</div>
                                <div class="ai-message-content">
                                    ${this.renderMarkdown(this.options.welcomeMessage)}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Typing Indicator -->
                    <div class="ai-typing" id="chatTyping" style="display: none;">
                        <div class="ai-typing-dot"></div>
                        <div class="ai-typing-dot"></div>
                        <div class="ai-typing-dot"></div>
                    </div>

                    <!-- Input -->
                    <div class="ai-chat-input-container">
                        <div class="ai-input-wrapper" id="chatInputWrapper">
                            <textarea
                                class="ai-chat-input"
                                id="chatInput"
                                placeholder="${this.options.placeholder}"
                                rows="1"
                            ></textarea>
                            <button class="ai-send-btn" id="chatSendBtn">➤</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', html);
    }

    attachEvents() {
        const toggleBtn = document.getElementById('chatToggleBtn');
        const closeBtn = document.getElementById('aiCloseBtn');
        const sendBtn = document.getElementById('chatSendBtn');
        const input = document.getElementById('chatInput');
        const themeBtn = document.getElementById('aiThemeBtn');
        const wrapper = document.getElementById('chatInputWrapper');

        toggleBtn.onclick = () => this.toggleChat();
        closeBtn.onclick = () => this.closeChat();
        themeBtn.onclick = () => this.toggleTheme();

        sendBtn.onclick = () => this.sendMessage();

        input.onkeydown = (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
            // Auto-resize
            input.style.height = 'auto';
            input.style.height = input.scrollHeight + 'px';
        };

        input.oninput = () => {
            if (input.value.trim()) {
                wrapper.classList.add('has-text');
            } else {
                wrapper.classList.remove('has-text');
            }
        };
    }

    toggleChat() {
        const container = document.getElementById('chatContainer');
        this.isOpen = !this.isOpen;

        if (this.isOpen) {
            container.classList.add('active');
            setTimeout(() => document.getElementById('chatInput').focus(), 300);
        } else {
            container.classList.remove('active');
        }
    }

    closeChat() {
        this.isOpen = false;
        document.getElementById('chatContainer').classList.remove('active');
    }

    async sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        if (!message || this.isTyping) return;

        // Clear input
        input.value = '';
        input.style.height = 'auto';
        document.getElementById('chatInputWrapper').classList.remove('has-text');

        // Add User Message
        this.addMessage(message, 'user');

        // Show Typing
        this.isTyping = true;
        document.getElementById('chatTyping').style.display = 'flex';
        this.scrollToBottom();

        try {
            // Special handling for club creation requests
            const lowerMessage = message.toLowerCase();
            if (lowerMessage.includes('создать клуб') || lowerMessage.includes('создай клуб') ||
                lowerMessage.includes('хочу создать') || lowerMessage.includes('создание клуба')) {

                // Return a helpful response for club creation
                this.isTyping = false;
                document.getElementById('chatTyping').style.display = 'none';
                this.addMessage("🎉 Отлично! Давайте создадим новый клуб!\n\n📋 Для создания клуба вам нужно:\n1. Перейти в раздел \"Создавайте сообщества\"\n2. Заполнить форму с информацией о клубе\n3. Добавить описание, фото и контакты\n\n🔗 Ссылка для создания: " + window.location.origin + "/clubs/create/\n\n💡 Вам помочь с идеями для названия или описания клуба?", 'assistant');
                return;
            }

            // Special handling for club search requests
            if (lowerMessage.includes('найти клуб') || lowerMessage.includes('поиск клуб') ||
                lowerMessage.includes('поищ') || lowerMessage.includes('клубы') ||
                lowerMessage.includes('сообщества')) {

                // Return a helpful response for club search
                this.isTyping = false;
                document.getElementById('chatTyping').style.display = 'none';
                this.addMessage("🔍 Отлично! Давайте найдем подходящий клуб!\n\n📋 Вы можете:\n1. Перейти в раздел \"Вступайте в сообщества\"\n2. Использовать фильтры по интересам и городам\n3. Посмотреть ТОП 16 клубов на главной странице\n\n🔗 Ссылка для поиска: " + window.location.origin + "/clubs/\n\n💡 Расскажите, что вас интересует, и я помогу подобрать подходящие клубы!", 'assistant');
                return;
            }

            // Send message to simple chat endpoint
            const response = await this.api('', 'POST', {
                message,
                session_id: this.currentSessionId
            });

            // Hide Typing
            document.getElementById('chatTyping').style.display = 'none';
            this.isTyping = false;

            // Handle response - our simple API returns 'response' field
            if (response.response) {
                this.addMessage(response.response, 'assistant');
            } else if (response.error) {
                this.addMessage('⚠️ Ошибка: ' + (response.details || response.error), 'assistant');
            } else {
                this.addMessage('⚠️ Неожиданный формат ответа', 'assistant');
            }

        } catch (e) {
            console.error('Chat error:', e);
            document.getElementById('chatTyping').style.display = 'none';
            this.isTyping = false;
            this.addMessage('⚠️ Ошибка соединения. Попробуйте позже.', 'assistant');
        }
    }

    addMessage(text, role) {
        const container = document.getElementById('chatMessages');
        const avatar = role === 'user' ? '👤' : '🤖';

        const div = document.createElement('div');
        div.className = `ai-message ${role}`;
        div.innerHTML = `
            <div class="ai-message-row">
                <div class="ai-message-avatar">${avatar}</div>
                <div class="ai-message-content">
                    ${this.renderMarkdown(text)}
                </div>
            </div>
        `;

        container.appendChild(div);
        this.scrollToBottom();
    }

    renderMarkdown(text) {
        if (window.marked) {
            return window.marked.parse(text);
        }
        // Fallback
        return text.replace(/\n/g, '<br>');
    }

    scrollToBottom() {
        const messages = document.getElementById('chatMessages');
        setTimeout(() => {
            messages.scrollTop = messages.scrollHeight;
        }, 50);
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        document.getElementById('ai-chat-widget').className = `ai-chat-widget ${this.currentTheme}-theme`;
        localStorage.setItem('ai_theme', this.currentTheme);
    }

    detectTheme() {
        const saved = localStorage.getItem('ai_theme');
        if (saved) {
            this.currentTheme = saved;
        } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.currentTheme = 'dark';
        }
    }

    async api(endpoint, method = 'GET', data = null) {
        try {
            const headers = {
                'Content-Type': 'application/json'
            };
            const options = { method, headers };
            if (data) options.body = JSON.stringify(data);

            const res = await fetch(this.options.apiUrl + endpoint, options);
            const json = await res.json();

            // Debug logging
            console.log('API Response:', json);
            console.log('Response has response field:', !!json.response);
            console.log('Response has error field:', !!json.error);

            // If there's an error in the response, check if it's the OpenAI error
            if (json.error && typeof json.details === 'string') {
                const errorMsg = json.details.toLowerCase();
                if (errorMsg.includes('empty') || errorMsg.includes('must contain either')) {
                    // Return a friendly fallback response
                    return {
                        response: "Привет! 👋 Я AI-консультант платформы ЦЕНТР СОБЫТИЙ.\n\nЯ могу помочь вам:\n🔍 Найти интересные клубы и сообщества\n📚 Узнать о функциях платформы\n🎯 Развивать свои навыки\n\nЧем могу помочь?",
                        session_id: json.session_id || this.currentSessionId
                    };
                }
            }

            return json;
        } catch (error) {
            console.error('API Error:', error);
            // Return a fallback response instead of throwing
            return {
                response: "Извините, произошла ошибка. Попробуйте еще раз.",
                error: true
            };
        }
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    checkAuth() {
        // Optional: Check if user is logged in to personalize welcome message
    }
}

// Global compatibility functions
window.initAIChatWidgetV2 = function(options = {}) {
    const widget = new AIChatWidget(options);
    window.aiChat = widget; // Сохраняем ссылку
    return widget;
};

window.aiChatWidgetV2 = {
    createWidget: (options = {}) => {
        const widget = new AIChatWidget(options);
        window.aiChat = widget; // Сохраняем ссылку
        return widget;
    },
    toggleChat: () => {
        if (window.aiChat) {
            window.aiChat.toggleChat();
        }
    }
};

// Автоматическая инициализация отключена, чтобы избежать конфликтов
// Инициализация происходит в HTML шаблоне