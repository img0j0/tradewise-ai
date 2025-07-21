/**
 * Enhanced Intelligent Stock Search with Quick Analysis and Detailed View
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
        if (this.searchInput) {
            this.searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch();
                }
            });
            
            this.searchInput.addEventListener('input', (e) => {
                this.showSuggestions(e.target.value);
            });
            
            this.searchInput.addEventListener('focus', () => {
                if (this.searchInput.value.length > 0) {
                    this.showSuggestions(this.searchInput.value);
                }
            });
        }
        
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
            { symbol: 'NFLX', name: 'Netflix Inc.', sector: 'Entertainment' }
        ];
    }
    
    async performSearch() {
        const query = this.searchInput.value.trim();
        if (!query || this.isLoading) return;
        
        this.isLoading = true;
        this.hideSuggestions();
        this.showLoadingState();
        
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
                this.displayQuickAnalysis(data);
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
    
    displayQuickAnalysis(data) {
        if (!this.resultsContainer) return;
        
        // Handle the data format from our API
        const changeClass = data.change_percent && parseFloat(data.change_percent) >= 0 ? 'positive' : 'negative';
        const changeSymbol = data.change_percent && parseFloat(data.change_percent) >= 0 ? '+' : '';
        const recommendationColor = this.getRecommendationColor(data.ai_recommendation);
        const confidencePercentage = data.confidence || Math.round((data.ai_confidence || 0.5) * 100);
        
        this.resultsContainer.innerHTML = `
            <div class="ai-analysis-card">
                <!-- Quick Analysis Header -->
                <div class="stock-header">
                    <div class="stock-info">
                        <h2 class="stock-title">${data.symbol} - ${data.name}</h2>
                        <div class="stock-metrics">
                            <span class="stock-price">$${data.price}</span>
                            <span class="price-change ${changeClass}">${changeSymbol}${data.change || 0} (${data.change_percent || '0.00'}%)</span>
                        </div>
                    </div>
                    <div class="ai-recommendation-badge">
                        <span class="recommendation" style="background-color: ${recommendationColor};">
                            ${data.ai_recommendation}
                        </span>
                        <span class="confidence">AI Confidence: ${confidencePercentage}%</span>
                        <span class="risk-level">Risk Level: ${data.risk_level}</span>
                    </div>
                </div>

                <!-- Quick AI Analysis -->
                <div class="quick-analysis-section">
                    <h4><i class="fas fa-brain"></i> AI Quick Analysis</h4>
                    <div class="analysis-content">
                        <p><strong>AI Assessment:</strong> ${data.ai_analysis ? data.ai_analysis.substring(0, 200) + '...' : 'Comprehensive analysis available'}</p>
                        <p><strong>Key Insight:</strong> ${this.generateKeyInsight(data)}</p>
                        <div class="confidence-indicator">
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: ${confidencePercentage}%"></div>
                            </div>
                            <span class="confidence-text">${confidencePercentage}% AI Confidence</span>
                        </div>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div class="action-buttons">
                    <button class="btn-primary" onclick="showDetailedAnalysis('${data.symbol}')">
                        <i class="fas fa-chart-line"></i> View Detailed Analysis
                    </button>
                    <button class="btn-secondary" onclick="addToWatchlist('${data.symbol}')">
                        <i class="fas fa-star"></i> Add to Watchlist
                    </button>
                    <button class="btn-secondary" onclick="showBuyModal('${data.symbol}')">
                        <i class="fas fa-shopping-cart"></i> Buy Stock
                    </button>
                </div>

                <!-- Expandable Detailed Analysis (Hidden by default) -->
                <div id="detailed-analysis-${data.symbol}" class="detailed-analysis-section" style="display: none;">
                    <div class="analysis-loading">
                        <div class="loading-spinner"></div>
                        <p>Loading detailed analysis...</p>
                    </div>
                </div>
            </div>
        `;
        
        this.resultsContainer.style.display = 'block';
        this.currentStockData = data;
    }

    generateKeyInsight(data) {
        const price = data.price || data.current_price;
        const changeValue = data.change_percent ? parseFloat(data.change_percent) : 0;
        
        const insights = [
            `Currently trading at $${price} with ${changeValue >= 0 ? 'positive' : 'negative'} momentum`,
            `AI models suggest ${data.ai_recommendation ? data.ai_recommendation.toLowerCase() : 'hold'} based on technical and fundamental analysis`,
            `Risk assessment indicates ${data.risk_level ? data.risk_level.toLowerCase() : 'medium'} volatility in current market conditions`,
            `Price target of $${data.price_target || price * 1.1} suggests potential ${changeValue >= 0 ? 'upside' : 'recovery'} opportunity`
        ];
        return insights[Math.floor(Math.random() * insights.length)];
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

    showSuggestions(query) {
        if (!query || query.length < 1) {
            this.hideSuggestions();
            return;
        }

        const filtered = this.stockSuggestions.filter(stock => 
            stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
            stock.name.toLowerCase().includes(query.toLowerCase())
        );

        if (filtered.length > 0 && this.suggestionsContainer) {
            this.suggestionsContainer.innerHTML = filtered.slice(0, 5).map(stock => `
                <div class="suggestion-item" onclick="selectSuggestion('${stock.symbol}')">
                    <strong>${stock.symbol}</strong> - ${stock.name}
                    <small>${stock.sector}</small>
                </div>
            `).join('');
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

    displayError(title, message) {
        if (!this.resultsContainer) return;
        
        this.resultsContainer.innerHTML = `
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <h3>${title}</h3>
                <p>${message}</p>
                <button class="btn-secondary" onclick="document.getElementById('ai-result').style.display='none'">
                    Close
                </button>
            </div>
        `;
        this.resultsContainer.style.display = 'block';
    }

    showNotification(message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}

// Global functions for button actions
function showDetailedAnalysis(symbol) {
    const detailedSection = document.getElementById(`detailed-analysis-${symbol}`);
    if (!detailedSection) return;

    if (detailedSection.style.display === 'block') {
        detailedSection.style.display = 'none';
        return;
    }

    detailedSection.style.display = 'block';
    loadDetailedAnalysis(symbol, detailedSection);
}

function hideDetailedAnalysis(symbol) {
    const detailedSection = document.getElementById(`detailed-analysis-${symbol}`);
    if (detailedSection) {
        detailedSection.style.display = 'none';
    }
}

async function loadDetailedAnalysis(symbol, container) {
    try {
        const response = await fetch('/api/stock-detailed-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symbol: symbol })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            container.innerHTML = `
                <h4><i class="fas fa-microscope"></i> Advanced Technical Analysis</h4>
                
                <!-- Technical Indicators -->
                <div class="technical-indicators">
                    <h5>Technical Indicators</h5>
                    <div class="indicators-grid">
                        <div class="indicator">
                            <span>RSI (14)</span>
                            <span class="${getRSIClass(data.rsi)}">${data.rsi?.toFixed(2) || 'N/A'}</span>
                        </div>
                        <div class="indicator">
                            <span>MACD</span>
                            <span class="${data.macd_signal > 0 ? 'positive' : 'negative'}">${data.macd?.toFixed(4) || 'N/A'}</span>
                        </div>
                        <div class="indicator">
                            <span>Bollinger Bands</span>
                            <span class="neutral">${data.bb_position || 'N/A'}</span>
                        </div>
                        <div class="indicator">
                            <span>Volume Trend</span>
                            <span class="${getVolumeClass(data.volume_trend)}">${data.volume_trend || 'N/A'}</span>
                        </div>
                    </div>
                </div>

                <!-- Key Financial Metrics -->
                <div class="key-metrics">
                    <h5>Financial Fundamentals</h5>
                    <div class="metrics-grid">
                        <div class="metric">
                            <span>Market Cap</span>
                            <span>$${formatLargeNumber(data.market_cap)}</span>
                        </div>
                        <div class="metric">
                            <span>P/E Ratio</span>
                            <span>${data.pe_ratio?.toFixed(2) || 'N/A'}</span>
                        </div>
                        <div class="metric">
                            <span>52-Week Range</span>
                            <span>$${data.week_52_low} - $${data.week_52_high}</span>
                        </div>
                        <div class="metric">
                            <span>Average Volume</span>
                            <span>${formatLargeNumber(data.avg_volume)}</span>
                        </div>
                        <div class="metric">
                            <span>Beta</span>
                            <span>${data.beta?.toFixed(2) || 'N/A'}</span>
                        </div>
                        <div class="metric">
                            <span>Price Target</span>
                            <span class="price-target">$${data.price_target?.toFixed(2) || 'N/A'}</span>
                        </div>
                    </div>
                </div>

                <!-- AI Risk Assessment -->
                <div class="ai-analysis-section">
                    <h5>AI Risk Assessment</h5>
                    <div class="analysis-content">
                        <p><strong>Risk Factors:</strong> ${data.risk_analysis || 'Comprehensive risk analysis not available'}</p>
                        <p><strong>Opportunity Score:</strong> ${data.opportunity_score || 'N/A'}/10</p>
                        <p><strong>Recommendation Basis:</strong> ${data.recommendation_reasoning || 'Based on technical and fundamental analysis'}</p>
                    </div>
                </div>

                <div class="detailed-actions">
                    <button class="btn-secondary" onclick="hideDetailedAnalysis('${symbol}')">
                        <i class="fas fa-chevron-up"></i> Hide Detailed Analysis
                    </button>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="error-message">
                    <p>Unable to load detailed analysis. Please try again.</p>
                    <button class="btn-secondary" onclick="hideDetailedAnalysis('${symbol}')">Close</button>
                </div>
            `;
        }
    } catch (error) {
        console.error('Detailed analysis error:', error);
        container.innerHTML = `
            <div class="error-message">
                <p>Error loading detailed analysis. Please check your connection.</p>
                <button class="btn-secondary" onclick="hideDetailedAnalysis('${symbol}')">Close</button>
            </div>
        `;
    }
}

// Helper functions
function formatLargeNumber(num) {
    if (!num) return 'N/A';
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toString();
}

function getRSIClass(rsi) {
    if (!rsi) return 'neutral';
    if (rsi < 30) return 'oversold';
    if (rsi > 70) return 'overbought';
    return 'neutral';
}

function getVolumeClass(trend) {
    if (!trend) return 'neutral';
    if (trend.includes('High')) return 'high-volume';
    if (trend.includes('Low')) return 'low-volume';
    return 'normal-volume';
}

function addToWatchlist(symbol) {
    // Show feedback
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-check"></i> Added!';
    button.style.background = '#10b981';
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.style.background = '';
    }, 2000);
    
    console.log(`Adding ${symbol} to watchlist`);
}

function showBuyModal(symbol) {
    // Show simple feedback for now
    alert(`Buy modal would open for ${symbol}. This connects to your existing trading interface.`);
    console.log(`Opening buy modal for ${symbol}`);
}

function performStockSearch() {
    if (window.intelligentSearch) {
        window.intelligentSearch.performSearch();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.intelligentSearch = new IntelligentStockSearch();
    console.log('Intelligent Stock Search initialized');
});