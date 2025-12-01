/**
 * 🤖 AI Consultant Chat Widget - HTTPS VERSION v2.1
 * Fixed for HTTPS/SSL compatibility
 */

class AIChatWidget {
    constructor(options = {}) {
        this.options = {
            apiUrl: window.location.protocol + '//' + window.location.host + '/api/v1/ai/production/agent/',
            widgetTitle: 'AI Консультант',
            welcomeMessage: '👋 Привет! Я помогу найти идеальное сообщество для тебя. С чего начнем?',
            placeholder: 'Напиши сообщение...',
            ...options
        };

        this.isOpen = false;
        this.isTyping = false;
        this.currentSessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
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
                    <span class="ai-btn-icon">🤖</span>
                </button>

                <div class="ai-chat-container" id="chatContainer">
                    <!-- Header -->
                    <div class="ai-chat-header">
                        <div class="ai-chat-title">${this.options.widgetTitle}</div>
                        <button class="ai-chat-close" id="chatCloseBtn">×</button>
                    </div>

                    <!-- Messages -->
                    <div class="ai-chat-messages" id="chatMessages">
                        <div class="ai-message ai-message-bot">
                            <div class="ai-avatar">🤖</div>
                            <div class="ai-message-content">
                                <div class="typing-dots">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Input -->
                    <div class="ai-chat-input-container">
                        <div class="ai-quick-replies" id="quickReplies"></div>
                        <div class="ai-chat-input-wrapper">
                            <textarea
                                class="ai-chat-input"
                                id="chatInput"
                                placeholder="${this.options.placeholder}"
                                rows="1"
                                maxlength="500"
                            ></textarea>
                            <button class="ai-chat-send" id="chatSendBtn">
                                <span>➤</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', html);
        this.widgetElement = document.getElementById('ai-chat-widget');
    }

    attachEvents() {
        const toggleBtn = document.getElementById('chatToggleBtn');
        const closeBtn = document.getElementById('chatCloseBtn');
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('chatSendBtn');
        const messagesContainer = document.getElementById('chatMessages');

        // Toggle widget
        toggleBtn.addEventListener('click', () => this.toggle());

        // Close widget
        closeBtn.addEventListener('click', () => this.close());

        // Send message
        const sendMessage = () => {
            const message = chatInput.value.trim();
            if (message && !this.isTyping) {
                this.sendMessage(message);
                chatInput.value = '';
            }
        };

        sendBtn.addEventListener('click', sendMessage);
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Auto-resize textarea
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = (chatInput.scrollHeight) + 'px';
        });

        // Quick replies
        messagesContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('ai-quick-reply')) {
                const text = e.target.textContent;
                this.sendMessage(text);
            }
        });
    }

    async sendMessage(message) {
        if (this.isTyping) return;

        this.isTyping = true;

        // Add user message
        this.addMessage(message, 'user');

        // Clear quick replies
        document.getElementById('quickReplies').innerHTML = '';

        try {
            const response = await fetch(this.options.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                                   document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.currentSessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                this.addMessage(data.response, 'bot');
                this.handleQuickReplies(data.quick_replies);
                this.currentSessionId = data.session_id || this.currentSessionId;
            } else {
                this.addMessage('Извините, произошла ошибка. Пожалуйста, попробуйте позже.', 'bot');
            }

        } catch (error) {
            console.error('Widget error:', error);
            this.addMessage('Извините, сервис временно недоступен. Пожалуйста, попробуйте позже.', 'bot');
        }

        this.isTyping = false;
    }

    addMessage(content, sender) {
        const messagesContainer = document.getElementById('chatMessages');
        const isBot = sender === 'bot';

        // Remove typing indicator if exists
        const typingIndicator = messagesContainer.querySelector('.typing-dots');
        if (typingIndicator) {
            typingIndicator.closest('.ai-message').remove();
        }

        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `ai-message ai-message-${sender}`;

        if (isBot) {
            messageDiv.innerHTML = `
                <div class="ai-avatar">🤖</div>
                <div class="ai-message-content">${this.renderMarkdown(content)}</div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="ai-message-content">${this.escapeHtml(content)}</div>
                <div class="ai-avatar user-avatar">👤</div>
            `;
        }

        messagesContainer.appendChild(messageDiv);

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Auto-open widget for bot responses
        if (isBot && !this.isOpen) {
            this.open();
        }
    }

    renderMarkdown(text) {
        if (typeof marked === 'undefined') {
            return this.escapeHtml(text);
        }

        // Configure marked
        marked.setOptions({
            breaks: true,
            gfm: true
        });

        return marked(text);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    handleQuickReplies(quickReplies) {
        if (!quickReplies || !Array.isArray(quickReplies) || quickReplies.length === 0) return;

        const quickRepliesContainer = document.getElementById('quickReplies');
        quickRepliesContainer.innerHTML = '';

        quickReplies.forEach(reply => {
            const button = document.createElement('button');
            button.className = 'ai-quick-reply';
            button.textContent = reply;
            quickRepliesContainer.appendChild(button);
        });
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        if (this.isOpen) return;

        this.isOpen = true;
        this.widgetElement.classList.add('open');

        // Remove initial typing indicator
        const typingIndicator = document.getElementById('chatMessages').querySelector('.typing-dots');
        if (typingIndicator) {
            typingIndicator.closest('.ai-message').remove();
        }

        // Send welcome message if no messages yet
        const messages = document.getElementById('chatMessages').querySelectorAll('.ai-message-bot');
        if (messages.length === 0) {
            setTimeout(() => {
                this.addMessage(this.options.welcomeMessage, 'bot');
            }, 1000);
        }
    }

    close() {
        if (!this.isOpen) return;

        this.isOpen = false;
        this.widgetElement.classList.remove('open');
    }

    detectTheme() {
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.currentTheme = prefersDark ? 'dark' : 'light';
    }

    checkAuth() {
        // Check if user is authenticated and adjust behavior accordingly
        // This is a placeholder for authentication logic
    }
}

// Global initialization function
function initAIChatWidgetV2(options = {}) {
    console.log('🤖 Инициализация AI Chat Widget v2...');
    try {
        const widget = new AIChatWidget(options);
        console.log('✅ AI Chat Widget v2 инициализирован успешно');
        return widget;
    } catch (error) {
        console.error('❌ Ошибка инициализации AI Chat Widget v2:', error);
        throw error;
    }
}

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🤖 DOM загружен, инициализация виджета...');
    if (typeof initAIChatWidgetV2 === 'function') {
        try {
            const widget = initAIChatWidgetV2();
            console.log('✅ Виджет инициализирован успешно:', widget);
        } catch (error) {
            console.error('❌ Ошибка инициализации виджета:', error);
        }
    } else {
        console.error('❌ Функция initAIChatWidgetV2 не найдена');
    }
});

// Fallback initialization
if (document.readyState === 'loading') {
    // Loading hasn't finished yet
} else {
    // Document is fully loaded, initialize immediately
    if (typeof initAIChatWidgetV2 === 'function') {
        try {
            const widget = initAIChatWidgetV2();
            console.log('✅ Виджет инициализирован успешно (fallback):', widget);
        } catch (error) {
            console.error('❌ Ошибка инициализации виджета (fallback):', error);
        }
    }
}