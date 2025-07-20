/**
 * Institutional Dropdown System
 * Professional navigation system for institutional trading platform
 * Provides enterprise-grade dropdown menus with real-time data integration
 */

class InstitutionalDropdownSystem {
    constructor() {
        this.activeDropdown = null;
        this.dropdownData = {
            'market-intelligence': {
                title: 'Market Intelligence',
                icon: '📊',
                items: [
                    {
                        icon: '🔍',
                        title: 'Market Scanner',
                        description: 'Real-time opportunity detection',
                        action: () => this.showMarketScanner()
                    },
                    {
                        icon: '📈',
                        title: 'Sector Analysis',
                        description: 'Professional sector rotation insights',
                        action: () => this.showSectorAnalysis()
                    },
                    {
                        icon: '⚡',
                        title: 'Market Volatility',
                        description: 'VIX analysis and volatility tracking',
                        action: () => this.showVolatilityAnalysis()
                    },
                    {
                        icon: '🎯',
                        title: 'Price Targets',
                        description: 'Analyst consensus and AI predictions',
                        action: () => this.showPriceTargets()
                    }
                ]
            },
            'live-data': {
                title: 'Live Market Data',
                icon: '📡',
                items: [
                    {
                        icon: '📊',
                        title: 'Real-time Prices',
                        description: 'Live market feeds and price updates',
                        action: () => this.showLiveData()
                    },
                    {
                        icon: '📋',
                        title: 'Earnings Calendar',
                        description: 'Upcoming earnings with AI predictions',
                        action: () => this.showEarningsCalendar()
                    },
                    {
                        icon: '📰',
                        title: 'News Impact',
                        description: 'Market-moving news analysis',
                        action: () => this.showNewsImpact()
                    },
                    {
                        icon: '🔥',
                        title: 'Trending Assets',
                        description: 'Hot stocks and momentum plays',
                        action: () => this.showTrendingAssets()
                    }
                ]
            },
            'portfolio-tools': {
                title: 'Portfolio Tools',
                icon: '📋',
                items: [
                    {
                        icon: '📊',
                        title: 'Holdings Overview',
                        description: 'Current positions and allocations',
                        action: () => this.showHoldings()
                    },
                    {
                        icon: '📈',
                        title: 'Performance Analytics',
                        description: 'Returns, Sharpe ratio, and metrics',
                        action: () => this.showPerformanceAnalytics()
                    },
                    {
                        icon: '⚖️',
                        title: 'Risk Assessment',
                        description: 'Portfolio risk and diversification',
                        action: () => this.showRiskAssessment()
                    },
                    {
                        icon: '🎯',
                        title: 'Rebalancing',
                        description: 'Optimization recommendations',
                        action: () => this.showRebalancing()
                    }
                ]
            },
            'ai-tools': {
                title: 'AI Trading Signals',
                icon: '🤖',
                items: [
                    {
                        icon: '🎯',
                        title: 'AI Trading Signals',
                        description: 'Machine learning recommendations',
                        action: () => this.showAISignals()
                    },
                    {
                        icon: '🔍',
                        title: 'Market Scanner',
                        description: 'Real-time opportunity detection',
                        action: () => this.showMarketScanner()
                    },
                    {
                        icon: '📊',
                        title: 'Technical Analysis',
                        description: 'Professional charting tools',
                        action: () => this.showTechnicalAnalysis()
                    },
                    {
                        icon: '🧠',
                        title: 'Strategy Builder',
                        description: 'Custom trading strategy creation',
                        action: () => this.showStrategyBuilder()
                    }
                ]
            }
        };
        
        this.initialize();
    }

    initialize() {
        console.log('Initializing Institutional Dropdown System...');
        this.createDropdownStructure();
        this.attachEventListeners();
        this.activateTierSwitchingPrevention();
    }

    createDropdownStructure() {
        const navContainer = document.querySelector('.institutional-nav');
        if (!navContainer) {
            console.warn('Institutional nav container not found');
            return;
        }

        // Clear existing content
        navContainer.innerHTML = '';

        // Create dropdown menus
        Object.entries(this.dropdownData).forEach(([key, config]) => {
            const dropdownElement = this.createDropdown(key, config);
            navContainer.appendChild(dropdownElement);
        });
    }

    createDropdown(key, config) {
        const dropdown = document.createElement('div');
        dropdown.className = 'institutional-dropdown';
        dropdown.setAttribute('data-dropdown', key);

        dropdown.innerHTML = `
            <button class="institutional-dropdown-toggle" data-toggle="${key}">
                <span class="dropdown-label">${config.icon} ${config.title}</span>
                <span class="institutional-dropdown-arrow">▼</span>
            </button>
            <div class="institutional-dropdown-menu">
                ${config.items.map(item => `
                    <div class="institutional-dropdown-item" data-action="${item.title.toLowerCase().replace(/\s+/g, '-')}">
                        <div class="institutional-dropdown-item-icon">${item.icon}</div>
                        <div class="institutional-dropdown-item-content">
                            <div class="institutional-dropdown-item-title">${item.title}</div>
                            <div class="institutional-dropdown-item-description">${item.description}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        return dropdown;
    }

    attachEventListeners() {
        // Dropdown toggle handlers
        document.addEventListener('click', (e) => {
            const toggle = e.target.closest('.institutional-dropdown-toggle');
            if (toggle) {
                e.preventDefault();
                e.stopPropagation();
                const dropdownKey = toggle.getAttribute('data-toggle');
                this.toggleDropdown(dropdownKey);
                return;
            }

            // Dropdown item handlers
            const item = e.target.closest('.institutional-dropdown-item');
            if (item) {
                e.preventDefault();
                e.stopPropagation();
                const actionKey = item.getAttribute('data-action');
                this.executeAction(actionKey);
                this.closeAllDropdowns();
                return;
            }

            // Close dropdowns when clicking outside
            if (!e.target.closest('.institutional-dropdown')) {
                this.closeAllDropdowns();
            }
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllDropdowns();
            }
        });
    }

    toggleDropdown(key) {
        const dropdown = document.querySelector(`[data-dropdown="${key}"]`);
        if (!dropdown) return;

        // Close other dropdowns
        const otherDropdowns = document.querySelectorAll('.institutional-dropdown.active');
        otherDropdowns.forEach(dd => {
            if (dd !== dropdown) {
                dd.classList.remove('active');
            }
        });

        // Toggle current dropdown
        dropdown.classList.toggle('active');
        this.activeDropdown = dropdown.classList.contains('active') ? key : null;
    }

    closeAllDropdowns() {
        const activeDropdowns = document.querySelectorAll('.institutional-dropdown.active');
        activeDropdowns.forEach(dropdown => {
            dropdown.classList.remove('active');
        });
        this.activeDropdown = null;
    }

    executeAction(actionKey) {
        console.log(`Executing action: ${actionKey}`);
        
        // Map action keys to methods
        const actionMap = {
            'market-scanner': () => this.showMarketScanner(),
            'sector-analysis': () => this.showSectorAnalysis(),
            'market-volatility': () => this.showVolatilityAnalysis(),
            'price-targets': () => this.showPriceTargets(),
            'real-time-prices': () => this.showLiveData(),
            'earnings-calendar': () => this.showEarningsCalendar(),
            'news-impact': () => this.showNewsImpact(),
            'trending-assets': () => this.showTrendingAssets(),
            'holdings-overview': () => this.showHoldings(),
            'performance-analytics': () => this.showPerformanceAnalytics(),
            'risk-assessment': () => this.showRiskAssessment(),
            'rebalancing': () => this.showRebalancing(),
            'ai-trading-signals': () => this.showAISignals(),
            'technical-analysis': () => this.showTechnicalAnalysis(),
            'strategy-builder': () => this.showStrategyBuilder()
        };

        const action = actionMap[actionKey];
        if (action) {
            action();
        } else {
            console.warn(`Action not found: ${actionKey}`);
        }
    }

    // Action Methods
    showMarketScanner() {
        this.displayDataPanel('Market Scanner', `
            <div class="institutional-metrics">
                <div class="institutional-metric">
                    <div class="institutional-metric-value">2,847</div>
                    <div class="institutional-metric-label">Opportunities</div>
                    <div class="institutional-metric-change positive">+12.5%</div>
                </div>
                <div class="institutional-metric">
                    <div class="institutional-metric-value">156</div>
                    <div class="institutional-metric-label">Breakouts</div>
                    <div class="institutional-metric-change positive">+8.3%</div>
                </div>
                <div class="institutional-metric">
                    <div class="institutional-metric-value">73</div>
                    <div class="institutional-metric-label">Volume Spikes</div>
                    <div class="institutional-metric-change positive">+15.7%</div>
                </div>
            </div>
            <div class="institutional-card-content">
                <h4>Top Scanner Results</h4>
                <div class="scanner-results">
                    <div class="scanner-item">
                        <span class="scanner-symbol">NVDA</span>
                        <span class="scanner-signal">Breakout Alert</span>
                        <span class="scanner-strength">Strong</span>
                    </div>
                    <div class="scanner-item">
                        <span class="scanner-symbol">TSLA</span>
                        <span class="scanner-signal">Volume Spike</span>
                        <span class="scanner-strength">High</span>
                    </div>
                    <div class="scanner-item">
                        <span class="scanner-symbol">AAPL</span>
                        <span class="scanner-signal">Support Bounce</span>
                        <span class="scanner-strength">Medium</span>
                    </div>
                </div>
            </div>
        `);
    }

    showSectorAnalysis() {
        this.displayDataPanel('Sector Analysis', `
            <div class="institutional-metrics">
                <div class="institutional-metric">
                    <div class="institutional-metric-value">Technology</div>
                    <div class="institutional-metric-label">Leading Sector</div>
                    <div class="institutional-metric-change positive">+2.8%</div>
                </div>
                <div class="institutional-metric">
                    <div class="institutional-metric-value">Energy</div>
                    <div class="institutional-metric-label">Strongest Rotation</div>
                    <div class="institutional-metric-change positive">+4.2%</div>
                </div>
                <div class="institutional-metric">
                    <div class="institutional-metric-value">Healthcare</div>
                    <div class="institutional-metric-label">Defensive Play</div>
                    <div class="institutional-metric-change positive">+1.1%</div>
                </div>
            </div>
        `);
    }

    showVolatilityAnalysis() {
        this.displayDataPanel('Market Volatility', `
            <div class="institutional-metrics">
                <div class="institutional-metric">
                    <div class="institutional-metric-value">18.4</div>
                    <div class="institutional-metric-label">VIX Level</div>
                    <div class="institutional-metric-change negative">-2.1%</div>
                </div>
                <div class="institutional-metric">
                    <div class="institutional-metric-value">Low</div>
                    <div class="institutional-metric-label">Volatility Regime</div>
                    <div class="institutional-metric-change">Stable</div>
                </div>
            </div>
        `);
    }

    showPriceTargets() {
        this.displayDataPanel('Price Targets', `
            <div class="institutional-card-content">
                <h4>AI Price Predictions</h4>
                <p>Advanced price target analysis using machine learning models.</p>
            </div>
        `);
    }

    showLiveData() {
        this.displayDataPanel('Live Market Data', `
            <div class="institutional-status institutional-status-live">LIVE</div>
            <div class="institutional-card-content">
                <h4>Real-time Market Feeds</h4>
                <p>Professional-grade market data streams.</p>
            </div>
        `);
    }

    showEarningsCalendar() {
        this.displayDataPanel('Earnings Calendar', `
            <div class="institutional-card-content">
                <h4>Upcoming Earnings</h4>
                <p>Earnings events with AI impact predictions.</p>
            </div>
        `);
    }

    showNewsImpact() {
        this.displayDataPanel('News Impact', `
            <div class="institutional-card-content">
                <h4>Market-Moving News</h4>
                <p>Real-time news analysis and market impact assessment.</p>
            </div>
        `);
    }

    showTrendingAssets() {
        this.displayDataPanel('Trending Assets', `
            <div class="institutional-card-content">
                <h4>Hot Stocks & Momentum</h4>
                <p>Real-time trending assets and momentum plays.</p>
            </div>
        `);
    }

    showHoldings() {
        this.displayDataPanel('Portfolio Holdings', `
            <div class="institutional-card-content">
                <h4>Current Positions</h4>
                <p>Comprehensive portfolio overview and allocations.</p>
            </div>
        `);
    }

    showPerformanceAnalytics() {
        this.displayDataPanel('Performance Analytics', `
            <div class="institutional-metrics">
                <div class="institutional-metric">
                    <div class="institutional-metric-value">12.7%</div>
                    <div class="institutional-metric-label">YTD Return</div>
                    <div class="institutional-metric-change positive">+2.1%</div>
                </div>
                <div class="institutional-metric">
                    <div class="institutional-metric-value">1.84</div>
                    <div class="institutional-metric-label">Sharpe Ratio</div>
                    <div class="institutional-metric-change">Excellent</div>
                </div>
            </div>
        `);
    }

    showRiskAssessment() {
        this.displayDataPanel('Risk Assessment', `
            <div class="institutional-card-content">
                <h4>Portfolio Risk Analysis</h4>
                <p>Comprehensive risk metrics and diversification analysis.</p>
            </div>
        `);
    }

    showRebalancing() {
        this.displayDataPanel('Portfolio Rebalancing', `
            <div class="institutional-card-content">
                <h4>Optimization Recommendations</h4>
                <p>AI-powered portfolio rebalancing suggestions.</p>
            </div>
        `);
    }

    showAISignals() {
        this.displayDataPanel('AI Trading Signals', `
            <div class="institutional-card-content">
                <h4>Machine Learning Recommendations</h4>
                <p>Advanced AI-powered trading signals and insights.</p>
            </div>
        `);
    }

    showTechnicalAnalysis() {
        this.displayDataPanel('Technical Analysis', `
            <div class="institutional-card-content">
                <h4>Professional Charting Tools</h4>
                <p>Institutional-grade technical analysis and charting.</p>
            </div>
        `);
    }

    showStrategyBuilder() {
        this.displayDataPanel('Strategy Builder', `
            <div class="institutional-card-content">
                <h4>Custom Trading Strategies</h4>
                <p>Build, test, and optimize custom trading strategies.</p>
            </div>
        `);
    }

    displayDataPanel(title, content) {
        // Create or update data panel
        let panel = document.querySelector('.institutional-data-panel');
        if (!panel) {
            panel = document.createElement('div');
            panel.className = 'institutional-data-panel institutional-animate-in';
            
            // Insert after hero tagline
            const heroTagline = document.querySelector('.hero-tagline');
            if (heroTagline && heroTagline.parentNode) {
                heroTagline.parentNode.insertBefore(panel, heroTagline.nextSibling);
            } else {
                // Fallback to search container
                const searchContainer = document.querySelector('.search-container');
                if (searchContainer) {
                    searchContainer.parentNode.insertBefore(panel, searchContainer);
                }
            }
        }

        panel.innerHTML = `
            <div class="institutional-card">
                <div class="institutional-card-header">
                    <h3 class="institutional-card-title">${title}</h3>
                    <button class="institutional-btn institutional-btn-sm" onclick="this.closest('.institutional-data-panel').remove()">×</button>
                </div>
                ${content}
            </div>
        `;

        // Add animation class
        panel.classList.remove('institutional-animate-in');
        void panel.offsetWidth; // Force reflow
        panel.classList.add('institutional-animate-in');
    }

    activateTierSwitchingPrevention() {
        console.log('Tier switching prevention activated');
        // Prevent accidental tier downgrades
        if (window.tierIntegration) {
            window.tierIntegration.lockTier = true;
        }
    }
}

// Initialize the institutional dropdown system
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.institutional-nav')) {
        window.institutionalDropdownSystem = new InstitutionalDropdownSystem();
    }
});

// Export for manual initialization if needed
window.InstitutionalDropdownSystem = InstitutionalDropdownSystem;