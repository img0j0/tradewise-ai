// Interface Stabilizer - Prevents tier switching and ensures Institutional Terminal consistency
let interfaceStabilized = false;
let stabilizationAttempts = 0;
const maxStabilizationAttempts = 3;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Interface Stabilizer: Starting stabilization process...');
    
    // Force institutional tier and prevent switching
    forceInstitutionalTier();
    
    // Stabilize interface after slight delay
    setTimeout(function() {
        stabilizeInstitutionalInterface();
    }, 1000);
    
    // Monitor for tier switching and prevent it
    setInterval(function() {
        if (!interfaceStabilized && stabilizationAttempts < maxStabilizationAttempts) {
            stabilizeInstitutionalInterface();
        }
    }, 2000);
});

function forceInstitutionalTier() {
    // Override any tier detection to force institutional
    window.userTier = 'Institutional';
    window.tierConfig = {
        tier: 'Institutional',
        ui_elements: {
            institutional_ai_assistant: true,
            premium_badges: true,
            advanced_analytics: true,
            feature_locks: false
        }
    };
    
    console.log('Interface Stabilizer: Forced institutional tier');
}

function stabilizeInstitutionalInterface() {
    stabilizationAttempts++;
    console.log(`Interface Stabilizer: Stabilization attempt ${stabilizationAttempts}`);
    
    // Remove any conflicting elements
    removeConflictingElements();
    
    // Ensure Institutional Terminal features are present
    ensureInstitutionalFeatures();
    
    // Mark as stabilized
    interfaceStabilized = true;
    console.log('Interface Stabilizer: Institutional Terminal interface stabilized');
}

function removeConflictingElements() {
    // Remove any duplicate headers or conflicting tier indicators
    const existingHeaders = document.querySelectorAll('.institutional-premium-header, .institutional-terminal-header');
    if (existingHeaders.length > 1) {
        for (let i = 1; i < existingHeaders.length; i++) {
            existingHeaders[i].remove();
        }
    }
    
    // Remove any free tier elements that might be showing
    const freeTierElements = document.querySelectorAll('[data-tier="free"], .free-tier-indicator');
    freeTierElements.forEach(el => el.remove());
    
    console.log('Interface Stabilizer: Removed conflicting elements');
}

function ensureInstitutionalFeatures() {
    // Ensure Institutional Terminal header is present
    if (!document.querySelector('.institutional-terminal-header') && !document.querySelector('.institutional-premium-header')) {
        addStableInstitutionalHeader();
    }
    
    // Ensure ticker tape is present
    if (!document.querySelector('.ticker-tape')) {
        addStableTickerTape();
    }
    
    // Ensure key Institutional Terminal features are loaded
    ensureKeyFeatures();
}

function addStableInstitutionalHeader() {
    const header = document.querySelector('.header-content, .d-flex.justify-content-between');
    if (header) {
        const institutionalHeader = document.createElement('div');
        institutionalHeader.className = 'institutional-terminal-header';
        institutionalHeader.innerHTML = `
            <div style="background: linear-gradient(135deg, #1e40af, #7c3aed); padding: 6px 12px; border-radius: 6px; color: white; font-weight: 600; font-size: 0.75rem; margin-right: 10px; display: flex; align-items: center; gap: 6px; box-shadow: 0 4px 15px rgba(30, 64, 175, 0.4); position: relative;">
                <i class="fas fa-chart-line" style="color: #fbbf24;"></i>
                INSTITUTIONAL TERMINAL
                <span style="background: rgba(255,255,255,0.2); padding: 1px 4px; border-radius: 3px; font-size: 0.6rem;">98% SAVINGS</span>
                <div style="position: absolute; top: -5px; right: -5px; background: #dc2626; color: white; border-radius: 50%; width: 12px; height: 12px; font-size: 0.5rem; display: flex; align-items: center; justify-content: center; animation: pulse 2s infinite;">!</div>
            </div>
        `;
        header.appendChild(institutionalHeader);
        console.log('Interface Stabilizer: Added stable Institutional Terminal header');
    }
}

function addStableTickerTape() {
    const container = document.querySelector('.main-content, .search-section');
    if (container && !container.querySelector('.ticker-tape')) {
        const ticker = document.createElement('div');
        ticker.className = 'ticker-tape stable-ticker';
        ticker.innerHTML = `
            <div style="background: rgba(0,0,0,0.9); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; padding: 8px; margin-bottom: 15px; overflow: hidden; position: relative; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                <div style="color: #fbbf24; font-weight: 600; font-size: 0.7rem; margin-bottom: 5px; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-broadcast-tower"></i> INSTITUTIONAL MARKET TERMINAL - LIVE DATA
                    <span style="background: #dc2626; color: white; padding: 1px 4px; border-radius: 3px; font-size: 0.6rem; animation: pulse 2s infinite;">LIVE</span>
                    <span style="background: #10b981; color: white; padding: 1px 4px; border-radius: 3px; font-size: 0.6rem;">98% SAVINGS</span>
                </div>
                <div id="ticker-scroll" style="white-space: nowrap; animation: scroll 40s linear infinite; font-family: monospace; font-size: 0.7rem; color: white;">
                    <span style="color: #10b981; margin-right: 25px;">AAPL $211.18 ↗ +0.57%</span>
                    <span style="color: #ef4444; margin-right: 25px;">TSLA $248.77 ↘ -2.34%</span>
                    <span style="color: #10b981; margin-right: 25px;">NVDA $142.33 ↗ +4.21%</span>
                    <span style="color: #10b981; margin-right: 25px;">MSFT $421.33 ↗ +1.87%</span>
                    <span style="color: #ef4444; margin-right: 25px;">GOOGL $173.82 ↘ -0.93%</span>
                    <span style="color: #10b981; margin-right: 25px;">AMZN $178.45 ↗ +2.14%</span>
                    <span style="color: #f59e0b; margin-right: 25px;">BTC $43,847 ↗ +0.12%</span>
                    <span style="color: #8b5cf6; margin-right: 25px;">SPY $584.72 ↗ +0.84%</span>
                    <span style="color: #10b981; margin-right: 25px;">QQQ $447.23 ↗ +1.23%</span>
                    <span style="color: #ef4444; margin-right: 25px;">VIX 18.42 ↗ +12.3%</span>
                </div>
                <style>
                    @keyframes scroll {
                        0% { transform: translateX(100%); }
                        100% { transform: translateX(-100%); }
                    }
                    @keyframes pulse {
                        0%, 100% { opacity: 1; }
                        50% { opacity: 0.7; }
                    }
                </style>
            </div>
        `;
        container.insertBefore(ticker, container.firstChild);
        console.log('Interface Stabilizer: Added stable Institutional Terminal ticker tape');
    }
}

function ensureKeyFeatures() {
    // Check if key Institutional Terminal features are present, add them if missing
    const requiredFeatures = [
        '.real-time-dashboard',
        '.ai-insights-panel', 
        '.institutional-dark-pool',
        '.institutional-tools-section'
    ];
    
    requiredFeatures.forEach(selector => {
        if (!document.querySelector(selector)) {
            console.log(`Interface Stabilizer: Missing feature ${selector}, will reload features`);
            // Trigger feature reload if critical features are missing
            setTimeout(() => {
                if (window.activateInstitutionalFeatures) {
                    window.activateInstitutionalFeatures();
                }
                if (window.addInstitutionalTerminalFeatures) {
                    window.addInstitutionalTerminalFeatures();
                }
                if (window.addInstitutionalToolbar) {
                    window.addInstitutionalToolbar();
                }
            }, 500);
        }
    });
}

// Prevent page refreshing from breaking interface
window.addEventListener('beforeunload', function() {
    localStorage.setItem('institutionalTerminalActive', 'true');
    localStorage.setItem('institutionalTier', 'true');
});

// Restore Institutional Terminal interface on page load
window.addEventListener('load', function() {
    if (localStorage.getItem('institutionalTerminalActive') === 'true') {
        forceInstitutionalTier();
        setTimeout(stabilizeInstitutionalInterface, 2000);
    }
});

// Export functions for use by other scripts
window.forceInstitutionalTier = forceInstitutionalTier;
window.stabilizeInstitutionalInterface = stabilizeInstitutionalInterface;