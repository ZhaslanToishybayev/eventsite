/**
 * 🤖 AI Consultant Chat Widget - STANDALONE VERSION v2.8
 * No external dependencies - guaranteed to work!
 */

class AIChatWidgetStandalone {
    constructor(options = {}) {
        this.options = {
            apiUrl: '/api/v1/ai/simplified/interactive/chat/',
            widgetTitle: 'AI Консультант',
            welcomeMessage: '👋 Привет! Я помогу найти идеальное сообщество для тебя. С чего начнем?',
            placeholder: 'Напиши сообщение...',
            ...options
        };

        this.isOpen = false;
        this.isTyping = false;
        this.currentStateId = null;  // Используем state_id вместо session_id
        this.currentTheme = 'light';

        // Simple markdown parser (no external dependency)
        this.markdownRules = {
            '**': (text) => `<strong>${text}</strong>`,
            '*': (text) => `<em>${text}</em>`,
            '`': (text) => `<code>${text}</code>`,
            '\n': () => '<br>'
        };

        this.init();
    }

    async init() {
        this.detectTheme();
        this.createWidget();
        this.attachEvents();
        this.checkAuth();
    }

    createWidget() {
        const html = `
            <div class="ai-chat-widget ${this.currentTheme}-theme" id="ai-chat-widget-standalone">
                <button class="ai-chat-button" id="chatToggleBtnStandalone">
                    <span class="ai-btn-icon">✨</span>
                </button>

                <div class="ai-chat-container" id="chatContainerStandalone">
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
                            <button class="ai-control-btn" id="aiThemeBtnStandalone">🌙</button>
                            <button class="ai-control-btn ai-close-btn" id="aiCloseBtnStandalone">✕</button>
                        </div>
                    </div>

                    <!-- Messages -->
                    <div class="ai-chat-messages" id="chatMessagesStandalone">
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
                    <div class="ai-typing" id="chatTypingStandalone" style="display: none;">
                        <div class="ai-typing-dot"></div>
                        <div class="ai-typing-dot"></div>
                        <div class="ai-typing-dot"></div>
                    </div>

                    <!-- Input -->
                    <div class="ai-chat-input-container">
                        <div class="ai-input-wrapper" id="chatInputWrapperStandalone">
                            <textarea
                                class="ai-chat-input"
                                id="chatInputStandalone"
                                placeholder="${this.options.placeholder}"
                                rows="1"
                            ></textarea>
                            <button class="ai-send-btn" id="chatSendBtnStandalone">➤</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', html);
    }

    attachEvents() {
        const toggleBtn = document.getElementById('chatToggleBtnStandalone');
        const closeBtn = document.getElementById('aiCloseBtnStandalone');
        const sendBtn = document.getElementById('chatSendBtnStandalone');
        const input = document.getElementById('chatInputStandalone');
        const themeBtn = document.getElementById('aiThemeBtnStandalone');
        const wrapper = document.getElementById('chatInputWrapperStandalone');

        if (toggleBtn) toggleBtn.onclick = () => this.toggleChat();
        if (closeBtn) closeBtn.onclick = () => this.closeChat();
        if (themeBtn) themeBtn.onclick = () => this.toggleTheme();
        if (sendBtn) sendBtn.onclick = () => this.sendMessage();

        if (input) {
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
    }

    toggleChat() {
        const container = document.getElementById('chatContainerStandalone');
        this.isOpen = !this.isOpen;

        if (this.isOpen) {
            if (container) container.classList.add('active');
            setTimeout(() => {
                const input = document.getElementById('chatInputStandalone');
                if (input) input.focus();
            }, 300);
        } else {
            if (container) container.classList.remove('active');
        }
    }

    closeChat() {
        this.isOpen = false;
        const container = document.getElementById('chatContainerStandalone');
        if (container) container.classList.remove('active');
    }

    async sendMessage() {
        const input = document.getElementById('chatInputStandalone');
        if (!input) return;

        const message = input.value.trim();
        if (!message || this.isTyping) return;

        // Clear input
        input.value = '';
        input.style.height = 'auto';
        const wrapper = document.getElementById('chatInputWrapperStandalone');
        if (wrapper) wrapper.classList.remove('has-text');

        // Add User Message
        this.addMessage(message, 'user');

        // Show Typing
        this.isTyping = true;
        const typingElement = document.getElementById('chatTypingStandalone');
        if (typingElement) typingElement.style.display = 'flex';
        this.scrollToBottom();

        try {
            // Send to simplified interactive endpoint (без сессий)
            const response = await fetch(this.options.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    message,
                    user_email: this.getUserEmail(),
                    state_id: this.currentStateId  // Send current state ID
                })
            });

            const json = await response.json();

            // Hide Typing
            if (typingElement) typingElement.style.display = 'none';
            this.isTyping = false;

            // Handle response
            if (json.message) {
                this.addMessage(json.message, 'assistant');
                // Update state ID if provided
                if (json.state_id) {
                    this.currentStateId = json.state_id;
                }
            } else if (json.error) {
                this.addMessage('⚠️ Ошибка: ' + (json.details || json.error), 'assistant');
            } else {
                this.addMessage('⚠️ Неожиданный формат ответа', 'assistant');
            }
        } catch (e) {
            console.error('Chat error:', e);
            if (typingElement) typingElement.style.display = 'none';
            this.isTyping = false;
            this.addMessage('⚠️ Ошибка соединения. Попробуйте позже.', 'assistant');
        }
    }

    addMessage(text, role) {
        const container = document.getElementById('chatMessagesStandalone');
        if (!container) return;

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
        // Simple markdown parser without external dependencies
        let rendered = text;

        // Bold text
        rendered = rendered.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Italic text
        rendered = rendered.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Inline code
        rendered = rendered.replace(/`(.*?)`/g, '<code>$1</code>');

        // Line breaks
        rendered = rendered.replace(/\n/g, '<br>');

        // Links
        rendered = rendered.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');

        return rendered;
    }

    scrollToBottom() {
        const messages = document.getElementById('chatMessagesStandalone');
        if (messages) {
            setTimeout(() => {
                messages.scrollTop = messages.scrollHeight;
            }, 50);
        }
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        const widget = document.getElementById('ai-chat-widget-standalone');
        if (widget) {
            widget.className = `ai-chat-widget ${this.currentTheme}-theme`;
        }
        localStorage.setItem('ai_theme_standalone', this.currentTheme);
    }

    detectTheme() {
        const saved = localStorage.getItem('ai_theme_standalone');
        if (saved) {
            this.currentTheme = saved;
        } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.currentTheme = 'dark';
        }
    }

    async api(endpoint, method = 'GET', data = null) {
        try {
            const headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            };
            const options = { method, headers };
            if (data) options.body = JSON.stringify(data);

            const res = await fetch(this.options.apiUrl + endpoint, options);
            const json = await res.json();

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

    getUserEmail() {
        // Try to get user email from various sources
        // 1. From a data attribute on the body
        const bodyEmail = document.body.getAttribute('data-user-email');
        if (bodyEmail) return bodyEmail;

        // 2. From a meta tag
        const metaEmail = document.querySelector('meta[name="user-email"]');
        if (metaEmail) return metaEmail.getAttribute('content');

        // 3. From a hidden input field
        const emailInput = document.querySelector('input[name="user_email"]');
        if (emailInput) return emailInput.value;

        // 4. Return null if no email found
        return null;
    }

    checkAuth() {
        // Optional: Check if user is logged in to personalize welcome message
    }
}

// Global functions
window.initAIChatWidgetStandalone = function(options = {}) {
    const widget = new AIChatWidgetStandalone(options);
    window.aiChatStandalone = widget;
    return widget;
};

// Auto-create if needed
if (typeof window.forceCreateStandaloneWidget !== 'undefined') {
    window.initAIChatWidgetStandalone();
}