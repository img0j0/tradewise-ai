// Premium Lock System JavaScript - Phase 5
// Premium features, upgrade flows, and notifications

document.addEventListener('DOMContentLoaded', function() {
    initializePremiumLockSystem();
    initializeNotificationSystem();
    initializePremiumUpgradeModal();
});

// Premium Lock System
function initializePremiumLockSystem() {
    // Add lock icons to premium features
    addPremiumLockIcons();
    
    // Handle premium feature clicks
    handlePremiumFeatureClicks();
    
    // Initialize tooltips
    initializePremiumTooltips();
}

// Add lock icons to premium features
function addPremiumLockIcons() {
    const premiumFeatures = document.querySelectorAll('[data-premium]');
    
    premiumFeatures.forEach(feature => {
        if (!feature.querySelector('.premium-lock-icon')) {
            const lockIcon = createPremiumLockIcon();
            feature.appendChild(lockIcon);
            feature.classList.add('premium-feature', 'clickable');
        }
    });
}

// Create premium lock icon with tooltip
function createPremiumLockIcon() {
    const lockContainer = document.createElement('div');
    lockContainer.className = 'premium-lock-icon';
    lockContainer.innerHTML = `
        <i class="fas fa-lock"></i>
        <div class="premium-tooltip">
            Unlock this feature with Pro or Enterprise
        </div>
    `;
    return lockContainer;
}

// Handle clicks on premium features
function handlePremiumFeatureClicks() {
    document.addEventListener('click', function(e) {
        const premiumFeature = e.target.closest('[data-premium]');
        
        if (premiumFeature && !isUserPremium()) {
            e.preventDefault();
            e.stopPropagation();
            
            const featureType = premiumFeature.getAttribute('data-premium');
            showPremiumUpgradeModal(featureType, premiumFeature);
        }
    });
}

// Initialize premium tooltips
function initializePremiumTooltips() {
    const lockIcons = document.querySelectorAll('.premium-lock-icon');
    
    lockIcons.forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            const tooltip = this.querySelector('.premium-tooltip');
            if (tooltip) {
                tooltip.style.opacity = '1';
                tooltip.style.visibility = 'visible';
            }
        });
        
        icon.addEventListener('mouseleave', function() {
            const tooltip = this.querySelector('.premium-tooltip');
            if (tooltip) {
                tooltip.style.opacity = '0';
                tooltip.style.visibility = 'hidden';
            }
        });
    });
}

// Premium Upgrade Modal System
function initializePremiumUpgradeModal() {
    // Create modal if it doesn't exist
    if (!document.getElementById('premium-upgrade-modal')) {
        createPremiumUpgradeModal();
    }
    
    // Handle modal close
    document.addEventListener('click', function(e) {
        if (e.target.matches('.premium-upgrade-modal') || 
            e.target.matches('.premium-upgrade-close')) {
            closePremiumUpgradeModal();
        }
    });
    
    // Handle escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closePremiumUpgradeModal();
        }
    });
}

// Create premium upgrade modal
function createPremiumUpgradeModal() {
    const modal = document.createElement('div');
    modal.id = 'premium-upgrade-modal';
    modal.className = 'premium-upgrade-modal';
    modal.innerHTML = `
        <div class="premium-upgrade-content">
            <button class="premium-upgrade-close">
                <i class="fas fa-times"></i>
            </button>
            
            <div class="premium-upgrade-header">
                <div class="premium-upgrade-icon">
                    <i class="fas fa-crown"></i>
                </div>
                <h2 class="premium-upgrade-title" id="upgrade-modal-title">
                    Unlock Premium Features
                </h2>
                <p class="premium-upgrade-subtitle" id="upgrade-modal-subtitle">
                    Get access to advanced tools and insights
                </p>
            </div>
            
            <div class="feature-preview" id="feature-preview">
                <div class="feature-preview-title">
                    <i class="fas fa-star"></i>
                    This Premium Feature Includes:
                </div>
                <ul class="feature-preview-list" id="feature-preview-list">
                    <!-- Dynamic feature list will be inserted here -->
                </ul>
            </div>
            
            <div class="upgrade-cta-container">
                <a href="/subscription/checkout?plan=pro" class="upgrade-cta-btn upgrade-cta-primary">
                    Upgrade to Pro - $29.99/month
                </a>
                <a href="/subscription/checkout?plan=enterprise" class="upgrade-cta-btn upgrade-cta-secondary">
                    Enterprise - $99.99/month
                </a>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Show premium upgrade modal with feature-specific content
function showPremiumUpgradeModal(featureType, featureElement) {
    const modal = document.getElementById('premium-upgrade-modal');
    if (!modal) return;
    
    // Update modal content based on feature type
    updateModalContent(featureType, featureElement);
    
    // Show modal
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Track upgrade modal view
    trackPremiumUpgradeView(featureType);
}

// Update modal content for specific features
function updateModalContent(featureType, featureElement) {
    const featureConfigs = {
        'backtest': {
            title: 'Unlock Portfolio Backtesting',
            subtitle: 'Test your investment strategies with historical data',
            features: [
                'Historical performance analysis',
                'Risk-adjusted returns calculation',
                'Benchmark comparisons',
                'Strategy optimization tools',
                'Detailed performance reports'
            ]
        },
        'peer-comparison': {
            title: 'Unlock Peer Analysis',
            subtitle: 'Compare stocks against industry competitors',
            features: [
                'Comprehensive peer comparisons',
                'Industry benchmark analysis',
                'Relative valuation metrics',
                'Competitive positioning insights',
                'Sector performance rankings'
            ]
        },
        'ai-insights': {
            title: 'Unlock Advanced AI Insights',
            subtitle: 'Get institutional-grade AI analysis',
            features: [
                'Advanced pattern recognition',
                'Predictive market analysis',
                'Risk assessment algorithms',
                'Opportunity detection alerts',
                'Portfolio optimization suggestions'
            ]
        },
        'alerts': {
            title: 'Unlock Smart Alerts',
            subtitle: 'Never miss important market movements',
            features: [
                'Unlimited price alerts',
                'Technical indicator alerts',
                'News sentiment alerts',
                'Volume surge notifications',
                'Custom alert conditions'
            ]
        },
        'default': {
            title: 'Unlock Premium Features',
            subtitle: 'Access professional-grade investment tools',
            features: [
                'Advanced analytics and insights',
                'Unlimited watchlists and alerts',
                'Portfolio optimization tools',
                'Priority customer support',
                'Early access to new features'
            ]
        }
    };
    
    const config = featureConfigs[featureType] || featureConfigs['default'];
    
    // Update modal content
    document.getElementById('upgrade-modal-title').textContent = config.title;
    document.getElementById('upgrade-modal-subtitle').textContent = config.subtitle;
    
    const featureList = document.getElementById('feature-preview-list');
    featureList.innerHTML = config.features.map(feature => 
        `<li class="feature-preview-item">${feature}</li>`
    ).join('');
}

// Close premium upgrade modal
function closePremiumUpgradeModal() {
    const modal = document.getElementById('premium-upgrade-modal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Check if user has premium access
function isUserPremium() {
    // Check user plan from session or API
    const planBadge = document.getElementById('plan-badge');
    if (planBadge) {
        const planText = planBadge.textContent.toLowerCase();
        return planText.includes('pro') || planText.includes('enterprise');
    }
    return false;
}

// Notification System
let notificationContainer = null;

function initializeNotificationSystem() {
    // Create notification container
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.className = 'notification-container';
        document.body.appendChild(notificationContainer);
    }
    
    // Listen for notification events
    window.addEventListener('premium-upgrade-success', handleUpgradeSuccess);
    window.addEventListener('premium-downgrade-success', handleDowngradeSuccess);
    window.addEventListener('alert-saved', handleAlertSaved);
    window.addEventListener('alert-triggered', handleAlertTriggered);
}

// Show notification
function showNotification(type, title, message, duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const iconMap = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    notification.innerHTML = `
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
        <div class="notification-header">
            <i class="notification-icon ${iconMap[type]}"></i>
            <span class="notification-title">${title}</span>
        </div>
        <div class="notification-message">${message}</div>
    `;
    
    // Add to container
    notificationContainer.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Auto-hide notification
    const hideTimer = setTimeout(() => {
        hideNotification(notification);
    }, duration);
    
    // Handle close button
    notification.querySelector('.notification-close').addEventListener('click', () => {
        clearTimeout(hideTimer);
        hideNotification(notification);
    });
    
    return notification;
}

// Hide notification
function hideNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

// Handle upgrade success
function handleUpgradeSuccess(event) {
    const plan = event.detail?.plan || 'Pro';
    showNotification(
        'success',
        'Upgrade Successful!',
        `Welcome to TradeWise AI ${plan}! You now have access to all premium features.`,
        7000
    );
    
    // Remove lock icons from premium features
    removePremiumLocks();
    
    // Update plan badge
    updatePlanBadge(plan);
}

// Handle downgrade success
function handleDowngradeSuccess(event) {
    const plan = event.detail?.plan || 'Free';
    showNotification(
        'info',
        'Plan Changed',
        `Your plan has been updated to ${plan}. Thank you for using TradeWise AI!`,
        6000
    );
    
    // Add lock icons back to premium features
    addPremiumLockIcons();
    
    // Update plan badge
    updatePlanBadge(plan);
}

// Handle alert saved
function handleAlertSaved(event) {
    const alertData = event.detail || {};
    showNotification(
        'success',
        'Alert Saved',
        `Your ${alertData.type || 'price'} alert for ${alertData.symbol || 'stock'} has been saved and is now active.`,
        4000
    );
}

// Handle alert triggered
function handleAlertTriggered(event) {
    const alertData = event.detail || {};
    showNotification(
        'warning',
        'Alert Triggered!',
        `${alertData.symbol || 'Stock'} alert: ${alertData.message || 'Condition met'}`,
        8000
    );
}

// Remove premium locks when user upgrades
function removePremiumLocks() {
    const lockIcons = document.querySelectorAll('.premium-lock-icon');
    lockIcons.forEach(icon => icon.remove());
    
    const premiumFeatures = document.querySelectorAll('.premium-feature');
    premiumFeatures.forEach(feature => {
        feature.classList.remove('premium-feature', 'locked', 'clickable');
    });
}

// Update plan badge
function updatePlanBadge(plan) {
    const planBadge = document.getElementById('plan-badge');
    if (planBadge) {
        const badgeClass = plan.toLowerCase() === 'free' ? 'free' : 'premium';
        planBadge.className = `plan-badge ${badgeClass}`;
        
        const icon = plan.toLowerCase() === 'free' ? 'fas fa-user' : 'fas fa-crown';
        planBadge.innerHTML = `<i class="${icon}"></i> ${plan}`;
    }
}

// Track premium upgrade modal views
function trackPremiumUpgradeView(featureType) {
    // Send analytics event
    if (typeof gtag !== 'undefined') {
        gtag('event', 'premium_upgrade_modal_view', {
            'feature_type': featureType,
            'event_category': 'Premium',
            'event_label': featureType
        });
    }
    
    console.log('Premium upgrade modal viewed for feature:', featureType);
}

// Utility functions for external integration
window.PremiumLockSystem = {
    showUpgradeModal: showPremiumUpgradeModal,
    closeUpgradeModal: closePremiumUpgradeModal,
    showNotification: showNotification,
    isUserPremium: isUserPremium,
    
    // Event triggers for external use
    triggerUpgradeSuccess: (plan) => {
        window.dispatchEvent(new CustomEvent('premium-upgrade-success', { 
            detail: { plan } 
        }));
    },
    
    triggerAlertSaved: (alertData) => {
        window.dispatchEvent(new CustomEvent('alert-saved', { 
            detail: alertData 
        }));
    },
    
    triggerAlertTriggered: (alertData) => {
        window.dispatchEvent(new CustomEvent('alert-triggered', { 
            detail: alertData 
        }));
    }
};