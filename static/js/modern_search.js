/**
 * Modern Search Component with Autocomplete
 * Provides unified search functionality across the platform
 */

class ModernSearchManager {
    constructor() {
        this.searchInput = null;
        this.dropdown = null;
        this.isDropdownOpen = false;
        this.selectedIndex = -1;
        this.searchResults = [];
        this.searchTimeout = null;
        this.cache = new Map();
        this.isInitialized = false;
        
        // Keyboard shortcuts
        this.shortcuts = {
            'KeyK': { ctrl: true, action: 'focus' },
            'Escape': { action: 'close' },
            'ArrowDown': { action: 'navigate', direction: 1 },
            'ArrowUp': { action: 'navigate', direction: -1 },
            'Enter': { action: 'select' }
        };
    }
    
    init() {
        if (this.isInitialized) return;
        
        this.searchInput = document.getElementById('global-search');
        if (!this.searchInput) {
            console.warn('Search input not found');
            return;
        }
        
        this.createDropdown();
        this.bindEvents();
        this.isInitialized = true;
        
        console.log('Modern Search Manager initialized');
    }
    
    createDropdown() {
        // Create dropdown container
        this.dropdown = document.createElement('div');
        this.dropdown.id = 'search-dropdown';
        this.dropdown.className = 'search-dropdown hidden';
        this.dropdown.innerHTML = `
            <div class="search-dropdown-content">
                <div class="search-results" id="search-results">
                    <!-- Results will be populated here -->
                </div>
                <div class="search-footer">
                    <div class="search-shortcuts">
                        <span class="shortcut"><kbd>↑</kbd><kbd>↓</kbd> Navigate</span>
                        <span class="shortcut"><kbd>Enter</kbd> Select</span>
                        <span class="shortcut"><kbd>Esc</kbd> Close</span>
                    </div>
                </div>
            </div>
        `;
        
        // Insert dropdown after search input
        this.searchInput.parentNode.insertBefore(this.dropdown, this.searchInput.nextSibling);
    }
    
    bindEvents() {
        // Search input events
        this.searchInput.addEventListener('input', (e) => this.handleInput(e));
        this.searchInput.addEventListener('focus', (e) => this.handleFocus(e));
        this.searchInput.addEventListener('blur', (e) => this.handleBlur(e));
        this.searchInput.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleGlobalKeydown(e));
        
        // Click outside to close
        document.addEventListener('click', (e) => this.handleClickOutside(e));
        
        // Dropdown events
        this.dropdown.addEventListener('mousedown', (e) => e.preventDefault()); // Prevent blur
        this.dropdown.addEventListener('click', (e) => this.handleDropdownClick(e));
    }
    
    async handleInput(e) {
        const query = e.target.value.trim();
        
        if (query.length < 1) {
            this.hideDropdown();
            return;
        }
        
        // Debounce search
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.performSearch(query);
        }, 150);
    }
    
    handleFocus(e) {
        const query = e.target.value.trim();
        if (query.length >= 1) {
            this.performSearch(query);
        }
    }
    
    handleBlur(e) {
        // Delay hiding dropdown to allow clicks
        setTimeout(() => this.hideDropdown(), 200);
    }
    
    handleKeydown(e) {
        if (!this.isDropdownOpen) return;
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.navigateDropdown(1);
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.navigateDropdown(-1);
                break;
            case 'Enter':
                e.preventDefault();
                this.selectCurrentResult();
                break;
            case 'Escape':
                e.preventDefault();
                this.hideDropdown();
                this.searchInput.blur();
                break;
        }
    }
    
    handleGlobalKeydown(e) {
        // Ctrl+K to focus search
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            this.focusSearch();
        }
    }
    
    handleClickOutside(e) {
        if (!this.searchInput.contains(e.target) && !this.dropdown.contains(e.target)) {
            this.hideDropdown();
        }
    }
    
    handleDropdownClick(e) {
        const resultItem = e.target.closest('.search-result-item');
        if (resultItem) {
            const symbol = resultItem.dataset.symbol;
            this.selectResult(symbol);
        }
    }
    
    async performSearch(query) {
        // Check cache first
        if (this.cache.has(query)) {
            this.displayResults(this.cache.get(query));
            return;
        }
        
        try {
            this.showLoadingState();
            
            const response = await fetch(`/api/search/autocomplete?q=${encodeURIComponent(query)}`);
            
            if (!response.ok) {
                throw new Error(`Search failed: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.results) {
                this.cache.set(query, data.results);
                this.displayResults(data.results);
            } else {
                this.displayNoResults();
            }
            
        } catch (error) {
            console.error('Search error:', error);
            this.displayError();
        }
    }
    
    displayResults(results) {
        this.searchResults = results;
        this.selectedIndex = -1;
        
        const resultsContainer = document.getElementById('search-results');
        
        if (results.length === 0) {
            this.displayNoResults();
            return;
        }
        
        resultsContainer.innerHTML = results.map((result, index) => `
            <div class="search-result-item" data-symbol="${result.symbol}" data-index="${index}">
                <div class="result-icon">
                    ${result.logo_url ? 
                        `<img src="${result.logo_url}" alt="${result.symbol}" class="company-logo" onerror="this.style.display='none'">` :
                        `<div class="symbol-icon">${result.symbol.charAt(0)}</div>`
                    }
                </div>
                <div class="result-content">
                    <div class="result-header">
                        <span class="symbol">${result.symbol}</span>
                        <span class="exchange">${result.exchange}</span>
                    </div>
                    <div class="company-name">${result.company_name}</div>
                    <div class="sector">${result.sector}</div>
                </div>
                <div class="result-meta">
                    ${result.market_cap ? `<div class="market-cap">$${this.formatMarketCap(result.market_cap)}</div>` : ''}
                    <div class="confidence">${Math.round(result.confidence_score)}% match</div>
                </div>
            </div>
        `).join('');
        
        this.showDropdown();
    }
    
    displayNoResults() {
        const resultsContainer = document.getElementById('search-results');
        resultsContainer.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">
                    <i class="fas fa-search"></i>
                </div>
                <div class="no-results-content">
                    <h4>No results found</h4>
                    <p>Try searching by:</p>
                    <ul>
                        <li>Stock symbol (e.g., "AAPL")</li>
                        <li>Company name (e.g., "Apple")</li>
                        <li>Part of the name (e.g., "Micro" for Microsoft)</li>
                    </ul>
                </div>
            </div>
        `;
        this.showDropdown();
    }
    
    displayError() {
        const resultsContainer = document.getElementById('search-results');
        resultsContainer.innerHTML = `
            <div class="search-error">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="error-content">
                    <h4>Search temporarily unavailable</h4>
                    <p>Please try again in a few moments</p>
                </div>
            </div>
        `;
        this.showDropdown();
    }
    
    showLoadingState() {
        const resultsContainer = document.getElementById('search-results');
        resultsContainer.innerHTML = `
            <div class="search-loading">
                <div class="loading-spinner"></div>
                <div class="loading-text">Searching...</div>
            </div>
        `;
        this.showDropdown();
    }
    
    navigateDropdown(direction) {
        const resultItems = this.dropdown.querySelectorAll('.search-result-item');
        
        if (resultItems.length === 0) return;
        
        // Remove current selection
        if (this.selectedIndex >= 0 && this.selectedIndex < resultItems.length) {
            resultItems[this.selectedIndex].classList.remove('selected');
        }
        
        // Update selection index
        this.selectedIndex += direction;
        
        if (this.selectedIndex < 0) {
            this.selectedIndex = resultItems.length - 1;
        } else if (this.selectedIndex >= resultItems.length) {
            this.selectedIndex = 0;
        }
        
        // Highlight new selection
        resultItems[this.selectedIndex].classList.add('selected');
        
        // Scroll into view
        resultItems[this.selectedIndex].scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
        });
    }
    
    selectCurrentResult() {
        if (this.selectedIndex >= 0 && this.selectedIndex < this.searchResults.length) {
            const result = this.searchResults[this.selectedIndex];
            this.selectResult(result.symbol);
        }
    }
    
    selectResult(symbol) {
        // Navigate to stock analysis
        window.location.href = `/search?symbol=${encodeURIComponent(symbol)}`;
        this.hideDropdown();
    }
    
    showDropdown() {
        this.dropdown.classList.remove('hidden');
        this.isDropdownOpen = true;
    }
    
    hideDropdown() {
        this.dropdown.classList.add('hidden');
        this.isDropdownOpen = false;
        this.selectedIndex = -1;
        
        // Clear selection highlighting
        const resultItems = this.dropdown.querySelectorAll('.search-result-item');
        resultItems.forEach(item => item.classList.remove('selected'));
    }
    
    focusSearch() {
        this.searchInput.focus();
        this.searchInput.select();
    }
    
    formatMarketCap(marketCap) {
        if (marketCap >= 1e12) {
            return (marketCap / 1e12).toFixed(1) + 'T';
        } else if (marketCap >= 1e9) {
            return (marketCap / 1e9).toFixed(1) + 'B';
        } else if (marketCap >= 1e6) {
            return (marketCap / 1e6).toFixed(1) + 'M';
        }
        return marketCap.toString();
    }
    
    // Public API methods
    search(symbol) {
        this.searchInput.value = symbol;
        this.hideDropdown();
        this.selectResult(symbol);
    }
    
    clear() {
        this.searchInput.value = '';
        this.hideDropdown();
    }
    
    destroy() {
        if (this.dropdown) {
            this.dropdown.remove();
        }
        
        clearTimeout(this.searchTimeout);
        this.cache.clear();
        this.isInitialized = false;
    }
}

// Global search manager instance
let modernSearchManager = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    modernSearchManager = new ModernSearchManager();
    modernSearchManager.init();
});

// Export for external use
// Create SearchManager constructor for backward compatibility
function SearchManager() {
    this.search = function(symbol) {
        if (modernSearchManager) {
            modernSearchManager.search(symbol);
        }
    };
    
    this.focus = function() {
        if (modernSearchManager) {
            modernSearchManager.focusSearch();
        }
    };
}

// Also provide both the class and function on window
window.SearchManager = SearchManager;
window.ModernSearchManager = ModernSearchManager;

// Export module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModernSearchManager;
}