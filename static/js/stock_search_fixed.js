// TradeWise AI Stock Search - Clean Implementation
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
    console.log('TradeWise AI: Performing search for symbol:', symbol);
    
    // Show loading state
    const resultsDiv = document.getElementById('main-search-results');
    if (resultsDiv) {
        resultsDiv.innerHTML = `
            <div class="search-loading">
                <div class="loading-spinner"></div>
                <p>Analyzing ${symbol}...</p>
            </div>
        `;
        resultsDiv.style.display = 'block';
    }
    
    // Make API call to get stock analysis
    fetch(`/api/stock-analysis/${symbol}`)
        .then(response => response.json())
        .then(data => {
            console.log('TradeWise AI: API response:', data);
            if (data.success) {
                displayStockResults(data);
            } else {
                showErrorMessage(data.error || `Stock ${symbol} not found`);
            }
        })
        .catch(error => {
            console.error('TradeWise AI: Search error:', error);
            showErrorMessage(`Error searching for ${symbol}: ${error.message}`);
        });
}

// Function to display stock results
function displayStockResults(data) {
    const resultsDiv = document.getElementById('main-search-results');
    if (!resultsDiv) return;

    const changeColor = data.change >= 0 ? 'var(--green)' : 'var(--red)';
    const changeSymbol = data.change >= 0 ? '+' : '';
    
    resultsDiv.innerHTML = `
        <div class="stock-result-card">
            <div class="stock-header">
                <h3>${data.symbol}</h3>
                <span class="stock-name">${data.name}</span>
            </div>
            <div class="stock-price-section">
                <div class="price-display">
                    <span class="current-price">$${data.price}</span>
                    <span class="price-change" style="color: ${changeColor}">
                        ${changeSymbol}$${Math.abs(data.change).toFixed(2)} (${data.change_percent}%)
                    </span>
                </div>
            </div>
            <div class="ai-analysis">
                <h4>AI Analysis</h4>
                <div class="ai-recommendation ${data.ai_recommendation.toLowerCase()}">
                    ${data.ai_recommendation} (${data.ai_confidence}% confidence)
                </div>
                <p class="analysis-text">${data.analysis}</p>
            </div>
            <div class="stock-actions">
                <button class="btn btn-primary" onclick="buyStock('${data.symbol}')">
                    Buy ${data.symbol}
                </button>
                <button class="btn btn-secondary" onclick="addToWatchlist('${data.symbol}')">
                    Add to Watchlist
                </button>
            </div>
        </div>
    `;
    
    resultsDiv.style.display = 'block';
}

// Function to show error message
function showErrorMessage(message) {
    const resultsDiv = document.getElementById('main-search-results');
    if (!resultsDiv) return;
    
    resultsDiv.innerHTML = `
        <div class="search-error">
            <div class="error-icon">⚠️</div>
            <h3>Search Error</h3>
            <p>${message}</p>
            <button class="btn btn-secondary" onclick="clearSearchResults()">Try Again</button>
        </div>
    `;
    resultsDiv.style.display = 'block';
}

// Function to clear search results
function clearSearchResults() {
    const resultsDiv = document.getElementById('main-search-results');
    if (resultsDiv) {
        resultsDiv.innerHTML = '';
        resultsDiv.style.display = 'none';
    }
    
    const searchInput = document.getElementById('main-search-input');
    if (searchInput) {
        searchInput.value = '';
        searchInput.focus();
    }
}

// Function to show notification
function showNotification(message, type = 'info') {
    console.log(`TradeWise AI Notification [${type}]: ${message}`);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem;
        border-radius: 8px;
        color: white;
        background: ${type === 'error' ? 'var(--red)' : type === 'warning' ? 'var(--yellow)' : 'var(--green)'};
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Handle search keypress
function handleSearchKeypress(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        performIntelligentSearch();
    }
}

// Placeholder functions for actions
function buyStock(symbol) {
    showNotification(`Buy functionality for ${symbol} coming soon!`, 'info');
}

function addToWatchlist(symbol) {
    showNotification(`${symbol} added to watchlist!`, 'success');
}

// Initialize
console.log('TradeWise AI: Stock search functionality loaded');