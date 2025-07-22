/**
 * Preference Display Enhancement - Shows when user preferences affect AI analysis
 */

// Load user preferences globally
let globalUserPreferences = null;

// Load preferences on page startup
async function loadGlobalPreferences() {
    try {
        const response = await fetch('/api/preferences');
        if (response.ok) {
            const data = await response.json();
            globalUserPreferences = data.preferences;
            console.log('✅ Global preferences loaded:', globalUserPreferences);
            
            // Add preference status indicator to search interface
            addPreferenceStatusIndicator();
        }
    } catch (error) {
        console.error('Failed to load global preferences:', error);
    }
}

// Add preference status indicator to the search interface (removed - too intrusive)
function addPreferenceStatusIndicator() {
    // Removed intrusive main screen indicator - preferences shown only in analysis results
    console.log('Preference status loaded silently - no main screen indicator');
}

// Generate preference indicator for analysis results
function generatePreferenceIndicator(analysisData) {
    if (!analysisData || !analysisData.preferences_applied) {
        return ''; // No preferences applied
    }
    
    const prefs = analysisData.preferences_applied;
    const indicators = [];
    
    // Risk tolerance indicator
    if (prefs.risk_tolerance) {
        const riskIcons = {
            'conservative': '🛡️',
            'moderate': '⚖️', 
            'aggressive': '🚀'
        };
        indicators.push(`
            <div class="preference-chip risk-${prefs.risk_tolerance}" title="Risk tolerance: ${prefs.risk_tolerance}">
                ${riskIcons[prefs.risk_tolerance] || '⚖️'} ${prefs.risk_tolerance.charAt(0).toUpperCase() + prefs.risk_tolerance.slice(1)}
            </div>
        `);
    }
    
    // Sector preference indicator
    if (analysisData.sector_boost) {
        indicators.push(`
            <div class="preference-chip sector-preferred" title="Preferred sector boost applied">
                ⭐ Sector Preference
            </div>
        `);
    }
    
    // Confidence threshold indicator
    if (analysisData.threshold_adjusted) {
        indicators.push(`
            <div class="preference-chip threshold-adjusted" title="Adjusted for your confidence threshold">
                📊 Confidence Filter
            </div>
        `);
    }
    
    // Time horizon indicator
    if (prefs.time_horizon && analysisData.time_horizon_note) {
        const horizonIcons = {
            'short': '⚡',
            'medium': '📈',
            'long': '🌱'
        };
        indicators.push(`
            <div class="preference-chip horizon-${prefs.time_horizon}" title="${analysisData.time_horizon_note}">
                ${horizonIcons[prefs.time_horizon] || '📈'} ${prefs.time_horizon}-term
            </div>
        `);
    }
    
    if (indicators.length === 0) {
        return ''; // No visual changes to show
    }
    
    return `
        <div class="preference-indicators" style="margin-top: 10px;">
            <div style="font-size: 0.75rem; opacity: 0.8; margin-bottom: 5px;">
                <i class="fas fa-magic"></i> Personalized for you:
            </div>
            <div class="preference-chips">
                ${indicators.join('')}
            </div>
        </div>
    `;
}

// Show detailed preference explanation
function showPreferenceExplanation(analysisData) {
    if (!analysisData || !analysisData.preferences_applied) {
        return 'Standard AI analysis applied.';
    }
    
    const prefs = analysisData.preferences_applied;
    const explanations = [];
    
    if (prefs.risk_tolerance) {
        const riskExplanations = {
            'conservative': `Conservative risk setting requires ${prefs.confidence_threshold || 80}%+ confidence for BUY recommendations`,
            'moderate': `Moderate risk setting uses standard ${prefs.confidence_threshold || 70}%+ confidence thresholds`,
            'aggressive': `Aggressive risk setting accepts ${prefs.confidence_threshold || 60}%+ confidence for opportunities`
        };
        explanations.push(riskExplanations[prefs.risk_tolerance]);
    }
    
    if (prefs.time_horizon && analysisData.time_horizon_note) {
        explanations.push(analysisData.time_horizon_note);
    }
    
    if (analysisData.sector_boost && analysisData.sector_note) {
        explanations.push(analysisData.sector_note);
    }
    
    if (analysisData.risk_note) {
        explanations.push(analysisData.risk_note);
    }
    
    return explanations.length > 0 ? explanations.join(' • ') : 'Analysis personalized based on your account preferences.';
}

// Toggle preference details panel
function togglePreferenceDetails() {
    let panel = document.getElementById('preference-details-panel');
    
    if (panel) {
        panel.remove();
        return;
    }
    
    panel = document.createElement('div');
    panel.id = 'preference-details-panel';
    panel.innerHTML = `
        <div class="preference-panel-content">
            <div class="preference-panel-header">
                <h5><i class="fas fa-user-cog"></i> Your AI Preferences</h5>
                <button onclick="togglePreferenceDetails()" class="close-btn">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="preference-panel-body">
                ${generatePreferenceSummary()}
                <div class="preference-actions">
                    <button onclick="window.open('/settings', '_blank')" class="btn-primary">
                        <i class="fas fa-cog"></i> Adjust Preferences
                    </button>
                    <button onclick="testPreferenceImpact()" class="btn-secondary">
                        <i class="fas fa-flask"></i> Test Impact
                    </button>
                </div>
            </div>
        </div>
    `;
    
    panel.style.cssText = `
        position: fixed;
        top: 120px;
        right: 20px;
        width: 350px;
        background: rgba(26, 26, 46, 0.95);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        color: white;
        z-index: 10001;
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(panel);
}

// Generate preference summary
function generatePreferenceSummary() {
    if (!globalUserPreferences) {
        return '<p style="opacity: 0.7;">No preferences loaded.</p>';
    }
    
    const prefs = globalUserPreferences;
    return `
        <div class="preference-summary-grid">
            <div class="pref-item">
                <strong>Risk Tolerance:</strong>
                <span class="pref-value risk-${prefs.risk_tolerance}">${prefs.risk_tolerance || 'moderate'}</span>
            </div>
            <div class="pref-item">
                <strong>Time Horizon:</strong>
                <span class="pref-value">${prefs.time_horizon || 'medium'}-term</span>
            </div>
            <div class="pref-item">
                <strong>Confidence Threshold:</strong>
                <span class="pref-value">${prefs.confidence_threshold || 70}%</span>
            </div>
            <div class="pref-item">
                <strong>Preferred Sectors:</strong>
                <span class="pref-value">
                    ${prefs.preferred_sectors && prefs.preferred_sectors.length > 0 
                        ? prefs.preferred_sectors.join(', ') 
                        : 'All sectors'}
                </span>
            </div>
        </div>
    `;
}

// Test preference impact with demo
async function testPreferenceImpact() {
    try {
        const testSymbol = 'AAPL';
        showNotification('Testing preference impact with AAPL...', 'info');
        
        const response = await fetch('/api/stock-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: testSymbol })
        });
        
        if (response.ok) {
            const data = await response.json();
            const analysis = data.analysis || {};
            
            if (analysis.preferences_applied) {
                showNotification('✅ Preferences are working! Check the analysis for personalized results.', 'success');
            } else {
                showNotification('⚠️ Preferences not detected in analysis. Check account settings.', 'warning');
            }
        }
    } catch (error) {
        showNotification('❌ Test failed. Please try again.', 'error');
    }
}

// Enhanced notification system
function showNotification(message, type = 'info', duration = 4000) {
    const notification = document.createElement('div');
    notification.className = `preference-notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10002;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        animation: slideInRight 0.3s ease-out;
        max-width: 400px;
    `;
    
    document.body.appendChild(notification);
    
    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);
    }
}

// Add CSS styles
const preferenceStyles = document.createElement('style');
preferenceStyles.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .preference-status-bar {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
    }
    
    .preference-toggle {
        background: rgba(255, 255, 255, 0.2);
        border: none;
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        cursor: pointer;
        transition: background 0.2s;
    }
    
    .preference-toggle:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    .preference-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }
    
    .preference-chip {
        background: rgba(59, 130, 246, 0.2);
        border: 1px solid rgba(59, 130, 246, 0.4);
        color: #93c5fd;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 500;
    }
    
    .preference-chip.risk-conservative { background: rgba(16, 185, 129, 0.2); border-color: rgba(16, 185, 129, 0.4); color: #6ee7b7; }
    .preference-chip.risk-aggressive { background: rgba(239, 68, 68, 0.2); border-color: rgba(239, 68, 68, 0.4); color: #fca5a5; }
    .preference-chip.sector-preferred { background: rgba(245, 158, 11, 0.2); border-color: rgba(245, 158, 11, 0.4); color: #fbbf24; }
    
    .preference-panel-content {
        padding: 20px;
    }
    
    .preference-panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 10px;
    }
    
    .close-btn {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 5px;
        opacity: 0.7;
        transition: opacity 0.2s;
    }
    
    .close-btn:hover { opacity: 1; }
    
    .preference-summary-grid {
        display: grid;
        gap: 12px;
        margin-bottom: 20px;
    }
    
    .pref-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .pref-value {
        font-weight: 600;
        opacity: 0.9;
    }
    
    .pref-value.risk-conservative { color: #10b981; }
    .pref-value.risk-moderate { color: #3b82f6; }
    .pref-value.risk-aggressive { color: #ef4444; }
    
    .preference-actions {
        display: flex;
        gap: 10px;
    }
    
    .preference-actions button {
        flex: 1;
        padding: 10px 15px;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
    }
    
    .btn-secondary {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .notification-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .notification-content button {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        opacity: 0.8;
        margin-left: 10px;
    }
    
    .notification-content button:hover { opacity: 1; }
`;

document.head.appendChild(preferenceStyles);

// Initialize on page load
document.addEventListener('DOMContentLoaded', loadGlobalPreferences);

// Make functions globally available
window.generatePreferenceIndicator = generatePreferenceIndicator;
window.showPreferenceExplanation = showPreferenceExplanation;
window.togglePreferenceDetails = togglePreferenceDetails;
window.testPreferenceImpact = testPreferenceImpact;