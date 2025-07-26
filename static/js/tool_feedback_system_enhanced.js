/**
 * Enhanced Tool Feedback System for TradeWise AI
 * Comprehensive progress indicators, error handling, and success notifications
 */

class EnhancedToolFeedbackManager {
    constructor() {
        this.activePolls = new Map();
        this.retryAttempts = new Map();
        this.activeBanners = new Map();
        this.pollInterval = 2500;
        this.maxPollAttempts = 120;
        this.maxRetries = 2;
        this.init();
    }

    init() {
        this.createNotificationContainer();
        this.addStyles();
        this.bindToolEvents();
        console.log('Enhanced Tool Feedback Manager initialized');
    }

    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
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
            .notification.success { border-left-color: #28a745; }
            .notification.error { border-left-color: #dc3545; }
            .notification.warning { border-left-color: #ffc107; }
            .notification.info { border-left-color: #17a2b8; }
            
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
            .progress-text {
                font-size: 12px;
                color: #666;
                margin-top: 4px;
                text-align: right;
            }
            .notification-actions {
                margin-top: 12px;
                display: flex;
                gap: 8px;
            }
            .notification-action {
                background: #007bff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
                cursor: pointer;
            }
            .notification-action.secondary {
                background: #6c757d;
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
            .task-banner {
                position: fixed;
                top: 0;
                left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
                color: white;
                padding: 12px 20px;
                border-radius: 0 0 8px 8px;
                box-shadow: 0 4px 12px rgba(0,123,255,0.3);
                z-index: 1060;
                display: flex;
                align-items: center;
                justify-content: space-between;
                min-width: 300px;
                max-width: 500px;
                animation: slideDown 0.3s ease-out;
            }
            .task-banner-content {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .task-banner-text {
                font-size: 14px;
            }
            .task-id {
                font-size: 12px;
                opacity: 0.8;
                font-weight: normal;
            }
            .task-banner-close {
                background: none;
                border: none;
                color: white;
                font-size: 18px;
                cursor: pointer;
                padding: 0;
                width: 20px;
                height: 20px;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideDown {
                from { transform: translateX(-50%) translateY(-100%); opacity: 0; }
                to { transform: translateX(-50%) translateY(0); opacity: 1; }
            }
            @keyframes slideUp {
                from { transform: translateX(-50%) translateY(0); opacity: 1; }
                to { transform: translateX(-50%) translateY(-100%); opacity: 0; }
            }
            @media (max-width: 768px) {
                .notification-container {
                    top: 60px;
                    right: 10px;
                    left: 10px;
                    max-width: none;
                }
                .task-banner {
                    left: 10px;
                    right: 10px;
                    transform: none;
                    min-width: auto;
                    max-width: none;
                }
            }
        `;
        document.head.appendChild(style);
    }

    createNotificationContainer() {
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
    }

    bindToolEvents() {
        document.addEventListener('click', (e) => {
            const toolButton = e.target.closest('[data-tool]');
            if (toolButton) {
                e.preventDefault();
                this.handleToolClick(toolButton);
            }
        });
        
        window.toolFeedback = this;
    }

    async handleToolClick(button) {
        const toolName = button.dataset.tool;
        const toolParams = this.getToolParameters(button);
        
        this.setButtonLoading(button, true);
        
        const notificationId = this.showNotification({
            type: 'info',
            title: this.getToolDisplayName(toolName),
            message: 'Starting analysis...',
            persistent: true,
            showProgress: true
        });

        try {
            const response = await this.callToolEndpoint(toolName, toolParams);
            
            if (response.task_id) {
                this.updateNotification(notificationId, {
                    message: 'Processing... This may take a few moments.',
                    showProgress: true
                });
                
                this.showTaskBanner(response.task_id, toolName);
                await this.pollTaskStatus(response.task_id, notificationId, button, toolName);
            } else if (response.success) {
                this.handleToolSuccess(response, notificationId, button, toolName);
            } else {
                this.handleToolError(response.error || 'Unknown error occurred', notificationId, button, toolName);
            }
        } catch (error) {
            console.error('Tool execution error:', error);
            this.handleToolError(error.message, notificationId, button, toolName);
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
        
        Object.keys(button.dataset).forEach(key => {
            if (key !== 'tool' && key !== 'endpoint') {
                const apiKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
                params[apiKey] = button.dataset[key];
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
            headers: { 'Content-Type': 'application/json' },
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
                this.hideTaskBanner(taskId);
                this.handleToolError('Task timed out', notificationId, button, toolName);
                return;
            }
            
            try {
                const response = await fetch(`/tools/task-status/${taskId}`);
                const statusData = await response.json();
                
                if (statusData.error) {
                    clearInterval(pollId);
                    this.activePolls.delete(taskId);
                    this.hideTaskBanner(taskId);
                    this.handleTaskFailure(statusData.error, taskId, notificationId, button, toolName);
                    return;
                }
                
                const progress = this.calculateProgress(statusData.status, pollCount);
                this.updateNotificationProgress(notificationId, progress);
                
                let message = 'Processing...';
                if (statusData.status === 'processing') {
                    message = 'Analyzing data...';
                } else if (statusData.queue_position) {
                    message = `Queue position: ${statusData.queue_position}`;
                }
                
                this.updateNotification(notificationId, { message });
                
                if (statusData.status === 'completed') {
                    clearInterval(pollId);
                    this.activePolls.delete(taskId);
                    this.hideTaskBanner(taskId);
                    this.handleToolSuccess(statusData.result, notificationId, button, toolName);
                } else if (statusData.status === 'failed') {
                    clearInterval(pollId);
                    this.activePolls.delete(taskId);
                    this.hideTaskBanner(taskId);
                    this.handleTaskFailure(statusData.error || 'Task failed', taskId, notificationId, button, toolName);
                }
            } catch (error) {
                console.error('Status poll error:', error);
                if (error.message.includes('NetworkError') || error.message.includes('fetch')) {
                    this.updateNotification(notificationId, {
                        type: 'warning',
                        message: 'Connection issue, retrying...'
                    });
                }
            }
        }, this.pollInterval);
        
        this.activePolls.set(taskId, pollId);
    }

    handleTaskFailure(error, taskId, notificationId, button, toolName) {
        const retryCount = this.retryAttempts.get(taskId) || 0;
        
        if (retryCount < this.maxRetries) {
            this.retryAttempts.set(taskId, retryCount + 1);
            this.updateNotification(notificationId, {
                type: 'warning',
                message: `Task failed. Retrying... (${retryCount + 1}/${this.maxRetries})`
            });
            
            setTimeout(async () => {
                try {
                    const retryResponse = await this.callToolEndpoint(toolName, this.getToolParameters(button));
                    if (retryResponse.task_id) {
                        this.showTaskBanner(retryResponse.task_id, toolName);
                        this.pollTaskStatus(retryResponse.task_id, notificationId, button, toolName);
                    }
                } catch (retryError) {
                    this.handleToolError(`Retry failed: ${retryError.message}`, notificationId, button, toolName);
                }
            }, 2000);
        } else {
            this.retryAttempts.delete(taskId);
            this.handleToolError(error, notificationId, button, toolName);
        }
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

    showTaskBanner(taskId, toolName) {
        if (this.activeBanners.has(taskId)) return;
        
        const banner = document.createElement('div');
        banner.id = `task-banner-${taskId}`;
        banner.className = 'task-banner';
        banner.innerHTML = `
            <div class="task-banner-content">
                <div class="spinner"></div>
                <span class="task-banner-text">
                    <strong>${this.getToolDisplayName(toolName)}</strong> running... 
                    <span class="task-id">(Task ID: ${taskId.substring(0, 8)}...)</span>
                </span>
            </div>
            <button class="task-banner-close" onclick="window.toolFeedback.hideTaskBanner('${taskId}')">&times;</button>
        `;
        
        document.body.appendChild(banner);
        this.activeBanners.set(taskId, banner);
    }

    hideTaskBanner(taskId) {
        const banner = this.activeBanners.get(taskId);
        if (banner) {
            banner.style.animation = 'slideUp 0.3s ease-out forwards';
            setTimeout(() => {
                if (banner.parentNode) {
                    banner.parentNode.removeChild(banner);
                }
            }, 300);
            this.activeBanners.delete(taskId);
        }
    }

    handleToolSuccess(result, notificationId, button, toolName) {
        this.setButtonLoading(button, false);
        
        const actions = this.getSuccessActions(result, toolName);
        
        this.updateNotification(notificationId, {
            type: 'success',
            title: `${this.getToolDisplayName(toolName)} Complete`,
            message: 'Analysis completed successfully!',
            persistent: false,
            duration: 8000,
            actions: actions
        });
        
        this.showButtonSuccess(button);
        this.handleToolResult(result, toolName);
    }

    handleToolError(error, notificationId, button, toolName) {
        this.setButtonLoading(button, false);
        
        const userMessage = this.getUserFriendlyError(error);
        
        this.updateNotification(notificationId, {
            type: 'error',
            title: 'Analysis Failed',
            message: userMessage,
            persistent: false,
            duration: 10000,
            actions: [{
                text: 'Try Again',
                action: () => {
                    this.handleToolClick(button);
                }
            }]
        });
        
        this.showButtonError(button);
    }

    getUserFriendlyError(error) {
        const errorMap = {
            'timeout': 'The analysis took too long to complete. Please try again.',
            'network': 'Connection error. Please check your internet connection.',
            'auth': 'Authentication required. Please log in again.',
            'quota': 'Daily limit reached. Please upgrade your plan.',
            'server': 'Server error. Our team has been notified.',
            'data': 'Unable to fetch market data. Please try again later.',
            'symbol not found': 'Invalid stock symbol. Please check the symbol and try again.',
            'api timeout': 'Request timed out. Please try again in a moment.',
            'rate limit': 'Too many requests. Please wait a moment before trying again.',
            'premium required': 'This feature requires a premium subscription.',
            'invalid input': 'Please check your input parameters and try again.',
            'market closed': 'Market data is not available while markets are closed.'
        };
        
        const errorLower = error.toLowerCase();
        for (const [key, message] of Object.entries(errorMap)) {
            if (errorLower.includes(key)) {
                return message;
            }
        }
        
        return 'Could not complete the analysis. Please try again.';
    }

    getSuccessActions(result, toolName) {
        const actions = [];
        
        actions.push({
            text: 'View Results',
            action: () => {
                this.displayResults(result, toolName);
            }
        });
        
        if (this.canDownload(result, toolName)) {
            actions.push({
                text: 'Download Report',
                action: () => {
                    this.downloadResults(result, toolName);
                }
            });
        }
        
        return actions;
    }

    canDownload(result, toolName) {
        const downloadableTools = ['backtest', 'peer_comparison', 'market_scanner', 'stock_analysis'];
        return downloadableTools.includes(toolName) && result;
    }

    downloadResults(result, toolName) {
        try {
            const reportData = this.formatResultsForDownload(result, toolName);
            const blob = new Blob([reportData], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `${toolName}_analysis_${new Date().toISOString().split('T')[0]}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.showNotification({
                type: 'success',
                title: 'Download Complete',
                message: 'Analysis report downloaded successfully',
                duration: 3000
            });
        } catch (error) {
            console.error('Download error:', error);
            this.showNotification({
                type: 'error',
                title: 'Download Failed',
                message: 'Could not download the report. Please try again.',
                duration: 5000
            });
        }
    }

    formatResultsForDownload(result, toolName) {
        const timestamp = new Date().toLocaleString();
        let content = `TradeWise AI - ${this.getToolDisplayName(toolName)} Report\n`;
        content += `Generated: ${timestamp}\n`;
        content += `${'='.repeat(50)}\n\n`;
        
        if (typeof result === 'object') {
            content += JSON.stringify(result, null, 2);
        } else {
            content += result.toString();
        }
        
        return content;
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

    // Notification management methods
    showNotification(options) {
        const id = 'notification-' + Date.now();
        const notification = document.createElement('div');
        notification.id = id;
        notification.className = `notification ${options.type || 'info'}`;
        
        let progressHtml = '';
        if (options.showProgress) {
            progressHtml = `
                <div class="notification-progress">
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                    <div class="progress-text">0%</div>
                </div>
            `;
        }
        
        let actionsHtml = '';
        if (options.actions && options.actions.length > 0) {
            actionsHtml = '<div class="notification-actions">';
            options.actions.forEach(action => {
                actionsHtml += `<button class="notification-action" onclick="(${action.action.toString()})()">${action.text}</button>`;
            });
            actionsHtml += '</div>';
        }
        
        notification.innerHTML = `
            <div class="notification-header">
                <h4 class="notification-title">${options.title || 'Notification'}</h4>
                <button class="notification-close" onclick="window.toolFeedback.removeNotification('${id}')">&times;</button>
            </div>
            <p class="notification-message">${options.message || ''}</p>
            ${progressHtml}
            ${actionsHtml}
        `;
        
        const container = document.getElementById('notification-container');
        container.appendChild(notification);
        
        if (options.duration && !options.persistent) {
            setTimeout(() => {
                this.removeNotification(id);
            }, options.duration);
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
            const title = notification.querySelector('.notification-title');
            if (title) title.textContent = updates.title;
        }
        
        if (updates.message) {
            const message = notification.querySelector('.notification-message');
            if (message) message.textContent = updates.message;
        }
        
        if (updates.actions) {
            let actionsContainer = notification.querySelector('.notification-actions');
            if (!actionsContainer) {
                actionsContainer = document.createElement('div');
                actionsContainer.className = 'notification-actions';
                notification.appendChild(actionsContainer);
            }
            
            actionsContainer.innerHTML = '';
            updates.actions.forEach(action => {
                const button = document.createElement('button');
                button.className = 'notification-action';
                button.textContent = action.text;
                button.onclick = action.action;
                actionsContainer.appendChild(button);
            });
        }
    }

    updateNotificationProgress(id, progress) {
        const notification = document.getElementById(id);
        if (!notification) return;
        
        const progressFill = notification.querySelector('.progress-fill');
        const progressText = notification.querySelector('.progress-text');
        
        if (progressFill) {
            progressFill.style.width = `${progress}%`;
        }
        
        if (progressText) {
            progressText.textContent = `${Math.round(progress)}%`;
        }
    }

    removeNotification(id) {
        const notification = document.getElementById(id);
        if (notification) {
            notification.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }

    // Tool result handling methods
    handleToolResult(result, toolName) {
        // Handle specific tool results based on tool type
        switch (toolName) {
            case 'stock_analysis':
                this.displayStockAnalysis(result);
                break;
            case 'ai_insights':
                this.displayAIInsights(result);
                break;
            case 'backtest':
                this.displayBacktestResults(result);
                break;
            default:
                console.log('Tool result:', result);
        }
    }

    displayResults(result, toolName) {
        // Generic result display method
        console.log(`Displaying ${toolName} results:`, result);
        
        // You can customize this to show results in modals, overlays, etc.
        if (typeof window.showAnalysisOverlay === 'function') {
            window.showAnalysisOverlay(result);
        }
    }

    displayStockAnalysis(result) {
        // Handle stock analysis specific display
        if (typeof window.displayResults === 'function') {
            window.displayResults(result);
        }
    }

    displayAIInsights(result) {
        // Handle AI insights specific display
        console.log('AI Insights result:', result);
    }

    displayBacktestResults(result) {
        // Handle backtest specific display
        console.log('Backtest result:', result);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (!window.toolFeedback || !(window.toolFeedback instanceof EnhancedToolFeedbackManager)) {
        window.toolFeedback = new EnhancedToolFeedbackManager();
        console.log('Enhanced Tool Feedback System initialized');
    }
});

// Backward compatibility
if (typeof window.ToolFeedbackManager === 'undefined') {
    window.ToolFeedbackManager = EnhancedToolFeedbackManager;
}