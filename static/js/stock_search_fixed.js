// TradeWise AI Stock Search - Clean Implementation
// Stock Search Functionality for TradeWise AI


// Note: Company name to symbol mapping is now handled by the backend S&P 500 database

// Get recommendation styles for color-coded badges
function getRecommendationStyles(recommendation) {
    const rec = recommendation.toLowerCase();
    
    switch(rec) {
        case 'strong buy':
            return { backgroundColor: '#059669', color: '#ffffff' };
        case 'buy':
            return { backgroundColor: '#10b981', color: '#ffffff' };
        case 'hold':
            return { backgroundColor: '#fbbf24', color: '#000000' };
        case 'sell':
            return { backgroundColor: '#ef4444', color: '#ffffff' };
        case 'strong sell':
            return { backgroundColor: '#dc2626', color: '#ffffff' };
        default:
            return { backgroundColor: '#6b7280', color: '#ffffff' };
    }
}

// Search by company name function
function searchStockByName(companyName) {
    console.log('TradeWise AI: Stock chip clicked for company:', companyName);
    
    const symbol = companySymbols[companyName.toLowerCase()];
    if (symbol) {
        console.log('TradeWise AI: Converting', companyName, '→', symbol);
        // Update search input
        const searchInput = document.getElementById('main-search-input');
        if (searchInput) {
            searchInput.value = symbol;
        }
        
        // Perform search with the symbol
        performIntelligentSearchWithSymbol(symbol);
    } else {
        console.error('TradeWise AI: Symbol not found for:', companyName);
        console.error('Available symbols:', Object.keys(companySymbols));
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
    
    // Convert search term to symbol (backend handles S&P 500 mapping)
    let symbol = searchValue;
    
    performIntelligentSearchWithSymbol(symbol);
}

// Enhanced stock symbol validation
function isValidStockSymbol(symbol) {
    // Allow 1-10 characters, letters, numbers, hyphens, dots
    const symbolRegex = /^[A-Z0-9.-]{1,10}$/;
    return symbolRegex.test(symbol.toUpperCase());
}

// Perform search with specific symbol
function performIntelligentSearchWithSymbol(symbol) {
    console.log('TradeWise AI: Performing search for symbol:', symbol);
    
    // Validate symbol format before making API call
    if (!isValidStockSymbol(symbol)) {
        showErrorMessage(`"${symbol}" is not a valid stock symbol. Please use 1-10 characters (letters, numbers, hyphens, dots only).`);
        return;
    }
    
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
            showErrorMessage(`Unable to find "${symbol}". This could mean:
            • The stock symbol doesn't exist
            • It's a foreign stock not available in US markets  
            • There's a temporary data issue
            
            Try searching for the full company name or verify the symbol on a financial website.`);
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

// Get recommendation styles based on type
function getRecommendationStyles(recommendation) {
    const rec = recommendation.toLowerCase();
    switch(rec) {
        case 'strong buy':
            return 'color: white !important; background: #059669 !important;';
        case 'buy':
            return 'color: white !important; background: #10b981 !important;';
        case 'hold':
            return 'color: #000000 !important; background: #fbbf24 !important;';
        case 'sell':
            return 'color: white !important; background: #ef4444 !important;';
        case 'strong sell':
            return 'color: white !important; background: #dc2626 !important;';
        default:
            return 'color: white !important; background: #6b7280 !important;';
    }
}

// Portfolio functionality
function buyStock(symbol) {
    // Show buy modal with stock details
    showBuyModal(symbol);
}

function addToWatchlist(symbol) {
    fetch('/api/add-to-watchlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ symbol: symbol })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`${symbol} added to watchlist!`, 'success');
        } else {
            showNotification(data.message || 'Failed to add to watchlist', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding to watchlist:', error);
        showNotification('Error adding to watchlist', 'error');
    });
}

// Show buy modal
function showBuyModal(symbol) {
    const modal = document.createElement('div');
    modal.className = 'buy-modal-overlay';
    modal.innerHTML = `
        <div class="buy-modal">
            <div class="buy-modal-header">
                <h3>Buy ${symbol}</h3>
                <button class="close-modal" onclick="closeBuyModal()">&times;</button>
            </div>
            <div class="buy-modal-body">
                <div class="loading-spinner">Loading stock details...</div>
            </div>
        </div>
    `;
    
    // Add modal styles
    const styles = `
        .buy-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .buy-modal {
            background: #1a1a2e;
            border-radius: 15px;
            width: min(90%, 500px);
            max-height: 90vh;
            overflow-y: auto;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .buy-modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .buy-modal-header h3 {
            color: white;
            margin: 0;
            font-size: 1.5rem;
        }
        .close-modal {
            background: none;
            border: none;
            color: rgba(255, 255, 255, 0.7);
            font-size: 2rem;
            cursor: pointer;
            line-height: 1;
        }
        .buy-modal-body {
            padding: 1.5rem;
        }
        .loading-spinner {
            text-align: center;
            color: rgba(255, 255, 255, 0.7);
            padding: 2rem;
        }
        .stock-price-info {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1.5rem;
        }
        .buy-form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        .form-group label {
            color: rgba(255, 255, 255, 0.8);
            font-weight: 600;
        }
        .form-group input {
            padding: 0.75rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 1rem;
        }
        .purchase-summary {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid #10b981;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .buy-button {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            border: none;
            padding: 1rem;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .buy-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        }
    `;
    
    if (!document.getElementById('buy-modal-styles')) {
        const styleSheet = document.createElement('style');
        styleSheet.id = 'buy-modal-styles';
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    document.body.appendChild(modal);
    
    // Load stock details
    loadStockDetailsForPurchase(symbol);
}

// Load stock details for purchase
function loadStockDetailsForPurchase(symbol) {
    fetch(`/api/stock-analysis/${symbol}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayBuyForm(symbol, data);
            } else {
                document.querySelector('.buy-modal-body').innerHTML = `
                    <div class="error-message">
                        <p style="color: #ef4444;">Failed to load stock details: ${data.error || 'Unknown error'}</p>
                        <button class="buy-button" onclick="closeBuyModal()">Close</button>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading stock details:', error);
            document.querySelector('.buy-modal-body').innerHTML = `
                <div class="error-message">
                    <p style="color: #ef4444;">Error loading stock details. Please try again.</p>
                    <button class="buy-button" onclick="closeBuyModal()">Close</button>
                </div>
            `;
        });
}

// Display buy form with stock details
function displayBuyForm(symbol, stockData) {
    const modalBody = document.querySelector('.buy-modal-body');
    const price = parseFloat(stockData.price);
    
    modalBody.innerHTML = `
        <div class="stock-price-info">
            <h4 style="color: white; margin: 0 0 0.5rem 0;">${stockData.name}</h4>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #10b981; font-size: 1.5rem; font-weight: 700;">$${price.toFixed(2)}</span>
                    <span style="color: ${stockData.change >= 0 ? '#10b981' : '#ef4444'}; margin-left: 0.5rem;">
                        ${stockData.change >= 0 ? '+' : ''}${stockData.change_percent}%
                    </span>
                </div>
                <div style="text-align: right;">
                    <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">Market Cap</div>
                    <div style="color: white; font-weight: 600;">${stockData.market_cap}</div>
                </div>
            </div>
        </div>
        
        <form class="buy-form" onsubmit="executePurchase(event, '${symbol}', ${price})">
            <div class="form-group">
                <label for="quantity">Number of Shares to Buy</label>
                <input type="number" id="quantity" name="quantity" min="1" value="1" required 
                       onchange="updatePurchaseTotal('${symbol}', ${price})">
            </div>
            
            <div class="form-group">
                <label>Price per Share</label>
                <input type="text" value="$${price.toFixed(2)}" readonly style="opacity: 0.7;">
            </div>
            
            <div class="purchase-summary" id="purchase-summary">
                <div style="color: white; font-weight: 600; margin-bottom: 0.5rem;">Purchase Summary</div>
                <div style="color: rgba(255,255,255,0.8);">
                    You are buying <span id="summary-quantity">1</span> shares for 
                    <strong style="color: #10b981;">$<span id="summary-total">${price.toFixed(2)}</span></strong>
                </div>
            </div>
            
            <button type="submit" class="buy-button">
                Buy ${symbol} Stock
            </button>
        </form>
    `;
}

// Update purchase total
function updatePurchaseTotal(symbol, price) {
    const quantity = parseInt(document.getElementById('quantity').value) || 1;
    const total = (quantity * price).toFixed(2);
    
    document.getElementById('summary-quantity').textContent = quantity;
    document.getElementById('summary-total').textContent = total;
}

// Execute purchase
function executePurchase(event, symbol, price) {
    event.preventDefault();
    
    const quantity = parseInt(document.getElementById('quantity').value);
    const total = quantity * price;
    
    // Show loading state
    const button = event.target.querySelector('.buy-button');
    const originalText = button.textContent;
    button.textContent = 'Processing Purchase...';
    button.disabled = true;
    
    fetch('/api/purchase-stock', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            symbol: symbol,
            quantity: quantity,
            price: price
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`Successfully purchased ${quantity} shares of ${symbol}!`, 'success');
            closeBuyModal();
            // Update portfolio display if visible
            loadPortfolioSummary();
        } else {
            showNotification(data.message || 'Purchase failed', 'error');
        }
    })
    .catch(error => {
        console.error('Error executing purchase:', error);
        showNotification('Error processing purchase', 'error');
    })
    .finally(() => {
        button.textContent = originalText;
        button.disabled = false;
    });
}

// Close buy modal
function closeBuyModal() {
    const modal = document.querySelector('.buy-modal-overlay');
    if (modal) {
        modal.remove();
    }
}

// Portfolio summary functionality
function loadPortfolioSummary() {
    // This will be called to refresh portfolio data
    console.log('TradeWise AI: Portfolio summary updated');
}

// Initialize
console.log('TradeWise AI: Stock search functionality loaded');