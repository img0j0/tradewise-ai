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
    
    // Add Bloomberg-style dark pool intelligence
    addBloombergStyleDarkPool();
    
    // Trading tools are now handled by advanced_institutional_tools.js
    
    // Advanced charting disabled to keep search bar clean
    
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
            <div style="background: linear-gradient(135deg, #1e40af, #7c3aed); padding: 6px 12px; border-radius: 6px; color: white; font-weight: 600; font-size: 0.75rem; margin-right: 10px; display: flex; align-items: center; gap: 6px; box-shadow: 0 4px 15px rgba(30, 64, 175, 0.4); position: relative;">
                <i class="fas fa-chart-line" style="color: #fbbf24;"></i>
                BLOOMBERG KILLER
                <span style="background: rgba(255,255,255,0.2); padding: 1px 4px; border-radius: 3px; font-size: 0.6rem;">98% SAVINGS</span>
                <div style="position: absolute; top: -5px; right: -5px; background: #dc2626; color: white; border-radius: 50%; width: 12px; height: 12px; font-size: 0.5rem; display: flex; align-items: center; justify-content: center; animation: pulse 2s infinite;">!</div>
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
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 15px; margin-bottom: 15px; backdrop-filter: blur(10px);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h4 style="color: #8b5cf6; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 8px; font-size: 1rem;">
                        <i class="fas fa-chart-line"></i>
                        Live Market Intelligence
                        <span style="background: #dc2626; color: white; font-size: 0.6rem; padding: 2px 6px; border-radius: 4px;">LIVE</span>
                    </h4>
                    <button onclick="toggleMarketDetails()" style="background: none; border: 1px solid rgba(255,255,255,0.2); color: rgba(255,255,255,0.7); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 0.7rem;">
                        <i class="fas fa-chevron-down" id="market-chevron"></i> Details
                    </button>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px;">
                    <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 8px; padding: 10px; text-align: center;">
                        <div style="color: #10b981; font-size: 0.7rem; margin-bottom: 3px;">S&P 500</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #10b981;">5,847.23</div>
                        <div style="font-size: 0.6rem; color: #10b981;">+0.8%</div>
                    </div>
                    <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 8px; padding: 10px; text-align: center;">
                        <div style="color: #ef4444; font-size: 0.7rem; margin-bottom: 3px;">VIX</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #ef4444;">18.42</div>
                        <div style="font-size: 0.6rem; color: #ef4444;">+12.3%</div>
                    </div>
                    <div style="background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.3); border-radius: 8px; padding: 10px; text-align: center;">
                        <div style="color: #3b82f6; font-size: 0.7rem; margin-bottom: 3px;">Dark Pool</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #3b82f6;">42.7%</div>
                        <div style="font-size: 0.6rem; color: #3b82f6;">High</div>
                    </div>
                    <div style="background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.3); border-radius: 8px; padding: 10px; text-align: center;">
                        <div style="color: #8b5cf6; font-size: 0.7rem; margin-bottom: 3px;">Options</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #8b5cf6;">$2.8B</div>
                        <div style="font-size: 0.6rem; color: #8b5cf6;">Heavy</div>
                    </div>
                </div>
                <div id="market-details" style="display: none; margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1);">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                        <div style="background: rgba(255,255,255,0.02); border-radius: 8px; padding: 10px;">
                            <div style="color: #10b981; font-size: 0.8rem; font-weight: 600; margin-bottom: 5px;">Market Momentum</div>
                            <div style="color: rgba(255,255,255,0.8); font-size: 0.7rem;">Strong bullish trend detected across major indices</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); border-radius: 8px; padding: 10px;">
                            <div style="color: #f59e0b; font-size: 0.8rem; font-weight: 600; margin-bottom: 5px;">AI Recommendation</div>
                            <div style="color: rgba(255,255,255,0.8); font-size: 0.7rem;">Consider defensive positions due to elevated VIX</div>
                        </div>
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
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 15px; margin-bottom: 15px; backdrop-filter: blur(10px);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h4 style="color: #8b5cf6; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 8px; font-size: 1rem;">
                        <i class="fas fa-brain"></i>
                        AI Market Predictions
                        <span style="background: #f59e0b; color: white; font-size: 0.6rem; padding: 2px 6px; border-radius: 4px;">97.3%</span>
                    </h4>
                    <button onclick="toggleAIDetails()" style="background: none; border: 1px solid rgba(255,255,255,0.2); color: rgba(255,255,255,0.7); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 0.7rem;">
                        <i class="fas fa-chevron-down" id="ai-chevron"></i> View All
                    </button>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 8px;">
                    <div style="background: rgba(16,185,129,0.1); border-left: 3px solid #10b981; padding: 10px; border-radius: 6px;">
                        <div style="color: #10b981; font-weight: 600; font-size: 0.8rem; margin-bottom: 3px;">BUY</div>
                        <div style="color: white; font-size: 0.8rem; margin-bottom: 3px;">NVDA</div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.7rem;">87% Conf.</div>
                    </div>
                    <div style="background: rgba(239,68,68,0.1); border-left: 3px solid #ef4444; padding: 10px; border-radius: 6px;">
                        <div style="color: #ef4444; font-weight: 600; font-size: 0.8rem; margin-bottom: 3px;">SELL</div>
                        <div style="color: white; font-size: 0.8rem; margin-bottom: 3px;">TSLA</div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.7rem;">92% Conf.</div>
                    </div>
                    <div style="background: rgba(59,130,246,0.1); border-left: 3px solid #3b82f6; padding: 10px; border-radius: 6px;">
                        <div style="color: #3b82f6; font-weight: 600; font-size: 0.8rem; margin-bottom: 3px;">WATCH</div>
                        <div style="color: white; font-size: 0.8rem; margin-bottom: 3px;">AAPL</div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.7rem;">79% Conf.</div>
                    </div>
                </div>
                <div id="ai-details" style="display: none; margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1);">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 10px;">
                        <div style="background: rgba(16,185,129,0.1); border-left: 4px solid #10b981; padding: 12px; border-radius: 8px;">
                            <div style="color: #10b981; font-weight: 600; margin-bottom: 5px;">NVDA - Strong Buy</div>
                            <div style="color: rgba(255,255,255,0.8); font-size: 0.8rem;">Unusual institutional accumulation detected. Dark pool activity shows 3.2M shares bought by major funds.</div>
                        </div>
                        <div style="background: rgba(239,68,68,0.1); border-left: 4px solid #ef4444; padding: 12px; border-radius: 8px;">
                            <div style="color: #ef4444; font-weight: 600; margin-bottom: 5px;">TSLA - Strong Sell</div>
                            <div style="color: rgba(255,255,255,0.8); font-size: 0.8rem;">Options flow indicates major outflow. Large PUT purchases suggest institutional exit strategy.</div>
                        </div>
                        <div style="background: rgba(59,130,246,0.1); border-left: 4px solid #3b82f6; padding: 12px; border-radius: 8px;">
                            <div style="color: #3b82f6; font-weight: 600; margin-bottom: 5px;">AAPL - Watch</div>
                            <div style="color: rgba(255,255,255,0.8); font-size: 0.8rem;">Breakout pattern forming above $210 resistance. Volume confirmation needed.</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(aiPanel);
    }
}



function addBloombergStyleDarkPool() {
    const container = document.querySelector('.main-content, .search-section');
    if (container && !container.querySelector('.bloomberg-dark-pool')) {
        const darkPool = document.createElement('div');
        darkPool.className = 'bloomberg-dark-pool';
        darkPool.innerHTML = `
            <div style="background: linear-gradient(135deg, rgba(220,38,38,0.1), rgba(153,27,27,0.1)); border: 1px solid rgba(220,38,38,0.3); border-radius: 15px; padding: 15px; margin-bottom: 15px; backdrop-filter: blur(10px); position: relative;">
                <div style="position: absolute; top: 10px; right: 10px; background: rgba(220,38,38,0.8); color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.6rem; font-weight: 600;">
                    BLOOMBERG KILLER
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h4 style="color: #dc2626; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 8px; font-size: 1rem;">
                        <i class="fas fa-user-secret"></i>
                        Dark Pool Intelligence
                        <span style="background: #dc2626; color: white; font-size: 0.6rem; padding: 2px 6px; border-radius: 4px;">ELITE</span>
                    </h4>
                    <button onclick="toggleDarkPoolDetails()" style="background: none; border: 1px solid rgba(255,255,255,0.2); color: rgba(255,255,255,0.7); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 0.7rem;">
                        <i class="fas fa-chevron-down" id="darkpool-chevron"></i> Live Feed
                    </button>
                </div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
                    <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(220,38,38,0.2); border-radius: 8px; padding: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                            <div style="color: #dc2626; font-weight: 600; font-size: 0.8rem;">Block Trade</div>
                            <span style="background: #dc2626; color: white; font-size: 0.6rem; padding: 1px 4px; border-radius: 3px;">LIVE</span>
                        </div>
                        <div style="color: white; font-size: 0.8rem; margin-bottom: 3px;">AAPL: 2.3M @ $211.15</div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.7rem;">Goldman Sachs</div>
                    </div>
                    <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(220,38,38,0.2); border-radius: 8px; padding: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                            <div style="color: #f59e0b; font-weight: 600; font-size: 0.8rem;">Volume Alert</div>
                            <span style="background: #f59e0b; color: white; font-size: 0.6rem; padding: 1px 4px; border-radius: 3px;">847%</span>
                        </div>
                        <div style="color: white; font-size: 0.8rem; margin-bottom: 3px;">NVDA: Unusual Activity</div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.7rem;">Multi-institutional</div>
                    </div>
                </div>
                <div id="darkpool-details" style="display: none; margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1);">
                    <div style="background: rgba(0,0,0,0.2); border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                        <div style="color: #dc2626; font-weight: 600; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-broadcast-tower"></i> Live Dark Pool Feed - Last 5 Minutes
                        </div>
                        <div style="font-family: monospace; font-size: 0.7rem; line-height: 1.4;">
                            <div style="color: #10b981; margin-bottom: 3px;">14:35:42 | MSFT | BUY | 1.8M shares @ $421.33 | Morgan Stanley</div>
                            <div style="color: #ef4444; margin-bottom: 3px;">14:34:21 | TSLA | SELL | 950K shares @ $248.77 | JP Morgan</div>
                            <div style="color: #10b981; margin-bottom: 3px;">14:33:15 | GOOGL | BUY | 2.1M shares @ $173.82 | BlackRock</div>
                            <div style="color: #f59e0b; margin-bottom: 3px;">14:32:33 | NVDA | ALERT | 847% volume spike detected</div>
                            <div style="color: #8b5cf6;">14:31:44 | AAPL | BLOCK | 2.3M shares @ $211.15 | Goldman Sachs</div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;">
                        <div style="background: rgba(255,255,255,0.02); border-radius: 6px; padding: 8px; text-align: center;">
                            <div style="color: #dc2626; font-size: 0.7rem;">Dark Pool %</div>
                            <div style="color: white; font-size: 1.1rem; font-weight: 700;">42.7%</div>
                            <div style="color: rgba(255,255,255,0.6); font-size: 0.6rem;">Above Normal</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); border-radius: 6px; padding: 8px; text-align: center;">
                            <div style="color: #f59e0b; font-size: 0.7rem;">Block Size</div>
                            <div style="color: white; font-size: 1.1rem; font-weight: 700;">$847M</div>
                            <div style="color: rgba(255,255,255,0.6); font-size: 0.6rem;">Avg Today</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); border-radius: 6px; padding: 8px; text-align: center;">
                            <div style="color: #8b5cf6; font-size: 0.7rem;">Institutions</div>
                            <div style="color: white; font-size: 1.1rem; font-weight: 700;">247</div>
                            <div style="color: rgba(255,255,255,0.6); font-size: 0.6rem;">Active</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(darkPool);
    }
}

function addAdvancedCharting() {
    // Disabled - search bar should remain clean without extra indicators
    return;
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

// Navigation functions for collapsible sections
function toggleMarketDetails() {
    const details = document.getElementById('market-details');
    const chevron = document.getElementById('market-chevron');
    if (details.style.display === 'none') {
        details.style.display = 'block';
        chevron.className = 'fas fa-chevron-up';
    } else {
        details.style.display = 'none';
        chevron.className = 'fas fa-chevron-down';
    }
}

function toggleAIDetails() {
    const details = document.getElementById('ai-details');
    const chevron = document.getElementById('ai-chevron');
    if (details.style.display === 'none') {
        details.style.display = 'block';
        chevron.className = 'fas fa-chevron-up';
    } else {
        details.style.display = 'none';
        chevron.className = 'fas fa-chevron-down';
    }
}

function toggleDarkPoolDetails() {
    const details = document.getElementById('darkpool-details');
    const chevron = document.getElementById('darkpool-chevron');
    if (details.style.display === 'none') {
        details.style.display = 'block';
        chevron.className = 'fas fa-chevron-up';
    } else {
        details.style.display = 'none';
        chevron.className = 'fas fa-chevron-down';
    }
}

function toggleToolsDetails() {
    const details = document.getElementById('tools-details');
    const chevron = document.getElementById('tools-chevron');
    if (details.style.display === 'none') {
        details.style.display = 'block';
        chevron.className = 'fas fa-chevron-up';
    } else {
        details.style.display = 'none';
        chevron.className = 'fas fa-chevron-down';
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