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
                this.updateUI();
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
            if (this.userStatus.isPremium) {
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
            if (this.userStatus.isPremium) {
                feature.style.display = 'block';
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
        const successModal = document.getElementById('premiumSuccessModal');
        const planName = document.getElementById('success-plan-name');
        
        if (planName) {
            planName.textContent = `AI Copilot ${result.plan.charAt(0).toUpperCase() + result.plan.slice(1)}`;
        }

        const modal = new bootstrap.Modal(successModal);
        modal.show();
    }

    async loadCopilotSignals() {
        if (!this.userStatus.isPremium) {
            this.displayUpgradePrompt();
            return;
        }

        try {
            const response = await fetch('/api/premium/copilot/signals?limit=5');
            if (response.ok) {
                const data = await response.json();
                this.copilotSignals = data.signals || [];
                this.displayCopilotSignals();
            } else if (response.status === 403) {
                this.displayUpgradePrompt();
            }
        } catch (error) {
            console.error('Error loading copilot signals:', error);
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

    startCopilotUpdates() {
        // Update signals every 30 seconds for premium users
        setInterval(() => {
            if (this.userStatus.isPremium) {
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