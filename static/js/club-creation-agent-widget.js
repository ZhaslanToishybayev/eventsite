/**
 * 🤖 Club Creation Agent Widget
 * Интерактивный виджет для создания клубов через ИИ-диалог
 */

class ClubCreationAgentWidget {
    constructor(options = {}) {
        this.options = {
            apiUrl: '/api/v1/ai/club-creation/agent/',
            guideUrl: '/api/v1/ai/club-creation/guide/',
            validateUrl: '/api/v1/ai/club-creation/validate/',
            enableProgressTracking: true,
            enableAutoSuggestions: true,
            maxMessageLength: 1000,
            ...options
        };

        this.isOpen = false;
        this.agentSession = null;
        this.currentStage = 'greeting';
        this.clubData = {};
        this.messageHistory = [];

        this.init();
    }

    init() {
        this.createWidget();
        this.bindEvents();
        this.loadAgentSession();
        this.displayWelcomeMessage();
    }

    createWidget() {
        // Создаем контейнер виджета
        this.widget = document.createElement('div');
        this.widget.className = 'club-creation-agent-widget';
        this.widget.innerHTML = `
            <div class="agent-header">
                <div class="agent-title">
                    <span class="agent-icon">🤖</span>
                    <span>AI Club Creator</span>
                </div>
                <div class="agent-controls">
                    <button class="restart-btn" title="Начать сначала">🔄</button>
                    <button class="close-btn" title="Закрыть">✕</button>
                </div>
            </div>
            <div class="agent-body">
                <div class="progress-section">
                    <div class="progress-bar">
                        <div class="progress-fill" id="agent-progress-fill"></div>
                    </div>
                    <div class="progress-text" id="agent-progress-text">Добро пожаловать!</div>
                </div>
                <div class="conversation-container" id="agent-conversation">
                    <div class="welcome-message">
                        <h3>Добро пожаловать в Club Creator! 🎉</h3>
                        <p>Я помогу вам создать клуб шаг за шагом. Давайте начнем!</p>
                    </div>
                </div>
                <div class="input-section">
                    <div class="message-input">
                        <textarea
                            id="agent-message-input"
                            placeholder="Введите ваш ответ..."
                            rows="2"
                            maxlength="${this.options.maxMessageLength}"
                        ></textarea>
                        <div class="input-controls">
                            <button class="voice-btn" id="agent-voice-btn" title="Голосовой ввод">
                                <span class="voice-icon">🎤</span>
                                <span class="voice-status">Говорите...</span>
                            </button>
                            <button class="send-btn" id="agent-send-btn" disabled>
                                <span class="send-icon">➤</span>
                                <span class="typing-text">Печатает...</span>
                            </button>
                        </div>
                    </div>
                    <div class="quick-actions" id="agent-quick-actions"></div>
                </div>
                <div class="club-preview" id="agent-club-preview" style="display: none;">
                    <h4>Предварительный просмотр клуба:</h4>
                    <div class="preview-content"></div>
                </div>
            </div>
        `;

        // Добавляем в DOM
        document.body.appendChild(this.widget);

        // Сохраняем ссылки на элементы
        this.conversationContainer = document.getElementById('agent-conversation');
        this.messageInput = document.getElementById('agent-message-input');
        this.sendBtn = document.getElementById('agent-send-btn');
        this.voiceBtn = document.getElementById('agent-voice-btn');
        this.voiceIcon = this.voiceBtn.querySelector('.voice-icon');
        this.voiceStatus = this.voiceBtn.querySelector('.voice-status');
        this.progressFill = document.getElementById('agent-progress-fill');
        this.progressText = document.getElementById('agent-progress-text');
        this.quickActions = document.getElementById('agent-quick-actions');
        this.clubPreview = document.getElementById('agent-club-preview');
    }

    bindEvents() {
        // Отправка сообщения
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.messageInput.addEventListener('input', () => {
            this.sendBtn.disabled = !this.messageInput.value.trim();
        });

        // Voice input functionality
        this.initVoiceRecognition();

        // Управление виджетом
        this.widget.querySelector('.restart-btn').addEventListener('click', () => {
            this.restartConversation();
        });

        this.widget.querySelector('.close-btn').addEventListener('click', () => {
            this.toggle();
        });
    }

    initVoiceRecognition() {
        // Check if SpeechRecognition is available
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            this.voiceBtn.style.display = 'none';
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'ru-RU';

        this.recognition.onstart = () => {
            this.isListening = true;
            this.voiceIcon.textContent = '🔴';
            this.voiceStatus.textContent = 'Слушаю...';
            this.voiceBtn.classList.add('recording');
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.voiceIcon.textContent = '🎤';
            this.voiceStatus.textContent = 'Говорите...';
            this.voiceBtn.classList.remove('recording');
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.messageInput.value = transcript;
            this.sendBtn.disabled = false;
            // Auto-send after voice input
            setTimeout(() => this.sendMessage(), 500);
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.voiceBtn.classList.remove('recording');
            this.voiceIcon.textContent = '🎤';
            this.voiceStatus.textContent = 'Ошибка';
            setTimeout(() => {
                this.voiceStatus.textContent = 'Говорите...';
            }, 2000);
        };

        this.voiceBtn.addEventListener('click', () => {
            if (this.isListening) {
                this.recognition.stop();
            } else {
                this.recognition.start();
            }
        });
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;

        this.addUserMessage(message);
        this.messageInput.value = '';
        this.sendBtn.disabled = true;
        this.setTyping(true);

        try {
            const response = await this.callAgent(message);
            this.handleAgentResponse(response);
        } catch (error) {
            console.error('Error sending message:', error);
            this.addAgentMessage('Извините, произошла ошибка. Пожалуйста, попробуйте позже.');
        } finally {
            this.setTyping(false);
        }
    }

    async callAgent(message) {
        const payload = {
            message: message,
            context: this.getUserContext(),
            action: 'message'
        };

        const response = await fetch(this.options.apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    handleAgentResponse(response) {
        if (response.success) {
            // Добавляем сообщение агента
            this.addAgentMessage(response.response);

            // Обновляем состояние
            this.currentStage = response.session_state;
            this.updateProgress(response.progress);
            this.updateQuickActions(response.next_steps);

            // Обновляем данные клуба
            if (response.club_data) {
                this.clubData = { ...this.clubData, ...response.club_data };
                this.updateClubPreview();
            }

            // Проверяем завершение
            if (response.session_state === 'completed') {
                this.showCompletionMessage();
            }
        } else {
            this.addAgentMessage(response.message || 'Произошла ошибка.');
        }
    }

    addUserMessage(message) {
        const messageElement = this.createMessageElement('user', message);
        this.conversationContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    addAgentMessage(message) {
        const messageElement = this.createMessageElement('agent', message);
        this.conversationContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    createMessageElement(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${sender}`;

        // Преобразуем Markdown в HTML
        const formattedContent = this.formatMessageContent(content);

        messageDiv.innerHTML = `
            <div class="message-avatar">${sender === 'user' ? '👤' : '🤖'}</div>
            <div class="message-content">
                <div class="message-text">${formattedContent}</div>
                <div class="message-time">${this.getCurrentTime()}</div>
            </div>
        `;

        return messageDiv;
    }

    formatMessageContent(content) {
        // Преобразуем Markdown разметку
        let formatted = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Жирный текст
            .replace(/\*(.*?)\*/g, '<em>$1</em>')              // Курсив
            .replace(/`(.*?)`/g, '<code>$1</code>')            // Инлайн код
            .replace(/\n/g, '<br>');                           // Переносы строк

        // Преобразуем списки
        formatted = formatted.replace(/• (.*?)(?=<br>|$)/g, '<li>$1</li>');
        if (formatted.includes('<li>')) {
            formatted = `<ul>${formatted}</ul>`;
        }

        return formatted;
    }

    updateProgress(progress) {
        if (!progress || !this.options.enableProgressTracking) return;

        const percentage = progress.percent || 0;
        this.progressFill.style.width = `${percentage}%`;
        this.progressText.textContent = `Прогресс: ${percentage}%`;

        // Обновляем цвет прогресс-бара
        if (percentage < 30) {
            this.progressFill.style.backgroundColor = '#ef4444'; // Красный
        } else if (percentage < 70) {
            this.progressFill.style.backgroundColor = '#f59e0b'; // Оранжевый
        } else {
            this.progressFill.style.backgroundColor = '#10b981'; // Зеленый
        }
    }

    updateQuickActions(nextSteps) {
        if (!nextSteps || !this.options.enableAutoSuggestions) return;

        this.quickActions.innerHTML = '';

        // Показываем следующие шаги
        nextSteps.slice(0, 3).forEach(step => {
            const actionBtn = document.createElement('button');
            actionBtn.className = 'quick-action-btn';
            actionBtn.textContent = step;
            actionBtn.addEventListener('click', () => {
                this.messageInput.value = this.getActionPrompt(step);
                this.sendMessage();
            });
            this.quickActions.appendChild(actionBtn);
        });
    }

    getActionPrompt(step) {
        const prompts = {
            '👋 Поприветствовать пользователя': 'Привет! Хочу создать клуб',
            '💡 Обсудить идею для клуба': 'Хочу создать клуб по',
            '🏷️ Выбрать категорию': 'Какую категорию выбрать для',
            '📝 Придумать название': 'Помоги придумать название для',
            '✍️ Написать описание': 'Как написать описание для',
            '📞 Собрать контактные данные': 'Нужно указать email и телефон',
            '👀 Проверить все данные': 'Проверь мои данные',
            '✅ Подтвердить создание': 'Готов создать клуб!'
        };

        return prompts[step] || step;
    }

    updateClubPreview() {
        if (!this.clubData || Object.keys(this.clubData).length === 0) {
            this.clubPreview.style.display = 'none';
            return;
        }

        this.clubPreview.style.display = 'block';
        const previewContent = this.clubPreview.querySelector('.preview-content');

        let previewHtml = '<div class="club-preview-item">';
        previewHtml += `<strong>Название:</strong> ${this.clubData.name || 'Не указано'}<br>`;

        if (this.clubData.description) {
            const shortDesc = this.clubData.description.length > 100
                ? this.clubData.description.substring(0, 100) + '...'
                : this.clubData.description;
            previewHtml += `<strong>Описание:</strong> ${shortDesc}<br>`;
        }

        if (this.clubData.category) {
            previewHtml += `<strong>Категория:</strong> ${this.clubData.category}<br>`;
        }

        if (this.clubData.city) {
            previewHtml += `<strong>Город:</strong> ${this.clubData.city}<br>`;
        }

        previewHtml += '</div>';
        previewContent.innerHTML = previewHtml;
    }

    showCompletionMessage() {
        const completionMessage = document.createElement('div');
        completionMessage.className = 'completion-message';
        completionMessage.innerHTML = `
            <div class="completion-icon">🎉</div>
            <h3>Поздравляем!</h3>
            <p>Ваш клуб успешно создан и отправлен на модерацию.</p>
            <p>Вы получите уведомление, когда клуб будет опубликован.</p>
            <div class="completion-actions">
                <button class="btn btn-primary" onclick="window.location.href='/clubs/'">Посмотреть клубы</button>
                <button class="btn btn-secondary" onclick="this.closest('.club-creation-agent-widget').style.display='none'">Закрыть</button>
            </div>
        `;

        this.conversationContainer.appendChild(completionMessage);
        this.scrollToBottom();
    }

    displayWelcomeMessage() {
        this.addAgentMessage(`
            Привет! 👋 Я твой AI-ассистент по созданию клубов.

            Давайте создадим вместе что-то классное! 🚀

            Я помогу тебе пройти все этапы:
            • 💡 Обсудим идею для клуба
            • 🏷️ Выберем подходящую категорию
            • 📝 Придумаем классное название
            • ✍️ Напишем вдохновляющее описание
            • 📞 Соберем контактные данные
            • 👀 Проверим все данные
            • ✅ Создадим клуб!

            С чего начнем? Расскажи, какой клуб ты хочешь создать?
        `);
    }

    async restartConversation() {
        try {
            const response = await fetch(this.options.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    action: 'restart'
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.currentStage = data.session_state;
                this.clubData = {};
                this.messageHistory = [];
                this.conversationContainer.innerHTML = '';
                this.updateProgress(data.progress);
                this.updateQuickActions(data.next_steps);

                this.addAgentMessage(data.response);
            }
        } catch (error) {
            console.error('Error restarting conversation:', error);
        }
    }

    getUserContext() {
        // Получаем контекст пользователя из страницы
        const context = {};

        // Пытаемся получить интересы из страницы
        const interestsElement = document.querySelector('[data-interests]');
        if (interestsElement) {
            context.interests = interestsElement.dataset.interests.split(',');
        }

        // Пытаемся получить город
        const cityElement = document.querySelector('[data-city], .user-city');
        if (cityElement) {
            context.city = cityElement.textContent.trim();
        }

        return context;
    }

    loadAgentSession() {
        // Загружаем сессию из localStorage
        const savedSession = localStorage.getItem('club_creation_session');
        if (savedSession) {
            try {
                this.agentSession = JSON.parse(savedSession);
                this.currentStage = this.agentSession.stage || 'greeting';
                this.clubData = this.agentSession.clubData || {};
            } catch (e) {
                console.error('Error loading agent session:', e);
            }
        }
    }

    saveAgentSession() {
        const sessionData = {
            stage: this.currentStage,
            clubData: this.clubData,
            lastActivity: new Date().toISOString()
        };

        localStorage.setItem('club_creation_session', JSON.stringify(sessionData));
    }

    setTyping(typing) {
        this.isTyping = typing;
        this.sendBtn.innerHTML = typing
            ? '<span class="typing-text">Печатает...</span>'
            : '<span class="send-icon">➤</span>';

        if (typing) {
            this.sendBtn.classList.add('typing');
        } else {
            this.sendBtn.classList.remove('typing');
        }
    }

    scrollToBottom() {
        this.conversationContainer.scrollTop = this.conversationContainer.scrollHeight;
    }

    getCurrentTime() {
        const now = new Date();
        return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    }

    toggle() {
        this.isOpen = !this.isOpen;
        this.widget.classList.toggle('open', this.isOpen);

        if (this.isOpen) {
            this.messageInput.focus();
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : null;
    }

    // Публичные методы
    startConversation() {
        this.isOpen = true;
        this.widget.classList.add('open');
        this.messageInput.focus();
    }

    destroy() {
        this.widget.remove();
        localStorage.removeItem('club_creation_session');
    }
}

// Стили для виджета (можно вынести в отдельный CSS файл)
const agentStyles = `
.club-creation-agent-widget {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 450px;
    height: 700px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    z-index: 10001;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    border: 1px solid #e5e7eb;
    transform: translateY(100px);
    opacity: 0;
    transition: all 0.3s ease;
}

.club-creation-agent-widget.open {
    transform: translateY(0);
    opacity: 1;
}

.agent-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.agent-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
}

.agent-controls {
    display: flex;
    gap: 10px;
}

.restart-btn, .close-btn {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.2s ease;
}

.restart-btn:hover, .close-btn:hover {
    background: rgba(255, 255, 255, 0.3);
}

.agent-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.progress-section {
    padding: 15px 20px;
    background: #f9fafb;
    border-bottom: 1px solid #e5e7eb;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: #e5e7eb;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 8px;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #10b981 0%, #059669 100%);
    transition: width 0.3s ease;
    border-radius: 4px;
}

.progress-text {
    font-size: 12px;
    color: #6b7280;
    text-align: center;
}

.conversation-container {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    min-height: 0;
}

.message {
    display: flex;
    margin-bottom: 15px;
    animation: fadeIn 0.3s ease;
}

.message-user {
    flex-direction: row-reverse;
}

.message-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #e5e7eb;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    margin: 0 10px;
    flex-shrink: 0;
}

.message-user .message-avatar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.message-content {
    flex: 1;
}

.message-text {
    background: #f3f4f6;
    padding: 12px 16px;
    border-radius: 18px;
    margin-bottom: 4px;
    line-height: 1.5;
}

.message-user .message-text {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.message-time {
    font-size: 11px;
    color: #9ca3af;
    text-align: right;
}

.welcome-message {
    text-align: center;
    padding: 40px 20px;
    color: #6b7280;
}

.welcome-message h3 {
    color: #1f2937;
    margin-bottom: 10px;
}

.input-section {
    padding: 15px 20px;
    border-top: 1px solid #e5e7eb;
    background: white;
}

.message-input {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
}

#agent-message-input {
    flex: 1;
    border: 2px solid #e5e7eb;
    border-radius: 20px;
    padding: 12px 16px;
    font-size: 14px;
    resize: none;
    outline: none;
    max-height: 120px;
}

#agent-message-input:focus {
    border-color: #667eea;
}

.send-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: white;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
}

.send-btn:disabled {
    background: #a0aec0;
    cursor: not-allowed;
    transform: scale(0.95);
}

.send-btn:hover:not(:disabled) {
    transform: scale(1.05);
}

.input-controls {
    display: flex;
    align-items: center;
    gap: 8px;
}

.voice-btn {
    background: #f3f4f6;
    border: 2px solid #e5e7eb;
    color: #6b7280;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}

.voice-btn:hover {
    background: #e5e7eb;
    border-color: #667eea;
    color: #667eea;
}

.voice-btn.recording {
    background: #fee2e2;
    border-color: #ef4444;
    animation: pulse 1.5s infinite;
}

.voice-btn.recording .voice-icon {
    color: #ef4444;
}

.voice-icon {
    font-size: 16px;
    transition: all 0.2s ease;
}

.voice-status {
    font-size: 9px;
    position: absolute;
    bottom: -20px;
    opacity: 0;
    transition: all 0.2s ease;
    white-space: nowrap;
}

.voice-btn:hover .voice-status {
    bottom: -2px;
    opacity: 1;
}

@keyframes pulse {
    0%, 100% {
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
    }
}

.quick-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.quick-action-btn {
    background: #f3f4f6;
    border: none;
    padding: 6px 12px;
    border-radius: 16px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.quick-action-btn:hover {
    background: #e5e7eb;
    transform: scale(1.05);
}

.club-preview {
    padding: 15px 20px;
    background: #f0fdf4;
    border-top: 1px solid #e5e7eb;
    border-bottom: 1px solid #e5e7eb;
}

.club-preview h4 {
    margin: 0 0 10px 0;
    color: #1f2937;
    font-size: 14px;
}

.club-preview-item {
    background: white;
    padding: 10px;
    border-radius: 8px;
    font-size: 12px;
    line-height: 1.4;
}

.club-preview-item strong {
    color: #374151;
}

.completion-message {
    text-align: center;
    padding: 30px 20px;
    background: #f0fdf4;
    border-radius: 12px;
    margin: 10px 0;
}

.completion-icon {
    font-size: 48px;
    margin-bottom: 15px;
}

.completion-message h3 {
    color: #1f2937;
    margin-bottom: 10px;
}

.completion-message p {
    color: #6b7280;
    margin-bottom: 20px;
    line-height: 1.5;
}

.completion-actions {
    display: flex;
    gap: 10px;
    justify-content: center;
}

.btn {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.btn-primary:hover {
    transform: translateY(-1px);
}

.btn-secondary {
    background: #e5e7eb;
    color: #374151;
}

.btn-secondary:hover {
    background: #d1d5db;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Responsive design */
@media (max-width: 768px) {
    .club-creation-agent-widget {
        width: 100%;
        max-width: 450px;
        bottom: 20px;
        right: 20px;
        left: 20px;
        height: 600px;
    }
}
`;

// Добавляем стили в документ
if (!document.getElementById('club-creation-agent-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'club-creation-agent-styles';
    styleSheet.textContent = agentStyles;
    document.head.appendChild(styleSheet);
}

// Автоматическая инициализация
document.addEventListener('DOMContentLoaded', () => {
    if (document.body.hasAttribute('data-club-creation-agent')) {
        window.clubCreationAgent = new ClubCreationAgentWidget();
    }
});

// Экспорт для ручной инициализации
window.ClubCreationAgentWidget = ClubCreationAgentWidget;