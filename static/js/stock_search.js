// Stock Search Functionality for TradeWise AI

// Company name to symbol mapping
const companySymbols = {
    'nvidia': 'NVDA',
    'apple': 'AAPL', 
    'tesla': 'TSLA',
    'microsoft': 'MSFT',
    'amazon': 'AMZN',
    'google': 'GOOGL',
    'alphabet': 'GOOGL',
    'meta': 'META',
    'facebook': 'META',
    'netflix': 'NFLX',
    'adobe': 'ADBE',
    'salesforce': 'CRM',
    'oracle': 'ORCL',
    'intel': 'INTC',
    'amd': 'AMD',
    'zoom': 'ZM',
    'spotify': 'SPOT',
    'uber': 'UBER',
    'lyft': 'LYFT',
    'airbnb': 'ABNB'
};

// Debug: Log company symbols on load
console.log('TradeWise AI: Company symbols loaded:', companySymbols);

// Search by company name function
function searchStockByName(companyName) {
    console.log('TradeWise AI: Searching for company:', companyName);
    
    const symbol = companySymbols[companyName.toLowerCase()];
    if (symbol) {
        console.log('TradeWise AI: Found symbol:', symbol);
        // Update search input
        const searchInput = document.getElementById('main-search-input');
        if (searchInput) {
            searchInput.value = symbol;
        }
        
        // Perform search with the symbol
        performIntelligentSearchWithSymbol(symbol);
    } else {
        console.error('TradeWise AI: Symbol not found for:', companyName);
        showNotification(`Company ${companyName} not found in our database`, 'error');
    }
}

// Perform intelligent search function
function performIntelligentSearch() {
    const searchInput = document.getElementById('main-search-input');
    const searchValue = searchInput ? searchInput.value.trim() : '';
    
    if (!searchValue) {
        showNotification('Please enter a stock symbol or company name', 'warning');
        return;
    }
    
    // Check if it's a company name and convert to symbol
    let symbol = searchValue.toUpperCase();
    const companySymbol = companySymbols[searchValue.toLowerCase()];
    if (companySymbol) {
        symbol = companySymbol;
        searchInput.value = symbol; // Update input with symbol
    }
    
    performIntelligentSearchWithSymbol(symbol);
}

// Perform search with specific symbol
function performIntelligentSearchWithSymbol(symbol) {
    console.log('Performing search for symbol:', symbol);
    
    // Show loading state
    showSearchLoading();
    
    // Call the stock analysis API
    fetch(`/api/stock-analysis/${symbol}`)
        .then(response => response.json())
        .then(data => {
            hideSearchLoading();
            displaySearchResults(data);
        })
        .catch(error => {
            console.error('Search error:', error);
            hideSearchLoading();
            showNotification('Search failed. Please try again.', 'error');
        });
}

// Display search results
function displaySearchResults(data) {
    const resultsContainer = document.getElementById('main-search-results');
    if (!resultsContainer) return;
    
    if (data.error) {
        resultsContainer.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i>
                ${data.error}
            </div>
        `;
        return;
    }
    
    // Create result card
    const resultCard = `
        <div class="search-result-card">
            <div class="stock-header">
                <h3 class="stock-name">${data.name || data.symbol}</h3>
                <span class="stock-symbol">${data.symbol}</span>
            </div>
            
            <div class="stock-price">
                <span class="price">$${data.price}</span>
                <span class="change ${data.change >= 0 ? 'positive' : 'negative'}">
                    ${data.change >= 0 ? '+' : ''}${data.change} (${data.change_percent}%)
                </span>
            </div>
            
            <div class="ai-recommendation">
                <div class="recommendation-badge ${data.ai_recommendation.toLowerCase()}">
                    ${data.ai_recommendation}
                </div>
                <div class="confidence-score">
                    Confidence: ${data.ai_confidence}%
                </div>
            </div>
            
            <div class="stock-details">
                <div class="detail-item">
                    <span class="label">Market Cap:</span>
                    <span class="value">${data.market_cap || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="label">P/E Ratio:</span>
                    <span class="value">${data.pe_ratio || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="label">Volume:</span>
                    <span class="value">${data.volume || 'N/A'}</span>
                </div>
            </div>
            
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="showBuyModal('${data.symbol}')">
                    <i class="fas fa-shopping-cart"></i> Buy Stock
                </button>
                <button class="btn btn-outline-secondary" onclick="addToWatchlist('${data.symbol}')">
                    <i class="fas fa-star"></i> Add to Watchlist
                </button>
            </div>
        </div>
    `;
    
    resultsContainer.innerHTML = resultCard;
}

// Show search loading
function showSearchLoading() {
    const resultsContainer = document.getElementById('main-search-results');
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = `
        <div class="loading-state">
            <div class="loading-spinner"></div>
            <span>Analyzing stock with AI...</span>
        </div>
    `;
}

// Hide search loading
function hideSearchLoading() {
    // Loading will be replaced by results
}

// Handle search keypress
function handleSearchKeypress(event) {
    if (event.key === 'Enter') {
        performIntelligentSearch();
    }
}

// Show notification (simple implementation)
function showNotification(message, type = 'info') {
    console.log(`${type.toUpperCase()}: ${message}`);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type === 'warning' ? 'warning' : 'info'}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 300px;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    notification.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'warning' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
    `;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Hide notification after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Placeholder functions for buy modal and watchlist
function showBuyModal(symbol) {
    showNotification(`Buy modal for ${symbol} - Feature coming soon!`, 'info');
}

function addToWatchlist(symbol) {
    showNotification(`Added ${symbol} to watchlist!`, 'success');
}

// Initialize search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('main-search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', handleSearchKeypress);
    }
    
    console.log('Stock search functionality loaded for TradeWise AI');
});