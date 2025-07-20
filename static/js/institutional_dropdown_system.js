/**
 * Institutional Dropdown System
 * Advanced dropdown management for professional trading platform
 * Designed for institutional users and professional traders
 */

class InstitutionalDropdownSystem {
    constructor() {
        this.dropdowns = new Map();
        this.activeDropdown = null;
        this.init();
    }

    init() {
        console.log('Initializing Institutional Dropdown System...');
        this.createDropdownElements();
        this.bindEvents();
        this.optimizeExistingInterface();
    }

    createDropdownElements() {
        // Market Intelligence Dropdown
        this.createMarketIntelligenceDropdown();
        
        // Portfolio Management Dropdown
        this.createPortfolioDropdown();
        
        // Trading Tools Dropdown
        this.createTradingToolsDropdown();
        
        // Analytics & Reports Dropdown
        this.createAnalyticsDropdown();
        
        // Risk Management Dropdown
        this.createRiskManagementDropdown();
    }

    createMarketIntelligenceDropdown() {
        const container = document.querySelector('.institutional-nav, .header-content');
        if (!container || container.querySelector('.market-intelligence-dropdown')) return;

        const dropdown = this.createDropdown('market-intelligence', '📊 Market Intelligence', [
            {
                icon: '📈',
                title: 'Live Market Data',
                description: 'Real-time market feeds and price updates',
                action: () => this.showLiveMarketData()
            },
            {
                icon: '🎯',
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
                icon: '🔥',
                title: 'Trending Assets',
                description: 'Hot stocks and momentum plays',
                action: () => this.showTrendingAssets()
            },
            {
                icon: '📰',
                title: 'News Impact',
                description: 'Market-moving news analysis',
                action: () => this.showNewsImpact()
            }
        ]);

        container.appendChild(dropdown);
    }

    createPortfolioDropdown() {
        const container = document.querySelector('.institutional-nav, .header-content');
        if (!container || container.querySelector('.portfolio-dropdown')) return;

        const dropdown = this.createDropdown('portfolio', '💼 Portfolio', [
            {
                icon: '📊',
                title: 'Holdings Overview',
                description: 'Current positions and allocations',
                action: () => this.showPortfolioOverview()
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
            },
            {
                icon: '💰',
                title: 'Tax Optimization',
                description: 'Tax-loss harvesting opportunities',
                action: () => this.showTaxOptimization()
            }
        ]);

        container.appendChild(dropdown);
    }

    createTradingToolsDropdown() {
        const container = document.querySelector('.institutional-nav, .header-content');
        if (!container || container.querySelector('.trading-tools-dropdown')) return;

        const dropdown = this.createDropdown('trading-tools', '🛠️ Trading Tools', [
            {
                icon: '📋',
                title: 'Order Management',
                description: 'Advanced order types and execution',
                action: () => this.showOrderManagement()
            },
            {
                icon: '📊',
                title: 'Technical Analysis',
                description: 'Professional charting tools',
                action: () => this.showTechnicalAnalysis()
            },
            {
                icon: '🤖',
                title: 'AI Trading Signals',
                description: 'Machine learning recommendations',
                action: () => this.showAISignals()
            },
            {
                icon: '⏰',
                title: 'Market Scanner',
                description: 'Real-time opportunity detection',
                action: () => this.showMarketScanner()
            },
            {
                icon: '🎯',
                title: 'Strategy Builder',
                description: 'Custom trading strategy creation',
                action: () => this.showStrategyBuilder()
            }
        ]);

        container.appendChild(dropdown);
    }

    createAnalyticsDropdown() {
        const container = document.querySelector('.institutional-nav, .header-content');
        if (!container || container.querySelector('.analytics-dropdown')) return;

        const dropdown = this.createDropdown('analytics', '📈 Analytics', [
            {
                icon: '📊',
                title: 'Performance Reports',
                description: 'Comprehensive trading analytics',
                action: () => this.showPerformanceReports()
            },
            {
                icon: '🎯',
                title: 'Attribution Analysis',
                description: 'Factor-based performance breakdown',
                action: () => this.showAttributionAnalysis()
            },
            {
                icon: '📈',
                title: 'Benchmark Comparison',
                description: 'Compare against indices and peers',
                action: () => this.showBenchmarkComparison()
            },
            {
                icon: '🔍',
                title: 'Trade Analysis',
                description: 'Individual trade performance review',
                action: () => this.showTradeAnalysis()
            },
            {
                icon: '📋',
                title: 'Custom Reports',
                description: 'Build personalized analytics',
                action: () => this.showCustomReports()
            }
        ]);

        container.appendChild(dropdown);
    }

    createRiskManagementDropdown() {
        const container = document.querySelector('.institutional-nav, .header-content');
        if (!container || container.querySelector('.risk-management-dropdown')) return;

        const dropdown = this.createDropdown('risk-management', '🛡️ Risk Management', [
            {
                icon: '⚠️',
                title: 'Risk Monitoring',
                description: 'Real-time risk exposure tracking',
                action: () => this.showRiskMonitoring()
            },
            {
                icon: '🎯',
                title: 'Position Sizing',
                description: 'Optimal position size calculator',
                action: () => this.showPositionSizing()
            },
            {
                icon: '🔄',
                title: 'Correlation Analysis',
                description: 'Portfolio correlation monitoring',
                action: () => this.showCorrelationAnalysis()
            },
            {
                icon: '📉',
                title: 'Stress Testing',
                description: 'Portfolio stress scenario analysis',
                action: () => this.showStressTesting()
            },
            {
                icon: '🚨',
                title: 'Alert Management',
                description: 'Risk-based alert configuration',
                action: () => this.showAlertManagement()
            }
        ]);

        container.appendChild(dropdown);
    }

    createDropdown(id, title, items) {
        const dropdown = document.createElement('div');
        dropdown.className = 'institutional-dropdown';
        dropdown.setAttribute('data-dropdown-id', id);

        dropdown.innerHTML = `
            <button class="institutional-dropdown-toggle" type="button">
                <span class="dropdown-title">${title}</span>
                <span class="institutional-dropdown-arrow">▼</span>
            </button>
            <div class="institutional-dropdown-menu">
                ${items.map(item => `
                    <div class="institutional-dropdown-item" data-action="${item.title}">
                        <span class="institutional-dropdown-item-icon">${item.icon}</span>
                        <div class="institutional-dropdown-item-content">
                            <div class="institutional-dropdown-item-title">${item.title}</div>
                            <div class="institutional-dropdown-item-description">${item.description}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        // Store dropdown reference with actions
        this.dropdowns.set(id, {
            element: dropdown,
            items: items
        });

        return dropdown;
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            // Handle dropdown toggle
            const toggle = e.target.closest('.institutional-dropdown-toggle');
            if (toggle) {
                e.stopPropagation();
                const dropdown = toggle.closest('.institutional-dropdown');
                this.toggleDropdown(dropdown);
                return;
            }

            // Handle dropdown item click
            const item = e.target.closest('.institutional-dropdown-item');
            if (item) {
                e.stopPropagation();
                this.handleDropdownItemClick(item);
                return;
            }

            // Close dropdown when clicking outside
            if (this.activeDropdown && !e.target.closest('.institutional-dropdown')) {
                this.closeAllDropdowns();
            }
        });

        // Close dropdowns on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeDropdown) {
                this.closeAllDropdowns();
            }
        });
    }

    toggleDropdown(dropdown) {
        const isActive = dropdown.classList.contains('active');
        
        // Close all other dropdowns
        this.closeAllDropdowns();
        
        if (!isActive) {
            dropdown.classList.add('active');
            this.activeDropdown = dropdown;
        }
    }

    closeAllDropdowns() {
        document.querySelectorAll('.institutional-dropdown.active').forEach(dropdown => {
            dropdown.classList.remove('active');
        });
        this.activeDropdown = null;
    }

    handleDropdownItemClick(item) {
        const dropdown = item.closest('.institutional-dropdown');
        const dropdownId = dropdown.getAttribute('data-dropdown-id');
        const actionTitle = item.getAttribute('data-action');
        
        const dropdownData = this.dropdowns.get(dropdownId);
        if (dropdownData) {
            const itemData = dropdownData.items.find(i => i.title === actionTitle);
            if (itemData && itemData.action) {
                itemData.action();
            }
        }
        
        this.closeAllDropdowns();
    }

    optimizeExistingInterface() {
        // Hide or consolidate existing elements that are now in dropdowns
        this.consolidateMarketData();
        this.optimizeHeaderSpace();
        this.improveSearchInterface();
    }

    consolidateMarketData() {
        // Hide redundant market data displays
        const tickerTape = document.querySelector('.ticker-tape');
        if (tickerTape) {
            tickerTape.style.display = 'none';
        }

        // Consolidate real-time dashboard
        const dashboard = document.querySelector('.real-time-dashboard');
        if (dashboard) {
            dashboard.style.display = 'none';
        }
    }

    optimizeHeaderSpace() {
        // Clean up header by moving elements to dropdowns
        const header = document.querySelector('.header-content, .d-flex.justify-content-between');
        if (header) {
            header.style.padding = '1rem 2rem';
            header.style.gap = '1.5rem';
        }
    }

    improveSearchInterface() {
        // Enhance search with professional styling
        const searchContainer = document.querySelector('.search-container, .search-section');
        if (searchContainer) {
            searchContainer.classList.add('institutional-search-container');
        }

        const searchInput = document.querySelector('#search-input, .search-input');
        if (searchInput) {
            searchInput.classList.add('institutional-search-input');
            searchInput.placeholder = 'Search stocks, ETFs, options, or analyze market data...';
        }
    }

    // Action methods for dropdown items
    showLiveMarketData() {
        console.log('Showing live market data...');
        this.displayDataPanel('market-data', 'Live Market Data', this.generateMarketDataContent());
    }

    showSectorAnalysis() {
        console.log('Showing sector analysis...');
        this.displayDataPanel('sector-analysis', 'Sector Analysis', this.generateSectorAnalysisContent());
    }

    showVolatilityAnalysis() {
        console.log('Showing volatility analysis...');
        this.displayDataPanel('volatility', 'Market Volatility Analysis', this.generateVolatilityContent());
    }

    showTrendingAssets() {
        console.log('Showing trending assets...');
        this.displayDataPanel('trending', 'Trending Assets', this.generateTrendingAssetsContent());
    }

    showNewsImpact() {
        console.log('Showing news impact...');
        this.displayDataPanel('news', 'News Impact Analysis', this.generateNewsImpactContent());
    }

    showPortfolioOverview() {
        console.log('Showing portfolio overview...');
        window.location.href = '/portfolio';
    }

    showPerformanceAnalytics() {
        console.log('Showing performance analytics...');
        this.displayDataPanel('performance', 'Performance Analytics', this.generatePerformanceContent());
    }

    showRiskAssessment() {
        console.log('Showing risk assessment...');
        this.displayDataPanel('risk', 'Risk Assessment', this.generateRiskAssessmentContent());
    }

    showRebalancing() {
        console.log('Showing rebalancing recommendations...');
        this.displayDataPanel('rebalancing', 'Portfolio Rebalancing', this.generateRebalancingContent());
    }

    showTaxOptimization() {
        console.log('Showing tax optimization...');
        this.displayDataPanel('tax', 'Tax Optimization', this.generateTaxOptimizationContent());
    }

    showOrderManagement() {
        console.log('Showing order management...');
        this.displayDataPanel('orders', 'Order Management', this.generateOrderManagementContent());
    }

    showTechnicalAnalysis() {
        console.log('Showing technical analysis...');
        this.displayDataPanel('technical', 'Technical Analysis', this.generateTechnicalAnalysisContent());
    }

    showAISignals() {
        console.log('Showing AI trading signals...');
        this.displayDataPanel('ai-signals', 'AI Trading Signals', this.generateAISignalsContent());
    }

    showMarketScanner() {
        console.log('Showing market scanner...');
        this.displayDataPanel('scanner', 'Market Scanner', this.generateMarketScannerContent());
    }

    showStrategyBuilder() {
        console.log('Showing strategy builder...');
        window.location.href = '/advanced#strategy-builder';
    }

    displayDataPanel(id, title, content) {
        // Remove existing panel
        const existingPanel = document.querySelector('.institutional-data-panel');
        if (existingPanel) {
            existingPanel.remove();
        }

        // Create new panel
        const panel = document.createElement('div');
        panel.className = 'institutional-data-panel institutional-animate-in';
        panel.setAttribute('data-panel-id', id);
        
        panel.innerHTML = `
            <div class="institutional-card">
                <div class="institutional-card-header">
                    <h3 class="institutional-card-title">${title}</h3>
                    <button class="institutional-btn institutional-btn-sm" onclick="this.closest('.institutional-data-panel').remove()">
                        ✕ Close
                    </button>
                </div>
                <div class="institutional-card-content">
                    ${content}
                </div>
            </div>
        `;

        // Insert after search section
        const searchSection = document.querySelector('.search-section, .main-content');
        if (searchSection) {
            searchSection.appendChild(panel);
        }
    }

    generateMarketDataContent() {
        return `
            <div class="institutional-metrics">
                <div class="institutional-metric">
                    <div class="institutional-metric-value">4,567.23</div>
                    <div class="institutional-metric-label">S&P 500</div>
                    <div class="institutional-metric-change positive">+1.24%</div>
                </div>
                <div class="institutional-metric">
                    <div class="institutional-metric-value">14,823.41</div>
                    <div class="institutional-metric-label">NASDAQ</div>
                    <div class="institutional-metric-change positive">+0.87%</div>
                </div>
                <div class="institutional-metric">
                    <div class="institutional-metric-value">35,241.67</div>
                    <div class="institutional-metric-label">DOW JONES</div>
                    <div class="institutional-metric-change negative">-0.23%</div>
                </div>
                <div class="institutional-metric">
                    <div class="institutional-metric-value">16.42</div>
                    <div class="institutional-metric-label">VIX</div>
                    <div class="institutional-metric-change positive">+2.15%</div>
                </div>
            </div>
            <div style="margin-top: 1.5rem;">
                <h4 style="color: var(--institutional-text); margin-bottom: 1rem;">Market Highlights</h4>
                <ul style="color: var(--institutional-text-muted); line-height: 1.6;">
                    <li>Technology sector leading gains with 2.1% increase</li>
                    <li>Energy sector under pressure, down 1.8%</li>
                    <li>Federal Reserve minutes show hawkish sentiment</li>
                    <li>Earnings season begins next week</li>
                </ul>
            </div>
        `;
    }

    generateSectorAnalysisContent() {
        return `
            <div class="institutional-metrics">
                <div class="institutional-metric">
                    <div class="institutional-metric-value">+2.34%</div>
                    <div class="institutional-metric-label">Technology</div>
                    <div class="institutional-status institutional-status-live">HOT</div>
                </div>
                <div class="institutional-metric">
                    <div class="institutional-metric-value">+1.87%</div>
                    <div class="institutional-metric-label">Healthcare</div>
                    <div class="institutional-status institutional-status-info">STABLE</div>
                </div>
                <div class="institutional-metric">
                    <div class="institutional-metric-value">-1.23%</div>
                    <div class="institutional-metric-label">Energy</div>
                    <div class="institutional-status institutional-status-warning">WEAK</div>
                </div>
                <div class="institutional-metric">
                    <div class="institutional-metric-value">+0.45%</div>
                    <div class="institutional-metric-label">Financial</div>
                    <div class="institutional-status institutional-status-info">NEUTRAL</div>
                </div>
            </div>
        `;
    }

    generateVolatilityContent() {
        return `
            <div class="institutional-metrics">
                <div class="institutional-metric">
                    <div class="institutional-metric-value">16.42</div>
                    <div class="institutional-metric-label">Current VIX</div>
                    <div class="institutional-metric-change positive">+2.15%</div>
                </div>
                <div class="institutional-metric">
                    <div class="institutional-metric-value">14.23</div>
                    <div class="institutional-metric-label">30-Day Average</div>
                    <div class="institutional-metric-change negative">-0.87%</div>
                </div>
            </div>
            <p style="color: var(--institutional-text-muted); margin-top: 1rem;">
                Market volatility is elevated but within normal ranges. Institutional activity suggests cautious optimism.
            </p>
        `;
    }

    generateTrendingAssetsContent() {
        return `
            <div style="display: grid; gap: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: rgba(16, 185, 129, 0.1); border-radius: 8px; border-left: 4px solid #10b981;">
                    <div>
                        <div style="font-weight: 600; color: #10b981;">NVDA</div>
                        <div style="font-size: 0.875rem; color: var(--institutional-text-muted);">+4.21% today</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: 600; color: var(--institutional-text);">$892.45</div>
                        <div style="font-size: 0.875rem; color: #10b981;">+$36.02</div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: rgba(59, 130, 246, 0.1); border-radius: 8px; border-left: 4px solid #3b82f6;">
                    <div>
                        <div style="font-weight: 600; color: #3b82f6;">TSLA</div>
                        <div style="font-size: 0.875rem; color: var(--institutional-text-muted);">+2.87% today</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: 600; color: var(--institutional-text);">$248.77</div>
                        <div style="font-size: 0.875rem; color: #3b82f6;">+$6.94</div>
                    </div>
                </div>
            </div>
        `;
    }

    generateNewsImpactContent() {
        return `
            <div style="display: grid; gap: 1rem;">
                <div style="padding: 1rem; background: rgba(59, 130, 246, 0.1); border-radius: 8px;">
                    <div style="font-weight: 600; color: var(--institutional-text); margin-bottom: 0.5rem;">Federal Reserve Minutes Released</div>
                    <div style="font-size: 0.875rem; color: var(--institutional-text-muted); margin-bottom: 0.5rem;">Market impact: Moderate positive</div>
                    <div style="font-size: 0.875rem; color: var(--institutional-text-muted);">Key sectors affected: Financial (+1.2%), Technology (+0.8%)</div>
                </div>
                <div style="padding: 1rem; background: rgba(245, 158, 11, 0.1); border-radius: 8px;">
                    <div style="font-weight: 600; color: var(--institutional-text); margin-bottom: 0.5rem;">Earnings Season Preview</div>
                    <div style="font-size: 0.875rem; color: var(--institutional-text-muted); margin-bottom: 0.5rem;">Market impact: High volatility expected</div>
                    <div style="font-size: 0.875rem; color: var(--institutional-text-muted);">Companies to watch: AAPL, MSFT, GOOGL</div>
                </div>
            </div>
        `;
    }

    generatePerformanceContent() {
        return `
            <div class="institutional-metrics">
                <div class="institutional-metric">
                    <div class="institutional-metric-value">+12.34%</div>
                    <div class="institutional-metric-label">YTD Return</div>
                    <div class="institutional-status institutional-status-live">OUTPERFORMING</div>
                </div>
                <div class="institutional-metric">
                    <div class="institutional-metric-value">1.67</div>
                    <div class="institutional-metric-label">Sharpe Ratio</div>
                    <div class="institutional-status institutional-status-info">EXCELLENT</div>
                </div>
            </div>
        `;
    }

    generateRiskAssessmentContent() {
        return `
            <div class="institutional-metrics">
                <div class="institutional-metric">
                    <div class="institutional-metric-value">15.2%</div>
                    <div class="institutional-metric-label">Portfolio Volatility</div>
                    <div class="institutional-status institutional-status-info">MODERATE</div>
                </div>
                <div class="institutional-metric">
                    <div class="institutional-metric-value">-8.4%</div>
                    <div class="institutional-metric-label">Max Drawdown</div>
                    <div class="institutional-status institutional-status-warning">ACCEPTABLE</div>
                </div>
            </div>
        `;
    }

    generateRebalancingContent() {
        return `
            <div style="color: var(--institutional-text-muted);">
                <h4 style="color: var(--institutional-text); margin-bottom: 1rem;">Rebalancing Recommendations</h4>
                <ul style="line-height: 1.6;">
                    <li>Reduce Technology allocation by 2% (currently 35%)</li>
                    <li>Increase Healthcare exposure by 1.5% (currently 18%)</li>
                    <li>Add International diversification by 1% (currently 12%)</li>
                </ul>
            </div>
        `;
    }

    generateTaxOptimizationContent() {
        return `
            <div style="color: var(--institutional-text-muted);">
                <h4 style="color: var(--institutional-text); margin-bottom: 1rem;">Tax-Loss Harvesting Opportunities</h4>
                <ul style="line-height: 1.6;">
                    <li>Potential tax savings: $4,230</li>
                    <li>3 positions eligible for harvesting</li>
                    <li>Wash sale rule considerations identified</li>
                </ul>
            </div>
        `;
    }

    generateOrderManagementContent() {
        return `
            <div style="display: grid; gap: 1rem;">
                <div style="display: flex; justify-content: space-between; background: rgba(59, 130, 246, 0.1); padding: 1rem; border-radius: 8px;">
                    <span style="color: var(--institutional-text);">Active Orders</span>
                    <span style="color: #3b82f6; font-weight: 600;">3</span>
                </div>
                <div style="display: flex; justify-content: space-between; background: rgba(16, 185, 129, 0.1); padding: 1rem; border-radius: 8px;">
                    <span style="color: var(--institutional-text);">Filled Today</span>
                    <span style="color: #10b981; font-weight: 600;">7</span>
                </div>
            </div>
        `;
    }

    generateTechnicalAnalysisContent() {
        return `
            <div style="color: var(--institutional-text-muted);">
                <h4 style="color: var(--institutional-text); margin-bottom: 1rem;">Market Technical Overview</h4>
                <ul style="line-height: 1.6;">
                    <li>S&P 500: Above 50-day MA, bullish momentum</li>
                    <li>RSI: 62 (neutral zone)</li>
                    <li>MACD: Positive crossover signal</li>
                    <li>Support: 4,520 | Resistance: 4,590</li>
                </ul>
            </div>
        `;
    }

    generateAISignalsContent() {
        return `
            <div style="display: grid; gap: 1rem;">
                <div style="padding: 1rem; background: rgba(16, 185, 129, 0.1); border-radius: 8px; border-left: 4px solid #10b981;">
                    <div style="font-weight: 600; color: #10b981;">STRONG BUY: NVDA</div>
                    <div style="font-size: 0.875rem; color: var(--institutional-text-muted);">AI Confidence: 87% | Target: $950</div>
                </div>
                <div style="padding: 1rem; background: rgba(245, 158, 11, 0.1); border-radius: 8px; border-left: 4px solid #f59e0b;">
                    <div style="font-weight: 600; color: #f59e0b;">HOLD: AAPL</div>
                    <div style="font-size: 0.875rem; color: var(--institutional-text-muted);">AI Confidence: 64% | Range: $210-$220</div>
                </div>
            </div>
        `;
    }

    generateMarketScannerContent() {
        return `
            <div style="color: var(--institutional-text-muted);">
                <h4 style="color: var(--institutional-text); margin-bottom: 1rem;">Live Opportunities</h4>
                <ul style="line-height: 1.6;">
                    <li>7 stocks breaking resistance levels</li>
                    <li>12 unusual volume alerts triggered</li>
                    <li>3 momentum plays identified</li>
                    <li>5 oversold bounce candidates</li>
                </ul>
            </div>
        `;
    }
}

// Initialize the dropdown system when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait for other systems to load first
    setTimeout(() => {
        window.institutionalDropdownSystem = new InstitutionalDropdownSystem();
    }, 1000);
});