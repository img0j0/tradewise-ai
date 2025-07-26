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
        
        // Make the entire tool feedback manager available globally
        window.toolFeedback = this;
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

    // Alias method for backward compatibility
    launchTool(button, params = {}) {
        return this.handleToolClick(button);
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
            if (key !== 'tool' && key !== 'endpoint') {
                // Convert camelCase to snake_case for API
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
        this.displayToolResults(result, toolName, button);
        
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
                if (notification.querySelector('.notification-message')) {
                    notification.querySelector('.notification-message').insertAdjacentHTML('afterend', progressHtml);
                }
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

    displayToolResults(result, toolName, button) {
        console.log('Tool results:', toolName, result);
        
        // Get the symbol from button data or result
        const symbol = button?.dataset?.symbol || result.symbol || 'Unknown';
        
        if (toolName === 'ai_insights') {
            this.showAIInsightsResults(symbol, result);
        } else if (toolName === 'smart_alerts') {
            this.showSmartAlertsResults(symbol, result);
        } else {
            // Fallback for other tools
            this.showGenericResults(toolName, result);
        }
    }

    showAIInsightsResults(symbol, result) {
        const resultsModal = this.createResultsModal('AI Insights Results', symbol, result, 'insights');
        document.body.appendChild(resultsModal);
        resultsModal.style.display = 'flex';
    }

    showSmartAlertsResults(symbol, result) {
        const resultsModal = this.createResultsModal('Smart Alerts Created', symbol, result, 'alerts');
        document.body.appendChild(resultsModal);
        resultsModal.style.display = 'flex';
    }

    showGenericResults(toolName, result) {
        this.showNotification({
            type: 'success',
            title: 'Results Ready',
            message: `${this.getToolDisplayName(toolName)} completed successfully`,
            autoClose: 8000
        });
    }

    createResultsModal(title, symbol, result, type) {
        const modal = document.createElement('div');
        modal.className = 'tool-modal results-modal';
        modal.innerHTML = `
            <div class="modal-content results-content">
                <div class="modal-header">
                    <h3>
                        <i class="fas fa-${type === 'insights' ? 'chart-pie' : 'bell'}"></i> 
                        ${title} - ${symbol.toUpperCase()}
                    </h3>
                    <button class="modal-close" onclick="this.closest('.tool-modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    ${this.generateResultsContent(result, type, symbol)}
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="this.closest('.tool-modal').remove()">Close</button>
                    <button class="btn-primary" onclick="window.location.href='/search?symbol=${symbol}'">
                        <i class="fas fa-search"></i> Detailed Analysis
                    </button>
                </div>
            </div>
        `;
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        return modal;
    }

    generateResultsContent(result, type, symbol) {
        if (type === 'insights') {
            return this.generateInsightsContent(result, symbol);
        } else if (type === 'alerts') {
            return this.generateAlertsContent(result, symbol);
        }
    }

    generateInsightsContent(result, symbol) {
        // Handle new AI Portfolio Intelligence structure
        const aiRec = result.ai_recommendation || {};
        const portfolioImpact = result.portfolio_impact || {};
        const marketIntel = result.market_intelligence || {};
        const scenarios = result.predictive_scenarios || {};
        const institutional = result.institutional_intelligence || {};
        
        const recommendationColor = this.getRecommendationColor(aiRec.action);
        const riskColor = this.getRiskColor(aiRec.risk_level);
        
        return `
            <div class="results-summary">
                <div class="summary-grid">
                    <div class="summary-card">
                        <div class="summary-label">AI Recommendation</div>
                        <div class="summary-value" style="color: ${recommendationColor}">
                            <strong>${aiRec.action || 'HOLD'}</strong>
                        </div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-label">Confidence Score</div>
                        <div class="summary-value">
                            <strong>${aiRec.confidence || 85}%</strong>
                        </div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-label">Risk Level</div>
                        <div class="summary-value" style="color: ${riskColor}">
                            <strong>${aiRec.risk_level || 'Medium'}</strong>
                        </div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-label">Portfolio Beta</div>
                        <div class="summary-value">
                            <strong>${portfolioImpact.correlation_analysis?.portfolio_beta || '0.94'}</strong>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Portfolio Impact Analysis -->
            <div class="results-section">
                <h4><i class="fas fa-chart-pie"></i> Portfolio Impact Analysis</h4>
                <div class="analysis-grid">
                    <div class="analysis-item">
                        <span class="analysis-label">Optimal Allocation:</span>
                        <span class="analysis-value">${portfolioImpact.correlation_analysis?.optimal_allocation || '6-12% based on risk profile'}</span>
                    </div>
                    <div class="analysis-item">
                        <span class="analysis-label">VaR Contribution:</span>
                        <span class="analysis-value">${portfolioImpact.risk_contribution?.var_contribution || '12.3% of portfolio VaR'}</span>
                    </div>
                    <div class="analysis-item">
                        <span class="analysis-label">Diversification:</span>
                        <span class="analysis-value">${portfolioImpact.correlation_analysis?.diversification_benefit || 'Medium benefit'}</span>
                    </div>
                </div>
            </div>

            <!-- Market Intelligence -->
            <div class="results-section">
                <h4><i class="fas fa-globe"></i> Market Intelligence</h4>
                <div class="market-analysis">
                    <div class="market-category">
                        <h5>Macro Environment</h5>
                        <ul class="compact-list">
                            <li>Interest Rate Sensitivity: ${marketIntel.macro_environment?.interest_rate_sensitivity || 'Moderate negative'}</li>
                            <li>Recession Probability: ${marketIntel.macro_environment?.recession_probability || '28% base case'}</li>
                            <li>Dollar Impact: ${marketIntel.macro_environment?.dollar_strength_impact || 'High exposure'}</li>
                        </ul>
                    </div>
                    <div class="market-category">
                        <h5>Sector Rotation</h5>
                        <ul class="compact-list">
                            <li>Current Phase: ${marketIntel.sector_rotation?.current_phase || 'Late cycle growth'}</li>
                            <li>Institutional Flow: ${marketIntel.sector_rotation?.institutional_flow || '+$2.1B net inflow'}</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Predictive Scenarios -->
            <div class="results-section">
                <h4><i class="fas fa-crystal-ball"></i> Predictive Scenarios</h4>
                <div class="scenarios-grid">
                    <div class="scenario-card bull">
                        <div class="scenario-header">
                            <span class="scenario-label">Bull Case</span>
                            <span class="scenario-probability">${scenarios.bull_case?.probability || '35%'}</span>
                        </div>
                        <div class="scenario-target">${scenarios.bull_case?.target_range || '$240-280'}</div>
                        <div class="scenario-catalyst">${scenarios.bull_case?.catalyst || 'AI services acceleration'}</div>
                    </div>
                    <div class="scenario-card base">
                        <div class="scenario-header">
                            <span class="scenario-label">Base Case</span>
                            <span class="scenario-probability">${scenarios.base_case?.probability || '45%'}</span>
                        </div>
                        <div class="scenario-target">${scenarios.base_case?.target_range || '$200-230'}</div>
                        <div class="scenario-catalyst">${scenarios.base_case?.catalyst || 'Steady iPhone cycle'}</div>
                    </div>
                    <div class="scenario-card bear">
                        <div class="scenario-header">
                            <span class="scenario-label">Bear Case</span>
                            <span class="scenario-probability">${scenarios.bear_case?.probability || '20%'}</span>
                        </div>
                        <div class="scenario-target">${scenarios.bear_case?.target_range || '$150-180'}</div>
                        <div class="scenario-catalyst">${scenarios.bear_case?.catalyst || 'Consumer spending decline'}</div>
                    </div>
                </div>
            </div>

            <!-- Institutional Intelligence -->
            <div class="results-section">
                <h4><i class="fas fa-university"></i> Institutional Intelligence</h4>
                <div class="institutional-grid">
                    <div class="institutional-category">
                        <h5>Smart Money Flow</h5>
                        <ul class="compact-list">
                            <li>Hedge Funds: ${institutional.smart_money_flow?.hedge_funds || 'Net buyers (+$890M)'}</li>
                            <li>Pension Funds: ${institutional.smart_money_flow?.pension_funds || 'Steady accumulation'}</li>
                            <li>Insider Activity: ${institutional.smart_money_flow?.insider_activity || '3 director purchases'}</li>
                        </ul>
                    </div>
                    <div class="institutional-category">
                        <h5>Options Intelligence</h5>
                        <ul class="compact-list">
                            <li>Put/Call Ratio: ${institutional.options_intelligence?.put_call_ratio || '0.67 (bullish)'}</li>
                            <li>Unusual Activity: ${institutional.options_intelligence?.unusual_activity || 'Large Jan 2025 calls'}</li>
                            <li>Max Pain: ${institutional.options_intelligence?.max_pain || '$215'}</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- AI Strategic Recommendation -->
            <div class="results-section ai-recommendation">
                <h4><i class="fas fa-robot"></i> AI Strategic Guidance</h4>
                <div class="recommendation-content">
                    <p class="portfolio-fit">${aiRec.portfolio_fit || 'Core holding - increase on 5-8% pullbacks'}</p>
                    <p class="time-horizon"><strong>Time Horizon:</strong> ${aiRec.time_horizon || '12+ month investment'}</p>
                    
                    <div class="risks-catalysts">
                        <div class="risk-section">
                            <h6>Key Risks</h6>
                            <ul class="risk-list">
                                ${(aiRec.key_risks || ['iPhone demand slowdown', 'China market deterioration']).map(risk => `<li>${risk}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="catalyst-section">
                            <h6>Key Catalysts</h6>
                            <ul class="catalyst-list">
                                ${(aiRec.key_catalysts || ['AI/ML monetization', 'Services margin expansion']).map(catalyst => `<li>${catalyst}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="results-footer">
                <p class="disclaimer">
                    <i class="fas fa-info-circle"></i>
                    Advanced AI Portfolio Intelligence • For informational purposes only • Not financial advice
                </p>
            </div>
        `;
    }

    generateAlertsContent(result, symbol) {
        const data = result.data || {};
        const recommendations = result.recommendations || [];
        const analysis = result.analysis || 'Smart alerts have been configured successfully';
        
        return `
            <div class="results-summary">
                <div class="alert-status">
                    <i class="fas fa-check-circle" style="color: #28a745; font-size: 2rem;"></i>
                    <h3>Alert Successfully Created!</h3>
                    <p>You'll be notified when conditions are met for ${symbol.toUpperCase()}</p>
                </div>
            </div>
            
            <div class="results-section">
                <h4><i class="fas fa-bell"></i> Alert Configuration</h4>
                <p class="analysis-text">${analysis}</p>
                
                <div class="alert-details">
                    <div class="alert-detail-item">
                        <span class="detail-label">Confidence Level:</span>
                        <span class="detail-value">${data.confidence_score || 'High'}%</span>
                    </div>
                    <div class="alert-detail-item">
                        <span class="detail-label">Risk Assessment:</span>
                        <span class="detail-value">${data.risk_level || 'Moderate'}</span>
                    </div>
                </div>
            </div>
            
            ${recommendations.length > 0 ? `
            <div class="results-section">
                <h4><i class="fas fa-tasks"></i> Monitoring Suggestions</h4>
                <ul class="recommendations-list">
                    ${recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
            ` : ''}
            
            <div class="results-footer">
                <p class="disclaimer">
                    <i class="fas fa-info-circle"></i>
                    Alerts are delivered via browser notifications. Ensure notifications are enabled for the best experience.
                </p>
            </div>
        `;
    }

    getRecommendationColor(recommendation) {
        switch (recommendation?.toUpperCase()) {
            case 'BUY': return '#28a745';
            case 'SELL': return '#dc3545';
            case 'HOLD': return '#ffc107';
            default: return '#6c757d';
        }
    }

    getRiskColor(riskLevel) {
        switch (riskLevel?.toLowerCase()) {
            case 'low': return '#28a745';
            case 'moderate': case 'medium': return '#ffc107';
            case 'high': return '#dc3545';
            default: return '#6c757d';
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

// Initialize and expose the global instance
window.toolFeedback = new ToolFeedbackManager();
console.log('Tool Feedback Manager initialized');

// Expose launchTool method for backwards compatibility
window.toolFeedback.launchTool = function(toolName, params = {}) {
    // Find button with matching tool name or create a virtual one
    let button = document.querySelector(`[data-tool="${toolName}"]`);
    if (!button) {
        // Create virtual button for programmatic tool launching
        button = document.createElement('button');
        button.dataset.tool = toolName;
        Object.keys(params).forEach(key => {
            button.dataset[key] = params[key];
        });
    }
    return this.handleToolClick(button);
};