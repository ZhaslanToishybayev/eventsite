// 🔧 ОБНОВЛЕНИЕ JAVASCRIPT ДЛЯ ИСПОЛЬЗОВАНИЯ УЛУЧШЕННОГО AI

// Найдем и заменим URL в существующем JavaScript
const currentScript = document.currentScript || document.getElementsByTagName('script')[document.getElementsByTagName('script').length - 1];
const scriptContent = currentScript.textContent;

// Обновим URL для использования улучшенного AI
if (scriptContent.includes('api/v1/ai/')) {
    console.log('🔧 Обновляем URL для использования улучшенного AI...');

    // Обновим apiUrl в виджете
    if (window.AIChatWidget) {
        window.AIChatWidget.prototype.options.apiUrl = '/api/v1/ai/enhanced/';
        console.log('✅ URL обновлен на /api/v1/ai/enhanced/');
    }

    // Перезапустим виджет с новым URL
    if (window.aiChatWidgetInstance) {
        window.aiChatWidgetInstance.destroy();
        window.aiChatWidgetInstance = new window.AIChatWidget({
            apiUrl: '/api/v1/ai/enhanced/'
        });
        console.log('✅ Виджет перезапущен с улучшенным AI');
    }
}

// Создадим улучшенный виджет если его нет
if (!window.ActionableAIWidget) {
    console.log('🤖 Создаем улучшенный Actionable AI Widget...');

    class EnhancedAIWidget extends window.AIChatWidget {
        constructor(options = {}) {
            super({
                apiUrl: '/api/v1/ai/enhanced/',
                widgetTitle: 'Action AI Консультант',
                welcomeMessage: '👋 Привет! Я Action AI консультант - твой помощник в создании и развитии фан-клубов! ⚡',
                placeholder: 'Напиши, что хочешь сделать...',
                ...options
            });

            this.setupEnhancedFeatures();
        }

        setupEnhancedFeatures() {
            // Добавляем кнопку быстрых действий
            this.createQuickActionsButton();
            this.addQuickActionListeners();
        }

        createQuickActionsButton() {
            if (!document.getElementById('aiQuickActionsBtn')) {
                const quickActionsBtn = document.createElement('button');
                quickActionsBtn.id = 'aiQuickActionsBtn';
                quickActionsBtn.className = 'ai-quick-actions-btn';
                quickActionsBtn.innerHTML = '⚡';
                quickActionsBtn.title = 'Быстрые действия';
                quickActionsBtn.onclick = () => this.showQuickActions();

                // Добавляем в input wrapper
                const inputWrapper = document.getElementById('chatInputWrapper');
                if (inputWrapper) {
                    inputWrapper.insertBefore(quickActionsBtn, inputWrapper.firstChild);
                }
            }
        }

        showQuickActions() {
            const actions = [
                { action: 'create_club', text: '🏆 Создать клуб', icon: '🏆' },
                { action: 'create_event', text: '📅 Мероприятие', icon: '📅' },
                { action: 'manage_clubs', text: '🛠️ Управление', icon: '🛠️' },
                { action: 'monetization', text: '💰 Монетизация', icon: '💰' },
                { action: 'promotion', text: '📢 Продвижение', icon: '📢' }
            ];

            const actionsHtml = actions.map(action => `
                <button class="ai-quick-action-item" data-action="${action.action}">
                    <span class="ai-quick-action-icon">${action.icon}</span>
                    <span class="ai-quick-action-text">${action.text}</span>
                </button>
            `).join('');

            this.showModal('⚡ Быстрые действия', actionsHtml);

            // Добавляем обработчики для кнопок
            document.querySelectorAll('.ai-quick-action-item').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const action = e.target.closest('[data-action]').dataset.action;
                    this.handleQuickAction(action);
                    this.hideModal();
                });
            });
        }

        handleQuickAction(action) {
            const messages = {
                'create_club': 'Напиши: "Создай клуб" и я помогу создать твой клуб! 🏆',
                'create_event': 'Напиши: "Создай мероприятие" и я помогу организовать событие! 📅',
                'manage_clubs': 'Напиши: "Мои клубы" и я покажу информацию об управлении! 🛠️',
                'monetization': 'Напиши: "Монетизация" и я расскажу о способах заработка! 💰',
                'promotion': 'Напиши: "Продвижение" и я дам советы по раскрутке! 📢'
            };

            this.addMessage(messages[action] || 'Выбери действие из меню!', 'assistant');
        }

        showModal(title, content) {
            // Создаем модальное окно
            let modal = document.getElementById('aiEnhancedModal');
            if (!modal) {
                modal = document.createElement('div');
                modal.id = 'aiEnhancedModal';
                modal.className = 'ai-enhanced-modal';
                modal.innerHTML = `
                    <div class="ai-modal-content">
                        <div class="ai-modal-header">
                            <h4>${title}</h4>
                            <button class="ai-modal-close" onclick="window.enhancedAIWidget.hideModal()">×</button>
                        </div>
                        <div class="ai-modal-body">
                            ${content}
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);

                // Добавляем стили
                this.addModalStyles();
            } else {
                modal.querySelector('.ai-modal-header h4').textContent = title;
                modal.querySelector('.ai-modal-body').innerHTML = content;
            }

            modal.style.display = 'block';
        }

        hideModal() {
            const modal = document.getElementById('aiEnhancedModal');
            if (modal) {
                modal.style.display = 'none';
            }
        }

        addModalStyles() {
            if (document.getElementById('aiModalStyles')) return;

            const styles = document.createElement('style');
            styles.id = 'aiModalStyles';
            styles.textContent = `
                .ai-enhanced-modal {
                    display: none;
                    position: fixed;
                    z-index: 10000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0,0,0,0.5);
                }
                .ai-modal-content {
                    background-color: white;
                    margin: 15% auto;
                    padding: 20px;
                    border-radius: 12px;
                    width: 80%;
                    max-width: 400px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }
                .ai-modal-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }
                .ai-modal-header h4 {
                    margin: 0;
                    color: #333;
                }
                .ai-modal-close {
                    background: none;
                    border: none;
                    font-size: 24px;
                    cursor: pointer;
                    color: #999;
                }
                .ai-modal-close:hover {
                    color: #333;
                }
                .ai-quick-action-item {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    width: 100%;
                    padding: 12px 16px;
                    margin-bottom: 8px;
                    background: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s;
                    text-align: left;
                }
                .ai-quick-action-item:hover {
                    background: #e9ecef;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }
                .ai-quick-action-icon {
                    font-size: 18px;
                }
                .ai-quick-action-text {
                    font-size: 14px;
                    font-weight: 500;
                    color: #495057;
                }
            `;
            document.head.appendChild(styles);
        }
    }

    window.EnhancedAIWidget = EnhancedAIWidget;
    console.log('✅ Улучшенный AI виджет создан');
}

// Инициализируем улучшенный виджет
document.addEventListener('DOMContentLoaded', () => {
    if (window.AIChatWidget && !window.enhancedAIWidget) {
        console.log('🚀 Инициализируем улучшенный AI виджет...');
        window.enhancedAIWidget = new window.EnhancedAIWidget();
        console.log('✅ Улучшенный AI виджет инициализирован');
    }
});

console.log('🔧 Скрипт обновления AI виджета загружен');