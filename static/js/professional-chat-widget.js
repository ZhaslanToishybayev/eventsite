/**
 * 🎨 Professional Chat Widget JavaScript - Premium Implementation
 * 🌟 Ultimate UX/UI with Perfect Design System
 */

(function() {
    'use strict';

    /**
     * 🎨 Professional Chat Widget Class - Perfect UX/UI Implementation
     */
    class ProfessionalChatWidget {
        constructor() {
            this.isOpen = false;
            this.sessionId = 'professional_' + Date.now();
            this.isTyping = false;
            this.messageCount = 0;
            this.typingTimeout = null;
            this.apiEndpoint = '/api/v1/ai/conversational/agent/';
            this.initializeElements();
            this.attachEventListeners();
            this.loadQuickActions();
            this.announceWidgetReady();
            console.log('🎨 ProfessionalChatWidget: Initialization complete');
        }

        /**
         * 🔊 Widget ready announcement for screen readers
         */
        announceWidgetReady() {
            const isSoundEnabled = localStorage.getItem('widget-sound-enabled') === 'true';
            if (window.speechSynthesis && isSoundEnabled) {
                const announcement = new SpeechSynthesisUtterance('AI chat consultant is ready');
                announcement.lang = 'ru-RU';
                setTimeout(() => window.speechSynthesis.speak(announcement), 1500);
            }
        }

        /**
         * 🔍 Initialize DOM elements
         */
        initializeElements() {
            this.btn = document.getElementById('professionalChatWidgetBtn');
            this.chat = document.getElementById('professionalChatWidgetChat');
            this.messages = document.getElementById('professionalChatWidgetMessages');
            this.input = document.getElementById('professionalChatWidgetInput');
            this.sendBtn = document.getElementById('professionalChatWidgetSend');
            this.closeBtn = document.getElementById('professionalChatWidgetClose');
            this.quickActions = document.getElementById('professionalQuickActions');

            if (this.chat) {
                this.chat.setAttribute('aria-expanded', 'false');
                this.chat.setAttribute('aria-hidden', 'true');
                this.chat.setAttribute('role', 'dialog');
                this.chat.setAttribute('aria-label', 'Professional AI chat consultant window');
            }

            if (this.sendBtn) {
                this.sendBtn.disabled = true;
            }
        }

        /**
         * 🎯 Attach event listeners
         */
        attachEventListeners() {
            if (this.btn) {
                this.btn.addEventListener('click', () => this.toggleChat());
                this.btn.addEventListener('keydown', (e) => this.handleButtonKeydown(e));
                this.btn.addEventListener('mouseenter', () => this.preloadResources());
            }

            if (this.closeBtn) {
                this.closeBtn.addEventListener('click', () => this.toggleChat());
            }

            if (this.sendBtn) {
                this.sendBtn.addEventListener('click', () => this.sendMessage());
            }

            if (this.input) {
                this.input.addEventListener('input', () => this.handleInputUpdate());
                this.input.addEventListener('keydown', (e) => this.handleInputKeydown(e));
                this.input.addEventListener('focus', () => this.handleInputFocus());
                this.input.addEventListener('blur', () => this.handleInputBlur());
            }

            // Quick actions
            document.addEventListener('click', (e) => {
                if (e.target.classList.contains('professional-chat-quick-action')) {
                    this.handleQuickAction(e.target.dataset.action);
                }
            });

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.toggleChat();
                }
            });

            this.chat?.addEventListener('transitionend', () => {
                if (this.isOpen && this.input) {
                    this.input.focus();
                }
            });

            // Performance monitoring
            window.addEventListener('beforeunload', () => {
                this.saveSessionData();
            });
        }

        /**
         * 🚀 Preload resources on hover
         */
        preloadResources() {
            if ('connection' in navigator) {
                this.testConnection();
            }
        }

        /**
         * 🔗 Test connection to AI agent
         */
        async testConnection() {
            try {
                const response = await fetch(this.apiEndpoint, {
                    method: 'OPTIONS',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                console.log('🎨 ProfessionalChatWidget: Connection test successful');
            } catch (error) {
                console.warn('🎨 ProfessionalChatWidget: Connection test failed', error);
            }
        }

        /**
         * ⌨️ Handle button keyboard events
         */
        handleButtonKeydown(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.toggleChat();
            }
        }

        /**
         * 📝 Handle input updates
         */
        handleInputUpdate() {
            const hasText = this.input && this.input.value.trim().length > 0;
            if (this.sendBtn) {
                this.sendBtn.disabled = !hasText;
            }
        }

        /**
         * ⌨️ Handle input keyboard events
         */
        handleInputKeydown(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        }

        /**
         * 🎯 Handle input focus
         */
        handleInputFocus() {
            if (this.input) {
                this.input.style.boxShadow = '0 0 0 3px rgba(20, 180, 166, 0.15)';
            }
        }

        /**
         * 🎯 Handle input blur
         */
        handleInputBlur() {
            if (this.input) {
                this.input.style.boxShadow = 'none';
            }
        }

        /**
         * 🎯 Handle quick action click
         */
        handleQuickAction(action) {
            let message = '';
            switch (action) {
                case 'create':
                    message = 'Хочу создать клуб';
                    break;
                case 'find':
                    message = 'Покажи существующие клубы';
                    break;
                case 'help':
                    message = 'Помощь';
                    break;
            }

            if (this.input) {
                this.input.value = message;
                this.sendMessage();
            }
        }

        /**
         * 🎭 Toggle chat window
         */
        toggleChat() {
            this.isOpen = !this.isOpen;

            if (this.chat) {
                this.chat.setAttribute('aria-expanded', this.isOpen);
                this.chat.setAttribute('aria-hidden', !this.isOpen);
            }

            if (this.isOpen) {
                this.chat.classList.add('show');
                this.loadQuickActions();
                this.btn?.setAttribute('aria-pressed', 'true');
                console.log('🎨 ProfessionalChatWidget: Chat opened');
            } else {
                this.chat.classList.remove('show');
                this.btn?.setAttribute('aria-pressed', 'false');
                console.log('🎨 ProfessionalChatWidget: Chat closed');
            }
        }

        /**
         * 💬 Add typing indicator
         */
        addTypingIndicator() {
            if (!this.messages) return;

            this.removeTypingIndicator();

            const typingDiv = document.createElement('div');
            typingDiv.className = 'typing-indicator';
            typingDiv.id = 'typingIndicator';
            typingDiv.setAttribute('aria-label', 'AI is typing');
            typingDiv.setAttribute('role', 'status');

            typingDiv.innerHTML = `
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                Печатает...
            `;

            this.messages.appendChild(typingDiv);
            this.scrollToBottom();

            this.typingTimeout = setTimeout(() => {
                this.removeTypingIndicator();
                this.addMessage('Кажется, у меня временные трудности с ответом. Попробуйте задать вопрос немного иначе!', 'ai');
            }, 10000);
        }

        /**
         * 💬 Remove typing indicator
         */
        removeTypingIndicator() {
            if (this.typingTimeout) {
                clearTimeout(this.typingTimeout);
                this.typingTimeout = null;
            }

            const typingIndicator = document.getElementById('typingIndicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }

        /**
         * 💬 Add quick actions
         */
        addQuickActions() {
            if (!this.quickActions) return;
            this.quickActions.classList.add('show');
        }

        /**
         * 🗑️ Remove quick actions
         */
        removeQuickActions() {
            if (!this.quickActions) return;
            this.quickActions.classList.remove('show');
        }

        /**
         * 📚 Load quick actions with delay
         */
        loadQuickActions() {
            setTimeout(() => {
                this.addQuickActions();
            }, 400);
        }

        /**
         * 📝 Send message
         */
        sendMessage() {
            if (!this.input) return;
            const message = this.input.value.trim();
            if (!message) return;

            this.input.value = '';
            this.handleInputUpdate();

            // Remove quick actions after first message
            this.removeQuickActions();

            // Add user message
            this.addMessage(message, 'user');

            // Send to AI
            setTimeout(() => {
                this.sendToAI(message);
            }, 200);
        }

        /**
         * 💬 Add message to chat
         */
        addMessage(text, sender) {
            if (!this.messages) return;

            const messageDiv = document.createElement('div');
            messageDiv.className = `professional-chat-widget-message ${sender}`;
            messageDiv.setAttribute('role', 'listitem');
            messageDiv.setAttribute('data-sender', sender);

            const formattedText = this.sanitizeHTML(text).replace(/\n/g, '<br>');
            messageDiv.innerHTML = formattedText;

            this.messageCount++;
            messageDiv.style.animationDelay = `${Math.min(this.messageCount * 0.08, 0.4)}s`;
            this.messages.appendChild(messageDiv);
            this.scrollToBottom();

            if (sender === 'ai') {
                this.announceMessage(text);
            }
        }

        /**
         * 🔊 Announce message for screen readers
         */
        announceMessage(text) {
            const isSoundEnabled = localStorage.getItem('widget-sound-enabled') === 'true';
            if (window.speechSynthesis && isSoundEnabled) {
                const announcement = new SpeechSynthesisUtterance(`Message from AI: ${text}`);
                announcement.lang = 'ru-RU';
                setTimeout(() => window.speechSynthesis.speak(announcement), 200);
            }
        }

        /**
         * 🛡️ Sanitize HTML content
         */
        sanitizeHTML(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        /**
         * 🤖 Send message to AI agent
         */
        async sendToAI(message) {
            this.addTypingIndicator();
            this.isTyping = true;

            try {
                const response = await fetch(this.apiEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({
                        message: message,
                        session_id: this.sessionId
                    })
                });

                const result = await response.json();
                this.removeTypingIndicator();
                this.isTyping = false;

                if (result.success) {
                    this.addMessage(result.response, 'ai');

                    if (result.quick_replies && result.quick_replies.length > 0) {
                        // Можно добавить дополнительные действия при необходимости
                    }

                    if (result.state === 'completed' || result.action === 'close_chat') {
                        setTimeout(() => {
                            this.addMessage('🎉 Отлично! Ваш клуб успешно создан! Спасибо за использование AI консультанта! 🎊', 'ai');
                            setTimeout(() => this.toggleChat(), 5000);
                        }, 1000);
                    }
                } else {
                    this.addMessage('😔 Ой, что-то пошло не так... Попробуйте еще раз или скажите "помощь" если нужна помощь! 🤗', 'ai');
                }

            } catch (error) {
                this.removeTypingIndicator();
                this.isTyping = false;
                console.error('ProfessionalChatWidget Error:', error);
                this.handleAIError(error);
            }

            this.enableInput();
            this.input?.focus();
        }

        /**
         * 🔄 Handle AI errors
         */
        handleAIError(error) {
            const errorMessage = error.message || 'Connection error';
            let userMessage = '❌ Ошибка соединения. Проверьте интернет и попробуйте снова!';

            if (errorMessage.includes('timeout')) {
                userMessage = '⏰ Время ожидания ответа истекло. Попробуйте еще раз!';
            } else if (errorMessage.includes('404')) {
                userMessage = '🔍 Сервис временно недоступен. Попробуйте через несколько минут!';
            } else if (errorMessage.includes('500')) {
                userMessage = '💥 Сервер временно перегружен. Попробуйте через минуту!';
            }

            this.addMessage(userMessage, 'ai');
        }

        /**
         * 🔌 Enable input fields
         */
        enableInput() {
            if (this.input) {
                this.input.disabled = false;
            }
            if (this.sendBtn) {
                this.sendBtn.disabled = !this.input?.value.trim();
            }
        }

        /**
         * 🍃 Smooth scroll to bottom
         */
        scrollToBottom() {
            if (!this.messages) return;

            try {
                this.messages.scrollTo({
                    top: this.messages.scrollHeight,
                    behavior: 'smooth'
                });
            } catch (e) {
                this.messages.scrollTop = this.messages.scrollHeight;
            }
        }

        /**
         * 🔑 Get CSRF token
         */
        getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                   document.querySelector('meta[name=csrf-token]')?.getAttribute('content') ||
                   document.querySelector('#csrf-token')?.value ||
                   '';
        }

        /**
         * 💾 Save session data
         */
        saveSessionData() {
            const sessionData = {
                sessionId: this.sessionId,
                messageCount: this.messageCount,
                timestamp: Date.now()
            };
            localStorage.setItem('widget-session-data', JSON.stringify(sessionData));
        }

        /**
         * 🎯 Reset widget state
         */
        reset() {
            this.isOpen = false;
            this.sessionId = 'professional_' + Date.now();
            this.isTyping = false;
            this.messageCount = 0;

            if (this.chat) {
                this.chat.classList.remove('show');
                this.chat.setAttribute('aria-expanded', 'false');
                this.chat.setAttribute('aria-hidden', 'true');
            }

            if (this.btn) {
                this.btn.setAttribute('aria-pressed', 'false');
            }

            this.removeTypingIndicator();
            this.removeQuickActions();

            if (this.messages) {
                this.messages.innerHTML = `
                    <div class="professional-chat-widget-message ai">
                        <strong>🚀 Добро пожаловать!</strong><br>
                        Я - ваш профессиональный AI консультант по созданию фан-клубов и сообществ.<br><br>
                        <em>💡 Просто скажите, что вас интересует:</em>
                    </div>
                    <div class="professional-chat-quick-actions" id="professionalQuickActions">
                        <div class="professional-chat-quick-action" data-action="create">➕ Создать клуб</div>
                        <div class="professional-chat-quick-action" data-action="find">🔍 Найти клубы</div>
                        <div class="professional-chat-quick-action" data-action="help">❓ Помощь</div>
                    </div>
                `;
            }

            this.loadQuickActions();
        }
    }

    /**
     * 🚀 Initialize Professional Chat Widget
     */
    function initializeProfessionalWidget() {
        console.log('🎨 ProfessionalChatWidget: DOM loaded, initializing...');

        // Check for existing widget instance
        if (window.professionalChatWidget) {
            console.warn('🎨 ProfessionalChatWidget: Instance already exists, destroying old instance');
            window.professionalChatWidget.reset();
        }

        // Create new widget instance
        window.professionalChatWidget = new ProfessionalChatWidget();
        console.log('✅ ProfessionalChatWidget: Ready for action!');

        // Add debug information
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.group('🎨 ProfessionalChatWidget Debug Info');
            console.log('Widget instance:', window.professionalChatWidget);
            console.log('API endpoint:', window.professionalChatWidget.apiEndpoint);
            const sessionData = localStorage.getItem('widget-session-data');
            if (sessionData) {
                console.log('Previous session data:', JSON.parse(sessionData));
            }
            console.groupEnd();
        }
    }

    /**
     * 🎯 Initialize when DOM is ready
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeProfessionalWidget);
    } else {
        initializeProfessionalWidget();
    }

    /**
     * 🎯 Expose debug methods globally
     */
    window.professionalChatWidgetDebug = {
        resetWidget: () => window.professionalChatWidget?.reset(),
        toggleWidget: () => window.professionalChatWidget?.toggleChat(),
        testConnection: () => window.professionalChatWidget?.testConnection()
    };

})();