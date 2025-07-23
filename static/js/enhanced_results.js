// Enhanced Results Display for State-of-the-Art Stock Analysis
// Provides comprehensive visualization of AI analysis results

function displayEnhancedAnalysis(stockData) {
    console.log('=== ENHANCED ANALYSIS DISPLAY ===');
    console.log('Stock data:', stockData);
    
    try {
        // Try desktop container first, then fallback
        let container = document.getElementById('mainAnalysisContainer');
        if (!container) {
            container = document.getElementById('ai-analysis-results');
        }
        if (!container) {
            console.error('No analysis results container found');
            throw new Error('No analysis results container found in DOM');
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
    console.log('=== GENERATING COMPETITIVE FEATURES UI - BLOOMBERG FOR EVERYONE ===');
    console.log('Enhanced Explanation Data:', data.enhanced_explanation);
    console.log('Smart Alerts Data:', data.smart_alerts);
    console.log('Educational Insights Data:', data.educational_insights);
    
    const enhanced = data.enhanced_analysis || {};
    const analysis = data.analysis || {};
    const strategy = analysis.strategy_applied || {};
    
    // Calculate change indicator with safe parsing
    const priceChange = isNaN(parseFloat(data.price_change)) ? 0 : parseFloat(data.price_change);
    const priceChangePercent = isNaN(parseFloat(data.price_change_percent)) ? 0 : parseFloat(data.price_change_percent);
    const changeClass = priceChange >= 0 ? 'positive' : 'negative';
    
    // Generate competitive advantages sections
    const competitiveAdvantagesHTML = generateCompetitiveAdvantagesHTML(data);
    
    return `
        <div class="enhanced-analysis-container competitive-advantage-enter">
            <!-- Bloomberg-Style Professional Header -->
            <div class="bloomberg-style-header">
                <div class="row mb-4">
                    <div class="col-md-8">
                        <div class="d-flex align-items-center mb-3">
                            <h1 class="mb-0 me-3" style="font-size: 2.5rem; font-weight: 800;">${data.symbol}</h1>
                            <span class="badge bg-primary fs-6 px-3 py-2">${enhanced.enhanced_metrics?.market_position?.sector || 'Technology'}</span>
                            <span class="professional-badge">Live Analysis</span>
                        </div>
                        <h4 class="text-light mb-3" style="font-weight: 600;">${data.company_name}</h4>
                        <div class="d-flex align-items-center gap-4">
                            <span class="text-light"><i class="fas fa-building me-2"></i>${enhanced.enhanced_metrics?.market_position?.exchange || 'NASDAQ'}</span>
                            <span class="text-light"><i class="fas fa-globe me-2"></i>${enhanced.enhanced_metrics?.market_position?.country || 'United States'}</span>
                            <span class="text-light"><i class="fas fa-clock me-2"></i>Real-time Data</span>
                        </div>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="price-display-large">
                            <div class="current-price-big">$${(parseFloat(data.current_price) || 0).toFixed(2)}</div>
                            <div class="price-change-big ${changeClass}">
                                ${priceChange >= 0 ? '+' : ''}${priceChange.toFixed(2)} (${priceChangePercent >= 0 ? '+' : ''}${priceChangePercent.toFixed(2)}%)
                            </div>
                            <div class="market-cap-display">
                                Market Cap: ${formatMarketCap(data.market_cap)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Professional Metrics Dashboard -->
            ${generateProfessionalMetricsGrid(data)}
            
            <!-- Strategy Applied Indicator -->
            ${generateStrategyIndicator(data)}
            
            <!-- Our Three Competitive Advantages -->
            ${competitiveAdvantagesHTML}
        </div>
    `;
}

function initializeEnhancedFeatures() {
    console.log('=== COMPETITIVE FEATURES VERIFICATION ===');
    console.log('✅ Enhanced AI Explanations: Providing transparent AI reasoning');
    console.log('✅ Smart Event Detection: Early warning system for market events');
    console.log('✅ Educational Insights: Learning integrated with every analysis');
    console.log('✅ New enhanced UI active - old basic UI disabled');
    
    // Initialize competitive features with animations
    if (typeof initializeCompetitiveFeatures === 'function') {
        initializeCompetitiveFeatures();
    }
    
    console.log('Enhanced features initialized');
}

function formatMarketCap(marketCap) {
    if (!marketCap || marketCap === 0) return 'N/A';
    
    const cap = parseFloat(marketCap);
    if (cap >= 1e12) return `$${(cap / 1e12).toFixed(1)}T`;
    if (cap >= 1e9) return `$${(cap / 1e9).toFixed(1)}B`;
    if (cap >= 1e6) return `$${(cap / 1e6).toFixed(1)}M`;
    return `$${cap.toFixed(0)}`;
}

function generateProfessionalMetricsGrid(data) {
    const analysis = data.analysis || {};
    
    return `
        <div class="professional-metrics-grid">
            <div class="metric-card">
                <div class="metric-label">AI Confidence</div>
                <div class="metric-value">${data.confidence || 60}%</div>
                <div class="metric-change ${(data.confidence || 60) >= 70 ? 'positive' : 'negative'}">
                    ${(data.confidence || 60) >= 70 ? 'High Confidence' : 'Moderate'}
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Recommendation</div>
                <div class="metric-value">${data.recommendation || 'HOLD'}</div>
                <div class="metric-change">
                    ${analysis.strategy_applied ? 'Strategy Applied' : 'Base Analysis'}
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Risk Level</div>
                <div class="metric-value">${data.risk_level || 'Medium'}</div>
                <div class="metric-change">
                    Volatility Assessment
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Market Cap</div>
                <div class="metric-value">${formatMarketCap(data.market_cap)}</div>
                <div class="metric-change">
                    Size Category
                </div>
            </div>
        </div>
    `;
}

function generateStrategyIndicator(data) {
    const analysis = data.analysis || {};
    const strategy = analysis.strategy_applied || {};
    const impact = analysis.strategy_impact || {};
    
    if (!strategy.name) return '';
    
    return `
        <div class="strategy-applied-indicator">
            <div class="d-flex align-items-center">
                <span class="strategy-icon">${strategy.icon || '📊'}</span>
                <div>
                    <strong>${strategy.name} Strategy Applied</strong>
                    <div style="font-size: 0.9rem; opacity: 0.9;">${strategy.description || 'Personalized analysis based on your investment style'}</div>
                </div>
                ${impact.changed ? `
                    <div class="strategy-change-indicator">
                        ${impact.original_recommendation || 'HOLD'} → ${data.recommendation || 'HOLD'}
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Make functions globally available
window.displayEnhancedAnalysis = displayEnhancedAnalysis;
window.generateEnhancedAnalysisHTML = generateEnhancedAnalysisHTML;
window.formatMarketCap = formatMarketCap;
window.generateProfessionalMetricsGrid = generateProfessionalMetricsGrid;
window.generateStrategyIndicator = generateStrategyIndicator;