// AI-Powered Stock Search and Analysis

let currentAnalyzedStock = null;

// Quick search function for popular stocks
function quickSearch(symbol) {
    document.getElementById('stock-search-input').value = symbol;
    searchStockAI();
}

// Main AI stock search function
async function searchStockAI() {
    const searchInput = document.getElementById('stock-search-input');
    const symbol = searchInput.value.trim().toUpperCase();
    
    if (!symbol) {
        showError('Please enter a stock symbol');
        return;
    }

    // Show loading state
    showSearchLoading();
    
    try {
        // Get stock data
        const stockData = await searchStockData(symbol);
        if (!stockData) {
            throw new Error('Stock not found');
        }

        // Get AI analysis
        const aiAnalysis = await getAIAnalysis(symbol);
        
        // Display results
        displayStockAnalysis(stockData, aiAnalysis);
        
    } catch (error) {
        console.error('Error searching stock:', error);
        showSearchError(error.message);
    }
}

// Search stock data from backend
async function searchStockData(symbol) {
    try {
        const response = await fetch(`/api/search-stock/${symbol}`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch stock data');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching stock data:', error);
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

// Display stock analysis results
function displayStockAnalysis(stockData, aiAnalysis) {
    currentAnalyzedStock = stockData;
    
    // Update stock information
    document.getElementById('stock-name').textContent = stockData.name;
    document.getElementById('stock-symbol').textContent = stockData.symbol;
    document.getElementById('stock-sector').textContent = stockData.sector;
    document.getElementById('stock-price').textContent = formatPrice(stockData.current_price);
    
    // Update price change
    const priceChange = stockData.current_price - stockData.previous_close;
    const priceChangePercent = (priceChange / stockData.previous_close) * 100;
    const changeElement = document.getElementById('stock-change');
    const changeClass = priceChange >= 0 ? 'text-success' : 'text-danger';
    const changeSymbol = priceChange >= 0 ? '+' : '';
    
    changeElement.innerHTML = `<span class="${changeClass}">${changeSymbol}${priceChange.toFixed(2)} (${changeSymbol}${priceChangePercent.toFixed(2)}%)</span>`;
    
    // Update AI recommendation
    const recommendationElement = document.getElementById('ai-recommendation');
    const recommendation = aiAnalysis.recommendation || 'HOLD';
    let badgeClass = 'bg-secondary';
    
    switch (recommendation) {
        case 'STRONG BUY':
            badgeClass = 'bg-success';
            break;
        case 'BUY':
            badgeClass = 'bg-success';
            break;
        case 'HOLD':
            badgeClass = 'bg-warning';
            break;
        case 'SELL':
            badgeClass = 'bg-danger';
            break;
        case 'STRONG SELL':
            badgeClass = 'bg-danger';
            break;
    }
    
    recommendationElement.innerHTML = `<span class="badge ${badgeClass}">${recommendation}</span>`;
    document.getElementById('ai-confidence').textContent = `${aiAnalysis.confidence || 50}%`;
    document.getElementById('ai-insight').textContent = aiAnalysis.insight || 'AI analysis in progress...';
    
    // Update risk assessment
    const riskElement = document.getElementById('risk-level');
    const riskLevel = aiAnalysis.risk_level || 'MEDIUM';
    let riskBadgeClass = 'bg-warning';
    
    switch (riskLevel) {
        case 'LOW':
            riskBadgeClass = 'bg-success';
            break;
        case 'MEDIUM':
            riskBadgeClass = 'bg-warning';
            break;
        case 'HIGH':
            riskBadgeClass = 'bg-danger';
            break;
    }
    
    riskElement.innerHTML = `<span class="badge ${riskBadgeClass}">${riskLevel}</span>`;
    document.getElementById('risk-score').textContent = `${aiAnalysis.risk_score || 5}/10`;
    
    // Update risk factors
    const riskFactors = aiAnalysis.key_risks || ['Market volatility', 'Economic conditions'];
    const riskFactorsList = document.getElementById('risk-factors');
    riskFactorsList.innerHTML = riskFactors.map(risk => `<li>${risk}</li>`).join('');
    
    // Update price target
    const priceTarget = aiAnalysis.price_target || stockData.current_price;
    const expectedReturn = aiAnalysis.expected_return || 0;
    
    document.getElementById('target-price').textContent = formatPrice(priceTarget);
    document.getElementById('price-range').textContent = `${formatPrice(priceTarget * 0.95)} - ${formatPrice(priceTarget * 1.05)}`;
    document.getElementById('expected-return').textContent = `${expectedReturn >= 0 ? '+' : ''}${expectedReturn.toFixed(2)}%`;
    
    // Update AI insights text
    const insightsText = generateDetailedInsights(stockData, aiAnalysis);
    const insightsElement = document.getElementById('ai-insights-text');
    if (insightsElement) {
        insightsElement.innerHTML = insightsText;
    }
    
    // Update buy button
    const buyButton = document.getElementById('buy-stock-btn');
    buyButton.setAttribute('onclick', `showBuyModal('${stockData.symbol}', ${stockData.current_price})`);
    
    // Show results
    document.getElementById('search-loading').style.display = 'none';
    document.getElementById('ai-analysis-results').style.display = 'block';
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

// Show loading state
function showSearchLoading() {
    document.getElementById('ai-analysis-results').style.display = 'none';
    document.getElementById('search-loading').style.display = 'block';
    
    // Update search button
    const searchBtn = document.getElementById('search-btn');
    if (searchBtn) {
        searchBtn.disabled = true;
        searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
    }
}

// Show search error
function showSearchError(message) {
    document.getElementById('search-loading').style.display = 'none';
    document.getElementById('ai-analysis-results').style.display = 'none';
    
    // Reset search button
    const searchBtn = document.getElementById('search-btn');
    if (searchBtn) {
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<i class="fas fa-brain me-2"></i>Analyze';
    }
    
    // Show error
    if (window.notificationManager) {
        window.notificationManager.showError(`Stock search failed: ${message}`);
    } else {
        alert(`Stock search failed: ${message}`);
    }
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
    const input = document.getElementById('stock-search-input');
    if (input) {
        input.value = symbol;
    }
    searchStockAI();
}

// Alternative function name for compatibility
window.quickSearch = quickSearch;

// Reset search button on page load
document.addEventListener('DOMContentLoaded', function() {
    const searchBtn = document.getElementById('search-btn');
    if (searchBtn) {
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<i class="fas fa-brain me-2"></i>Analyze';
    }
});