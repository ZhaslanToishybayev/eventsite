/**
 * 🤖 JavaScript для улучшенного AI консультанта с функциями
 */

class ActionableAIWidget {
    constructor() {
        this.isOpen = false;
        this.isTyping = false;
        this.currentUserId = null;
        this.init();
    }

    async init() {
        this.createWidget();
        this.attachEvents();
        this.loadUserContext();
    }

    createWidget() {
        // Создаем виджет из HTML шаблона
        const widgetContainer = document.createElement('div');
        widgetContainer.innerHTML = this.getWidgetHTML();
        document.body.appendChild(widgetContainer.firstElementChild);

        // Инициализируем элементы
        this.elements = {
            widget: document.getElementById('ai-chat-widget-v4'),
            toggleBtn: document.getElementById('chatToggleBtnV4'),
            container: document.getElementById('chatContainerV4'),
            messages: document.getElementById('chatMessagesV4'),
            input: document.getElementById('chatInputV4'),
            inputWrapper: document.getElementById('chatInputWrapperV4'),
            sendBtn: document.getElementById('chatSendBtnV4'),
            typing: document.getElementById('chatTypingV4'),
            actionsBtn: document.getElementById('aiActionsBtn'),
            actionsBlock: document.getElementById('aiActionsBlock'),
            clubForm: document.getElementById('aiClubForm'),
            clubFormBtn: document.getElementById('aiClubFormBtn')
        };
    }

    getWidgetHTML() {
        // HTML виджета уже вставлен в шаблон
        return '';
    }

    attachEvents() {
        // Кнопка открытия/закрытия
        this.elements.toggleBtn.addEventListener('click', () => this.toggleWidget());
        this.elements.widget.addEventListener('click', (e) => {
            if (e.target.id === 'aiCloseBtnV4') this.closeWidget();
        });

        // Ввод сообщения
        this.elements.input.addEventListener('input', (e) => this.handleInput(e));
        this.elements.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Быстрые действия
        this.elements.actionsBtn.addEventListener('click', () => this.toggleActions());
        this.elements.widget.addEventListener('click', (e) => {
            if (e.target.closest('[data-action]')) {
                this.handleQuickAction(e.target.closest('[data-action]').dataset.action);
            }
        });

        // Форма создания клуба
        this.elements.widget.addEventListener('click', (e) => {
            if (e.target.id === 'aiClubFormBtn') this.showClubForm();
            if (e.target.id === 'aiClubFormClose') this.hideClubForm();
            if (e.target.id === 'aiActionsClose') this.hideActions();
        });

        // Отправка формы создания клуба
        this.elements.widget.addEventListener('submit', (e) => {
            if (e.target.id === 'clubCreationForm') {
                e.preventDefault();
                this.submitClubForm(e.target);
            }
        });

        // Закрытие по Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideActions();
                this.hideClubForm();
                if (!this.isOpen) this.closeWidget();
            }
        });
    }

    async loadUserContext() {
        try {
            // Получаем информацию о пользователе
            const response = await fetch('/api/v1/user/context/');
            if (response.ok) {
                const userData = await response.json();
                this.currentUserId = userData.id;
            }
        } catch (error) {
            console.warn('User context not available');
        }
    }

    toggleWidget() {
        if (this.isOpen) {
            this.closeWidget();
        } else {
            this.openWidget();
        }
    }

    openWidget() {
        this.isOpen = true;
        this.elements.container.classList.add('active');
        this.elements.toggleBtn.style.display = 'none';
    }

    closeWidget() {
        this.isOpen = false;
        this.elements.container.classList.remove('active');
        this.elements.toggleBtn.style.display = 'flex';
        this.hideActions();
        this.hideClubForm();
    }

    handleInput(e) {
        const value = e.target.value;
        const hasText = value.trim().length > 0;

        // Обновляем счетчик символов
        document.getElementById('charCountV4').textContent = value.length;

        // Активируем/деактивируем кнопку отправки
        this.elements.sendBtn.disabled = !hasText;

        // Обновляем классы
        this.elements.inputWrapper.classList.toggle('has-text', hasText);

        // Авто-расширение высоты
        e.target.style.height = 'auto';
        e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
    }

    async sendMessage() {
        const message = this.elements.input.value.trim();
        if (!message) return;

        // Добавляем сообщение пользователя
        this.addMessage(message, 'user');

        // Очищаем поле ввода
        this.elements.input.value = '';
        this.elements.input.style.height = 'auto';
        this.handleInput({ target: this.elements.input });

        // Показываем индикатор печати
        this.showTyping();

        // Отправляем сообщение в AI
        try {
            const response = await fetch('/api/v1/ai/enhanced/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    message: message,
                    user_email: this.getUserEmail()
                })
            });

            this.hideTyping();

            if (response.ok) {
                const data = await response.json();
                this.addMessage(data.message, 'assistant');

                // Обработка действий
                if (data.action_performed) {
                    this.handleActionResponse(data.action_performed);
                }
            } else {
                this.addMessage('❌ Произошла ошибка. Попробуйте еще раз.', 'assistant');
            }
        } catch (error) {
            this.hideTyping();
            this.addMessage('❌ Ошибка соединения. Проверьте интернет и попробуйте снова.', 'assistant');
        }
    }

    addMessage(text, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `ai-message-v4 ${role}-v4`;

        const avatar = role === 'user' ? '👤' : '🤖';

        messageDiv.innerHTML = `
            <div class="ai-message-row-v4">
                <div class="ai-message-avatar-v4">${avatar}</div>
                <div class="ai-message-content-v4">
                    ${this.renderMarkdown(text)}
                </div>
            </div>
        `;

        this.elements.messages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTyping() {
        this.isTyping = true;
        this.elements.typing.style.display = 'flex';
    }

    hideTyping() {
        this.isTyping = false;
        this.elements.typing.style.display = 'none';
    }

    scrollToBottom() {
        setTimeout(() => {
            this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
        }, 100);
    }

    renderMarkdown(text) {
        // Простая реализация Markdown
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>')
            .replace(/^• (.*)$/gm, '• $1')
            .replace(/^• (.*)$/gm, '<li>$1</li>')
            .replace(/<li>.*<\/li>/g, '<ul>$&</ul>');
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.querySelector('[data-csrf-token]')?.dataset.csrfToken ||
               '';
    }

    getUserEmail() {
        // Пытаемся получить email пользователя
        const userEmailElement = document.querySelector('[data-user-email]');
        if (userEmailElement) {
            return userEmailElement.dataset.userEmail;
        }
        return null;
    }

    // Функции быстрых действий
    toggleActions() {
        const isVisible = this.elements.actionsBlock.style.display === 'block';
        if (isVisible) {
            this.hideActions();
        } else {
            this.showActions();
        }
    }

    showActions() {
        this.elements.actionsBlock.style.display = 'block';
    }

    hideActions() {
        this.elements.actionsBlock.style.display = 'none';
    }

    showClubForm() {
        this.hideActions();
        this.elements.clubForm.style.display = 'block';
    }

    hideClubForm() {
        this.elements.clubForm.style.display = 'none';
    }

    handleQuickAction(action) {
        const messages = {
            'create_club': 'Напиши: "Создай клуб" и я помогу создать твой клуб!',
            'create_event': 'Напиши: "Создай мероприятие" и я помогу организовать событие!',
            'manage_clubs': 'Напиши: "Мои клубы" и я покажу информацию об управлении!',
            'monetization': 'Напиши: "Монетизация" и я расскажу о способах заработка!',
            'promotion': 'Напиши: "Продвижение" и я дам советы по раскрутке!',
            'analytics': 'Напиши: "Аналитика" и я расскажу о статистике!'
        };

        this.addMessage(messages[action] || 'Выбери действие из меню!', 'assistant');
        this.hideActions();
    }

    async submitClubForm(form) {
        const formData = new FormData(form);
        const clubData = Object.fromEntries(formData);

        // Валидация формы
        if (!clubData.name || !clubData.description || !clubData.category || !clubData.city || !clubData.email) {
            this.addMessage('❌ Заполните все обязательные поля!', 'assistant');
            return;
        }

        if (clubData.description.length < 200) {
            this.addMessage('❌ Описание должно быть не менее 200 символов!', 'assistant');
            return;
        }

        // Показываем индикатор
        this.showTyping();

        try {
            const response = await fetch('/api/v1/clubs/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(clubData)
            });

            this.hideTyping();

            if (response.ok) {
                const result = await response.json();
                this.addMessage(`🎉 Отлично! Твой клуб "${result.name}" успешно создан!`, 'assistant');
                this.hideClubForm();

                // Добавляем сообщение с инструкциями
                this.addMessage(`
                    **📋 Что дальше:**
                    1. **Зайди в админку**: Перейди в личный кабинет и найди свой клуб
                    2. **Добавь фото**: Загрузи логотип и фотографии клуба
                    3. **Создай первое мероприятие**: Организуй знакомство участников
                    4. **Расскажи друзьям**: Пригласи первых участников

                    **📱 Твой клуб теперь на fan-club.kz!**
                    Ссылка: https://fan-club.kz/clubs/${result.club_id}
                `, 'assistant');
            } else {
                const error = await response.json();
                this.addMessage(`❌ Ошибка создания клуба: ${error.error}`, 'assistant');
            }
        } catch (error) {
            this.hideTyping();
            this.addMessage('❌ Ошибка сети. Попробуйте еще раз.', 'assistant');
        }
    }

    handleActionResponse(action) {
        // Обработка ответов от сервера
        console.log('Action performed:', action);
    }
}

// Инициализация виджета
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('ai-chat-widget-v4')) {
        new ActionableAIWidget();
    }
});

// Экспортируем для использования в других модулях
window.ActionableAIWidget = ActionableAIWidget;