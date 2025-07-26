/**
 * Tool Feedback System for TradeWise AI
 * Handles loading states, progress tracking, and user feedback for all tools
 */

class ToolFeedbackManager {
    constructor() {
        this.activePolls = new Map();
        this.pollInterval = 2500; // 2.5 seconds
        this.maxPollAttempts = 120; // 5 minutes max
        this.init();
    }

    init() {
        this.createNotificationContainer();
        this.bindToolEvents();
        console.log('Tool Feedback Manager initialized');
    }

    createNotificationContainer() {
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            container.innerHTML = `
                <style>
                .notification-container {
                    position: fixed;
                    top: 80px;
                    right: 20px;
                    z-index: 1050;
                    max-width: 400px;
                }
                .notification {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    margin-bottom: 10px;
                    padding: 16px;
                    border-left: 4px solid #007bff;
                    animation: slideIn 0.3s ease-out;
                    position: relative;
                }
                .notification.success {
                    border-left-color: #28a745;
                    background: linear-gradient(135deg, #f8f9fa 0%, #e8f5e8 100%);
                }
                .notification.error {
                    border-left-color: #dc3545;
                    background: linear-gradient(135deg, #f8f9fa 0%, #f8e8e8 100%);
                }
                .notification.warning {
                    border-left-color: #ffc107;
                    background: linear-gradient(135deg, #f8f9fa 0%, #fff8e1 100%);
                }
                .notification.info {
                    border-left-color: #17a2b8;
                    background: linear-gradient(135deg, #f8f9fa 0%, #e8f4f8 100%);
                }
                .notification-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 8px;
                }
                .notification-title {
                    font-weight: 600;
                    font-size: 14px;
                    margin: 0;
                }
                .notification-close {
                    background: none;
                    border: none;
                    font-size: 18px;
                    cursor: pointer;
                    color: #666;
                    padding: 0;
                    width: 20px;
                    height: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .notification-message {
                    font-size: 13px;
                    color: #555;
                    margin: 0;
                }
                .notification-progress {
                    margin-top: 12px;
                }
                .progress-bar {
                    width: 100%;
                    height: 6px;
                    background: #e9ecef;
                    border-radius: 3px;
                    overflow: hidden;
                }
                .progress-fill {
                    height: 100%;
                    background: #007bff;
                    border-radius: 3px;
                    transition: width 0.3s ease;
                    width: 0%;
                }
                .spinner {
                    display: inline-block;
                    width: 16px;
                    height: 16px;
                    border: 2px solid #e9ecef;
                    border-radius: 50%;
                    border-top-color: #007bff;
                    animation: spin 1s ease-in-out infinite;
                    margin-right: 8px;
                }
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
                @keyframes slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                /* Dark mode styles */
                .dark-mode .notification {
                    background: #2d3748;
                    color: #e2e8f0;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                }
                .dark-mode .notification.success {
                    background: linear-gradient(135deg, #2d3748 0%, #1a2e1a 100%);
                }
                .dark-mode .notification.error {
                    background: linear-gradient(135deg, #2d3748 0%, #2e1a1a 100%);
                }
                .dark-mode .notification.warning {
                    background: linear-gradient(135deg, #2d3748 0%, #2e2a1a 100%);
                }
                .dark-mode .notification.info {
                    background: linear-gradient(135deg, #2d3748 0%, #1a2a2e 100%);
                }
                .dark-mode .notification-message {
                    color: #cbd5e0;
                }
                .dark-mode .progress-bar {
                    background: #4a5568;
                }
                /* Mobile responsive */
                @media (max-width: 768px) {
                    .notification-container {
                        top: 60px;
                        right: 10px;
                        left: 10px;
                        max-width: none;
                    }
                    .notification {
                        padding: 12px;
                    }
                    .notification-title {
                        font-size: 13px;
                    }
                    .notification-message {
                        font-size: 12px;
                    }
                }
                </style>
            `;
            document.body.appendChild(container);
        }
    }

    bindToolEvents() {
        // Bind to all tool buttons with data-tool attribute
        document.addEventListener('click', (e) => {
            const toolButton = e.target.closest('[data-tool]');
            if (toolButton) {
                e.preventDefault();
                this.handleToolClick(toolButton);
            }
        });
    }

    async handleToolClick(button) {
        const toolName = button.dataset.tool;
        const toolParams = this.getToolParameters(button);
        
        // Set loading state
        this.setButtonLoading(button, true);
        
        // Show loading notification
        const notificationId = this.showNotification({
            type: 'info',
            title: this.getToolDisplayName(toolName),
            message: 'Starting analysis...',
            persistent: true,
            showProgress: true
        });

        try {
            // Call the appropriate tool endpoint
            const response = await this.callToolEndpoint(toolName, toolParams);
            
            if (response.task_id) {
                // Handle async task
                this.updateNotification(notificationId, {
                    message: 'Processing... This may take a few moments.',
                    showProgress: true
                });
                
                await this.pollTaskStatus(response.task_id, notificationId, button, toolName);
            } else if (response.success) {
                // Handle immediate response
                this.handleToolSuccess(response, notificationId, button, toolName);
            } else {
                // Handle error response
                this.handleToolError(response.error || 'Unknown error occurred', notificationId, button);
            }
        } catch (error) {
            console.error('Tool execution error:', error);
            this.handleToolError(error.message, notificationId, button);
        }
    }

    getToolParameters(button) {
        const form = button.closest('form');
        const params = {};
        
        if (form) {
            const formData = new FormData(form);
            for (let [key, value] of formData.entries()) {
                params[key] = value;
            }
        }
        
        // Get parameters from data attributes
        Object.keys(button.dataset).forEach(key => {
            if (key !== 'tool') {
                params[key] = button.dataset[key];
            }
        });
        
        return params;
    }

    async callToolEndpoint(toolName, params) {
        const endpoints = {
            'backtest': '/tools/premium/backtesting',
            'ai_insights': '/tools/ai/insights',
            'peer_comparison': '/tools/premium/peer-comparison',
            'market_scanner': '/tools/premium/market-scanner',
            'smart_alerts': '/tools/alerts/smart',
            'stock_analysis': '/tools/analysis/stocks',
            'enhanced_analysis': '/tools/ai/enhanced'
        };
        
        const endpoint = endpoints[toolName];
        if (!endpoint) {
            throw new Error(`Unknown tool: ${toolName}`);
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params)
        });
        
        return await response.json();
    }

    async pollTaskStatus(taskId, notificationId, button, toolName) {
        let pollCount = 0;
        
        const pollId = setInterval(async () => {
            pollCount++;
            
            if (pollCount > this.maxPollAttempts) {
                clearInterval(pollId);
                this.activePolls.delete(taskId);
                this.handleToolError('Task timed out', notificationId, button);
                return;
            }
            
            try {
                const response = await fetch(`/tools/task-status/${taskId}`);
                const statusData = await response.json();
                
                if (statusData.error) {
                    clearInterval(pollId);
                    this.activePolls.delete(taskId);
                    this.handleToolError(statusData.error, notificationId, button);
                    return;
                }
                
                // Update progress
                const progress = this.calculateProgress(statusData.status, pollCount);
                this.updateNotificationProgress(notificationId, progress);
                
                // Update message based on status
                let message = 'Processing...';
                if (statusData.status === 'processing') {
                    message = 'Analyzing data...';
                } else if (statusData.queue_position) {
                    message = `Queue position: ${statusData.queue_position}`;
                }
                
                this.updateNotification(notificationId, { message });
                
                // Check if completed
                if (statusData.status === 'completed') {
                    clearInterval(pollId);
                    this.activePolls.delete(taskId);
                    this.handleToolSuccess(statusData.result, notificationId, button, toolName);
                } else if (statusData.status === 'failed') {
                    clearInterval(pollId);
                    this.activePolls.delete(taskId);
                    this.handleToolError(statusData.error || 'Task failed', notificationId, button);
                }
                
            } catch (error) {
                console.error('Polling error:', error);
                // Continue polling on network errors
            }
        }, this.pollInterval);
        
        this.activePolls.set(taskId, pollId);
    }

    calculateProgress(status, pollCount) {
        switch (status) {
            case 'pending':
                return Math.min(10 + (pollCount * 2), 25);
            case 'processing':
                return Math.min(30 + (pollCount * 3), 85);
            case 'completed':
                return 100;
            case 'failed':
                return 0;
            default:
                return Math.min(pollCount * 2, 20);
        }
    }

    handleToolSuccess(result, notificationId, button, toolName) {
        this.setButtonLoading(button, false);
        
        this.updateNotification(notificationId, {
            type: 'success',
            title: `${this.getToolDisplayName(toolName)} Complete`,
            message: 'Analysis completed successfully!',
            showProgress: false,
            autoClose: 5000
        });
        
        // Display results based on tool type
        this.displayToolResults(result, toolName);
        
        // Add success indicator to button
        this.showButtonSuccess(button);
    }

    handleToolError(error, notificationId, button) {
        this.setButtonLoading(button, false);
        
        const userFriendlyError = this.getUserFriendlyError(error);
        
        this.updateNotification(notificationId, {
            type: 'error',
            title: 'Analysis Failed',
            message: userFriendlyError,
            showProgress: false,
            autoClose: 8000
        });
        
        // Add error indicator to button
        this.showButtonError(button);
    }

    getUserFriendlyError(error) {
        const errorMap = {
            'symbol not found': 'Invalid stock symbol. Please check the symbol and try again.',
            'api timeout': 'Request timed out. Please try again in a moment.',
            'rate limit': 'Too many requests. Please wait a moment before trying again.',
            'premium required': 'This feature requires a premium subscription.',
            'invalid input': 'Please check your input parameters and try again.',
            'market closed': 'Market data is not available while markets are closed.',
            'network error': 'Network connection issue. Please check your connection and try again.'
        };
        
        const errorLower = error.toLowerCase();
        for (const [key, message] of Object.entries(errorMap)) {
            if (errorLower.includes(key)) {
                return message;
            }
        }
        
        return `Analysis failed: ${error}. Please try again.`;
    }

    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<span class="spinner"></span>Processing...';
            button.classList.add('loading');
        } else {
            button.disabled = false;
            if (button.dataset.originalText) {
                button.innerHTML = button.dataset.originalText;
                delete button.dataset.originalText;
            }
            button.classList.remove('loading');
        }
    }

    showButtonSuccess(button) {
        button.classList.add('btn-success');
        setTimeout(() => {
            button.classList.remove('btn-success');
        }, 2000);
    }

    showButtonError(button) {
        button.classList.add('btn-danger');
        setTimeout(() => {
            button.classList.remove('btn-danger');
        }, 3000);
    }

    getToolDisplayName(toolName) {
        const names = {
            'backtest': 'Portfolio Backtest',
            'ai_insights': 'AI Insights',
            'peer_comparison': 'Peer Comparison',
            'market_scanner': 'Market Scanner',
            'smart_alerts': 'Smart Alerts',
            'stock_analysis': 'Stock Analysis',
            'enhanced_analysis': 'Enhanced Analysis'
        };
        return names[toolName] || toolName;
    }

    showNotification({ type = 'info', title, message, persistent = false, autoClose = 5000, showProgress = false }) {
        const id = 'notification-' + Date.now() + Math.random().toString(36).substr(2, 9);
        const container = document.getElementById('notification-container');
        
        const notification = document.createElement('div');
        notification.id = id;
        notification.className = `notification ${type}`;
        
        let progressHtml = '';
        if (showProgress) {
            progressHtml = `
                <div class="notification-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 0%"></div>
                    </div>
                </div>
            `;
        }
        
        notification.innerHTML = `
            <div class="notification-header">
                <div class="notification-title">${title}</div>
                <button class="notification-close" onclick="toolFeedback.closeNotification('${id}')">&times;</button>
            </div>
            <div class="notification-message">${message}</div>
            ${progressHtml}
        `;
        
        container.appendChild(notification);
        
        if (!persistent && autoClose) {
            setTimeout(() => {
                this.closeNotification(id);
            }, autoClose);
        }
        
        return id;
    }

    updateNotification(id, updates) {
        const notification = document.getElementById(id);
        if (!notification) return;
        
        if (updates.type) {
            notification.className = `notification ${updates.type}`;
        }
        
        if (updates.title) {
            const titleEl = notification.querySelector('.notification-title');
            if (titleEl) titleEl.textContent = updates.title;
        }
        
        if (updates.message) {
            const messageEl = notification.querySelector('.notification-message');
            if (messageEl) messageEl.textContent = updates.message;
        }
        
        if (updates.hasOwnProperty('showProgress')) {
            const progressEl = notification.querySelector('.notification-progress');
            if (updates.showProgress && !progressEl) {
                const progressHtml = `
                    <div class="notification-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%"></div>
                        </div>
                    </div>
                `;
                notification.insertAdjacentHTML('beforeend', progressHtml);
            } else if (!updates.showProgress && progressEl) {
                progressEl.remove();
            }
        }
        
        if (updates.autoClose) {
            setTimeout(() => {
                this.closeNotification(id);
            }, updates.autoClose);
        }
    }

    updateNotificationProgress(id, percentage) {
        const notification = document.getElementById(id);
        if (!notification) return;
        
        const progressFill = notification.querySelector('.progress-fill');
        if (progressFill) {
            progressFill.style.width = `${Math.min(percentage, 100)}%`;
        }
    }

    closeNotification(id) {
        const notification = document.getElementById(id);
        if (notification) {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }

    displayToolResults(result, toolName) {
        // This will be implemented to show results in appropriate UI components
        console.log('Tool results:', toolName, result);
        
        // For now, show a basic results notification
        if (result && typeof result === 'object') {
            let resultMessage = 'Analysis complete';
            
            if (result.recommendation) {
                resultMessage = `Recommendation: ${result.recommendation}`;
            } else if (result.analysis && result.analysis.recommendation) {
                resultMessage = `Recommendation: ${result.analysis.recommendation}`;
            }
            
            this.showNotification({
                type: 'success',
                title: 'Results Ready',
                message: resultMessage,
                autoClose: 8000
            });
        }
    }

    // Cleanup method to stop all active polls
    cleanup() {
        this.activePolls.forEach((pollId) => {
            clearInterval(pollId);
        });
        this.activePolls.clear();
    }
}

// Initialize the tool feedback system
const toolFeedback = new ToolFeedbackManager();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    toolFeedback.cleanup();
});

// CSS for additional button states
const additionalStyles = document.createElement('style');
additionalStyles.textContent = `
    .btn.loading {
        opacity: 0.7;
        cursor: not-allowed;
    }
    
    .btn-success {
        background-color: #28a745 !important;
        border-color: #28a745 !important;
        color: white !important;
    }
    
    .btn-danger {
        background-color: #dc3545 !important;
        border-color: #dc3545 !important;
        color: white !important;
    }
    
    @keyframes slideOut {
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(additionalStyles);