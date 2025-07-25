/**
 * Modern Search JavaScript
 * Enhanced search functionality with autocomplete and real-time results
 */

// Global search variables
let searchTimeout = null;
let autocompleteVisible = false;
let selectedIndex = -1;
let searchResults = [];

// Initialize search functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
    setupSearchEventListeners();
    loadRecentSearches();
    loadStarredStocks();
});

// Initialize search components
function initializeSearch() {
    const globalSearchInput = document.getElementById('global-search-input');
    const mobileSearchInput = document.getElementById('mobile-search-input');
    
    if (globalSearchInput) {
        setupAutocomplete(globalSearchInput, 'global-autocomplete-results');
    }
    
    if (mobileSearchInput) {
        setupAutocomplete(mobileSearchInput, 'mobile-autocomplete-results');
    }
    
    // Handle URL parameters for direct search
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('q');
    if (searchQuery) {
        performSearch(searchQuery);
    }
}

// Setup autocomplete functionality
function setupAutocomplete(inputElement, resultsId) {
    inputElement.addEventListener('input', function(e) {
        const query = e.target.value.trim();
        if (query.length >= 2) {
            handleSearchInput(query, resultsId);
        } else {
            hideAutocomplete(resultsId);
        }
    });
    
    inputElement.addEventListener('keydown', function(e) {
        handleSearchKeyDown(e, resultsId);
    });
    
    inputElement.addEventListener('focus', function(e) {
        const query = e.target.value.trim();
        if (query.length >= 2) {
            handleSearchInput(query, resultsId);
        }
    });
    
    // Hide autocomplete when clicking outside
    document.addEventListener('click', function(e) {
        if (!inputElement.contains(e.target) && !document.getElementById(resultsId).contains(e.target)) {
            hideAutocomplete(resultsId);
        }
    });
}

// Handle search input with debouncing
function handleSearchInput(query, resultsId) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        fetchAutocomplete(query, resultsId);
    }, 200);
}

// Fetch autocomplete suggestions
async function fetchAutocomplete(query, resultsId) {
    try {
        const response = await fetch(`/api/search/autocomplete?q=${encodeURIComponent(query)}`);
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.suggestions) {
                displayAutocomplete(data.suggestions, resultsId);
            }
        }
    } catch (error) {
        console.error('Error fetching autocomplete:', error);
    }
}

// Display autocomplete suggestions
function displayAutocomplete(suggestions, resultsId) {
    const resultsContainer = document.getElementById(resultsId);
    if (!resultsContainer) return;
    
    if (suggestions.length === 0) {
        hideAutocomplete(resultsId);
        return;
    }
    
    const html = suggestions.map((suggestion, index) => `
        <div class="autocomplete-item flex items-center p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
             data-index="${index}" onclick="selectSuggestion('${suggestion.symbol}', '${resultsId}')">
            <div class="flex-shrink-0 w-10 h-10 bg-gradient-to-r from-brand-blue to-brand-purple rounded-lg flex items-center justify-center text-white font-bold text-sm mr-3">
                ${suggestion.symbol.charAt(0)}
            </div>
            <div class="flex-1">
                <div class="font-semibold text-gray-800">${suggestion.symbol}</div>
                <div class="text-sm text-gray-600">${suggestion.company_name}</div>
                ${suggestion.sector ? `<div class="text-xs text-gray-500">${suggestion.sector}</div>` : ''}
            </div>
            <div class="text-right">
                ${suggestion.price ? `<div class="font-medium text-gray-800">$${suggestion.price}</div>` : ''}
                ${suggestion.change ? `<div class="text-sm ${suggestion.change >= 0 ? 'text-green-600' : 'text-red-600'}">${suggestion.change >= 0 ? '+' : ''}${suggestion.change}%</div>` : ''}
            </div>
        </div>
    `).join('');
    
    resultsContainer.innerHTML = html;
    resultsContainer.classList.remove('hidden');
    autocompleteVisible = true;
    selectedIndex = -1;
}

// Hide autocomplete dropdown
function hideAutocomplete(resultsId) {
    const resultsContainer = document.getElementById(resultsId);
    if (resultsContainer) {
        resultsContainer.classList.add('hidden');
        autocompleteVisible = false;
        selectedIndex = -1;
    }
}

// Handle keyboard navigation in search
function handleSearchKeyDown(e, resultsId) {
    const resultsContainer = document.getElementById(resultsId);
    const items = resultsContainer.querySelectorAll('.autocomplete-item');
    
    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            if (autocompleteVisible && items.length > 0) {
                selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
                updateSelection(items);
            }
            break;
            
        case 'ArrowUp':
            e.preventDefault();
            if (autocompleteVisible && items.length > 0) {
                selectedIndex = Math.max(selectedIndex - 1, -1);
                updateSelection(items);
            }
            break;
            
        case 'Enter':
            e.preventDefault();
            if (selectedIndex >= 0 && items[selectedIndex]) {
                const symbol = items[selectedIndex].querySelector('.font-semibold').textContent;
                selectSuggestion(symbol, resultsId);
            } else {
                const query = e.target.value.trim();
                if (query) {
                    performSearch(query);
                }
            }
            break;
            
        case 'Escape':
            hideAutocomplete(resultsId);
            e.target.blur();
            break;
    }
}

// Update visual selection in autocomplete
function updateSelection(items) {
    items.forEach((item, index) => {
        if (index === selectedIndex) {
            item.classList.add('bg-blue-50');
        } else {
            item.classList.remove('bg-blue-50');
        }
    });
}

// Select autocomplete suggestion
function selectSuggestion(symbol, resultsId) {
    hideAutocomplete(resultsId);
    performSearch(symbol);
}

// Perform stock search and analysis
async function performSearch(query) {
    if (!query.trim()) return;
    
    // Show loading state
    showLoadingState();
    
    // Save to recent searches
    saveRecentSearch(query);
    
    try {
        const response = await fetch('/api/stock-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        if (response.ok) {
            const data = await response.json();
            displaySearchResults(data);
        } else {
            const errorData = await response.json();
            displaySearchError(errorData.error || 'Search failed');
        }
    } catch (error) {
        console.error('Search error:', error);
        displaySearchError('Connection error occurred');
    } finally {
        hideLoadingState();
    }
}

// Show loading state
function showLoadingState() {
    const loadingDiv = document.getElementById('loading-state');
    const resultsDiv = document.getElementById('search-results');
    
    if (loadingDiv) loadingDiv.classList.remove('hidden');
    if (resultsDiv) resultsDiv.classList.add('hidden');
}

// Hide loading state
function hideLoadingState() {
    const loadingDiv = document.getElementById('loading-state');
    if (loadingDiv) loadingDiv.classList.add('hidden');
}

// Display search results
function displaySearchResults(data) {
    const resultsContainer = document.getElementById('search-results');
    const analysisContent = document.getElementById('analysis-content');
    
    if (!resultsContainer || !analysisContent) return;
    
    // Generate comprehensive analysis display
    const html = generateAnalysisHTML(data);
    analysisContent.innerHTML = html;
    
    resultsContainer.classList.remove('hidden');
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

// Generate analysis HTML
function generateAnalysisHTML(data) {
    const analysis = data.analysis || data;
    const stockInfo = data.stock_info || data;
    
    return `
        <div class="space-y-6">
            <!-- Stock Header -->
            <div class="flex items-start justify-between bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg">
                <div class="flex items-center gap-4">
                    <div class="w-16 h-16 bg-gradient-to-r from-brand-blue to-brand-purple rounded-xl flex items-center justify-center text-white font-bold text-xl">
                        ${analysis.symbol?.charAt(0) || 'S'}
                    </div>
                    <div>
                        <h2 class="text-2xl font-bold text-gray-800">${analysis.symbol || 'N/A'}</h2>
                        <p class="text-gray-600">${analysis.company_name || 'Company Name'}</p>
                        <div class="flex items-center gap-4 mt-2">
                            <span class="text-3xl font-bold text-gray-800">$${typeof analysis.current_price === 'number' ? analysis.current_price.toFixed(2) : '0.00'}</span>
                            <span class="px-3 py-1 rounded-full text-sm font-medium ${(analysis.day_change || 0) >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                                ${(analysis.day_change || 0) >= 0 ? '+' : ''}${typeof analysis.day_change === 'number' ? analysis.day_change.toFixed(2) : '0.00'}%
                            </span>
                        </div>
                    </div>
                </div>
                <button onclick="toggleStarred('${analysis.symbol}')" class="p-2 text-gray-400 hover:text-yellow-500">
                    <i class="fas fa-star text-xl"></i>
                </button>
            </div>
            
            <!-- AI Recommendation -->
            <div class="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg">
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-10 h-10 bg-gradient-to-r from-brand-blue to-brand-purple rounded-lg flex items-center justify-center">
                        <i class="fas fa-brain text-white"></i>
                    </div>
                    <h3 class="text-xl font-bold text-gray-800">AI Analysis</h3>
                </div>
                <div class="grid md:grid-cols-3 gap-4">
                    <div class="text-center">
                        <div class="text-2xl font-bold ${getRecommendationColor(analysis.recommendation)}">${analysis.recommendation || 'HOLD'}</div>
                        <div class="text-sm text-gray-600">Recommendation</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl font-bold text-blue-600">${analysis.confidence || 75}%</div>
                        <div class="text-sm text-gray-600">Confidence</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl font-bold text-purple-600">$${typeof analysis.target_price === 'number' ? analysis.target_price.toFixed(2) : '0.00'}</div>
                        <div class="text-sm text-gray-600">Target Price</div>
                    </div>
                </div>
                <div class="mt-4 p-4 bg-white rounded-lg">
                    <p class="text-gray-700">${analysis.ai_explanation || 'AI analysis provides comprehensive insights based on market data, technical indicators, and fundamental analysis.'}</p>
                </div>
            </div>
            
            <!-- Key Metrics -->
            <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                ${generateMetricsHTML(analysis)}
            </div>
            
            <!-- Analysis Sections -->
            <div class="grid md:grid-cols-2 gap-6">
                <div class="saas-card">
                    <div class="saas-card-header">
                        <h4 class="saas-card-title">Technical Analysis</h4>
                    </div>
                    <div class="saas-card-content">
                        <div class="space-y-3">
                            <div class="flex justify-between">
                                <span class="text-gray-600">RSI (14)</span>
                                <span class="font-medium">${analysis.rsi || 'N/A'}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Moving Avg (50)</span>
                                <span class="font-medium">$${typeof analysis.ma_50 === 'number' ? analysis.ma_50.toFixed(2) : 'N/A'}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Support Level</span>
                                <span class="font-medium">$${typeof analysis.support_level === 'number' ? analysis.support_level.toFixed(2) : 'N/A'}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Resistance Level</span>
                                <span class="font-medium">$${typeof analysis.resistance_level === 'number' ? analysis.resistance_level.toFixed(2) : 'N/A'}</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="saas-card">
                    <div class="saas-card-header">
                        <h4 class="saas-card-title">Risk Assessment</h4>
                    </div>
                    <div class="saas-card-content">
                        <div class="space-y-3">
                            <div class="flex justify-between">
                                <span class="text-gray-600">Volatility</span>
                                <span class="font-medium">${analysis.volatility || 'Medium'}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Risk Score</span>
                                <span class="font-medium">${analysis.risk_score || '6/10'}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Beta</span>
                                <span class="font-medium">${analysis.beta || 'N/A'}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Sector Risk</span>
                                <span class="font-medium">${analysis.sector_risk || 'Moderate'}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Generate metrics HTML
function generateMetricsHTML(analysis) {
    const metrics = [
        { label: 'Market Cap', value: analysis.market_cap ? `$${analysis.market_cap}B` : 'N/A' },
        { label: 'P/E Ratio', value: analysis.pe_ratio || 'N/A' },
        { label: '52W High', value: analysis.week_52_high ? `$${analysis.week_52_high}` : 'N/A' },
        { label: '52W Low', value: analysis.week_52_low ? `$${analysis.week_52_low}` : 'N/A' }
    ];
    
    return metrics.map(metric => `
        <div class="saas-card text-center">
            <div class="saas-card-content">
                <div class="text-2xl font-bold text-gray-800">${metric.value}</div>
                <div class="text-sm text-gray-600">${metric.label}</div>
            </div>
        </div>
    `).join('');
}

// Get recommendation color class
function getRecommendationColor(recommendation) {
    switch (recommendation) {
        case 'BUY': return 'text-green-600';
        case 'SELL': return 'text-red-600';
        case 'HOLD': return 'text-yellow-600';
        default: return 'text-gray-600';
    }
}

// Display search error
function displaySearchError(errorMessage) {
    const resultsContainer = document.getElementById('search-results');
    const analysisContent = document.getElementById('analysis-content');
    
    if (!resultsContainer || !analysisContent) return;
    
    analysisContent.innerHTML = `
        <div class="text-center py-12">
            <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <i class="fas fa-exclamation-triangle text-red-600 text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-gray-800 mb-2">Search Error</h3>
            <p class="text-gray-600">${errorMessage}</p>
            <button onclick="closeResults()" class="mt-4 saas-btn-secondary">Try Again</button>
        </div>
    `;
    
    resultsContainer.classList.remove('hidden');
}

// Close search results
function closeResults() {
    const resultsContainer = document.getElementById('search-results');
    if (resultsContainer) {
        resultsContainer.classList.add('hidden');
    }
}

// Toggle starred status
function toggleStarred(symbol) {
    // Implementation for starring/unstarring stocks
    console.log('Toggle starred:', symbol);
}

// Save recent search
function saveRecentSearch(query) {
    let recentSearches = JSON.parse(localStorage.getItem('recentSearches') || '[]');
    recentSearches = recentSearches.filter(search => search !== query);
    recentSearches.unshift(query);
    recentSearches = recentSearches.slice(0, 10); // Keep only last 10
    localStorage.setItem('recentSearches', JSON.stringify(recentSearches));
    updateRecentSearchesDisplay();
}

// Load and display recent searches
function loadRecentSearches() {
    updateRecentSearchesDisplay();
}

// Update recent searches display
function updateRecentSearchesDisplay() {
    const container = document.getElementById('recent-searches');
    if (!container) return;
    
    const recentSearches = JSON.parse(localStorage.getItem('recentSearches') || '[]');
    
    if (recentSearches.length === 0) {
        container.innerHTML = '<div class="text-sm text-gray-500 text-center py-4">No recent searches yet</div>';
        return;
    }
    
    container.innerHTML = recentSearches.map(search => `
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer" onclick="performSearch('${search}')">
            <div class="flex items-center gap-3">
                <i class="fas fa-clock text-gray-400"></i>
                <span class="text-gray-800">${search}</span>
            </div>
        </div>
    `).join('');
}

// Load starred stocks
function loadStarredStocks() {
    // Implementation for loading starred stocks
}

// Setup search event listeners
function setupSearchEventListeners() {
    // Global search enter key
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('global-search-input');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });
    
    // Trending stock buttons
    document.querySelectorAll('[onclick^="searchStock"]').forEach(button => {
        button.addEventListener('click', function() {
            const symbol = this.getAttribute('onclick').match(/'([^']+)'/)[1];
            performSearch(symbol);
        });
    });
}

// Export for external use (not as constructor)
window.SearchManager = {
    performSearch,
    closeResults,
    toggleStarred,
    // Helper function for inline onclick calls
    search: performSearch
};