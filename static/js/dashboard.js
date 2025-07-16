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
    
    // Load theme preference
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    
    // Load initial data
    loadDashboardData();
    loadSectors();
    
    // Set up event listeners
    setupEventListeners();
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
    const sections = ['dashboard', 'stocks', 'alerts', 'portfolio'];
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
        default:
            loadDashboardData();
    }
}

// Data loading functions
async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        dashboardData = data;
        updateDashboard(data);
        
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
    // Update market overview
    updateMarketOverview(data.market_overview);
    
    // Update welcome banner
    updateWelcomeBanner(data.market_overview);
    
    // Update account balance
    updateAccountBalance(data.user_account);
    
    // Update performance summary
    updatePerformanceSummary(data.portfolio_performance);
    
    // Update top movers
    updateTopMovers(data.top_movers);
    
    // Update recent trades
    updateRecentTrades(data.recent_trades);
    
    // Update active alerts
    updateActiveAlerts(data.active_alerts);
    
    // Update timestamp
    updateTimestamp(data.timestamp);
}

function updateMarketOverview(overview) {
    document.getElementById('total-stocks').textContent = overview.total_stocks;
    document.getElementById('gainers').textContent = overview.gainers;
    document.getElementById('losers').textContent = overview.losers;
    document.getElementById('unchanged').textContent = overview.unchanged;
    
    const avgChange = overview.avg_change;
    const avgChangeElement = document.getElementById('avg-change');
    avgChangeElement.textContent = formatCurrency(avgChange);
    avgChangeElement.className = `stat-number ${avgChange >= 0 ? 'text-success' : 'text-danger'}`;
    
    document.getElementById('total-volume').textContent = formatVolume(overview.total_volume);
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
    document.getElementById('total-trades').textContent = performance.total_trades;
    document.getElementById('win-rate').textContent = performance.win_rate.toFixed(1) + '%';
    
    const pnl = performance.total_pnl;
    const pnlElement = document.getElementById('total-pnl');
    pnlElement.textContent = formatCurrency(pnl);
    pnlElement.className = pnl >= 0 ? 'text-success' : 'text-danger';
    
    document.getElementById('avg-confidence').textContent = performance.avg_confidence.toFixed(1) + '%';
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
    const container = document.getElementById('active-alerts');
    
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
    
    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<div class="text-center text-muted">No alerts found</div>';
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
    
    container.innerHTML = holdings.map(holding => `
        <div class="portfolio-item">
            <div class="portfolio-header">
                <div class="stock-symbol">${holding.symbol}</div>
                <div class="text-end">
                    <div class="stock-price">${formatCurrency(holding.current_price)}</div>
                    <div class="${holding.pnl >= 0 ? 'text-success' : 'text-danger'}">
                        ${formatCurrency(holding.pnl)} (${holding.pnl_pct.toFixed(2)}%)
                    </div>
                </div>
            </div>
            <div class="portfolio-details">
                <div class="portfolio-metric">
                    <div class="portfolio-metric-value">${holding.quantity}</div>
                    <div class="portfolio-metric-label">Shares</div>
                </div>
                <div class="portfolio-metric">
                    <div class="portfolio-metric-value">${formatCurrency(holding.avg_price)}</div>
                    <div class="portfolio-metric-label">Avg Price</div>
                </div>
                <div class="portfolio-metric">
                    <div class="portfolio-metric-value">${formatCurrency(holding.current_value)}</div>
                    <div class="portfolio-metric-label">Current Value</div>
                </div>
                <div class="portfolio-metric">
                    <div class="portfolio-metric-value">${formatCurrency(holding.cost_basis)}</div>
                    <div class="portfolio-metric-label">Cost Basis</div>
                </div>
            </div>
        </div>
    `).join('');
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
    
    switch (currentSection) {
        case 'stocks':
            loadStocks();
            break;
        case 'alerts':
            loadAlerts();
            break;
        case 'portfolio':
            loadPortfolio();
            break;
        default:
            loadDashboardData();
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
    // Create toast notification
    const toast = createToast('Error', message, 'danger');
    showToast(toast);
}

function showSuccess(message) {
    console.log(message);
    // Create toast notification
    const toast = createToast('Success', message, 'success');
    showToast(toast);
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

function showSellModal() {
    const modal = new bootstrap.Modal(document.getElementById('sellModal'));
    
    // Populate portfolio options
    const stockSelect = document.getElementById('sell-symbol');
    stockSelect.innerHTML = '<option value="">Select a stock...</option>';
    
    portfolioData.forEach(holding => {
        const option = document.createElement('option');
        option.value = holding.symbol;
        option.textContent = `${holding.symbol} - ${holding.quantity} shares`;
        option.dataset.quantity = holding.quantity;
        stockSelect.appendChild(option);
    });
    
    // Set up event listeners
    stockSelect.addEventListener('change', updateSellCalculations);
    document.getElementById('sell-quantity').addEventListener('input', updateSellCalculations);
    
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
        // Find current price from stocks data
        const stockData = stocksData.find(stock => stock.symbol === symbol);
        const price = stockData ? stockData.price : 0;
        const owned = parseInt(selectedOption.dataset.quantity) || 0;
        
        priceElement.textContent = price > 0 ? formatCurrency(price) : '-';
        totalElement.textContent = formatCurrency(price * quantity);
        ownedElement.textContent = owned;
        
        // Validate quantity
        if (quantity > owned) {
            quantityInput.setCustomValidity('Quantity exceeds owned shares');
        } else {
            quantityInput.setCustomValidity('');
        }
    } else {
        priceElement.textContent = '-';
        totalElement.textContent = '$0.00';
        ownedElement.textContent = '0';
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
