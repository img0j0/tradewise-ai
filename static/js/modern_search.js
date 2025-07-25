/**
 * Modern Search JavaScript
 * Handles autocomplete, search functionality, and result display
 */

class ModernSearch {
    constructor() {
        this.autocompleteTimeout = null;
        this.selectedIndex = -1;
        this.suggestions = [];
        this.recentSearches = [];
        this.starredStocks = [];
        
        this.init();
    }
    
    init() {
        this.initEventListeners();
        this.loadUserData();
        this.initTheme();
    }
    
    initEventListeners() {
        const searchInput = document.getElementById('stock-search-input');
        const searchButton = document.getElementById('search-button');
        
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearchInput(e));
            searchInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
            searchInput.addEventListener('focus', () => this.showAutocomplete());
            searchInput.addEventListener('blur', () => this.hideAutocompleteDelayed());
        }
        
        if (searchButton) {
            searchButton.addEventListener('click', () => this.performSearch());
        }
        
        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        
        // User menu
        const userMenuBtn = document.getElementById('user-menu-btn');
        if (userMenuBtn) {
            userMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                // Handle user menu
            });
        }
        
        // Close autocomplete when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#stock-search-input') && !e.target.closest('#autocomplete-dropdown')) {
                this.hideAutocomplete();
            }
        });
    }
    
    initTheme() {
        const isDarkMode = localStorage.getItem('theme') === 'dark';
        const html = document.documentElement;
        const themeIcon = document.getElementById('theme-icon');
        
        if (isDarkMode) {
            html.setAttribute('data-theme', 'dark');
            html.classList.add('dark');
            if (themeIcon) {
                themeIcon.className = 'fas fa-sun';
            }
        } else {
            html.setAttribute('data-theme', 'light');
            html.classList.remove('dark');
            if (themeIcon) {
                themeIcon.className = 'fas fa-moon';
            }
        }
    }
    
    toggleTheme() {
        const isDarkMode = localStorage.getItem('theme') !== 'dark';
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        this.initTheme();
    }
    
    async handleSearchInput(e) {
        const query = e.target.value.trim();
        
        if (this.autocompleteTimeout) {
            clearTimeout(this.autocompleteTimeout);
        }
        
        if (query.length >= 1) {
            this.autocompleteTimeout = setTimeout(() => {
                this.fetchAutocomplete(query);
            }, 300);
        } else {
            this.hideAutocomplete();
        }
    }
    
    handleKeyDown(e) {
        const dropdown = document.getElementById('autocomplete-dropdown');
        
        if (!dropdown || dropdown.classList.contains('hidden')) {
            if (e.key === 'Enter') {
                this.performSearch();
            }
            return;
        }
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, this.suggestions.length - 1);
                this.updateSelection();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection();
                break;
            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0) {
                    this.selectSuggestion(this.suggestions[this.selectedIndex]);
                } else {
                    this.performSearch();
                }
                break;
            case 'Escape':
                this.hideAutocomplete();
                break;
        }
    }
    
    async fetchAutocomplete(query) {
        try {
            const response = await fetch(`/api/search/autocomplete?q=${encodeURIComponent(query)}&limit=8`);
            const data = await response.json();
            
            if (data.success && data.suggestions) {
                this.suggestions = data.suggestions;
                this.displayAutocomplete();
                this.selectedIndex = -1;
            }
        } catch (error) {
            console.error('Autocomplete error:', error);
            // Fallback to basic autocomplete
            this.fallbackAutocomplete(query);
        }
    }
    
    async fallbackAutocomplete(query) {
        try {
            const response = await fetch(`/api/search/autocomplete?q=${encodeURIComponent(query)}&limit=8`);
            const data = await response.json();
            
            if (data.success && data.suggestions) {
                this.suggestions = data.suggestions;
                this.displayAutocomplete();
                this.selectedIndex = -1;
            }
        } catch (error) {
            console.error('Fallback autocomplete error:', error);
        }
    }
    
    displayAutocomplete() {
        const dropdown = document.getElementById('autocomplete-dropdown');
        const resultsContainer = document.getElementById('autocomplete-results');
        
        if (!dropdown || !resultsContainer) return;
        
        if (this.suggestions.length === 0) {
            this.hideAutocomplete();
            return;
        }
        
        resultsContainer.innerHTML = this.suggestions.map((suggestion, index) => `
            <div class="autocomplete-item p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0 ${index === this.selectedIndex ? 'bg-blue-50' : ''}" 
                 data-index="${index}"
                 onclick="window.searchManager.selectSuggestion(${JSON.stringify(suggestion).replace(/"/g, '&quot;')})">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        ${suggestion.logo_url ? 
                            `<img src="${suggestion.logo_url}" alt="${suggestion.symbol}" class="w-8 h-8 rounded-lg object-cover">` :
                            `<div class="w-8 h-8 bg-gradient-to-r from-brand-blue to-brand-purple rounded-lg flex items-center justify-center text-white text-xs font-bold">
                                ${suggestion.symbol.substring(0, 2)}
                            </div>`
                        }
                        <div>
                            <div class="font-semibold text-gray-800">${suggestion.symbol}</div>
                            <div class="text-sm text-gray-600">${suggestion.name}</div>
                            ${suggestion.sector ? `<div class="text-xs text-gray-500">${suggestion.sector}</div>` : ''}
                        </div>
                    </div>
                    <div class="text-right flex flex-col items-end gap-1">
                        <div class="flex items-center gap-2">
                            ${this.getMarketStatusIndicator(suggestion.market_status)}
                            ${suggestion.trend ? `<div class="text-xs ${suggestion.trend === 'up' ? 'status-positive' : suggestion.trend === 'down' ? 'status-negative' : 'status-neutral'}">
                                <i class="fas fa-arrow-${suggestion.trend === 'up' ? 'up' : suggestion.trend === 'down' ? 'down' : 'right'}"></i>
                            </div>` : ''}
                        </div>
                        ${suggestion.match_type ? `<div class="text-xs px-2 py-1 rounded-full ${this.getMatchTypeBadge(suggestion.match_type)}">${this.getMatchTypeLabel(suggestion.match_type)}</div>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
        
        dropdown.classList.remove('hidden');
        this.showAutocomplete();
    }
    
    updateSelection() {
        const items = document.querySelectorAll('.autocomplete-item');
        items.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.classList.add('bg-blue-50');
            } else {
                item.classList.remove('bg-blue-50');
            }
        });
    }
    
    selectSuggestion(suggestion) {
        const searchInput = document.getElementById('stock-search-input');
        if (searchInput) {
            searchInput.value = suggestion.symbol;
        }
        
        // Record selection for ML improvement
        this.recordSelection(searchInput.value, suggestion.symbol);
        
        this.hideAutocomplete();
        this.performSearch();
    }
    
    async recordSelection(query, selectedSymbol) {
        try {
            await fetch('/api/search/record-selection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    symbol: selectedSymbol
                })
            });
        } catch (error) {
            console.log('Could not record selection:', error);
        }
    }
    
    getMarketStatusIndicator(status) {
        const indicators = {
            'open': '<div class="w-2 h-2 bg-green-500 rounded-full" title="Market Open"></div>',
            'closed': '<div class="w-2 h-2 bg-red-500 rounded-full" title="Market Closed"></div>',
            'pre_market': '<div class="w-2 h-2 bg-yellow-500 rounded-full" title="Pre-Market"></div>',
            'after_hours': '<div class="w-2 h-2 bg-orange-500 rounded-full" title="After Hours"></div>',
            'unknown': '<div class="w-2 h-2 bg-gray-400 rounded-full" title="Unknown"></div>'
        };
        return indicators[status] || indicators['unknown'];
    }
    
    getMatchTypeBadge(matchType) {
        const badges = {
            'exact_symbol': 'bg-green-100 text-green-800',
            'fuzzy_symbol': 'bg-blue-100 text-blue-800', 
            'fuzzy_company': 'bg-purple-100 text-purple-800',
            'trending': 'bg-yellow-100 text-yellow-800'
        };
        return badges[matchType] || 'bg-gray-100 text-gray-800';
    }
    
    getMatchTypeLabel(matchType) {
        const labels = {
            'exact_symbol': 'Exact',
            'fuzzy_symbol': 'Symbol',
            'fuzzy_company': 'Name',
            'trending': 'Trending'
        };
        return labels[matchType] || 'Match';
    }
    
    showAutocomplete() {
        const dropdown = document.getElementById('autocomplete-dropdown');
        if (dropdown && this.suggestions.length > 0) {
            dropdown.classList.remove('hidden');
        }
    }
    
    hideAutocomplete() {
        const dropdown = document.getElementById('autocomplete-dropdown');
        if (dropdown) {
            dropdown.classList.add('hidden');
        }
    }
    
    hideAutocompleteDelayed() {
        setTimeout(() => this.hideAutocomplete(), 150);
    }
    
    async performSearch() {
        const searchInput = document.getElementById('stock-search-input');
        const query = searchInput ? searchInput.value.trim() : '';
        
        if (!query) {
            this.showError('Please enter a stock symbol or company name');
            return;
        }
        
        this.showLoading();
        this.hideAutocomplete();
        
        try {
            // Add to recent searches
            await this.addToRecentSearches(query);
            
            // Perform analysis
            const response = await fetch('/api/stock-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ symbol: query })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displayResults(data);
            } else {
                this.showError(data.error || 'Analysis failed. Please try again.');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Unable to perform analysis. Please check your connection and try again.');
        } finally {
            this.hideLoading();
        }
    }
    
    showLoading() {
        const loadingState = document.getElementById('loading-state');
        const searchResults = document.getElementById('search-results');
        
        if (loadingState) {
            loadingState.classList.remove('hidden');
        }
        
        if (searchResults) {
            searchResults.classList.add('hidden');
        }
    }
    
    hideLoading() {
        const loadingState = document.getElementById('loading-state');
        if (loadingState) {
            loadingState.classList.add('hidden');
        }
    }
    
    displayResults(data) {
        const searchResults = document.getElementById('search-results');
        const analysisContent = document.getElementById('analysis-content');
        
        if (!searchResults || !analysisContent) return;
        
        const analysis = data.analysis || {};
        const stockInfo = data.stock_info || {};
        
        analysisContent.innerHTML = `
            <div class="space-y-6">
                <!-- Stock Header -->
                <div class="flex items-center justify-between p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
                    <div class="flex items-center gap-4">
                        <div class="w-16 h-16 bg-gradient-to-r from-brand-blue to-brand-purple rounded-2xl flex items-center justify-center text-white text-xl font-bold">
                            ${(stockInfo.symbol || '').substring(0, 2)}
                        </div>
                        <div>
                            <h2 class="text-2xl font-bold text-gray-800">${stockInfo.symbol || 'N/A'}</h2>
                            <p class="text-gray-600">${stockInfo.company_name || 'Company Name'}</p>
                            <p class="text-sm text-gray-500">${stockInfo.sector || 'Unknown Sector'}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-3xl font-bold text-gray-800">
                            $${typeof stockInfo.price === 'number' ? stockInfo.price.toFixed(2) : '0.00'}
                        </div>
                        <div class="text-lg ${(stockInfo.change || 0) >= 0 ? 'status-positive' : 'status-negative'}">
                            ${(stockInfo.change || 0) >= 0 ? '+' : ''}${typeof stockInfo.change === 'number' ? stockInfo.change.toFixed(2) : '0.00'}
                            (${(stockInfo.change_percent || 0) >= 0 ? '+' : ''}${typeof stockInfo.change_percent === 'number' ? stockInfo.change_percent.toFixed(2) : '0.00'}%)
                        </div>
                    </div>
                </div>
                
                <!-- AI Recommendation -->
                <div class="p-6 bg-white border border-gray-200 rounded-xl">
                    <div class="flex items-center gap-3 mb-4">
                        <i class="fas fa-brain text-brand-blue text-xl"></i>
                        <h3 class="text-xl font-semibold text-gray-800">AI Recommendation</h3>
                    </div>
                    <div class="flex items-center gap-4 mb-4">
                        <div class="px-4 py-2 bg-gradient-to-r from-brand-blue to-brand-purple text-white rounded-lg font-semibold text-lg">
                            ${analysis.recommendation || 'HOLD'}
                        </div>
                        <div class="text-gray-600">
                            Confidence: <span class="font-semibold">${analysis.confidence || 65}%</span>
                        </div>
                    </div>
                    <p class="text-gray-700 leading-relaxed">
                        ${analysis.reasoning || 'Comprehensive analysis based on technical indicators, fundamental metrics, and market sentiment.'}
                    </p>
                </div>
                
                <!-- Key Metrics -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="metric-card">
                        <div class="metric-value">${typeof stockInfo.pe_ratio === 'number' ? stockInfo.pe_ratio.toFixed(2) : 'N/A'}</div>
                        <div class="metric-label">P/E Ratio</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${typeof stockInfo.market_cap === 'number' ? this.formatLargeNumber(stockInfo.market_cap) : 'N/A'}</div>
                        <div class="metric-label">Market Cap</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${typeof stockInfo.volume === 'number' ? this.formatLargeNumber(stockInfo.volume) : 'N/A'}</div>
                        <div class="metric-label">Volume</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${typeof stockInfo.beta === 'number' ? stockInfo.beta.toFixed(2) : 'N/A'}</div>
                        <div class="metric-label">Beta</div>
                    </div>
                </div>
                
                <!-- Action Buttons -->
                <div class="flex gap-4 pt-4">
                    <button onclick="window.searchManager.addToWatchlist('${stockInfo.symbol}')" class="saas-button-secondary">
                        <i class="fas fa-star mr-2"></i>
                        Add to Watchlist
                    </button>
                    <button onclick="window.searchManager.handlePremiumFeature('/peer-comparison/${stockInfo.symbol}')" class="saas-button-primary">
                        <i class="fas fa-balance-scale mr-2"></i>
                        Peer Comparison
                        <span class="premium-indicator ml-2">
                            <i class="fas fa-lock premium-lock-icon"></i>
                            Pro
                        </span>
                    </button>
                </div>
            </div>
        `;
        
        searchResults.classList.remove('hidden');
        searchResults.scrollIntoView({ behavior: 'smooth' });
    }
    
    formatLargeNumber(num) {
        if (num >= 1e12) return (num / 1e12).toFixed(1) + 'T';
        if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
        if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
        if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
        return num.toString();
    }
    
    showError(message) {
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg shadow-lg z-50';
        notification.innerHTML = `
            <div class="flex items-center gap-2">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-red-500 hover:text-red-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    async loadUserData() {
        try {
            // Load recent searches
            const recentResponse = await fetch('/api/search/recent');
            if (recentResponse.ok) {
                const recentData = await recentResponse.json();
                if (recentData.success) {
                    this.displayRecentSearches(recentData.recent_searches || []);
                }
            }
            
            // Load starred stocks
            const starredResponse = await fetch('/api/search/starred');
            if (starredResponse.ok) {
                const starredData = await starredResponse.json();
                if (starredData.success) {
                    this.displayStarredStocks(starredData.starred_symbols || []);
                }
            }
        } catch (error) {
            console.log('User data not available');
        }
    }
    
    displayRecentSearches(searches) {
        const container = document.getElementById('recent-searches');
        if (!container) return;
        
        if (searches.length === 0) {
            container.innerHTML = '<div class="text-sm text-gray-500 text-center py-4">No recent searches yet</div>';
            return;
        }
        
        container.innerHTML = searches.map(search => `
            <button onclick="searchStock('${search.symbol}')" class="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 bg-gradient-to-r from-brand-blue to-brand-purple rounded-lg flex items-center justify-center text-white text-xs font-bold">
                        ${search.symbol.substring(0, 2)}
                    </div>
                    <div class="text-left">
                        <div class="font-semibold text-gray-800">${search.symbol}</div>
                        <div class="text-sm text-gray-600">${search.name || 'Unknown'}</div>
                    </div>
                </div>
                <div class="text-xs text-gray-500">
                    ${search.timestamp ? new Date(search.timestamp).toLocaleDateString() : ''}
                </div>
            </button>
        `).join('');
    }
    
    displayStarredStocks(starred) {
        const container = document.getElementById('starred-stocks');
        if (!container) return;
        
        if (starred.length === 0) {
            container.innerHTML = '<div class="text-sm text-gray-500 text-center py-4">No starred stocks yet</div>';
            return;
        }
        
        container.innerHTML = starred.map(stock => `
            <button onclick="searchStock('${stock.symbol}')" class="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 bg-gradient-to-r from-brand-blue to-brand-purple rounded-lg flex items-center justify-center text-white text-xs font-bold">
                        ${stock.symbol.substring(0, 2)}
                    </div>
                    <div class="text-left">
                        <div class="font-semibold text-gray-800">${stock.symbol}</div>
                        <div class="text-sm text-gray-600">${stock.name || 'Unknown'}</div>
                    </div>
                </div>
                <button onclick="event.stopPropagation(); window.searchManager.removeFromStarred('${stock.symbol}')" 
                        class="text-yellow-500 hover:text-yellow-700 p-1">
                    <i class="fas fa-star"></i>
                </button>
            </button>
        `).join('');
    }
    
    async addToRecentSearches(symbol) {
        try {
            await fetch('/api/search/add-recent', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    symbol: symbol.toUpperCase(),
                    name: '',
                    sector: ''
                })
            });
        } catch (error) {
            console.log('Could not add to recent searches');
        }
    }
    
    async addToWatchlist(symbol) {
        try {
            const response = await fetch('/api/search/starred', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ symbol: symbol })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.showSuccess(`${symbol} ${data.action} watchlist`);
                    this.loadUserData(); // Refresh the starred stocks display
                }
            }
        } catch (error) {
            console.error('Could not update watchlist:', error);
        }
    }
    
    async removeFromStarred(symbol) {
        // Toggle starred status (same endpoint)
        await this.addToWatchlist(symbol);
    }
    
    handlePremiumFeature(url) {
        // Check if user has premium access (simplified check)
        const isPremium = false; // This would come from user data
        
        if (!isPremium) {
            this.showUpgradeModal();
            return;
        }
        
        window.location.href = url;
    }
    
    showUpgradeModal() {
        // Create modal or redirect to upgrade page
        window.location.href = '/premium/upgrade';
    }
    
    showSuccess(message) {
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg shadow-lg z-50';
        notification.innerHTML = `
            <div class="flex items-center gap-2">
                <i class="fas fa-check-circle"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-green-500 hover:text-green-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 3000);
    }
}

// Global functions
function searchStock(symbol) {
    const searchInput = document.getElementById('stock-search-input');
    if (searchInput) {
        searchInput.value = symbol;
    }
    window.searchManager.performSearch();
}

function closeResults() {
    const searchResults = document.getElementById('search-results');
    if (searchResults) {
        searchResults.classList.add('hidden');
    }
}

// Initialize search manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.searchManager = new ModernSearch();
});