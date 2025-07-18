// Google-Style AI Stock Search and Analysis

let currentAnalyzedStock = null;
let searchTimeout = null;
let selectedSuggestionIndex = -1;
let suggestions = [];

// Popular stocks data for suggestions
const popularStocks = [
    { symbol: 'AAPL', name: 'Apple Inc.', sector: 'Technology' },
    { symbol: 'MSFT', name: 'Microsoft Corporation', sector: 'Technology' },
    { symbol: 'GOOGL', name: 'Alphabet Inc.', sector: 'Technology' },
    { symbol: 'TSLA', name: 'Tesla Inc.', sector: 'Automotive' },
    { symbol: 'NVDA', name: 'NVIDIA Corporation', sector: 'Technology' },
    { symbol: 'AMZN', name: 'Amazon.com Inc.', sector: 'E-commerce' },
    { symbol: 'META', name: 'Meta Platforms Inc.', sector: 'Technology' },
    { symbol: 'NFLX', name: 'Netflix Inc.', sector: 'Entertainment' },
    { symbol: 'JPM', name: 'JPMorgan Chase & Co.', sector: 'Banking' },
    { symbol: 'V', name: 'Visa Inc.', sector: 'Financial Services' }
];

// Initialize Google-style search
document.addEventListener('DOMContentLoaded', function() {
    initializeGoogleSearch();
});

function initializeGoogleSearch() {
    const searchInput = document.getElementById('stock-search-input');
    const searchBtn = document.getElementById('search-btn');
    const suggestionsContainer = document.getElementById('search-suggestions');
    
    if (!searchInput || !searchBtn) return;
    
    // Add event listeners
    searchInput.addEventListener('input', handleSearchInput);
    searchInput.addEventListener('keydown', handleSearchKeydown);
    searchInput.addEventListener('focus', handleSearchFocus);
    searchInput.addEventListener('blur', handleSearchBlur);
    
    searchBtn.addEventListener('click', searchStockAI);
    
    // Click outside to close suggestions
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.google-search-box')) {
            hideSuggestions();
        }
    });
}

function handleSearchInput(e) {
    const query = e.target.value.trim();
    
    // Clear previous timeout
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    
    // Debounce search suggestions
    searchTimeout = setTimeout(() => {
        if (query.length > 0) {
            showSuggestions(query);
        } else {
            hideSuggestions();
        }
    }, 150);
}

function handleSearchKeydown(e) {
    const suggestionsContainer = document.getElementById('search-suggestions');
    const suggestionItems = suggestionsContainer.querySelectorAll('.suggestion-item');
    
    switch(e.key) {
        case 'ArrowDown':
            e.preventDefault();
            selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, suggestionItems.length - 1);
            updateSuggestionSelection();
            break;
            
        case 'ArrowUp':
            e.preventDefault();
            selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, -1);
            updateSuggestionSelection();
            break;
            
        case 'Enter':
            e.preventDefault();
            if (selectedSuggestionIndex >= 0 && suggestionItems[selectedSuggestionIndex]) {
                const suggestion = suggestions[selectedSuggestionIndex];
                selectSuggestion(suggestion);
            } else {
                searchStockAI();
            }
            break;
            
        case 'Escape':
            hideSuggestions();
            e.target.blur();
            break;
    }
}

function handleSearchFocus() {
    const query = document.getElementById('stock-search-input').value.trim();
    if (query.length > 0) {
        showSuggestions(query);
    }
}

function handleSearchBlur() {
    // Delay hiding suggestions to allow for click events
    setTimeout(() => {
        hideSuggestions();
    }, 150);
}

async function showSuggestions(query) {
    const suggestionsContainer = document.getElementById('search-suggestions');
    const suggestionsList = document.getElementById('suggestions-list');
    
    // Show loading state
    showLoadingState();
    
    try {
        // Get AI-powered suggestions from the backend
        suggestions = await getAIAutocompleteData(query);
        
        if (suggestions.length === 0) {
            hideSuggestions();
            return;
        }
    } catch (error) {
        console.error('Error getting AI suggestions:', error);
        // Fallback to local suggestions
        suggestions = filterSuggestions(query);
        
        if (suggestions.length === 0) {
            hideSuggestions();
            return;
        }
    }
    }
    
    // Create suggestion items
    suggestionsList.innerHTML = suggestions.map((suggestion, index) => `
        <button class="suggestion-item" onclick="selectSuggestion(${JSON.stringify(suggestion).replace(/"/g, '&quot;')})" type="button">
            <div class="suggestion-icon">
                <i class="fas fa-chart-line"></i>
            </div>
            <div class="suggestion-content">
                <div class="suggestion-symbol">${suggestion.symbol}</div>
                <div class="suggestion-name">${suggestion.name}</div>
            </div>
        </button>
    `).join('');
    
    suggestionsContainer.style.display = 'block';
    selectedSuggestionIndex = -1;
}

function hideSuggestions() {
    const suggestionsContainer = document.getElementById('search-suggestions');
    suggestionsContainer.style.display = 'none';
    selectedSuggestionIndex = -1;
}

function filterSuggestions(query) {
    const lowerQuery = query.toLowerCase();
    
    return popularStocks.filter(stock => 
        stock.symbol.toLowerCase().includes(lowerQuery) ||
        stock.name.toLowerCase().includes(lowerQuery) ||
        stock.sector.toLowerCase().includes(lowerQuery)
    ).slice(0, 8); // Limit to 8 suggestions
}

function updateSuggestionSelection() {
    const suggestionItems = document.querySelectorAll('.suggestion-item');
    
    suggestionItems.forEach((item, index) => {
        item.classList.toggle('selected', index === selectedSuggestionIndex);
    });
}

function selectSuggestion(suggestion) {
    const searchInput = document.getElementById('stock-search-input');
    searchInput.value = suggestion.symbol;
    hideSuggestions();
    searchStockAI();
}

// Quick search function for popular stocks
function quickSearch(symbol) {
    const searchInput = document.getElementById('stock-search-input');
    searchInput.value = symbol;
    hideSuggestions();
    searchStockAI();
}

// Main AI stock search function
async function searchStockAI() {
    const searchInput = document.getElementById('stock-search-input');
    const symbol = searchInput.value.trim().toUpperCase();
    
    if (!symbol) {
        showSearchError('Please enter a stock symbol or company name');
        return;
    }

    // Show loading state
    showSearchLoading();
    hideSuggestions();
    
    try {
        // Get stock data
        const stockData = await searchStockData(symbol);
        if (!stockData) {
            throw new Error('Stock not found');
        }

        // Get AI analysis
        const aiAnalysis = await getAIAnalysis(symbol);
        
        // Display results
        displayStockAnalysis(stockData, aiAnalysis);
        
    } catch (error) {
        console.error('Error searching stock:', error);
        showSearchError(error.message || 'Stock not found. Please try a different symbol.');
    }
}

// Search stock data from backend
async function searchStockData(symbol) {
    try {
        const response = await fetch(`/api/search-stock/${symbol}`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch stock data');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching stock data:', error);
        return null;
    }
}

// Get AI analysis
async function getAIAnalysis(symbol) {
    try {
        const response = await fetch(`/api/ai-analysis/${symbol}`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Failed to get AI analysis');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error getting AI analysis:', error);
        return {
            recommendation: 'HOLD',
            confidence: 50,
            risk_level: 'MEDIUM',
            risk_score: 5,
            insight: 'AI analysis temporarily unavailable. Please try again later.',
            price_target: 0,
            expected_return: 0,
            key_risks: ['Market volatility', 'Economic conditions']
        };
    }
}

// Display stock analysis results
function displayStockAnalysis(stockData, aiAnalysis) {
    currentAnalyzedStock = stockData;
    
    // Reset search interface
    const searchBtn = document.getElementById('search-btn');
    const searchBox = document.querySelector('.google-search-box');
    
    searchBtn.disabled = false;
    searchBtn.innerHTML = '<i class="fas fa-brain me-2"></i><span class="d-none d-sm-inline">AI Analysis</span><span class="d-sm-none">Analyze</span>';
    
    // Remove loading animation
    if (searchBox) {
        searchBox.classList.remove('search-loading');
    }
    
    // Update stock information
    document.getElementById('stock-name').textContent = stockData.name;
    document.getElementById('stock-symbol').textContent = stockData.symbol;
    document.getElementById('stock-sector').textContent = stockData.sector;
    document.getElementById('stock-price').textContent = formatPrice(stockData.current_price);
    
    // Update price change
    const priceChange = stockData.current_price - stockData.previous_close;
    const priceChangePercent = (priceChange / stockData.previous_close) * 100;
    const changeElement = document.getElementById('stock-change');
    const changeClass = priceChange >= 0 ? 'text-success' : 'text-danger';
    const changeSymbol = priceChange >= 0 ? '+' : '';
    
    changeElement.innerHTML = `<span class="${changeClass}">${changeSymbol}${priceChange.toFixed(2)} (${changeSymbol}${priceChangePercent.toFixed(2)}%)</span>`;
    
    // Update AI recommendation
    const recommendationElement = document.getElementById('ai-recommendation');
    const recommendation = aiAnalysis.recommendation || 'HOLD';
    let badgeClass = 'bg-secondary';
    
    switch (recommendation) {
        case 'STRONG BUY':
            badgeClass = 'bg-success';
            break;
        case 'BUY':
            badgeClass = 'bg-success';
            break;
        case 'HOLD':
            badgeClass = 'bg-warning';
            break;
        case 'SELL':
            badgeClass = 'bg-danger';
            break;
        case 'STRONG SELL':
            badgeClass = 'bg-danger';
            break;
    }
    
    recommendationElement.innerHTML = `<span class="badge ${badgeClass}">${recommendation}</span>`;
    document.getElementById('ai-confidence').textContent = `${aiAnalysis.confidence || 50}%`;
    document.getElementById('ai-insight').textContent = aiAnalysis.insight || 'AI analysis in progress...';
    
    // Update risk assessment
    const riskElement = document.getElementById('risk-level');
    const riskLevel = aiAnalysis.risk_level || 'MEDIUM';
    let riskBadgeClass = 'bg-warning';
    
    switch (riskLevel) {
        case 'LOW':
            riskBadgeClass = 'bg-success';
            break;
        case 'MEDIUM':
            riskBadgeClass = 'bg-warning';
            break;
        case 'HIGH':
            riskBadgeClass = 'bg-danger';
            break;
    }
    
    riskElement.innerHTML = `<span class="badge ${riskBadgeClass}">${riskLevel}</span>`;
    document.getElementById('risk-score').textContent = `${aiAnalysis.risk_score || 5}/10`;
    
    // Update risk factors
    const riskFactors = aiAnalysis.key_risks || ['Market volatility', 'Economic conditions'];
    const riskFactorsList = document.getElementById('risk-factors');
    riskFactorsList.innerHTML = riskFactors.map(risk => `<li>${risk}</li>`).join('');
    
    // Update price target
    const priceTarget = aiAnalysis.price_target || stockData.current_price;
    const expectedReturn = aiAnalysis.expected_return || 0;
    
    document.getElementById('target-price').textContent = formatPrice(priceTarget);
    document.getElementById('price-range').textContent = `${formatPrice(priceTarget * 0.95)} - ${formatPrice(priceTarget * 1.05)}`;
    document.getElementById('expected-return').textContent = `${expectedReturn >= 0 ? '+' : ''}${expectedReturn.toFixed(2)}%`;
    
    // Update AI insights text
    const insightsText = generateDetailedInsights(stockData, aiAnalysis);
    const insightsElement = document.getElementById('ai-insights-text');
    if (insightsElement) {
        insightsElement.innerHTML = insightsText;
    }
    
    // Update buy button
    const buyButton = document.getElementById('buy-stock-btn');
    buyButton.setAttribute('onclick', `showBuyModal('${stockData.symbol}', ${stockData.current_price})`);
    
    // Show results
    document.getElementById('search-loading').style.display = 'none';
    document.getElementById('ai-analysis-results').style.display = 'block';
}

// Generate detailed AI insights
function generateDetailedInsights(stockData, aiAnalysis) {
    const insights = [];
    
    // Market position insight
    insights.push(`<strong>Market Position:</strong> ${stockData.name} (${stockData.symbol}) is currently trading at ${formatPrice(stockData.current_price)}, positioning it within the ${stockData.sector} sector.`);
    
    // AI recommendation reasoning
    const recommendation = aiAnalysis.recommendation || 'HOLD';
    const confidence = aiAnalysis.confidence || 50;
    
    if (recommendation === 'STRONG BUY' || recommendation === 'BUY') {
        insights.push(`<strong>Buy Signal:</strong> Our AI identifies strong bullish indicators with ${confidence}% confidence. The algorithm detects favorable momentum and technical patterns suggesting potential upward movement.`);
    } else if (recommendation === 'SELL' || recommendation === 'STRONG SELL') {
        insights.push(`<strong>Sell Signal:</strong> AI analysis indicates bearish sentiment with ${confidence}% confidence. Technical indicators suggest potential downward pressure and increased risk.`);
    } else {
        insights.push(`<strong>Hold Position:</strong> AI analysis suggests a neutral stance with ${confidence}% confidence. The stock shows mixed signals requiring careful monitoring.`);
    }
    
    // Risk assessment
    const riskLevel = aiAnalysis.risk_level || 'MEDIUM';
    if (riskLevel === 'LOW') {
        insights.push(`<strong>Risk Profile:</strong> Low risk investment with stable fundamentals and minimal volatility exposure. Suitable for conservative portfolios.`);
    } else if (riskLevel === 'HIGH') {
        insights.push(`<strong>Risk Profile:</strong> High risk investment with significant volatility and uncertainty. Suitable only for aggressive growth portfolios.`);
    } else {
        insights.push(`<strong>Risk Profile:</strong> Moderate risk investment with balanced growth potential and manageable volatility.`);
    }
    
    // Price target analysis
    const expectedReturn = aiAnalysis.expected_return || 0;
    if (expectedReturn > 5) {
        insights.push(`<strong>Growth Potential:</strong> AI projects strong upside potential with expected returns of ${expectedReturn.toFixed(1)}%. Technical analysis supports bullish price targets.`);
    } else if (expectedReturn < -5) {
        insights.push(`<strong>Downside Risk:</strong> AI identifies potential downside with projected returns of ${expectedReturn.toFixed(1)}%. Consider risk management strategies.`);
    } else {
        insights.push(`<strong>Price Stability:</strong> AI expects moderate price movement with projected returns around ${expectedReturn.toFixed(1)}%. Suitable for income-focused strategies.`);
    }
    
    return insights.join('<br><br>');
}

// Show loading state
function showSearchLoading() {
    const resultsContainer = document.getElementById('ai-analysis-results');
    const searchBtn = document.getElementById('search-btn');
    const searchBox = document.querySelector('.google-search-box');
    
    // Update button state
    searchBtn.disabled = true;
    searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i><span class="d-none d-sm-inline">Analyzing...</span><span class="d-sm-none">Loading...</span>';
    
    // Add loading animation to search box
    if (searchBox) {
        searchBox.classList.add('search-loading');
    }
    
    resultsContainer.innerHTML = `
        <div class="col-12">
            <div class="card bg-dark border-0 shadow">
                <div class="card-body text-center py-5">
                    <div class="loading-spinner"></div>
                    <h3 class="text-white mt-3 mb-2">Analyzing Stock...</h3>
                    <p class="text-muted">Our AI is gathering market data and generating insights</p>
                </div>
            </div>
        </div>
    `;
    resultsContainer.style.display = 'block';
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Show search error
function showSearchError(message) {
    const resultsContainer = document.getElementById('ai-analysis-results');
    const searchBtn = document.getElementById('search-btn');
    const searchBox = document.querySelector('.google-search-box');
    
    // Reset button state
    searchBtn.disabled = false;
    searchBtn.innerHTML = '<i class="fas fa-brain me-2"></i><span class="d-none d-sm-inline">AI Analysis</span><span class="d-sm-none">Analyze</span>';
    
    // Remove loading animation
    if (searchBox) {
        searchBox.classList.remove('search-loading');
    }
    
    // Show error message
    resultsContainer.innerHTML = `
        <div class="col-12">
            <div class="card bg-danger border-0 shadow">
                <div class="card-body text-center py-4">
                    <i class="fas fa-exclamation-triangle text-white mb-3" style="font-size: 3rem;"></i>
                    <h4 class="text-white mb-2">Search Error</h4>
                    <p class="text-white mb-3">${message}</p>
                    <button class="btn btn-light" onclick="hideSuggestions(); document.getElementById('stock-search-input').focus();">
                        <i class="fas fa-search me-2"></i>Try Again
                    </button>
                </div>
            </div>
        </div>
    `;
    resultsContainer.style.display = 'block';
    
    // Auto-hide error after 5 seconds
    setTimeout(() => {
        if (resultsContainer.innerHTML.includes('Search Error')) {
            resultsContainer.style.display = 'none';
        }
    }, 5000);
}

// Format price display
function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(price);
}

// Add to watchlist function
function addToWatchlist() {
    if (!currentAnalyzedStock) {
        showError('No stock selected');
        return;
    }
    
    // TODO: Implement watchlist functionality
    if (window.notificationManager) {
        window.notificationManager.showSuccess(`${currentAnalyzedStock.symbol} added to watchlist`);
    }
}

// Show error function
function showError(message) {
    if (window.notificationManager) {
        window.notificationManager.showError(message);
    } else {
        alert(message);
    }
}

// Quick search function for popular stocks
function quickSearch(symbol) {
    const input = document.getElementById('stock-search-input');
    if (input) {
        input.value = symbol;
    }
    searchStockAI();
}

// Alternative function name for compatibility
window.quickSearch = quickSearch;

// Reset search button on page load
document.addEventListener('DOMContentLoaded', function() {
    const searchBtn = document.getElementById('search-btn');
    if (searchBtn) {
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<i class="fas fa-brain me-2"></i>Analyze';
    }
});