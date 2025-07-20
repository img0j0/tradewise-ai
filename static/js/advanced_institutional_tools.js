// Advanced Institutional Trading Tools
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        addInstitutionalToolbar();
        addProfessionalFeatures();
    }, 3000);
});

function addInstitutionalToolbar() {
    if (!document.querySelector('.institutional-toolbar')) {
        const toolbar = document.createElement('div');
        toolbar.className = 'institutional-toolbar';
        toolbar.innerHTML = `
            <div style="position: fixed; bottom: 20px; right: 20px; background: rgba(0,0,0,0.9); border: 1px solid rgba(139,92,246,0.5); border-radius: 15px; padding: 15px; z-index: 1000; backdrop-filter: blur(10px); min-width: 200px;">
                <div style="color: #8b5cf6; font-weight: 700; margin-bottom: 10px; text-align: center; border-bottom: 1px solid rgba(139,92,246,0.3); padding-bottom: 8px;">
                    <i class="fas fa-crown"></i> Institutional Tools
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <button onclick="openAdvancedChart()" style="background: linear-gradient(135deg, #8b5cf6, #7c3aed); border: none; color: white; padding: 8px 12px; border-radius: 8px; cursor: pointer; font-size: 0.8rem; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-chart-area"></i> Level II Data
                    </button>
                    <button onclick="openOrderFlow()" style="background: linear-gradient(135deg, #dc2626, #b91c1c); border: none; color: white; padding: 8px 12px; border-radius: 8px; cursor: pointer; font-size: 0.8rem; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-water"></i> Options Flow
                    </button>
                    <button onclick="openRiskManager()" style="background: linear-gradient(135deg, #10b981, #059669); border: none; color: white; padding: 8px 12px; border-radius: 8px; cursor: pointer; font-size: 0.8rem; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-shield-alt"></i> Risk Manager
                    </button>
                    <button onclick="openAIBot()" style="background: linear-gradient(135deg, #f59e0b, #d97706); border: none; color: white; padding: 8px 12px; border-radius: 8px; cursor: pointer; font-size: 0.8rem; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-robot"></i> AI Trading Bot
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(toolbar);
    }
}

function openAdvancedChart() {
    showInstitutionalModal('Level II Order Book', `
        <div style="background: rgba(0,0,0,0.8); padding: 20px; border-radius: 10px;">
            <h5 style="color: #8b5cf6; margin-bottom: 15px;">AAPL - Real-time Order Book</h5>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h6 style="color: #ef4444; margin-bottom: 10px;">Bids</h6>
                    <div style="font-family: monospace; font-size: 0.8rem;">
                        <div style="display: flex; justify-content: space-between; color: #ef4444; margin-bottom: 3px;">
                            <span>211.15</span><span>2,500</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; color: #ef4444; margin-bottom: 3px;">
                            <span>211.14</span><span>1,800</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; color: #ef4444; margin-bottom: 3px;">
                            <span>211.13</span><span>3,200</span>
                        </div>
                    </div>
                </div>
                <div>
                    <h6 style="color: #10b981; margin-bottom: 10px;">Asks</h6>
                    <div style="font-family: monospace; font-size: 0.8rem;">
                        <div style="display: flex; justify-content: space-between; color: #10b981; margin-bottom: 3px;">
                            <span>211.16</span><span>1,900</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; color: #10b981; margin-bottom: 3px;">
                            <span>211.17</span><span>2,100</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; color: #10b981; margin-bottom: 3px;">
                            <span>211.18</span><span>1,500</span>
                        </div>
                    </div>
                </div>
            </div>
            <div style="margin-top: 15px; padding: 10px; background: rgba(139,92,246,0.1); border-radius: 8px;">
                <small style="color: #8b5cf6;">Institutional access - Real-time Level II market data</small>
            </div>
        </div>
    `);
}

function openOrderFlow() {
    showInstitutionalModal('Live Options Flow', `
        <div style="background: rgba(0,0,0,0.8); padding: 20px; border-radius: 10px;">
            <h5 style="color: #dc2626; margin-bottom: 15px;">Real-time Smart Money Flow</h5>
            <div style="space-y: 10px;">
                <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="color: #10b981; font-weight: 600;">NVDA 01/25 $140 CALL</div>
                            <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem;">Unusual Activity - 847% above average</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #10b981; font-weight: 600;">$12.3M</div>
                            <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem;">Volume</div>
                        </div>
                    </div>
                </div>
                <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="color: #ef4444; font-weight: 600;">TSLA 01/25 $250 PUT</div>
                            <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem;">Large block trade detected</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #ef4444; font-weight: 600;">$8.7M</div>
                            <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem;">Volume</div>
                        </div>
                    </div>
                </div>
            </div>
            <div style="margin-top: 15px; padding: 10px; background: rgba(220,38,38,0.1); border-radius: 8px;">
                <small style="color: #dc2626;">Elite feature - Real-time institutional options flow tracking</small>
            </div>
        </div>
    `);
}

function openRiskManager() {
    showInstitutionalModal('Advanced Risk Management', `
        <div style="background: rgba(0,0,0,0.8); padding: 20px; border-radius: 10px;">
            <h5 style="color: #10b981; margin-bottom: 15px;">Portfolio Risk Analysis</h5>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
                <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="color: #10b981; font-size: 0.8rem; margin-bottom: 5px;">Portfolio Beta</div>
                    <div style="font-size: 1.6rem; font-weight: 700; color: #10b981;">0.87</div>
                    <div style="font-size: 0.7rem; color: rgba(255,255,255,0.7);">Low Risk</div>
                </div>
                <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="color: #ef4444; font-size: 0.8rem; margin-bottom: 5px;">Max Drawdown</div>
                    <div style="font-size: 1.6rem; font-weight: 700; color: #ef4444;">-3.2%</div>
                    <div style="font-size: 0.7rem; color: rgba(255,255,255,0.7);">30 Days</div>
                </div>
                <div style="background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.3); border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="color: #8b5cf6; font-size: 0.8rem; margin-bottom: 5px;">Sharpe Ratio</div>
                    <div style="font-size: 1.6rem; font-weight: 700; color: #8b5cf6;">2.34</div>
                    <div style="font-size: 0.7rem; color: rgba(255,255,255,0.7);">Excellent</div>
                </div>
            </div>
            <div style="margin-top: 15px;">
                <button style="background: linear-gradient(135deg, #10b981, #059669); border: none; color: white; padding: 10px 20px; border-radius: 8px; cursor: pointer; width: 100%;">
                    Auto-Rebalance Portfolio
                </button>
            </div>
            <div style="margin-top: 15px; padding: 10px; background: rgba(16,185,129,0.1); border-radius: 8px;">
                <small style="color: #10b981;">Institutional risk management - Real-time portfolio monitoring</small>
            </div>
        </div>
    `);
}

function openAIBot() {
    showInstitutionalModal('AI Trading Bot', `
        <div style="background: rgba(0,0,0,0.8); padding: 20px; border-radius: 10px;">
            <h5 style="color: #f59e0b; margin-bottom: 15px;">Autonomous Trading AI</h5>
            <div style="background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3); border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div style="color: #f59e0b; font-weight: 600;">Bot Status</div>
                    <div style="background: #10b981; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem;">ACTIVE</div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; text-align: center;">
                    <div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem;">Today's Trades</div>
                        <div style="color: white; font-size: 1.4rem; font-weight: 700;">7</div>
                    </div>
                    <div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem;">Success Rate</div>
                        <div style="color: #10b981; font-size: 1.4rem; font-weight: 700;">87%</div>
                    </div>
                </div>
            </div>
            <div style="margin-bottom: 15px;">
                <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem; margin-bottom: 8px;">Risk Level</div>
                <div style="display: flex; gap: 5px;">
                    <button style="background: #10b981; border: none; color: white; padding: 5px 15px; border-radius: 5px; font-size: 0.8rem;">Conservative</button>
                    <button style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; padding: 5px 15px; border-radius: 5px; font-size: 0.8rem;">Moderate</button>
                    <button style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; padding: 5px 15px; border-radius: 5px; font-size: 0.8rem;">Aggressive</button>
                </div>
            </div>
            <button style="background: linear-gradient(135deg, #f59e0b, #d97706); border: none; color: white; padding: 12px 20px; border-radius: 8px; cursor: pointer; width: 100%; font-weight: 600;">
                Configure AI Strategy
            </button>
            <div style="margin-top: 15px; padding: 10px; background: rgba(245,158,11,0.1); border-radius: 8px;">
                <small style="color: #f59e0b;">Institutional AI - Autonomous trading with institutional-grade algorithms</small>
            </div>
        </div>
    `);
}

function showInstitutionalModal(title, content) {
    // Remove existing modal if any
    const existingModal = document.querySelector('.institutional-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modal = document.createElement('div');
    modal.className = 'institutional-modal';
    modal.innerHTML = `
        <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); z-index: 2000; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(5px);">
            <div style="background: rgba(17,24,39,0.95); border: 1px solid rgba(139,92,246,0.3); border-radius: 15px; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto; position: relative;">
                <div style="background: linear-gradient(135deg, #8b5cf6, #7c3aed); padding: 15px; border-radius: 15px 15px 0 0; display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="color: white; margin: 0; font-weight: 600;">${title}</h4>
                    <button onclick="this.closest('.institutional-modal').remove()" style="background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer; padding: 0; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center;">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div style="padding: 0;">
                    ${content}
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function addProfessionalFeatures() {
    // Add professional status indicator to search box
    const searchContainer = document.querySelector('.search-container, .input-group');
    if (searchContainer && !searchContainer.querySelector('.professional-indicator')) {
        const indicator = document.createElement('div');
        indicator.className = 'professional-indicator';
        indicator.innerHTML = `
            <div style="position: absolute; top: -25px; right: 0; background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: white; padding: 4px 12px; border-radius: 15px 15px 0 0; font-size: 0.7rem; font-weight: 600; z-index: 10;">
                <i class="fas fa-crown"></i> INSTITUTIONAL ACCESS
            </div>
        `;
        searchContainer.style.position = 'relative';
        searchContainer.appendChild(indicator);
    }
}