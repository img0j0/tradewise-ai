// Smart AI Assistant Upgrades
class SmartAssistant {
    constructor() {
        this.conversationHistory = [];
        this.userPreferences = this.loadUserPreferences();
        this.contextAware = true;
        this.learningMode = true;
        this.initialize();
    }

    initialize() {
        this.setupEnhancedUI();
        this.setupContextualResponses();
        this.setupLearningSystem();
        this.setupSmartSuggestions();
        this.setupVoiceSupport();
        this.setupProactiveInsights();
    }

    setupEnhancedUI() {
        // Enhanced assistant widget with smart features
        const assistantWidget = document.getElementById('ai-assistant');
        if (assistantWidget) {
            // Add typing indicator
            const typingIndicator = document.createElement('div');
            typingIndicator.id = 'typing-indicator';
            typingIndicator.className = 'typing-indicator d-none';
            typingIndicator.innerHTML = `
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
                <small class="text-muted">AI is thinking...</small>
            `;
            assistantWidget.appendChild(typingIndicator);

            // Add smart suggestions panel
            const suggestionsPanel = document.createElement('div');
            suggestionsPanel.id = 'smart-suggestions';
            suggestionsPanel.className = 'smart-suggestions d-none';
            suggestionsPanel.innerHTML = `
                <div class="suggestions-header">
                    <h6 class="mb-2">Smart Suggestions</h6>
                </div>
                <div class="suggestions-list" id="suggestions-list"></div>
            `;
            assistantWidget.appendChild(suggestionsPanel);

            // Add context panel
            const contextPanel = document.createElement('div');
            contextPanel.id = 'context-panel';
            contextPanel.className = 'context-panel';
            contextPanel.innerHTML = `
                <div class="context-info">
                    <small class="text-muted">
                        <i class="fas fa-brain me-1"></i>
                        Context: <span id="current-context">Dashboard</span>
                    </small>
                </div>
            `;
            assistantWidget.appendChild(contextPanel);
        }
    }

    setupContextualResponses() {
        // Track current page context
        this.currentContext = this.detectContext();
        
        // Update context when user switches tabs
        document.addEventListener('click', (e) => {
            if (e.target.matches('.nav-link')) {
                setTimeout(() => {
                    this.currentContext = this.detectContext();
                    this.updateContextDisplay();
                    this.generateContextualSuggestions();
                }, 100);
            }
        });
    }

    detectContext() {
        const activeTab = document.querySelector('.nav-link.active');
        if (activeTab) {
            return activeTab.textContent.trim();
        }
        return 'Dashboard';
    }

    updateContextDisplay() {
        const contextElement = document.getElementById('current-context');
        if (contextElement) {
            contextElement.textContent = this.currentContext;
        }
    }

    setupLearningSystem() {
        // Learn from user interactions
        this.userPatterns = {
            preferredStocks: [],
            tradingStyle: 'conservative',
            activeHours: [],
            riskTolerance: 'medium'
        };

        // Track user behavior
        this.trackUserBehavior();
    }

    trackUserBehavior() {
        // Track stock viewing patterns
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-symbol]')) {
                const symbol = e.target.dataset.symbol;
                this.recordStockInteraction(symbol);
            }
        });

        // Track time spent on different sections
        let sectionStartTime = Date.now();
        document.addEventListener('click', (e) => {
            if (e.target.matches('.nav-link')) {
                const timeSpent = Date.now() - sectionStartTime;
                this.recordSectionTime(this.currentContext, timeSpent);
                sectionStartTime = Date.now();
            }
        });
    }

    recordStockInteraction(symbol) {
        const existing = this.userPatterns.preferredStocks.find(s => s.symbol === symbol);
        if (existing) {
            existing.interactions++;
            existing.lastViewed = new Date();
        } else {
            this.userPatterns.preferredStocks.push({
                symbol: symbol,
                interactions: 1,
                lastViewed: new Date()
            });
        }
        this.saveUserPreferences();
    }

    recordSectionTime(section, timeSpent) {
        // Record time spent in each section for personalization
        if (!this.userPatterns.sectionTime) {
            this.userPatterns.sectionTime = {};
        }
        this.userPatterns.sectionTime[section] = (this.userPatterns.sectionTime[section] || 0) + timeSpent;
        this.saveUserPreferences();
    }

    setupSmartSuggestions() {
        // Generate contextual suggestions based on current view
        this.generateContextualSuggestions();
        
        // Update suggestions every 30 seconds
        setInterval(() => {
            this.generateContextualSuggestions();
        }, 30000);
    }

    generateContextualSuggestions() {
        const suggestions = [];
        
        switch (this.currentContext) {
            case 'Dashboard':
                suggestions.push(
                    { text: "Show my portfolio performance", action: "portfolio_performance" },
                    { text: "What are today's top movers?", action: "top_movers" },
                    { text: "Any new alerts for me?", action: "check_alerts" }
                );
                break;
            case 'Stocks':
                suggestions.push(
                    { text: "Find undervalued stocks", action: "undervalued_stocks" },
                    { text: "Show technical analysis", action: "technical_analysis" },
                    { text: "Compare with my watchlist", action: "compare_watchlist" }
                );
                break;
            case 'Portfolio':
                suggestions.push(
                    { text: "Optimize my portfolio", action: "optimize_portfolio" },
                    { text: "Show risk analysis", action: "risk_analysis" },
                    { text: "Suggest rebalancing", action: "rebalancing" }
                );
                break;
            case 'Advanced':
                suggestions.push(
                    { text: "Train AI with latest data", action: "train_ai" },
                    { text: "Create new strategy", action: "create_strategy" },
                    { text: "Backtest performance", action: "backtest" }
                );
                break;
        }

        // Add personalized suggestions based on user patterns
        this.addPersonalizedSuggestions(suggestions);
        
        this.displaySuggestions(suggestions);
    }

    addPersonalizedSuggestions(suggestions) {
        // Add suggestions based on user's preferred stocks
        const topStocks = this.userPatterns.preferredStocks
            .sort((a, b) => b.interactions - a.interactions)
            .slice(0, 2);
        
        topStocks.forEach(stock => {
            suggestions.push({
                text: `Analyze ${stock.symbol}`,
                action: `analyze_${stock.symbol}`,
                personalized: true
            });
        });
    }

    displaySuggestions(suggestions) {
        const suggestionsList = document.getElementById('suggestions-list');
        if (!suggestionsList) return;

        suggestionsList.innerHTML = '';
        
        suggestions.slice(0, 4).forEach(suggestion => {
            const suggestionElement = document.createElement('div');
            suggestionElement.className = `suggestion-item ${suggestion.personalized ? 'personalized' : ''}`;
            suggestionElement.innerHTML = `
                <button class="btn btn-sm btn-outline-primary w-100 mb-1" 
                        onclick="window.smartAssistant.handleSuggestion('${suggestion.action}')">
                    ${suggestion.personalized ? '<i class="fas fa-star me-1"></i>' : ''}
                    ${suggestion.text}
                </button>
            `;
            suggestionsList.appendChild(suggestionElement);
        });

        // Show suggestions panel
        document.getElementById('smart-suggestions').classList.remove('d-none');
    }

    handleSuggestion(action) {
        // Handle suggestion clicks
        switch (action) {
            case 'portfolio_performance':
                this.sendMessage('Show me my portfolio performance analysis');
                break;
            case 'top_movers':
                this.sendMessage('What are today\'s top moving stocks?');
                break;
            case 'check_alerts':
                this.sendMessage('Show me my active alerts');
                break;
            case 'undervalued_stocks':
                this.sendMessage('Find undervalued stocks in the market');
                break;
            case 'technical_analysis':
                this.sendMessage('Show technical analysis for trending stocks');
                break;
            case 'optimize_portfolio':
                this.sendMessage('How can I optimize my portfolio?');
                break;
            case 'risk_analysis':
                this.sendMessage('Analyze the risk in my portfolio');
                break;
            case 'train_ai':
                this.sendMessage('Train the AI model with latest market data');
                break;
            default:
                if (action.startsWith('analyze_')) {
                    const symbol = action.replace('analyze_', '');
                    this.sendMessage(`Provide detailed analysis for ${symbol}`);
                }
        }
    }

    setupVoiceSupport() {
        // Voice recognition setup
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            this.voiceSupport = true;
            this.setupVoiceRecognition();
        }
    }

    setupVoiceRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.sendMessage(transcript);
        };

        // Add voice button to chat interface
        const voiceButton = document.createElement('button');
        voiceButton.className = 'btn btn-sm btn-outline-primary ms-2';
        voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        voiceButton.onclick = () => this.startVoiceRecognition();
        
        const chatInput = document.querySelector('#ai-chat-input');
        if (chatInput && chatInput.parentElement) {
            chatInput.parentElement.appendChild(voiceButton);
        }
    }

    startVoiceRecognition() {
        if (this.recognition) {
            this.recognition.start();
        }
    }

    setupProactiveInsights() {
        // Proactive insights based on market conditions
        this.checkMarketConditions();
        
        // Check every 5 minutes
        setInterval(() => {
            this.checkMarketConditions();
        }, 300000);
    }

    async checkMarketConditions() {
        try {
            const response = await fetch('/api/market-overview');
            const data = await response.json();
            
            // Generate proactive insights
            this.generateProactiveInsights(data);
        } catch (error) {
            console.error('Error checking market conditions:', error);
        }
    }

    generateProactiveInsights(marketData) {
        const insights = [];
        
        // Market volatility insights
        if (marketData.volatility > 0.3) {
            insights.push({
                type: 'warning',
                message: 'High market volatility detected. Consider reviewing your risk exposure.',
                action: 'risk_review'
            });
        }
        
        // Opportunity insights
        if (marketData.opportunities && marketData.opportunities.length > 0) {
            insights.push({
                type: 'opportunity',
                message: `${marketData.opportunities.length} potential opportunities identified.`,
                action: 'show_opportunities'
            });
        }
        
        this.displayProactiveInsights(insights);
    }

    displayProactiveInsights(insights) {
        if (insights.length === 0) return;
        
        // Show insights as notifications
        insights.forEach(insight => {
            this.showInsightNotification(insight);
        });
    }

    showInsightNotification(insight) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${insight.type === 'warning' ? 'warning' : 'info'} alert-dismissible fade show`;
        notification.innerHTML = `
            <i class="fas fa-brain me-2"></i>
            ${insight.message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(notification, container.firstChild);
            
            // Auto-dismiss after 10 seconds
            setTimeout(() => {
                notification.remove();
            }, 10000);
        }
    }

    sendMessage(message) {
        // Enhanced message sending with context
        const messageData = {
            message: message,
            context: this.currentContext,
            timestamp: new Date().toISOString(),
            userPreferences: this.userPreferences
        };
        
        // Send to AI assistant endpoint
        this.sendToAIAssistant(messageData);
    }

    async sendToAIAssistant(messageData) {
        try {
            this.showTypingIndicator();
            
            const response = await fetch('/api/ai-assistant', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(messageData)
            });
            
            const data = await response.json();
            
            this.hideTypingIndicator();
            this.displayAIResponse(data);
            
        } catch (error) {
            console.error('Error sending message to AI:', error);
            this.hideTypingIndicator();
        }
    }

    showTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.classList.remove('d-none');
        }
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.classList.add('d-none');
        }
    }

    displayAIResponse(response) {
        // Display AI response in chat interface
        const chatMessages = document.getElementById('ai-chat-messages');
        if (chatMessages) {
            const messageElement = document.createElement('div');
            messageElement.className = 'ai-message';
            messageElement.innerHTML = `
                <div class="message-content">
                    ${response.message}
                </div>
                <div class="message-timestamp">
                    ${new Date().toLocaleTimeString()}
                </div>
            `;
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    loadUserPreferences() {
        const saved = localStorage.getItem('smartAssistant_preferences');
        return saved ? JSON.parse(saved) : {
            preferredStocks: [],
            tradingStyle: 'conservative',
            riskTolerance: 'medium'
        };
    }

    saveUserPreferences() {
        localStorage.setItem('smartAssistant_preferences', JSON.stringify(this.userPatterns));
    }
}

// Initialize smart assistant
document.addEventListener('DOMContentLoaded', () => {
    window.smartAssistant = new SmartAssistant();
});

// Export for use in other modules
window.SmartAssistant = SmartAssistant;