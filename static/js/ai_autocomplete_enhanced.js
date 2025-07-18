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
        const searchInput = document.getElementById('stock-search-input');
        const searchBtn = document.getElementById('search-btn');
        const suggestionsContainer = document.getElementById('search-suggestions');
        
        if (!searchInput || !searchBtn) return;
        
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
        const searchInput = document.getElementById('stock-search-input');
        if (!searchInput) return;
        
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
        // Load trending themes
        this.loadTrendingThemes();
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
            // Get AI-powered suggestions
            const response = await fetch(`/api/search-autocomplete?q=${encodeURIComponent(query)}&limit=8`, {
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
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
                throw new Error(`HTTP error! status: ${response.status}`);
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
        
        suggestionsList.innerHTML = `
            <div class="suggestion-loading">
                <div class="loading-spinner"></div>
                <span>Getting AI suggestions...</span>
            </div>
        `;
        
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
    
    async loadTrendingThemes() {
        try {
            const response = await fetch('/api/search-themes', {
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error('Failed to load themes');
            }
            
            const data = await response.json();
            this.displayTrendingThemes(data.themes);
            
        } catch (error) {
            console.error('Error loading trending themes:', error);
        }
    }
    
    displayTrendingThemes(themes) {
        const themesContainer = document.getElementById('trending-themes');
        if (!themesContainer) return;
        
        let themesHTML = '';
        Object.entries(themes).forEach(([key, description]) => {
            themesHTML += `
                <button class="theme-btn" onclick="aiAutocomplete.searchTheme('${key}')">
                    <i class="fas fa-chart-line me-2"></i>
                    ${key}
                </button>
            `;
        });
        
        themesContainer.innerHTML = themesHTML;
    }
    
    async searchTheme(theme) {
        try {
            this.showLoadingState();
            
            const response = await fetch(`/api/search-theme/${encodeURIComponent(theme)}`, {
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error('Failed to load theme suggestions');
            }
            
            const data = await response.json();
            this.suggestions = data.suggestions || [];
            
            if (this.suggestions.length > 0) {
                this.displaySuggestions();
            }
            
        } catch (error) {
            console.error('Error searching theme:', error);
            this.hideSuggestions();
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