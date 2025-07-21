/**
 * Intelligent Stock Search JavaScript
 * Handles real-time stock search with AI-powered analysis
 */

class IntelligentStockSearch {
    constructor() {
        this.searchInput = document.getElementById('stock-search-input');
        this.resultsContainer = document.getElementById('ai-result');
        this.suggestionsContainer = document.getElementById('suggestions-container');
        this.isLoading = false;
        
        this.initializeEventListeners();
        this.initializeSearchSuggestions();
    }
    
    initializeEventListeners() {
        // Enter key search
        if (this.searchInput) {
            this.searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch();
                }
            });
            
            // Real-time suggestions
            this.searchInput.addEventListener('input', (e) => {
                this.showSuggestions(e.target.value);
            });
            
            // Focus handling
            this.searchInput.addEventListener('focus', () => {
                if (this.searchInput.value.length > 0) {
                    this.showSuggestions(this.searchInput.value);
                }
            });
        }
        
        // Close suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                this.hideSuggestions();
            }
        });
    }
    
    initializeSearchSuggestions() {
        this.stockSuggestions = [
            { symbol: 'AAPL', name: 'Apple Inc.', sector: 'Technology' },
            { symbol: 'MSFT', name: 'Microsoft Corporation', sector: 'Technology' },
            { symbol: 'GOOGL', name: 'Alphabet Inc.', sector: 'Technology' },
            { symbol: 'AMZN', name: 'Amazon.com Inc.', sector: 'Consumer Discretionary' },
            { symbol: 'TSLA', name: 'Tesla Inc.', sector: 'Automotive' },
            { symbol: 'NVDA', name: 'NVIDIA Corporation', sector: 'Technology' },
            { symbol: 'META', name: 'Meta Platforms Inc.', sector: 'Technology' },
            { symbol: 'NFLX', name: 'Netflix Inc.', sector: 'Entertainment' },
            { symbol: 'DIS', name: 'The Walt Disney Company', sector: 'Entertainment' },
            { symbol: 'WMT', name: 'Walmart Inc.', sector: 'Consumer Staples' },
            { symbol: 'JNJ', name: 'Johnson & Johnson', sector: 'Healthcare' },
            { symbol: 'V', name: 'Visa Inc.', sector: 'Financial Services' },
            { symbol: 'MA', name: 'Mastercard Inc.', sector: 'Financial Services' },
            { symbol: 'UNH', name: 'UnitedHealth Group', sector: 'Healthcare' },
            { symbol: 'HD', name: 'The Home Depot Inc.', sector: 'Consumer Discretionary' },
            { symbol: 'PG', name: 'Procter & Gamble Co.', sector: 'Consumer Staples' },
            { symbol: 'JPM', name: 'JPMorgan Chase & Co.', sector: 'Financial Services' },
            { symbol: 'BAC', name: 'Bank of America Corp.', sector: 'Financial Services' },
            { symbol: 'XOM', name: 'Exxon Mobil Corporation', sector: 'Energy' },
            { symbol: 'CVX', name: 'Chevron Corporation', sector: 'Energy' }
        ];
    }
    
    showSuggestions(query) {
        if (!query || query.length < 1) {
            this.hideSuggestions();
            return;
        }
        
        const filtered = this.stockSuggestions.filter(stock => 
            stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
            stock.name.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 6);
        
        if (filtered.length > 0) {
            const suggestionsHtml = filtered.map(stock => `
                <div class="suggestion-item" onclick="intelligentSearch.selectSuggestion('${stock.symbol}')">
                    <div class="suggestion-content">
                        <span class="suggestion-symbol">${stock.symbol}</span>
                        <span class="suggestion-name">${stock.name}</span>
                        <span class="suggestion-sector">${stock.sector}</span>
                    </div>
                </div>
            `).join('');
            
            this.suggestionsContainer.innerHTML = suggestionsHtml;
            this.suggestionsContainer.style.display = 'block';
        } else {
            this.hideSuggestions();
        }
    }
    
    selectSuggestion(symbol) {
        this.searchInput.value = symbol;
        this.hideSuggestions();
        this.performSearch();
    }
    
    hideSuggestions() {
        if (this.suggestionsContainer) {
            this.suggestionsContainer.style.display = 'none';
        }
    }
    
    async performSearch() {
        const query = this.searchInput.value.trim();
        
        if (!query) {
            this.showNotification('Please enter a stock symbol or company name', 'warning');
            return;
        }
        
        if (this.isLoading) {
            return; // Prevent multiple simultaneous searches
        }
        
        this.isLoading = true;
        this.showLoadingState();
        this.hideSuggestions();
        
        try {
            const response = await fetch('/api/stock-search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.displayStockResult(data);
                this.showNotification(`Analysis complete for ${data.symbol}`, 'success');
            } else {
                this.displayError(data.error || 'Stock not found', data.message);
            }
            
        } catch (error) {
            console.error('Search error:', error);
            this.displayError('Search failed', 'Please check your connection and try again.');
        } finally {
            this.isLoading = false;
            this.hideLoadingState();
        }
    }
    
    showLoadingState() {
        if (this.resultsContainer) {
            this.resultsContainer.style.display = 'block';
            this.resultsContainer.innerHTML = `
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <h3>AI Analysis in Progress...</h3>
                    <p>Gathering real-time market data and generating intelligent insights</p>
                </div>
            `;
        }
        
        // Disable search input
        if (this.searchInput) {
            this.searchInput.disabled = true;
            this.searchInput.style.opacity = '0.6';
        }
    }
    
    hideLoadingState() {
        if (this.searchInput) {
            this.searchInput.disabled = false;
            this.searchInput.style.opacity = '1';
        }
    }
    
    displayStockResult(data) {
        if (!this.resultsContainer) return;
        
        const changeClass = data.change >= 0 ? 'positive' : 'negative';
        const changeSymbol = data.change >= 0 ? '+' : '';
        const recommendationColor = this.getRecommendationColor(data.ai_recommendation);
        
        this.resultsContainer.innerHTML = `
            <div class="ai-analysis-card">
                <!-- Stock Header -->
                <div class="stock-header">
                    <div class="stock-info">
                        <h2 class="stock-title">${data.symbol} - ${data.name}</h2>
                        <div class="stock-metrics">
                            <span class="stock-price">$${data.price.toFixed(2)}</span>
                            <span class="price-change ${changeClass}">
                                ${changeSymbol}$${Math.abs(data.change).toFixed(2)} (${data.change_percent}%)
                            </span>
                        </div>
                        <div class="market-info">
                            <span>Market Cap: $${this.formatMarketCap(data.market_cap)}</span>
                            <span>Volume: ${this.formatNumber(data.volume)}</span>
                            <span>Sector: ${data.sector}</span>
                        </div>
                    </div>
                    <div class="ai-recommendation-badge">
                        <span class="recommendation" style="background: ${recommendationColor}">${data.ai_recommendation}</span>
                        <span class="confidence">${data.confidence}% Confidence</span>
                        <span class="risk-level">Risk: ${data.risk_level}</span>
                    </div>
                </div>
                
                <!-- AI Analysis -->
                <div class="ai-analysis-section">
                    <h4><i class="fas fa-robot"></i> AI-Powered Analysis</h4>
                    <div class="analysis-content">
                        ${this.formatAnalysisText(data.ai_analysis)}
                    </div>
                </div>
                
                <!-- Technical Indicators -->
                ${this.renderTechnicalIndicators(data.technical_analysis)}
                
                <!-- Key Metrics -->
                ${this.renderKeyMetrics(data.key_metrics, data.price_target)}
                
                <!-- Action Buttons -->
                <div class="action-buttons">
                    <button class="btn-primary" onclick="intelligentSearch.actionBuy('${data.symbol}', '${data.name}', ${data.price})">
                        <i class="fas fa-shopping-cart"></i> Buy ${data.symbol}
                    </button>
                    <button class="btn-secondary" onclick="intelligentSearch.actionWatchlist('${data.symbol}', '${data.name}', ${data.price})">
                        <i class="fas fa-star"></i> Add to Watchlist
                    </button>
                    <button class="btn-secondary" onclick="intelligentSearch.actionAnalyze('${data.symbol}')">
                        <i class="fas fa-chart-line"></i> Detailed Analysis
                    </button>
                    <button class="btn-close" onclick="intelligentSearch.hideAnalysis()">
                        <i class="fas fa-times"></i> Hide Analysis
                    </button>
                </div>
            </div>
        `;
        
        this.resultsContainer.style.display = 'block';
        
        // Smooth scroll to results
        this.resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    renderTechnicalIndicators(technical) {
        if (!technical || Object.keys(technical).length === 0) {
            return '';
        }
        
        return `
            <div class="technical-indicators">
                <h4><i class="fas fa-chart-area"></i> Technical Indicators</h4>
                <div class="indicators-grid">
                    ${technical.rsi ? `<div class="indicator"><span>RSI:</span> <span class="${this.getRSIClass(technical.rsi)}">${technical.rsi}</span></div>` : ''}
                    ${technical.sma_20 ? `<div class="indicator"><span>SMA 20:</span> <span>$${technical.sma_20}</span></div>` : ''}
                    ${technical.sma_50 ? `<div class="indicator"><span>SMA 50:</span> <span>$${technical.sma_50}</span></div>` : ''}
                    ${technical.volatility ? `<div class="indicator"><span>Volatility:</span> <span>${technical.volatility}%</span></div>` : ''}
                    ${technical.volume_ratio ? `<div class="indicator"><span>Volume Ratio:</span> <span class="${this.getVolumeClass(technical.volume_ratio)}">${technical.volume_ratio}x</span></div>` : ''}
                </div>
            </div>
        `;
    }
    
    renderKeyMetrics(metrics, priceTarget) {
        if (!metrics) return '';
        
        return `
            <div class="key-metrics">
                <h4><i class="fas fa-analytics"></i> Key Metrics</h4>
                <div class="metrics-grid">
                    <div class="metric"><span>52-Week High:</span> <span>$${metrics['52_week_high'] || 'N/A'}</span></div>
                    <div class="metric"><span>52-Week Low:</span> <span>$${metrics['52_week_low'] || 'N/A'}</span></div>
                    <div class="metric"><span>Price Target:</span> <span class="price-target">$${priceTarget}</span></div>
                    <div class="metric"><span>Beta:</span> <span>${metrics.beta || 'N/A'}</span></div>
                    <div class="metric"><span>P/E Ratio:</span> <span>${metrics.pe_ratio || 'N/A'}</span></div>
                    <div class="metric"><span>Book Value:</span> <span>${metrics.book_value || 'N/A'}</span></div>
                </div>
            </div>
        `;
    }
    
    displayError(title, message) {
        if (!this.resultsContainer) return;
        
        this.resultsContainer.innerHTML = `
            <div class="error-card">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3>${title}</h3>
                <p>${message || 'Please try a different search term.'}</p>
                <button class="btn-secondary" onclick="intelligentSearch.clearResults()">
                    Try Another Search
                </button>
            </div>
        `;
        this.resultsContainer.style.display = 'block';
    }
    
    clearResults() {
        if (this.resultsContainer) {
            this.resultsContainer.style.display = 'none';
            this.resultsContainer.innerHTML = '';
        }
        if (this.searchInput) {
            this.searchInput.focus();
        }
    }

    hideAnalysis() {
        if (this.resultsContainer) {
            // Smooth fade out animation
            this.resultsContainer.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            this.resultsContainer.style.opacity = '0';
            this.resultsContainer.style.transform = 'translateY(-20px)';
            
            setTimeout(() => {
                this.resultsContainer.style.display = 'none';
                this.resultsContainer.innerHTML = '';
                // Reset styles for next use
                this.resultsContainer.style.opacity = '1';
                this.resultsContainer.style.transform = 'translateY(0)';
                this.resultsContainer.style.transition = '';
            }, 300);
        }
        
        if (this.searchInput) {
            this.searchInput.focus();
        }
        
        this.showNotification('Analysis hidden - ready for new search', 'info');
    }
    
    // Action handlers
    actionBuy(symbol, name, price) {
        this.showNotification(`Opening buy order for ${symbol}`, 'info');
        // Integration point for buy functionality
        console.log(`Buy action: ${symbol} at $${price}`);
    }
    
    actionWatchlist(symbol, name, price) {
        this.showNotification(`Adding ${symbol} to watchlist`, 'success');
        // Integration point for watchlist functionality
        console.log(`Watchlist action: ${symbol}`);
    }
    
    actionAnalyze(symbol) {
        this.showNotification(`Loading detailed analysis for ${symbol}`, 'info');
        // Integration point for detailed analysis
        console.log(`Analyze action: ${symbol}`);
    }
    
    // Utility functions
    formatMarketCap(marketCap) {
        if (!marketCap || marketCap === 0) return 'N/A';
        
        if (marketCap >= 1e12) {
            return `${(marketCap / 1e12).toFixed(1)}T`;
        } else if (marketCap >= 1e9) {
            return `${(marketCap / 1e9).toFixed(1)}B`;
        } else if (marketCap >= 1e6) {
            return `${(marketCap / 1e6).toFixed(1)}M`;
        }
        return marketCap.toLocaleString();
    }
    
    formatNumber(num) {
        if (!num) return 'N/A';
        return num.toLocaleString();
    }
    
    formatAnalysisText(text) {
        if (!text) return '';
        
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>')
            .replace(/•/g, '<br>•');
    }
    
    getRecommendationColor(recommendation) {
        const colors = {
            'STRONG BUY': '#10b981',
            'BUY': '#059669',
            'HOLD': '#f59e0b',
            'SELL': '#ef4444',
            'STRONG SELL': '#dc2626'
        };
        return colors[recommendation] || '#6b7280';
    }
    
    getRSIClass(rsi) {
        if (rsi < 30) return 'oversold';
        if (rsi > 70) return 'overbought';
        return 'neutral';
    }
    
    getVolumeClass(ratio) {
        if (ratio > 1.5) return 'high-volume';
        if (ratio < 0.7) return 'low-volume';
        return 'normal-volume';
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '10000',
            animation: 'slideInRight 0.3s ease',
            maxWidth: '300px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.2)'
        });
        
        // Type-specific colors
        const colors = {
            success: 'background: rgba(16, 185, 129, 0.9); border: 1px solid #10b981;',
            error: 'background: rgba(239, 68, 68, 0.9); border: 1px solid #ef4444;',
            warning: 'background: rgba(245, 158, 11, 0.9); border: 1px solid #f59e0b;',
            info: 'background: rgba(59, 130, 246, 0.9); border: 1px solid #3b82f6;'
        };
        
        notification.style.cssText += colors[type] || colors.info;
        document.body.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Global search functions for backward compatibility
function performStockSearch() {
    if (window.intelligentSearch) {
        window.intelligentSearch.performSearch();
    }
}

function handleSearchEnter(event) {
    if (event.key === 'Enter') {
        performStockSearch();
    }
}

function showSearchSuggestions(value) {
    if (window.intelligentSearch) {
        window.intelligentSearch.showSuggestions(value);
    }
}

function selectSuggestion(symbol) {
    if (window.intelligentSearch) {
        window.intelligentSearch.selectSuggestion(symbol);
    }
}

function searchStock(symbol) {
    const searchInput = document.getElementById('stock-search-input');
    if (searchInput) {
        searchInput.value = symbol;
        performStockSearch();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.intelligentSearch = new IntelligentStockSearch();
    console.log('Intelligent Stock Search initialized');
});