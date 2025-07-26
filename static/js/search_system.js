/**
 * Advanced Search System with Fuzzy Matching and Autocomplete
 * Handles global search, suggestions, and Redis caching
 */

const SearchSystem = {
    // Configuration
    config: {
        debounceMs: 300,
        maxSuggestions: 8,
        minQueryLength: 1,
        cacheExpiry: 300000, // 5 minutes
        apiEndpoints: {
            suggestions: '/api/search/suggestions',
            search: '/api/stock-analysis',
            autocomplete: '/api/search/autocomplete'
        }
    },
    
    // State management
    state: {
        activeInput: null,
        suggestions: [],
        selectedIndex: -1,
        isLoading: false,
        cache: new Map()
    },
    
    // Initialize search system
    init() {
        this.initSearchInputs();
        this.initKeyboardNavigation();
        this.initClickHandlers();
        this.preloadPopularStocks();
        
        console.log('Search System initialized');
    },
    
    // Initialize search input fields
    initSearchInputs() {
        const globalInput = document.getElementById('global-search-input');
        const mobileInput = document.getElementById('mobile-search-input');
        
        if (globalInput) {
            this.setupSearchInput(globalInput, 'global');
        }
        
        if (mobileInput) {
            this.setupSearchInput(mobileInput, 'mobile');
        }
    },
    
    setupSearchInput(input, type) {
        const debouncedSearch = SaaSApp.debounce(
            (query) => this.handleSearch(query, input, type),
            this.config.debounceMs
        );
        
        // Input event listener
        input.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            
            if (query.length >= this.config.minQueryLength) {
                debouncedSearch(query);
            } else {
                this.hideSuggestions();
            }
        });
        
        // Focus and blur events
        input.addEventListener('focus', (e) => {
            this.state.activeInput = input;
            const query = e.target.value.trim();
            
            if (query.length >= this.config.minQueryLength) {
                this.handleSearch(query, input, type);
            } else {
                this.showPopularStocks(input);
            }
        });
        
        input.addEventListener('blur', (e) => {
            // Delay hiding to allow for suggestion clicks
            setTimeout(() => {
                if (this.state.activeInput === input) {
                    this.hideSuggestions();
                }
            }, 150);
        });
        
        // Form submission
        const form = input.closest('form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const query = input.value.trim();
                if (query) {
                    this.performSearch(query);
                }
            });
        }
    },
    
    // Handle search with fuzzy matching
    async handleSearch(query, input, type) {
        if (!query || query.length < this.config.minQueryLength) {
            this.hideSuggestions();
            return;
        }
        
        // Check cache first
        const cacheKey = `search_${query.toLowerCase()}`;
        const cached = this.getCached(cacheKey);
        
        if (cached) {
            this.displaySuggestions(cached, input);
            return;
        }
        
        // Show loading state
        this.setLoading(true);
        
        try {
            const response = await fetch(`${this.config.apiEndpoints.suggestions}?q=${encodeURIComponent(query)}&limit=${this.config.maxSuggestions}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            const suggestions = this.processSuggestions(data.suggestions || [], query);
            
            // Cache results
            this.setCached(cacheKey, suggestions);
            
            // Display suggestions
            this.displaySuggestions(suggestions, input);
            
        } catch (error) {
            console.error('Search error:', error);
            this.showErrorSuggestions(input);
        } finally {
            this.setLoading(false);
        }
    },
    
    // Process and enhance suggestions with fuzzy matching
    processSuggestions(suggestions, query) {
        const processed = suggestions.map(item => ({
            ...item,
            relevanceScore: this.calculateRelevance(item, query),
            matchType: this.getMatchType(item, query),
            highlightedSymbol: this.highlightMatch(item.symbol, query),
            highlightedName: this.highlightMatch(item.name, query)
        }));
        
        // Sort by relevance score
        return processed.sort((a, b) => b.relevanceScore - a.relevanceScore);
    },
    
    // Calculate relevance score for fuzzy matching
    calculateRelevance(item, query) {
        const queryLower = query.toLowerCase();
        const symbolLower = item.symbol.toLowerCase();
        const nameLower = item.name.toLowerCase();
        
        let score = 0;
        
        // Exact matches get highest score
        if (symbolLower === queryLower) score += 100;
        if (nameLower === queryLower) score += 90;
        
        // Starts with matches
        if (symbolLower.startsWith(queryLower)) score += 80;
        if (nameLower.startsWith(queryLower)) score += 70;
        
        // Contains matches
        if (symbolLower.includes(queryLower)) score += 50;
        if (nameLower.includes(queryLower)) score += 40;
        
        // Word boundary matches
        const words = nameLower.split(' ');
        words.forEach(word => {
            if (word.startsWith(queryLower)) score += 30;
            if (word.includes(queryLower)) score += 20;
        });
        
        // Fuzzy matching for typos (simple implementation)
        if (this.fuzzyMatch(symbolLower, queryLower)) score += 25;
        if (this.fuzzyMatch(nameLower, queryLower)) score += 15;
        
        // Boost popular stocks
        if (this.isPopularStock(item.symbol)) score += 10;
        
        return score;
    },
    
    // Simple fuzzy matching for typo tolerance
    fuzzyMatch(str, pattern) {
        if (pattern.length > str.length) return false;
        
        let patternIdx = 0;
        for (let i = 0; i < str.length && patternIdx < pattern.length; i++) {
            if (str[i] === pattern[patternIdx]) {
                patternIdx++;
            }
        }
        
        return patternIdx === pattern.length;
    },
    
    // Determine match type for display
    getMatchType(item, query) {
        const queryLower = query.toLowerCase();
        const symbolLower = item.symbol.toLowerCase();
        const nameLower = item.name.toLowerCase();
        
        if (symbolLower === queryLower || nameLower === queryLower) return 'exact';
        if (symbolLower.startsWith(queryLower) || nameLower.startsWith(queryLower)) return 'starts';
        if (symbolLower.includes(queryLower) || nameLower.includes(queryLower)) return 'contains';
        return 'fuzzy';
    },
    
    // Highlight matching text
    highlightMatch(text, query) {
        if (!query || !text) return text;
        
        const queryLower = query.toLowerCase();
        const textLower = text.toLowerCase();
        const index = textLower.indexOf(queryLower);
        
        if (index === -1) return text;
        
        return text.substring(0, index) +
               `<mark class="search-highlight">${text.substring(index, index + query.length)}</mark>` +
               text.substring(index + query.length);
    },
    
    // Display suggestions dropdown
    displaySuggestions(suggestions, input) {
        const container = this.getSuggestionsContainer(input);
        if (!container) return;
        
        container.innerHTML = '';
        this.state.suggestions = suggestions;
        this.state.selectedIndex = -1;
        
        if (suggestions.length === 0) {
            this.showNoResults(container);
            return;
        }
        
        // Create suggestion items
        suggestions.forEach((suggestion, index) => {
            const item = this.createSuggestionItem(suggestion, index);
            container.appendChild(item);
        });
        
        // Show container
        container.classList.remove('hidden');
        this.positionSuggestions(container, input);
    },
    
    // Create individual suggestion item
    createSuggestionItem(suggestion, index) {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.dataset.index = index;
        
        // Match type indicator
        const matchBadge = this.getMatchTypeBadge(suggestion.matchType);
        
        // Price change indicator
        const priceChange = suggestion.change ? this.formatPriceChange(suggestion.change) : '';
        
        item.innerHTML = `
            <div class="suggestion-content">
                <div class="suggestion-header">
                    <div class="suggestion-symbol">${suggestion.highlightedSymbol}</div>
                    ${matchBadge}
                    ${priceChange}
                </div>
                <div class="suggestion-name">${suggestion.highlightedName}</div>
                <div class="suggestion-meta">
                    <span class="sector">${suggestion.sector || 'Unknown Sector'}</span>
                    ${suggestion.price ? `<span class="price">$${suggestion.price}</span>` : ''}
                </div>
            </div>
            <div class="suggestion-action">
                <i class="fas fa-arrow-right"></i>
            </div>
        `;
        
        // Click handler
        item.addEventListener('click', () => {
            this.selectSuggestion(suggestion);
        });
        
        // Hover handler
        item.addEventListener('mouseenter', () => {
            this.state.selectedIndex = index;
            this.updateSelection();
        });
        
        return item;
    },
    
    // Get match type badge
    getMatchTypeBadge(matchType) {
        const badges = {
            exact: '<span class="match-badge exact">Exact</span>',
            starts: '<span class="match-badge starts">Match</span>',
            contains: '<span class="match-badge contains">Contains</span>',
            fuzzy: '<span class="match-badge fuzzy">Similar</span>'
        };
        
        return badges[matchType] || '';
    },
    
    // Format price change
    formatPriceChange(change) {
        const className = change >= 0 ? 'positive' : 'negative';
        const sign = change >= 0 ? '+' : '';
        return `<span class="price-change ${className}">${sign}${change.toFixed(2)}%</span>`;
    },
    
    // Show popular stocks when input is focused but empty
    async showPopularStocks(input) {
        const popular = await this.getPopularStocks();
        this.displaySuggestions(popular, input);
    },
    
    // Get popular stocks
    async getPopularStocks() {
        const cacheKey = 'popular_stocks';
        const cached = this.getCached(cacheKey);
        
        if (cached) return cached;
        
        // Default popular stocks
        const popular = [
            { symbol: 'AAPL', name: 'Apple Inc.', sector: 'Technology', price: 214.40, change: 0.9, matchType: 'popular' },
            { symbol: 'TSLA', name: 'Tesla, Inc.', sector: 'Automotive', price: 436.58, change: 5.1, matchType: 'popular' },
            { symbol: 'NVDA', name: 'NVIDIA Corporation', sector: 'Technology', price: 167.03, change: 3.8, matchType: 'popular' },
            { symbol: 'MSFT', name: 'Microsoft Corporation', sector: 'Technology', price: 427.89, change: -1.2, matchType: 'popular' },
            { symbol: 'GOOGL', name: 'Alphabet Inc.', sector: 'Technology', price: 186.35, change: 2.1, matchType: 'popular' },
            { symbol: 'AMZN', name: 'Amazon.com, Inc.', sector: 'E-commerce', price: 201.20, change: 1.8, matchType: 'popular' }
        ];
        
        this.setCached(cacheKey, popular);
        return popular;
    },
    
    // Check if stock is popular
    isPopularStock(symbol) {
        const popular = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX'];
        return popular.includes(symbol);
    },
    
    // Keyboard navigation
    initKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (!this.state.activeInput) return;
            
            const container = this.getSuggestionsContainer(this.state.activeInput);
            if (!container || container.classList.contains('hidden')) return;
            
            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    this.navigateDown();
                    break;
                    
                case 'ArrowUp':
                    e.preventDefault();
                    this.navigateUp();
                    break;
                    
                case 'Enter':
                    e.preventDefault();
                    this.selectCurrentSuggestion();
                    break;
                    
                case 'Escape':
                    e.preventDefault();
                    this.hideSuggestions();
                    this.state.activeInput.blur();
                    break;
            }
        });
    },
    
    navigateDown() {
        if (this.state.selectedIndex < this.state.suggestions.length - 1) {
            this.state.selectedIndex++;
            this.updateSelection();
        }
    },
    
    navigateUp() {
        if (this.state.selectedIndex > 0) {
            this.state.selectedIndex--;
            this.updateSelection();
        } else if (this.state.selectedIndex === 0) {
            this.state.selectedIndex = -1;
            this.updateSelection();
        }
    },
    
    updateSelection() {
        const container = this.getSuggestionsContainer(this.state.activeInput);
        if (!container) return;
        
        const items = container.querySelectorAll('.suggestion-item');
        items.forEach((item, index) => {
            if (index === this.state.selectedIndex) {
                item.classList.add('selected');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('selected');
            }
        });
    },
    
    selectCurrentSuggestion() {
        if (this.state.selectedIndex >= 0 && this.state.suggestions[this.state.selectedIndex]) {
            this.selectSuggestion(this.state.suggestions[this.state.selectedIndex]);
        } else if (this.state.activeInput.value.trim()) {
            this.performSearch(this.state.activeInput.value.trim());
        }
    },
    
    // Select a suggestion
    selectSuggestion(suggestion) {
        this.hideSuggestions();
        
        // Update input value
        if (this.state.activeInput) {
            this.state.activeInput.value = suggestion.symbol;
        }
        
        // Perform search
        this.performSearch(suggestion.symbol);
        
        // Track selection
        this.trackSuggestionClick(suggestion);
    },
    
    // Perform actual search
    async performSearch(query) {
        // Close mobile menu if open
        SaaSApp.closeMobileMenu();
        
        // Navigate to search page if not already there
        if (window.location.pathname !== '/search') {
            window.location.href = `/search?q=${encodeURIComponent(query)}`;
            return;
        }
        
        // Perform search on current page
        this.setLoading(true);
        
        try {
            const response = await fetch(`${this.config.apiEndpoints.search}?symbol=${encodeURIComponent(query)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            // Display results (assuming there's a results handler)
            if (window.SearchResultsHandler) {
                SearchResultsHandler.displayResults(data, query);
            }
            
            // Track search
            this.trackSearch(query);
            
        } catch (error) {
            console.error('Search error:', error);
            SaaSApp.showToast('Search failed. Please try again.', 'error');
        } finally {
            this.setLoading(false);
        }
    },
    
    // Get suggestions container
    getSuggestionsContainer(input) {
        if (!input) return null;
        
        let container = input.parentElement.querySelector('.search-suggestions');
        
        if (!container) {
            container = document.createElement('div');
            container.className = 'search-suggestions hidden';
            input.parentElement.appendChild(container);
        }
        
        return container;
    },
    
    // Position suggestions dropdown
    positionSuggestions(container, input) {
        const rect = input.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        
        // Position below input
        container.style.top = `${rect.bottom + window.scrollY}px`;
        container.style.left = `${rect.left + window.scrollX}px`;
        container.style.width = `${rect.width}px`;
        
        // Adjust if container goes off screen
        const viewportHeight = window.innerHeight;
        if (rect.bottom + containerRect.height > viewportHeight) {
            // Position above input instead
            container.style.top = `${rect.top + window.scrollY - containerRect.height}px`;
        }
    },
    
    // Hide suggestions
    hideSuggestions() {
        const containers = document.querySelectorAll('.search-suggestions');
        containers.forEach(container => {
            container.classList.add('hidden');
            container.innerHTML = '';
        });
        
        this.state.selectedIndex = -1;
        this.state.suggestions = [];
        this.state.activeInput = null;
    },
    
    // Show no results message
    showNoResults(container) {
        container.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">
                    <i class="fas fa-search"></i>
                </div>
                <div class="no-results-text">No stocks found</div>
                <div class="no-results-suggestion">Try searching by symbol or company name</div>
            </div>
        `;
        container.classList.remove('hidden');
    },
    
    // Show error suggestions
    showErrorSuggestions(input) {
        const container = this.getSuggestionsContainer(input);
        if (!container) return;
        
        container.innerHTML = `
            <div class="error-suggestion">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="error-text">Search temporarily unavailable</div>
                <div class="error-action">
                    <button onclick="this.closest('.search-suggestions').classList.add('hidden')">
                        Try again
                    </button>
                </div>
            </div>
        `;
        container.classList.remove('hidden');
    },
    
    // Loading state management
    setLoading(loading) {
        this.state.isLoading = loading;
        
        // Update search inputs
        document.querySelectorAll('#global-search-input, #mobile-search-input').forEach(input => {
            if (loading) {
                input.classList.add('loading');
            } else {
                input.classList.remove('loading');
            }
        });
    },
    
    // Cache management
    setCached(key, data) {
        this.state.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    },
    
    getCached(key) {
        const cached = this.state.cache.get(key);
        
        if (!cached) return null;
        
        if (Date.now() - cached.timestamp > this.config.cacheExpiry) {
            this.state.cache.delete(key);
            return null;
        }
        
        return cached.data;
    },
    
    // Preload popular stocks
    async preloadPopularStocks() {
        try {
            await this.getPopularStocks();
        } catch (error) {
            console.warn('Failed to preload popular stocks:', error);
        }
    },
    
    // Click handlers
    initClickHandlers() {
        // Close suggestions when clicking outside
        document.addEventListener('click', (e) => {
            const isSearchInput = e.target.matches('#global-search-input, #mobile-search-input');
            const isSearchSuggestion = e.target.closest('.search-suggestions');
            
            if (!isSearchInput && !isSearchSuggestion) {
                this.hideSuggestions();
            }
        });
    },
    
    // Analytics and tracking
    trackSearch(query) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'search', {
                search_term: query
            });
        }
        
        SaaSApp.trackFeatureClick('search');
    },
    
    trackSuggestionClick(suggestion) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'suggestion_click', {
                suggestion_symbol: suggestion.symbol,
                suggestion_type: suggestion.matchType
            });
        }
    }
};

// Export for use in other modules
window.SearchSystem = SearchSystem;