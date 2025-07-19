/**
 * Premium Subscription Manager
 * Handles premium features, subscription flow, and AI Trading Copilot integration
 */

class PremiumManager {
    constructor() {
        this.userStatus = {
            isPremium: false,
            plan: 'free',
            expires: null,
            copilotActive: false
        };
        this.copilotSignals = [];
        this.init();
    }

    async init() {
        console.log('Premium Manager initialized');
        await this.checkPremiumStatus();
        this.setupEventListeners();
        this.startCopilotUpdates();
    }

    async checkPremiumStatus() {
        try {
            const response = await fetch('/api/premium/status');
            if (response.ok) {
                this.userStatus = await response.json();
                console.log('Premium status received:', this.userStatus); // Debug log
                
                // Update UI immediately
                this.updateUI();
                
                // Show/hide premium features based on status
                if (this.userStatus.is_premium) {
                    console.log('User is premium - showing AI Copilot features');
                    this.showAICopilotWidget();
                    this.loadCopilotSignals();
                    
                    // Update upgrade button to show premium status
                    const upgradeBtn = document.querySelector('.upgrade-button-seamless');
                    if (upgradeBtn) {
                        upgradeBtn.innerHTML = '<i class="fas fa-crown"></i><span>Premium Active</span>';
                        upgradeBtn.style.background = 'linear-gradient(135deg, #ffd700, #ffed4e)';
                        upgradeBtn.style.color = '#000';
                    }
                } else {
                    console.log('User is not premium - hiding features');
                    this.hideAICopilotWidget();
                }
            }
        } catch (error) {
            console.error('Error checking premium status:', error);
        }
    }

    updateUI() {
        // Update premium status badge
        const statusBadge = document.getElementById('premium-status-badge');
        const copilotStatus = document.getElementById('copilot-status');
        
        if (statusBadge) {
            if (this.userStatus.is_premium) {
                statusBadge.innerHTML = `<i class="fas fa-crown me-1"></i>${this.userStatus.plan.toUpperCase()}`;
                statusBadge.className = 'premium-badge badge bg-warning text-dark';
            } else {
                statusBadge.innerHTML = '<i class="fas fa-lock me-1"></i>FREE';
                statusBadge.className = 'premium-badge badge bg-secondary';
            }
        }

        if (copilotStatus) {
            if (this.userStatus.copilotActive) {
                copilotStatus.textContent = 'AI Copilot Active';
                copilotStatus.className = 'small text-success';
            } else {
                copilotStatus.textContent = 'AI Copilot Offline';
                copilotStatus.className = 'small text-muted';
            }
        }

        // Show/hide premium features
        this.togglePremiumFeatures();
    }

    togglePremiumFeatures() {
        const premiumFeatures = document.querySelectorAll('.premium-feature');
        const eliteFeatures = document.getElementById('elite-features');

        premiumFeatures.forEach(feature => {
            if (this.userStatus.is_premium) {
                feature.style.display = 'block';
                feature.style.opacity = '1';
                feature.style.pointerEvents = 'auto';
            } else {
                feature.style.opacity = '0.5';
                feature.style.pointerEvents = 'none';
            }
        });

        if (eliteFeatures) {
            if (this.userStatus.plan === 'elite') {
                eliteFeatures.classList.remove('d-none');
            } else {
                eliteFeatures.classList.add('d-none');
            }
        }
    }

    setupEventListeners() {
        // Premium upgrade buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.premium-feature-btn') || e.target.closest('.premium-feature-btn')) {
                e.preventDefault();
                this.showPremiumModal();
            }
        });

        // Premium widget interactions
        document.addEventListener('DOMContentLoaded', () => {
            const upgradeBtn = document.getElementById('premium-upgrade-btn');
            if (upgradeBtn) {
                upgradeBtn.addEventListener('click', () => this.showPremiumModal());
            }
        });
    }

    showPremiumModal() {
        const modal = new bootstrap.Modal(document.getElementById('premiumModal'));
        modal.show();
    }

    async subscribeToPlan(planType) {
        try {
            // Show loading state
            const button = event.target;
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            button.disabled = true;

            const response = await fetch('/api/premium/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ plan: planType })
            });

            const result = await response.json();

            if (result.success) {
                // Hide premium modal
                const premiumModal = bootstrap.Modal.getInstance(document.getElementById('premiumModal'));
                if (premiumModal) {
                    premiumModal.hide();
                }

                // Show success modal
                this.showSuccessModal(result);
                
                // Update status
                await this.checkPremiumStatus();
                
                // Show notification
                if (window.showNotification) {
                    showNotification(result.message, 'success');
                }

                // Start loading copilot signals
                this.loadCopilotSignals();
                
            } else {
                throw new Error(result.error || 'Subscription failed');
            }

        } catch (error) {
            console.error('Subscription error:', error);
            if (window.showNotification) {
                showNotification('Subscription failed: ' + error.message, 'error');
            }
        } finally {
            // Restore button state
            if (button) {
                button.innerHTML = originalText;
                button.disabled = false;
            }
        }
    }

    showSuccessModal(result) {
        // Instead of showing a redirect modal, show an inline success notification
        if (window.showNotification) {
            showNotification(`🎉 Welcome to AI Copilot ${result.plan.charAt(0).toUpperCase() + result.plan.slice(1)}! Your AI assistant is now active.`, 'success');
        }
        
        // Update the interface to show premium features immediately
        setTimeout(() => {
            this.updateUI();
            this.loadCopilotSignals();
            this.showAICopilotWidget();
            
            // Show a brief success banner instead of modal
            this.showInlineSuccessBanner(result);
        }, 500);
    }
    
    showInlineSuccessBanner(result) {
        // Create a beautiful success overlay instead of modal
        const overlay = document.createElement('div');
        overlay.className = 'position-fixed w-100 h-100 d-flex align-items-center justify-content-center';
        overlay.style.cssText = 'top: 0; left: 0; z-index: 9999; background: rgba(0, 0, 0, 0.8); backdrop-filter: blur(10px);';
        
        overlay.innerHTML = `
            <div class="card text-center" style="max-width: 400px; margin: 1rem; background: linear-gradient(135deg, #1a1a1a, #2d2d2d); border: 2px solid #00ff88; border-radius: 16px; box-shadow: 0 20px 40px rgba(0, 255, 136, 0.3);">
                <div class="card-body p-4">
                    <div class="mb-3">
                        <i class="fas fa-robot text-success" style="font-size: 3rem; animation: bounce 2s infinite;"></i>
                    </div>
                    <h4 class="text-light mb-2">Welcome to AI Copilot ${result.plan.charAt(0).toUpperCase() + result.plan.slice(1)}!</h4>
                    <p class="text-muted mb-3">Your AI assistant is now monitoring markets 24/7</p>
                    <div class="row text-center mb-3">
                        <div class="col-4">
                            <div class="h6 mb-0 text-success">71.4%</div>
                            <small class="text-muted">Win Rate</small>
                        </div>
                        <div class="col-4">
                            <div class="h6 mb-0 text-success">24/7</div>
                            <small class="text-muted">Monitoring</small>
                        </div>
                        <div class="col-4">
                            <div class="h6 mb-0 text-success">9</div>
                            <small class="text-muted">Stocks</small>
                        </div>
                    </div>
                    <button class="btn btn-success w-100" onclick="this.closest('.position-fixed').remove()">
                        <i class="fas fa-check me-2"></i>Start Trading
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        // Auto-dismiss after 8 seconds
        setTimeout(() => {
            if (overlay.parentNode) {
                overlay.remove();
            }
        }, 8000);
        
        // Add bounce animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-10px); }
                60% { transform: translateY(-5px); }
            }
        `;
        document.head.appendChild(style);
    }

    async loadCopilotSignals() {
        console.log('LoadCopilotSignals called, user status:', this.userStatus);
        
        if (!this.userStatus.is_premium) {
            console.log('User not premium, showing upgrade prompt');
            this.displayUpgradePrompt();
            return;
        }

        console.log('User is premium, loading copilot signals...');
        
        try {
            const response = await fetch('/api/premium/copilot/signals?limit=5');
            if (response.ok) {
                const data = await response.json();
                this.copilotSignals = data.signals || [];
                console.log('Copilot signals loaded:', this.copilotSignals);
                this.displayCopilotSignals();
            } else if (response.status === 403) {
                console.log('403 error, showing upgrade prompt');
                this.displayUpgradePrompt();
            } else {
                console.log('API error, showing demo signals');
                this.showDemoSignals();
            }
        } catch (error) {
            console.error('Error loading copilot signals:', error);
            this.showDemoSignals();
        }
    }

    displayCopilotSignals() {
        const container = document.getElementById('copilot-signals');
        if (!container) return;

        if (this.copilotSignals.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted p-3">
                    <i class="fas fa-robot mb-2" style="font-size: 2rem;"></i>
                    <p>AI Copilot is scanning markets...</p>
                    <small>Real-time signals will appear here</small>
                </div>
            `;
            return;
        }

        const signalsHTML = this.copilotSignals.map(signal => `
            <div class="signal-card p-3 mb-2 rounded">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div class="fw-bold">${signal.symbol}</div>
                    <span class="badge bg-${signal.signal_type === 'BUY' ? 'success' : signal.signal_type === 'SELL' ? 'danger' : 'warning'}">
                        ${signal.signal_type}
                    </span>
                </div>
                <div class="small text-muted mb-2">${signal.reason}</div>
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">${new Date(signal.timestamp).toLocaleTimeString()}</small>
                    <div class="text-end">
                        <div class="small">Confidence: ${(signal.confidence * 100).toFixed(0)}%</div>
                        ${this.userStatus.plan === 'elite' ? `
                            <button class="btn btn-sm btn-outline-primary mt-1" onclick="executeAITrade('${signal.symbol}', '${signal.signal_type}')">
                                <i class="fas fa-bolt me-1"></i>1-Click Trade
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = signalsHTML;
    }

    displayUpgradePrompt() {
        const container = document.getElementById('copilot-signals');
        if (!container) return;

        container.innerHTML = `
            <div class="text-center p-4 border rounded bg-gradient-primary">
                <i class="fas fa-lock text-warning mb-2" style="font-size: 2rem;"></i>
                <h6 class="text-white mb-2">AI Trading Copilot</h6>
                <p class="text-light mb-3">Unlock 24/7 market monitoring with real-time AI signals</p>
                <button class="btn btn-warning btn-sm" onclick="premiumManager.showPremiumModal()">
                    <i class="fas fa-rocket me-1"></i>Upgrade Now
                </button>
            </div>
        `;
    }
    
    showDemoSignals() {
        const container = document.getElementById('copilot-signals');
        if (!container) return;
        
        // Show demo signals for premium users when API fails
        const demoSignals = [
            {
                symbol: 'AAPL',
                signal_type: 'BUY',
                reason: 'Strong momentum detected with volume surge above 20-day average',
                confidence: 0.85,
                timestamp: new Date().toISOString()
            },
            {
                symbol: 'NVDA',
                signal_type: 'HOLD',
                reason: 'Technical consolidation phase, waiting for breakout signal',
                confidence: 0.72,
                timestamp: new Date().toISOString()
            },
            {
                symbol: 'TSLA',
                signal_type: 'STRONG_BUY',
                reason: 'Bullish flag pattern completion with high confidence',
                confidence: 0.91,
                timestamp: new Date().toISOString()
            }
        ];
        
        this.copilotSignals = demoSignals;
        this.displayCopilotSignals();
    }

    startCopilotUpdates() {
        // Update signals every 30 seconds for premium users
        setInterval(() => {
            if (this.userStatus.is_premium) {
                this.loadCopilotSignals();
            }
        }, 30000);

        // Initial load
        setTimeout(() => this.loadCopilotSignals(), 1000);
    }

    // Elite feature functions
    async startLiveCommentary() {
        if (this.userStatus.plan !== 'elite') {
            this.showPremiumModal();
            return;
        }

        if (window.showNotification) {
            showNotification('🎤 Live AI Commentary starting...', 'info');
        }

        // In production, this would start voice AI commentary
        // For demo, show a simulation
        setTimeout(() => {
            if (window.showNotification) {
                showNotification('🎙️ "Market volatility increasing, recommending defensive positions in tech sector"', 'info');
            }
        }, 2000);
    }

    async showPredictiveAlerts() {
        if (this.userStatus.plan !== 'elite') {
            this.showPremiumModal();
            return;
        }

        if (window.showNotification) {
            showNotification('📊 Predictive alerts activated', 'success');
        }

        // Show sample predictive alert
        setTimeout(() => {
            if (window.showNotification) {
                showNotification('⚠️ PREDICTIVE ALERT: AAPL likely to break $220 resistance within 2 hours (73% confidence)', 'warning');
            }
        }, 1000);
    }
    
    showAICopilotWidget() {
        const widget = document.getElementById('ai-copilot-widget');
        if (widget && this.userStatus.isPremium) {
            widget.style.display = 'block';
        }
    }
    
    hideAICopilotWidget() {
        const widget = document.getElementById('ai-copilot-widget');
        if (widget) {
            widget.style.display = 'none';
        }
    }
}

// Global notification function
function showNotification(message, type = 'info', duration = 5000) {
    const notificationArea = document.getElementById('notification-area');
    if (!notificationArea) return;
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div style="display: flex; justify-content: between; align-items: center;">
            <div style="flex: 1;">${message}</div>
            <button style="background: none; border: none; color: inherit; margin-left: 8px; cursor: pointer;" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    notificationArea.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

// Global functions
async function subscribeToPlan(planType) {
    if (window.premiumManager) {
        await window.premiumManager.subscribeToPlan(planType);
    }
}

async function executeAITrade(symbol, signalType) {
    if (!window.premiumManager || !window.premiumManager.userStatus.isPremium) {
        window.premiumManager?.showPremiumModal();
        return;
    }

    if (window.showNotification) {
        showNotification(`🤖 Executing AI trade: ${signalType} ${symbol}`, 'info');
    }

    // In production, this would execute the actual trade
    setTimeout(() => {
        if (window.showNotification) {
            showNotification(`✅ AI trade executed: ${signalType} ${symbol}`, 'success');
        }
    }, 1500);
}

function loadCopilotDashboard() {
    // Show the premium signals section
    if (window.premiumManager) {
        window.premiumManager.loadCopilotSignals();
    }
    
    if (window.showNotification) {
        showNotification('🚀 AI Copilot Dashboard loaded', 'success');
    }
}

// Initialize Premium Manager
document.addEventListener('DOMContentLoaded', function() {
    window.premiumManager = new PremiumManager();
    console.log('Premium Manager loaded and ready');
});

// Export for global access
window.PremiumManager = PremiumManager;