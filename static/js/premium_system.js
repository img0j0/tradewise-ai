/**
 * Premium System - Handles upsell modals, feature locks, and premium interactions
 */

const PremiumSystem = {
    // Configuration
    config: {
        plans: {
            free: {
                name: 'Free',
                price: 0,
                features: ['Basic stock search', 'Limited AI insights', 'Public market data']
            },
            pro: {
                name: 'Pro',
                price: 29.99,
                features: ['Advanced backtesting', 'Peer comparison', 'Real-time alerts', 'AI market scanner', 'Premium support']
            },
            enterprise: {
                name: 'Enterprise',
                price: 99.99,
                features: ['Team management', 'Custom reports', 'API access', 'Dedicated support', 'White-label options']
            }
        },
        featureDescriptions: {
            'backtest': {
                title: 'Portfolio Backtesting',
                description: 'Test your investment strategies against historical data with advanced analytics and performance metrics.',
                benefits: ['Historical performance analysis', 'Risk-adjusted returns', 'Strategy comparison', 'Drawdown analysis'],
                image: '/static/images/backtest-preview.jpg'
            },
            'peer-analysis': {
                title: 'Peer Comparison',
                description: 'Compare stocks against industry peers with comprehensive financial metrics and competitive analysis.',
                benefits: ['Industry benchmarking', 'Competitive positioning', 'Financial ratio comparison', 'Sector analysis'],
                image: '/static/images/peer-analysis-preview.jpg'
            },
            'alerts': {
                title: 'Smart Market Alerts',
                description: 'Get real-time notifications when your stocks hit target prices or meet specific criteria.',
                benefits: ['Real-time notifications', 'Custom alert criteria', 'SMS and email alerts', 'Portfolio monitoring'],
                image: '/static/images/alerts-preview.jpg'
            },
            'scanner': {
                title: 'AI Market Scanner',
                description: 'Discover new investment opportunities with our AI-powered stock screening and analysis tools.',
                benefits: ['AI-powered screening', 'Custom filters', 'Opportunity scoring', 'Real-time scanning'],
                image: '/static/images/scanner-preview.jpg'
            }
        }
    },
    
    // State management
    state: {
        currentPlan: 'free',
        modalOpen: false,
        currentFeature: null
    },
    
    // Initialize premium system
    init() {
        this.initPremiumLocks();
        this.initUpsellModal();
        this.loadUserPlan();
        
        console.log('Premium System initialized');
    },
    
    // Initialize premium feature locks
    initPremiumLocks() {
        document.querySelectorAll('.premium-lock').forEach(lock => {
            const feature = lock.dataset.feature;
            
            lock.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                // Show upsell modal
                this.showUpsellModal(feature);
                
                // Track premium click
                this.trackPremiumClick(feature);
            });
            
            // Add hover tooltip
            this.addTooltip(lock, feature);
        });
        
        // Handle premium navigation links
        document.querySelectorAll('a[href*="backtest"], a[href*="peer"]').forEach(link => {
            if (this.state.currentPlan === 'free') {
                link.addEventListener('click', (e) => {
                    const url = new URL(link.href);
                    const feature = url.pathname.includes('backtest') ? 'backtest' : 'peer-analysis';
                    
                    if (this.isPremiumFeature(feature)) {
                        e.preventDefault();
                        this.showUpsellModal(feature);
                    }
                });
            }
        });
    },
    
    // Add tooltip to premium locks
    addTooltip(element, feature) {
        const featureInfo = this.config.featureDescriptions[feature];
        const tooltipText = featureInfo ? 
            `${featureInfo.title} - Pro Feature` : 
            'This is a premium feature';
        
        element.setAttribute('title', tooltipText);
        
        // Custom tooltip implementation
        element.addEventListener('mouseenter', (e) => {
            this.showTooltip(e.target, tooltipText);
        });
        
        element.addEventListener('mouseleave', (e) => {
            this.hideTooltip(e.target);
        });
    },
    
    showTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'premium-tooltip-custom';
        tooltip.textContent = text;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.position = 'absolute';
        tooltip.style.top = `${rect.bottom + window.scrollY + 5}px`;
        tooltip.style.left = `${rect.left + window.scrollX}px`;
        
        setTimeout(() => tooltip.classList.add('visible'), 10);
    },
    
    hideTooltip(element) {
        const tooltips = document.querySelectorAll('.premium-tooltip-custom');
        tooltips.forEach(tooltip => {
            tooltip.classList.remove('visible');
            setTimeout(() => tooltip.remove(), 200);
        });
    },
    
    // Initialize upsell modal
    initUpsellModal() {
        const modal = document.getElementById('premium-modal');
        const closeBtn = document.getElementById('premium-modal-close');
        const cancelBtn = document.getElementById('modal-cancel');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hideUpsellModal());
        }
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.hideUpsellModal());
        }
        
        // Close modal on overlay click
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideUpsellModal();
                }
            });
        }
        
        // Close modal on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.state.modalOpen) {
                this.hideUpsellModal();
            }
        });
    },
    
    // Show upsell modal for specific feature
    showUpsellModal(feature) {
        const modal = document.getElementById('premium-modal');
        const preview = document.getElementById('feature-preview');
        
        if (!modal || !preview) return;
        
        this.state.modalOpen = true;
        this.state.currentFeature = feature;
        
        // Generate feature preview content
        const featureInfo = this.config.featureDescriptions[feature] || {
            title: 'Premium Feature',
            description: 'This feature requires a Pro subscription to unlock.',
            benefits: ['Advanced functionality', 'Enhanced performance', 'Priority support'],
            image: '/static/images/premium-default.jpg'
        };
        
        preview.innerHTML = this.generateFeaturePreview(featureInfo);
        
        // Show modal with animation
        modal.classList.remove('hidden');
        setTimeout(() => modal.classList.add('visible'), 10);
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Track modal show
        this.trackModalShow(feature);
    },
    
    // Generate feature preview HTML
    generateFeaturePreview(featureInfo) {
        const benefits = featureInfo.benefits.map(benefit => 
            `<li><i class="fas fa-check text-success-500"></i>${benefit}</li>`
        ).join('');
        
        return `
            <div class="feature-preview-content">
                <div class="feature-hero">
                    <div class="feature-icon">
                        <i class="fas fa-crown text-premium-500"></i>
                    </div>
                    <h4 class="text-subtitle mb-2">${featureInfo.title}</h4>
                    <p class="text-body text-gray-600 mb-4">${featureInfo.description}</p>
                </div>
                
                <div class="feature-preview-image">
                    <div class="preview-placeholder">
                        <i class="fas fa-chart-line text-4xl text-gray-400"></i>
                        <p class="text-body-small text-gray-500 mt-2">Feature Preview</p>
                    </div>
                </div>
                
                <div class="feature-benefits mt-6">
                    <h5 class="text-body-medium font-semibold mb-3">What you'll get:</h5>
                    <ul class="benefits-list">
                        ${benefits}
                    </ul>
                </div>
                
                <div class="upgrade-urgency mt-6 p-4 bg-premium-50 rounded-lg border border-premium-200">
                    <div class="flex items-center gap-3">
                        <i class="fas fa-bolt text-premium-500"></i>
                        <div>
                            <div class="text-body-medium font-semibold text-premium-800">Limited Time Offer</div>
                            <div class="text-body-small text-premium-600">Get 50% off your first month when you upgrade today</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },
    
    // Hide upsell modal
    hideUpsellModal() {
        const modal = document.getElementById('premium-modal');
        
        if (!modal) return;
        
        this.state.modalOpen = false;
        this.state.currentFeature = null;
        
        // Hide modal with animation
        modal.classList.remove('visible');
        setTimeout(() => modal.classList.add('hidden'), 200);
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Track modal close
        this.trackModalClose();
    },
    
    // Check if feature is premium-only
    isPremiumFeature(feature) {
        const premiumFeatures = ['backtest', 'peer-analysis', 'alerts', 'scanner', 'reports', 'api'];
        return premiumFeatures.includes(feature);
    },
    
    // Load user's current plan
    async loadUserPlan() {
        try {
            const response = await fetch('/api/user/plan');
            if (response.ok) {
                const data = await response.json();
                this.updateUserPlan(data.plan || 'free');
            }
        } catch (error) {
            console.warn('Could not load user plan:', error);
            this.updateUserPlan('free');
        }
    },
    
    // Update user plan and UI
    updateUserPlan(plan) {
        this.state.currentPlan = plan.toLowerCase();
        
        // Update plan badge
        const badge = document.getElementById('plan-badge');
        if (badge) {
            badge.textContent = this.config.plans[this.state.currentPlan].name;
            badge.className = `plan-badge ${this.state.currentPlan}`;
        }
        
        // Show/hide upgrade button
        const upgradeBtn = document.getElementById('upgrade-btn');
        if (upgradeBtn) {
            upgradeBtn.style.display = this.state.currentPlan === 'free' ? 'flex' : 'none';
        }
        
        // Update premium locks visibility
        this.updatePremiumLocksVisibility();
        
        // Update user dropdown
        this.updateUserDropdown();
    },
    
    // Update premium locks visibility based on plan
    updatePremiumLocksVisibility() {
        document.querySelectorAll('.premium-lock').forEach(lock => {
            const feature = lock.dataset.feature;
            const shouldShow = this.state.currentPlan === 'free' && this.isPremiumFeature(feature);
            
            lock.style.display = shouldShow ? 'inline-flex' : 'none';
        });
        
        // Update premium badges in mobile menu
        document.querySelectorAll('.premium-badge').forEach(badge => {
            badge.style.display = this.state.currentPlan === 'free' ? 'inline' : 'none';
        });
    },
    
    // Update user dropdown
    updateUserDropdown() {
        const dropdown = document.getElementById('user-dropdown');
        if (!dropdown) return;
        
        const planText = dropdown.querySelector('.dropdown-header .text-caption');
        if (planText) {
            planText.textContent = `${this.config.plans[this.state.currentPlan].name} Plan`;
        }
        
        // Show/hide upgrade link
        const upgradeLink = dropdown.querySelector('.premium-item');
        if (upgradeLink) {
            upgradeLink.style.display = this.state.currentPlan === 'free' ? 'flex' : 'none';
        }
    },
    
    // Handle successful upgrade
    handleUpgradeSuccess(newPlan) {
        this.updateUserPlan(newPlan);
        this.hideUpsellModal();
        
        // Show success message
        SaaSApp.showToast(`Welcome to ${this.config.plans[newPlan].name}! 🎉`, 'success', 5000);
        
        // Track upgrade
        this.trackUpgrade(newPlan);
        
        // Refresh page to show new features
        setTimeout(() => {
            window.location.reload();
        }, 2000);
    },
    
    // Pricing helpers
    formatPrice(price) {
        if (price === 0) return 'Free';
        return `$${price.toFixed(2)}/month`;
    },
    
    getPlanFeatures(plan) {
        return this.config.plans[plan]?.features || [];
    },
    
    // Analytics and tracking
    trackPremiumClick(feature) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'premium_feature_click', {
                feature: feature,
                current_plan: this.state.currentPlan
            });
        }
        
        SaaSApp.trackFeatureClick(`premium_${feature}`);
    },
    
    trackModalShow(feature) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'upsell_modal_show', {
                feature: feature,
                current_plan: this.state.currentPlan
            });
        }
    },
    
    trackModalClose() {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'upsell_modal_close', {
                feature: this.state.currentFeature,
                current_plan: this.state.currentPlan
            });
        }
    },
    
    trackUpgrade(newPlan) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'purchase', {
                transaction_id: Date.now().toString(),
                value: this.config.plans[newPlan].price,
                currency: 'USD',
                items: [{
                    item_id: `plan_${newPlan}`,
                    item_name: `${this.config.plans[newPlan].name} Plan`,
                    category: 'subscription',
                    quantity: 1,
                    price: this.config.plans[newPlan].price
                }]
            });
        }
    }
};

// Export for use in other modules
window.PremiumSystem = PremiumSystem;