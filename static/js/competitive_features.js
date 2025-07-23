// Competitive Features UI Generator - Bloomberg for Everyone Vision
// Generates enhanced displays for our three competitive advantages

function generateCompetitiveAdvantagesHTML(data) {
    const transparencyHTML = generateTransparencyAdvantageHTML(data);
    const earlyWarningHTML = generateEarlyWarningSystemHTML(data);
    const learningHTML = generateLearningIntegrationHTML(data);
    
    return `
        <div class="competitive-advantages-layout">
            ${transparencyHTML}
            ${earlyWarningHTML}
            ${learningHTML}
        </div>
    `;
}

function generateTransparencyAdvantageHTML(data) {
    const explanation = data.enhanced_explanation || {};
    const confidence = explanation.confidence_breakdown || {};
    
    return `
        <div class="transparency-advantage">
            <div class="transparency-content">
                <h4 class="mb-3" style="font-weight: 700;">AI Decision Transparency</h4>
                <p class="mb-3" style="opacity: 0.9;">
                    Unlike "black box" competitors, we show exactly how our AI reaches its conclusions.
                </p>
                
                <div class="confidence-breakdown">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <strong>Overall Confidence:</strong>
                        <span class="badge bg-light text-dark px-3 py-2">${confidence.overall_confidence || data.confidence || 60}%</span>
                    </div>
                    <p style="font-size: 0.9rem; opacity: 0.8;">${confidence.confidence_interpretation || 'Analysis based on multiple market factors'}</p>
                    
                    <div class="confidence-factors">
                        ${generateConfidenceFactors(confidence.contributing_factors || {})}
                    </div>
                </div>
                
                <div style="margin-top: 16px; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                    <strong>Why This Matters:</strong> You can trust the analysis because you understand the reasoning behind it.
                </div>
            </div>
        </div>
    `;
}

function generateEarlyWarningSystemHTML(data) {
    const alerts = data.smart_alerts || {};
    const marketEvents = alerts.market_events || [];
    const stockEvents = alerts.stock_events || [];
    
    const allEvents = [...marketEvents, ...stockEvents];
    const highImpactEvents = allEvents.filter(event => event.impact_level === 'HIGH');
    
    return `
        <div class="early-warning-system">
            <h4 class="mb-3" style="font-weight: 700;">Smart Market Intelligence</h4>
            <p class="mb-3" style="opacity: 0.9;">
                Early detection of market events that could impact your investments.
            </p>
            
            ${allEvents.length > 0 ? `
                <div class="alert-summary mb-3">
                    <div class="row text-center">
                        <div class="col-4">
                            <div class="metric-value">${allEvents.length}</div>
                            <div class="metric-label">Total Events</div>
                        </div>
                        <div class="col-4">
                            <div class="metric-value">${highImpactEvents.length}</div>
                            <div class="metric-label">High Impact</div>
                        </div>
                        <div class="col-4">
                            <div class="metric-value">${marketEvents.length}</div>
                            <div class="metric-label">Market Wide</div>
                        </div>
                    </div>
                </div>
                
                ${generateEventAlerts(allEvents.slice(0, 3))}
            ` : `
                <div class="event-alert">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-shield-alt me-2" style="color: #10b981;"></i>
                        <span>No immediate threats detected</span>
                    </div>
                    <small style="opacity: 0.8;">Continuous monitoring active for ${data.symbol}</small>
                </div>
            `}
            
            <div style="margin-top: 16px; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                <strong>Competitive Edge:</strong> Institutional-level event detection for retail investors.
            </div>
        </div>
    `;
}

function generateLearningIntegrationHTML(data) {
    const education = data.educational_insights || {};
    const concepts = education.concept_explanations || {};
    const mistakes = education.common_mistakes || [];
    
    return `
        <div class="learning-integration">
            <h4 class="mb-3" style="font-weight: 700;">Learn While You Invest</h4>
            <p class="mb-3" style="opacity: 0.9;">
                Every analysis includes educational insights to improve your investment knowledge.
            </p>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="concept-card">
                        <h6 style="color: #a78bfa; margin-bottom: 8px;">💡 Concept: Confidence Levels</h6>
                        <p style="font-size: 0.9rem; margin-bottom: 8px;">
                            ${concepts.confidence_levels?.definition || 'How certain our analysis is about the recommendation'}
                        </p>
                        <div class="practical-tip">
                            <strong>Practical Tip:</strong> ${concepts.confidence_levels?.practical_tip || 'Lower confidence suggests reducing position size'}
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="concept-card">
                        <h6 style="color: #a78bfa; margin-bottom: 8px;">⚠️ Common Mistake</h6>
                        ${mistakes.length > 0 ? `
                            <p style="font-size: 0.9rem; margin-bottom: 8px;">
                                <strong>${mistakes[0].mistake}:</strong> ${mistakes[0].description}
                            </p>
                            <div class="practical-tip">
                                <strong>How to Avoid:</strong> ${mistakes[0].how_to_avoid}
                            </div>
                        ` : `
                            <p style="font-size: 0.9rem;">Always diversify your portfolio across different sectors and asset classes.</p>
                            <div class="practical-tip">
                                <strong>Tip:</strong> Limit single stock positions to 5-10% of total portfolio.
                            </div>
                        `}
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 16px; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                <strong>Learning Advantage:</strong> Build expertise while analyzing investments - no separate education needed.
            </div>
        </div>
    `;
}

function generateConfidenceFactors(factors) {
    const defaultFactors = {
        'technical_analysis': 25,
        'fundamental_analysis': 35,
        'market_sentiment': 20,
        'ai_signals': 20
    };
    
    const actualFactors = Object.keys(factors).length > 0 ? factors : defaultFactors;
    
    return Object.entries(actualFactors).map(([factor, weight]) => `
        <div class="factor-item">
            <div class="d-flex justify-content-between align-items-center">
                <span style="text-transform: capitalize;">${factor.replace('_', ' ')}</span>
                <span class="badge bg-info">${weight}%</span>
            </div>
        </div>
    `).join('');
}

function generateEventAlerts(events) {
    return events.map(event => `
        <div class="event-alert">
            <div class="d-flex align-items-start justify-content-between">
                <div>
                    <div class="d-flex align-items-center mb-1">
                        <strong>${event.title}</strong>
                        <span class="event-impact impact-${event.impact_level?.toLowerCase() || 'medium'}">${event.impact_level || 'MEDIUM'}</span>
                    </div>
                    <p style="font-size: 0.9rem; margin: 0; opacity: 0.9;">${event.description}</p>
                </div>
                <i class="fas fa-exclamation-triangle" style="color: #f59e0b; margin-left: 12px;"></i>
            </div>
        </div>
    `).join('');
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

function formatMarketCap(marketCap) {
    if (!marketCap || marketCap === 0) return 'N/A';
    
    const cap = parseFloat(marketCap);
    if (cap >= 1e12) return `$${(cap / 1e12).toFixed(1)}T`;
    if (cap >= 1e9) return `$${(cap / 1e9).toFixed(1)}B`;
    if (cap >= 1e6) return `$${(cap / 1e6).toFixed(1)}M`;
    return `$${cap.toFixed(0)}`;
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

// Initialize competitive features with animations
function initializeCompetitiveFeatures() {
    // Add entrance animations
    const elements = document.querySelectorAll('.competitive-advantage-enter');
    elements.forEach((el, index) => {
        el.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Add interactive hover effects
    const advantageCards = document.querySelectorAll('.transparency-advantage, .early-warning-system, .learning-integration');
    advantageCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Export functions for global use
window.generateCompetitiveAdvantagesHTML = generateCompetitiveAdvantagesHTML;
window.initializeCompetitiveFeatures = initializeCompetitiveFeatures;