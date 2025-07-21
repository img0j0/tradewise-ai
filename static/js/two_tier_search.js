/**
 * Two-Tier Analysis Search System
 * Overrides existing search to show Quick Analysis + Detailed Analysis
 */

window.twoTierSearch = {
    currentStockData: null,
    
    async search(query) {
        try {
            // Show loading state
            this.showLoadingState();
            
            // Call the API
            const response = await fetch('/api/stock-search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.currentStockData = data;
            
            // Display two-tier analysis
            this.displayTwoTierAnalysis(data);
            
        } catch (error) {
            this.displayError(error.message);
            console.error('Search error:', error);
        }
    },
    
    showLoadingState() {
        const resultsContainer = document.getElementById('ai-result');
        resultsContainer.style.display = 'block';
        resultsContainer.innerHTML = `
            <div class="analysis-loading">
                <div class="loading-spinner"></div>
                <p>AI analyzing stock data...</p>
            </div>
        `;
    },
    
    displayTwoTierAnalysis(data) {
        const resultsContainer = document.getElementById('ai-result');
        
        const html = `
            <div class="stock-analysis-container">
                <!-- Stock Header -->
                <div class="stock-header">
                    <div class="stock-basic-info">
                        <h2 class="stock-symbol">${data.symbol}</h2>
                        <p class="stock-name">${data.name}</p>
                        <div class="stock-price">
                            <span class="price">$${data.price}</span>
                            <span class="change ${parseFloat(data.change_percent) >= 0 ? 'positive' : 'negative'}">
                                ${data.change_percent}%
                            </span>
                        </div>
                    </div>
                    <div class="ai-recommendation">
                        <span class="recommendation-badge ${data.ai_recommendation?.toLowerCase()}">${data.ai_recommendation}</span>
                        <span class="confidence-badge">${data.confidence}% Confidence</span>
                    </div>
                </div>

                <!-- TIER 1: Quick Analysis -->
                <div class="quick-analysis-tier">
                    <h3><i class="fas fa-brain"></i> AI Quick Analysis</h3>
                    <div class="quick-content">
                        <div class="ai-summary">
                            <p><strong>Market Position:</strong> ${data.name} is currently trading at $${data.price} with a market cap of $${(data.market_cap / 1e9).toFixed(1)}B in the Technology sector.</p>
                            <p><strong>AI Assessment:</strong> Our AI model rates this stock as ${data.ai_recommendation} with ${data.confidence}% confidence based on technical indicators, market sentiment, and fundamental metrics.</p>
                        </div>
                        
                        <div class="confidence-display">
                            <div class="confidence-bar-container">
                                <div class="confidence-bar">
                                    <div class="confidence-fill" style="width: ${data.confidence}%"></div>
                                </div>
                                <span class="confidence-text">${data.confidence}% AI Confidence</span>
                            </div>
                        </div>
                        
                        <div class="quick-metrics">
                            <div class="metric">
                                <span class="metric-label">Risk Level:</span>
                                <span class="metric-value risk-${data.risk_level?.toLowerCase()}">${data.risk_level}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Market Cap:</span>
                                <span class="metric-value">$${(data.market_cap / 1e9).toFixed(1)}B</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div class="action-buttons-tier">
                    <button class="btn btn-primary expand-btn" onclick="window.twoTierSearch.showDetailedAnalysis('${data.symbol}')">
                        <i class="fas fa-chart-line"></i> View Detailed Technical Analysis
                    </button>
                    <button class="btn btn-success" onclick="window.twoTierSearch.buyStock('${data.symbol}')">
                        <i class="fas fa-shopping-cart"></i> Buy Stock
                    </button>
                    <button class="btn btn-secondary" onclick="window.twoTierSearch.addToWatchlist('${data.symbol}')">
                        <i class="fas fa-star"></i> Add to Watchlist
                    </button>
                </div>

                <!-- TIER 2: Detailed Analysis (Initially Hidden) -->
                <div id="detailed-analysis-${data.symbol}" class="detailed-analysis-tier" style="display: none;">
                    <h3><i class="fas fa-chart-bar"></i> Detailed Technical Analysis</h3>
                    <div class="detailed-loading">
                        <div class="loading-spinner-small"></div>
                        <span>Loading comprehensive technical analysis...</span>
                    </div>
                </div>
            </div>
        `;
        
        resultsContainer.innerHTML = html;
        resultsContainer.style.display = 'block';
    },
    
    async showDetailedAnalysis(symbol) {
        const detailedSection = document.getElementById(`detailed-analysis-${symbol}`);
        detailedSection.style.display = 'block';
        
        // Update button to show it's loading
        const expandBtn = document.querySelector('.expand-btn');
        expandBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        expandBtn.disabled = true;
        
        try {
            const response = await fetch('/api/stock-detailed-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ symbol: symbol })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const detailedData = await response.json();
            this.displayDetailedAnalysis(detailedData, symbol);
            
        } catch (error) {
            detailedSection.innerHTML = `
                <h3><i class="fas fa-chart-bar"></i> Detailed Technical Analysis</h3>
                <div class="error-message">
                    <p>Unable to load detailed analysis: ${error.message}</p>
                    <button onclick="window.twoTierSearch.showDetailedAnalysis('${symbol}')" class="btn btn-sm btn-primary">Retry</button>
                </div>
            `;
        } finally {
            // Restore button
            expandBtn.innerHTML = '<i class="fas fa-eye-slash"></i> Hide Detailed Analysis';
            expandBtn.onclick = () => this.hideDetailedAnalysis(symbol);
            expandBtn.disabled = false;
        }
    },
    
    displayDetailedAnalysis(data, symbol) {
        const detailedSection = document.getElementById(`detailed-analysis-${symbol}`);
        
        const html = `
            <h3><i class="fas fa-chart-bar"></i> Detailed Technical Analysis</h3>
            <div class="detailed-content">
                <div class="technical-indicators">
                    <div class="indicator-grid">
                        <div class="indicator-card">
                            <h4>RSI (Relative Strength Index)</h4>
                            <div class="indicator-value">${data.rsi ? data.rsi.toFixed(2) : 'N/A'}</div>
                            <div class="indicator-signal ${this.getRSISignal(data.rsi)}">${this.getRSISignalText(data.rsi)}</div>
                        </div>
                        
                        <div class="indicator-card">
                            <h4>MACD Signal</h4>
                            <div class="indicator-value">${data.macd_signal === 1 ? 'Bullish' : 'Bearish'}</div>
                            <div class="indicator-signal ${data.macd_signal === 1 ? 'bullish' : 'bearish'}">
                                ${data.macd_signal === 1 ? 'Upward momentum' : 'Downward pressure'}
                            </div>
                        </div>
                        
                        <div class="indicator-card">
                            <h4>Bollinger Bands</h4>
                            <div class="indicator-value">${data.bb_position}</div>
                            <div class="indicator-signal neutral">Position analysis</div>
                        </div>
                        
                        <div class="indicator-card">
                            <h4>Volume Trend</h4>
                            <div class="indicator-value">${data.volume_trend}</div>
                            <div class="indicator-signal neutral">Trading activity</div>
                        </div>
                    </div>
                </div>
                
                <div class="price-analysis">
                    <h4>Price Analysis</h4>
                    <div class="price-range">
                        <div class="price-item">
                            <span class="label">52-Week High:</span>
                            <span class="value">$${data.week_52_high}</span>
                        </div>
                        <div class="price-item">
                            <span class="label">52-Week Low:</span>
                            <span class="value">$${data.week_52_low}</span>
                        </div>
                        <div class="price-item">
                            <span class="label">AI Price Target:</span>
                            <span class="value">$${data.price_target ? data.price_target.toFixed(2) : 'N/A'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="risk-analysis">
                    <h4>Risk Assessment</h4>
                    <p class="risk-description">${data.risk_analysis}</p>
                </div>
            </div>
        `;
        
        detailedSection.innerHTML = html;
    },
    
    hideDetailedAnalysis(symbol) {
        const detailedSection = document.getElementById(`detailed-analysis-${symbol}`);
        detailedSection.style.display = 'none';
        
        const expandBtn = document.querySelector('.expand-btn');
        expandBtn.innerHTML = '<i class="fas fa-chart-line"></i> View Detailed Technical Analysis';
        expandBtn.onclick = () => this.showDetailedAnalysis(symbol);
    },
    
    getRSISignal(rsi) {
        if (!rsi) return 'neutral';
        if (rsi > 70) return 'bearish';
        if (rsi < 30) return 'bullish';
        return 'neutral';
    },
    
    getRSISignalText(rsi) {
        if (!rsi) return 'No data';
        if (rsi > 70) return 'Overbought';
        if (rsi < 30) return 'Oversold';
        return 'Neutral range';
    },
    
    buyStock(symbol) {
        // Show buy modal or redirect to buy page
        console.log(`Buy stock functionality for ${symbol}`);
        // You can implement actual buy functionality here
    },
    
    addToWatchlist(symbol) {
        console.log(`Added ${symbol} to watchlist`);
        // Show success message instead of alert
        this.showNotification(`Added ${symbol} to your watchlist`, 'success');
    },
    
    showNotification(message, type = 'info') {
        // Create a notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#22c55e' : '#06b6d4'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    },
    
    displayError(message) {
        const resultsContainer = document.getElementById('ai-result');
        resultsContainer.style.display = 'block';
        resultsContainer.innerHTML = `
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <h3>Search Error</h3>
                <p>${message}</p>
                <button onclick="document.getElementById('ai-result').style.display='none'" class="btn btn-secondary">
                    Try Again
                </button>
            </div>
        `;
    }
};

// Override the existing search function
window.performStockSearch = function() {
    const searchInput = document.getElementById('stock-search-input');
    const query = searchInput.value.trim();
    
    if (query) {
        window.twoTierSearch.search(query);
    }
};

// Also handle Enter key
window.handleSearchEnter = function(event) {
    if (event.key === 'Enter') {
        window.performStockSearch();
    }
};

console.log('Two-tier search system loaded successfully');