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