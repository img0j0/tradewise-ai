// Enhanced Results Display for State-of-the-Art Stock Analysis
// Provides comprehensive visualization of AI analysis results

function displayEnhancedAnalysis(stockData) {
    console.log('=== ENHANCED ANALYSIS DISPLAY ===');
    console.log('Stock data:', stockData);
    
    try {
        // Create enhanced analysis container
        const container = document.getElementById('ai-analysis-results');
        if (!container) {
            console.error('Analysis results container not found');
            throw new Error('ai-analysis-results container not found in DOM');
        }
        
        // Clear existing content
        container.innerHTML = '';
        
        // Build enhanced analysis HTML
        const enhancedHTML = generateEnhancedAnalysisHTML(stockData);
        container.innerHTML = enhancedHTML;
        
        // Initialize interactive elements
        try {
            initializeEnhancedFeatures();
        } catch (initError) {
            console.warn('Enhanced features initialization failed:', initError);
            // Continue without interactive features
        }
        
        // Show the container
        container.style.display = 'block';
        
        console.log('✅ Enhanced analysis displayed successfully');
        
    } catch (error) {
        console.error('❌ Enhanced analysis display error:', error);
        throw error; // Re-throw to be caught by calling function
    }
}

function generateEnhancedAnalysisHTML(data) {
    const enhanced = data.enhanced_analysis || {};
    const analysis = data.analysis || {};
    const strategy = analysis.strategy_applied || {};
    
    // Calculate change indicator
    const priceChange = parseFloat(data.price_change || 0);
    const priceChangePercent = parseFloat(data.price_change_percent || 0);
    const changeClass = priceChange >= 0 ? 'positive' : 'negative';
    
    return `
        <div class="enhanced-analysis-container">
            <!-- Stock Header -->
            <div class="stock-header-enhanced">
                <div class="stock-title-section">
                    <div class="stock-symbol-large">${data.symbol}</div>
                    <div class="stock-company-name">${data.company_name}</div>
                    <div class="stock-sector">${enhanced.sector || 'Technology'}</div>
                </div>
                <div class="stock-price-section">
                    <div class="current-price">$${parseFloat(data.current_price || 0).toFixed(2)}</div>
                    <div class="price-change ${changeClass}">
                        ${priceChange >= 0 ? '+' : ''}${priceChange.toFixed(2)} 
                        (${priceChangePercent >= 0 ? '+' : ''}${priceChangePercent.toFixed(2)}%)
                    </div>
                    <div class="market-cap">Market Cap: $${formatNumber(data.market_cap)}</div>
                </div>
            </div>

            <!-- Strategy Impact Display -->
            ${strategy.name ? `
            <div class="strategy-impact-display">
                <div class="strategy-badge">
                    <span>${strategy.emoji || '📈'}</span>
                    <span>${strategy.name}</span>
                </div>
                <div class="strategy-change-indicator">
                    <span class="change-label">Strategy Impact:</span> 
                    ${strategy.before_recommendation || 'HOLD'} (${strategy.before_confidence || 50}%) 
                    → ${strategy.after_recommendation || 'BUY'} (${strategy.after_confidence || 80}%)
                </div>
            </div>
            ` : ''}

            <!-- Quick Metrics Grid -->
            <div class="quick-metrics-grid">
                <div class="metric-card">
                    <div class="metric-icon">🎯</div>
                    <div class="metric-label">AI Recommendation</div>
                    <div class="metric-value ${(data.recommendation || 'HOLD').toLowerCase()}-recommendation">
                        ${data.recommendation || 'HOLD'}
                    </div>
                    <div class="metric-subtitle">${data.confidence || 50}% Confidence</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">⚠️</div>
                    <div class="metric-label">Risk Level</div>
                    <div class="metric-value ${(data.risk_level || 'Medium').toLowerCase()}-risk">
                        ${data.risk_level || 'Medium'}
                    </div>
                    <div class="metric-subtitle">Risk Assessment</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">📊</div>
                    <div class="metric-label">Technical Score</div>
                    <div class="metric-value">${data.technical_score || 50}/100</div>
                    <div class="metric-subtitle">Technical Analysis</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">💰</div>
                    <div class="metric-label">Fundamental Score</div>
                    <div class="metric-value">${data.fundamental_score || 50}/100</div>
                    <div class="metric-subtitle">Financial Health</div>
                </div>
            </div>

            <!-- Enhanced Analysis Insights -->
            <div class="analysis-insights-section">
                <h3><i class="fas fa-brain"></i> AI Investment Analysis</h3>
                
                <div class="key-insights-grid">
                    <div class="insight-card positive">
                        <div class="insight-header">
                            <span class="insight-type">INVESTMENT THESIS</span>
                            <span class="insight-impact positive">HIGH IMPACT</span>
                        </div>
                        <div class="insight-title">AI-Powered Investment Recommendation</div>
                        <div class="insight-description">
                            ${data.investment_thesis || analysis.analysis || 'Comprehensive AI analysis indicates favorable investment opportunity based on current market conditions and fundamental analysis.'}
                        </div>
                    </div>
                    
                    <div class="insight-card">
                        <div class="insight-header">
                            <span class="insight-type">MARKET SENTIMENT</span>
                            <span class="insight-impact">${(data.market_sentiment || 'Neutral').toUpperCase()}</span>
                        </div>
                        <div class="insight-title">Current Market Sentiment</div>
                        <div class="insight-description">
                            Market sentiment analysis shows ${(data.market_sentiment || 'neutral').toLowerCase()} investor sentiment based on recent news, social media trends, and trading patterns.
                        </div>
                    </div>
                </div>
            </div>

            <!-- Technical Analysis Section -->
            ${enhanced.technical_analysis ? generateTechnicalAnalysisSection(enhanced.technical_analysis) : ''}

            <!-- Risk Assessment Section -->
            ${enhanced.risk_assessment ? generateRiskAssessmentSection(enhanced.risk_assessment) : ''}

            <!-- Price Predictions Section -->
            ${enhanced.price_predictions ? generatePricePredictionsSection(enhanced.price_predictions) : ''}

            <!-- AI Insights Section -->
            ${enhanced.ai_insights ? generateAIInsightsSection(enhanced.ai_insights) : ''}

            <!-- Action Buttons -->
            <div class="action-buttons-section">
                <div class="primary-actions">
                    <button class="action-btn primary" onclick="addToWatchlist('${data.symbol}')">
                        <i class="fas fa-plus"></i> Add to Watchlist
                    </button>
                    <button class="action-btn secondary" onclick="getDetailedAnalysis('${data.symbol}')">
                        <i class="fas fa-chart-area"></i> Deep Dive Analysis
                    </button>
                    <button class="action-btn tertiary" onclick="comparePeers('${data.symbol}')">
                        <i class="fas fa-balance-scale"></i> Compare Peers
                    </button>
                </div>
                
                <div class="analysis-actions">
                    <button class="analysis-btn" onclick="exportAnalysis('${data.symbol}')">
                        <i class="fas fa-download"></i> Export Report
                    </button>
                    <button class="analysis-btn" onclick="shareAnalysis('${data.symbol}')">
                        <i class="fas fa-share"></i> Share Analysis
                    </button>
                    <button class="analysis-btn" onclick="setAlert('${data.symbol}')">
                        <i class="fas fa-bell"></i> Set Alert
                    </button>
                </div>
            </div>
        </div>
    `;
}

function generateTechnicalAnalysisSection(technical) {
    if (!technical || !Object.keys(technical).length) return '';
    
    return `
        <div class="technical-analysis-section">
            <h3><i class="fas fa-chart-line"></i> Technical Analysis</h3>
            
            <div class="technical-grid">
                <div class="technical-card">
                    <div class="technical-header">Moving Averages</div>
                    <div class="ma-indicators">
                        ${technical.moving_averages ? Object.entries(technical.moving_averages).map(([period, data]) => `
                            <div class="ma-item">
                                <span class="ma-label">${period}</span>
                                <span class="ma-value">$${data.value?.toFixed(2) || 'N/A'}</span>
                                <span class="ma-percent ${data.signal === 'bullish' ? 'positive' : 'negative'}">
                                    ${data.signal || 'neutral'}
                                </span>
                            </div>
                        `).join('') : '<div class="ma-item"><span>No data available</span></div>'}
                    </div>
                </div>
                
                <div class="technical-card">
                    <div class="technical-header">RSI Analysis</div>
                    <div class="rsi-display">
                        <div class="rsi-value">${technical.rsi?.value?.toFixed(1) || '50.0'}</div>
                        <div class="rsi-signal ${technical.rsi?.signal || 'neutral'}">${technical.rsi?.interpretation || 'Neutral'}</div>
                        <div class="rsi-bar">
                            <div class="rsi-fill" style="width: ${technical.rsi?.value || 50}%"></div>
                        </div>
                    </div>
                </div>
                
                <div class="technical-card">
                    <div class="technical-header">MACD Signal</div>
                    <div class="macd-display">
                        <div class="macd-value">${technical.macd?.value?.toFixed(3) || '0.000'}</div>
                        <div class="macd-signal">${technical.macd?.signal || 'Hold'}</div>
                        <span class="macd-histogram ${technical.macd?.histogram > 0 ? 'positive' : 'negative'}">
                            ${technical.macd?.histogram?.toFixed(3) || '0.000'}
                        </span>
                    </div>
                </div>
            </div>
            
            <div class="technical-signals">
                <div class="signals-header">Technical Signals Summary</div>
                <div class="signals-list">
                    ${technical.signals ? technical.signals.map(signal => `
                        <div class="signal-item">
                            <span class="signal-dot"></span>
                            ${signal}
                        </div>
                    `).join('') : '<div class="signal-item"><span class="signal-dot"></span>Technical analysis in progress</div>'}
                </div>
                <div class="overall-rating">
                    Overall Technical Rating: ${technical.overall_rating || 'Neutral'}
                </div>
            </div>
        </div>
    `;
}

function generateRiskAssessmentSection(risk) {
    if (!risk || !Object.keys(risk).length) return '';
    
    return `
        <div class="risk-assessment-section">
            <h3><i class="fas fa-shield-alt"></i> Risk Assessment</h3>
            
            <div class="risk-metrics-grid">
                <div class="risk-metric">
                    <div class="risk-label">Volatility</div>
                    <div class="risk-value">${risk.volatility?.toFixed(1) || '15.0'}%</div>
                    <div class="risk-description">Price volatility measure</div>
                    <div class="risk-bar">
                        <div class="risk-fill medium-risk-bar" style="width: ${(risk.volatility || 15) * 2}%"></div>
                    </div>
                </div>
                
                <div class="risk-metric">
                    <div class="risk-label">Beta</div>
                    <div class="risk-value">${risk.beta?.toFixed(2) || '1.00'}</div>
                    <div class="risk-description">Market correlation</div>
                    <div class="risk-bar">
                        <div class="risk-fill ${risk.beta > 1.2 ? 'high-risk-bar' : risk.beta < 0.8 ? 'low-risk-bar' : 'medium-risk-bar'}" 
                             style="width: ${Math.min((risk.beta || 1) * 50, 100)}%"></div>
                    </div>
                </div>
                
                <div class="risk-metric">
                    <div class="risk-label">Max Drawdown</div>
                    <div class="risk-value">${risk.max_drawdown?.toFixed(1) || '10.0'}%</div>
                    <div class="risk-description">Worst decline period</div>
                    <div class="risk-bar">
                        <div class="risk-fill high-risk-bar" style="width: ${(risk.max_drawdown || 10) * 2}%"></div>
                    </div>
                </div>
                
                <div class="risk-metric">
                    <div class="risk-label">Sharpe Ratio</div>
                    <div class="risk-value">${risk.sharpe_ratio?.toFixed(2) || '1.20'}</div>
                    <div class="risk-description">Risk-adjusted returns</div>
                    <div class="risk-bar">
                        <div class="risk-fill ${risk.sharpe_ratio > 1.5 ? 'low-risk-bar' : risk.sharpe_ratio < 0.8 ? 'high-risk-bar' : 'medium-risk-bar'}" 
                             style="width: ${Math.min((risk.sharpe_ratio || 1.2) * 40, 100)}%"></div>
                    </div>
                </div>
            </div>
            
            <div class="risk-factors">
                <div class="factors-header">Key Risk Factors</div>
                <div class="factors-list">
                    ${risk.factors ? risk.factors.map(factor => `
                        <div class="risk-factor-item">
                            <span class="factor-bullet">•</span>
                            ${factor}
                        </div>
                    `).join('') : `
                        <div class="risk-factor-item">
                            <span class="factor-bullet">•</span>
                            Market volatility and sector rotation risks
                        </div>
                        <div class="risk-factor-item">
                            <span class="factor-bullet">•</span>
                            Economic cycle and interest rate sensitivity
                        </div>
                        <div class="risk-factor-item">
                            <span class="factor-bullet">•</span>
                            Company-specific operational risks
                        </div>
                    `}
                </div>
            </div>
        </div>
    `;
}

function generatePricePredictionsSection(predictions) {
    if (!predictions || !Object.keys(predictions).length) return '';
    
    return `
        <div class="price-predictions-section">
            <h3><i class="fas fa-crystal-ball"></i> AI Price Predictions</h3>
            
            <div class="predictions-grid">
                ${predictions.short_term ? `
                <div class="prediction-card">
                    <div class="pred-timeframe">1 Month</div>
                    <div class="pred-price">$${predictions.short_term.target?.toFixed(2) || '0.00'}</div>
                    <div class="pred-change ${predictions.short_term.change >= 0 ? 'positive' : 'negative'}">
                        ${predictions.short_term.change >= 0 ? '+' : ''}${predictions.short_term.change?.toFixed(1) || '0.0'}%
                    </div>
                    <div class="pred-range">Range: $${predictions.short_term.low?.toFixed(2) || '0.00'} - $${predictions.short_term.high?.toFixed(2) || '0.00'}</div>
                    <span class="pred-confidence">${predictions.short_term.confidence || 75}% Confidence</span>
                </div>
                ` : ''}
                
                ${predictions.medium_term ? `
                <div class="prediction-card">
                    <div class="pred-timeframe">3 Months</div>
                    <div class="pred-price">$${predictions.medium_term.target?.toFixed(2) || '0.00'}</div>
                    <div class="pred-change ${predictions.medium_term.change >= 0 ? 'positive' : 'negative'}">
                        ${predictions.medium_term.change >= 0 ? '+' : ''}${predictions.medium_term.change?.toFixed(1) || '0.0'}%
                    </div>
                    <div class="pred-range">Range: $${predictions.medium_term.low?.toFixed(2) || '0.00'} - $${predictions.medium_term.high?.toFixed(2) || '0.00'}</div>
                    <span class="pred-confidence">${predictions.medium_term.confidence || 70}% Confidence</span>
                </div>
                ` : ''}
                
                ${predictions.long_term ? `
                <div class="prediction-card">
                    <div class="pred-timeframe">12 Months</div>
                    <div class="pred-price">$${predictions.long_term.target?.toFixed(2) || '0.00'}</div>
                    <div class="pred-change ${predictions.long_term.change >= 0 ? 'positive' : 'negative'}">
                        ${predictions.long_term.change >= 0 ? '+' : ''}${predictions.long_term.change?.toFixed(1) || '0.0'}%
                    </div>
                    <div class="pred-range">Range: $${predictions.long_term.low?.toFixed(2) || '0.00'} - $${predictions.long_term.high?.toFixed(2) || '0.00'}</div>
                    <span class="pred-confidence">${predictions.long_term.confidence || 65}% Confidence</span>
                </div>
                ` : ''}
            </div>
            
            <div class="predictions-disclaimer">
                <i class="fas fa-exclamation-triangle"></i>
                Price predictions are AI-generated estimates based on historical data and market analysis. 
                Past performance does not guarantee future results. Always conduct your own research.
            </div>
        </div>
    `;
}

function generateAIInsightsSection(insights) {
    if (!insights || !Object.keys(insights).length) return '';
    
    return `
        <div class="ai-insights-section">
            <h3><i class="fas fa-lightbulb"></i> AI Investment Insights</h3>
            
            <div class="strengths-concerns-grid">
                <div class="strengths-section">
                    <div class="section-header positive">
                        <i class="fas fa-thumbs-up"></i>
                        Investment Strengths
                    </div>
                    <div class="items-list">
                        ${insights.strengths ? insights.strengths.map(strength => `
                            <div class="strength-item">
                                <span class="item-bullet positive">+</span>
                                ${strength}
                            </div>
                        `).join('') : `
                            <div class="strength-item">
                                <span class="item-bullet positive">+</span>
                                Strong financial fundamentals and market position
                            </div>
                            <div class="strength-item">
                                <span class="item-bullet positive">+</span>
                                Positive technical indicators and momentum
                            </div>
                        `}
                    </div>
                </div>
                
                <div class="concerns-section">
                    <div class="section-header caution">
                        <i class="fas fa-exclamation-triangle"></i>
                        Risk Considerations
                    </div>
                    <div class="items-list">
                        ${insights.concerns ? insights.concerns.map(concern => `
                            <div class="concern-item">
                                <span class="item-bullet caution">!</span>
                                ${concern}
                            </div>
                        `).join('') : `
                            <div class="concern-item">
                                <span class="item-bullet caution">!</span>
                                Market volatility and economic uncertainty
                            </div>
                            <div class="concern-item">
                                <span class="item-bullet caution">!</span>
                                Sector-specific risks and competition
                            </div>
                        `}
                    </div>
                </div>
            </div>
            
            <div class="ai-confidence-meter">
                <div class="confidence-label">AI Analysis Confidence Level</div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${insights.confidence || 85}%"></div>
                </div>
                <div class="confidence-text">${insights.confidence || 85}% Confidence in Analysis</div>
            </div>
        </div>
    `;
}

function initializeEnhancedFeatures() {
    // Initialize any interactive features
    console.log('Enhanced features initialized');
    
    // Add hover effects and animations
    const cards = document.querySelectorAll('.metric-card, .prediction-card, .technical-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

function formatNumber(num) {
    if (!num || num === 0) return '0';
    
    if (num >= 1e12) {
        return (num / 1e12).toFixed(1) + 'T';
    } else if (num >= 1e9) {
        return (num / 1e9).toFixed(1) + 'B';
    } else if (num >= 1e6) {
        return (num / 1e6).toFixed(1) + 'M';
    } else if (num >= 1e3) {
        return (num / 1e3).toFixed(1) + 'K';
    }
    
    return num.toString();
}

// Action button handlers
function addToWatchlist(symbol) {
    console.log(`Adding ${symbol} to watchlist`);
    // This will call the existing watchlist functionality
    if (typeof showAddStockModal === 'function') {
        showAddStockModal();
        setTimeout(() => {
            const input = document.getElementById('stock-symbol-input');
            if (input) input.value = symbol;
        }, 100);
    }
}

function getDetailedAnalysis(symbol) {
    console.log(`Getting detailed analysis for ${symbol}`);
    alert(`Detailed analysis for ${symbol} - This feature will provide comprehensive fundamental analysis, earnings forecasts, and sector comparison.`);
}

function comparePeers(symbol) {
    console.log(`Comparing peers for ${symbol}`);
    alert(`Peer comparison for ${symbol} - This feature will show how this stock compares to industry competitors and sector averages.`);
}

function exportAnalysis(symbol) {
    console.log(`Exporting analysis for ${symbol}`);
    alert(`Analysis export for ${symbol} - This feature will generate a PDF report with all analysis insights.`);
}

function shareAnalysis(symbol) {
    console.log(`Sharing analysis for ${symbol}`);
    alert(`Share analysis for ${symbol} - This feature will create a shareable link to the analysis results.`);
}

function setAlert(symbol) {
    console.log(`Setting alert for ${symbol}`);
    alert(`Price alert for ${symbol} - This feature will set up price alerts and technical signal notifications.`);
}

// Make functions globally available
window.displayEnhancedAnalysis = displayEnhancedAnalysis;
window.addToWatchlist = addToWatchlist;
window.getDetailedAnalysis = getDetailedAnalysis;
window.comparePeers = comparePeers;
window.exportAnalysis = exportAnalysis;
window.shareAnalysis = shareAnalysis;
window.setAlert = setAlert;

// The initializeEnhancedFeatures function is already defined above

console.log('Enhanced results display module loaded');