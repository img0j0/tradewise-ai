/**
 * AI Team Chat System
 * Provides intelligent routing to AI specialists for user support
 */

class AITeamChat {
    constructor() {
        this.isWidgetVisible = false;
        this.currentMember = 'auto';
        this.conversationHistory = [];
        this.isTyping = false;
        
        this.memberProfiles = {
            'auto': {
                name: 'Auto-Route',
                role: 'Smart Routing',
                avatar: 'fas fa-robot',
                description: 'Automatically routes your question to the best specialist'
            },
            'sarah': {
                name: 'Sarah Chen',
                role: 'Market Analyst',
                avatar: 'fas fa-chart-line',
                description: 'Stock analysis, market trends, and trading strategies'
            },
            'alex': {
                name: 'Alex Rodriguez',
                role: 'Technical Support',
                avatar: 'fas fa-tools',
                description: 'Platform issues, troubleshooting, and technical help'
            },
            'maria': {
                name: 'Maria Santos',
                role: 'Customer Success',
                avatar: 'fas fa-graduation-cap',
                description: 'Feature guidance, tutorials, and onboarding help'
            }
        };
        
        this.init();
    }

    init() {
        this.createWidget();
        this.bindEvents();
        this.loadTeamStatus();
        
        console.log('AI Team Chat System initialized');
    }

    createWidget() {
        // Widget is already created in HTML template
        // Just ensure it's properly initialized
        const widget = document.getElementById('ai-team-widget');
        const launcher = document.getElementById('ai-team-launcher');
        
        if (!widget || !launcher) {
            console.warn('AI Team widget elements not found - creating elements');
            this.createFallbackWidget();
            return;
        }
        
        // Show launcher by default
        launcher.style.display = 'flex';
        launcher.style.visibility = 'visible';
        console.log('AI Team launcher is now visible');
    }

    createFallbackWidget() {
        // Create launcher if missing
        const launcher = document.createElement('div');
        launcher.id = 'ai-team-launcher';
        launcher.className = 'ai-team-launcher';
        launcher.innerHTML = `
            <div class="launcher-icon">
                <i class="fas fa-users"></i>
            </div>
            <div class="launcher-tooltip">AI Support Team</div>
        `;
        
        // Add styles
        launcher.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            z-index: 999;
            transition: all 0.3s ease;
            color: white;
            font-size: 24px;
        `;
        
        document.body.appendChild(launcher);
        console.log('AI Team launcher created as fallback');
        
        // Bind click event
        launcher.addEventListener('click', () => {
            console.log('AI Team launcher clicked - opening simple chat');
            this.showSimpleChat();
        });
    }

    showSimpleChat() {
        // Simple fallback chat interface
        const message = prompt('Ask your question to our AI team:');
        if (message && message.trim()) {
            alert('Thank you! Our AI team will process your question: "' + message + '"');
            this.routeToAITeam(message);
        }
    }

    bindEvents() {
        // Launcher click
        const launcher = document.getElementById('ai-team-launcher');
        if (launcher) {
            launcher.addEventListener('click', () => this.toggleWidget());
        }

        // Widget controls
        const minimizeBtn = document.getElementById('minimize-team-widget');
        const closeBtn = document.getElementById('close-team-widget');
        
        if (minimizeBtn) minimizeBtn.addEventListener('click', () => this.minimizeWidget());
        if (closeBtn) closeBtn.addEventListener('click', () => this.closeWidget());

        // Team member selection
        const teamMembers = document.querySelectorAll('.team-member');
        teamMembers.forEach(member => {
            member.addEventListener('click', (e) => {
                const memberType = e.currentTarget.dataset.member;
                this.selectTeamMember(memberType);
            });
        });

        // Back to team list
        const backBtn = document.getElementById('back-to-team-list');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.showTeamList());
        }

        // Chat input
        const chatInput = document.getElementById('team-chat-input');
        const sendBtn = document.getElementById('send-team-message');
        
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }

        // Quick actions
        const quickActions = document.querySelectorAll('.quick-action-btn');
        quickActions.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleQuickAction(action);
            });
        });
    }

    toggleWidget() {
        const widget = document.getElementById('ai-team-widget');
        const launcher = document.getElementById('ai-team-launcher');
        
        if (!widget) return;
        
        if (this.isWidgetVisible) {
            this.closeWidget();
        } else {
            this.showWidget();
        }
    }

    showWidget() {
        const widget = document.getElementById('ai-team-widget');
        const launcher = document.getElementById('ai-team-launcher');
        
        if (!widget) return;
        
        widget.style.display = 'flex';
        widget.classList.add('show');
        widget.classList.remove('hide');
        
        if (launcher) {
            launcher.style.display = 'none';
        }
        
        this.isWidgetVisible = true;
        
        // Show team list by default
        this.showTeamList();
    }

    closeWidget() {
        const widget = document.getElementById('ai-team-widget');
        const launcher = document.getElementById('ai-team-launcher');
        
        if (!widget) return;
        
        widget.classList.add('hide');
        widget.classList.remove('show');
        
        setTimeout(() => {
            widget.style.display = 'none';
            if (launcher) {
                launcher.style.display = 'flex';
            }
        }, 300);
        
        this.isWidgetVisible = false;
    }

    minimizeWidget() {
        this.closeWidget();
    }

    selectTeamMember(memberType) {
        this.currentMember = memberType;
        this.showChatInterface();
        this.updateActiveMember();
        
        // Clear previous messages and show welcome
        this.clearChat();
        this.showWelcomeMessage();
        
        // Update selected state
        const teamMembers = document.querySelectorAll('.team-member');
        teamMembers.forEach(member => {
            member.classList.remove('selected');
            if (member.dataset.member === memberType) {
                member.classList.add('selected');
            }
        });
    }

    showTeamList() {
        const teamList = document.getElementById('team-members-list');
        const chatInterface = document.getElementById('team-chat-interface');
        
        if (teamList) teamList.style.display = 'block';
        if (chatInterface) chatInterface.style.display = 'none';
    }

    showChatInterface() {
        const teamList = document.getElementById('team-members-list');
        const chatInterface = document.getElementById('team-chat-interface');
        
        if (teamList) teamList.style.display = 'none';
        if (chatInterface) chatInterface.style.display = 'flex';
    }

    updateActiveMember() {
        const member = this.memberProfiles[this.currentMember];
        if (!member) return;
        
        const nameEl = document.getElementById('active-member-name');
        const roleEl = document.getElementById('active-member-role');
        const avatarEl = document.getElementById('active-member-avatar');
        
        if (nameEl) nameEl.textContent = member.name;
        if (roleEl) roleEl.textContent = member.role;
        if (avatarEl) {
            avatarEl.innerHTML = `<i class="${member.avatar}"></i>`;
        }
    }

    clearChat() {
        const messagesContainer = document.getElementById('team-chat-messages');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }
        this.conversationHistory = [];
    }

    showWelcomeMessage() {
        const member = this.memberProfiles[this.currentMember];
        let welcomeText = `Hi! I'm ${member.name}. ${member.description}. How can I help you today?`;
        
        if (this.currentMember === 'auto') {
            welcomeText = "Hi! I'll help route your question to the right specialist. What can I assist you with?";
        }
        
        this.addMessage(welcomeText, 'assistant', member.avatar);
    }

    sendMessage() {
        const input = document.getElementById('team-chat-input');
        if (!input) return;
        
        const message = input.value.trim();
        if (!message) return;
        
        // Add user message
        this.addMessage(message, 'user');
        input.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Send to AI team API
        this.routeToAITeam(message);
    }

    addMessage(text, sender, avatar = null) {
        const messagesContainer = document.getElementById('team-chat-messages');
        if (!messagesContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender === 'user' ? 'user-message' : ''}`;
        
        const currentTime = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        let avatarIcon = avatar || (sender === 'user' ? 'fas fa-user' : this.memberProfiles[this.currentMember].avatar);
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="${avatarIcon}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${text}</div>
                <div class="message-time">${currentTime}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Store in conversation history
        this.conversationHistory.push({
            text: text,
            sender: sender,
            timestamp: new Date(),
            member: this.currentMember
        });
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('team-chat-messages');
        if (!messagesContainer) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        typingDiv.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        this.isTyping = true;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
        this.isTyping = false;
    }

    async routeToAITeam(query) {
        try {
            const response = await fetch('/api/ai-team/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    preferred_member: this.currentMember === 'auto' ? null : this.currentMember
                })
            });
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            if (data.success && data.response) {
                const aiResponse = data.response;
                
                // Update current member if AI routed to different specialist
                if (aiResponse.member && aiResponse.member !== this.currentMember) {
                    const memberKey = this.findMemberKey(aiResponse.member);
                    if (memberKey && memberKey !== this.currentMember) {
                        this.currentMember = memberKey;
                        this.updateActiveMember();
                        
                        // Add routing message
                        this.addMessage(`I'm routing you to ${aiResponse.member} who specializes in this area.`, 'assistant');
                    }
                }
                
                // Add AI response
                this.addMessage(aiResponse.message || "I'm here to help! What would you like to know?", 'assistant');
                
                // Show suggested actions if provided
                if (aiResponse.suggested_actions && aiResponse.suggested_actions.length > 0) {
                    this.showSuggestedActions(aiResponse.suggested_actions);
                }
                
                // Show educational resources if provided
                if (aiResponse.educational_resources && aiResponse.educational_resources.length > 0) {
                    this.showEducationalResources(aiResponse.educational_resources);
                }
                
            } else {
                this.addMessage("I apologize, but I'm having trouble processing your request right now. Please try again.", 'assistant');
            }
            
        } catch (error) {
            console.error('Error routing to AI team:', error);
            this.hideTypingIndicator();
            this.addMessage("I'm experiencing some technical difficulties. Please try your question again.", 'assistant');
        }
    }

    findMemberKey(memberName) {
        for (const [key, profile] of Object.entries(this.memberProfiles)) {
            if (profile.name === memberName) {
                return key;
            }
        }
        return null;
    }

    showSuggestedActions(actions) {
        const messagesContainer = document.getElementById('team-chat-messages');
        if (!messagesContainer) return;
        
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'suggested-actions';
        
        let actionsHTML = '<div class="actions-title">Suggested actions:</div>';
        actions.forEach(action => {
            actionsHTML += `<button class="action-btn" onclick="aiTeamChat.handleSuggestedAction('${action}')">${action}</button>`;
        });
        
        actionsDiv.innerHTML = actionsHTML;
        messagesContainer.appendChild(actionsDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showEducationalResources(resources) {
        const messagesContainer = document.getElementById('team-chat-messages');
        if (!messagesContainer) return;
        
        const resourcesDiv = document.createElement('div');
        resourcesDiv.className = 'educational-resources';
        
        let resourcesHTML = '<div class="resources-title">Educational resources:</div>';
        resources.forEach(resource => {
            resourcesHTML += `<div class="resource-item"><i class="fas fa-book"></i> ${resource}</div>`;
        });
        
        resourcesDiv.innerHTML = resourcesHTML;
        messagesContainer.appendChild(resourcesDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    handleQuickAction(action) {
        const actionQueries = {
            'help': "I need help getting started with the platform",
            'trading': "I have a question about trading and investments", 
            'technical': "I'm experiencing a technical issue with the platform",
            'features': "Can you help me learn about the platform features?"
        };
        
        const query = actionQueries[action] || action;
        
        // Set input value and send
        const input = document.getElementById('team-chat-input');
        if (input) {
            input.value = query;
            this.sendMessage();
        }
    }

    handleSuggestedAction(action) {
        // Handle suggested actions from AI responses
        const actionHandlers = {
            'Search for specific stocks': () => {
                // Focus on search tab and show search interface
                if (window.showSearchTab) {
                    window.showSearchTab();
                    this.closeWidget();
                }
            },
            'View market overview': () => {
                // Focus on dashboard
                if (window.showDashboardTab) {
                    window.showDashboardTab();
                    this.closeWidget();
                }
            },
            'Check portfolio analysis': () => {
                // Focus on portfolio tab
                if (window.showPortfolioTab) {
                    window.showPortfolioTab();
                    this.closeWidget();
                }
            }
        };
        
        if (actionHandlers[action]) {
            actionHandlers[action]();
        } else {
            // Default: treat as a new query
            const input = document.getElementById('team-chat-input');
            if (input) {
                input.value = action;
                this.sendMessage();
            }
        }
    }

    async loadTeamStatus() {
        try {
            const response = await fetch('/api/ai-team/status');
            const data = await response.json();
            
            if (data.success && data.team_status) {
                this.updateTeamStatusDisplay(data.team_status);
            }
        } catch (error) {
            console.error('Error loading team status:', error);
        }
    }

    updateTeamStatusDisplay(status) {
        const statusEl = document.getElementById('team-status');
        if (statusEl && status.members) {
            const onlineCount = status.members.length;
            statusEl.textContent = `${onlineCount} specialists online`;
        }
    }

    showNotification(count = 1) {
        const badge = document.getElementById('team-notification-badge');
        const countEl = document.getElementById('team-notification-count');
        
        if (badge && countEl) {
            countEl.textContent = count;
            badge.style.display = 'flex';
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                badge.style.display = 'none';
            }, 5000);
        }
    }

    // Public method to trigger team chat from external sources
    static openWithQuery(query, memberType = 'auto') {
        if (window.aiTeamChat) {
            window.aiTeamChat.showWidget();
            
            if (memberType !== 'auto') {
                window.aiTeamChat.selectTeamMember(memberType);
            }
            
            if (query) {
                setTimeout(() => {
                    const input = document.getElementById('team-chat-input');
                    if (input) {
                        input.value = query;
                        window.aiTeamChat.sendMessage();
                    }
                }, 500);
            }
        }
    }
}

// Initialize AI Team Chat when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing AI Team Chat...');
    
    // Wait for page to fully load before initializing
    setTimeout(() => {
        try {
            window.aiTeamChat = new AITeamChat();
            console.log('AI Team Chat System ready');
        } catch (error) {
            console.error('Error initializing AI Team Chat:', error);
        }
    }, 1000);
});

// Export for external access
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AITeamChat;
}