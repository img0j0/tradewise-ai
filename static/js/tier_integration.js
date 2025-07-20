/**
 * TradeWise AI - Tier Integration System
 * Transforms the main interface based on subscription tier
 */

class TierIntegrationManager {
    constructor() {
        this.currentTier = 'Free';
        this.tierConfig = null;
        this.upgradePrompts = [];
        this.init();
    }

    async init() {
        await this.loadTierConfiguration();
        this.applyTierTransformations();
        this.setupUpgradePrompts();
        
        console.log(`Tier Integration initialized for ${this.currentTier} tier`);
    }

    async loadTierConfiguration() {
        try {
            const response = await fetch('/api/user-tier-config');
            const data = await response.json();
            
            if (data.success) {
                this.tierConfig = data.tier_config;
                this.currentTier = this.tierConfig.tier;
                this.upgradePrompts = this.tierConfig.upgrade_recommendations;
                
                // Apply theme configuration
                this.applyTierTheme();
            }
        } catch (error) {
            console.error('Error loading tier configuration:', error);
            // Fallback to Free tier
            this.currentTier = 'Free';
        }
    }

    applyTierTheme() {
        if (!this.tierConfig?.theme_config) return;

        const theme = this.tierConfig.theme_config;
        const root = document.documentElement;

        // Apply tier-specific colors
        root.style.setProperty('--tier-primary-color', theme.primary_color);
        root.style.setProperty('--tier-accent-color', theme.accent_color);

        // Add tier class to body
        document.body.classList.remove('tier-free', 'tier-pro', 'tier-elite', 'tier-institutional');
        document.body.classList.add(`tier-${this.currentTier.toLowerCase()}`);
    }

    applyTierTransformations() {
        if (!this.tierConfig) return;

        // Transform header based on tier
        this.transformHeader();
        
        // Transform search interface
        this.transformSearchInterface();
        
        // Transform AI assistant capabilities
        this.transformAIAssistant();
        
        // Add tier-specific features
        this.addTierFeatures();
    }

    transformHeader() {
        const headerTitle = document.querySelector('.header-title');
        const upgradeButton = document.getElementById('upgrade-button');
        
        if (headerTitle) {
            // Add tier badge to header
            const tierBadge = this.createTierBadge();
            if (tierBadge && !headerTitle.querySelector('.tier-badge')) {
                headerTitle.appendChild(tierBadge);
            }
        }

        if (upgradeButton) {
            if (this.currentTier === 'Institutional') {
                upgradeButton.style.display = 'none';
            } else {
                upgradeButton.innerHTML = `
                    <i class="fas fa-crown" style="font-size: 0.85rem;"></i>
                    <span>Upgrade to ${this.getNextTier()}</span>
                `;
            }
        }
    }

    createTierBadge() {
        if (this.currentTier === 'Free') return null;

        const badge = document.createElement('span');
        badge.className = `tier-badge tier-${this.currentTier.toLowerCase()}`;
        badge.innerHTML = `<i class="fas fa-crown"></i> ${this.currentTier}`;
        
        const badgeStyles = {
            'Pro': 'background: linear-gradient(135deg, #8b5cf6, #f59e0b); color: white;',
            'Elite': 'background: linear-gradient(135deg, #ef4444, #f97316); color: white;',
            'Institutional': 'background: linear-gradient(135deg, #1f2937, #dc2626); color: white;'
        };

        badge.style.cssText = `
            ${badgeStyles[this.currentTier] || ''}
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-left: 0.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        `;

        return badge;
    }

    transformSearchInterface() {
        const searchInput = document.getElementById('stock-search-input');
        const searchContainer = searchInput?.parentElement;
        
        if (!searchContainer) return;

        // Add tier-specific search enhancements
        const searchConfig = this.tierConfig?.search_enhancements;
        
        if (searchConfig?.suggestions_count > 5) {
            // Enhanced suggestions for Pro+ tiers
            searchInput.setAttribute('data-enhanced-suggestions', 'true');
            searchInput.setAttribute('data-suggestion-limit', searchConfig.suggestions_count);
        }

        // Add tier indicator to search
        if (!searchContainer.querySelector('.search-tier-indicator')) {
            const tierIndicator = this.createSearchTierIndicator();
            searchContainer.appendChild(tierIndicator);
        }
    }

    createSearchTierIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'search-tier-indicator';
        
        const features = [];
        const searchConfig = this.tierConfig?.search_enhancements;
        
        if (searchConfig?.real_time_prices) features.push('Real-time Prices');
        if (searchConfig?.confidence_scores) features.push('AI Confidence');
        if (searchConfig?.level_2_data) features.push('Level 2 Data');
        if (searchConfig?.dark_pool_insights) features.push('Dark Pool Intel');

        indicator.innerHTML = `
            <div class="tier-features-badge">
                <i class="fas fa-shield-check"></i>
                <span>${this.currentTier} Features: ${features.join(', ') || 'Basic'}</span>
            </div>
        `;

        indicator.style.cssText = `
            position: absolute;
            top: -25px;
            right: 0;
            font-size: 0.7rem;
            color: rgba(255,255,255,0.7);
            z-index: 1000;
        `;

        return indicator;
    }

    transformAIAssistant() {
        // Transform AI assistant capabilities based on tier
        const aiCapabilities = this.tierConfig?.ai_capabilities;
        
        if (aiCapabilities) {
            // Store capabilities for AI assistant to use
            window.tierAICapabilities = aiCapabilities;
            
            // Update AI assistant UI if it exists
            const aiButton = document.querySelector('.ai-assistant-toggle');
            if (aiButton && this.currentTier !== 'Free') {
                aiButton.classList.add(`tier-${this.currentTier.toLowerCase()}`);
                
                // Add tier badge to AI assistant
                if (!aiButton.querySelector('.ai-tier-badge')) {
                    const aiBadge = document.createElement('span');
                    aiBadge.className = 'ai-tier-badge';
                    aiBadge.textContent = this.currentTier;
                    aiBadge.style.cssText = `
                        position: absolute;
                        top: -5px;
                        right: -5px;
                        background: ${this.tierConfig.theme_config.accent_color};
                        color: white;
                        font-size: 0.6rem;
                        padding: 0.1rem 0.3rem;
                        border-radius: 8px;
                        font-weight: 600;
                    `;
                    aiButton.appendChild(aiBadge);
                }
            }
        }
    }

    addTierFeatures() {
        const features = this.tierConfig?.ui_features;
        if (!features) return;

        // Add advanced charts for Pro+ tiers
        if (features.advanced_charts) {
            this.enableAdvancedCharts();
        }

        // Add real-time data indicators for Pro+ tiers
        if (features.real_time_data) {
            this.enableRealTimeIndicators();
        }

        // Add dark pool intelligence for Elite+ tiers
        if (features.dark_pool_intelligence) {
            this.enableDarkPoolFeatures();
        }
    }

    enableAdvancedCharts() {
        // Add advanced charting capabilities
        const stockCards = document.querySelectorAll('.stock-result-card');
        stockCards.forEach(card => {
            if (!card.querySelector('.advanced-chart-btn')) {
                const chartBtn = document.createElement('button');
                chartBtn.className = 'btn btn-sm advanced-chart-btn';
                chartBtn.innerHTML = '<i class="fas fa-chart-line"></i> Advanced Chart';
                chartBtn.style.cssText = `
                    background: ${this.tierConfig.theme_config.primary_color};
                    color: white;
                    border: none;
                    margin-top: 0.5rem;
                `;
                card.appendChild(chartBtn);
            }
        });
    }

    enableRealTimeIndicators() {
        // Add real-time data indicators
        const priceElements = document.querySelectorAll('.stock-price');
        priceElements.forEach(element => {
            if (!element.querySelector('.real-time-indicator')) {
                const indicator = document.createElement('span');
                indicator.className = 'real-time-indicator';
                indicator.innerHTML = '<i class="fas fa-circle" style="color: #10b981; font-size: 0.5rem;"></i> LIVE';
                indicator.style.cssText = `
                    font-size: 0.6rem;
                    color: #10b981;
                    margin-left: 0.5rem;
                    animation: pulse 2s infinite;
                `;
                element.appendChild(indicator);
            }
        });
    }

    enableDarkPoolFeatures() {
        // Add dark pool intelligence indicators
        const searchResults = document.getElementById('search-results');
        if (searchResults && !searchResults.querySelector('.dark-pool-panel')) {
            const darkPoolPanel = document.createElement('div');
            darkPoolPanel.className = 'dark-pool-panel';
            darkPoolPanel.innerHTML = `
                <div class="dark-pool-header">
                    <i class="fas fa-eye-slash"></i>
                    <span>Dark Pool Intelligence</span>
                    <span class="elite-badge">ELITE</span>
                </div>
                <div class="dark-pool-content">
                    Institutional flow analysis available for searched stocks
                </div>
            `;
            darkPoolPanel.style.cssText = `
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 8px;
                padding: 1rem;
                margin-top: 1rem;
                color: #ef4444;
            `;
            searchResults.appendChild(darkPoolPanel);
        }
    }

    setupUpgradePrompts() {
        if (this.currentTier === 'Institutional' || !this.upgradePrompts.length) return;

        // Add upgrade prompts to appropriate locations
        this.addSearchUpgradePrompt();
        this.addFeatureLimitPrompts();
    }

    addSearchUpgradePrompt() {
        const searchContainer = document.querySelector('.search-container');
        if (!searchContainer || searchContainer.querySelector('.upgrade-prompt')) return;

        const prompt = this.upgradePrompts[0];
        if (!prompt) return;

        const upgradePrompt = document.createElement('div');
        upgradePrompt.className = 'upgrade-prompt search-upgrade';
        upgradePrompt.innerHTML = `
            <div class="upgrade-content">
                <div class="upgrade-headline">${prompt.headline}</div>
                <div class="upgrade-benefits">
                    ${prompt.benefits.map(benefit => `<div>✨ ${benefit}</div>`).join('')}
                </div>
                <button class="upgrade-cta-btn" onclick="openSubscriptionUpgrade('${prompt.target_tier}')">
                    ${prompt.cta}
                </button>
            </div>
        `;

        upgradePrompt.style.cssText = `
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(16, 185, 129, 0.1));
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 12px;
            padding: 1rem;
            margin-top: 1rem;
            text-align: center;
        `;

        searchContainer.appendChild(upgradePrompt);
    }

    addFeatureLimitPrompts() {
        // Add prompts when users hit tier limits
        const apiLimits = this.tierConfig?.api_limits;
        
        if (apiLimits?.ai_analysis_per_day && apiLimits.ai_analysis_per_day !== 'unlimited') {
            // Add usage counter for AI analysis
            this.setupUsageTracking();
        }
    }

    async enhancedStockSearch(symbol) {
        try {
            const response = await fetch(`/api/tier-enhanced-search/${symbol}`);
            const data = await response.json();
            
            if (data.success) {
                // Process tier-enhanced data
                return this.processEnhancedStockData(data);
            }
            
            return data;
        } catch (error) {
            console.error('Enhanced search error:', error);
            // Fallback to basic search
            return await this.basicStockSearch(symbol);
        }
    }

    processEnhancedStockData(data) {
        // Add tier-specific enhancements to stock data display
        const tierFeatures = data.tier_features;
        
        if (tierFeatures?.confidence_scores) {
            data.enhanced_ui = {
                ...data.enhanced_ui,
                confidence_display: true,
                confidence_score: data.ai_confidence_score
            };
        }

        if (tierFeatures?.level_2_data && data.level_2_data) {
            data.enhanced_ui = {
                ...data.enhanced_ui,
                level_2_display: true,
                level_2_data: data.level_2_data
            };
        }

        if (tierFeatures?.dark_pool_insights && data.dark_pool_activity) {
            data.enhanced_ui = {
                ...data.enhanced_ui,
                dark_pool_display: true,
                dark_pool_data: data.dark_pool_activity
            };
        }

        return data;
    }

    getNextTier() {
        const tiers = ['Free', 'Pro', 'Elite', 'Institutional'];
        const currentIndex = tiers.indexOf(this.currentTier);
        return currentIndex < tiers.length - 1 ? tiers[currentIndex + 1] : 'Institutional';
    }

    async openSubscriptionUpgrade(targetTier) {
        try {
            const response = await fetch(`/api/subscription-upgrade-modal/${targetTier}`);
            const data = await response.json();
            
            if (data.success) {
                this.showUpgradeModal(data.upgrade_content);
            }
        } catch (error) {
            console.error('Error loading upgrade modal:', error);
        }
    }

    showUpgradeModal(content) {
        // Create and show upgrade modal
        const modal = document.createElement('div');
        modal.className = 'tier-upgrade-modal';
        modal.innerHTML = `
            <div class="modal-overlay" onclick="this.parentElement.remove()"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Upgrade to ${content.target_tier}</h3>
                    <button onclick="this.closest('.tier-upgrade-modal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="pricing-info">
                        <div class="price">$${content.pricing.monthly}/month</div>
                        <div class="savings">Save ${content.pricing.savings_vs_bloomberg.percentage}% vs Bloomberg Terminal</div>
                    </div>
                    <div class="benefits-list">
                        ${content.benefits[0]?.benefits?.map(benefit => `<div>✅ ${benefit}</div>`).join('') || ''}
                    </div>
                    <button class="upgrade-btn" onclick="initializeSubscription('${content.target_tier}')">
                        Upgrade Now
                    </button>
                </div>
            </div>
        `;

        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;

        document.body.appendChild(modal);
    }
}

// Global tier integration manager
window.tierIntegration = new TierIntegrationManager();

// Global functions for upgrade system
window.showUpgradeModal = (targetTier) => {
    window.tierIntegration.openSubscriptionUpgrade(targetTier);
};

window.initializeSubscription = (targetTier) => {
    // Placeholder for subscription initialization
    alert(`Initializing ${targetTier} subscription. This would redirect to payment processing.`);
    // In production, this would integrate with Stripe or payment processor
};

// Enhanced global functions
window.openSubscriptionUpgrade = (targetTier) => {
    window.tierIntegration.openSubscriptionUpgrade(targetTier);
};

window.enhancedStockSearch = (symbol) => {
    return window.tierIntegration.enhancedStockSearch(symbol);
};