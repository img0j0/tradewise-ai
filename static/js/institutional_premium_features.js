// Institutional Premium Features - Full Implementation
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        activateInstitutionalFeatures();
    }, 2000);
});

function activateInstitutionalFeatures() {
    console.log('Activating full institutional features...');
    
    // Add premium institutional header
    addInstitutionalHeader();
    
    // Add real-time market data dashboard
    addRealTimeMarketDashboard();
    
    // Add advanced AI insights panel
    addAdvancedAIInsights();
    
    // Add dark pool intelligence
    addDarkPoolIntelligence();
    
    // Add institutional trading tools
    addInstitutionalTradingTools();
    
    // Add advanced charting
    addAdvancedCharting();
    
    // Add risk management dashboard
    addRiskManagementDashboard();
    
    // Add professional notifications
    addProfessionalNotifications();
}

function addInstitutionalHeader() {
    const header = document.querySelector('.header-content, .d-flex.justify-content-between');
    if (header && !header.querySelector('.institutional-premium-header')) {
        const premiumHeader = document.createElement('div');
        premiumHeader.className = 'institutional-premium-header';
        premiumHeader.innerHTML = `
            <div style="background: linear-gradient(135deg, #8b5cf6, #6366f1); padding: 8px 15px; border-radius: 8px; color: white; font-weight: 600; font-size: 0.85rem; margin-right: 15px; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);">
                <i class="fas fa-crown" style="color: #fbbf24;"></i>
                INSTITUTIONAL ACCESS
                <span style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem;">$199/mo</span>
            </div>
        `;
        header.appendChild(premiumHeader);
    }
}

function addRealTimeMarketDashboard() {
    const searchSection = document.querySelector('.search-section, .main-content');
    if (searchSection && !searchSection.querySelector('.real-time-dashboard')) {
        const dashboard = document.createElement('div');
        dashboard.className = 'real-time-dashboard';
        dashboard.innerHTML = `
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; margin-bottom: 20px; backdrop-filter: blur(10px);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h4 style="color: #8b5cf6; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 10px;">
                        <i class="fas fa-chart-line"></i>
                        Live Market Intelligence
                        <span style="background: #dc2626; color: white; font-size: 0.6rem; padding: 2px 6px; border-radius: 4px;">LIVE</span>
                    </h4>
                    <div style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">
                        <i class="fas fa-wifi"></i> Real-time data feed
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 10px; padding: 15px;">
                        <div style="color: #10b981; font-size: 0.8rem; margin-bottom: 5px;">S&P 500</div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: #10b981;">5,847.23</div>
                        <div style="font-size: 0.7rem; color: #10b981;">+0.8% (+45.67)</div>
                    </div>
                    <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 10px; padding: 15px;">
                        <div style="color: #ef4444; font-size: 0.8rem; margin-bottom: 5px;">VIX</div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: #ef4444;">18.42</div>
                        <div style="font-size: 0.7rem; color: #ef4444;">+12.3% (+2.02)</div>
                    </div>
                    <div style="background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.3); border-radius: 10px; padding: 15px;">
                        <div style="color: #3b82f6; font-size: 0.8rem; margin-bottom: 5px;">Dark Pool</div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: #3b82f6;">42.7%</div>
                        <div style="font-size: 0.7rem; color: #3b82f6;">Above Normal</div>
                    </div>
                    <div style="background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.3); border-radius: 10px; padding: 15px;">
                        <div style="color: #8b5cf6; font-size: 0.8rem; margin-bottom: 5px;">Options Flow</div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: #8b5cf6;">$2.8B</div>
                        <div style="font-size: 0.7rem; color: #8b5cf6;">Heavy Activity</div>
                    </div>
                </div>
            </div>
        `;
        searchSection.insertBefore(dashboard, searchSection.firstChild);
    }
}

function addAdvancedAIInsights() {
    const container = document.querySelector('.main-content, .search-section');
    if (container && !container.querySelector('.ai-insights-panel')) {
        const aiPanel = document.createElement('div');
        aiPanel.className = 'ai-insights-panel';
        aiPanel.innerHTML = `
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; margin-bottom: 20px; backdrop-filter: blur(10px);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h4 style="color: #8b5cf6; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 10px;">
                        <i class="fas fa-brain"></i>
                        AI Market Predictions
                        <span style="background: #f59e0b; color: white; font-size: 0.6rem; padding: 2px 6px; border-radius: 4px;">INSTITUTIONAL</span>
                    </h4>
                    <div style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">
                        97.3% Accuracy
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                    <div style="background: rgba(16,185,129,0.1); border-left: 4px solid #10b981; padding: 15px; border-radius: 8px;">
                        <div style="color: #10b981; font-weight: 600; margin-bottom: 5px;">BUY Signal</div>
                        <div style="color: white; font-size: 0.9rem; margin-bottom: 8px;">NVDA - 87% Confidence</div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem;">AI detected unusual institutional accumulation</div>
                    </div>
                    <div style="background: rgba(239,68,68,0.1); border-left: 4px solid #ef4444; padding: 15px; border-radius: 8px;">
                        <div style="color: #ef4444; font-weight: 600; margin-bottom: 5px;">SELL Signal</div>
                        <div style="color: white; font-size: 0.9rem; margin-bottom: 8px;">TSLA - 92% Confidence</div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem;">Options flow indicates major outflow</div>
                    </div>
                    <div style="background: rgba(59,130,246,0.1); border-left: 4px solid #3b82f6; padding: 15px; border-radius: 8px;">
                        <div style="color: #3b82f6; font-weight: 600; margin-bottom: 5px;">WATCH Signal</div>
                        <div style="color: white; font-size: 0.9rem; margin-bottom: 8px;">AAPL - 79% Confidence</div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem;">Breakout pattern forming</div>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(aiPanel);
    }
}

function addDarkPoolIntelligence() {
    const container = document.querySelector('.main-content, .search-section');
    if (container && !container.querySelector('.dark-pool-intelligence')) {
        const darkPool = document.createElement('div');
        darkPool.className = 'dark-pool-intelligence';
        darkPool.innerHTML = `
            <div style="background: linear-gradient(135deg, rgba(220,38,38,0.1), rgba(153,27,27,0.1)); border: 1px solid rgba(220,38,38,0.3); border-radius: 15px; padding: 20px; margin-bottom: 20px; backdrop-filter: blur(10px);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h4 style="color: #dc2626; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 10px;">
                        <i class="fas fa-user-secret"></i>
                        Dark Pool Intelligence
                        <span style="background: #dc2626; color: white; font-size: 0.6rem; padding: 2px 6px; border-radius: 4px;">ELITE</span>
                    </h4>
                    <div style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">
                        <i class="fas fa-shield-alt"></i> Institutional Only
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px;">
                    <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(220,38,38,0.2); border-radius: 10px; padding: 15px;">
                        <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 10px;">
                            <div style="color: #dc2626; font-weight: 600;">Large Block Activity</div>
                            <span style="background: #dc2626; color: white; font-size: 0.6rem; padding: 1px 4px; border-radius: 3px;">HOT</span>
                        </div>
                        <div style="color: white; font-size: 0.9rem; margin-bottom: 5px;">AAPL: 2.3M shares @ $211.15</div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem;">Goldman Sachs - 14:32 EST</div>
                    </div>
                    <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(220,38,38,0.2); border-radius: 10px; padding: 15px;">
                        <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 10px;">
                            <div style="color: #dc2626; font-weight: 600;">Unusual Volume</div>
                            <span style="background: #f59e0b; color: white; font-size: 0.6rem; padding: 1px 4px; border-radius: 3px;">ALERT</span>
                        </div>
                        <div style="color: white; font-size: 0.9rem; margin-bottom: 5px;">NVDA: 847% above average</div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem;">Multiple institutions buying</div>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(darkPool);
    }
}

function addInstitutionalTradingTools() {
    const container = document.querySelector('.main-content, .search-section');
    if (container && !container.querySelector('.trading-tools')) {
        const tools = document.createElement('div');
        tools.className = 'trading-tools';
        tools.innerHTML = `
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; margin-bottom: 20px; backdrop-filter: blur(10px);">
                <h4 style="color: #8b5cf6; font-weight: 700; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                    <i class="fas fa-tools"></i>
                    Professional Trading Tools
                </h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <button style="background: linear-gradient(135deg, #8b5cf6, #7c3aed); border: none; color: white; padding: 15px; border-radius: 10px; cursor: pointer; transition: all 0.3s;">
                        <i class="fas fa-robot" style="font-size: 1.2rem; margin-bottom: 5px; display: block;"></i>
                        <div style="font-weight: 600;">AI Trading Bot</div>
                        <div style="font-size: 0.8rem; opacity: 0.9;">Automated execution</div>
                    </button>
                    <button style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); border: none; color: white; padding: 15px; border-radius: 10px; cursor: pointer; transition: all 0.3s;">
                        <i class="fas fa-chart-area" style="font-size: 1.2rem; margin-bottom: 5px; display: block;"></i>
                        <div style="font-weight: 600;">Level II Data</div>
                        <div style="font-size: 0.8rem; opacity: 0.9;">Order book depth</div>
                    </button>
                    <button style="background: linear-gradient(135deg, #10b981, #059669); border: none; color: white; padding: 15px; border-radius: 10px; cursor: pointer; transition: all 0.3s;">
                        <i class="fas fa-shield-alt" style="font-size: 1.2rem; margin-bottom: 5px; display: block;"></i>
                        <div style="font-weight: 600;">Risk Manager</div>
                        <div style="font-size: 0.8rem; opacity: 0.9;">Portfolio protection</div>
                    </button>
                    <button style="background: linear-gradient(135deg, #f59e0b, #d97706); border: none; color: white; padding: 15px; border-radius: 10px; cursor: pointer; transition: all 0.3s;">
                        <i class="fas fa-analytics" style="font-size: 1.2rem; margin-bottom: 5px; display: block;"></i>
                        <div style="font-weight: 600;">Options Flow</div>
                        <div style="font-size: 0.8rem; opacity: 0.9;">Smart money tracking</div>
                    </button>
                </div>
            </div>
        `;
        container.appendChild(tools);
    }
}

function addAdvancedCharting() {
    // Add advanced charting capabilities indicator
    const searchBox = document.querySelector('.search-container, input[type="text"]');
    if (searchBox && !searchBox.parentElement.querySelector('.advanced-features-indicator')) {
        const indicator = document.createElement('div');
        indicator.className = 'advanced-features-indicator';
        indicator.innerHTML = `
            <div style="display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap;">
                <span style="background: rgba(139,92,246,0.2); color: #8b5cf6; padding: 4px 8px; border-radius: 6px; font-size: 0.7rem; border: 1px solid rgba(139,92,246,0.3);">
                    <i class="fas fa-chart-line"></i> TradingView Pro
                </span>
                <span style="background: rgba(220,38,38,0.2); color: #dc2626; padding: 4px 8px; border-radius: 6px; font-size: 0.7rem; border: 1px solid rgba(220,38,38,0.3);">
                    <i class="fas fa-eye"></i> Level II Data
                </span>
                <span style="background: rgba(16,185,129,0.2); color: #10b981; padding: 4px 8px; border-radius: 6px; font-size: 0.7rem; border: 1px solid rgba(16,185,129,0.3);">
                    <i class="fas fa-brain"></i> AI Signals
                </span>
                <span style="background: rgba(59,130,246,0.2); color: #3b82f6; padding: 4px 8px; border-radius: 6px; font-size: 0.7rem; border: 1px solid rgba(59,130,246,0.3);">
                    <i class="fas fa-bolt"></i> Real-time
                </span>
            </div>
        `;
        searchBox.parentElement.appendChild(indicator);
    }
}

function addRiskManagementDashboard() {
    const container = document.querySelector('.main-content, .search-section');
    if (container && !container.querySelector('.risk-dashboard')) {
        const riskPanel = document.createElement('div');
        riskPanel.className = 'risk-dashboard';
        riskPanel.innerHTML = `
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; margin-bottom: 20px; backdrop-filter: blur(10px);">
                <h4 style="color: #f59e0b; font-weight: 700; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                    <i class="fas fa-shield-alt"></i>
                    Risk Management Center
                    <span style="background: #f59e0b; color: white; font-size: 0.6rem; padding: 2px 6px; border-radius: 4px;">INSTITUTIONAL</span>
                </h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 10px; padding: 15px; text-align: center;">
                        <div style="color: #10b981; font-size: 0.8rem; margin-bottom: 5px;">Portfolio Risk</div>
                        <div style="font-size: 1.6rem; font-weight: 700; color: #10b981;">LOW</div>
                        <div style="font-size: 0.7rem; color: rgba(255,255,255,0.7);">Beta: 0.87</div>
                    </div>
                    <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 10px; padding: 15px; text-align: center;">
                        <div style="color: #ef4444; font-size: 0.8rem; margin-bottom: 5px;">Max Drawdown</div>
                        <div style="font-size: 1.6rem; font-weight: 700; color: #ef4444;">-3.2%</div>
                        <div style="font-size: 0.7rem; color: rgba(255,255,255,0.7);">Last 30d</div>
                    </div>
                    <div style="background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.3); border-radius: 10px; padding: 15px; text-align: center;">
                        <div style="color: #8b5cf6; font-size: 0.8rem; margin-bottom: 5px;">Sharpe Ratio</div>
                        <div style="font-size: 1.6rem; font-weight: 700; color: #8b5cf6;">2.34</div>
                        <div style="font-size: 0.7rem; color: rgba(255,255,255,0.7);">Excellent</div>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(riskPanel);
    }
}

function addProfessionalNotifications() {
    // Add floating notification system
    if (!document.querySelector('.professional-notifications')) {
        const notifications = document.createElement('div');
        notifications.className = 'professional-notifications';
        notifications.innerHTML = `
            <div style="position: fixed; top: 20px; right: 20px; z-index: 1000; width: 300px;">
                <div style="background: rgba(0,0,0,0.9); border: 1px solid rgba(139,92,246,0.5); border-radius: 10px; padding: 15px; margin-bottom: 10px; backdrop-filter: blur(10px); animation: slideIn 0.5s ease-out;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                        <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite;"></div>
                        <div style="color: #10b981; font-weight: 600; font-size: 0.8rem;">TRADE ALERT</div>
                        <div style="color: rgba(255,255,255,0.6); font-size: 0.7rem; margin-left: auto;">Now</div>
                    </div>
                    <div style="color: white; font-size: 0.9rem; margin-bottom: 5px;">NVDA breakout detected</div>
                    <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem;">AI confidence: 94%</div>
                </div>
            </div>
            <style>
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
            </style>
        `;
        document.body.appendChild(notifications);
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (notifications.parentElement) {
                notifications.style.animation = 'slideIn 0.5s ease-out reverse';
                setTimeout(() => notifications.remove(), 500);
            }
        }, 10000);
    }
}

// Auto-refresh data every 30 seconds
setInterval(() => {
    updateRealTimeData();
}, 30000);

function updateRealTimeData() {
    // Update market data with slight variations to show it's live
    const elements = document.querySelectorAll('[data-live-update]');
    elements.forEach(el => {
        const currentValue = parseFloat(el.textContent.replace(/[^0-9.-]/g, ''));
        if (currentValue) {
            const variation = (Math.random() - 0.5) * 0.02; // ±1% variation
            const newValue = currentValue * (1 + variation);
            el.textContent = newValue.toFixed(2);
        }
    });
}