/**
 * Enhanced AI Team Chat System with UI Improvements
 * Provides intelligent routing with quick actions and contextual help
 */

class EnhancedAITeamChat {
    constructor() {
        this.isWidgetVisible = false;
        this.currentMember = 'auto';
        this.conversationHistory = [];
        this.isTyping = false;
        this.quickActionsEnabled = true;
        this.contextualHelpEnabled = true;
        
        this.memberProfiles = {
            'auto': {
                name: 'Auto-Route',
                role: 'Smart Routing',
                avatar: 'fas fa-robot',
                description: 'Automatically routes your question to the best specialist',
                color: '#6c757d'
            },
            'sarah': {
                name: 'Sarah Chen',
                role: 'Market Analyst',
                avatar: 'fas fa-chart-line',
                description: 'Stock analysis, market trends, and trading strategies',
                color: '#28a745'
            },
            'alex': {
                name: 'Alex Rodriguez',
                role: 'Technical Support',
                avatar: 'fas fa-tools',
                description: 'Platform issues, troubleshooting, and technical help',
                color: '#dc3545'
            },
            'maria': {
                name: 'Maria Santos',
                role: 'Customer Success',
                avatar: 'fas fa-graduation-cap',
                description: 'Feature guidance, tutorials, and onboarding help',
                color: '#007bff'
            }
        };
        
        this.quickActionTemplates = {
            'stock_search': {
                text: '🔍 Search Stocks',
                action: () => this.navigateToSection('stocks'),
                keywords: ['stock', 'search', 'ticker', 'symbol', 'company']
            },
            'portfolio_view': {
                text: '📊 View Portfolio',
                action: () => this.navigateToSection('portfolio'),
                keywords: ['portfolio', 'holdings', 'investments', 'balance']
            },
            'market_analysis': {
                text: '📈 Market Insights',
                action: () => this.navigateToSection('dashboard'),
                keywords: ['market', 'analysis', 'trends', 'insights']
            },
            'help_center': {
                text: '❓ Help Center',
                action: () => this.showHelpCenter(),
                keywords: ['help', 'tutorial', 'guide', 'learn', 'how']
            },
            'account_settings': {
                text: '⚙️ Settings',
                action: () => this.showAccountSettings(),
                keywords: ['account', 'settings', 'profile', 'preferences']
            }
        };
        
        this.init();
    }

    init() {
        this.createEnhancedWidget();
        this.bindEvents();
        this.loadTeamStatus();
        this.initializeContextualHelp();
        
        console.log('Enhanced AI Team Chat System initialized');
    }

    createEnhancedWidget() {
        // Create enhanced launcher with better visibility
        const launcher = document.getElementById('ai-team-launcher') || this.createLauncher();
        
        // Ensure launcher is visible with enhanced styling
        launcher.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #007bff, #28a745);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 1050;
            box-shadow: 0 4px 20px rgba(0, 123, 255, 0.3);
            transition: all 0.3s ease;
            animation: pulse 2s infinite;
        `;
        
        launcher.innerHTML = `
            <i class="fas fa-robot" style="color: white; font-size: 24px;"></i>
        `;
        
        // Add pulse animation
        this.addPulseAnimation();
        
        console.log('Enhanced AI Team launcher created');
    }
    
    createLauncher() {
        const launcher = document.createElement('div');
        launcher.id = 'ai-team-launcher';
        launcher.className = 'enhanced-ai-team-launcher';
        document.body.appendChild(launcher);
        return launcher;
    }
    
    addPulseAnimation() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes pulse {
                0% { box-shadow: 0 4px 20px rgba(0, 123, 255, 0.3); }
                50% { box-shadow: 0 6px 30px rgba(0, 123, 255, 0.5); }
                100% { box-shadow: 0 4px 20px rgba(0, 123, 255, 0.3); }
            }
            
            .enhanced-ai-team-launcher:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 25px rgba(0, 123, 255, 0.4) !important;
            }
            
            .quick-actions-container {
                margin-top: 15px;
                padding: 15px;
                background: rgba(0, 123, 255, 0.1);
                border-radius: 10px;
                border-left: 4px solid #007bff;
            }
            
            .quick-actions-title {
                font-weight: bold;
                color: #007bff;
                margin-bottom: 10px;
                font-size: 0.9em;
            }
            
            .quick-action-btn {
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 0.85em;
                transition: all 0.2s ease;
                border: 1px solid #007bff;
                background: transparent;
                color: #007bff;
            }
            
            .quick-action-btn:hover {
                background: #007bff;
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
            }
            
            .contextual-help-card {
                background: linear-gradient(135deg, #28a745, #20c997);
                color: white;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .contextual-help-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(40, 167, 69, 0.3);
            }
            
            .typing-indicator-enhanced {
                display: flex;
                align-items: center;
                padding: 10px;
                color: #6c757d;
                font-style: italic;
            }
            
            .typing-dots {
                display: inline-flex;
                align-items: center;
                margin-left: 10px;
            }
            
            .typing-dots span {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: #007bff;
                margin: 0 2px;
                animation: typing 1.4s infinite ease-in-out;
            }
            
            .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
            .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
            
            @keyframes typing {
                0%, 80%, 100% { transform: scale(0); }
                40% { transform: scale(1); }
            }
        `;
        document.head.appendChild(style);
    }

    bindEvents() {
        const launcher = document.getElementById('ai-team-launcher');
        if (launcher) {
            launcher.addEventListener('click', () => {
                this.toggleWidget();
                console.log('AI Team launcher clicked - Enhanced version');
            });
        }
    }

    async sendEnhancedMessage(message) {
        if (!message.trim()) return;
        
        // Add user message to conversation
        this.addMessageToConversation('user', message);
        
        // Show enhanced typing indicator
        this.showEnhancedTypingIndicator();
        
        // Add contextual quick actions before sending
        this.suggestQuickActions(message);
        
        try {
            const response = await fetch('/api/ai-team/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: message,
                    member: this.currentMember,
                    enhanced: true
                })
            });
            
            const data = await response.json();
            
            if (data.success && data.response) {
                this.hideTypingIndicator();
                
                const memberName = data.response.member || 'AI Assistant';
                const responseMessage = data.response.message || 'I understand your question and will help you with that.';
                
                // Add response with enhanced formatting
                this.addEnhancedMessageToConversation('bot', responseMessage, memberName);
                
                // Add contextual help based on response
                this.addContextualHelp(data.response);
                
                // Add post-response quick actions
                this.addResponseQuickActions(data.response);
                
            } else {
                this.hideTypingIndicator();
                this.addMessageToConversation('bot', 'I apologize, but I\'m having trouble processing your request. Let me connect you with a human agent.', 'System');
                this.offerHumanSupport();
            }
            
        } catch (error) {
            console.error('Enhanced chat error:', error);
            this.hideTypingIndicator();
            this.addMessageToConversation('bot', 'I\'m experiencing technical difficulties. Our technical team has been automatically notified.', 'System');
            this.showTechnicalSupport();
        }
        
        // Clear input with enhanced feedback
        const messageInput = document.getElementById('ai-team-message-input');
        if (messageInput) {
            messageInput.value = '';
            messageInput.focus();
        }
    }

    showEnhancedTypingIndicator() {
        const chatContainer = document.getElementById('ai-team-messages');
        if (!chatContainer) return;
        
        const typingIndicator = document.createElement('div');
        typingIndicator.id = 'typing-indicator';
        typingIndicator.className = 'typing-indicator-enhanced';
        typingIndicator.innerHTML = `
            <i class="fas fa-robot" style="color: #007bff;"></i>
            <span style="margin-left: 10px;">AI is thinking</span>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        chatContainer.appendChild(typingIndicator);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    suggestQuickActions(message) {
        if (!this.quickActionsEnabled) return;
        
        const messageLower = message.toLowerCase();
        const relevantActions = [];
        
        // Find relevant quick actions based on message content
        for (const [key, action] of Object.entries(this.quickActionTemplates)) {
            if (action.keywords.some(keyword => messageLower.includes(keyword))) {
                relevantActions.push(action);
            }
        }
        
        if (relevantActions.length > 0) {
            this.displayQuickActions(relevantActions);
        }
    }

    addResponseQuickActions(response) {
        const actions = [];
        const message = (response.message || '').toLowerCase();
        
        // Smart action suggestions based on response content
        if (message.includes('search') || message.includes('stock')) {
            actions.push(this.quickActionTemplates.stock_search);
        }
        
        if (message.includes('portfolio') || message.includes('investment')) {
            actions.push(this.quickActionTemplates.portfolio_view);
        }
        
        if (message.includes('market') || message.includes('analysis')) {
            actions.push(this.quickActionTemplates.market_analysis);
        }
        
        if (message.includes('help') || message.includes('guide')) {
            actions.push(this.quickActionTemplates.help_center);
        }
        
        // Always offer additional help
        actions.push({
            text: '💬 Continue Chat',
            action: () => this.focusMessageInput()
        });
        
        if (actions.length > 0) {
            this.displayQuickActions(actions);
        }
    }

    displayQuickActions(actions) {
        const chatContainer = document.getElementById('ai-team-messages');
        if (!chatContainer || actions.length === 0) return;
        
        const quickActionsHtml = `
            <div class="quick-actions-container">
                <div class="quick-actions-title">
                    <i class="fas fa-magic"></i> Quick Actions
                </div>
                <div class="quick-actions-buttons">
                    ${actions.map((action, index) => 
                        `<button class="btn btn-sm quick-action-btn me-2 mb-2" 
                         onclick="window.enhancedAITeamChat.executeQuickAction(${index})" 
                         data-action-index="${index}">
                            ${action.text}
                        </button>`
                    ).join('')}
                </div>
            </div>
        `;
        
        // Store actions for execution
        this.currentQuickActions = actions;
        
        // Add to chat
        const actionContainer = document.createElement('div');
        actionContainer.innerHTML = quickActionsHtml;
        chatContainer.appendChild(actionContainer);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    executeQuickAction(index) {
        if (this.currentQuickActions && this.currentQuickActions[index]) {
            this.currentQuickActions[index].action();
        }
    }

    addContextualHelp(response) {
        if (!this.contextualHelpEnabled) return;
        
        const helpSuggestions = this.generateContextualHelp(response);
        if (helpSuggestions.length > 0) {
            this.displayContextualHelp(helpSuggestions);
        }
    }

    generateContextualHelp(response) {
        const suggestions = [];
        const message = (response.message || '').toLowerCase();
        
        // Context-aware help suggestions
        if (message.includes('stock') && !message.includes('search')) {
            suggestions.push({
                title: 'Stock Search Tips',
                description: 'Try searching by company name (Apple) or ticker (AAPL)',
                action: () => this.showStockSearchTips()
            });
        }
        
        if (message.includes('portfolio') && !message.includes('view')) {
            suggestions.push({
                title: 'Portfolio Management',
                description: 'Learn how to track and optimize your investments',
                action: () => this.showPortfolioTips()
            });
        }
        
        if (message.includes('beginner') || message.includes('start')) {
            suggestions.push({
                title: 'Getting Started Guide',
                description: 'Complete walkthrough for new investors',
                action: () => this.showGettingStarted()
            });
        }
        
        return suggestions;
    }

    displayContextualHelp(suggestions) {
        const chatContainer = document.getElementById('ai-team-messages');
        if (!chatContainer) return;
        
        const helpHtml = `
            <div class="contextual-help-container mt-3">
                <div class="contextual-help-title">
                    <i class="fas fa-lightbulb"></i> Helpful Resources
                </div>
                ${suggestions.map((suggestion, index) => 
                    `<div class="contextual-help-card" 
                     onclick="window.enhancedAITeamChat.executeHelpAction(${index})">
                        <div class="help-card-title">${suggestion.title}</div>
                        <div class="help-card-description">${suggestion.description}</div>
                    </div>`
                ).join('')}
            </div>
        `;
        
        this.currentHelpSuggestions = suggestions;
        
        const helpContainer = document.createElement('div');
        helpContainer.innerHTML = helpHtml;
        chatContainer.appendChild(helpContainer);
    }

    executeHelpAction(index) {
        if (this.currentHelpSuggestions && this.currentHelpSuggestions[index]) {
            this.currentHelpSuggestions[index].action();
        }
    }

    // Navigation and utility methods
    navigateToSection(section) {
        this.hideWidget();
        if (typeof showSection === 'function') {
            showSection(section);
        }
        this.showNotification(`Navigated to ${section}`, 'success');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed ai-team-notification`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 2000; max-width: 300px;';
        notification.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 3000);
    }

    focusMessageInput() {
        const messageInput = document.getElementById('ai-team-message-input');
        if (messageInput) {
            messageInput.focus();
        }
    }

    // Enhanced member-specific improvements
    addEnhancedMessageToConversation(sender, message, memberName) {
        const chatContainer = document.getElementById('ai-team-messages');
        if (!chatContainer) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message enhanced-message`;
        
        if (sender === 'bot' && memberName) {
            const memberProfile = this.getMemberProfile(memberName);
            messageElement.innerHTML = `
                <div class="message-header">
                    <i class="${memberProfile.avatar}" style="color: ${memberProfile.color}"></i>
                    <span class="member-name" style="color: ${memberProfile.color}">${memberProfile.name}</span>
                    <span class="member-role">${memberProfile.role}</span>
                    <span class="message-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                </div>
                <div class="message-content">${this.formatMessage(message)}</div>
            `;
        } else {
            messageElement.innerHTML = `
                <div class="message-content">${this.formatMessage(message)}</div>
            `;
        }
        
        chatContainer.appendChild(messageElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    getMemberProfile(memberName) {
        const firstName = memberName.toLowerCase().split(' ')[0];
        return this.memberProfiles[firstName] || this.memberProfiles['auto'];
    }

    formatMessage(message) {
        // Enhanced message formatting with emoji support
        return message
            .replace(/\b(recommend|suggest)\b/gi, '<strong>$1</strong>')
            .replace(/\b(\d+)%/g, '<span class="confidence-score">$1%</span>')
            .replace(/\b(buy|sell|hold)\b/gi, '<span class="trading-action">$1</span>');
    }

    // Initialize enhanced system
    initializeContextualHelp() {
        // Add CSS for enhanced styling
        const style = document.createElement('style');
        style.textContent = `
            .confidence-score {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
                padding: 2px 6px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 0.85em;
            }
            
            .trading-action {
                background: linear-gradient(45deg, #007bff, #6610f2);
                color: white;
                padding: 2px 6px;
                border-radius: 8px;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 0.8em;
            }
            
            .message-header {
                display: flex;
                align-items: center;
                margin-bottom: 8px;
                font-size: 0.9em;
            }
            
            .member-name {
                font-weight: bold;
                margin-left: 8px;
            }
            
            .member-role {
                margin-left: 8px;
                color: #6c757d;
                font-size: 0.85em;
            }
            
            .message-time {
                margin-left: auto;
                color: #6c757d;
                font-size: 0.75em;
            }
            
            .enhanced-message {
                margin-bottom: 15px;
                padding: 15px;
                border-radius: 12px;
                transition: all 0.2s ease;
            }
            
            .enhanced-message:hover {
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize enhanced AI team chat
window.enhancedAITeamChat = new EnhancedAITeamChat();