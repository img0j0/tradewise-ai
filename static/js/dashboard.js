// Trading Analytics Platform JavaScript

// Global variables
let currentTheme = 'dark';
let currentSection = 'dashboard';
let stocksData = [];
let alertsData = [];
let portfolioData = [];
let dashboardData = {};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a page that requires dashboard functionality
    // Skip initialization if we're on login or register pages
    const currentPath = window.location.pathname;
    if (currentPath === '/login' || currentPath === '/register') {
        console.log('Skipping dashboard initialization on auth page');
        return;
    }
    
    initializeDashboard();
    setInterval(refreshData, 30000); // Refresh every 30 seconds
});

// Initialize dashboard
function initializeDashboard() {
    console.log('Initializing Trading Analytics Dashboard...');
    
    try {
        // Initialize notification manager
        window.notificationManager = new NotificationManager();
        
        // Show loading state (disabled to prevent content replacement)
        // showMainLoadingState();
        
        // Load theme preference
        const savedTheme = localStorage.getItem('theme') || 'dark';
        setTheme(savedTheme);
        
        // Show dashboard section by default
        showSection('dashboard');
        
        // Load initial data with error handling
        Promise.all([
            loadDashboardData(),
            loadSectors()
        ]).catch(error => {
            console.error('Error loading initial data:', error);
            if (window.notificationManager) {
                notificationManager.showError('Failed to load dashboard data. Please refresh the page.');
            }
        });
        
        // Set up event listeners
        setupEventListeners();
        
        // Hide loading state after initial load
        // setTimeout(() => {
        //     hideMainLoadingState();
        // }, 1000);
        
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        if (window.notificationManager) {
            notificationManager.showError('Dashboard initialization failed. Please refresh the page.');
        }
    }
}

// Set up event listeners
function setupEventListeners() {
    // Filter form (check if elements exist first)
    const sectorFilter = document.getElementById('sector-filter');
    const minPrice = document.getElementById('min-price');
    const maxPrice = document.getElementById('max-price');
    
    if (sectorFilter) sectorFilter.addEventListener('change', applyFilters);
    if (minPrice) minPrice.addEventListener('input', applyFilters);
    if (maxPrice) maxPrice.addEventListener('input', applyFilters);
    
    // Auto-refresh toggle
    document.addEventListener('keydown', function(event) {
        if (event.ctrlKey && event.key === 'r') {
            event.preventDefault();
            refreshData();
        }
    });
}

// Theme management
function toggleTheme() {
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

function setTheme(theme) {
    currentTheme = theme;
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');
    
    if (theme === 'light') {
        body.classList.add('light-theme');
        themeIcon.className = 'fas fa-sun';
    } else {
        body.classList.remove('light-theme');
        themeIcon.className = 'fas fa-moon';
    }
    
    localStorage.setItem('theme', theme);
}

// Section management
function showSection(sectionName) {
    // Hide all sections
    const sections = ['dashboard', 'stocks', 'alerts', 'portfolio', 'advanced'];
    sections.forEach(section => {
        const element = document.getElementById(section + '-section');
        if (element) {
            element.style.display = 'none';
        }
    });
    
    // Show selected section
    const selectedSection = document.getElementById(sectionName + '-section');
    if (selectedSection) {
        selectedSection.style.display = 'block';
    }
    
    // Update active nav link
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    const activeLink = document.querySelector(`.navbar-nav .nav-link[href="#${sectionName}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
    
    currentSection = sectionName;
    
    // Load section-specific data
    switch (sectionName) {
        case 'stocks':
            loadStocks();
            break;
        case 'alerts':
            loadAlerts();
            break;
        case 'portfolio':
            loadPortfolio();
            break;
        case 'advanced':
            loadAdvancedFeatures();
            break;
        default:
            loadDashboardData();
    }
}

// Data loading functions
async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard', {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        dashboardData = data;
        
        // Safely update dashboard with proper error handling
        try {
            updateDashboard(data);
        } catch (updateError) {
            console.error('Error updating dashboard UI:', updateError);
            showError('Failed to update dashboard display: ' + updateError.message);
        }
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Failed to load dashboard data: ' + error.message);
    }
}

async function loadStocks() {
    try {
        const sector = document.getElementById('sector-filter').value;
        const minPrice = document.getElementById('min-price').value;
        const maxPrice = document.getElementById('max-price').value;
        
        const params = new URLSearchParams();
        if (sector) params.append('sector', sector);
        if (minPrice) params.append('min_price', minPrice);
        if (maxPrice) params.append('max_price', maxPrice);
        
        const response = await fetch('/api/stocks?' + params.toString());
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        stocksData = data.stocks;
        updateStocksList(data.stocks);
        
    } catch (error) {
        console.error('Error loading stocks:', error);
        showError('Failed to load stocks: ' + error.message);
    }
}

async function loadAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        alertsData = data.alerts;
        updateAlertsList(data.alerts);
        
    } catch (error) {
        console.error('Error loading alerts:', error);
        showError('Failed to load alerts: ' + error.message);
    }
}

async function loadPortfolio() {
    try {
        const response = await fetch('/api/portfolio');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        portfolioData = data;
        updatePortfolio(data);
        
    } catch (error) {
        console.error('Error loading portfolio:', error);
        showError('Failed to load portfolio: ' + error.message);
    }
}

async function loadSectors() {
    try {
        const response = await fetch('/api/sectors');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        const sectorFilter = document.getElementById('sector-filter');
        sectorFilter.innerHTML = '<option value="">All Sectors</option>';
        
        data.sectors.forEach(sector => {
            const option = document.createElement('option');
            option.value = sector;
            option.textContent = sector;
            sectorFilter.appendChild(option);
        });
        
    } catch (error) {
        console.error('Error loading sectors:', error);
    }
}

// Update UI functions
function updateDashboard(data) {
    // Only update dashboard elements if we're on the dashboard tab
    if (currentSection !== 'dashboard') return;
    
    console.log('Updating dashboard with data:', data);
    
    // Update each section with individual error handling
    try {
        if (data.market_overview) {
            updateMarketOverview(data.market_overview);
            updateWelcomeBanner(data.market_overview);
        }
    } catch (error) {
        console.error('Error updating market overview:', error);
    }
    
    try {
        if (data.user_account) {
            updateAccountBalance(data.user_account);
        }
    } catch (error) {
        console.error('Error updating account balance:', error);
    }
    
    try {
        if (data.portfolio_performance) {
            updatePerformanceSummary(data.portfolio_performance);
        }
    } catch (error) {
        console.error('Error updating performance summary:', error);
    }
    
    try {
        if (data.top_movers) {
            updateTopMovers(data.top_movers);
        }
    } catch (error) {
        console.error('Error updating top movers:', error);
    }
    
    try {
        if (data.recent_trades) {
            updateRecentTrades(data.recent_trades);
        }
    } catch (error) {
        console.error('Error updating recent trades:', error);
    }
    
    try {
        if (data.active_alerts) {
            updateActiveAlerts(data.active_alerts);
        }
    } catch (error) {
        console.error('Error updating active alerts:', error);
    }
    
    try {
        if (data.timestamp) {
            updateTimestamp(data.timestamp);
        }
    } catch (error) {
        console.error('Error updating timestamp:', error);
    }
}

function updateMarketOverview(overview) {
    try {
        if (document.getElementById('total-stocks')) {
            document.getElementById('total-stocks').textContent = overview.total_stocks;
        }
        if (document.getElementById('gainers')) {
            document.getElementById('gainers').textContent = overview.gainers;
        }
        if (document.getElementById('losers')) {
            document.getElementById('losers').textContent = overview.losers;
        }
        if (document.getElementById('unchanged')) {
            document.getElementById('unchanged').textContent = overview.unchanged;
        }
        
        const avgChange = overview.avg_change;
        const avgChangeElement = document.getElementById('avg-change');
        if (avgChangeElement) {
            avgChangeElement.textContent = formatCurrency(avgChange);
            avgChangeElement.className = `stat-number ${avgChange >= 0 ? 'text-success' : 'text-danger'}`;
        }
        
        if (document.getElementById('total-volume')) {
            document.getElementById('total-volume').textContent = formatVolume(overview.total_volume);
        }
    } catch (error) {
        console.error('Error in updateMarketOverview:', error);
        throw error;
    }
}

function updateWelcomeBanner(overview) {
    // Update market trend
    const marketTrendElement = document.getElementById('market-trend');
    if (marketTrendElement) {
        let trend = 'Neutral';
        let trendClass = 'text-warning';
        
        if (overview.gainers > overview.losers * 1.2) {
            trend = 'Bullish';
            trendClass = 'text-success';
        } else if (overview.losers > overview.gainers * 1.2) {
            trend = 'Bearish';
            trendClass = 'text-danger';
        }
        
        marketTrendElement.textContent = trend;
        marketTrendElement.className = trendClass;
    }
    
    // AI accuracy stays at 98% (simulated for now)
    const aiAccuracyElement = document.getElementById('ai-accuracy');
    if (aiAccuracyElement) {
        aiAccuracyElement.textContent = '98%';
    }
}

function updatePerformanceSummary(performance) {
    try {
        const totalTradesElement = document.getElementById('total-trades');
        if (totalTradesElement) {
            totalTradesElement.textContent = performance.total_trades;
        }
        
        const winRateElement = document.getElementById('win-rate');
        if (winRateElement) {
            const winRate = performance.win_rate || 0;
            winRateElement.textContent = winRate.toFixed(1) + '%';
        }
        
        // Total P&L
        const pnl = performance.total_pnl || 0;
        const pnlElement = document.getElementById('total-pnl');
        if (pnlElement) {
            pnlElement.textContent = formatCurrency(pnl);
            pnlElement.className = pnl >= 0 ? 'text-success' : 'text-danger';
        }
        
        // Realized P&L
        const realizedPnl = performance.total_realized_pnl || 0;
        const realizedElement = document.getElementById('realized-pnl');
        if (realizedElement) {
            realizedElement.textContent = formatCurrency(realizedPnl);
            realizedElement.className = realizedPnl >= 0 ? 'text-success' : 'text-danger';
        }
        
        // Unrealized P&L
        const unrealizedPnl = performance.total_unrealized_pnl || 0;
        const unrealizedElement = document.getElementById('unrealized-pnl');
        if (unrealizedElement) {
            unrealizedElement.textContent = formatCurrency(unrealizedPnl);
            unrealizedElement.className = unrealizedPnl >= 0 ? 'text-success' : 'text-danger';
        }
        
        const avgConfidenceElement = document.getElementById('avg-confidence');
        if (avgConfidenceElement) {
            const avgConfidence = performance.avg_confidence || 0;
            avgConfidenceElement.textContent = avgConfidence.toFixed(1) + '%';
        }
    } catch (error) {
        console.error('Error in updatePerformanceSummary:', error);
        throw error;
    }
}

function updateAccountBalance(userAccount) {
    const balanceElement = document.getElementById('account-balance');
    if (balanceElement && userAccount) {
        balanceElement.textContent = formatCurrency(userAccount.balance);
    }
}

function updateTopMovers(topMovers) {
    updateTopGainers(topMovers.top_gainers);
    updateTopLosers(topMovers.top_losers);
}

function updateTopGainers(gainers) {
    const container = document.getElementById('top-gainers');
    
    if (!container) return;
    
    if (!gainers || gainers.length === 0) {
        container.innerHTML = '<div class="text-center text-muted">No gainers found</div>';
        return;
    }
    
    container.innerHTML = gainers.map(stock => `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <div>
                <span class="fw-bold text-primary">${stock.symbol}</span>
                <small class="text-muted ms-2">${formatCurrency(stock.current_price)}</small>
            </div>
            <span class="badge bg-success">+${stock.change_pct.toFixed(2)}%</span>
        </div>
    `).join('');
}

function updateTopLosers(losers) {
    const container = document.getElementById('top-losers');
    
    if (!container) return;
    
    if (!losers || losers.length === 0) {
        container.innerHTML = '<div class="text-center text-muted">No losers found</div>';
        return;
    }
    
    container.innerHTML = losers.map(stock => `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <div>
                <span class="fw-bold text-primary">${stock.symbol}</span>
                <small class="text-muted ms-2">${formatCurrency(stock.current_price)}</small>
            </div>
            <span class="badge bg-danger">${stock.change_pct.toFixed(2)}%</span>
        </div>
    `).join('');
}

function updateRecentTrades(trades) {
    const container = document.getElementById('recent-trades');
    
    if (!container) return;
    
    if (!trades || trades.length === 0) {
        container.innerHTML = '<div class="text-center text-muted">No recent trades</div>';
        return;
    }
    
    container.innerHTML = trades.map(trade => `
        <div class="trade-item">
            <div class="trade-info">
                <div class="trade-symbol">${trade.symbol}</div>
                <div class="trade-details">
                    ${trade.quantity} shares at ${formatCurrency(trade.price)}
                    <small class="text-muted">• ${formatDateTime(trade.timestamp)}</small>
                </div>
            </div>
            <div class="trade-action ${trade.action}">${trade.action.toUpperCase()}</div>
        </div>
    `).join('');
}

function updateActiveAlerts(alerts) {
    // Only update if we're on the dashboard tab
    if (currentSection !== 'dashboard') return;
    
    const container = document.getElementById('active-alerts');
    
    if (!container) return;
    
    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<div class="text-center text-muted">No active alerts</div>';
        return;
    }
    
    container.innerHTML = alerts.map(alert => `
        <div class="alert-item alert-${alert.alert_type}">
            <div class="alert-content">
                <div class="alert-symbol">${alert.symbol}</div>
                <div class="alert-message">${alert.message}</div>
                <small class="text-muted">${formatDateTime(alert.created_at)}</small>
            </div>
            <div class="alert-actions">
                <span class="confidence-badge confidence-${getConfidenceClass(alert.confidence_score)}">
                    ${alert.confidence_score.toFixed(0)}%
                </span>
                <button class="btn btn-sm btn-outline-primary" onclick="showTradeModal('${alert.symbol}')">
                    <i class="fas fa-exchange-alt"></i>
                </button>
            </div>
        </div>
    `).join('');
}

function updateStocksList(stocks) {
    const container = document.getElementById('stocks-list');
    
    if (!stocks || stocks.length === 0) {
        container.innerHTML = '<div class="text-center text-muted">No stocks found</div>';
        return;
    }
    
    container.innerHTML = stocks.map(stock => {
        const change = stock.current_price - stock.previous_close;
        const changePct = (change / stock.previous_close) * 100;
        const insights = stock.ai_insights || {};
        
        return `
            <div class="stock-item">
                <div class="stock-header">
                    <div>
                        <div class="stock-symbol">${stock.symbol}</div>
                        <div class="stock-name">${stock.name}</div>
                        <div class="text-muted small">${stock.sector}</div>
                    </div>
                    <div class="text-end">
                        <div class="stock-price">${formatCurrency(stock.current_price)}</div>
                        <div class="stock-change ${change >= 0 ? 'positive' : 'negative'}">
                            ${change >= 0 ? '+' : ''}${formatCurrency(change)} (${changePct.toFixed(2)}%)
                        </div>
                    </div>
                </div>
                
                <div class="stock-details">
                    <div class="stock-info">
                        <span>Volume: ${formatVolume(stock.volume)}</span>
                        <span>High: ${formatCurrency(stock.high)}</span>
                        <span>Low: ${formatCurrency(stock.low)}</span>
                        <span>Market Cap: ${formatMarketCap(stock.market_cap)}</span>
                    </div>
                    <div>
                        <button class="btn btn-sm btn-primary" onclick="showTradeModal('${stock.symbol}')">
                            <i class="fas fa-exchange-alt me-1"></i>Trade
                        </button>
                    </div>
                </div>
                
                ${insights.confidence_score ? `
                    <div class="ai-insights">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <div>
                                <span class="confidence-badge confidence-${getConfidenceClass(insights.confidence_score)}">
                                    ${insights.confidence_score.toFixed(0)}% Confidence
                                </span>
                                <span class="recommendation-badge recommendation-${insights.recommendation ? insights.recommendation.toLowerCase().replace(' ', '-') : 'hold'}">
                                    ${insights.recommendation || 'HOLD'}
                                </span>
                            </div>
                            <span class="text-muted small">Risk: ${insights.risk_level || 'MEDIUM'}</span>
                        </div>
                        <div class="small text-muted">
                            ${insights.analysis || 'No analysis available'}
                        </div>
                        ${insights.key_factors && insights.key_factors.length > 0 ? `
                            <div class="mt-2">
                                <small class="text-info">Key Factors:</small>
                                <ul class="small text-muted mt-1 mb-0">
                                    ${insights.key_factors.map(factor => `<li>${factor}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

function updateAlertsList(alerts) {
    const container = document.getElementById('alerts-list');
    const countBadge = document.getElementById('active-alerts-count');
    
    // Update active alerts count
    if (countBadge) {
        countBadge.textContent = alerts ? alerts.length : 0;
    }
    
    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<div class="text-center text-muted">No alerts found. Create your first personalized alert above!</div>';
        return;
    }
    
    container.innerHTML = alerts.map(alert => `
        <div class="alert-item alert-${alert.alert_type}">
            <div class="alert-content">
                <div class="alert-symbol">${alert.symbol}</div>
                <div class="alert-message">${alert.message}</div>
                <small class="text-muted">${formatDateTime(alert.created_at)}</small>
            </div>
            <div class="alert-actions">
                <span class="confidence-badge confidence-${getConfidenceClass(alert.confidence_score)}">
                    ${alert.confidence_score.toFixed(0)}%
                </span>
                <button class="btn btn-sm btn-outline-primary" onclick="showTradeModal('${alert.symbol}')">
                    <i class="fas fa-exchange-alt me-1"></i>Trade
                </button>
                <button class="btn btn-sm btn-outline-secondary" onclick="dismissAlert(${alert.id})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `).join('');
}

function updatePortfolio(data) {
    // Update portfolio summary
    updatePortfolioSummary(data.summary);
    
    // Update portfolio holdings
    updatePortfolioHoldings(data.portfolio_items);
}

function updatePortfolioSummary(summary) {
    document.getElementById('portfolio-value').textContent = formatCurrency(summary.total_value);
    document.getElementById('portfolio-cost').textContent = formatCurrency(summary.total_cost);
    
    const pnl = summary.total_pnl;
    const pnlElement = document.getElementById('portfolio-pnl');
    pnlElement.textContent = formatCurrency(pnl);
    pnlElement.className = `stat-number ${pnl >= 0 ? 'text-success' : 'text-danger'}`;
    
    const pnlPct = summary.total_pnl_pct;
    const pnlPctElement = document.getElementById('portfolio-pnl-pct');
    pnlPctElement.textContent = pnlPct.toFixed(2) + '%';
    pnlPctElement.className = `stat-number ${pnlPct >= 0 ? 'text-success' : 'text-danger'}`;
}

function updatePortfolioHoldings(holdings) {
    const container = document.getElementById('portfolio-holdings');
    
    if (!holdings || holdings.length === 0) {
        container.innerHTML = '<div class="text-center text-muted">No holdings found</div>';
        return;
    }
    
    container.innerHTML = holdings.map(holding => {
        const pnlClass = holding.pnl >= 0 ? 'text-success' : 'text-danger';
        const pnlIcon = holding.pnl >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
        
        return `
            <div class="portfolio-item">
                <div class="portfolio-header">
                    <div>
                        <div class="stock-symbol">${holding.symbol}</div>
                        <div class="small text-muted mt-1">
                            <i class="fas fa-coins me-1"></i>${holding.quantity} shares @ ${formatCurrency(holding.avg_price)}
                        </div>
                    </div>
                    <div class="text-end">
                        <div class="stock-price">${formatCurrency(holding.current_price)}</div>
                        <div class="${pnlClass} fw-bold">
                            <i class="fas ${pnlIcon} me-1"></i>
                            ${formatCurrency(holding.pnl)} (${holding.pnl_pct.toFixed(2)}%)
                        </div>
                    </div>
                </div>
                <div class="portfolio-details">
                    <div class="portfolio-metric">
                        <div class="portfolio-metric-value">${holding.quantity}</div>
                        <div class="portfolio-metric-label">Shares Owned</div>
                    </div>
                    <div class="portfolio-metric">
                        <div class="portfolio-metric-value">${formatCurrency(holding.avg_price)}</div>
                        <div class="portfolio-metric-label">Purchase Price</div>
                    </div>
                    <div class="portfolio-metric">
                        <div class="portfolio-metric-value ${pnlClass}">${formatCurrency(holding.current_value)}</div>
                        <div class="portfolio-metric-label">Market Value</div>
                    </div>
                    <div class="portfolio-metric">
                        <div class="portfolio-metric-value">${formatCurrency(holding.cost_basis)}</div>
                        <div class="portfolio-metric-label">Total Invested</div>
                    </div>
                </div>
                <div class="mt-3 d-flex justify-content-between align-items-center">
                    <button class="btn btn-sm btn-outline-success" onclick="showBuyModal('${holding.symbol}')">
                        <i class="fas fa-plus me-1"></i>Buy More
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="showSellModal('${holding.symbol}')">
                        <i class="fas fa-minus me-1"></i>Sell
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function updateTimestamp(timestamp) {
    const element = document.getElementById('last-updated');
    if (element) {
        element.textContent = `Last updated: ${formatDateTime(timestamp)}`;
    }
}

// Trading functions
function showTradeModal(symbol) {
    const stock = stocksData.find(s => s.symbol === symbol);
    if (!stock) {
        showError('Stock not found');
        return;
    }
    
    document.getElementById('trade-symbol').value = symbol;
    document.getElementById('trade-current-price').textContent = formatCurrency(stock.current_price);
    
    const insights = stock.ai_insights || {};
    document.getElementById('trade-confidence').textContent = insights.confidence_score ? 
        `${insights.confidence_score.toFixed(0)}% (${insights.recommendation || 'HOLD'})` : 'N/A';
    
    const modal = new bootstrap.Modal(document.getElementById('tradeModal'));
    modal.show();
}

async function executeTrade() {
    try {
        const symbol = document.getElementById('trade-symbol').value;
        const action = document.getElementById('trade-action').value;
        const quantity = parseInt(document.getElementById('trade-quantity').value);
        
        if (!symbol || !action || !quantity || quantity <= 0) {
            showError('Please fill in all required fields');
            return;
        }
        
        const response = await fetch('/api/trade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                symbol: symbol,
                action: action,
                quantity: quantity
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('tradeModal'));
        modal.hide();
        
        // Clear form
        document.getElementById('trade-form').reset();
        
        // Show success message
        showSuccess(data.message);
        
        // Track trade execution
        if (window.analyticsManager) {
            analyticsManager.trackEvent('trade_executed', {
                symbol: symbol,
                action: action,
                quantity: quantity,
                price: price
            });
        }
        
        // Refresh data
        refreshData();
        
    } catch (error) {
        console.error('Error executing trade:', error);
        showError('Failed to execute trade: ' + error.message);
    }
}

// Filter functions
function applyFilters() {
    if (currentSection === 'stocks') {
        loadStocks();
    }
}

// Utility functions
function refreshData() {
    console.log('Refreshing data...');
    showRefreshIndicator();
    
    let loadPromise;
    switch (currentSection) {
        case 'stocks':
            loadPromise = loadStocks();
            break;
        case 'alerts':
            loadPromise = loadAlerts();
            break;
        case 'portfolio':
            loadPromise = loadPortfolio();
            break;
        default:
            loadPromise = loadDashboardData();
    }
    
    if (loadPromise && loadPromise.then) {
        loadPromise.then(() => {
            hideRefreshIndicator();
            showSuccess('Data refreshed successfully!');
        }).catch(error => {
            hideRefreshIndicator();
            showError('Failed to refresh data: ' + error.message);
        });
    } else {
        setTimeout(() => {
            hideRefreshIndicator();
        }, 1000);
    }
}

// Loading state functions
function showMainLoadingState() {
    const loadingHTML = `
        <div id="main-loading" class="text-center p-5">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <h5 class="text-primary">Loading Trading Dashboard...</h5>
            <p class="text-muted">Fetching real-time market data and your portfolio</p>
        </div>
    `;
    
    const dashboardSection = document.getElementById('dashboard-section');
    if (dashboardSection) {
        dashboardSection.innerHTML = loadingHTML;
    }
}

function hideMainLoadingState() {
    const mainLoading = document.getElementById('main-loading');
    if (mainLoading) {
        mainLoading.remove();
    }
}

function showRefreshIndicator() {
    // Add refresh indicator to the page
    let refreshIndicator = document.getElementById('refresh-indicator');
    if (!refreshIndicator) {
        refreshIndicator = document.createElement('div');
        refreshIndicator.id = 'refresh-indicator';
        refreshIndicator.className = 'refresh-indicator';
        refreshIndicator.innerHTML = `
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            <span>Refreshing data...</span>
        `;
        document.body.appendChild(refreshIndicator);
    }
    refreshIndicator.style.display = 'flex';
}

function hideRefreshIndicator() {
    const refreshIndicator = document.getElementById('refresh-indicator');
    if (refreshIndicator) {
        refreshIndicator.style.display = 'none';
    }
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

function formatVolume(volume) {
    if (volume >= 1000000) {
        return (volume / 1000000).toFixed(1) + 'M';
    } else if (volume >= 1000) {
        return (volume / 1000).toFixed(1) + 'K';
    }
    return volume.toLocaleString();
}

function formatMarketCap(marketCap) {
    if (marketCap >= 1000000000000) {
        return (marketCap / 1000000000000).toFixed(1) + 'T';
    } else if (marketCap >= 1000000000) {
        return (marketCap / 1000000000).toFixed(1) + 'B';
    } else if (marketCap >= 1000000) {
        return (marketCap / 1000000).toFixed(1) + 'M';
    }
    return marketCap.toLocaleString();
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getConfidenceClass(score) {
    if (score >= 70) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
}

function showError(message) {
    console.error(message);
    if (window.notificationManager) {
        notificationManager.showError(message);
    } else {
        // Fallback to toast notification
        const toast = createToast('Error', message, 'danger');
        showToast(toast);
    }
}

function showSuccess(message) {
    console.log(message);
    if (window.notificationManager) {
        notificationManager.showSuccess(message);
    } else {
        // Fallback to toast notification
        const toast = createToast('Success', message, 'success');
        showToast(toast);
    }
}

function createToast(title, message, type) {
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}:</strong> ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    return toast;
}

function showToast(toast) {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

async function dismissAlert(alertId) {
    try {
        // In a real implementation, this would make an API call to dismiss the alert
        console.log('Dismissing alert:', alertId);
        
        // For now, just refresh the alerts
        loadAlerts();
        
    } catch (error) {
        console.error('Error dismissing alert:', error);
        showError('Failed to dismiss alert');
    }
}

// Payment and Trading Functions

function showDepositModal() {
    const modal = new bootstrap.Modal(document.getElementById('depositModal'));
    modal.show();
}

async function processDeposit() {
    const amount = parseFloat(document.getElementById('deposit-amount').value);
    const depositBtn = document.getElementById('deposit-btn');
    
    if (!amount || amount <= 0) {
        showError('Please enter a valid deposit amount');
        return;
    }
    
    try {
        depositBtn.disabled = true;
        depositBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        
        const response = await fetch('/api/create-deposit-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ amount: amount })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Redirect to Stripe checkout
            window.location.href = data.checkout_url;
        } else {
            showError(data.error || 'Failed to create deposit session');
        }
    } catch (error) {
        console.error('Error processing deposit:', error);
        showError('Failed to process deposit');
    } finally {
        depositBtn.disabled = false;
        depositBtn.innerHTML = '<i class="fas fa-credit-card me-2"></i>Proceed to Payment';
    }
}

function showBuyModal() {
    const modal = new bootstrap.Modal(document.getElementById('buyModal'));
    
    // Clear previous search results
    currentSearchedStock = null;
    document.getElementById('stock-search-result').style.display = 'none';
    document.getElementById('ai-risk-analysis').style.display = 'none';
    document.getElementById('buy-symbol-search').value = '';
    document.getElementById('buy-quantity').value = '';
    updateBuyCalculations();
    
    // Set up event listener for quantity changes
    document.getElementById('buy-quantity').addEventListener('input', updateBuyCalculations);
    
    modal.show();
}

function updateBuyCalculations() {
    const quantityInput = document.getElementById('buy-quantity');
    const priceElement = document.getElementById('buy-current-price');
    const totalElement = document.getElementById('buy-total-cost');
    const balanceElement = document.getElementById('buy-available-balance');
    const summaryElement = document.getElementById('buy-purchase-summary');
    const sharesCountElement = document.getElementById('buy-shares-count');
    const totalAmountElement = document.getElementById('buy-total-amount');
    const insufficientFundsElement = document.getElementById('buy-insufficient-funds');
    const buyBtn = document.getElementById('buy-btn');
    
    let price = 0;
    
    // Check if we have a searched stock
    if (currentSearchedStock) {
        price = currentSearchedStock.current_price || 0;
    }
    
    const quantity = parseInt(quantityInput.value) || 0;
    const totalCost = price * quantity;
    
    priceElement.textContent = price > 0 ? formatCurrency(price) : '-';
    totalElement.textContent = formatCurrency(totalCost);
    
    // Update available balance from dashboard data
    let availableBalance = 0;
    if (dashboardData.user_account) {
        availableBalance = dashboardData.user_account.balance;
        balanceElement.textContent = formatCurrency(availableBalance);
    }
    
    // Show purchase summary if quantity is entered
    if (quantity > 0 && price > 0) {
        summaryElement.style.display = 'block';
        sharesCountElement.textContent = quantity;
        totalAmountElement.textContent = formatCurrency(totalCost);
        
        // Check if sufficient funds
        if (totalCost > availableBalance) {
            insufficientFundsElement.style.display = 'block';
            buyBtn.disabled = true;
        } else {
            insufficientFundsElement.style.display = 'none';
            buyBtn.disabled = false;
        }
    } else {
        summaryElement.style.display = 'none';
        insufficientFundsElement.style.display = 'none';
        buyBtn.disabled = quantity <= 0;
    }
}

async function executeBuy() {
    const quantity = parseInt(document.getElementById('buy-quantity').value);
    const buyBtn = document.getElementById('buy-btn');
    
    if (!currentSearchedStock || !quantity || quantity <= 0) {
        showError('Please search for a stock and enter a valid quantity');
        return;
    }
    
    const symbol = currentSearchedStock.symbol;
    
    try {
        buyBtn.disabled = true;
        buyBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        
        const response = await fetch('/api/purchase-stock', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ symbol: symbol, quantity: quantity })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess(data.message);
            bootstrap.Modal.getInstance(document.getElementById('buyModal')).hide();
            refreshData(); // Refresh dashboard data
        } else {
            showError(data.error || 'Failed to purchase stock');
        }
    } catch (error) {
        console.error('Error purchasing stock:', error);
        showError('Failed to purchase stock');
    } finally {
        buyBtn.disabled = false;
        buyBtn.innerHTML = '<i class="fas fa-shopping-cart me-2"></i>Buy Stock';
    }
}

function showSellModal(symbol = null) {
    const modal = new bootstrap.Modal(document.getElementById('sellModal'));
    
    // Populate portfolio options
    const stockSelect = document.getElementById('sell-symbol');
    stockSelect.innerHTML = '<option value="">Select a stock...</option>';
    
    // Get portfolio data from dashboard data
    const holdings = dashboardData.portfolio?.portfolio_items || [];
    
    holdings.forEach(holding => {
        const option = document.createElement('option');
        option.value = holding.symbol;
        option.textContent = `${holding.symbol} - ${holding.quantity} shares @ ${formatCurrency(holding.current_price)}`;
        option.dataset.quantity = holding.quantity;
        option.dataset.price = holding.current_price;
        stockSelect.appendChild(option);
    });
    
    // If symbol is provided, select it
    if (symbol) {
        stockSelect.value = symbol;
    }
    
    // Set up event listeners
    stockSelect.addEventListener('change', updateSellCalculations);
    document.getElementById('sell-quantity').addEventListener('input', updateSellCalculations);
    
    // Trigger calculation if symbol was pre-selected
    if (symbol) {
        updateSellCalculations();
    }
    
    modal.show();
}

function updateSellCalculations() {
    const stockSelect = document.getElementById('sell-symbol');
    const quantityInput = document.getElementById('sell-quantity');
    const priceElement = document.getElementById('sell-current-price');
    const totalElement = document.getElementById('sell-total-proceeds');
    const ownedElement = document.getElementById('sell-shares-owned');
    
    const selectedOption = stockSelect.options[stockSelect.selectedIndex];
    const symbol = stockSelect.value;
    const quantity = parseInt(quantityInput.value) || 0;
    
    if (symbol) {
        // Get price from the selected option's dataset
        const price = parseFloat(selectedOption.dataset.price) || 0;
        const owned = parseInt(selectedOption.dataset.quantity) || 0;
        
        priceElement.textContent = price > 0 ? formatCurrency(price) : '-';
        totalElement.textContent = formatCurrency(price * quantity);
        ownedElement.textContent = owned;
        
        // Update max attribute
        quantityInput.max = owned;
        
        // Validate quantity
        if (quantity > owned) {
            quantityInput.setCustomValidity('Quantity exceeds owned shares');
            document.getElementById('sell-btn').disabled = true;
        } else if (quantity <= 0) {
            quantityInput.setCustomValidity('');
            document.getElementById('sell-btn').disabled = true;
        } else {
            quantityInput.setCustomValidity('');
            document.getElementById('sell-btn').disabled = false;
        }
    } else {
        priceElement.textContent = '-';
        totalElement.textContent = '$0.00';
        ownedElement.textContent = '0';
        document.getElementById('sell-btn').disabled = true;
    }
}

async function executeSell() {
    const symbol = document.getElementById('sell-symbol').value;
    const quantity = parseInt(document.getElementById('sell-quantity').value);
    const sellBtn = document.getElementById('sell-btn');
    
    if (!symbol || !quantity || quantity <= 0) {
        showError('Please select a stock and enter a valid quantity');
        return;
    }
    
    try {
        sellBtn.disabled = true;
        sellBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        
        const response = await fetch('/api/sell-stock', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ symbol: symbol, quantity: quantity })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess(data.message);
            bootstrap.Modal.getInstance(document.getElementById('sellModal')).hide();
            refreshData(); // Refresh dashboard data
        } else {
            showError(data.error || 'Failed to sell stock');
        }
    } catch (error) {
        console.error('Error selling stock:', error);
        showError('Failed to sell stock');
    } finally {
        sellBtn.disabled = false;
        sellBtn.innerHTML = '<i class="fas fa-money-bill-wave me-2"></i>Sell Stock';
    }
}

async function showTransactionHistory() {
    const modal = new bootstrap.Modal(document.getElementById('transactionModal'));
    const historyContainer = document.getElementById('transaction-history');
    
    try {
        historyContainer.innerHTML = '<div class="text-center text-muted">Loading transactions...</div>';
        
        const response = await fetch('/api/transactions');
        const transactions = await response.json();
        
        if (response.ok) {
            if (transactions.length === 0) {
                historyContainer.innerHTML = '<div class="text-center text-muted">No transactions found</div>';
            } else {
                historyContainer.innerHTML = transactions.map(tx => `
                    <div class="transaction-item mb-3 p-3 border rounded">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <span class="fw-bold">${tx.transaction_type.replace('_', ' ').toUpperCase()}</span>
                                ${tx.symbol ? `<span class="text-muted ms-2">${tx.symbol}</span>` : ''}
                            </div>
                            <div class="text-end">
                                <div class="fw-bold ${tx.transaction_type === 'deposit' || tx.transaction_type === 'stock_sale' ? 'text-success' : 'text-danger'}">
                                    ${tx.transaction_type === 'deposit' || tx.transaction_type === 'stock_sale' ? '+' : '-'}${formatCurrency(tx.amount)}
                                </div>
                                <small class="text-muted">${formatDateTime(tx.created_at)}</small>
                            </div>
                        </div>
                        ${tx.quantity ? `<div class="text-muted small">Quantity: ${tx.quantity} shares @ ${formatCurrency(tx.price_per_share)}</div>` : ''}
                    </div>
                `).join('');
            }
        } else {
            historyContainer.innerHTML = '<div class="text-center text-danger">Failed to load transactions</div>';
        }
    } catch (error) {
        console.error('Error loading transactions:', error);
        historyContainer.innerHTML = '<div class="text-center text-danger">Failed to load transactions</div>';
    }
    
    modal.show();
}

// Global variable to store current searched stock data
let currentSearchedStock = null;

async function searchStock() {
    const symbolInput = document.getElementById('buy-symbol-search');
    const symbol = symbolInput.value.trim().toUpperCase();
    
    if (!symbol) {
        showError('Please enter a stock symbol');
        return;
    }
    
    try {
        // Show loading state
        const searchBtn = symbolInput.nextElementSibling;
        searchBtn.disabled = true;
        searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
        
        // Search for the stock
        const response = await fetch('/api/search-stock', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ symbol: symbol })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentSearchedStock = data;
            displayStockInfo(data);
            
            // Get AI risk analysis
            const riskResponse = await fetch('/api/ai-risk-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ symbol: symbol })
            });
            
            if (riskResponse.ok) {
                const riskData = await riskResponse.json();
                displayRiskAnalysis(riskData);
            }
            
            // Update calculations
            updateBuyCalculations();
            
        } else {
            showError(data.error || 'Stock not found');
            currentSearchedStock = null;
            document.getElementById('stock-search-result').style.display = 'none';
            document.getElementById('ai-risk-analysis').style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error searching stock:', error);
        showError('Failed to search stock');
    } finally {
        const searchBtn = symbolInput.nextElementSibling;
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<i class="fas fa-search"></i> Search';
    }
}

function displayStockInfo(stock) {
    document.getElementById('stock-info-name').textContent = `${stock.symbol} - ${stock.name}`;
    document.getElementById('stock-info-sector').textContent = stock.sector;
    document.getElementById('stock-info-marketcap').textContent = formatMarketCap(stock.market_cap);
    document.getElementById('stock-search-result').style.display = 'block';
}

function displayRiskAnalysis(riskData) {
    // Set risk level badge
    const riskBadge = document.getElementById('risk-level-badge');
    riskBadge.textContent = riskData.risk_level;
    riskBadge.className = 'badge bg-' + (
        riskData.risk_level === 'Low' ? 'success' :
        riskData.risk_level === 'Moderate' ? 'warning' :
        riskData.risk_level === 'High' ? 'danger' : 'danger'
    );
    
    // Display key risks
    const risksList = document.getElementById('key-risks-list');
    risksList.innerHTML = riskData.key_risks.map(risk => `<li>${risk}</li>`).join('');
    
    // Display potential rewards
    const rewardsList = document.getElementById('potential-rewards-list');
    rewardsList.innerHTML = riskData.potential_rewards.map(reward => `<li>${reward}</li>`).join('');
    
    // Set AI recommendation badge
    const recBadge = document.getElementById('ai-recommendation-badge');
    recBadge.textContent = `AI Recommendation: ${riskData.ai_recommendation.action} (${riskData.ai_recommendation.confidence}% confidence)`;
    recBadge.className = 'badge bg-' + (
        riskData.ai_recommendation.action === 'BUY' ? 'success' :
        riskData.ai_recommendation.action === 'CONSIDER' ? 'info' :
        riskData.ai_recommendation.action === 'HOLD' ? 'warning' : 'danger'
    );
    
    document.getElementById('ai-risk-analysis').style.display = 'block';
}

// Advanced Features Functions
async function loadAdvancedFeatures() {
    try {
        // Load all advanced features data in parallel
        const [portfolioOptimization, topTraders, achievements, leaderboard, challenges] = await Promise.all([
            loadPortfolioOptimization(),
            loadTopTraders(),
            loadAchievements(),
            loadLeaderboard(),
            loadChallenges()
        ]);
        
        updateAdvancedFeaturesUI({
            portfolioOptimization,
            topTraders,
            achievements,
            leaderboard,
            challenges
        });
        
        // Load AI performance data
        loadAIPerformance();
        loadPersonalizedAI();
        loadUserStrategies();
    } catch (error) {
        console.error('Error loading advanced features:', error);
        showError('Failed to load advanced features');
    }
}

async function loadPortfolioOptimization() {
    try {
        const response = await fetch('/api/portfolio/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ risk_tolerance: 'moderate' })
        });
        return await response.json();
    } catch (error) {
        console.error('Error loading portfolio optimization:', error);
        return null;
    }
}

async function loadTopTraders() {
    try {
        const response = await fetch('/api/social/top-traders?limit=5');
        return await response.json();
    } catch (error) {
        console.error('Error loading top traders:', error);
        return null;
    }
}

async function loadAchievements() {
    try {
        const response = await fetch('/api/gamification/achievements');
        return await response.json();
    } catch (error) {
        console.error('Error loading achievements:', error);
        return null;
    }
}

async function loadLeaderboard() {
    try {
        const response = await fetch('/api/gamification/leaderboard?limit=5');
        return await response.json();
    } catch (error) {
        console.error('Error loading leaderboard:', error);
        return null;
    }
}

async function loadChallenges() {
    try {
        const response = await fetch('/api/gamification/challenges');
        return await response.json();
    } catch (error) {
        console.error('Error loading challenges:', error);
        return null;
    }
}

function updateAdvancedFeaturesUI(data) {
    // Update Portfolio Optimization
    if (data.portfolioOptimization && data.portfolioOptimization.weights) {
        updatePortfolioOptimizationUI(data.portfolioOptimization);
    }
    
    // Update Social Trading
    if (data.topTraders && data.topTraders.top_traders) {
        updateTopTradersUI(data.topTraders);
    }
    
    // Update Achievements
    if (data.achievements) {
        updateAchievementsDisplay(data.achievements);
    }
    
    // Update Leaderboard
    if (data.leaderboard) {
        updateLeaderboardDisplay(data.leaderboard);
    }
    
    // Update Challenges
    if (data.challenges) {
        updateChallengesDisplay(data.challenges);
    }
}

function updatePortfolioOptimizationUI(optimization) {
    const container = document.getElementById('portfolio-optimization');
    if (!container) return;
    
    if (optimization.error) {
        container.innerHTML = `<div class="alert alert-warning">${optimization.error}</div>`;
        return;
    }
    
    let html = `
        <div class="optimization-results">
            <h6>Recommended Allocation</h6>
            <div class="allocation-chart mb-3">
    `;
    
    // Display weights
    for (const [symbol, weight] of Object.entries(optimization.weights)) {
        const percentage = (weight * 100).toFixed(1);
        html += `
            <div class="allocation-row mb-2">
                <div class="d-flex justify-content-between align-items-center">
                    <span class="symbol">${symbol}</span>
                    <span class="percentage">${percentage}%</span>
                </div>
                <div class="progress" style="height: 20px;">
                    <div class="progress-bar bg-success" style="width: ${percentage}%"></div>
                </div>
            </div>
        `;
    }
    
    // Display metrics
    if (optimization.metrics) {
        html += `
            <div class="metrics mt-3">
                <div class="row">
                    <div class="col-md-4">
                        <div class="metric-card">
                            <div class="metric-value">${(optimization.metrics.return * 100).toFixed(1)}%</div>
                            <div class="metric-label">Expected Return</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="metric-card">
                            <div class="metric-value">${(optimization.metrics.volatility * 100).toFixed(1)}%</div>
                            <div class="metric-label">Volatility</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="metric-card">
                            <div class="metric-value">${optimization.metrics.sharpe_ratio.toFixed(2)}</div>
                            <div class="metric-label">Sharpe Ratio</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Display recommendations
    if (optimization.recommendations && optimization.recommendations.length > 0) {
        html += `
            <div class="recommendations mt-3">
                <h6>AI Recommendations</h6>
                <ul class="list-unstyled">
        `;
        optimization.recommendations.forEach(rec => {
            html += `<li><i class="fas fa-check-circle text-success me-2"></i>${rec}</li>`;
        });
        html += `</ul></div>`;
    }
    
    html += `</div>`;
    container.innerHTML = html;
}

function updateTopTradersUI(data) {
    const container = document.getElementById('top-traders');
    if (!container) return;
    
    let html = '<div class="traders-list">';
    
    if (data.top_traders && data.top_traders.length > 0) {
        data.top_traders.forEach((trader, index) => {
            html += `
                <div class="trader-card mb-3 p-3 bg-dark rounded">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">
                                <span class="rank">#${index + 1}</span>
                                ${trader.username}
                            </h6>
                            <div class="trader-stats">
                                <span class="badge bg-success me-2">${trader.win_rate.toFixed(0)}% Win Rate</span>
                                <span class="badge bg-info me-2">${trader.total_trades} Trades</span>
                                <span class="badge bg-warning">Risk: ${trader.risk_score.toFixed(0)}/100</span>
                            </div>
                        </div>
                        <div class="text-end">
                            <div class="profit-display ${trader.profit_loss >= 0 ? 'text-success' : 'text-danger'}">
                                ${trader.profit_loss >= 0 ? '+' : ''}$${Math.abs(trader.profit_loss).toFixed(2)}
                            </div>
                            <button class="btn btn-sm btn-outline-primary mt-2" onclick="viewTraderProfile(${trader.user_id})">
                                View Profile
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
    } else {
        html += '<p class="text-muted">No top traders data available</p>';
    }
    
    html += '</div>';
    container.innerHTML = html;
}

function updateAchievementsUI(data) {
    const container = document.getElementById('achievements');
    if (!container) return;
    
    if (!data.user_stats) {
        container.innerHTML = '<p class="text-muted">No achievements data available</p>';
        return;
    }
    
    const stats = data.user_stats;
    let html = `
        <div class="achievement-summary mb-4">
            <div class="row">
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value">${stats.total_points}</div>
                        <div class="stat-label">Total Points</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value">Level ${stats.current_level}</div>
                        <div class="stat-label">${stats.level_name}</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value">${stats.achievements_earned}/${stats.achievements_total}</div>
                        <div class="stat-label">Achievements</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value">${stats.progress_to_next.toFixed(0)}%</div>
                        <div class="stat-label">Next Level</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Display achievements grid
    if (stats.achievement_list && stats.achievement_list.length > 0) {
        html += '<div class="achievements-grid row">';
        stats.achievement_list.forEach(achievement => {
            const earnedClass = achievement.earned ? 'earned' : 'locked';
            html += `
                <div class="col-md-4 mb-3">
                    <div class="achievement-card ${earnedClass}">
                        <div class="achievement-icon">
                            <i class="${achievement.icon}"></i>
                        </div>
                        <h6>${achievement.name}</h6>
                        <p class="achievement-desc">${achievement.description}</p>
                        <div class="achievement-points">+${achievement.points} points</div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    container.innerHTML = html;
}

function updateLeaderboardUI(leaderboard) {
    const container = document.getElementById('leaderboard');
    if (!container) return;
    
    if (!leaderboard || leaderboard.length === 0) {
        container.innerHTML = '<p class="text-muted">No leaderboard data available</p>';
        return;
    }
    
    let html = '<div class="leaderboard-list">';
    leaderboard.forEach((user, index) => {
        const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '';
        html += `
            <div class="leaderboard-row d-flex justify-content-between align-items-center p-2 mb-2 bg-dark rounded">
                <div class="d-flex align-items-center">
                    <span class="rank me-3">${medal || '#' + (index + 1)}</span>
                    <div>
                        <strong>${user.username}</strong>
                        <div class="small text-muted">Level ${user.level} • ${user.achievements} achievements</div>
                    </div>
                </div>
                <div class="text-end">
                    <div class="points">${user.points} pts</div>
                    <div class="small text-muted">${user.trades} trades</div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

function updateChallengesUI(challenges) {
    const container = document.getElementById('challenges');
    if (!container) return;
    
    if (!challenges || challenges.length === 0) {
        container.innerHTML = '<p class="text-muted">No active challenges</p>';
        return;
    }
    
    let html = '<div class="challenges-list">';
    challenges.forEach(challenge => {
        html += `
            <div class="challenge-card mb-3 p-3 bg-dark rounded">
                <h6>${challenge.name}</h6>
                <p class="mb-2">${challenge.description}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="badge bg-success">${challenge.reward} points</span>
                        <span class="badge bg-info">${challenge.participants} participants</span>
                    </div>
                    <div class="text-muted">
                        Ends in ${challenge.ends_in}
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

// Helper function to view trader profile
function viewTraderProfile(traderId) {
    // This could open a modal or navigate to a trader profile page
    console.log('Viewing trader profile:', traderId);
    // Implementation can be added later
}

// AI Training Functions
async function loadAIPerformance() {
    try {
        const response = await fetch('/api/ai/performance');
        const data = await response.json();
        
        const performanceDiv = document.getElementById('ai-performance');
        if (data.model_performance) {
            performanceDiv.innerHTML = `
                <div class="row">
                    <div class="col-6">
                        <div class="text-muted small">Price Prediction Accuracy</div>
                        <div class="text-success h5">${(data.model_performance.price_prediction * 100).toFixed(1)}%</div>
                    </div>
                    <div class="col-6">
                        <div class="text-muted small">Trend Classification</div>
                        <div class="text-info h5">${(data.model_performance.trend_classifier * 100).toFixed(1)}%</div>
                    </div>
                </div>
                <div class="row mt-2">
                    <div class="col-6">
                        <div class="text-muted small">Volatility Prediction</div>
                        <div class="text-warning h5">${(data.model_performance.volatility_predictor * 100).toFixed(1)}%</div>
                    </div>
                    <div class="col-6">
                        <div class="text-muted small">Training Samples</div>
                        <div class="text-primary h5">${data.model_performance.training_samples || 0}</div>
                    </div>
                </div>
                <div class="mt-2">
                    <small class="text-muted">Last trained: ${data.last_updated}</small>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading AI performance:', error);
    }
}

async function trainAIModel() {
    const statusDiv = document.getElementById('training-status');
    statusDiv.innerHTML = '<div class="alert alert-info"><i class="fas fa-spinner fa-spin me-2"></i>Training AI model with latest market data...</div>';
    
    try {
        const response = await fetch('/api/ai/train', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                days: 90
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    AI model trained successfully!
                    <br><small>Trained on ${data.training_samples} samples</small>
                </div>
            `;
            loadAIPerformance();
        } else {
            statusDiv.innerHTML = '<div class="alert alert-danger"><i class="fas fa-exclamation-triangle me-2"></i>Failed to train model</div>';
        }
    } catch (error) {
        console.error('Error training AI model:', error);
        statusDiv.innerHTML = '<div class="alert alert-danger"><i class="fas fa-exclamation-triangle me-2"></i>Error training model</div>';
    }
}

async function triggerContinuousLearning() {
    const statusDiv = document.getElementById('training-status');
    statusDiv.innerHTML = '<div class="alert alert-info"><i class="fas fa-sync-alt fa-spin me-2"></i>Updating AI from recent trades...</div>';
    
    try {
        const response = await fetch('/api/ai/continuous-learning', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    AI updated from recent trading activity!
                </div>
            `;
            loadAIPerformance();
        } else {
            statusDiv.innerHTML = '<div class="alert alert-warning"><i class="fas fa-info-circle me-2"></i>No recent trades to learn from</div>';
        }
    } catch (error) {
        console.error('Error in continuous learning:', error);
        statusDiv.innerHTML = '<div class="alert alert-danger"><i class="fas fa-exclamation-triangle me-2"></i>Error updating AI</div>';
    }
}

async function getPredictions() {
    const symbolsInput = document.getElementById('prediction-symbols');
    const predictionsDiv = document.getElementById('market-predictions');
    
    const symbols = symbolsInput.value.split(',').map(s => s.trim()).filter(s => s);
    
    if (symbols.length === 0) {
        predictionsDiv.innerHTML = '<div class="alert alert-warning">Please enter at least one symbol</div>';
        return;
    }
    
    predictionsDiv.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Generating predictions...</div>';
    
    try {
        const response = await fetch('/api/ai/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ symbols })
        });
        
        const data = await response.json();
        
        if (data.predictions && Object.keys(data.predictions).length > 0) {
            let html = '<div class="row">';
            
            for (const [symbol, prediction] of Object.entries(data.predictions)) {
                const recommendationClass = prediction.recommendation.includes('buy') ? 'success' : 
                                          prediction.recommendation.includes('sell') ? 'danger' : 'warning';
                
                html += `
                    <div class="col-md-6 mb-3">
                        <div class="card bg-dark border-${recommendationClass}">
                            <div class="card-body">
                                <h6 class="card-title">${symbol}</h6>
                                <div class="mb-2">
                                    <small class="text-muted">Expected Return:</small>
                                    <span class="text-${prediction.expected_return > 0 ? 'success' : 'danger'}">
                                        ${(prediction.expected_return * 100).toFixed(2)}%
                                    </span>
                                </div>
                                <div class="mb-2">
                                    <small class="text-muted">Uptrend Probability:</small>
                                    <div class="progress" style="height: 20px;">
                                        <div class="progress-bar bg-${prediction.uptrend_probability > 0.6 ? 'success' : 'warning'}" 
                                             style="width: ${prediction.uptrend_probability * 100}%">
                                            ${(prediction.uptrend_probability * 100).toFixed(0)}%
                                        </div>
                                    </div>
                                </div>
                                <div class="mb-2">
                                    <small class="text-muted">Risk Score:</small>
                                    <span class="text-${prediction.risk_score < 40 ? 'success' : prediction.risk_score < 70 ? 'warning' : 'danger'}">
                                        ${prediction.risk_score.toFixed(0)}/100
                                    </span>
                                </div>
                                <div class="mt-2">
                                    <span class="badge bg-${recommendationClass}">
                                        ${prediction.recommendation.toUpperCase()}
                                    </span>
                                    <span class="badge bg-secondary">
                                        ${prediction.market_regime.replace('_', ' ')}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            html += '</div>';
            predictionsDiv.innerHTML = html;
        } else {
            predictionsDiv.innerHTML = '<div class="alert alert-warning">No predictions available</div>';
        }
    } catch (error) {
        console.error('Error getting predictions:', error);
        predictionsDiv.innerHTML = '<div class="alert alert-danger">Error generating predictions</div>';
    }
}

// Export functions for global access
window.showSection = showSection;
window.toggleTheme = toggleTheme;
window.applyFilters = applyFilters;
window.showTradeModal = showTradeModal;
window.executeTrade = executeTrade;
window.dismissAlert = dismissAlert;
window.showDepositModal = showDepositModal;
window.processDeposit = processDeposit;
window.showBuyModal = showBuyModal;
window.executeBuy = executeBuy;
window.showSellModal = showSellModal;
window.executeSell = executeSell;
window.showTransactionHistory = showTransactionHistory;
window.searchStock = searchStock;
window.viewTraderProfile = viewTraderProfile;
window.trainAIModel = trainAIModel;
window.triggerContinuousLearning = triggerContinuousLearning;
window.getPredictions = getPredictions;

// Personalized AI Functions
async function loadPersonalizedAI() {
    try {
        // Load personalized recommendations
        const response = await fetch('/api/ai/personalized/recommendations');
        const data = await response.json();
        
        const container = document.getElementById('personalized-recommendations');
        if (!container) return;
        
        if (data.status === 'no_profile') {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    ${data.message}
                </div>
            `;
            document.getElementById('trading-profile').innerHTML = `
                <p class="text-muted">No trading profile yet. Make some trades to build your profile!</p>
            `;
            return;
        }
        
        if (data.status === 'success') {
            // Show trading profile
            const profileHtml = `
                <div class="trading-style mb-3">
                    <strong>Your Style:</strong> ${data.insights.trading_style}
                </div>
                <div class="risk-profile mb-3">
                    <strong>Risk Profile:</strong> 
                    <span class="badge bg-${data.insights.risk_profile === 'conservative' ? 'success' : data.insights.risk_profile === 'moderate' ? 'warning' : 'danger'}">
                        ${data.insights.risk_profile}
                    </span>
                </div>
                <div class="suggestions">
                    <strong>AI Suggestions:</strong>
                    <ul class="small">
                        ${data.insights.suggestions.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                </div>
            `;
            document.getElementById('trading-profile').innerHTML = profileHtml;
            
            // Show recommendations
            let recsHtml = '<div class="personalized-recs">';
            data.recommendations.forEach(rec => {
                recsHtml += `
                    <div class="recommendation-card mb-2 p-2 bg-dark rounded">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${rec.symbol}</strong>
                                <span class="badge bg-${rec.action === 'buy' ? 'success' : 'warning'} ms-2">
                                    ${rec.action.toUpperCase()}
                                </span>
                            </div>
                            <div class="text-end">
                                <div class="score">Match: ${(rec.score * 100).toFixed(0)}%</div>
                            </div>
                        </div>
                        <div class="reason text-muted small mt-1">${rec.reason}</div>
                    </div>
                `;
            });
            recsHtml += '</div>';
            container.innerHTML = recsHtml;
        }
    } catch (error) {
        console.error('Error loading personalized AI:', error);
    }
}

async function learnTradingPatterns() {
    const button = event.target;
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Learning...';
    
    try {
        const response = await fetch('/api/ai/personalized/learn', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('Trading patterns analyzed successfully!', 'success');
            await loadPersonalizedAI();
        } else {
            showNotification(data.message || 'Failed to analyze patterns', 'error');
        }
    } catch (error) {
        console.error('Error learning patterns:', error);
        showNotification('Error analyzing trading patterns', 'error');
    } finally {
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-graduation-cap me-2"></i>Update Profile from Trades';
    }
}

// Strategy Builder Functions
async function loadUserStrategies() {
    try {
        const response = await fetch('/api/strategies');
        const data = await response.json();
        
        const container = document.getElementById('user-strategies');
        if (!container) return;
        
        if (data.status === 'success' && data.strategies.length > 0) {
            let html = '<div class="strategies-list">';
            data.strategies.forEach(strategy => {
                html += `
                    <div class="strategy-item mb-2 p-2 bg-dark rounded">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${strategy.name}</strong>
                                ${strategy.ai_optimized ? '<span class="badge bg-success ms-2">AI Optimized</span>' : ''}
                            </div>
                            <div>
                                <button class="btn btn-sm btn-outline-primary" onclick="backtestStrategy('${strategy.id}')">
                                    <i class="fas fa-chart-line"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-success" onclick="optimizeStrategy('${strategy.id}')">
                                    <i class="fas fa-magic"></i>
                                </button>
                            </div>
                        </div>
                        <div class="text-muted small">${strategy.description || 'No description'}</div>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p class="text-muted">No strategies created yet</p>';
        }
    } catch (error) {
        console.error('Error loading strategies:', error);
    }
}

function showStrategyBuilder() {
    const form = document.getElementById('strategy-builder-form');
    if (form.style.display === 'none') {
        form.style.display = 'block';
        form.innerHTML = `
            <div class="strategy-form">
                <input type="text" class="form-control mb-2" id="strategy-name" placeholder="Strategy Name">
                <textarea class="form-control mb-2" id="strategy-description" rows="2" placeholder="Description"></textarea>
                
                <h6 class="text-info mt-3">Add Rules</h6>
                <div id="strategy-rules">
                    <div class="rule-item mb-2">
                        <select class="form-select form-select-sm mb-1" id="rule-type">
                            <option value="price_above_ma">Price Above Moving Average</option>
                            <option value="rsi">RSI Condition</option>
                            <option value="volume">Volume Spike</option>
                        </select>
                        <input type="number" class="form-control form-control-sm mb-1" placeholder="Parameter (e.g., 20 for MA20)">
                        <select class="form-select form-select-sm">
                            <option value="buy">Action: Buy</option>
                            <option value="sell">Action: Sell</option>
                        </select>
                    </div>
                </div>
                
                <button class="btn btn-success btn-sm mt-2" onclick="createStrategy()">
                    <i class="fas fa-save me-2"></i>Create Strategy
                </button>
                <button class="btn btn-secondary btn-sm mt-2" onclick="hideStrategyBuilder()">
                    Cancel
                </button>
            </div>
        `;
    } else {
        form.style.display = 'none';
    }
}

function hideStrategyBuilder() {
    document.getElementById('strategy-builder-form').style.display = 'none';
}

async function createStrategy() {
    const name = document.getElementById('strategy-name').value;
    const description = document.getElementById('strategy-description').value;
    
    if (!name) {
        showNotification('Please enter a strategy name', 'error');
        return;
    }
    
    const strategyConfig = {
        name: name,
        description: description,
        rules: [
            {
                condition: {
                    type: document.getElementById('rule-type').value,
                    period: 20
                },
                action: 'buy'
            }
        ],
        indicators: ['ma', 'rsi'],
        risk_params: {
            stop_loss: 0.05,
            take_profit: 0.10
        }
    };
    
    try {
        const response = await fetch('/api/strategies', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(strategyConfig)
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('Strategy created successfully!', 'success');
            hideStrategyBuilder();
            await loadUserStrategies();
        } else {
            showNotification(data.message || 'Failed to create strategy', 'error');
        }
    } catch (error) {
        console.error('Error creating strategy:', error);
        showNotification('Error creating strategy', 'error');
    }
}

async function backtestStrategy(strategyId) {
    const resultsContainer = document.getElementById('backtest-results');
    resultsContainer.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Running backtest...</div>';
    
    try {
        const response = await fetch(`/api/strategies/${strategyId}/backtest`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            const results = data.results;
            resultsContainer.innerHTML = `
                <div class="backtest-results">
                    <div class="metric mb-2">
                        <strong>Total Return:</strong> 
                        <span class="${results.total_return > 0 ? 'text-success' : 'text-danger'}">
                            ${results.total_return.toFixed(2)}%
                        </span>
                    </div>
                    <div class="metric mb-2">
                        <strong>Win Rate:</strong> ${results.win_rate.toFixed(1)}%
                    </div>
                    <div class="metric mb-2">
                        <strong>Max Drawdown:</strong> 
                        <span class="text-danger">${results.max_drawdown.toFixed(1)}%</span>
                    </div>
                    <div class="metric mb-2">
                        <strong>Sharpe Ratio:</strong> ${results.sharpe_ratio.toFixed(2)}
                    </div>
                    ${results.ai_suggestions.length > 0 ? `
                        <div class="ai-suggestions mt-3">
                            <strong class="text-warning">AI Suggestions:</strong>
                            <ul class="small">
                                ${results.ai_suggestions.map(s => `<li>${s.message}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `;
        } else {
            resultsContainer.innerHTML = `<div class="alert alert-danger">${data.message || 'Backtest failed'}</div>`;
        }
    } catch (error) {
        console.error('Error backtesting strategy:', error);
        resultsContainer.innerHTML = '<div class="alert alert-danger">Error running backtest</div>';
    }
}

async function optimizeStrategy(strategyId) {
    const button = event.target.closest('button');
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    try {
        const response = await fetch(`/api/strategies/${strategyId}/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification(`Strategy optimized! Expected improvement: ${data.expected_improvement.toFixed(1)}%`, 'success');
            await loadUserStrategies();
        } else {
            showNotification(data.message || 'Optimization failed', 'error');
        }
    } catch (error) {
        console.error('Error optimizing strategy:', error);
        showNotification('Error optimizing strategy', 'error');
    } finally {
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-magic"></i>';
    }
}

// Functions for Advanced tab display
function updateAchievementsDisplay(data) {
    const container = document.getElementById('achievements-list');
    if (!container) return;
    
    if (data.achievements && data.achievements.length > 0) {
        let html = '';
        data.achievements.forEach(achievement => {
            const completedClass = achievement.completed ? 'completed' : '';
            html += `
                <div class="achievement-item ${completedClass}">
                    <i class="${achievement.icon}"></i>
                    <div class="achievement-info">
                        <div class="achievement-name">${achievement.name}</div>
                        <div class="achievement-progress">
                            <div class="progress" style="height: 4px;">
                                <div class="progress-bar bg-warning" style="width: ${achievement.progress}%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;
    }
}

function updateLeaderboardDisplay(data) {
    const container = document.getElementById('top-traders-list');
    if (!container) return;
    
    if (data.traders && data.traders.length > 0) {
        let html = '';
        data.traders.forEach(trader => {
            html += `
                <div class="trader-item">
                    <div class="trader-rank">#${trader.rank}</div>
                    <div class="trader-info">
                        <div class="trader-name">${trader.username}</div>
                        <div class="trader-stats">
                            <span class="text-success">${trader.return_percentage.toFixed(1)}%</span>
                            <span class="text-muted">${trader.trades} trades</span>
                        </div>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;
    }
}

function updateChallengesDisplay(data) {
    const container = document.getElementById('challenges-list');
    if (!container) return;
    
    if (data.challenges && data.challenges.length > 0) {
        let html = '';
        data.challenges.forEach(challenge => {
            html += `
                <div class="challenge-card">
                    <div class="challenge-header">
                        <i class="${challenge.icon} text-warning"></i>
                        <h6>${challenge.name}</h6>
                    </div>
                    <p class="challenge-desc">${challenge.description}</p>
                    <div class="challenge-progress">
                        <div class="progress">
                            <div class="progress-bar bg-success" style="width: ${challenge.progress}%">
                                ${challenge.progress}%
                            </div>
                        </div>
                    </div>
                    <div class="challenge-footer">
                        <span class="reward">${challenge.reward}</span>
                        <span class="participants">${challenge.participants} participants</span>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;
    }
}

// Alert Management Functions
async function createAlert() {
    const symbol = document.getElementById('alert-symbol').value.toUpperCase();
    const alertType = document.getElementById('alert-type').value;
    const value = document.getElementById('alert-value').value;
    
    if (!symbol || !alertType || !value) {
        showError('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetch('/api/alerts/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symbol: symbol,
                alert_type: alertType,
                trigger_value: parseFloat(value)
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess('Alert created successfully!');
            // Clear form
            document.getElementById('alert-symbol').value = '';
            document.getElementById('alert-value').value = '';
            // Reload alerts
            loadAlerts();
        } else {
            showError(data.error || 'Failed to create alert');
        }
    } catch (error) {
        console.error('Error creating alert:', error);
        showError('Failed to create alert');
    }
}

async function dismissAlert(alertId) {
    try {
        const response = await fetch(`/api/alerts/${alertId}/dismiss`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess('Alert dismissed');
            loadAlerts(); // Reload alerts
        } else {
            showError(data.error || 'Failed to dismiss alert');
        }
    } catch (error) {
        console.error('Error dismissing alert:', error);
        showError('Failed to dismiss alert');
    }
}

// Export new functions
window.loadPersonalizedAI = loadPersonalizedAI;
window.learnTradingPatterns = learnTradingPatterns;
window.loadUserStrategies = loadUserStrategies;
window.showStrategyBuilder = showStrategyBuilder;
window.hideStrategyBuilder = hideStrategyBuilder;
window.createStrategy = createStrategy;
window.backtestStrategy = backtestStrategy;
window.optimizeStrategy = optimizeStrategy;
window.createAlert = createAlert;
window.dismissAlert = dismissAlert;
