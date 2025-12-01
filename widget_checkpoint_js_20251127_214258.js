// 🚀 Enhanced Chat Widget JavaScript - v6.0.0
// 🎯 Professional AI Consultant Widget with Premium Design

class EnhancedChatWidget {
    constructor() {
        this.isOpen = false;
        this.isProcessing = false;
        this.messageHistory = [];
        this.sessionId = 'enhanced_' + Math.random().toString(36).substr(2, 9);
        this.typingTimeout = null;

        this.initializeElements();
        this.bindEvents();
        this.loadMessageHistory();
    }

    initializeElements() {
        this.button = document.getElementById('modernWidgetButton');
        this.chat = document.getElementById('modernWidgetChat');
        this.messages = document.getElementById('modernWidgetMessages');
        this.input = document.getElementById('modernWidgetInput');
        this.sendBtn = document.getElementById('modernWidgetSend');
        this.closeBtn = document.getElementById('modernWidgetClose');

        // Проверка существования элементов
        if (!this.button || !this.chat || !this.messages || !this.input || !this.sendBtn || !this.closeBtn) {
            console.error('❌ Один или несколько элементов виджета не найдены');
            return;
        }
    }

    bindEvents() {
        if (this.button) this.button.addEventListener('click', () => this.toggleChat());
        if (this.closeBtn) this.closeBtn.addEventListener('click', () => this.toggleChat());
        if (this.sendBtn) this.sendBtn.addEventListener('click', () => this.sendMessage());
        if (this.input) {
            this.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            this.input.addEventListener('input', () => {
                this.updateSendButtonState();
            });
        }

        // Инициализация частиц при наведении
        if (this.button) {
            this.button.addEventListener('mouseenter', (e) => {
                this.createParticleEffect(e.target);
            });
        }
    }

    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    openChat() {
        this.isOpen = true;
        if (this.chat) {
            this.chat.style.display = 'flex';
            this.chat.style.animation = 'slideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)';
        }
        if (this.input) {
            this.input.focus();
        }

        // Приветствие при первом открытии
        if (this.messages && this.messages.children.length === 0) {
            setTimeout(() => {
                this.addMessage('👋 Добро пожаловать в UnitySphere AI Консультант!', 'bot');
                setTimeout(() => {
                    this.addMessage('✨ <strong>Наши возможности:</strong><br>• 🏠 Поиск и создание клубов<br>• 🎉 Организация мероприятий<br>• 💬 Консультации по развитию<br>• 🔍 Поиск единомышленников', 'bot');
                    setTimeout(() => {
                        this.addMessage('💡 Задайте любой вопрос о клубах, мероприятиях или сообществах!', 'bot');
                    }, 800);
                }, 800);
            }, 500);
        }
    }

    closeChat() {
        this.isOpen = false;
        if (this.chat) {
            this.chat.style.animation = 'slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) reverse';
            setTimeout(() => {
                if (!this.isOpen) {
                    this.chat.style.display = 'none';
                }
            }, 300);
        }
    }

    updateSendButtonState() {
        if (!this.sendBtn || !this.input) return;

        const hasText = this.input.value.trim().length > 0;
        const isDisabled = !hasText || this.isProcessing;

        this.sendBtn.disabled = isDisabled;
        this.sendBtn.style.opacity = isDisabled ? '0.6' : '1';
        this.sendBtn.style.cursor = isDisabled ? 'not-allowed' : 'pointer';
    }

    sendMessage() {
        if (!this.input) return;

        const message = this.input.value.trim();
        if (!message || this.isProcessing) return;

        this.addMessage(message, 'user');
        this.messageHistory.push({ role: 'user', content: message });
        this.input.value = '';
        this.setProcessingState(true);

        // Сохранение истории
        this.saveMessageHistory();

        // Искусственная задержка для реализма
        setTimeout(() => {
            this.showTypingIndicator();
            setTimeout(() => {
                this.removeTypingIndicator();
                const response = this.generateSmartResponse(message);
                this.addMessage(response, 'bot');
                this.messageHistory.push({ role: 'bot', content: response });
                this.setProcessingState(false);
            }, 1500 + Math.random() * 1000);
        }, 300);
    }

    showTypingIndicator() {
        if (!this.messages) return;

        const typingDiv = document.createElement('div');
        typingDiv.className = 'modern-widget-typing';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="modern-widget-typing-text">AI печатает...</div>
            <div class="modern-widget-typing-dots">
                <div class="modern-widget-typing-dot"></div>
                <div class="modern-widget-typing-dot"></div>
                <div class="modern-widget-typing-dot"></div>
            </div>
        `;

        this.messages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    addMessage(text, sender) {
        if (!this.messages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `modern-widget-message modern-widget-${sender}-message`;
        messageDiv.innerHTML = text;

        this.messages.appendChild(messageDiv);
        this.scrollToBottom();

        // Эффект появления
        setTimeout(() => {
            messageDiv.style.animation = 'messageSlideIn 0.3s ease-out';
        }, 50);
    }

    scrollToBottom() {
        if (this.messages) {
            this.messages.scrollTop = this.messages.scrollHeight;
        }
    }

    generateSmartResponse(userMessage) {
        const message = userMessage.toLowerCase();

        // Ключевые слова
        const clubKeywords = ['клуб', 'сообщество', 'группа', 'фан', 'фан-клуб', 'объединение'];
        const eventKeywords = ['мероприяти', 'фестиваль', 'событи', 'встреч', 'концерт', 'вечеринка'];
        const helpKeywords = ['помощь', 'помоги', 'как', 'что', 'где', 'когда', 'почему'];
        const createKeywords = ['создать', 'сделать', 'основать', 'запустить'];

        // Проверка ключевых слов
        const hasClubKeywords = clubKeywords.some(keyword => message.includes(keyword));
        const hasEventKeywords = eventKeywords.some(keyword => message.includes(keyword));
        const hasHelpKeywords = helpKeywords.some(keyword => message.includes(keyword));
        const hasCreateKeywords = createKeywords.some(keyword => message.includes(keyword));

        // Приоритеты ответов
        if (hasCreateKeywords || message.includes('создать')) {
            return `🏠 Отличный выбор! Создание клуба - это увлекательно!\n\n<b>✨ Пошаговый гайд:</b>\n• Определите тематику и целевую аудиторию\n• Придумайте запоминающееся название\n• Создайте описание с четкой миссией\n• Найдите первых активных участников\n• Организуйте первое мероприятие\n\n<b>🎯 Популярные направления:</b>\n• Музыка и искусство\n• Спорт и активный отдых\n• Технологии и игры\n• Образование и развитие\n\nХотите подробную консультацию по созданию клуба?`;

        } else if (hasClubKeywords) {
            return `🏠 Клубы - основа нашего сообщества!\n\n<b>✨ Что мы предлагаем:</b>\n• Поиск подходящих клубов по интересам\n• Рейтинги самых активных сообществ\n• Возможности для развития и роста\n• Площадка для общения и идей\n\n<b>🎯 Популярные категории:</b>\n• 🎵 Музыка и творчество\n• ⚽ Спорт и активный образ жизни\n• 🎮 Игры и технологии\n• 📚 Образование и саморазвитие\n\nРасскажите, что вас интересует больше всего?`;

        } else if (hasEventKeywords) {
            return `🎉 Мероприятия - это здорово!\n\n<b>📅 Текущие события:</b>\n• Музыкальные вечера каждые выходные\n• Спортивные турниры и соревнования\n• Творческие мастер-классы\n• Образовательные встречи и лекции\n\n<b>💡 Советы по организации:</b>\n• Четко определите целевую аудиторию\n• Выберите подходящую площадку\n• Продумайте интересную программу\n• Сделайте качественную рекламу\n• Позаботьтесь о комфорте гостей\n\nХотите узнать о конкретном типе мероприятия?`;

        } else if (hasHelpKeywords || message.includes('как')) {
            return `🤔 С удовольствием помогу!\n\n<b>🚀 Возможности UnitySphere:</b>\n• 🔍 Поиск подходящих клубов по интересам\n• 💬 Консультации по развитию сообществ\n• 🎉 Помощь в организации мероприятий\n• 👥 Поиск единомышленников\n• 📈 Советы по продвижению и росту\n\n<b>📋 Просто спросите:</b>\n• "Как создать популярный клуб?"\n• "Где найти людей с похожими интересами?"\n• "Как организовать успешное мероприятие?"\n• "Что сейчас популярно среди фанатов?"`;

        } else if (message.includes('спасибо') || message.includes('благодар')) {
            return `🙏 Пожалуйста! Рад был помочь!\n\n💡 Если понадобится еще assistance, просто напишите. Я всегда готов помочь с:\n• 🏠 Поиском и созданием клубов\n• 🎉 Организацией мероприятий\n• 💬 Советами по развитию сообществ\n• 👥 Поиском единомышленников\n\n✨ Хорошего дня и успешных начинаний!`;

        } else if (message.includes('пока') || message.includes('досвидания') || message.includes('хватит')) {
            return `👋 До свидания! Был рад пообщаться!\n\n💡 Возвращайтесь, когда понадобится помощь с:\n• 🏠 Клубами и сообществами\n• 🎉 Мероприятиями и событиями\n• 💬 Советами и консультациями\n\n✨ UnitySphere всегда к вашим услугам!`;

        } else {
            // Генерация случайного умного ответа
            const responses = [
                `🔍 Интересный вопрос! Давайте подумаем вместе.\n\n💡 Вы можете:\n• Рассказать больше о своих интересах\n• Спросить о конкретных клубах\n• Узнать о предстоящих мероприятиях\n• Получить советы по созданию сообществ\n\nЧто именно вас интересует?`,
                `✨ Отличный вопрос! Предлагаю начать с:\n\n🏠 <b>Для поиска клубов:</b> Используйте фильтры по интересам\n🎉 <b>Для мероприятий:</b> Смотрите раздел "Фестивали"\n💬 <b>Для общения:</b> Присоединяйтесь к интересующим вас сообществам\n\nЧто хотите изучить подробнее?`,
                `🌟 Понял ваш запрос! Рекомендую начать с:\n\n🎯 <b>Пошаговый план:</b>\n1. Определите ваши интересы и цели\n2. Поищите похожие клубы\n3. Примите участие в мероприятиях\n4. Создайте свое сообщество\n\nХочется что-то конкретное?`
            ];

            return responses[Math.floor(Math.random() * responses.length)];
        }
    }

    setProcessingState(processing) {
        this.isProcessing = processing;
        this.updateSendButtonState();

        if (this.input) {
            this.input.disabled = processing;
        }
    }

    saveMessageHistory() {
        try {
            localStorage.setItem(`widgetHistory_${this.sessionId}`, JSON.stringify(this.messageHistory));
        } catch (e) {
            console.warn('⚠️ Не удалось сохранить историю сообщений');
        }
    }

    loadMessageHistory() {
        try {
            const savedHistory = localStorage.getItem(`widgetHistory_${this.sessionId}`);
            if (savedHistory) {
                this.messageHistory = JSON.parse(savedHistory);
                console.log('✅ История сообщений загружена');
            }
        } catch (e) {
            console.warn('⚠️ Не удалось загрузить историю');
        }
    }

    createParticleEffect(element) {
        const particles = 3;
        for (let i = 0; i < particles; i++) {
            this.createParticle(element);
        }
    }

    createParticle(element) {
        if (!element || !document.body) return;

        const particle = document.createElement('div');
        particle.style.cssText = `
            position: fixed;
            width: 4px;
            height: 4px;
            background: rgba(37, 99, 235, 0.6);
            border-radius: 50%;
            pointer-events: none;
            z-index: 9997;
            animation: particleFloat 2s ease-out forwards;
        `;

        document.body.appendChild(particle);

        const rect = element.getBoundingClientRect();
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;

        particle.style.left = x + 'px';
        particle.style.top = y + 'px';

        const angle = Math.random() * Math.PI * 2;
        const velocity = 50 + Math.random() * 50;
        const vx = Math.cos(angle) * velocity;
        const vy = Math.sin(angle) * velocity;

        particle.animate([
            { transform: 'translate(0, 0) scale(1)', opacity: 1 },
            { transform: `translate(${vx}px, ${vy}px) scale(0)`, opacity: 0 }
        ], {
            duration: 2000,
            easing: 'ease-out'
        });

        setTimeout(() => particle.remove(), 2000);
    }
}

// Инициализация виджета
function initializeEnhancedWidget() {
    console.log('🚀 Enhanced Chat Widget инициализируется...');

    if (typeof EnhancedChatWidget !== 'undefined') {
        window.enhancedChatWidget = new EnhancedChatWidget();
        console.log('✅ Enhanced Chat Widget успешно инициализирован!');
        console.log('   • Современный дизайн с градиентами');
        console.log('   • Умные ответы на основе анализа текста');
        console.log('   • Эффекты частиц при наведении');
        console.log('   • История сообщений');
        console.log('   • Реалистичная имитация печати');
        console.log('   Session ID:', window.enhancedChatWidget.sessionId);
    } else {
        console.error('❌ EnhancedChatWidget класс не найден');
    }
}

// Автоматическая инициализация после загрузки DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeEnhancedWidget);
} else {
    initializeEnhancedWidget();
}