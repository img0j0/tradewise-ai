/**
 * Simplified Two-Tier Search System - No conflicts
 */

// Simple global search system
window.simpleTwoTierSearch = {
    async performSearch(query) {
        try {
            console.log('Searching for:', query);
            
            // Show loading
            const resultsContainer = document.getElementById('ai-result');
            resultsContainer.style.display = 'block';
            resultsContainer.innerHTML = `
                <div style="text-align: center; padding: 40px; color: rgba(255,255,255,0.8);">
                    <div style="width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.2); border-top: 3px solid #06b6d4; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 15px;"></div>
                    <p>AI analyzing ${query}...</p>
                </div>
            `;
            
            // API call
            const response = await fetch('/api/stock-search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            const data = await response.json();
            this.displayResults(data);
            
        } catch (error) {
            console.error('Search error:', error);
            this.displayError(error.message);
        }
    },
    
    displayResults(data) {
        const resultsContainer = document.getElementById('ai-result');
        
        const html = `
            <div style="background: linear-gradient(135deg, rgba(16, 16, 32, 0.95), rgba(26, 26, 46, 0.95)); border-radius: 20px; padding: 25px; margin: 20px 0; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);">
                
                <!-- Stock Header -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                    <div>
                        <h2 style="font-size: 2.2em; font-weight: 700; color: #06b6d4; margin: 0;">${data.symbol}</h2>
                        <p style="color: rgba(255, 255, 255, 0.8); margin: 5px 0; font-size: 1.1em;">${data.name}</p>
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <span style="font-size: 1.8em; font-weight: 600; color: white;">$${data.price}</span>
                            <span style="padding: 6px 12px; border-radius: 15px; font-weight: 600; font-size: 0.9em; background: ${parseFloat(data.change_percent) >= 0 ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)'}; color: ${parseFloat(data.change_percent) >= 0 ? '#22c55e' : '#ef4444'};">${data.change_percent}%</span>
                        </div>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 10px;">
                        <span style="padding: 8px 16px; border-radius: 20px; font-weight: 600; font-size: 0.9em; text-transform: uppercase; background: rgba(251, 191, 36, 0.2); color: #fbbf24; border: 1px solid #fbbf24;">${data.ai_recommendation}</span>
                        <span style="background: rgba(139, 92, 246, 0.2); color: #8b5cf6; padding: 6px 12px; border-radius: 15px; font-size: 0.85em; font-weight: 500; border: 1px solid rgba(139, 92, 246, 0.3);">${data.confidence}% Confidence</span>
                    </div>
                </div>

                <!-- TIER 1: Quick Analysis -->
                <div style="background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; margin-bottom: 20px; border: 1px solid rgba(255, 255, 255, 0.1);">
                    <h3 style="color: #06b6d4; margin-bottom: 15px; font-size: 1.3em; display: flex; align-items: center; gap: 10px;">
                        <i class="fas fa-brain"></i> AI Quick Analysis
                    </h3>
                    <div>
                        <p style="line-height: 1.6; margin-bottom: 15px; color: rgba(255, 255, 255, 0.9);">
                            <strong>Market Position:</strong> ${data.name} is currently trading at $${data.price} with a market cap of $${(data.market_cap / 1e9).toFixed(1)}B in the Technology sector.
                        </p>
                        <p style="line-height: 1.6; margin-bottom: 15px; color: rgba(255, 255, 255, 0.9);">
                            <strong>AI Assessment:</strong> Our AI model rates this stock as ${data.ai_recommendation} with ${data.confidence}% confidence based on technical indicators, market sentiment, and fundamental metrics.
                        </p>
                        
                        <div style="margin: 20px 0;">
                            <div style="display: flex; align-items: center; gap: 15px;">
                                <div style="flex-grow: 1; height: 8px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden;">
                                    <div style="height: 100%; background: linear-gradient(90deg, #8b5cf6, #06b6d4); width: ${data.confidence}%; transition: width 0.5s ease;"></div>
                                </div>
                                <span style="font-weight: 600; color: #8b5cf6; white-space: nowrap;">${data.confidence}% AI Confidence</span>
                            </div>
                        </div>
                        
                        <div style="display: flex; gap: 25px; margin-top: 15px;">
                            <div style="display: flex; flex-direction: column; gap: 5px;">
                                <span style="color: rgba(255, 255, 255, 0.7); font-size: 0.85em;">Risk Level:</span>
                                <span style="font-weight: 600; font-size: 1.1em; color: #fbbf24;">${data.risk_level}</span>
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 5px;">
                                <span style="color: rgba(255, 255, 255, 0.7); font-size: 0.85em;">Market Cap:</span>
                                <span style="font-weight: 600; font-size: 1.1em; color: white;">$${(data.market_cap / 1e9).toFixed(1)}B</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div style="display: flex; gap: 15px; margin: 25px 0; flex-wrap: wrap;">
                    <button onclick="window.simpleTwoTierSearch.showDetailed('${data.symbol}')" style="flex: 1; min-width: 180px; padding: 12px 20px; border-radius: 12px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.3s ease; border: none; background: linear-gradient(135deg, #8b5cf6, #06b6d4); color: white; cursor: pointer;">
                        <i class="fas fa-chart-line"></i> View Detailed Technical Analysis
                    </button>
                    <button onclick="alert('Buy ${data.symbol}')" style="flex: 1; min-width: 180px; padding: 12px 20px; border-radius: 12px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.3s ease; border: none; background: linear-gradient(135deg, #22c55e, #16a34a); color: white; cursor: pointer;">
                        <i class="fas fa-shopping-cart"></i> Buy Stock
                    </button>
                    <button onclick="alert('Added ${data.symbol} to watchlist')" style="flex: 1; min-width: 180px; padding: 12px 20px; border-radius: 12px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.3s ease; border: none; background: rgba(255, 255, 255, 0.1); color: white; border: 1px solid rgba(255, 255, 255, 0.2); cursor: pointer;">
                        <i class="fas fa-star"></i> Add to Watchlist
                    </button>
                </div>

                <!-- TIER 2: Detailed Analysis (Initially Hidden) -->
                <div id="detailed-analysis-${data.symbol}" style="display: none; background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; margin-top: 20px; border: 1px solid rgba(255, 255, 255, 0.1); animation: slideDown 0.3s ease;">
                    <h3 style="color: #06b6d4; margin-bottom: 20px; font-size: 1.3em; display: flex; align-items: center; gap: 10px;">
                        <i class="fas fa-chart-bar"></i> Detailed Technical Analysis
                    </h3>
                    <div style="text-align: center; padding: 40px; color: rgba(255,255,255,0.8);">
                        <div style="width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.2); border-top: 2px solid #06b6d4; border-radius: 50%; animation: spin 1s linear infinite; display: inline-block; margin-right: 10px;"></div>
                        <span>Loading comprehensive technical analysis...</span>
                    </div>
                </div>
            </div>
        `;
        
        resultsContainer.innerHTML = html;
    },
    
    async showDetailed(symbol) {
        const detailedSection = document.getElementById(`detailed-analysis-${symbol}`);
        detailedSection.style.display = 'block';
        
        try {
            const response = await fetch('/api/stock-detailed-analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symbol: symbol })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            const data = await response.json();
            
            detailedSection.innerHTML = `
                <h3 style="color: #06b6d4; margin-bottom: 20px; font-size: 1.3em; display: flex; align-items: center; gap: 10px;">
                    <i class="fas fa-chart-bar"></i> Detailed Technical Analysis
                </h3>
                <div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 25px;">
                        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
                            <h4 style="color: rgba(255, 255, 255, 0.9); font-size: 0.95em; margin-bottom: 10px; font-weight: 600;">RSI (Relative Strength Index)</h4>
                            <div style="font-size: 1.4em; font-weight: 700; color: white; margin-bottom: 5px;">${data.rsi ? data.rsi.toFixed(2) : 'N/A'}</div>
                            <div style="font-size: 0.85em; padding: 4px 8px; border-radius: 8px; font-weight: 500; background: rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.8);">
                                ${data.rsi ? (data.rsi > 70 ? 'Overbought' : data.rsi < 30 ? 'Oversold' : 'Neutral range') : 'No data'}
                            </div>
                        </div>
                        
                        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
                            <h4 style="color: rgba(255, 255, 255, 0.9); font-size: 0.95em; margin-bottom: 10px; font-weight: 600;">MACD Signal</h4>
                            <div style="font-size: 1.4em; font-weight: 700; color: white; margin-bottom: 5px;">${data.macd_signal === 1 ? 'Bullish' : 'Bearish'}</div>
                            <div style="font-size: 0.85em; padding: 4px 8px; border-radius: 8px; font-weight: 500; background: ${data.macd_signal === 1 ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)'}; color: ${data.macd_signal === 1 ? '#22c55e' : '#ef4444'};">
                                ${data.macd_signal === 1 ? 'Upward momentum' : 'Downward pressure'}
                            </div>
                        </div>
                        
                        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
                            <h4 style="color: rgba(255, 255, 255, 0.9); font-size: 0.95em; margin-bottom: 10px; font-weight: 600;">52-Week Range</h4>
                            <div style="font-size: 1.1em; font-weight: 600; color: white; margin-bottom: 5px;">$${data.week_52_low} - $${data.week_52_high}</div>
                            <div style="font-size: 0.85em; padding: 4px 8px; border-radius: 8px; font-weight: 500; background: rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.8);">
                                Trading range
                            </div>
                        </div>
                        
                        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
                            <h4 style="color: rgba(255, 255, 255, 0.9); font-size: 0.95em; margin-bottom: 10px; font-weight: 600;">AI Price Target</h4>
                            <div style="font-size: 1.4em; font-weight: 700; color: white; margin-bottom: 5px;">$${data.price_target ? data.price_target.toFixed(2) : 'N/A'}</div>
                            <div style="font-size: 0.85em; padding: 4px 8px; border-radius: 8px; font-weight: 500; background: rgba(139, 92, 246, 0.2); color: #8b5cf6;">
                                AI prediction
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 25px; padding: 20px; background: rgba(139, 92, 246, 0.1); border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.2);">
                        <h4 style="color: #8b5cf6; margin-bottom: 10px; font-size: 1.1em;">Risk Assessment</h4>
                        <p style="line-height: 1.6; color: rgba(255, 255, 255, 0.9); margin: 0;">${data.risk_analysis || 'Risk analysis based on current market conditions and stock volatility.'}</p>
                    </div>
                </div>
            `;
            
        } catch (error) {
            detailedSection.innerHTML = `
                <h3 style="color: #06b6d4; margin-bottom: 20px;">Detailed Technical Analysis</h3>
                <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 20px; color: rgba(255, 255, 255, 0.9);">
                    Unable to load detailed analysis: ${error.message}
                </div>
            `;
        }
    },
    
    displayError(message) {
        const resultsContainer = document.getElementById('ai-result');
        resultsContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; color: rgba(255, 255, 255, 0.8);">
                <div style="font-size: 3em; margin-bottom: 15px;">⚠️</div>
                <h3>Search Error</h3>
                <p>${message}</p>
                <button onclick="document.getElementById('ai-result').style.display='none'" style="padding: 10px 20px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: white; cursor: pointer;">
                    Try Again
                </button>
            </div>
        `;
    }
};

// Override global functions with simple versions
window.performStockSearch = function() {
    const searchInput = document.getElementById('stock-search-input');
    const query = searchInput.value.trim();
    
    if (query) {
        window.simpleTwoTierSearch.performSearch(query);
    }
};

window.handleSearchEnter = function(event) {
    if (event.key === 'Enter') {
        window.performStockSearch();
    }
};

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);

console.log('Simple two-tier search system loaded successfully');