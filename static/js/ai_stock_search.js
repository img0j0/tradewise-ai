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
    const searchInput = document.getElementById('search-input'); // Fixed ID to match template
    const searchBtn = document.querySelector('.submit-btn');
    const suggestionsContainer = document.getElementById('search-suggestions');
    
    if (!searchInput) {
        console.log('Search input not found, search functionality disabled');
        return;
    }
    
    // Add event listeners
    searchInput.addEventListener('input', handleSearchInput);
    searchInput.addEventListener('keydown', handleSearchKeydown);
    searchInput.addEventListener('focus', handleSearchFocus);
    searchInput.addEventListener('blur', handleSearchBlur);
    
    if (searchBtn) {
        searchBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Search button clicked');
            searchStockAI();
        });
    }
    
    // Click outside to close suggestions
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-container')) {
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
    if (!suggestionsContainer) return;
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
    const searchInput = document.getElementById('search-input'); // Fixed ID
    if (searchInput) {
        const query = searchInput.value.trim();
        if (query.length > 0) {
            showSuggestions(query);
        }
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
    if (!suggestionsContainer) {
        console.log('Search suggestions container not found');
        return;
    }
    
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
    
    // Create suggestion items
    suggestionsContainer.innerHTML = suggestions.map((suggestion, index) => `
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
    ).slice(0, 8); // Limit to 8 suggestions
}

function updateSuggestionSelection() {
    const suggestionItems = document.querySelectorAll('.suggestion-item');
    
    suggestionItems.forEach((item, index) => {
        item.classList.toggle('selected', index === selectedSuggestionIndex);
    });
}

function selectSuggestion(suggestion) {
    const searchInput = document.getElementById('search-input'); // Fixed ID
    if (searchInput) {
        searchInput.value = suggestion.symbol;
        hideSuggestions();
        searchStockAI(suggestion.symbol);
    }
}

// Quick search function for popular stocks
function quickSearch(symbol) {
    const searchInput = document.getElementById('search-input'); // Fixed ID
    if (searchInput) {
        searchInput.value = symbol;
        hideSuggestions();
        searchStockAI(symbol);
    }
}

// Main AI stock search function - completely rewritten for reliability
async function searchStockAI(inputSymbol = null) {
    console.log('🔍 Using enhanced searchStockAI function');
    console.log('searchStockAI called with inputSymbol:', inputSymbol);
    
    let symbol = inputSymbol;
    
    // If no symbol provided, try to get from input
    if (!symbol) {
        // Try multiple ways to get the search input
        let searchInput = document.getElementById('search-input');
        if (!searchInput) {
            console.log('🔍 search-input not found, trying alternative selectors...');
            searchInput = document.querySelector('#search-input') || 
                         document.querySelector('input[type="text"]') || 
                         document.querySelector('.search-input') ||
                         document.querySelector('[placeholder*="stock"]');
        }
        
        if (!searchInput) {
            console.error('🚨 Search input element not found with any selector');
            // Try to prompt user for input as fallback
            symbol = prompt('Please enter a stock symbol (e.g., AAPL, TSLA, NVDA):');
            if (!symbol) {
                alert('No stock symbol provided.');
                return;
            }
        } else {
            console.log('🔍 Found search input element:', searchInput);
            console.log('🔍 Input value before trim:', JSON.stringify(searchInput.value));
            symbol = (searchInput.value || '').trim();
        }
    }
    
    // Clean and validate symbol
    symbol = symbol.toUpperCase().trim();
    console.log('🔍 Final search symbol:', JSON.stringify(symbol));
    
    if (!symbol) {
        alert('Please enter a stock symbol or company name');
        return;
    }

    // Show loading state (but don't use conflicting container)
    console.log('Search loading started...');
    hideSuggestions();
    
    try {
        console.log('Fetching stock data for:', symbol);
        // Get stock data
        const stockData = await searchStockData(symbol);
        console.log('Stock data received:', stockData);
        
        if (!stockData || !stockData.success) {
            throw new Error(stockData?.error || 'Stock analysis failed - please check the symbol and try again');
        }

        // FORCE DISPLAY: Only use the enhanced ChatGPT-style overlay
        console.log('=== FORCING COMPREHENSIVE CHATGPT-STYLE ANALYSIS ===');
        console.log('Stock data structure:', stockData);
        
        // Completely hide and disable old results
        hideOldResults();
        
        // Disable any other display functions and conflicting containers
        const oldSearchResults = document.getElementById('search-results');
        if (oldSearchResults) {
            oldSearchResults.remove(); // Completely remove old container
        }
        
        // Clear any existing content in ai-analysis-results from loading/error functions
        const existingContainer = document.getElementById('ai-analysis-results');
        if (existingContainer) {
            existingContainer.innerHTML = ''; // Clear any basic card content
        }
        
        // ENHANCED AI ANALYSIS DISPLAY
        console.log('=== ENHANCED ANALYSIS DISPLAY ===');
        
        // First, ensure the overlay is visible
        console.log('🔧 Making sure analysis overlay is visible');
        if (typeof showAnalysisOverlay === 'function') {
            showAnalysisOverlay();
        } else {
            // Fallback to direct DOM manipulation
            const overlay = document.getElementById('analysis-overlay');
            if (overlay) {
                overlay.style.display = 'flex';
                console.log('✅ Analysis overlay shown via fallback');
            }
        }
        
        // Check if we're in desktop mode and use appropriate display
        const isDesktopMode = document.querySelector('.desktop-main-layout') !== null;
        console.log('=== DISPLAY MODE DETECTION ===');
        console.log('Desktop mode detected:', isDesktopMode);
        
        if (isDesktopMode) {
            // Use desktop display function directly
            console.log('Using desktop displayResults function');
            if (typeof displayResults === 'function') {
                try {
                    displayResults(stockData);
                    console.log('✅ Desktop display successful');
                } catch (displayError) {
                    console.error('❌ Desktop display error:', displayError);
                    showBasicAnalysis(stockData);
                }
            } else {
                console.error('displayResults function not available');
                showBasicAnalysis(stockData);
            }
        } else {
            // Use enhanced analysis display for mobile
            console.log('Using enhanced analysis display for mobile');
            if (typeof displayEnhancedAnalysis === 'function') {
                try {
                    displayEnhancedAnalysis(stockData);
                    console.log('✅ Enhanced analysis display successful');
                } catch (displayError) {
                console.error('❌ ENHANCED DISPLAY ERROR DETECTED:', displayError);
                console.error('❌ Error type:', displayError.constructor?.name || 'Unknown');
                console.error('❌ Error message:', displayError.message || 'No message');
                console.error('❌ Error stack:', displayError.stack || 'No stack');
                console.error('❌ Full error object:', JSON.stringify(displayError, Object.getOwnPropertyNames(displayError)));
                
                // Check if this is the toFixed error
                if (displayError.message && displayError.message.includes('toFixed')) {
                    console.error('🔢 CONFIRMED: This is the toFixed error we are hunting!');
                    console.error('🔢 Examining stockData for undefined values:');
                    console.error('🔢 - current_price type:', typeof stockData.current_price, 'value:', stockData.current_price);
                    console.error('🔢 - price_change type:', typeof stockData.price_change, 'value:', stockData.price_change);
                    console.error('🔢 - price_change_percent type:', typeof stockData.price_change_percent, 'value:', stockData.price_change_percent);
                }
                
                // Show basic analysis if enhanced fails
                console.log('🔄 Switching to basic analysis fallback...');
                showBasicAnalysis(stockData);
                }
            } else {
                console.error('❌ Enhanced display function not loaded - function type:', typeof displayEnhancedAnalysis);
                console.log('🔄 Using basic analysis fallback...');
                showBasicAnalysis(stockData);
            }
        }
        
    } catch (error) {
        console.error('❌ Stock analysis error:', error);
        alert('Stock analysis failed: ' + error.message);
    }
}

// Basic analysis fallback function
function showBasicAnalysis(stockData) {
    const container = document.getElementById('ai-analysis-results');
    if (!container) return;
    
    container.innerHTML = `
        <div style="padding: 30px; text-align: center; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <h2>${stockData.company_name || stockData.symbol}</h2>
            <div style="font-size: 2rem; font-weight: bold; color: #1f2937; margin: 20px 0;">
                $${(parseFloat(stockData.current_price) || 0).toFixed(2)}
            </div>
            <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <div style="font-weight: bold; margin-bottom: 10px;">AI Recommendation</div>
                <div style="font-size: 1.5rem; color: #059669;">${stockData.recommendation || 'HOLD'}</div>
                <div style="color: #6b7280; margin-top: 5px;">${stockData.confidence || 50}% Confidence</div>
            </div>
            <div style="color: #6b7280; font-size: 0.9rem;">
                Basic analysis mode - Enhanced features loading...
            </div>
        </div>
    `;
    container.style.display = 'block';
    console.log('Basic analysis displayed');
}

// Search stock data from backend using comprehensive API
async function searchStockData(symbol) {
    try {
        console.log(`Fetching comprehensive stock data for: ${symbol}`);
        const response = await fetch('/api/stock-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ query: symbol })
        });
        
        console.log(`Response status: ${response.status}`);
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Stock symbol not found. Please check the symbol and try again.');
            }
            throw new Error(`Failed to fetch stock data (${response.status})`);
        }
        
        const data = await response.json();
        console.log('🔍 COMPREHENSIVE STOCK DATA RECEIVED:', data);
        console.log('🔍 Data structure check:');
        console.log('🔍 - success:', data.success);
        console.log('🔍 - current_price:', data.current_price);
        console.log('🔍 - price_change:', data.price_change);
        console.log('🔍 - price_change_percent:', data.price_change_percent);
        console.log('🔍 - company_name:', data.company_name);
        console.log('🔍 - symbol:', data.symbol);
        console.log('Search results:', [data]);
        
        // Validate response has required data
        if (!data.success) {
            throw new Error(data.error || 'Analysis failed');
        }
        
        return data;
    } catch (error) {
        console.error('🔍 SEARCH DATA ERROR FOUND:', error);
        console.error('🔍 Error type:', error.constructor?.name || 'Unknown');
        console.error('🔍 Error message:', error.message || 'No message available');
        console.error('🔍 Error stack:', error.stack || 'No stack trace available');
        console.error('🔍 Full error object:', JSON.stringify(error, Object.getOwnPropertyNames(error)));
        
        // Check if this is a network error or parsing error
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            console.error('🌐 Network fetch error detected');
        } else if (error.name === 'SyntaxError') {
            console.error('📝 JSON parsing error detected');
        } else if (error.message && error.message.includes('toFixed')) {
            console.error('🔢 toFixed error detected - undefined value passed to number formatting');
        }
        
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

// Generate strategy indicator display for analysis results
function generatePreferenceIndicatorDisplay(stockData) {
    // Check if we have strategy data
    const analysis = stockData.analysis || {};
    const strategy = analysis.strategy_applied;
    const impact = analysis.strategy_impact;
    
    if (!strategy && !impact) {
        return ''; // No personalization to display
    }
    
    const indicators = [];
    const explanations = [];
    
    // Strategy indicator
    if (strategy) {
        indicators.push(`
            <div class="preference-chip" style="background: #3b82f620; border: 1px solid #3b82f660; color: #3b82f6">
                ${strategy.icon} ${strategy.name}
            </div>
        `);
        explanations.push(`Analysis personalized using ${strategy.name}: ${strategy.description}`);
    }
    
    // Strategy impact indicator
    if (impact && impact.changed) {
        indicators.push(`
            <div class="preference-chip" style="background: #10b98120; border: 1px solid #10b98160; color: #10b981">
                🔄 Modified by Strategy
            </div>
        `);
        explanations.push(`Strategy changed recommendation from ${impact.original_recommendation} (${impact.original_confidence}%)`);
    }
    
    // Risk tolerance indicator
    if (prefs.risk_tolerance) {
        const riskIcons = { 'conservative': '🛡️', 'moderate': '⚖️', 'aggressive': '🚀' };
        const riskColors = { 'conservative': '#10b981', 'moderate': '#3b82f6', 'aggressive': '#ef4444' };
        indicators.push(`
            <div class="preference-chip" style="background: ${riskColors[prefs.risk_tolerance]}20; border: 1px solid ${riskColors[prefs.risk_tolerance]}60; color: ${riskColors[prefs.risk_tolerance]}">
                ${riskIcons[prefs.risk_tolerance]} ${prefs.risk_tolerance.charAt(0).toUpperCase() + prefs.risk_tolerance.slice(1)} Risk
            </div>
        `);
        explanations.push(`Analysis uses ${prefs.risk_tolerance} risk tolerance with ${prefs.confidence_threshold || 70}% confidence threshold`);
    }
    
    // Time horizon indicator
    if (prefs.time_horizon && analysis.time_horizon_note) {
        const horizonIcons = { 'short': '⚡', 'medium': '📈', 'long': '🌱' };
        indicators.push(`
            <div class="preference-chip" style="background: #8b5cf620; border: 1px solid #8b5cf660; color: #8b5cf6">
                ${horizonIcons[prefs.time_horizon]} ${prefs.time_horizon.charAt(0).toUpperCase() + prefs.time_horizon.slice(1)}-term Focus
            </div>
        `);
        explanations.push(analysis.time_horizon_note);
    }
    
    // Sector preference boost
    if (analysis.sector_boost && analysis.sector_note) {
        indicators.push(`
            <div class="preference-chip" style="background: #f59e0b20; border: 1px solid #f59e0b60; color: #f59e0b">
                ⭐ Preferred Sector
            </div>
        `);
        explanations.push(analysis.sector_note);
    }
    
    // Risk adjustment indicator
    if (analysis.risk_adjusted && analysis.risk_note) {
        indicators.push(`
            <div class="preference-chip" style="background: #06b6d420; border: 1px solid #06b6d460; color: #06b6d4">
                🔍 Risk Adjusted
            </div>
        `);
        explanations.push(analysis.risk_note);
    }
    
    if (indicators.length === 0) {
        return ''; // Nothing personalized to show
    }
    
    return `
        <div class="personalization-section">
            <div class="personalization-header">
                <h6><i class="fas fa-user-cog"></i> Personalized for You</h6>
                <button class="info-toggle" onclick="togglePersonalizationDetails()" title="Learn how your preferences affect this analysis">
                    <i class="fas fa-info-circle"></i>
                </button>
            </div>
            <div class="preference-chips-container">
                ${indicators.join('')}
            </div>
            <div class="personalization-details" id="personalization-details" style="display: none;">
                <div class="personalization-explanation">
                    <strong>How Your Preferences Modified This Analysis:</strong>
                    <ul>
                        ${explanations.map(exp => `<li>${exp}</li>`).join('')}
                    </ul>
                </div>
                <div class="personalization-actions">
                    <button onclick="window.open('/settings', '_blank')" class="btn-adjust-preferences">
                        <i class="fas fa-cog"></i> Adjust Preferences
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Toggle personalization details
function togglePersonalizationDetails() {
    const details = document.getElementById('personalization-details');
    if (details) {
        const isHidden = details.style.display === 'none';
        details.style.display = isHidden ? 'block' : 'none';
        
        // Update toggle button
        const toggle = document.querySelector('.info-toggle i');
        if (toggle) {
            toggle.className = isHidden ? 'fas fa-times' : 'fas fa-info-circle';
        }
    }
}

// Display comprehensive stock analysis results
function displayComprehensiveStockAnalysis(stockData) {
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
    
    // Clear any existing results first
    hideOldResults();
    
    // Log preference data for debugging and display
    if (stockData.analysis && stockData.analysis.preferences_applied) {
        console.log('🎯 PREFERENCES DETECTED:', stockData.analysis.preferences_applied);
        // Store preference data for display functions
        window.currentPreferenceData = {
            applied: stockData.analysis.preferences_applied,
            risk_adjusted: stockData.analysis.risk_adjusted,
            sector_boost: stockData.analysis.sector_boost,
            threshold_adjusted: stockData.analysis.threshold_adjusted,
            risk_note: stockData.analysis.risk_note,
            sector_note: stockData.analysis.sector_note,
            time_horizon_note: stockData.analysis.time_horizon_note
        };
    } else {
        console.log('⚠️ NO PREFERENCES DETECTED IN RESPONSE');
        window.currentPreferenceData = null;
    }
    
    // Build comprehensive analysis results using our enhanced API data
    const resultsContainer = document.getElementById('ai-analysis-results');
    if (!resultsContainer) {
        console.error('ai-analysis-results container not found! Creating it...');
        // Create the overlay container if it doesn't exist
        const overlay = document.createElement('div');
        overlay.id = 'ai-analysis-results';
        overlay.className = 'ai-results-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            z-index: 10000;
            display: none;
            justify-content: center;
            align-items: flex-start;
            overflow-y: auto;
            padding: 20px;
        `;
        document.body.appendChild(overlay);
        console.log('Created ai-analysis-results overlay container');
    }
    
    const comprehensiveHTML = buildComprehensiveAnalysisHTML(stockData);
    
    // Get the container again in case it was just created
    const finalContainer = document.getElementById('ai-analysis-results');
    finalContainer.innerHTML = comprehensiveHTML;
    finalContainer.style.display = 'flex';
    
    console.log('ChatGPT-style overlay should now be visible');
    console.log('Container display style:', finalContainer.style.display);
    console.log('Container innerHTML length:', finalContainer.innerHTML.length);
    
    // Force the overlay to be visible
    finalContainer.style.display = 'flex !important';
    finalContainer.style.position = 'fixed';
    finalContainer.style.top = '0';
    finalContainer.style.left = '0';
    finalContainer.style.width = '100%';
    finalContainer.style.height = '100%';
    finalContainer.style.zIndex = '10000';
    finalContainer.style.background = 'rgba(0, 0, 0, 0.95)';
    
    // Show the results with smooth animation
    setTimeout(() => {
        const content = finalContainer.querySelector('.search-results-content');
        if (content) {
            content.style.transform = 'scale(1)';
            content.style.opacity = '1';
        }
    }, 50);
    
    console.log('ChatGPT-style search results displayed successfully');
    console.log('Final container styles applied');
    
    // Scroll to top to ensure overlay is visible
    window.scrollTo(0, 0);
}

// Build comprehensive analysis HTML using new API data structure
function buildComprehensiveAnalysisHTML(stockData) {
    // Extract real-time data from comprehensive API response
    const currentPrice = parseFloat(stockData.price || stockData.current_price || 0);
    const change = parseFloat(stockData.change || 0);
    const changePercent = parseFloat(stockData.change_percent || 0);
    
    const changeColor = change >= 0 ? '#10b981' : '#ef4444';
    const changeSign = change >= 0 ? '+' : '';
    
    // Get confidence level color
    const confidence = parseInt(stockData.confidence || 50);
    let confidenceColor = '#ef4444'; // Red for low confidence
    if (confidence > 70) confidenceColor = '#10b981'; // Green for high confidence
    else if (confidence > 40) confidenceColor = '#f59e0b'; // Yellow for medium confidence
    
    // Format market sentiment badge
    const sentiment = stockData.market_sentiment || 'NEUTRAL';
    const sentimentColor = {
        'VERY_BULLISH': '#10b981',
        'BULLISH': '#34d399', 
        'NEUTRAL': '#6b7280',
        'BEARISH': '#f87171',
        'VERY_BEARISH': '#ef4444'
    }[sentiment] || '#6b7280';
    
    // Format risk level badge
    const riskLevel = stockData.risk_level || 'MEDIUM';
    const riskColor = {
        'LOW': '#10b981',
        'MEDIUM': '#f59e0b',
        'HIGH': '#ef4444'
    }[riskLevel] || '#f59e0b';
    
    return `
        <div class="search-results-overlay">
            <div class="search-results-content">
                <!-- Enhanced Stock Header with Real-time Data -->
                <div class="stock-header">
                    <div class="stock-info">
                        <h2 class="stock-name">${stockData.name || 'Unknown Company'}</h2>
                        <div class="stock-symbol-sector">
                            <span class="stock-symbol">${stockData.symbol}</span>
                            <span class="live-indicator">🔴 LIVE</span>
                        </div>
                    </div>
                    <div class="stock-price-info">
                        <div class="current-price">$${currentPrice.toFixed(2)}</div>
                        <div class="price-change" style="color: ${changeColor}">
                            ${changeSign}$${Math.abs(change).toFixed(2)} (${changeSign}${changePercent.toFixed(2)}%)
                        </div>
                        <div class="data-timestamp">
                            Updated: ${stockData.timestamp ? new Date(stockData.timestamp).toLocaleTimeString() : 'Real-time'}
                        </div>
                    </div>
                </div>
                
                <!-- Enhanced AI Analysis Section -->
                <div class="ai-analysis-section">
                    <h3>🤖 AI Market Intelligence Analysis</h3>
                    <div class="analysis-grid">
                        <!-- AI Recommendation Panel -->
                        <div class="ai-recommendation-panel">
                            <div class="recommendation-header">
                                <div class="recommendation-badge ${(stockData.analysis || 'HOLD').toLowerCase().replace(' ', '-').replace('_', '-')}">${stockData.analysis || 'HOLD'}</div>
                                <div class="confidence-container">
                                    <div class="confidence-label">AI Confidence Level</div>
                                    <div class="confidence-display">
                                        <div class="confidence-bar">
                                            <div class="confidence-fill" style="width: ${confidence}%; background-color: ${confidenceColor}"></div>
                                        </div>
                                        <span class="confidence-text" style="color: ${confidenceColor}">${confidence}%</span>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Investment Thesis -->
                            <div class="investment-thesis">
                                <h5><i class="fas fa-lightbulb"></i> Investment Thesis</h5>
                                <p>${stockData.investment_thesis || stockData.ai_reasoning || 'AI analysis indicates market conditions and technical factors support current recommendation.'}</p>
                            </div>
                            
                            <!-- Preference Personalization Indicators -->
                            ${generatePreferenceIndicatorDisplay(stockData)}
                            
                            <!-- Key Insights -->
                            <div class="key-insights">
                                <h5><i class="fas fa-chart-line"></i> Key Market Insights</h5>
                                <ul class="insights-list">
                                    ${(stockData.key_points || []).map(point => `<li><i class="fas fa-arrow-right"></i> ${point}</li>`).join('')}
                                    ${(!stockData.key_points || stockData.key_points.length === 0) ? '<li><i class="fas fa-info-circle"></i> Market conditions appear stable</li>' : ''}
                                </ul>
                            </div>
                        </div>
                        
                        <!-- Intelligence Dashboard -->
                        <div class="intelligence-dashboard">
                            <h5><i class="fas fa-brain"></i> AI Intelligence Dashboard</h5>
                            
                            <div class="metric-grid">
                                <div class="metric-item">
                                    <i class="fas fa-heart" style="color: ${sentimentColor}"></i>
                                    <span>Market Sentiment</span>
                                    <span class="badge" style="background-color: ${sentimentColor}">${sentiment.replace('_', ' ')}</span>
                                </div>
                                
                                <div class="metric-item">
                                    <i class="fas fa-building" style="color: #10b981"></i>
                                    <span>Fundamental Score</span>
                                    <span class="score">${stockData.fundamental_score || 50}/100</span>
                                </div>
                                
                                <div class="metric-item">
                                    <i class="fas fa-chart-bar" style="color: #3b82f6"></i>
                                    <span>Technical Score</span>
                                    <span class="score">${stockData.technical_score || 50}/100</span>
                                </div>
                                
                                <div class="metric-item">
                                    <i class="fas fa-shield-alt" style="color: ${riskColor}"></i>
                                    <span>Risk Assessment</span>
                                    <span class="badge" style="background-color: ${riskColor}">${riskLevel}</span>
                                </div>
                                
                                <div class="metric-item">
                                    <i class="fas fa-crosshairs" style="color: #8b5cf6"></i>
                                    <span>AI Price Target</span>
                                    <span class="price-target">${stockData.price_target || 'Under evaluation'}</span>
                                </div>
                                
                                <div class="metric-item">
                                    <i class="fas fa-exclamation-triangle" style="color: #f59e0b"></i>
                                    <span>Risk Factors</span>
                                    <span class="risk-count">${(stockData.risk_factors || ['Market volatility']).length} identified</span>
                                </div>
                            </div>
                            
                            <!-- Catalyst Events -->
                            ${stockData.catalyst_events && stockData.catalyst_events.length > 0 ? `
                            <div class="catalyst-events">
                                <h6><i class="fas fa-bolt"></i> Market Catalysts</h6>
                                <ul class="catalyst-list">
                                    ${stockData.catalyst_events.map(event => `<li><i class="fas fa-lightning-bolt"></i> ${event}</li>`).join('')}
                                </ul>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
                
                <!-- Real-time Market Data Section -->
                <div class="market-data-section">
                    <h4><i class="fas fa-chart-area"></i> Live Market Data</h4>
                    <div class="market-data-grid">
                        <div class="data-item">
                            <span><i class="fas fa-dollar-sign"></i> Market Cap:</span>
                            <span class="data-value">$${formatLargeNumber(stockData.market_cap || 0)}</span>
                        </div>
                        <div class="data-item">
                            <span><i class="fas fa-volume-up"></i> Volume:</span>
                            <span class="data-value">${formatLargeNumber(stockData.volume || 0)}</span>
                        </div>
                        <div class="data-item">
                            <span><i class="fas fa-percentage"></i> P/E Ratio:</span>
                            <span class="data-value">${stockData.pe_ratio ? stockData.pe_ratio.toFixed(2) : 'N/A'}</span>
                        </div>
                        <div class="data-item">
                            <span><i class="fas fa-arrow-up"></i> Day High:</span>
                            <span class="data-value">$${(stockData.day_high || 0).toFixed(2)}</span>
                        </div>
                        <div class="data-item">
                            <span><i class="fas fa-arrow-down"></i> Day Low:</span>
                            <span class="data-value">$${(stockData.day_low || 0).toFixed(2)}</span>
                        </div>
                        <div class="data-item">
                            <span><i class="fas fa-coins"></i> Dividend Yield:</span>
                            <span class="data-value">${stockData.dividend_yield ? (stockData.dividend_yield * 100).toFixed(2) + '%' : 'N/A'}</span>
                        </div>
                    </div>
                    
                    <!-- Data Source Attribution -->
                    <div class="data-attribution">
                        <i class="fas fa-database"></i> Data Source: ${stockData.data_source || 'Yahoo Finance (Real-time)'} | 
                        Analysis Type: ${stockData.analysis_type || 'Live AI Analysis'}
                    </div>
                </div>
                
                <!-- Close Button -->
                <button class="close-results" onclick="closeSearchResults()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `;
}

function buildAnalysisHTML_OLD_DISABLED(stockData, aiAnalysis) {
    const priceChange = stockData.current_price - stockData.previous_close;
    const priceChangePercent = (priceChange / stockData.previous_close) * 100;
    const changeClass = priceChange >= 0 ? 'text-success' : 'text-danger';
    const changeSymbol = priceChange >= 0 ? '+' : '';
    
    const recommendation = aiAnalysis.recommendation || 'HOLD';
    const confidence = aiAnalysis.confidence || 50;
    const riskLevel = aiAnalysis.risk_level || 'MEDIUM';
    const riskScore = aiAnalysis.risk_score || 5;
    const insight = aiAnalysis.insight || 'AI analysis in progress...';
    const priceTarget = aiAnalysis.price_target || stockData.current_price;
    const expectedReturn = aiAnalysis.expected_return || 0;
    const keyRisks = aiAnalysis.key_risks || ['Market volatility', 'Economic conditions'];
    
    // Get badge classes
    const recBadgeClass = getRecommendationBadgeClass(recommendation);
    const riskBadgeClass = getRiskBadgeClass(riskLevel);
    
    return `
        <div class="row">
            <div class="col-12">
                <div class="card bg-dark border-0 shadow-lg">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-8">
                                <div class="d-flex justify-content-between align-items-start mb-3">
                                    <div>
                                        <h2 class="text-white mb-1">${stockData.name}</h2>
                                        <p class="text-muted mb-0">${stockData.symbol} • ${stockData.sector}</p>
                                    </div>
                                    <div class="text-end">
                                        <h3 class="text-white mb-0">${formatPrice(stockData.current_price)}</h3>
                                        <p class="mb-0">
                                            <span class="${changeClass}">
                                                ${changeSymbol}${priceChange.toFixed(2)} (${changeSymbol}${priceChangePercent.toFixed(2)}%)
                                            </span>
                                        </p>
                                    </div>
                                </div>
                                
                                <div class="row mb-4">
                                    <div class="col-md-6">
                                        <div class="ai-recommendation-card">
                                            <h5 class="text-white mb-2">
                                                <i class="fas fa-robot me-2"></i>AI Recommendation
                                            </h5>
                                            <span class="badge ${recBadgeClass} fs-6 mb-2">${recommendation}</span>
                                            <p class="text-muted mb-0">Confidence: ${confidence}%</p>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="risk-assessment-card">
                                            <h5 class="text-white mb-2">
                                                <i class="fas fa-exclamation-triangle me-2"></i>Risk Assessment
                                            </h5>
                                            <span class="badge ${riskBadgeClass} fs-6 mb-2">${riskLevel}</span>
                                            <p class="text-muted mb-0">Risk Score: ${riskScore}/10</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="ai-insights-section">
                                    <h5 class="text-white mb-3">
                                        <i class="fas fa-brain me-2"></i>AI Insights
                                    </h5>
                                    <p class="text-light mb-3">${insight}</p>
                                    
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="metric-card">
                                                <h6 class="text-white">Price Target</h6>
                                                <p class="text-success fs-5 mb-0">${formatPrice(priceTarget)}</p>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="metric-card">
                                                <h6 class="text-white">Expected Return</h6>
                                                <p class="fs-5 mb-0 ${expectedReturn >= 0 ? 'text-success' : 'text-danger'}">
                                                    ${expectedReturn >= 0 ? '+' : ''}${expectedReturn.toFixed(2)}%
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="key-risks-section mt-4">
                                        <h6 class="text-white mb-2">Key Risk Factors</h6>
                                        <ul class="text-muted">
                                            ${keyRisks.map(risk => `<li>${risk}</li>`).join('')}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-md-4">
                                <div class="action-panel">
                                    <button class="btn btn-success btn-lg w-100 mb-3" onclick="showBuyModal('${stockData.symbol}', ${stockData.current_price})">
                                        <i class="fas fa-shopping-cart me-2"></i>Buy Stock
                                    </button>
                                    <button class="btn btn-outline-primary w-100 mb-3" onclick="addToWatchlist('${stockData.symbol}')">
                                        <i class="fas fa-eye me-2"></i>Add to Watchlist
                                    </button>
                                    <button class="btn btn-outline-secondary w-100" onclick="showNewSearch()">
                                        Search Another
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function getRecommendationBadgeClass(recommendation) {
    switch (recommendation) {
        case 'STRONG BUY':
        case 'BUY':
            return 'bg-success';
        case 'HOLD':
            return 'bg-warning';
        case 'SELL':
        case 'STRONG SELL':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
}

function getRiskBadgeClass(riskLevel) {
    switch (riskLevel) {
        case 'LOW':
            return 'bg-success';
        case 'MEDIUM':
            return 'bg-warning';
        case 'HIGH':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
}

function showNewSearch() {
    document.getElementById('ai-analysis-results').style.display = 'none';
    const searchInput = document.getElementById('search-input'); // Fixed ID
    if (searchInput) {
        searchInput.value = '';
        searchInput.focus();
    }
}

function addToWatchlist(symbol) {
    // Implementation for adding to watchlist
    console.log('Adding to watchlist:', symbol);
    // You can implement this feature later
    alert('Watchlist feature coming soon!');
}

// Global function for enhanced suggestion selection
function selectEnhancedSuggestion(suggestion) {
    const searchInput = document.getElementById('search-input'); // Fixed ID
    if (searchInput) {
        searchInput.value = suggestion.symbol;
        hideSuggestions();
        searchStockAI();
    }
}

// Global function for theme search
function searchTheme(themeName) {
    console.log('Searching theme:', themeName);
    // Navigate to theme analysis page
    showThemeAnalysis(themeName);
}

// Show theme analysis page
async function showThemeAnalysis(themeName) {
    const resultsContainer = document.getElementById('ai-analysis-results');
    
    // Show loading state
    resultsContainer.innerHTML = `
        <div class="col-12">
            <div class="card bg-dark border-0 shadow">
                <div class="card-body text-center py-5">
                    <div class="loading-spinner"></div>
                    <h3 class="text-white mt-3 mb-2">Analyzing ${themeName} Theme...</h3>
                    <p class="text-muted">Our AI is gathering market data and generating insights</p>
                </div>
            </div>
        </div>
    `;
    resultsContainer.style.display = 'block';
    
    try {
        // Fetch theme analysis
        const response = await fetch(`/api/search-theme/${encodeURIComponent(themeName)}`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch theme analysis');
        }
        
        const themeData = await response.json();
        displayThemeAnalysis(themeData);
        
    } catch (error) {
        console.error('Error fetching theme analysis:', error);
        showSearchError('Failed to load theme analysis. Please try again.');
    }
}

// Display theme analysis results
function displayThemeAnalysis(themeData) {
    const resultsContainer = document.getElementById('ai-analysis-results');
    
    const topStocks = themeData.top_stocks || [];
    const themeInsights = themeData.insights || {};
    const performance = themeData.performance || {};
    
    const analysisHTML = `
        <div class="row">
            <div class="col-12">
                <div class="card bg-dark border-0 shadow-lg">
                    <div class="card-body">
                        <div class="theme-header mb-4">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h2 class="text-white mb-2">
                                        <i class="fas ${themeData.icon || 'fa-chart-line'} me-2"></i>
                                        ${themeData.name} Investment Theme
                                    </h2>
                                    <p class="text-muted mb-0">${themeData.description || 'Investment theme analysis'}</p>
                                </div>
                                <div class="text-end">
                                    <div class="theme-performance">
                                        <div class="performance-metric">
                                            <span class="text-white">30-Day Return</span>
                                            <h4 class="mb-0 ${performance.return_30d >= 0 ? 'text-success' : 'text-danger'}">
                                                ${performance.return_30d >= 0 ? '+' : ''}${performance.return_30d?.toFixed(2) || '0.00'}%
                                            </h4>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row mb-4">
                            <div class="col-md-4">
                                <div class="metric-card">
                                    <h6 class="text-white">Market Cap</h6>
                                    <p class="text-success fs-5 mb-0">${formatMarketCap(themeData.total_market_cap)}</p>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="metric-card">
                                    <h6 class="text-white">Stocks in Theme</h6>
                                    <p class="text-info fs-5 mb-0">${topStocks.length || 0}</p>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="metric-card">
                                    <h6 class="text-white">AI Confidence</h6>
                                    <p class="text-warning fs-5 mb-0">${themeInsights.confidence || 75}%</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="theme-insights mb-4">
                            <h5 class="text-white mb-3">
                                <i class="fas fa-brain me-2"></i>AI Theme Analysis
                            </h5>
                            <p class="text-light">${themeInsights.analysis || 'Comprehensive analysis of this investment theme.'}</p>
                        </div>
                        
                        <div class="top-stocks-section">
                            <h5 class="text-white mb-3">
                                <i class="fas fa-star me-2"></i>Top Stocks in Theme
                            </h5>
                            <div class="row">
                                ${topStocks.map(stock => `
                                    <div class="col-md-6 mb-3">
                                        <div class="stock-card">
                                            <div class="d-flex justify-content-between align-items-center">
                                                <div>
                                                    <h6 class="text-white mb-1">${stock.symbol}</h6>
                                                    <p class="text-muted mb-0">${stock.name}</p>
                                                </div>
                                                <div class="text-end">
                                                    <div class="text-white">$${stock.current_price?.toFixed(2) || 'N/A'}</div>
                                                    <div class="text-${stock.change_percent >= 0 ? 'success' : 'danger'}">
                                                        ${stock.change_percent >= 0 ? '+' : ''}${stock.change_percent?.toFixed(2) || '0.00'}%
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="mt-2">
                                                <button class="btn btn-sm btn-outline-primary me-2" onclick="searchStockSymbol('${stock.symbol}')">
                                                    Analyze
                                                </button>
                                                <button class="btn btn-sm btn-success" onclick="showBuyModal('${stock.symbol}', ${stock.current_price || 0})">
                                                    <i class="fas fa-shopping-cart"></i> Buy
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        
                        <div class="theme-actions mt-4">
                            <button class="btn btn-outline-secondary" onclick="showNewSearch()">
                                Search Another Theme
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    resultsContainer.innerHTML = analysisHTML;
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Search stock by symbol
function searchStockSymbol(symbol) {
    const searchInput = document.getElementById('search-input'); // Fixed ID
    if (searchInput) {
        searchInput.value = symbol;
        searchStockAI();
    }
}

// Enhanced autocomplete will be initialized by ai_autocomplete_enhanced.js

// Utility function to format market cap
function formatMarketCap(marketCap) {
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

// Show new search interface
function showNewSearch() {
    const resultsContainer = document.getElementById('ai-analysis-results');
    resultsContainer.style.display = 'none';
    
    // Clear search input and focus
    const searchInput = document.getElementById('search-input'); // Fixed ID
    if (searchInput) {
        searchInput.value = '';
        searchInput.focus();
    }
    
    // Show popular suggestions if autocomplete is available
    if (window.aiAutocomplete) {
        window.aiAutocomplete.showPopularSuggestions();
    }
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

// Show loading state - DISABLED to prevent conflict with ChatGPT overlay
function showSearchLoading_DISABLED() {
    console.log('Loading state - using ChatGPT overlay system instead');
    return;
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
                    <button class="btn btn-light" onclick="hideSuggestions(); document.getElementById('search-input').focus();">
                        Try Again
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
    const input = document.getElementById('search-input'); // Fixed ID
    if (input) {
        input.value = symbol;
        searchStockAI();
    }
}

// Alternative function name for compatibility
window.quickSearch = quickSearch;

// Hide old search results and any competing displays
function hideOldResults() {
    const oldResults = document.getElementById('search-results');
    if (oldResults) {
        oldResults.style.display = 'none';
        oldResults.innerHTML = '';
    }
    
    // Also hide any other result containers that might interfere
    const containers = ['stock-analysis-results', 'analysis-results', 'search-output'];
    containers.forEach(containerId => {
        const container = document.getElementById(containerId);
        if (container) {
            container.style.display = 'none';
            container.innerHTML = '';
        }
    });
}

// Close search results function
function closeSearchResults() {
    const resultsContainer = document.getElementById('ai-analysis-results');
    if (resultsContainer) {
        const content = resultsContainer.querySelector('.search-results-content');
        if (content) {
            content.style.transform = 'scale(0.95)';
            content.style.opacity = '0';
        }
        setTimeout(() => {
            resultsContainer.style.display = 'none';
        }, 300);
    }
}

// Test function to demonstrate ChatGPT-style overlay
function testChatGPTOverlay() {
    const testData = {
        name: "Apple Inc.",
        symbol: "AAPL",
        price: 211.18,
        change: 1.16,
        change_percent: 0.55,
        confidence: 75,
        analysis: "HOLD",
        market_sentiment: "NEUTRAL",
        risk_level: "MEDIUM",
        investment_thesis: "Strong fundamentals with mixed technical signals indicate holding current position.",
        key_points: ["Solid revenue growth", "Market leadership position"],
        fundamental_score: 85,
        technical_score: 65,
        market_cap: 3154142035968,
        volume: 48317144,
        data_source: "Test Data",
        timestamp: new Date().toISOString()
    };
    
    displayComprehensiveStockAnalysis(testData);
}

// Make test function globally available
window.testChatGPTOverlay = testChatGPTOverlay;

// Force overlay display function - use this to debug
function forceShowOverlay() {
    const testData = {
        name: "Test Stock",
        symbol: "TEST",
        price: 100.00,
        change: 5.00,
        change_percent: 5.0,
        confidence: 85,
        analysis: "STRONG BUY",
        market_sentiment: "BULLISH",
        risk_level: "LOW",
        investment_thesis: "This is a test of the ChatGPT-style overlay display system.",
        key_points: ["Test point 1", "Test point 2"],
        fundamental_score: 90,
        technical_score: 80,
        market_cap: 1000000000,
        volume: 1000000,
        data_source: "Test System",
        timestamp: new Date().toISOString()
    };
    
    console.log('=== FORCING OVERLAY DISPLAY TEST ===');
    
    // Remove any existing overlay
    const existing = document.getElementById('ai-analysis-results');
    if (existing) existing.remove();
    
    // Create new overlay
    const overlay = document.createElement('div');
    overlay.id = 'ai-analysis-results';
    overlay.style.cssText = `
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        background: rgba(0, 0, 0, 0.95) !important;
        z-index: 999999 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 20px !important;
    `;
    overlay.innerHTML = `
        <div style="background: white; padding: 40px; border-radius: 10px; max-width: 600px; color: black;">
            <h2>ChatGPT-Style Overlay Test</h2>
            <p>If you can see this, the overlay system is working!</p>
            <p><strong>Stock:</strong> ${testData.name} (${testData.symbol})</p>
            <p><strong>Price:</strong> $${testData.price}</p>
            <p><strong>Analysis:</strong> ${testData.analysis}</p>
            <p><strong>Confidence:</strong> ${testData.confidence}%</p>
            <button onclick="document.getElementById('ai-analysis-results').remove()" style="padding: 10px 20px; margin-top: 20px; background: #007bff; color: white; border: none; border-radius: 5px;">Close Test</button>
        </div>
    `;
    
    document.body.appendChild(overlay);
    console.log('Test overlay created and displayed');
}

window.forceShowOverlay = forceShowOverlay;

// Reset search button on page load
document.addEventListener('DOMContentLoaded', function() {
    const searchBtn = document.getElementById('search-btn');
    if (searchBtn) {
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<i class="fas fa-brain me-2"></i>Analyze';
    }
    
    console.log('TradeWise AI enhanced search interface loaded');
    console.log('To test ChatGPT-style overlay, type: testChatGPTOverlay()');
});