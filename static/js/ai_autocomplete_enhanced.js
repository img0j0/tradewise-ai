/**
 * Enhanced AI-Powered Stock Search Autocomplete
 * Provides intelligent suggestions with real-time market data and AI insights
 */

// Enhanced AI Autocomplete functionality
class AIAutocompleteEngine {
    constructor() {
        this.searchTimeout = null;
        this.selectedSuggestionIndex = -1;
        this.suggestions = [];
        this.currentQuery = '';
        this.isLoading = false;
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    init() {
        this.setupEventListeners();
        this.setupKeyboardNavigation();
        this.setupThemeButtons();
    }
    
    setupEventListeners() {
        const searchInput = document.getElementById('stock-search-input') || 
                           document.getElementById('main-search-input');
        const searchBtn = document.getElementById('search-btn') || 
                         document.querySelector('.chatgpt-search-btn');
        const suggestionsContainer = document.getElementById('search-suggestions');
        
        if (!searchInput || !searchBtn) {
            console.log('Search elements not found, skipping autocomplete setup');
            return;
        }
        
        // Search input events
        searchInput.addEventListener('input', (e) => this.handleSearchInput(e));
        searchInput.addEventListener('focus', (e) => this.handleSearchFocus(e));
        searchInput.addEventListener('blur', (e) => this.handleSearchBlur(e));
        
        // Search button event
        searchBtn.addEventListener('click', () => this.executeSearch());
        
        // Click outside to close suggestions
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.google-search-box')) {
                this.hideSuggestions();
            }
        });
    }
    
    setupKeyboardNavigation() {
        const searchInput = document.getElementById('stock-search-input') || 
                           document.getElementById('main-search-input');
        if (!searchInput) {
            console.log('Search input not found, skipping keyboard navigation setup');
            return;
        }
        
        searchInput.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    this.navigateSuggestions(1);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    this.navigateSuggestions(-1);
                    break;
                case 'Enter':
                    e.preventDefault();
                    this.selectCurrentSuggestion();
                    break;
                case 'Escape':
                    this.hideSuggestions();
                    searchInput.blur();
                    break;
            }
        });
    }
    
    setupThemeButtons() {
        // Load trending themes immediately with default themes
        this.displayTrendingThemes(this.getDefaultThemes());
    }
    
    async handleSearchInput(e) {
        const query = e.target.value.trim();
        this.currentQuery = query;
        
        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        // Debounce search suggestions
        this.searchTimeout = setTimeout(async () => {
            if (query.length > 0) {
                await this.showAISuggestions(query);
            } else {
                this.hideSuggestions();
            }
        }, 200);
    }
    
    async handleSearchFocus(e) {
        const query = e.target.value.trim();
        if (query.length > 0) {
            await this.showAISuggestions(query);
        } else {
            await this.showPopularSuggestions();
        }
    }
    
    handleSearchBlur(e) {
        // Delay hiding suggestions to allow for click events
        setTimeout(() => {
            this.hideSuggestions();
        }, 200);
    }
    
    async showAISuggestions(query) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoadingState();
        
        try {
            // Get AI-powered suggestions with enhanced matching
            const response = await fetch(`/api/search-autocomplete?q=${encodeURIComponent(query)}&limit=8&enhanced=true`, {
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch suggestions');
            }
            
            const data = await response.json();
            this.suggestions = data.suggestions || [];
            
            // Add smart prefill and ranking
            this.suggestions = this.rankSuggestions(this.suggestions, query);
            
            // Display enhanced suggestions
            this.displayEnhancedSuggestions(this.suggestions, query);
            
        } catch (error) {
            console.error('Error getting AI suggestions:', error);
            // Fallback to local suggestions
            this.suggestions = this.getLocalSuggestions(query);
            this.displayEnhancedSuggestions(this.suggestions, query);
        } finally {
            this.isLoading = false;
        }
    }
    
    rankSuggestions(suggestions, query) {
        const lowerQuery = query.toLowerCase();
        
        return suggestions.map(suggestion => {
            let score = 0;
            
            // Exact symbol match gets highest priority
            if (suggestion.symbol.toLowerCase() === lowerQuery) {
                score += 100;
            } else if (suggestion.symbol.toLowerCase().startsWith(lowerQuery)) {
                score += 80;
            } else if (suggestion.symbol.toLowerCase().includes(lowerQuery)) {
                score += 60;
            }
            
            // Company name matching
            if (suggestion.name.toLowerCase().includes(lowerQuery)) {
                score += 40;
            }
            
            // Sector matching
            if (suggestion.sector && suggestion.sector.toLowerCase().includes(lowerQuery)) {
                score += 20;
            }
            
            // Market cap and volume boost popular stocks
            if (suggestion.market_cap > 100000000000) score += 10; // Large cap
            if (suggestion.avg_volume > 10000000) score += 5; // High volume
            
            return { ...suggestion, relevanceScore: score };
        }).sort((a, b) => b.relevanceScore - a.relevanceScore);
    }
    
    displayEnhancedSuggestions(suggestions, query) {
        const suggestionsContainer = document.getElementById('search-suggestions');
        const suggestionsList = document.getElementById('suggestions-list');
        
        if (!suggestions || suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }
        
        const lowerQuery = query.toLowerCase();
        
        suggestionsList.innerHTML = suggestions.map((suggestion, index) => {
            const highlightedSymbol = this.highlightMatch(suggestion.symbol, query);
            const highlightedName = this.highlightMatch(suggestion.name, query);
            
            // Calculate change percentage
            const changePercent = ((suggestion.current_price - suggestion.previous_close) / suggestion.previous_close) * 100;
            const changeClass = changePercent >= 0 ? 'text-success' : 'text-danger';
            const changeIcon = changePercent >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
            
            return `
                <button class="suggestion-item enhanced-suggestion" onclick="selectEnhancedSuggestion(${JSON.stringify(suggestion).replace(/"/g, '&quot;')})" type="button">
                    <div class="suggestion-main">
                        <div class="suggestion-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="suggestion-content">
                            <div class="suggestion-symbol">${highlightedSymbol}</div>
                            <div class="suggestion-name">${highlightedName}</div>
                            <div class="suggestion-sector">${suggestion.sector || 'N/A'}</div>
                        </div>
                    </div>
                    <div class="suggestion-metrics">
                        <div class="price-info">
                            <div class="current-price">$${suggestion.current_price?.toFixed(2) || 'N/A'}</div>
                            <div class="price-change ${changeClass}">
                                <i class="fas ${changeIcon}"></i>
                                ${changePercent.toFixed(2)}%
                            </div>
                        </div>
                        <div class="market-cap">
                            <small class="text-muted">${this.formatMarketCap(suggestion.market_cap)}</small>
                        </div>
                    </div>
                </button>
            `;
        }).join('');
        
        suggestionsContainer.style.display = 'block';
        this.selectedSuggestionIndex = -1;
    }
    
    highlightMatch(text, query) {
        if (!query || !text) return text;
        
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    formatMarketCap(marketCap) {
        if (!marketCap) return 'N/A';
        
        if (marketCap >= 1000000000000) {
            return `$${(marketCap / 1000000000000).toFixed(1)}T`;
        } else if (marketCap >= 1000000000) {
            return `$${(marketCap / 1000000000).toFixed(1)}B`;
        } else if (marketCap >= 1000000) {
            return `$${(marketCap / 1000000).toFixed(1)}M`;
        } else {
            return `$${marketCap.toFixed(0)}`;
        }
    }
    
    async showPopularSuggestions() {
        try {
            const response = await fetch('/api/search-autocomplete?q=&limit=8&popular=true', {
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch popular suggestions');
            }
            
            const data = await response.json();
            this.suggestions = data.suggestions || [];
            
            this.displayPopularSuggestions(this.suggestions);
            
        } catch (error) {
            console.error('Error getting popular suggestions:', error);
            this.suggestions = this.getDefaultPopularStocks();
            this.displayPopularSuggestions(this.suggestions);
        }
    }
    
    displayPopularSuggestions(suggestions) {
        const suggestionsContainer = document.getElementById('search-suggestions');
        const suggestionsList = document.getElementById('suggestions-list');
        
        suggestionsList.innerHTML = 
            '<div class="suggestions-header">' +
                '<i class="fas fa-fire me-2"></i>' +
                '<span>Popular Searches</span>' +
            '</div>' +
            suggestions.map(function(suggestion, index) {
                const changePercent = ((suggestion.current_price - suggestion.previous_close) / suggestion.previous_close) * 100;
                const changeClass = changePercent >= 0 ? 'text-success' : 'text-danger';
                const changeIcon = changePercent >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
                
                return '<button class="suggestion-item popular-suggestion" onclick="selectEnhancedSuggestion(' + 
                    JSON.stringify(suggestion).replace(/"/g, '&quot;') + ')" type="button">' +
                        '<div class="suggestion-main">' +
                            '<div class="suggestion-icon">' +
                                '<i class="fas fa-star"></i>' +
                            '</div>' +
                            '<div class="suggestion-content">' +
                                '<div class="suggestion-symbol">' + suggestion.symbol + '</div>' +
                                '<div class="suggestion-name">' + suggestion.name + '</div>'
                            </div>
                        </div>
                        '<div class="suggestion-metrics">' +
                            '<div class="price-info">' +
                                '<div class="current-price">$' + (suggestion.current_price ? suggestion.current_price.toFixed(2) : 'N/A') + '</div>' +
                                '<div class="price-change ' + changeClass + '">' +
                                    '<i class="fas ' + changeIcon + '"></i>' +
                                    changePercent.toFixed(2) + '%' +
                                '</div>' +
                            '</div>' +
                        '</div>' +
                    '</button>';
            }).join('');
        
        suggestionsContainer.style.display = 'block';
        this.selectedSuggestionIndex = -1;
    }
    
    getLocalSuggestions(query) {
        const popularStocks = [
            { symbol: 'AAPL', name: 'Apple Inc.', sector: 'Technology', current_price: 210.06, previous_close: 210.16, market_cap: 3136816676864 },
            { symbol: 'MSFT', name: 'Microsoft Corporation', sector: 'Technology', current_price: 441.54, previous_close: 441.58, market_cap: 3282738647040 },
            { symbol: 'GOOGL', name: 'Alphabet Inc.', sector: 'Technology', current_price: 180.17, previous_close: 180.17, market_cap: 2217651167744 },
            { symbol: 'AMZN', name: 'Amazon.com Inc.', sector: 'Consumer Discretionary', current_price: 191.76, previous_close: 191.76, market_cap: 2003456671744 },
            { symbol: 'TSLA', name: 'Tesla Inc.', sector: 'Automotive', current_price: 261.77, previous_close: 261.77, market_cap: 835839770624 },
            { symbol: 'NVDA', name: 'NVIDIA Corporation', sector: 'Technology', current_price: 136.93, previous_close: 136.93, market_cap: 3360086392832 },
            { symbol: 'META', name: 'Meta Platforms Inc.', sector: 'Technology', current_price: 591.80, previous_close: 591.80, market_cap: 1503438848000 },
            { symbol: 'NFLX', name: 'Netflix Inc.', sector: 'Entertainment', current_price: 712.73, previous_close: 712.73, market_cap: 306372321280 }
        ];
        
        const lowerQuery = query.toLowerCase();
        return popularStocks.filter(stock => 
            stock.symbol.toLowerCase().includes(lowerQuery) ||
            stock.name.toLowerCase().includes(lowerQuery) ||
            stock.sector.toLowerCase().includes(lowerQuery)
        ).slice(0, 8);
    }
    
    getDefaultPopularStocks() {
        return [
            { symbol: 'AAPL', name: 'Apple Inc.', current_price: 210.06, previous_close: 210.16 },
            { symbol: 'MSFT', name: 'Microsoft Corporation', current_price: 441.54, previous_close: 441.58 },
            { symbol: 'GOOGL', name: 'Alphabet Inc.', current_price: 180.17, previous_close: 180.17 },
            { symbol: 'AMZN', name: 'Amazon.com Inc.', current_price: 191.76, previous_close: 191.76 },
            { symbol: 'TSLA', name: 'Tesla Inc.', current_price: 261.77, previous_close: 261.77 },
            { symbol: 'NVDA', name: 'NVIDIA Corporation', current_price: 136.93, previous_close: 136.93 },
            { symbol: 'META', name: 'Meta Platforms Inc.', current_price: 591.80, previous_close: 591.80 },
            { symbol: 'NFLX', name: 'Netflix Inc.', current_price: 712.73, previous_close: 712.73 }
        ];
    }
    
    async loadTrendingThemes() {
        try {
            const response = await fetch('/api/search-themes', {
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch trending themes');
            }
            
            const data = await response.json();
            this.displayTrendingThemes(data.themes || []);
            
        } catch (error) {
            console.error('Error loading trending themes:', error);
            this.displayTrendingThemes(this.getDefaultThemes());
        }
    }
    
    displayTrendingThemes(themes) {
        const themesContainer = document.getElementById('trending-themes');
        if (!themesContainer) return;
        
        themesContainer.innerHTML = themes.map(function(theme) {
            return '<button class="theme-btn" onclick="searchTheme(\'' + theme.name + '\')" data-theme="' + theme.name + '">' +
                '<i class="fas ' + theme.icon + '"></i>' +
                '<span>' + theme.name + '</span>' +
                '<small class="theme-return ' + (theme.return >= 0 ? 'text-success' : 'text-danger') + '">' +
                    (theme.return >= 0 ? '+' : '') + theme.return.toFixed(1) + '%' +
                '</small>' +
            '</button>';
        }).join('');
    }
    
    getDefaultThemes() {
        return [
            { name: 'AI & Tech', icon: 'fa-robot', return: 15.2 },
            { name: 'Clean Energy', icon: 'fa-leaf', return: 12.8 },
            { name: 'Healthcare', icon: 'fa-heartbeat', return: 8.5 },
            { name: 'Fintech', icon: 'fa-credit-card', return: 11.3 },
            { name: 'Gaming', icon: 'fa-gamepad', return: 7.9 },
            { name: 'Crypto', icon: 'fa-coins', return: -5.2 }
        ];
    }
    
    async showAISuggestions(query) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoadingState();
        
        try {
            const response = await fetch('/api/search-autocomplete?q=' + encodeURIComponent(query) + '&limit=8', {
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error('HTTP error! status: ' + response.status);
            }
            
            const data = await response.json();
            this.suggestions = data.suggestions || [];
            
            if (this.suggestions.length > 0) {
                this.displaySuggestions();
            } else {
                this.hideSuggestions();
            }
            
        } catch (error) {
            console.error('Error fetching AI suggestions:', error);
            // Fallback to popular suggestions
            await this.showPopularSuggestions();
        } finally {
            this.isLoading = false;
        }
    }
    
    async showPopularSuggestions() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoadingState();
        
        try {
            // Get popular suggestions (empty query)
            const response = await fetch('/api/search-autocomplete?q=&limit=8', {
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error('HTTP error! status: ' + response.status);
            }
            
            const data = await response.json();
            this.suggestions = data.suggestions || [];
            
            if (this.suggestions.length > 0) {
                this.displaySuggestions();
            }
            
        } catch (error) {
            console.error('Error fetching popular suggestions:', error);
            this.hideSuggestions();
        } finally {
            this.isLoading = false;
        }
    }
    
    showLoadingState() {
        const suggestionsContainer = document.getElementById('search-suggestions');
        const suggestionsList = document.getElementById('suggestions-list');
        
        if (!suggestionsContainer || !suggestionsList) return;
        
        suggestionsList.innerHTML = 
            '<div class="suggestion-loading">' +
                '<div class="loading-spinner"></div>' +
                '<span>Getting AI suggestions...</span>' +
            '</div>';
        
        suggestionsContainer.style.display = 'block';
    }
    
    displaySuggestions() {
        const suggestionsContainer = document.getElementById('search-suggestions');
        const suggestionsList = document.getElementById('suggestions-list');
        
        if (!suggestionsContainer || !suggestionsList) return;
        
        let suggestionsHTML = '';
        
        this.suggestions.forEach((suggestion, index) => {
            const priceChange = suggestion.price_change_percent || 0;
            const priceChangeClass = priceChange >= 0 ? 'positive' : 'negative';
            const priceChangeSign = priceChange >= 0 ? '+' : '';
            const aiSentiment = suggestion.ai_sentiment || 'Neutral';
            const confidence = suggestion.confidence || 70;
            const suggestionReason = suggestion.suggestion_reason || 'Popular stock';
            
            suggestionsHTML += `
                <div class="suggestion-item" data-index="${index}" onclick="aiAutocomplete.selectSuggestion(${index})">
                    <div class="suggestion-main">
                        <div class="suggestion-symbol">${suggestion.symbol}</div>
                        <div class="suggestion-name">${suggestion.name}</div>
                        <div class="suggestion-sector">${suggestion.sector}</div>
                    </div>
                    <div class="suggestion-ai-data">
                        ${suggestion.current_price ? `<div class="suggestion-price">$${suggestion.current_price.toFixed(2)}</div>` : ''}
                        ${priceChange !== 0 ? `<div class="suggestion-change ${priceChangeClass}">${priceChangeSign}${priceChange.toFixed(1)}%</div>` : ''}
                        <div class="suggestion-sentiment ai-sentiment-${aiSentiment.toLowerCase().replace(/\s+/g, '-')}">${aiSentiment}</div>
                        <div class="suggestion-confidence">AI: ${confidence}%</div>
                    </div>
                    <div class="suggestion-reason">${suggestionReason}</div>
                </div>
            `;
        });
        
        suggestionsList.innerHTML = suggestionsHTML;
        suggestionsContainer.style.display = 'block';
        this.selectedSuggestionIndex = -1;
    }
    
    hideSuggestions() {
        const suggestionsContainer = document.getElementById('search-suggestions');
        if (suggestionsContainer) {
            suggestionsContainer.style.display = 'none';
        }
        this.selectedSuggestionIndex = -1;
    }
    
    navigateSuggestions(direction) {
        const suggestionItems = document.querySelectorAll('.suggestion-item');
        if (suggestionItems.length === 0) return;
        
        this.selectedSuggestionIndex += direction;
        
        if (this.selectedSuggestionIndex < 0) {
            this.selectedSuggestionIndex = suggestionItems.length - 1;
        } else if (this.selectedSuggestionIndex >= suggestionItems.length) {
            this.selectedSuggestionIndex = 0;
        }
        
        // Update visual selection
        suggestionItems.forEach((item, index) => {
            item.classList.toggle('selected', index === this.selectedSuggestionIndex);
        });
    }
    
    selectCurrentSuggestion() {
        if (this.selectedSuggestionIndex >= 0 && this.selectedSuggestionIndex < this.suggestions.length) {
            this.selectSuggestion(this.selectedSuggestionIndex);
        } else {
            this.executeSearch();
        }
    }
    
    selectSuggestion(index) {
        if (index >= 0 && index < this.suggestions.length) {
            const suggestion = this.suggestions[index];
            const searchInput = document.getElementById('stock-search-input');
            
            if (searchInput) {
                searchInput.value = suggestion.symbol;
            }
            
            this.hideSuggestions();
            this.executeSearch();
        }
    }
    
    executeSearch() {
        const searchInput = document.getElementById('stock-search-input');
        const symbol = searchInput ? searchInput.value.trim().toUpperCase() : '';
        
        if (!symbol) {
            this.showError('Please enter a stock symbol or company name');
            return;
        }
        
        // Use existing search function if available
        if (typeof searchStockAI === 'function') {
            searchStockAI();
        } else {
            // Fallback search implementation
            this.performSearch(symbol);
        }
    }
    
    async performSearch(symbol) {
        try {
            this.showSearchLoading();
            
            const response = await fetch(`/api/search-stock/${symbol}`, {
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error('Stock not found');
            }
            
            const stockData = await response.json();
            this.displaySearchResults(stockData);
            
        } catch (error) {
            console.error('Error searching stock:', error);
            this.showError('Stock not found. Please try a different symbol.');
        }
    }
    
    showSearchLoading() {
        const searchBtn = document.getElementById('search-btn');
        if (searchBtn) {
            searchBtn.disabled = true;
            searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Searching...';
        }
    }
    
    displaySearchResults(stockData) {
        // Implementation would depend on existing UI structure
        console.log('Stock data received:', stockData);
        
        const searchBtn = document.getElementById('search-btn');
        if (searchBtn) {
            searchBtn.disabled = false;
            searchBtn.innerHTML = '<i class="fas fa-brain me-2"></i><span class="d-none d-sm-inline">AI Analysis</span><span class="d-sm-none">Analyze</span>';
        }
    }
    
    showError(message) {
        const searchBtn = document.getElementById('search-btn');
        if (searchBtn) {
            searchBtn.disabled = false;
            searchBtn.innerHTML = '<i class="fas fa-brain me-2"></i><span class="d-none d-sm-inline">AI Analysis</span><span class="d-sm-none">Analyze</span>';
        }
        
        // Show error message (implementation depends on notification system)
        console.error(message);
        
        // You could add a notification here
        if (typeof showNotification === 'function') {
            showNotification(message, 'error');
        }
    }
    

    
    // Quick search function for popular stocks
    quickSearch(symbol) {
        const searchInput = document.getElementById('stock-search-input');
        if (searchInput) {
            searchInput.value = symbol;
        }
        
        this.hideSuggestions();
        this.executeSearch();
    }
}

// Initialize the AI Autocomplete Engine
const aiAutocomplete = new AIAutocompleteEngine();

// Export for global access
window.aiAutocomplete = aiAutocomplete;

// Global function for theme buttons
function searchTheme(themeName) {
    console.log('Searching theme:', themeName);
    // Use the existing theme analysis function from ai_stock_search.js
    if (typeof showThemeAnalysis === 'function') {
        showThemeAnalysis(themeName);
    } else {
        // Fallback: navigate to theme analysis in same page
        window.location.hash = 'stocks';
        showSection('stocks');
        // Delay to ensure section is loaded
        setTimeout(() => {
            if (typeof showThemeAnalysis === 'function') {
                showThemeAnalysis(themeName);
            }
        }, 100);
    }
}

// Global function for popular stock buttons
function quickSearch(symbol) {
    console.log('Quick search for:', symbol);
    if (window.aiAutocomplete) {
        window.aiAutocomplete.quickSearch(symbol);
    }
}