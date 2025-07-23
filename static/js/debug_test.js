// JavaScript Debug Test Functions
// This file provides debugging functions to test the search system

function testStockSearch() {
    console.log('=== TESTING STOCK SEARCH SYSTEM ===');
    
    // Test if main function exists
    if (typeof searchStockAI !== 'function') {
        console.error('❌ searchStockAI function not found');
        return;
    }
    
    // Test if enhanced display function exists
    if (typeof displayEnhancedAnalysis !== 'function') {
        console.error('❌ displayEnhancedAnalysis function not found');
        return;
    }
    
    // Test container exists
    const container = document.getElementById('ai-analysis-results');
    if (!container) {
        console.error('❌ ai-analysis-results container not found');
        return;
    }
    
    console.log('✅ All functions and containers are available');
    
    // Test with sample data
    const testData = {
        success: true,
        symbol: 'TEST',
        company_name: 'Test Company',
        current_price: 100.50,
        recommendation: 'BUY',
        confidence: 85,
        enhanced_analysis: {
            sector: 'Technology',
            technical_indicators: {
                rsi: 65,
                macd: 'Bullish'
            }
        }
    };
    
    try {
        displayEnhancedAnalysis(testData);
        console.log('✅ Enhanced analysis display test successful');
    } catch (error) {
        console.error('❌ Enhanced analysis display test failed:', error);
    }
}

function testAPICall() {
    console.log('=== TESTING API CALL ===');
    
    fetch('/api/stock-analysis', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: 'AAPL' })
    })
    .then(response => {
        console.log('API Response Status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('✅ API call successful:', data);
        if (data.success) {
            console.log('✅ Backend working correctly');
            displayEnhancedAnalysis(data);
        } else {
            console.error('❌ Backend returned error:', data.error);
        }
    })
    .catch(error => {
        console.error('❌ API call failed:', error);
    });
}

function debugSearchError() {
    console.log('=== DEBUGGING SEARCH ERRORS ===');
    
    // Override console.error to catch all errors
    const originalError = console.error;
    console.error = function(...args) {
        originalError.apply(console, ['🔍 CAPTURED ERROR:'].concat(args));
        
        // If this is the search error we're looking for
        if (args[0] === 'Search error:' && args[1] && typeof args[1] === 'object') {
            console.log('🎯 FOUND THE SEARCH ERROR FROM DEBUG_TEST.JS!');
            console.log('Error object:', args[1]);
            console.log('Error type:', args[1]?.constructor?.name);
            console.log('Error message:', args[1]?.message);
            console.log('Error stack:', args[1]?.stack);
            console.log('Error message:', args[1].message || 'No message');
            console.log('Error stack:', args[1].stack || 'No stack');
        }
    };
    
    // Test a search to trigger any errors
    if (typeof searchStockAI === 'function') {
        searchStockAI('AAPL');
    } else {
        console.error('searchStockAI function not available for testing');
    }
}

// Make functions globally available
window.testStockSearch = testStockSearch;
window.testAPICall = testAPICall;
window.debugSearchError = debugSearchError;

console.log('🔧 Debug test functions loaded. Use testStockSearch(), testAPICall(), or debugSearchError() in console.');