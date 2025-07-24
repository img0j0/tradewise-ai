// Google-Style AI Stock Search and Analysis - Clean Version
// Fixed all template literal and syntax errors

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
});

function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    
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
            searchStockAI();
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
    }, 300);
}

function handleSearchKeydown(e) {
    const suggestionItems = document.querySelectorAll('.suggestion-item');
    
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
                suggestionItems[selectedSuggestionIndex].click();
            } else {
                searchStockAI();
            }
            break;
        case 'Escape':
            hideSuggestions();
            break;
    }
}

async function showSuggestions(query) {
    const suggestionsContainer = document.getElementById('search-suggestions');
    if (!suggestionsContainer) {
        return;
    }
    
    // Filter suggestions
    suggestions = filterSuggestions(query);
    
    if (suggestions.length === 0) {
        hideSuggestions();
        return;
    }
    
    // Create suggestion items HTML
    const suggestionsHTML = suggestions.map((suggestion, index) => {
        const suggestionStr = JSON.stringify(suggestion).replace(/"/g, '&quot;');
        return `
            <button class="suggestion-item" onclick="selectSuggestion(${suggestionStr})" type="button">
                <div class="suggestion-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                <div class="suggestion-content">
                    <div class="suggestion-symbol">${suggestion.symbol}</div>
                    <div class="suggestion-name">${suggestion.name}</div>
                </div>
            </button>
        `;
    }).join('');
    
    suggestionsContainer.innerHTML = suggestionsHTML;
    suggestionsContainer.style.display = 'block';
    selectedSuggestionIndex = -1;
}

function hideSuggestions() {
    const suggestionsContainer = document.getElementById('search-suggestions');
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
    }
    selectedSuggestionIndex = -1;
}

function filterSuggestions(query) {
    const lowerQuery = query.toLowerCase();
    
    return popularStocks.filter(stock => 
        stock.symbol.toLowerCase().includes(lowerQuery) ||
        stock.name.toLowerCase().includes(lowerQuery) ||
        stock.sector.toLowerCase().includes(lowerQuery)
    ).slice(0, 8);
}

function updateSuggestionSelection() {
    const suggestionItems = document.querySelectorAll('.suggestion-item');
    
    suggestionItems.forEach((item, index) => {
        item.classList.toggle('selected', index === selectedSuggestionIndex);
    });
}

function selectSuggestion(suggestion) {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = suggestion.symbol;
        hideSuggestions();
        searchStockAI(suggestion.symbol);
    }
}

// Main AI stock search function
async function searchStockAI(inputSymbol = null) {
    console.log('Starting stock search...');
    
    let symbol = inputSymbol;
    
    if (!symbol) {
        const searchInput = document.getElementById('search-input');
        if (!searchInput) {
            console.error('Search input not found');
            return;
        }
        symbol = searchInput.value.trim().toUpperCase();
    }
    
    if (!symbol) {
        alert('Please enter a stock symbol');
        return;
    }
    
    hideSuggestions();
    
    try {
        console.log('Fetching stock data for:', symbol);
        const response = await fetch(`/api/stock-analysis?query=${encodeURIComponent(symbol)}`);
        const stockData = await response.json();
        
        if (!stockData || !stockData.success) {
            throw new Error(stockData?.error || 'Stock analysis failed');
        }
        
        // Display results using the existing function from the template
        if (typeof displayResults === 'function') {
            displayResults(stockData);
        } else {
            console.log('Stock data received:', stockData);
            alert(`Analysis complete for ${stockData.symbol}: ${stockData.recommendation}`);
        }
        
    } catch (error) {
        console.error('Search error:', error);
        alert('Stock analysis failed: ' + error.message);
    }
}

// Make functions globally available
window.searchStockAI = searchStockAI;
window.selectSuggestion = selectSuggestion;

console.log('AI Stock Search module loaded successfully');