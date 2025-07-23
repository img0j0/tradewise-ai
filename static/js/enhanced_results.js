// Enhanced Stock Analysis Results Display
// State-of-the-art visualization and insights

function displayEnhancedAnalysis(data) {
    const resultsContainer = document.getElementById('analysis-results');
    if (!resultsContainer) return;
    
    // Build enhanced results HTML
    const enhancedHTML = `
        <div class="enhanced-analysis-container">
            ${buildStockHeader(data)}
            ${buildQuickMetrics(data)}
            ${buildAnalysisInsights(data)}
            ${buildTechnicalAnalysis(data)}
            ${buildRiskAssessment(data)}
            ${buildPricePredictions(data)}
            ${buildAIInsights(data)}
            ${buildActionButtons(data)}
        </div>
    `;
    
    resultsContainer.innerHTML = enhancedHTML;
    resultsContainer.style.display = 'block';
    
    // Add interactive features
    initializeEnhancedFeatures();
}

function buildStockHeader(data) {
    const enhanced = data.enhanced_analysis || {};
    const marketPos = enhanced.enhanced_metrics?.market_position || {};
    
    return `
        <div class="stock-header-enhanced">
            <div class="stock-title-section">
                <div class="stock-symbol-large">${data.symbol}</div>
                <div class="stock-company-name">${data.company_name || data.symbol}</div>
                <div class="stock-sector">${marketPos.sector || ''} • ${marketPos.market_cap_class || ''}</div>
            </div>
            <div class="stock-price-section">
                <div class="current-price">$${(data.current_price || 0).toFixed(2)}</div>
                <div class="price-change ${data.price_change >= 0 ? 'positive' : 'negative'}">
                    ${data.price_change >= 0 ? '+' : ''}${(data.price_change || 0).toFixed(2)} 
                    (${data.price_change_percent >= 0 ? '+' : ''}${(data.price_change_percent || 0).toFixed(2)}%)
                </div>
                <div class="market-cap">Market Cap: ${formatMarketCap(data.market_cap || 0)}</div>
            </div>
        </div>
    `;
}

function buildQuickMetrics(data) {
    const enhanced = data.enhanced_analysis || {};
    const recommendation = enhanced.recommendation || data.analysis?.recommendation || {};
    
    return `
        <div class="quick-metrics-grid">
            <div class="metric-card recommendation-card">
                <div class="metric-icon">🎯</div>
                <div class="metric-label">AI Recommendation</div>
                <div class="metric-value ${getRecommendationClass(recommendation.recommendation)}">${recommendation.recommendation || 'HOLD'}</div>
                <div class="metric-subtitle">${recommendation.confidence || 50}% Confidence</div>
            </div>
            
            <div class="metric-card sentiment-card">
                <div class="metric-icon">📊</div>
                <div class="metric-label">Market Sentiment</div>
                <div class="metric-value">${enhanced.sentiment_analysis?.sentiment_label || 'Neutral'}</div>
                <div class="metric-subtitle">Score: ${enhanced.sentiment_analysis?.sentiment_score || 0}</div>
            </div>
            
            <div class="metric-card risk-card">
                <div class="metric-icon">⚠️</div>
                <div class="metric-label">Risk Level</div>
                <div class="metric-value ${getRiskClass(enhanced.risk_assessment?.risk_level)}">${enhanced.risk_assessment?.risk_level || 'Medium'}</div>
                <div class="metric-subtitle">${enhanced.risk_assessment?.volatility_annual || 0}% Volatility</div>
            </div>
            
            <div class="metric-card momentum-card">
                <div class="metric-icon">🚀</div>
                <div class="metric-label">Momentum</div>
                <div class="metric-value">${enhanced.enhanced_metrics?.momentum?.trend || 'Neutral'}</div>
                <div class="metric-subtitle">3M: ${enhanced.enhanced_metrics?.momentum?.['3_month'] || 0}%</div>
            </div>
        </div>
    `;
}

function buildAnalysisInsights(data) {
    const analysis = data.analysis || {};
    const enhanced = data.enhanced_analysis || {};
    
    return `
        <div class="analysis-insights-section">
            <h3>💡 AI Analysis Insights</h3>
            
            <div class="strategy-impact-display">
                ${analysis.strategy_applied ? `
                    <div class="strategy-badge">
                        <span class="strategy-icon">${analysis.strategy_applied.icon}</span>
                        <span class="strategy-name">${analysis.strategy_applied.name}</span>
                    </div>
                ` : ''}
                
                ${analysis.strategy_impact?.changed ? `
                    <div class="strategy-change-indicator">
                        <span class="change-label">Strategy Impact:</span>
                        <span class="change-detail">
                            ${analysis.strategy_impact.original_recommendation} (${analysis.strategy_impact.original_confidence}%) 
                            → ${analysis.recommendation} (${analysis.confidence}%)
                        </span>
                    </div>
                ` : ''}
            </div>
            
            <div class="key-insights-grid">
                ${enhanced.ai_insights?.insights?.map(insight => `
                    <div class="insight-card ${insight.impact?.toLowerCase() || 'neutral'}">
                        <div class="insight-header">
                            <span class="insight-type">${insight.type?.toUpperCase() || 'ANALYSIS'}</span>
                            <span class="insight-impact ${insight.impact?.toLowerCase() || 'neutral'}">${insight.impact || 'Neutral'}</span>
                        </div>
                        <div class="insight-title">${insight.title || 'Market Analysis'}</div>
                        <div class="insight-description">${insight.description || 'Comprehensive market evaluation'}</div>
                    </div>
                `).join('') || '<div class="no-insights">Advanced insights processing...</div>'}
            </div>
        </div>
    `;
}

function buildTechnicalAnalysis(data) {
    const technical = data.enhanced_analysis?.technical_analysis || {};
    
    return `
        <div class="technical-analysis-section">
            <h3>📈 Technical Analysis</h3>
            
            <div class="technical-grid">
                <div class="technical-card">
                    <div class="technical-header">Moving Averages</div>
                    <div class="ma-indicators">
                        <div class="ma-item">
                            <span class="ma-label">20-Day MA:</span>
                            <span class="ma-value">$${technical.moving_averages?.ma_20 || 0}</span>
                            <span class="ma-percent ${technical.moving_averages?.price_vs_ma20 >= 0 ? 'positive' : 'negative'}">
                                ${technical.moving_averages?.price_vs_ma20 >= 0 ? '+' : ''}${technical.moving_averages?.price_vs_ma20 || 0}%
                            </span>
                        </div>
                        <div class="ma-item">
                            <span class="ma-label">50-Day MA:</span>
                            <span class="ma-value">$${technical.moving_averages?.ma_50 || 0}</span>
                            <span class="ma-percent ${technical.moving_averages?.price_vs_ma50 >= 0 ? 'positive' : 'negative'}">
                                ${technical.moving_averages?.price_vs_ma50 >= 0 ? '+' : ''}${technical.moving_averages?.price_vs_ma50 || 0}%
                            </span>
                        </div>
                    </div>
                </div>
                
                <div class="technical-card">
                    <div class="technical-header">RSI Indicator</div>
                    <div class="rsi-display">
                        <div class="rsi-value">${technical.rsi?.current || 50}</div>
                        <div class="rsi-signal ${getRSIClass(technical.rsi?.current)}">${technical.rsi?.signal || 'Neutral'}</div>
                        <div class="rsi-bar">
                            <div class="rsi-fill" style="width: ${technical.rsi?.current || 50}%"></div>
                        </div>
                    </div>
                </div>
                
                <div class="technical-card">
                    <div class="technical-header">MACD</div>
                    <div class="macd-display">
                        <div class="macd-value">${technical.macd?.value || 0}</div>
                        <div class="macd-signal">${technical.macd?.trend || 'Neutral'}</div>
                        <div class="macd-histogram ${technical.macd?.histogram >= 0 ? 'positive' : 'negative'}">
                            ${technical.macd?.histogram || 0}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="technical-signals">
                <div class="signals-header">Technical Signals</div>
                <div class="signals-list">
                    ${technical.technical_signals?.map(signal => `
                        <div class="signal-item">
                            <span class="signal-dot"></span>
                            <span class="signal-text">${signal}</span>
                        </div>
                    `).join('') || '<div class="signal-item">No significant signals detected</div>'}
                </div>
                <div class="overall-rating">
                    <strong>Overall Technical Rating: ${technical.overall_technical_rating || 'Hold'}</strong>
                </div>
            </div>
        </div>
    `;
}

function buildRiskAssessment(data) {
    const risk = data.enhanced_analysis?.risk_assessment || {};
    
    return `
        <div class="risk-assessment-section">
            <h3>⚠️ Risk Assessment</h3>
            
            <div class="risk-metrics-grid">
                <div class="risk-metric">
                    <div class="risk-label">Annual Volatility</div>
                    <div class="risk-value">${risk.volatility_annual || 0}%</div>
                    <div class="risk-bar">
                        <div class="risk-fill ${getRiskBarClass(risk.volatility_annual)}" 
                             style="width: ${Math.min(100, (risk.volatility_annual || 0) * 2)}%"></div>
                    </div>
                </div>
                
                <div class="risk-metric">
                    <div class="risk-label">Value at Risk (95%)</div>
                    <div class="risk-value">${risk.value_at_risk_95 || 0}%</div>
                    <div class="risk-description">Daily loss potential</div>
                </div>
                
                <div class="risk-metric">
                    <div class="risk-label">Max Drawdown</div>
                    <div class="risk-value">${risk.max_drawdown || 0}%</div>
                    <div class="risk-description">Historical worst decline</div>
                </div>
            </div>
            
            <div class="risk-factors">
                <div class="factors-header">Key Risk Factors:</div>
                <div class="factors-list">
                    ${risk.risk_factors?.map(factor => `
                        <div class="risk-factor-item">
                            <span class="factor-bullet">•</span>
                            <span class="factor-text">${factor}</span>
                        </div>
                    `).join('') || '<div class="risk-factor-item">Standard market risks apply</div>'}
                </div>
            </div>
        </div>
    `;
}

function buildPricePredictions(data) {
    const predictions = data.enhanced_analysis?.price_predictions?.predictions || {};
    
    return `
        <div class="price-predictions-section">
            <h3>🔮 AI Price Predictions</h3>
            
            <div class="predictions-grid">
                ${Object.entries(predictions).map(([timeframe, pred]) => `
                    <div class="prediction-card">
                        <div class="pred-timeframe">${timeframe.replace('_', ' ').toUpperCase()}</div>
                        <div class="pred-price">$${pred.expected_price || 0}</div>
                        <div class="pred-change ${pred.change_percent >= 0 ? 'positive' : 'negative'}">
                            ${pred.change_percent >= 0 ? '+' : ''}${pred.change_percent || 0}%
                        </div>
                        <div class="pred-range">
                            Range: $${pred.lower_bound || 0} - $${pred.upper_bound || 0}
                        </div>
                        <div class="pred-confidence">${pred.confidence || 95}% Confidence</div>
                    </div>
                `).join('') || '<div class="no-predictions">Prediction models processing...</div>'}
            </div>
            
            <div class="predictions-disclaimer">
                <small>⚠️ Predictions are estimates based on historical data and should not be used as sole investment criteria.</small>
            </div>
        </div>
    `;
}

function buildAIInsights(data) {
    const aiInsights = data.enhanced_analysis?.ai_insights || {};
    
    return `
        <div class="ai-insights-section">
            <h3>🤖 AI Investment Intelligence</h3>
            
            <div class="strengths-concerns-grid">
                <div class="strengths-section">
                    <div class="section-header positive">💪 Key Strengths</div>
                    <div class="items-list">
                        ${aiInsights.key_strengths?.map(strength => `
                            <div class="strength-item">
                                <span class="item-bullet positive">✓</span>
                                <span class="item-text">${strength}</span>
                            </div>
                        `).join('') || '<div class="strength-item">Analysis in progress...</div>'}
                    </div>
                </div>
                
                <div class="concerns-section">
                    <div class="section-header caution">⚠️ Key Concerns</div>
                    <div class="items-list">
                        ${aiInsights.key_concerns?.map(concern => `
                            <div class="concern-item">
                                <span class="item-bullet caution">!</span>
                                <span class="item-text">${concern}</span>
                            </div>
                        `).join('') || '<div class="concern-item">No significant concerns identified</div>'}
                    </div>
                </div>
            </div>
            
            <div class="ai-confidence-meter">
                <div class="confidence-label">AI Analysis Confidence</div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${getConfidenceWidth(aiInsights.ai_confidence)}%"></div>
                </div>
                <div class="confidence-text">${aiInsights.ai_confidence || 'Medium'} Confidence</div>
            </div>
        </div>
    `;
}

function buildActionButtons(data) {
    return `
        <div class="action-buttons-section">
            <div class="primary-actions">
                <button class="action-btn primary" onclick="addToWatchlist('${data.symbol}')">
                    📋 Add to Watchlist
                </button>
                <button class="action-btn secondary" onclick="createSmartAlert('${data.symbol}')">
                    🔔 Smart Alerts
                </button>
                <button class="action-btn tertiary" onclick="showComparison('${data.symbol}')">
                    ⚖️ Compare Stocks
                </button>
            </div>
            
            <div class="analysis-actions">
                <button class="analysis-btn" onclick="exportAnalysis('${data.symbol}')">
                    📄 Export Analysis
                </button>
                <button class="analysis-btn" onclick="shareAnalysis('${data.symbol}')">
                    📤 Share
                </button>
            </div>
        </div>
    `;
}

// Helper functions
function formatMarketCap(marketCap) {
    if (marketCap >= 1000000000000) {
        return '$' + (marketCap / 1000000000000).toFixed(2) + 'T';
    } else if (marketCap >= 1000000000) {
        return '$' + (marketCap / 1000000000).toFixed(2) + 'B';
    } else if (marketCap >= 1000000) {
        return '$' + (marketCap / 1000000).toFixed(2) + 'M';
    } else {
        return '$' + marketCap.toLocaleString();
    }
}

function getRecommendationClass(recommendation) {
    switch (recommendation?.toLowerCase()) {
        case 'buy':
        case 'strong buy':
            return 'buy-recommendation';
        case 'sell':
        case 'strong sell':
            return 'sell-recommendation';
        default:
            return 'hold-recommendation';
    }
}

function getRiskClass(riskLevel) {
    switch (riskLevel?.toLowerCase()) {
        case 'high':
            return 'high-risk';
        case 'low':
            return 'low-risk';
        default:
            return 'medium-risk';
    }
}

function getRSIClass(rsiValue) {
    if (rsiValue > 70) return 'overbought';
    if (rsiValue < 30) return 'oversold';
    return 'neutral';
}

function getRiskBarClass(volatility) {
    if (volatility > 30) return 'high-risk-bar';
    if (volatility > 15) return 'medium-risk-bar';
    return 'low-risk-bar';
}

function getConfidenceWidth(confidence) {
    switch (confidence?.toLowerCase()) {
        case 'high':
            return 85;
        case 'low':
            return 45;
        default:
            return 65;
    }
}

function initializeEnhancedFeatures() {
    // Add smooth scroll animations
    const sections = document.querySelectorAll('.enhanced-analysis-container > div');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        setTimeout(() => {
            section.style.transition = 'all 0.6s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Action button handlers
function addToWatchlist(symbol) {
    // Implementation will connect to existing watchlist functionality
    console.log('Adding to watchlist:', symbol);
    showNotification(`${symbol} added to watchlist`, 'success');
}

function createSmartAlert(symbol) {
    // Implementation will connect to existing alert functionality
    console.log('Creating smart alert for:', symbol);
    showNotification('Smart alert creator opening...', 'info');
}

function showComparison(symbol) {
    console.log('Opening comparison for:', symbol);
    showNotification('Stock comparison feature coming soon', 'info');
}

function exportAnalysis(symbol) {
    console.log('Exporting analysis for:', symbol);
    showNotification('Analysis export feature coming soon', 'info');
}

function shareAnalysis(symbol) {
    console.log('Sharing analysis for:', symbol);
    showNotification('Analysis sharing feature coming soon', 'info');
}

function showNotification(message, type = 'info') {
    // Simple notification system
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#06b6d4'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        font-weight: 600;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}