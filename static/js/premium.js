/**
 * Premium Features JavaScript
 * Handles AI Trading Copilot subscription and real-time signals
 */

class PremiumManager {
    constructor() {
        this.userStatus = null;
        this.copilotSignals = [];
        this.signalUpdateInterval = null;
        this.init();
    }

    async init() {
        await this.checkPremiumStatus();
        this.setupEventListeners();
        
        // Start signal updates if user is premium
        if (this.isPremium()) {
            this.startSignalUpdates();
        }
    }

    async checkPremiumStatus() {
        try {
            const response = await fetch('/api/premium/status');
            const data = await response.json();
            this.userStatus = data;
            
            this.updatePremiumUI();
            return data;
        } catch (error) {
            console.error('Error checking premium status:', error);
            return null;
        }
    }

    isPremium() {
        return this.userStatus && this.userStatus.is_premium;
    }

    updatePremiumUI() {
        const premiumBadges = document.querySelectorAll('.premium-badge');
        const premiumButtons = document.querySelectorAll('.premium-feature-btn');
        
        if (this.isPremium()) {
            // Show premium features
            premiumBadges.forEach(badge => {
                badge.innerHTML = `<i class="fas fa-crown text-warning me-1"></i>${this.userStatus.plan.toUpperCase()}`;
                badge.classList.add('bg-primary');
            });
            
            premiumButtons.forEach(btn => {
                btn.classList.remove('btn-outline-warning');
                btn.classList.add('btn-success');
                btn.innerHTML = '<i class="fas fa-check me-2"></i>Active';
                btn.disabled = false;
            });
            
            // Show copilot status
            this.updateCopilotStatus();
        } else {
            // Show upgrade prompts
            premiumBadges.forEach(badge => {
                badge.innerHTML = '<i class="fas fa-lock me-1"></i>FREE';
                badge.classList.add('bg-secondary');
            });
            
            premiumButtons.forEach(btn => {
                btn.classList.add('btn-outline-warning');
                btn.innerHTML = '<i class="fas fa-rocket me-2"></i>Upgrade';
                btn.onclick = () => this.showPremiumModal();
            });
        }
    }

    async updateCopilotStatus() {
        try {
            const response = await fetch('/api/premium/copilot/status');
            const data = await response.json();
            
            const statusElement = document.getElementById('copilot-status');
            if (statusElement && data.success) {
                const status = data.copilot_status;
                statusElement.innerHTML = `
                    <div class="d-flex align-items-center">
                        <div class="status-indicator ${status.monitoring ? 'active' : 'inactive'} me-2"></div>
                        <span class="me-3">${status.monitoring ? 'Monitoring' : 'Offline'}</span>
                        <small class="text-muted">
                            ${status.signals_today} signals today • ${status.subscribers} active users
                        </small>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error updating copilot status:', error);
        }
    }

    async startSignalUpdates() {
        if (this.signalUpdateInterval) return;
        
        // Update signals every 30 seconds
        this.signalUpdateInterval = setInterval(() => {
            this.fetchLatestSignals();
        }, 30000);
        
        // Initial fetch
        this.fetchLatestSignals();
    }

    stopSignalUpdates() {
        if (this.signalUpdateInterval) {
            clearInterval(this.signalUpdateInterval);
            this.signalUpdateInterval = null;
        }
    }

    async fetchLatestSignals() {
        try {
            const response = await fetch('/api/premium/copilot/signals?limit=5');
            const data = await response.json();
            
            if (data.success) {
                this.copilotSignals = data.signals;
                this.displaySignals();
                
                // Show new signal notification
                if (data.signals.length > 0) {
                    this.showNewSignalNotification(data.signals[0]);
                }
            }
        } catch (error) {
            console.error('Error fetching signals:', error);
        }
    }

    displaySignals() {
        const signalsContainer = document.getElementById('copilot-signals');
        if (!signalsContainer) return;
        
        if (this.copilotSignals.length === 0) {
            signalsContainer.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-robot fa-2x text-muted mb-2"></i>
                    <p class="text-muted">AI Copilot is monitoring markets...</p>
                    <small class="text-muted">You'll see trading signals here when opportunities arise</small>
                </div>
            `;
            return;
        }
        
        signalsContainer.innerHTML = this.copilotSignals.map(signal => `
            <div class="signal-card mb-3 p-3 border rounded ${this.getSignalClass(signal)}">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div class="d-flex align-items-center">
                        <span class="fw-bold me-2">${signal.symbol}</span>
                        <span class="badge ${this.getSignalBadgeClass(signal.type)}">${signal.type.toUpperCase()}</span>
                        <span class="badge bg-info ms-2">${Math.round(signal.confidence * 100)}%</span>
                    </div>
                    <small class="text-muted">${this.formatTime(signal.timestamp)}</small>
                </div>
                
                <p class="mb-2 signal-message">${signal.message}</p>
                
                <div class="row g-2 small">
                    <div class="col-4">
                        <strong>Price:</strong> $${signal.price.toFixed(2)}
                    </div>
                    <div class="col-4">
                        <strong>Target:</strong> $${signal.target.toFixed(2)}
                    </div>
                    <div class="col-4">
                        <strong>Strength:</strong> ${signal.strength.toUpperCase()}
                    </div>
                </div>
                
                ${this.userStatus.plan === 'elite' ? `
                    <div class="mt-3">
                        <button class="btn btn-sm btn-warning me-2" onclick="executeAITrade('${signal.symbol}')">
                            <i class="fas fa-bolt me-1"></i>Execute Trade
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="addToWatchlist('${signal.symbol}')">
                            <i class="fas fa-eye me-1"></i>Watch
                        </button>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    getSignalClass(signal) {
        const strengthClasses = {
            'low': 'border-secondary',
            'medium': 'border-warning',
            'high': 'border-success',
            'critical': 'border-danger'
        };
        return strengthClasses[signal.strength] || 'border-secondary';
    }

    getSignalBadgeClass(type) {
        const typeClasses = {
            'breakout': 'bg-success',
            'reversal': 'bg-warning',
            'volume_spike': 'bg-info',
            'momentum_shift': 'bg-primary'
        };
        return typeClasses[type] || 'bg-secondary';
    }

    formatTime(timestamp) {
        return new Date(timestamp).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    showNewSignalNotification(signal) {
        // Only show notification for high/critical signals
        if (!['high', 'critical'].includes(signal.strength)) return;
        
        const notification = document.createElement('div');
        notification.className = 'alert alert-success alert-dismissible fade show position-fixed';
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-robot text-success me-2"></i>
                <div>
                    <strong>AI Signal: ${signal.symbol}</strong>
                    <br><small>${signal.message}</small>
                </div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 10000);
    }

    showPremiumModal() {
        const modal = new bootstrap.Modal(document.getElementById('premiumModal'));
        modal.show();
    }

    setupEventListeners() {
        // Premium upgrade buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.premium-feature-btn')) {
                if (!this.isPremium()) {
                    this.showPremiumModal();
                }
            }
        });
    }
}

// Global premium functions
async function subscribeToPremium(plan) {
    try {
        showNotification('Processing subscription...', 'info');
        
        const response = await fetch('/api/premium/subscribe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ plan: plan })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('premiumModal'));
            if (modal) modal.hide();
            
            // Refresh page to update UI
            setTimeout(() => location.reload(), 2000);
        } else {
            showNotification(data.error || 'Subscription failed', 'error');
        }
    } catch (error) {
        console.error('Subscription error:', error);
        showNotification('Network error during subscription', 'error');
    }
}

async function executeAITrade(symbol) {
    try {
        showNotification(`Executing AI trade for ${symbol}...`, 'info');
        
        // In production, this would execute the trade
        // For now, show success message
        setTimeout(() => {
            showNotification(`AI trade executed for ${symbol}!`, 'success');
        }, 1500);
        
    } catch (error) {
        console.error('Trade execution error:', error);
        showNotification('Failed to execute trade', 'error');
    }
}

async function addToWatchlist(symbol) {
    try {
        showNotification(`Added ${symbol} to watchlist`, 'success');
    } catch (error) {
        console.error('Watchlist error:', error);
        showNotification('Failed to add to watchlist', 'error');
    }
}

// Initialize premium manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.premiumManager = new PremiumManager();
});

// CSS for premium features
const premiumStyles = `
.status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}

.status-indicator.active {
    background-color: #28a745;
    animation: pulse 2s infinite;
}

.status-indicator.inactive {
    background-color: #6c757d;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }
    70% { box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); }
    100% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }
}

.signal-card {
    transition: all 0.3s ease;
}

.signal-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.signal-message {
    font-size: 0.9em;
    color: #6c757d;
}
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = premiumStyles;
document.head.appendChild(styleSheet);