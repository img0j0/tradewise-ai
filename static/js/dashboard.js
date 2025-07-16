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
    // Filter form
    document.getElementById('sector-filter').addEventListener('change', applyFilters);
    document.getElementById('min-price').addEventListener('input', applyFilters);
    document.getElementById('max-price').addEventListener('input', applyFilters);
    
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

function updatePerformanceSummary(performance) {
    document.getElementById('total-trades').textContent = performance.total_trades;
    document.getElementById('win-rate').textContent = performance.win_rate.toFixed(1) + '%';
    
    const pnl = performance.total_pnl;
    const pnlElement = document.getElementById('total-pnl');
    pnlElement.textContent = formatCurrency(pnl);
    pnlElement.className = pnl >= 0 ? 'text-success' : 'text-danger';
    
    document.getElementById('avg-confidence').textContent = performance.avg_confidence.toFixed(1) + '%';
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

// Export functions for global access
window.showSection = showSection;
window.toggleTheme = toggleTheme;
window.applyFilters = applyFilters;
window.showTradeModal = showTradeModal;
window.executeTrade = executeTrade;
window.dismissAlert = dismissAlert;
