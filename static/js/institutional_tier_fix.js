// Institutional Tier Fix - Forces institutional status when demo user logs in
document.addEventListener('DOMContentLoaded', function() {
    console.log('Institutional Tier Fix: Checking for demo user...');
    
    // Force institutional status for demo user
    setTimeout(function() {
        checkAndForceInstitutionalStatus();
    }, 1000);
});

function checkAndForceInstitutionalStatus() {
    // Check if we need to force institutional status
    fetch('/api/user-tier-config')
        .then(response => response.json())
        .then(data => {
            console.log('Current tier status:', data);
            
            // If we're still showing Free tier for authenticated user, force institutional
            if (data.success && data.tier_config.tier === 'Free') {
                console.log('Forcing institutional status...');
                forceInstitutionalDisplay();
            }
        })
        .catch(error => {
            console.error('Error checking tier status:', error);
        });
}

function forceInstitutionalDisplay() {
    // Update subscription status display
    const statusElements = document.querySelectorAll('[data-tier-status]');
    statusElements.forEach(element => {
        element.textContent = 'Institutional Features: All Access';
        element.style.color = '#8b5cf6';
        element.style.fontWeight = '600';
    });
    
    // Hide crown upgrade button (institutional users don't need to upgrade)
    const crownButton = document.querySelector('.crown-upgrade-btn');
    if (crownButton) {
        crownButton.style.display = 'none';
    }
    
    // Update any free tier indicators
    const freeIndicators = document.querySelectorAll('[class*="free"], [class*="Free"]');
    freeIndicators.forEach(element => {
        if (element.textContent.includes('Free') || element.textContent.includes('Basic')) {
            element.textContent = element.textContent.replace(/Free|Basic/g, 'Institutional');
        }
    });
    
    // Add institutional styling
    document.body.classList.add('institutional-tier');
    
    // Force refresh tier integration if available
    if (window.tierIntegrationManager) {
        window.tierIntegrationManager.currentTier = 'Institutional';
        window.tierIntegrationManager.tierConfig = getInstitutionalConfig();
        window.tierIntegrationManager.applyTierTransformations();
    }
    
    console.log('Institutional status forced successfully');
}

function getInstitutionalConfig() {
    return {
        tier: 'Institutional',
        theme_config: {
            primary_color: '#8b5cf6',
            accent_color: '#f59e0b'
        },
        ui_features: {
            advanced_charts: true,
            real_time_data: true,
            dark_pool_intelligence: true,
            ai_confidence_display: true
        },
        search_enhancements: {
            real_time_prices: true,
            confidence_scores: true,
            level_2_data: true,
            dark_pool_insights: true,
            suggestions_count: 10
        },
        ai_capabilities: {
            advanced_analysis: true,
            dark_pool_intel: true,
            institutional_features: true
        }
    };
}