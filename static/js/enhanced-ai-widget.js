/**
 * 🚀 Enhanced AI Chat Widget with RAG Integration
 * Advanced chat widget with semantic search, recommendations, and personalization
 */

class EnhancedAIChatWidget {
    constructor(options = {}) {
        this.options = {
            apiUrl: '/api/v1/ai/enhanced-chat/',
            recommendationsUrl: '/api/v1/ai/recommendations/',
            rateRecommendationUrl: '/api/v1/ai/recommendations/rate/',
            healthCheckUrl: '/api/v1/ai/health/',
            enableRecommendations: true,
            enableRAG: true,
            enablePersonalization: true,
            maxMessages: 50,
            autoScroll: true,
            showRecommendations: true,
            enableVoiceInput: false,
            enableMarkdown: true,
            ...options
        };

        this.isOpen = false;
        this.messages = [];
        this.userContext = {};
        this.currentSessionId = null;
        this.isTyping = false;
        this.recommendations = [];

        this.init();
    }

    init() {
        this.createWidget();
        this.loadUserContext();
        this.bindEvents();
        this.checkServiceHealth();
        this.loadInitialRecommendations();
    }

    createWidget() {
        // Create main widget container
        this.widget = document.createElement('div');
        this.widget.className = 'enhanced-ai-widget';
        this.widget.innerHTML = `
            <div class="widget-header">
                <div class="widget-title">
                    <span class="ai-icon">🤖</span>
                    <span>Enhanced AI Assistant</span>
                </div>
                <div class="widget-controls">
                    <button class="minimize-btn" title="Minimize">−</button>
                    <button class="close-btn" title="Close">×</button>
                </div>
            </div>
            <div class="widget-body">
                <div class="chat-container">
                    <div class="messages-container" id="enhanced-messages"></div>
                    <div class="recommendations-container" id="enhanced-recommendations"></div>
                </div>
                <div class="input-container">
                    <div class="input-controls">
                        <button class="voice-input-btn" title="Voice Input" style="display: ${this.options.enableVoiceInput ? 'inline-flex' : 'none'}">
                            🎤
                        </button>
                        <button class="context-btn" title="Update Context">👤</button>
                    </div>
                    <div class="message-input">
                        <textarea
                            id="enhanced-message-input"
                            placeholder="Ask me anything about clubs, events, or get personalized recommendations..."
                            rows="1"
                            maxlength="1000"
                        ></textarea>
                        <button class="send-btn" id="enhanced-send-btn" disabled>
                            <span class="send-icon">➤</span>
                            <span class="typing-text">Thinking...</span>
                        </button>
                    </div>
                    <div class="input-footer">
                        <div class="service-status">
                            <span class="status-indicator"></span>
                            <span class="status-text">Connecting...</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add to DOM
        document.body.appendChild(this.widget);

        // Cache elements
        this.messagesContainer = document.getElementById('enhanced-messages');
        this.recommendationsContainer = document.getElementById('enhanced-recommendations');
        this.messageInput = document.getElementById('enhanced-message-input');
        this.sendBtn = document.getElementById('enhanced-send-btn');
        this.statusIndicator = this.widget.querySelector('.status-indicator');
        this.statusText = this.widget.querySelector('.status-text');
    }

    bindEvents() {
        // Send message on button click
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        // Send message on Enter key
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Enable send button when input has content
        this.messageInput.addEventListener('input', () => {
            this.sendBtn.disabled = !this.messageInput.value.trim();
        });

        // Minimize widget
        this.widget.querySelector('.minimize-btn').addEventListener('click', () => {
            this.toggleMinimize();
        });

        // Close widget
        this.widget.querySelector('.close-btn').addEventListener('click', () => {
            this.toggle();
        });

        // Context update
        this.widget.querySelector('.context-btn').addEventListener('click', () => {
            this.updateUserContext();
        });

        // Voice input
        if (this.options.enableVoiceInput) {
            this.widget.querySelector('.voice-input-btn').addEventListener('click', () => {
                this.startVoiceInput();
            });
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;

        this.addMessage('user', message);
        this.messageInput.value = '';
        this.sendBtn.disabled = true;
        this.setTyping(true);

        try {
            const response = await this.callEnhancedAI(message);
            this.handleAIResponse(response);
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('ai', 'Sorry, there was an error processing your request. Please try again.');
        } finally {
            this.setTyping(false);
        }
    }

    async callEnhancedAI(message) {
        const payload = {
            message: message,
            context: this.userContext,
            session_id: this.currentSessionId
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

    handleAIResponse(response) {
        if (response.success) {
            // Add AI message
            this.addMessage('ai', response.message, {
                intent: response.intent?.primary_intent,
                context_used: response.context_used
            });

            // Update recommendations
            if (response.recommendations && response.recommendations.length > 0) {
                this.recommendations = response.recommendations;
                this.displayRecommendations();
            }

            // Update session
            this.currentSessionId = response.session_id || this.currentSessionId;
        } else {
            this.addMessage('ai', response.message || 'An error occurred. Please try again.');
        }
    }

    addMessage(sender, content, metadata = {}) {
        const message = {
            id: Date.now(),
            sender: sender,
            content: content,
            timestamp: new Date(),
            metadata: metadata
        };

        this.messages.push(message);
        this.displayMessage(message);

        // Limit message history
        if (this.messages.length > this.options.maxMessages) {
            this.messages.shift();
        }
    }

    displayMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = `message message-${message.sender}`;

        const timestamp = message.timestamp.toLocaleTimeString();

        if (this.options.enableMarkdown && sender === 'ai') {
            // Use marked.js for markdown rendering
            const renderedContent = marked.parse(message.content);
            messageElement.innerHTML = `
                <div class="message-content">${renderedContent}</div>
                <div class="message-meta">
                    <span class="timestamp">${timestamp}</span>
                    ${message.metadata.intent ? `<span class="intent">${message.metadata.intent}</span>` : ''}
                    ${message.metadata.context_used ? '<span class="context-badge">📚</span>' : ''}
                </div>
            `;
        } else {
            messageElement.innerHTML = `
                <div class="message-content">${this.escapeHtml(message.content)}</div>
                <div class="message-meta">
                    <span class="timestamp">${timestamp}</span>
                    ${message.metadata.intent ? `<span class="intent">${message.metadata.intent}</span>` : ''}
                    ${message.metadata.context_used ? '<span class="context-badge">📚</span>' : ''}
                </div>
            `;
        }

        this.messagesContainer.appendChild(messageElement);

        if (this.options.autoScroll) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }

    async loadInitialRecommendations() {
        if (!this.options.enableRecommendations) return;

        try {
            const response = await fetch(`${this.options.recommendationsUrl}?limit=5`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.recommendations = data.recommendations;
                    this.displayRecommendations();
                }
            }
        } catch (error) {
            console.error('Error loading initial recommendations:', error);
        }
    }

    displayRecommendations() {
        if (!this.options.showRecommendations || this.recommendations.length === 0) {
            this.recommendationsContainer.style.display = 'none';
            return;
        }

        this.recommendationsContainer.style.display = 'block';
        this.recommendationsContainer.innerHTML = '<div class="recommendations-header">🎯 Personalized Recommendations</div>';

        this.recommendations.forEach((rec, index) => {
            const recElement = document.createElement('div');
            recElement.className = 'recommendation-item';
            recElement.innerHTML = `
                <div class="recommendation-content">
                    <div class="recommendation-title">${rec.reason || 'Recommended for you'}</div>
                    <div class="recommendation-score">Confidence: ${(rec.score * 100).toFixed(0)}%</div>
                </div>
                <div class="recommendation-actions">
                    <button class="like-btn" data-club-id="${rec.club_id}" title="Like">
                        👍
                    </button>
                    <button class="dislike-btn" data-club-id="${rec.club_id}" title="Dislike">
                        👎
                    </button>
                </div>
            `;

            // Add event listeners for rating
            recElement.querySelector('.like-btn').addEventListener('click', () => {
                this.rateRecommendation(rec.club_id, 'like');
            });

            recElement.querySelector('.dislike-btn').addEventListener('click', () => {
                this.rateRecommendation(rec.club_id, 'dislike');
            });

            this.recommendationsContainer.appendChild(recElement);
        });
    }

    async rateRecommendation(clubId, rating) {
        try {
            const response = await fetch(this.options.rateRecommendationUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    club_id: clubId,
                    rating: rating === 'like' ? 5 : 1,
                    action: rating
                })
            });

            if (response.ok) {
                // Remove the recommendation from display
                const buttons = document.querySelectorAll(`[data-club-id="${clubId}"]`);
                buttons.forEach(btn => {
                    btn.parentElement.parentElement.style.opacity = '0.5';
                    btn.parentElement.innerHTML = '<span class="rated-text">Thanks!</span>';
                });
            }
        } catch (error) {
            console.error('Error rating recommendation:', error);
        }
    }

    async checkServiceHealth() {
        try {
            const response = await fetch(this.options.healthCheckUrl);
            const data = await response.json();

            if (data.status === 'healthy') {
                this.updateServiceStatus('healthy', 'AI Services Active');
            } else {
                this.updateServiceStatus('degraded', 'Some services may be limited');
            }
        } catch (error) {
            this.updateServiceStatus('error', 'Service connection failed');
        }
    }

    updateServiceStatus(status, text) {
        this.statusIndicator.className = `status-indicator ${status}`;
        this.statusText.textContent = text;
    }

    loadUserContext() {
        // Load context from localStorage or determine from page
        const savedContext = localStorage.getItem('enhanced_ai_context');
        if (savedContext) {
            this.userContext = JSON.parse(savedContext);
        } else {
            this.determineContextFromPage();
        }
    }

    determineContextFromPage() {
        // Try to determine context from current page
        const url = window.location.pathname;

        if (url.includes('/clubs/')) {
            this.userContext.page_type = 'clubs';
        } else if (url.includes('/events/')) {
            this.userContext.page_type = 'events';
        } else if (url.includes('/profile/')) {
            this.userContext.page_type = 'profile';
        }

        // Try to get city from page or IP
        this.detectLocation();

        // Try to get interests from page content
        this.detectInterests();
    }

    detectLocation() {
        // Simple location detection - in production you might use geolocation API
        const cityElement = document.querySelector('[data-city], .user-city, .location');
        if (cityElement) {
            this.userContext.city = cityElement.textContent.trim();
        }
    }

    detectInterests() {
        // Simple interest detection from page content
        const interestKeywords = ['спорт', 'хобби', 'профессия', 'ит', 'технологии', 'бизнес'];
        const pageText = document.body.textContent.toLowerCase();

        const detectedInterests = interestKeywords.filter(keyword =>
            pageText.includes(keyword)
        );

        if (detectedInterests.length > 0) {
            this.userContext.interests = detectedInterests;
        }
    }

    updateUserContext() {
        // Open context configuration modal
        const modal = document.createElement('div');
        modal.className = 'context-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Update Your Context</h3>
                <form id="context-form">
                    <div class="form-group">
                        <label for="context-city">City:</label>
                        <input type="text" id="context-city" value="${this.userContext.city || ''}" placeholder="e.g., Almaty">
                    </div>
                    <div class="form-group">
                        <label for="context-interests">Interests (comma-separated):</label>
                        <input type="text" id="context-interests" value="${this.userContext.interests?.join(', ') || ''}" placeholder="e.g., спорт, технологии">
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" id="cancel-context">Cancel</button>
                        <button type="submit" class="btn btn-primary">Save</button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);

        // Bind form events
        modal.querySelector('#context-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveUserContext();
            modal.remove();
        });

        modal.querySelector('#cancel-context').addEventListener('click', () => {
            modal.remove();
        });
    }

    saveUserContext() {
        const city = document.getElementById('context-city').value.trim();
        const interests = document.getElementById('context-interests').value
            .split(',')
            .map(interest => interest.trim())
            .filter(interest => interest);

        this.userContext = {
            ...this.userContext,
            city: city || undefined,
            interests: interests.length > 0 ? interests : undefined
        };

        // Save to localStorage
        localStorage.setItem('enhanced_ai_context', JSON.stringify(this.userContext));

        // Refresh recommendations with new context
        this.loadInitialRecommendations();
    }

    setTyping(typing) {
        this.isTyping = typing;
        this.sendBtn.innerHTML = typing
            ? '<span class="typing-text">Thinking...</span>'
            : '<span class="send-icon">➤</span>';
    }

    toggle() {
        this.isOpen = !this.isOpen;
        this.widget.classList.toggle('open', this.isOpen);

        if (this.isOpen) {
            this.messageInput.focus();
        }
    }

    toggleMinimize() {
        this.widget.classList.toggle('minimized');
    }

    startVoiceInput() {
        if (!('SpeechRecognition' in window) && !('webkitSpeechRecognition' in window)) {
            alert('Voice input is not supported in this browser.');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();

        recognition.onstart = () => {
            this.widget.querySelector('.voice-input-btn').classList.add('listening');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.messageInput.value = transcript;
            this.sendMessage();
        };

        recognition.onend = () => {
            this.widget.querySelector('.voice-input-btn').classList.remove('listening');
        };

        recognition.start();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : null;
    }

    // Public methods
    updateContext(newContext) {
        this.userContext = { ...this.userContext, ...newContext };
        localStorage.setItem('enhanced_ai_context', JSON.stringify(this.userContext));
    }

    clearMessages() {
        this.messages = [];
        this.messagesContainer.innerHTML = '';
    }

    destroy() {
        this.widget.remove();
    }
}

// Auto-initialize if data-enhanced-widget attribute is present
document.addEventListener('DOMContentLoaded', () => {
    if (document.body.hasAttribute('data-enhanced-widget')) {
        window.enhancedAIWidget = new EnhancedAIChatWidget();
    }
});

// Export for manual initialization
window.EnhancedAIChatWidget = EnhancedAIChatWidget;