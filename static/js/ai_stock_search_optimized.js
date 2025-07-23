// Optimized AI Stock Search and Analysis - Full JavaScript Implementation

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

// Initialize search functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
    console.log('Optimized AI stock search loaded');
});

function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.querySelector('.submit-btn');
    
    if (!searchInput) {
        console.log('Search input not found');
        return;
    }
    
    // Add event listeners
    searchInput.addEventListener('input', handleSearchInput);
    searchInput.addEventListener('keydown', handleSearchKeydown);
    
    if (searchBtn) {
        searchBtn.addEventListener('click', function(e) {
            e.preventDefault();
            performSearch();
        });
    }
}

function handleSearchInput(e) {
    const query = e.target.value.trim();
    
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    
    searchTimeout = setTimeout(() => {
        if (query.length > 0) {
            showSuggestions(query);
        } else {
            hideSuggestions();
        }
    }, 150);
}

function handleSearchKeydown(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        performSearch();
    }
}

function showSuggestions(query) {
    const container = document.getElementById('search-suggestions');
    if (!container) return;

    const filtered = popularStocks.filter(stock => 
        stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
        stock.name.toLowerCase().includes(query.toLowerCase())
    );

    if (filtered.length === 0) {
        hideSuggestions();
        return;
    }

    suggestions = filtered;
    container.innerHTML = filtered.map((stock, index) => `
        <div class="suggestion-item" onclick="selectSuggestion('${stock.symbol}')">
            <strong>${stock.symbol}</strong> - ${stock.name}
            <small class="text-muted d-block">${stock.sector}</small>
        </div>
    `).join('');
    
    container.style.display = 'block';
}

function hideSuggestions() {
    const container = document.getElementById('search-suggestions');
    if (container) {
        container.style.display = 'none';
    }
}

function selectSuggestion(symbol) {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = symbol;
    }
    hideSuggestions();
    performSearch();
}

async function performSearch() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;

    const query = searchInput.value.trim();
    if (!query) return;

    console.log('Performing search for:', query);
    
    try {
        // Show loading state
        showLoadingState();
        
        const response = await fetch('/api/stock-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('API response:', data);
        
        if (data.success) {
            // Check if enhanced display is available, use it, otherwise use basic display
            if (typeof displayEnhancedAnalysis === 'function') {
                console.log('Using enhanced display system');
                displayEnhancedAnalysis(data);
            } else {
                console.log('Using basic display system');
                displayResults(data);
            }
        } else {
            showError('Analysis failed: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Search error:', error);
        showError('Search failed: ' + error.message);
    }
}

function showLoadingState() {
    const container = document.getElementById('mainAnalysisContainer');
    if (container) {
        container.innerHTML = `
            <div class="col-12 text-center p-5">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h5>Analyzing Stock...</h5>
                <p class="text-muted">Fetching real-time data and AI insights</p>
            </div>
        `;
    }
}

function displayResults(data) {
    console.log('displayResults called with:', data);
    const container = document.getElementById('mainAnalysisContainer');
    if (!container) {
        console.error('mainAnalysisContainer not found');
        return;
    }

    try {
        // Extract data safely
        const analysis = data.analysis || {};
        const stockInfo = data.stock_info || data;
    
    const price = typeof stockInfo.current_price === 'number' ? stockInfo.current_price.toFixed(2) : '0.00';
    const change = typeof stockInfo.price_change === 'number' ? stockInfo.price_change.toFixed(2) : '0.00';
    const changePercent = typeof stockInfo.price_change_percent === 'number' ? stockInfo.price_change_percent.toFixed(2) : '0.00';
    const recommendation = analysis.recommendation || 'HOLD';
    const confidence = analysis.confidence || 50;
    const companyName = stockInfo.company_name || stockInfo.symbol || 'Unknown Company';

    container.innerHTML = `
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5>${companyName} (${stockInfo.symbol || data.symbol})</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h3 class="mb-0">$${price}</h3>
                            <p class="text-${parseFloat(change) >= 0 ? 'success' : 'danger'} mb-3">
                                ${parseFloat(change) >= 0 ? '+' : ''}${change} (${changePercent}%)
                            </p>
                        </div>
                        <div class="col-md-6">
                            <div class="text-end">
                                <span class="badge bg-${getRecommendationColor(recommendation)} fs-6">
                                    ${recommendation}
                                </span>
                                <p class="small text-muted mb-0">AI Confidence: ${confidence}%</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row mt-4">
                        <div class="col-md-8">
                            <h6>Investment Thesis</h6>
                            <p>${analysis.investment_thesis || 'Comprehensive analysis suggests monitoring market conditions.'}</p>
                            
                            <h6>AI Reasoning</h6>
                            <p>${analysis.ai_reasoning || 'Technical and fundamental analysis indicates current position evaluation.'}</p>
                        </div>
                        <div class="col-md-4">
                            <h6>Key Metrics</h6>
                            <div class="d-flex justify-content-between">
                                <span>Risk Level:</span>
                                <span class="badge bg-${getRiskColor(analysis.risk_level)}">${analysis.risk_level || 'MEDIUM'}</span>
                            </div>
                            <div class="d-flex justify-content-between mt-2">
                                <span>Sentiment:</span>
                                <span>${analysis.market_sentiment || 'NEUTRAL'}</span>
                            </div>
                            <div class="d-flex justify-content-between mt-2">
                                <span>Target Price:</span>
                                <span>${analysis.price_target || 'Current levels'}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    console.log('displayResults completed successfully');
    } catch (error) {
        console.error('Error in displayResults:', error);
        showError('Failed to display analysis results: ' + error.message);
    }
}

function getRecommendationColor(recommendation) {
    switch(recommendation?.toUpperCase()) {
        case 'BUY': case 'STRONG BUY': return 'success';
        case 'SELL': case 'STRONG SELL': return 'danger';
        case 'HOLD': return 'warning';
        default: return 'secondary';
    }
}

function getRiskColor(riskLevel) {
    switch(riskLevel?.toUpperCase()) {
        case 'LOW': return 'success';
        case 'HIGH': return 'danger';
        case 'MEDIUM': return 'warning';
        default: return 'secondary';
    }
}

function showError(message) {
    const container = document.getElementById('mainAnalysisContainer');
    if (container) {
        container.innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger" role="alert">
                    <h5>Analysis Error</h5>
                    <p>${message}</p>
                    <button class="btn btn-outline-danger" onclick="location.reload()">Try Again</button>
                </div>
            </div>
        `;
    }
}

// Desktop quick analysis functions
function analyzeStock(symbol) {
    console.log('Desktop analyzeStock called with:', symbol);
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = symbol;
        performSearch();
    }
}

// Export for global access
window.searchStockAI = performSearch;
window.analyzeStock = analyzeStock;