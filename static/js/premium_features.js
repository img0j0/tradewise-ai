/**
 * Premium Features Manager
 * Handles premium feature locking, upsell modals, and plan management
 */

class PremiumFeaturesManager {
    constructor() {
        this.userPlan = 'free'; // Default to free, will be updated from server
        this.upsellModal = null;
        this.premiumFeatures = {
            'backtest': {
                name: 'Portfolio Backtesting',
                description: 'Test your investment strategies with historical data',
                icon: 'fas fa-chart-bar',
                benefits: [
                    'Historical performance analysis',
                    'Risk-adjusted returns calculation',
                    'Multiple strategy comparison',
                    'Drawdown analysis'
                ]
            },
            'peer-comparison': {
                name: 'Peer Comparison Analysis',
                description: 'Compare stocks against industry competitors',
                icon: 'fas fa-balance-scale',
                benefits: [
                    'Industry benchmarking',
                    'Competitive positioning',
                    'Relative valuation metrics',
                    'Market share analysis'
                ]
            },
            'ai-scanner': {
                name: 'AI Market Scanner',
                description: 'AI-powered market opportunities detection',
                icon: 'fas fa-search-plus',
                benefits: [
                    'Real-time opportunity alerts',
                    'Pattern recognition',
                    'Sentiment analysis',
                    'Custom screening filters'
                ]
            }
        };
        
        this.init();
    }
    
    init() {
        this.fetchUserPlan();
        this.createUpsellModal();
        this.initializePremiumLocks();
        this.bindEvents();
        console.log('Premium Features Manager initialized');
    }
    
    async fetchUserPlan() {
        try {
            const response = await fetch('/api/user/plan');
            if (response.ok) {
                const data = await response.json();
                this.userPlan = data.plan || 'free';
                this.updatePlanBadge();
            }
        } catch (error) {
            console.log('Using default free plan');
            this.userPlan = 'free';
            this.updatePlanBadge();
        }
    }
    
    updatePlanBadge() {
        const planBadges = document.querySelectorAll('.plan-badge');
        planBadges.forEach(badge => {
            badge.className = `plan-badge ${this.userPlan}`;
            badge.innerHTML = this.getPlanBadgeContent();
        });
        
        // Show/hide upgrade button
        const upgradeButtons = document.querySelectorAll('.navbar-upgrade-btn');
        upgradeButtons.forEach(btn => {
            btn.style.display = this.userPlan === 'free' ? 'inline-flex' : 'none';
        });
    }
    
    getPlanBadgeContent() {
        const planData = {
            'free': { icon: 'fas fa-user', text: 'Free' },
            'pro': { icon: 'fas fa-star', text: 'Pro' },
            'enterprise': { icon: 'fas fa-crown', text: 'Enterprise' }
        };
        
        const plan = planData[this.userPlan] || planData.free;
        return `<i class="${plan.icon}"></i> ${plan.text}`;
    }
    
    createUpsellModal() {
        // Remove existing modal if any
        const existing = document.getElementById('upsell-modal');
        if (existing) existing.remove();
        
        this.upsellModal = document.createElement('div');
        this.upsellModal.id = 'upsell-modal';
        this.upsellModal.className = 'upsell-modal';
        this.upsellModal.innerHTML = `
            <div class="upsell-modal-content">
                <div class="upsell-modal-header">
                    <button class="upsell-modal-close" onclick="premiumManager.closeUpsellModal()">
                        <i class="fas fa-times"></i>
                    </button>
                    <div class="upsell-modal-icon">
                        <i class="fas fa-lock"></i>
                    </div>
                    <h2 class="upsell-modal-title">Premium Feature</h2>
                    <p class="upsell-modal-subtitle">Upgrade to unlock advanced functionality</p>
                </div>
                <div class="upsell-modal-body">
                    <div class="upsell-feature-list" id="upsell-features">
                        <!-- Features will be populated dynamically -->
                    </div>
                    <div class="upsell-modal-actions">
                        <a href="/premium/upgrade" class="upsell-upgrade-btn">
                            <i class="fas fa-crown mr-2"></i>Upgrade to Pro
                        </a>
                        <button class="upsell-cancel-btn" onclick="premiumManager.closeUpsellModal()">
                            Maybe Later
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.upsellModal);
        
        // Close modal on backdrop click
        this.upsellModal.addEventListener('click', (e) => {
            if (e.target === this.upsellModal) {
                this.closeUpsellModal();
            }
        });
    }
    
    initializePremiumLocks() {
        // Lock premium navigation links
        this.lockNavigationItems();
        
        // Lock premium buttons and cards
        this.lockPremiumElements();
        
        // Add tooltips to premium features
        this.addPremiumTooltips();
    }
    
    lockNavigationItems() {
        const premiumNavItems = [
            { selector: 'a[href="/backtest"]', feature: 'backtest' },
            { selector: 'a[href="/peer-comparison"]', feature: 'peer-comparison' },
            { selector: 'a[href*="scanner"]', feature: 'ai-scanner' }
        ];
        
        premiumNavItems.forEach(({ selector, feature }) => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                if (this.userPlan === 'free') {
                    this.addPremiumLock(element, feature);
                }
            });
        });
    }
    
    lockPremiumElements() {
        // Find all elements with premium data attributes
        const premiumElements = document.querySelectorAll('[data-premium]');
        premiumElements.forEach(element => {
            const feature = element.dataset.premium;
            if (this.userPlan === 'free' && this.premiumFeatures[feature]) {
                this.addPremiumLock(element, feature);
            }
        });
    }
    
    addPremiumLock(element, featureKey) {
        // Don't lock if already locked
        if (element.classList.contains('premium-locked')) return;
        
        element.classList.add('premium-locked');
        
        // For navigation links, prevent default and show upsell
        if (element.tagName === 'A') {
            element.addEventListener('click', (e) => {
                e.preventDefault();
                this.showUpsellModal(featureKey);
            });
            
            // Add lock icon to the link
            const lockIcon = document.createElement('span');
            lockIcon.className = 'premium-lock-icon ml-2';
            lockIcon.innerHTML = '<i class="fas fa-lock"></i>';
            element.appendChild(lockIcon);
        }
        
        // For cards and buttons, add overlay
        if (element.classList.contains('card') || element.classList.contains('premium-card')) {
            this.addCardOverlay(element, featureKey);
        }
        
        // For buttons, make them show upsell on click
        if (element.tagName === 'BUTTON' || element.classList.contains('btn')) {
            element.addEventListener('click', (e) => {
                e.preventDefault();
                this.showUpsellModal(featureKey);
            });
        }
    }
    
    addCardOverlay(element, featureKey) {
        const feature = this.premiumFeatures[featureKey];
        if (!feature) return;
        
        // Make the card relative positioned
        element.style.position = 'relative';
        
        const overlay = document.createElement('div');
        overlay.className = 'premium-card-overlay';
        overlay.innerHTML = `
            <div class="lock-icon">
                <i class="fas fa-lock"></i>
            </div>
            <div class="lock-message">${feature.name}</div>
            <div class="lock-description">Available with Pro or Enterprise plans</div>
            <button class="unlock-button" onclick="premiumManager.showUpsellModal('${featureKey}')">
                <i class="fas fa-unlock mr-2"></i>Unlock Feature
            </button>
        `;
        
        element.appendChild(overlay);
    }
    
    addPremiumTooltips() {
        const premiumElements = document.querySelectorAll('.premium-locked');
        premiumElements.forEach(element => {
            if (!element.classList.contains('premium-tooltip')) {
                element.classList.add('premium-tooltip');
                element.setAttribute('data-tooltip', 'Available with Pro or Enterprise plans');
            }
        });
    }
    
    showUpsellModal(featureKey) {
        const feature = this.premiumFeatures[featureKey];
        if (!feature) return;
        
        // Update modal content
        const modalIcon = this.upsellModal.querySelector('.upsell-modal-icon i');
        const modalTitle = this.upsellModal.querySelector('.upsell-modal-title');
        const modalSubtitle = this.upsellModal.querySelector('.upsell-modal-subtitle');
        const featuresContainer = this.upsellModal.querySelector('#upsell-features');
        
        modalIcon.className = feature.icon;
        modalTitle.textContent = feature.name;
        modalSubtitle.textContent = feature.description;
        
        // Populate benefits
        featuresContainer.innerHTML = feature.benefits.map(benefit => `
            <div class="upsell-feature-item">
                <div class="upsell-feature-icon">
                    <i class="fas fa-check"></i>
                </div>
                <div class="upsell-feature-content">
                    <h4>${benefit}</h4>
                    <p>Unlock powerful insights with premium features</p>
                </div>
            </div>
        `).join('');
        
        // Show modal
        this.upsellModal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Track modal view
        this.trackEvent('upsell_modal_shown', { feature: featureKey });
    }
    
    closeUpsellModal() {
        this.upsellModal.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    bindEvents() {
        // Upgrade button clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('.navbar-upgrade-btn') || e.target.closest('.navbar-upgrade-btn')) {
                this.trackEvent('upgrade_button_clicked', { location: 'navbar' });
            }
        });
        
        // Premium feature attempts
        document.addEventListener('click', (e) => {
            if (e.target.matches('.premium-locked') || e.target.closest('.premium-locked')) {
                const feature = e.target.dataset.premium || e.target.closest('[data-premium]')?.dataset.premium;
                if (feature) {
                    this.trackEvent('premium_feature_attempted', { feature });
                }
            }
        });
        
        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.upsellModal.classList.contains('active')) {
                this.closeUpsellModal();
            }
        });
    }
    
    trackEvent(event, data = {}) {
        // Send analytics event
        if (typeof gtag !== 'undefined') {
            gtag('event', event, data);
        }
        
        // Also send to our backend for analytics
        fetch('/api/analytics/track', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                event,
                data,
                timestamp: new Date().toISOString()
            })
        }).catch(() => {}); // Silent fail
    }
    
    // Public methods for external use
    unlockFeature(featureKey) {
        const lockedElements = document.querySelectorAll(`[data-premium="${featureKey}"]`);
        lockedElements.forEach(element => {
            element.classList.remove('premium-locked');
            const overlay = element.querySelector('.premium-card-overlay');
            if (overlay) overlay.remove();
            
            const lockIcon = element.querySelector('.premium-lock-icon');
            if (lockIcon) lockIcon.remove();
        });
    }
    
    updateUserPlan(newPlan) {
        this.userPlan = newPlan;
        this.updatePlanBadge();
        
        // Unlock features based on plan
        if (newPlan !== 'free') {
            Object.keys(this.premiumFeatures).forEach(feature => {
                this.unlockFeature(feature);
            });
        }
    }
    
    // Stripe checkout integration
    async createCheckoutSession(planType = 'pro') {
        try {
            const response = await fetch('/api/stripe/create-checkout-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    plan: planType,
                    success_url: window.location.origin + '/premium/success',
                    cancel_url: window.location.origin + '/premium/upgrade'
                })
            });
            
            if (response.ok) {
                const { checkout_url } = await response.json();
                window.location.href = checkout_url;
            } else {
                throw new Error('Failed to create checkout session');
            }
        } catch (error) {
            console.error('Checkout error:', error);
            alert('Unable to process upgrade. Please try again.');
        }
    }
}

// Initialize global premium manager
let premiumManager = null;

document.addEventListener('DOMContentLoaded', function() {
    premiumManager = new PremiumFeaturesManager();
    
    // Make it globally available
    window.premiumManager = premiumManager;
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PremiumFeaturesManager;
}