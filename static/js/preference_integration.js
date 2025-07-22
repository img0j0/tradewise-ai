/**
 * Preference Integration - Connects account settings with AI analysis
 */

class PreferenceManager {
    constructor() {
        this.preferences = {};
        this.loadPreferences();
        this.setupEventListeners();
    }

    async loadPreferences() {
        try {
            const response = await fetch('/api/preferences');
            if (response.ok) {
                const data = await response.json();
                this.preferences = data.preferences;
                this.updateUI();
            }
        } catch (error) {
            console.error('Error loading preferences:', error);
        }
    }

    async savePreferences(preferences) {
        try {
            const response = await fetch('/api/preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ preferences: preferences })
            });

            if (response.ok) {
                this.preferences = preferences;
                this.showNotification('Preferences saved! AI analysis will now be personalized.', 'success');
                return true;
            } else {
                throw new Error('Failed to save preferences');
            }
        } catch (error) {
            console.error('Error saving preferences:', error);
            this.showNotification('Failed to save preferences. Please try again.', 'error');
            return false;
        }
    }

    setupEventListeners() {
        // Listen for form changes in account settings
        const settingsForm = document.getElementById('settingsForm');
        if (settingsForm) {
            settingsForm.addEventListener('change', this.handleFormChange.bind(this));
            settingsForm.addEventListener('submit', this.handleFormSubmit.bind(this));
        }

        // Real-time preference updates
        const riskTolerance = document.getElementById('riskTolerance');
        if (riskTolerance) {
            riskTolerance.addEventListener('change', (e) => {
                this.updatePreference('risk_tolerance', e.target.value);
            });
        }

        const timeHorizon = document.getElementById('timeHorizon');
        if (timeHorizon) {
            timeHorizon.addEventListener('change', (e) => {
                this.updatePreference('time_horizon', e.target.value);
            });
        }

        // Sector preferences (checkboxes)
        const sectorCheckboxes = document.querySelectorAll('input[name="preferred_sectors"]');
        sectorCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', this.updateSectorPreferences.bind(this));
        });
    }

    updatePreference(key, value) {
        this.preferences[key] = value;
        this.savePreferences(this.preferences);
        
        // Show immediate impact
        this.showPreferenceImpact(key, value);
    }

    updateSectorPreferences() {
        const checkedSectors = Array.from(document.querySelectorAll('input[name="preferred_sectors"]:checked'))
            .map(cb => cb.value);
        
        this.preferences.preferred_sectors = checkedSectors;
        this.savePreferences(this.preferences);
        
        this.showNotification(`Preferred sectors updated: ${checkedSectors.join(', ')}`, 'info');
    }

    showPreferenceImpact(key, value) {
        const impacts = {
            'risk_tolerance': {
                'conservative': 'AI will require higher confidence (80%+) for BUY recommendations',
                'moderate': 'AI will use standard confidence thresholds (70%+) for recommendations',
                'aggressive': 'AI will use lower confidence thresholds (60%+) for opportunities'
            },
            'time_horizon': {
                'short': 'AI will emphasize technical analysis for short-term signals',
                'medium': 'AI will balance technical and fundamental analysis',
                'long': 'AI will emphasize fundamental analysis for long-term value'
            }
        };

        const impact = impacts[key]?.[value];
        if (impact) {
            this.showNotification(`Impact: ${impact}`, 'info', 8000);
        }
    }

    updateUI() {
        // Update form fields with loaded preferences
        const riskTolerance = document.getElementById('riskTolerance');
        if (riskTolerance && this.preferences.risk_tolerance) {
            riskTolerance.value = this.preferences.risk_tolerance;
        }

        const timeHorizon = document.getElementById('timeHorizon');
        if (timeHorizon && this.preferences.time_horizon) {
            timeHorizon.value = this.preferences.time_horizon;
        }

        // Update sector checkboxes
        const preferredSectors = this.preferences.preferred_sectors || [];
        preferredSectors.forEach(sector => {
            const checkbox = document.querySelector(`input[name="preferred_sectors"][value="${sector}"]`);
            if (checkbox) {
                checkbox.checked = true;
            }
        });

        // Show preference summary
        this.updatePreferenceSummary();
    }

    updatePreferenceSummary() {
        const summaryElement = document.getElementById('preferenceSummary');
        if (summaryElement) {
            const summary = this.generatePreferenceSummary();
            summaryElement.innerHTML = summary;
        }
    }

    generatePreferenceSummary() {
        const risk = this.preferences.risk_tolerance || 'moderate';
        const horizon = this.preferences.time_horizon || 'medium';
        const sectors = this.preferences.preferred_sectors || [];
        const confidence = this.preferences.confidence_threshold || 70;

        return `
            <div class="preference-summary">
                <h5><i class="fas fa-user-cog"></i> Your AI Preferences</h5>
                <div class="summary-grid">
                    <div class="summary-item">
                        <strong>Risk Profile:</strong> ${risk.charAt(0).toUpperCase() + risk.slice(1)}
                        <small>(${confidence}% min confidence)</small>
                    </div>
                    <div class="summary-item">
                        <strong>Time Focus:</strong> ${horizon.charAt(0).toUpperCase() + horizon.slice(1)}-term
                    </div>
                    <div class="summary-item">
                        <strong>Preferred Sectors:</strong> 
                        ${sectors.length ? sectors.join(', ') : 'All sectors'}
                    </div>
                </div>
            </div>
        `;
    }

    handleFormChange(event) {
        // Real-time feedback for form changes
        if (event.target.type === 'range') {
            const valueDisplay = event.target.parentElement.querySelector('.range-value');
            if (valueDisplay) {
                valueDisplay.textContent = event.target.value + '%';
            }
        }
    }

    handleFormSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const preferences = {};
        
        // Convert form data to preferences object
        for (let [key, value] of formData.entries()) {
            if (key === 'preferred_sectors') {
                if (!preferences.preferred_sectors) {
                    preferences.preferred_sectors = [];
                }
                preferences.preferred_sectors.push(value);
            } else {
                preferences[key] = value;
            }
        }

        this.savePreferences(preferences);
    }

    showNotification(message, type = 'info', duration = 5000) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `preference-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            animation: slideInRight 0.3s ease-out;
            color: white;
            font-weight: 500;
            background: ${this.getNotificationColor(type)};
        `;

        document.body.appendChild(notification);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, duration);
        }
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    }

    getNotificationColor(type) {
        const colors = {
            success: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            error: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
            warning: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            info: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)'
        };
        return colors[type] || colors.info;
    }

    // Test AI integration with current preferences
    async testAIIntegration(symbol = 'AAPL') {
        try {
            this.showNotification('Testing AI analysis with your preferences...', 'info');
            
            const response = await fetch('/api/stock-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: symbol })
            });

            if (response.ok) {
                const data = await response.json();
                const analysis = data.analysis || {};
                
                let testResult = `AI Test Results for ${symbol}:\n`;
                testResult += `• Recommendation: ${analysis.recommendation || 'N/A'}\n`;
                testResult += `• Confidence: ${analysis.confidence || 'N/A'}%\n`;
                
                if (analysis.preferences_applied) {
                    testResult += `• Preferences Applied: ✅\n`;
                    testResult += `• Risk Tolerance: ${analysis.preferences_applied.risk_tolerance}\n`;
                } else {
                    testResult += `• Preferences Applied: ❌`;
                }

                console.log(testResult);
                this.showNotification('AI integration test completed! Check console for details.', 'success');
            }
        } catch (error) {
            console.error('AI integration test failed:', error);
            this.showNotification('AI integration test failed. Check console for details.', 'error');
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.preferenceManager = new PreferenceManager();
    
    // Add test button for debugging
    if (window.location.pathname.includes('settings')) {
        setTimeout(() => {
            const testButton = document.createElement('button');
            testButton.textContent = 'Test AI Integration';
            testButton.className = 'btn btn-outline-primary btn-sm';
            testButton.onclick = () => window.preferenceManager.testAIIntegration();
            testButton.style.position = 'fixed';
            testButton.style.bottom = '20px';
            testButton.style.right = '20px';
            testButton.style.zIndex = '9999';
            document.body.appendChild(testButton);
        }, 1000);
    }
});

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .preference-summary {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .summary-grid {
        display: grid;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .summary-item {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .summary-item small {
        opacity: 0.7;
        font-size: 0.85rem;
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: inherit;
        cursor: pointer;
        padding: 0.25rem;
        margin-left: auto;
        opacity: 0.8;
        transition: opacity 0.2s;
    }
    
    .notification-close:hover {
        opacity: 1;
    }
`;
document.head.appendChild(style);