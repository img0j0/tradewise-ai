// Mobile Optimization JavaScript - Phase 4
// Mobile-first responsive interactions for TradeWise AI

document.addEventListener('DOMContentLoaded', function() {
    initializeMobileNavigation();
    initializeMobileSearch();
    initializeTouchOptimizations();
    initializeScrollOptimizations();
});

// Mobile Navigation System
function initializeMobileNavigation() {
    const mobileNavToggle = document.getElementById('mobile-nav-toggle');
    const mobileNavMenu = document.getElementById('mobile-nav-menu');
    const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');
    
    if (mobileNavToggle && mobileNavMenu) {
        mobileNavToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            mobileNavMenu.classList.toggle('active');
            
            // Update toggle icon
            const icon = mobileNavToggle.querySelector('i');
            if (mobileNavMenu.classList.contains('active')) {
                icon.className = 'fas fa-times';
            } else {
                icon.className = 'fas fa-bars';
            }
        });
        
        // Close mobile nav when clicking outside
        document.addEventListener('click', (e) => {
            if (!mobileNavMenu.contains(e.target) && !mobileNavToggle.contains(e.target)) {
                mobileNavMenu.classList.remove('active');
                const icon = mobileNavToggle.querySelector('i');
                icon.className = 'fas fa-bars';
            }
        });
        
        // Close mobile nav when clicking links
        mobileNavLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileNavMenu.classList.remove('active');
                const icon = mobileNavToggle.querySelector('i');
                icon.className = 'fas fa-bars';
            });
        });
    }
}

// Mobile Search Modal System
function initializeMobileSearch() {
    const mobileSearchToggle = document.getElementById('mobile-search-toggle');
    const mobileSearchModal = document.getElementById('mobile-search-modal');
    const mobileSearchClose = document.getElementById('mobile-search-close');
    const mobileSearchInput = document.getElementById('mobile-search-input');
    const mobileAutocompleteResults = document.getElementById('mobile-autocomplete-results');
    
    let mobileSearchTimeout;
    
    // Open mobile search modal
    if (mobileSearchToggle && mobileSearchModal) {
        mobileSearchToggle.addEventListener('click', () => {
            mobileSearchModal.classList.add('active');
            setTimeout(() => {
                mobileSearchInput?.focus();
            }, 150);
        });
    }
    
    // Close mobile search modal
    if (mobileSearchClose && mobileSearchModal) {
        mobileSearchClose.addEventListener('click', () => {
            mobileSearchModal.classList.remove('active');
            clearMobileSearchResults();
        });
    }
    
    // Close modal when clicking backdrop
    if (mobileSearchModal) {
        mobileSearchModal.addEventListener('click', (e) => {
            if (e.target === mobileSearchModal) {
                mobileSearchModal.classList.remove('active');
                clearMobileSearchResults();
            }
        });
    }
    
    // Mobile search input with fuzzy autocomplete
    if (mobileSearchInput && mobileAutocompleteResults) {
        mobileSearchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            clearTimeout(mobileSearchTimeout);
            
            if (query.length >= 2) {
                mobileSearchTimeout = setTimeout(() => {
                    fetchMobileSearchSuggestions(query);
                }, 200);
            } else {
                mobileAutocompleteResults.classList.add('hidden');
            }
        });
        
        mobileSearchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = e.target.value.trim();
                if (query) {
                    performMobileSearch(query);
                }
            } else if (e.key === 'Escape') {
                mobileSearchModal.classList.remove('active');
                clearMobileSearchResults();
            }
        });
    }
}

// Fetch mobile search suggestions with fuzzy matching
function fetchMobileSearchSuggestions(query) {
    const resultsDiv = document.getElementById('mobile-autocomplete-results');
    if (!resultsDiv) return;
    
    // Show loading state
    resultsDiv.innerHTML = `
        <div class="p-4 text-center text-gray-500">
            <i class="fas fa-spinner fa-spin mr-2"></i>
            Searching with smart matching...
        </div>
    `;
    resultsDiv.classList.remove('hidden');
    
    fetch(`/api/search/autocomplete-enhanced?q=${encodeURIComponent(query)}&limit=6`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.suggestions && data.suggestions.length > 0) {
                displayMobileSearchSuggestions(data.suggestions);
            } else {
                showMobileSearchNoResults(query);
            }
        })
        .catch(error => {
            console.error('Mobile search error:', error);
            showMobileSearchError();
        });
}

// Display mobile search suggestions
function displayMobileSearchSuggestions(suggestions) {
    const resultsDiv = document.getElementById('mobile-autocomplete-results');
    if (!resultsDiv) return;
    
    const suggestionsHTML = suggestions.map(stock => `
        <div class="mobile-suggestion-item" onclick="selectMobileSearchSuggestion('${stock.symbol}')">
            <div class="flex items-center gap-3 p-3">
                <div class="suggestion-logo">${stock.logo || '📈'}</div>
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="font-semibold text-gray-800 text-sm">${stock.symbol}</span>
                        <span class="text-xs text-gray-600 truncate">${stock.name}</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">${stock.sector}</span>
                        ${stock.match_score ? `<span class="text-xs text-gray-500">${stock.match_score}% match</span>` : ''}
                    </div>
                </div>
                <i class="fas fa-chevron-right text-gray-400 text-xs"></i>
            </div>
        </div>
    `).join('');
    
    resultsDiv.innerHTML = suggestionsHTML;
    resultsDiv.classList.remove('hidden');
}

// Show no results message
function showMobileSearchNoResults(query) {
    const resultsDiv = document.getElementById('mobile-autocomplete-results');
    if (!resultsDiv) return;
    
    resultsDiv.innerHTML = `
        <div class="p-4 text-center">
            <div class="text-gray-500 mb-2">
                <i class="fas fa-search text-2xl mb-2"></i>
                <p class="text-sm">No matches found for "${query}"</p>
            </div>
            <button onclick="performMobileSearch('${query}')" 
                    class="text-xs bg-blue-500 text-white px-3 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                Search anyway
            </button>
        </div>
    `;
}

// Show search error
function showMobileSearchError() {
    const resultsDiv = document.getElementById('mobile-autocomplete-results');
    if (!resultsDiv) return;
    
    resultsDiv.innerHTML = `
        <div class="p-4 text-center text-red-500">
            <i class="fas fa-exclamation-triangle mb-2"></i>
            <p class="text-sm">Search temporarily unavailable</p>
        </div>
    `;
}

// Select mobile search suggestion
function selectMobileSearchSuggestion(symbol) {
    performMobileSearch(symbol);
}

// Perform mobile search
function performMobileSearch(query) {
    window.location.href = `/search?q=${encodeURIComponent(query)}`;
}

// Clear mobile search results
function clearMobileSearchResults() {
    const mobileSearchInput = document.getElementById('mobile-search-input');
    const mobileAutocompleteResults = document.getElementById('mobile-autocomplete-results');
    
    if (mobileSearchInput) {
        mobileSearchInput.value = '';
    }
    
    if (mobileAutocompleteResults) {
        mobileAutocompleteResults.classList.add('hidden');
        mobileAutocompleteResults.innerHTML = '';
    }
}

// Touch optimizations for mobile devices
function initializeTouchOptimizations() {
    // Add touch-friendly hover effects
    const touchElements = document.querySelectorAll('.dashboard-card, .mobile-nav-link, .card-button');
    
    touchElements.forEach(element => {
        element.addEventListener('touchstart', function() {
            this.classList.add('touch-active');
        });
        
        element.addEventListener('touchend', function() {
            setTimeout(() => {
                this.classList.remove('touch-active');
            }, 150);
        });
    });
    
    // Prevent double-tap zoom on buttons
    const buttons = document.querySelectorAll('button, .btn, .card-button');
    buttons.forEach(button => {
        button.addEventListener('touchend', function(e) {
            e.preventDefault();
        });
    });
    
    // Optimize form inputs for mobile
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        // Prevent zoom on focus for iOS
        if (input.type !== 'file') {
            input.addEventListener('focus', function() {
                if (window.innerWidth < 768) {
                    // Temporarily set font-size to 16px to prevent iOS zoom
                    this.style.fontSize = '16px';
                }
            });
            
            input.addEventListener('blur', function() {
                // Restore original font size
                this.style.fontSize = '';
            });
        }
    });
}

// Scroll optimizations for mobile
function initializeScrollOptimizations() {
    // Add momentum scrolling for iOS
    const scrollContainers = document.querySelectorAll('.table-scroll-container, .mobile-autocomplete-results');
    scrollContainers.forEach(container => {
        container.style.webkitOverflowScrolling = 'touch';
    });
    
    // Hide mobile nav on scroll down, show on scroll up
    let lastScrollTop = 0;
    const navbar = document.querySelector('.saas-navbar');
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (window.innerWidth < 768 && navbar) {
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                // Scrolling down - hide navbar
                navbar.style.transform = 'translateY(-100%)';
            } else {
                // Scrolling up - show navbar
                navbar.style.transform = 'translateY(0)';
            }
        }
        
        lastScrollTop = scrollTop;
    });
}

// Keyboard shortcuts that work on mobile
document.addEventListener('keydown', (e) => {
    // Ctrl+K or Cmd+K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        
        if (window.innerWidth < 768) {
            // On mobile, open the search modal
            const mobileSearchToggle = document.getElementById('mobile-search-toggle');
            mobileSearchToggle?.click();
        } else {
            // On desktop, focus the global search
            const globalSearch = document.getElementById('global-search');
            globalSearch?.focus();
        }
    }
    
    // Escape to close mobile modals
    if (e.key === 'Escape') {
        const mobileSearchModal = document.getElementById('mobile-search-modal');
        const mobileNavMenu = document.getElementById('mobile-nav-menu');
        
        if (mobileSearchModal?.classList.contains('active')) {
            mobileSearchModal.classList.remove('active');
            clearMobileSearchResults();
        }
        
        if (mobileNavMenu?.classList.contains('active')) {
            mobileNavMenu.classList.remove('active');
            const mobileNavToggle = document.getElementById('mobile-nav-toggle');
            const icon = mobileNavToggle?.querySelector('i');
            if (icon) icon.className = 'fas fa-bars';
        }
    }
});

// Resize handler for mobile optimizations
window.addEventListener('resize', function() {
    // Close mobile menus when switching to desktop
    if (window.innerWidth >= 768) {
        const mobileSearchModal = document.getElementById('mobile-search-modal');
        const mobileNavMenu = document.getElementById('mobile-nav-menu');
        
        if (mobileSearchModal?.classList.contains('active')) {
            mobileSearchModal.classList.remove('active');
            clearMobileSearchResults();
        }
        
        if (mobileNavMenu?.classList.contains('active')) {
            mobileNavMenu.classList.remove('active');
            const mobileNavToggle = document.getElementById('mobile-nav-toggle');
            const icon = mobileNavToggle?.querySelector('i');
            if (icon) icon.className = 'fas fa-bars';
        }
        
        // Reset navbar transform
        const navbar = document.querySelector('.saas-navbar');
        if (navbar) {
            navbar.style.transform = 'translateY(0)';
        }
    }
});

// Add CSS classes for touch interactions
const mobileOptimizationStyles = `
    <style>
        .touch-active {
            background-color: rgba(29, 53, 87, 0.1) !important;
            transform: scale(0.98);
            transition: all 0.1s ease;
        }
        
        .mobile-suggestion-item {
            cursor: pointer;
            border-bottom: 1px solid #f3f4f6;
            transition: background-color 0.2s ease;
        }
        
        .mobile-suggestion-item:hover,
        .mobile-suggestion-item:active {
            background-color: #f9fafb;
        }
        
        .mobile-suggestion-item:last-child {
            border-bottom: none;
        }
        
        .suggestion-logo {
            font-size: 1.5rem;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f3f4f6;
            border-radius: 8px;
        }
        
        /* Mobile table scroll indicators */
        .table-scroll-container {
            position: relative;
        }
        
        .table-scroll-container::after {
            content: '→';
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: #9ca3af;
            pointer-events: none;
            opacity: 0.7;
        }
        
        @media (min-width: 768px) {
            .table-scroll-container::after {
                display: none;
            }
        }
    </style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', mobileOptimizationStyles);