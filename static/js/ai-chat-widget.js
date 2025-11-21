/**
 * 🤖 AI Consultant Chat Widget - УЛУЧШЕННАЯ ВЕРСИЯ v2.0
 * Современный виджет чата с ИИ-консультантом для "ЦЕНТР СОБЫТИЙ"
 */

class AIChatWidget {
    constructor(options = {}) {
        this.options = {
            apiUrl: '/api/v1/ai/',
            widgetTitle: '🤖 AI Консультант',
            platformName: 'ЦЕНТР СОБЫТИЙ',
            welcomeMessage: '👋 Привет! Я твой помощник в мире сообществ. Чем могу помочь?',
            placeholder: 'Напиши свой вопрос...',
            typingDelay: 800,
            maxMessages: 100,
            autoScroll: true,
            soundEnabled: false,
            ...options
        };

        // Состояние виджета
        this.isOpen = false;
        this.isMinimized = false;
        this.isTyping = false;
        this.currentSessionId = null;
        this.messages = [];
        this.currentTheme = 'light';

        // Подсказки и команды
        this.selectedSuggestionIndex = -1;
        this.currentSuggestions = [];
        this.commandHistory = [];
        this.historyIndex = -1;

        // Аналитика
        this.stats = {
            messagesCount: 0,
            sessionsCount: 0,
            startTime: Date.now(),
            lastActivity: Date.now()
        };

        // Быстрые команды
        this.quickCommands = [
            { command: '/clubs', description: 'Найти сообщества', icon: '🏠' },
            { command: '/help', description: 'Помощь', icon: '❓' },
            { command: '/events', description: 'Мероприятия', icon: '📅' },
            { command: '/mentor', description: 'Развитие', icon: '🎓' }
        ];

        this.init();
    }

    async init() {
        this.detectPreferredTheme();
        this.createWidget();
        this.attachEventListeners();
        this.setupKeyboardShortcuts();

        if (this.isUserAuthenticated()) {
            await this.loadOrCreateSession();
        }

        await this.checkFirstVisit();
    }

    isUserAuthenticated() {
        return document.querySelector('[name=csrfmiddlewaretoken]') ||
            document.querySelector('meta[name="csrf-token"]');
    }

    createWidget() {
        const widgetHTML = `
            <div class="ai-chat-widget ${this.currentTheme}-theme" id="aiChatWidget">
                <!-- Кнопка открытия -->
                <button class="ai-chat-button" id="aiChatToggle" aria-label="Открыть чат">
                    💬
                    <span class="notification-dot" id="notificationDot"></span>
                </button>

                <!-- Контейнер чата -->
                <div class="ai-chat-container" id="aiChatContainer" role="dialog" aria-labelledby="chatTitle">
                    <!-- Шапка -->
                    <div class="ai-chat-header">
                        <div>
                            <h3 id="chatTitle">${this.options.widgetTitle}</h3>
                            <div class="ai-chat-status">
                                <span class="ai-status-dot"></span>
                                <span>В сети</span>
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px; align-items: center;">
                            <button class="ai-theme-toggle" id="aiThemeToggle" 
                                    title="Переключить тему" aria-label="Переключить тему">
                                ${this.currentTheme === 'dark' ? '☀️' : '🌙'}
                            </button>
                            <button class="ai-stats-button" id="aiStatsButton" 
                                    title="Статистика" aria-label="Показать статистику">
                                📊
                            </button>
                            <button class="ai-chat-close" id="aiChatClose" 
                                    aria-label="Закрыть чат">
                                ✕
                            </button>
                        </div>
                    </div>

                    <!-- Панель статистики -->
                    <div class="ai-stats-panel" id="aiStatsPanel">
                        <h4>📊 Статистика</h4>
                        <div class="ai-stat-item">
                            <span>Сообщений:</span>
                            <span class="ai-stat-value" id="statMessages">0</span>
                        </div>
                        <div class="ai-stat-item">
                            <span>Время:</span>
                            <span class="ai-stat-value" id="statTime">0 мин</span>
                        </div>
                    </div>

                    <!-- Область сообщений -->
                    <div class="ai-chat-messages" id="aiChatMessages" role="log" aria-live="polite">
                        <div class="ai-message system">
                            <div class="ai-message-content">${this.options.welcomeMessage}</div>
                        </div>
                    </div>

                    <!-- Индикатор печати -->
                    <div class="ai-chat-typing" id="aiTypingIndicator" style="display: none;">
                        <div class="ai-typing-dot"></div>
                        <div class="ai-typing-dot"></div>
                        <div class="ai-typing-dot"></div>
                    </div>

                    <!-- Быстрые команды -->
                    <div class="ai-quick-commands" id="aiQuickCommands">
                        <div class="ai-quick-commands-list">
                            ${this.quickCommands.map(cmd => `
                                <span class="ai-quick-command" data-command="${cmd.command}" 
                                      title="${cmd.description}">
                                    ${cmd.icon} ${cmd.command}
                                </span>
                            `).join('')}
                        </div>
                    </div>

                    <!-- Умные подсказки -->
                    <div class="ai-suggestions-container" id="aiSuggestionsContainer"></div>

                    <!-- Поле ввода -->
                    <div class="ai-chat-input-container">
                        <div class="ai-chat-input-wrapper">
                            <input
                                type="text"
                                class="ai-chat-input"
                                id="aiChatInput"
                                placeholder="${this.options.placeholder}"
                                maxlength="1000"
                                autocomplete="off"
                                aria-label="Введите сообщение"
                            />
                            <button class="ai-chat-send" id="aiChatSend" 
                                    aria-label="Отправить сообщение" disabled>
                                ➤
                            </button>
                        </div>
                    </div>

                    <!-- Индикатор загрузки -->
                    <div class="ai-loading-indicator" id="aiLoadingIndicator">
                        <div class="ai-loading-spinner"></div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', widgetHTML);
    }

    attachEventListeners() {
        // Кнопки управления
        document.getElementById('aiChatToggle').addEventListener('click', () => this.toggleChat());
        document.getElementById('aiChatClose').addEventListener('click', () => this.closeChat());
        document.getElementById('aiThemeToggle').addEventListener('click', () => this.toggleTheme());
        document.getElementById('aiStatsButton').addEventListener('click', () => this.toggleStats());

        // Отправка сообщения
        const sendButton = document.getElementById('aiChatSend');
        const inputField = document.getElementById('aiChatInput');

        sendButton.addEventListener('click', () => this.sendMessage());

        inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Обновление кнопки отправки
        inputField.addEventListener('input', (e) => {
            this.updateSendButton();
            this.handleInput(e.target.value);
        });

        // Навигация по истории (↑↓)
        inputField.addEventListener('keydown', (e) => {
            this.handleKeyNavigation(e);
        });

        // Быстрые команды
        document.querySelectorAll('.ai-quick-command').forEach(cmd => {
            cmd.addEventListener('click', () => {
                const command = cmd.dataset.command;
                inputField.value = command;
                inputField.focus();
                this.updateSendButton();
            });
        });

        // Клик вне подсказок
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.ai-suggestions-container') &&
                !e.target.closest('.ai-chat-input')) {
                this.hideSuggestions();
            }
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Escape - закрыть чат
            if (e.key === 'Escape' && this.isOpen) {
                this.closeChat();
            }

            // Ctrl/Cmd + K - открыть/закрыть чат
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.toggleChat();
            }
        });
    }

    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    openChat() {
        const container = document.getElementById('aiChatContainer');
        const widget = document.getElementById('aiChatWidget');

        container.classList.add('active');
        widget.classList.add('open');
        this.isOpen = true;

        // Фокус на поле ввода
        setTimeout(() => {
            document.getElementById('aiChatInput').focus();
        }, 300);

        // Скролл вниз
        this.scrollToBottom();

        // Скрыть уведомление
        document.getElementById('notificationDot').classList.remove('active');
    }

    closeChat() {
        const container = document.getElementById('aiChatContainer');
        const widget = document.getElementById('aiChatWidget');

        container.classList.remove('active');
        widget.classList.remove('open');
        this.isOpen = false;

        // Скрыть панели
        this.hideStats();
        this.hideSuggestions();
    }

    async sendMessage() {
        const input = document.getElementById('aiChatInput');
        const message = input.value.trim();

        if (!message || this.isTyping) return;

        // Добавляем в историю команд
        this.commandHistory.unshift(message);
        if (this.commandHistory.length > 50) {
            this.commandHistory.pop();
        }
        this.historyIndex = -1;

        // Скрываем подсказки
        this.hideSuggestions();

        // Добавляем сообщение пользователя
        this.addMessage(message, 'user');
        input.value = '';
        this.updateSendButton();

        // Обновляем статистику
        this.updateStats('message_sent');

        // Показываем индикатор печати
        this.showTypingIndicator();
        this.isTyping = true;

        try {
            // Для неавторизованных - создаем сессию на лету
            if (!this.currentSessionId) {
                const sessionResponse = await this.apiRequest('sessions/create/', 'POST');
                this.currentSessionId = sessionResponse.id;
            }

            const response = await this.apiRequest('chat/', 'POST', {
                message: message,
                session_id: this.currentSessionId
            });

            this.hideTypingIndicator();

            if (response.success) {
                this.addMessage(response.message, 'assistant');
                this.currentSessionId = response.session_id;
            } else {
                this.showError(response.message || 'Произошла ошибка');
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.showError('Не удалось отправить сообщение. Попробуйте еще раз.');
            console.error('AI Chat: Ошибка отправки сообщения', error);
        } finally {
            this.isTyping = false;
        }
    }

    addMessage(content, role, saveToHistory = true) {
        const messagesContainer = document.getElementById('aiChatMessages');
        const messageElement = document.createElement('div');
        messageElement.className = `ai-message ${role}`;

        const currentTime = new Date().toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit'
        });

        const formattedContent = this.formatMessageContent(content);

        messageElement.innerHTML = `
            <div class="ai-message-content">${formattedContent}</div>
            ${role === 'user' ? `<div class="ai-message-time">${currentTime}</div>` : ''}
        `;

        messagesContainer.appendChild(messageElement);

        // Автоскролл
        if (this.options.autoScroll) {
            this.scrollToBottom();
        }

        // Ограничиваем количество сообщений
        const allMessages = messagesContainer.querySelectorAll('.ai-message');
        if (allMessages.length > this.options.maxMessages) {
            allMessages[0].remove();
        }

        if (saveToHistory) {
            this.messages.push({ content, role, timestamp: new Date() });
        }
    }

    formatMessageContent(content) {
        // Экранируем HTML
        let formatted = this.escapeHtml(content);

        // Переносы строк
        formatted = formatted.replace(/\n/g, '<br>');

        // Жирный текст **текст**
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Курсив *текст*
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Код `код`
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Списки
        formatted = formatted.replace(/^• (.+)$/gm, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

        return formatted;
    }

    showTypingIndicator() {
        const indicator = document.getElementById('aiTypingIndicator');
        indicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('aiTypingIndicator');
        indicator.style.display = 'none';
    }

    showError(message) {
        this.addMessage(`❌ ${message}`, 'system');
    }

    updateSendButton() {
        const input = document.getElementById('aiChatInput');
        const sendButton = document.getElementById('aiChatSend');
        sendButton.disabled = !input.value.trim() || this.isTyping;
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('aiChatMessages');
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }

    handleInput(value) {
        // Показываем быстрые команды при вводе /
        const quickCommands = document.getElementById('aiQuickCommands');
        if (value.startsWith('/')) {
            quickCommands.classList.add('active');
        } else {
            quickCommands.classList.remove('active');
        }

        // Умные подсказки (можно расширить)
        if (value.length > 2) {
            // this.showSmartSuggestions(value);
        }

        this.stats.lastActivity = Date.now();
    }

    handleKeyNavigation(e) {
        // Навигация по истории команд (↑↓)
        if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (this.historyIndex < this.commandHistory.length - 1) {
                this.historyIndex++;
                document.getElementById('aiChatInput').value =
                    this.commandHistory[this.historyIndex];
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (this.historyIndex > 0) {
                this.historyIndex--;
                document.getElementById('aiChatInput').value =
                    this.commandHistory[this.historyIndex];
            } else if (this.historyIndex === 0) {
                this.historyIndex = -1;
                document.getElementById('aiChatInput').value = '';
            }
        }
    }

    hideSuggestions() {
        document.getElementById('aiSuggestionsContainer').classList.remove('active');
    }

    toggleTheme() {
        const widget = document.getElementById('aiChatWidget');
        const themeButton = document.getElementById('aiThemeToggle');

        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';

        widget.className = `ai-chat-widget ${this.currentTheme}-theme`;
        if (this.isOpen) widget.classList.add('open');

        themeButton.textContent = this.currentTheme === 'dark' ? '☀️' : '🌙';

        // Сохраняем выбор
        localStorage.setItem('ai_chat_theme', this.currentTheme);
    }

    toggleStats() {
        const panel = document.getElementById('aiStatsPanel');
        const isVisible = panel.classList.contains('active');

        if (isVisible) {
            this.hideStats();
        } else {
            this.showStats();
        }
    }

    showStats() {
        const panel = document.getElementById('aiStatsPanel');
        panel.classList.add('active');
        this.updateStatsDisplay();
    }

    hideStats() {
        const panel = document.getElementById('aiStatsPanel');
        panel.classList.remove('active');
    }

    updateStatsDisplay() {
        document.getElementById('statMessages').textContent = this.stats.messagesCount;

        const minutes = Math.floor((Date.now() - this.stats.startTime) / 60000);
        document.getElementById('statTime').textContent = `${minutes} мин`;
    }

    updateStats(event) {
        if (event === 'message_sent') {
            this.stats.messagesCount++;
        } else if (event === 'session_created') {
            this.stats.sessionsCount++;
        }
        this.stats.lastActivity = Date.now();
    }

    detectPreferredTheme() {
        const savedTheme = localStorage.getItem('ai_chat_theme');
        if (savedTheme) {
            this.currentTheme = savedTheme;
        } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.currentTheme = 'dark';
        } else {
            this.currentTheme = 'light';
        }
    }

    async loadOrCreateSession() {
        try {
            const response = await this.apiRequest('sessions/');

            if (response.sessions && response.sessions.length > 0) {
                this.currentSessionId = response.sessions[0].id;
            } else {
                const newSession = await this.apiRequest('sessions/create/', 'POST');
                this.currentSessionId = newSession.id;
                this.updateStats('session_created');
            }
        } catch (error) {
            console.error('AI Chat: Ошибка загрузки сессии', error);
        }
    }

    async checkFirstVisit() {
        const hasVisited = localStorage.getItem('ai_chat_visited');

        if (!hasVisited) {
            // Показываем приветственную анимацию
            setTimeout(() => {
                const button = document.getElementById('aiChatToggle');
                button.classList.add('welcome-animation');

                setTimeout(() => {
                    button.classList.remove('welcome-animation');
                }, 3000);
            }, 1000);

            localStorage.setItem('ai_chat_visited', 'true');
        }
    }

    async apiRequest(endpoint, method = 'GET', data = null) {
        const url = `${this.options.apiUrl}${endpoint}`;
        const options = {
            method,
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token && token.value) {
            return token.value;
        }

        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            return metaToken.getAttribute('content');
        }

        return '';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Автоматическая инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.aiChatWidget = new AIChatWidget({
        widgetTitle: '🤖 AI Консультант',
        platformName: 'ЦЕНТР СОБЫТИЙ',
        welcomeMessage: '👋 Привет! Я помогу тебе найти сообщество по душе. Что тебя интересует?'
    });
});