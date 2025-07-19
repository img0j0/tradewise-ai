/**
 * Account Settings JavaScript
 * Handles all interactions for the account settings page
 */

class AccountSettings {
    constructor() {
        this.init();
    }

    init() {
        // Load data when page loads
        this.loadProfileData();
        this.loadPaymentMethods();
        this.loadSubscriptionDetails();
        this.loadNotificationPreferences();
        
        // Set up event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Tab change listeners
        document.querySelectorAll('[data-bs-toggle="pill"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const targetTab = e.target.getAttribute('data-bs-target');
                this.onTabChange(targetTab);
            });
        });
    }

    onTabChange(targetTab) {
        // Load data specific to the active tab
        switch(targetTab) {
            case '#payments':
                this.loadPaymentMethods();
                break;
            case '#subscription':
                this.loadSubscriptionDetails();
                break;
            case '#notifications':
                this.loadNotificationPreferences();
                break;
        }
    }

    async loadProfileData() {
        try {
            const response = await fetch('/api/account/profile');
            const data = await response.json();
            
            if (data.error) {
                this.showError('Failed to load profile data');
                return;
            }

            // Populate profile form
            const userInfo = data.user_info || {};
            const accountInfo = data.account_info || {};

            document.getElementById('firstName').value = userInfo.first_name || '';
            document.getElementById('lastName').value = userInfo.last_name || '';
            document.getElementById('email').value = userInfo.email || '';
            
            if (userInfo.profile_image_url) {
                const img = document.getElementById('profileImage');
                img.src = userInfo.profile_image_url;
                img.style.display = 'block';
            }

            // Update statistics
            document.getElementById('totalTrades').textContent = accountInfo.total_trades || '0';
            document.getElementById('accountBalance').textContent = '$' + (accountInfo.balance || '0.00');
            document.getElementById('memberSince').textContent = accountInfo.member_since || 'Recently';
            document.getElementById('lastLogin').textContent = userInfo.last_login || 'Unknown';

        } catch (error) {
            console.error('Error loading profile:', error);
            this.showError('Failed to load profile data');
        }
    }

    async loadPaymentMethods() {
        try {
            const response = await fetch('/api/account/payment-methods');
            const data = await response.json();
            
            if (!data.success) {
                this.showError('Failed to load payment methods');
                return;
            }

            this.renderPaymentMethods(data.payment_methods);

        } catch (error) {
            console.error('Error loading payment methods:', error);
            this.showError('Failed to load payment methods');
        }
    }

    renderPaymentMethods(paymentMethods) {
        const container = document.getElementById('paymentMethodsList');
        const cards = paymentMethods.cards || [];
        
        if (cards.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-credit-card fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No payment methods added</h5>
                    <p class="text-muted">Add a payment method to start trading</p>
                </div>
            `;
            return;
        }

        container.innerHTML = cards.map(card => `
            <div class="payment-method-card ${card.is_default ? 'default' : ''}">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="d-flex align-items-center">
                        <i class="fab fa-cc-${card.brand} fa-2x me-3 text-primary"></i>
                        <div>
                            <h6 class="mb-1">•••• •••• •••• ${card.last4}</h6>
                            <small class="text-muted">Expires ${card.exp_month}/${card.exp_year}</small>
                            ${card.is_default ? '<br><small class="text-success"><i class="fas fa-check"></i> Default</small>' : ''}
                        </div>
                    </div>
                    <div class="btn-group">
                        ${!card.is_default ? '<button class="btn btn-sm btn-outline-primary" onclick="setDefaultPaymentMethod(\'' + card.id + '\')">Set Default</button>' : ''}
                        <button class="btn btn-sm btn-outline-danger" onclick="removePaymentMethod('${card.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                ${card.billing_address ? `
                    <div class="mt-2">
                        <small class="text-muted">
                            ${card.billing_address.line1}<br>
                            ${card.billing_address.city}, ${card.billing_address.state} ${card.billing_address.postal_code}
                        </small>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    async loadSubscriptionDetails() {
        try {
            const response = await fetch('/api/account/subscription');
            const data = await response.json();
            
            if (!data.success) {
                this.showError('Failed to load subscription details');
                return;
            }

            this.renderSubscriptionDetails(data.subscription);

        } catch (error) {
            console.error('Error loading subscription:', error);
            this.showError('Failed to load subscription details');
        }
    }

    renderSubscriptionDetails(subscription) {
        const currentPlan = subscription.current_plan || {};
        const usageStats = subscription.usage_stats || {};
        const availablePlans = subscription.available_plans || [];

        // Render current plan
        document.getElementById('currentPlan').innerHTML = `
            <div class="plan-badge">Current</div>
            <h5>${currentPlan.name} Plan</h5>
            <h3 class="text-primary">$${currentPlan.price}/month</h3>
            <p class="text-muted">Next billing: ${currentPlan.next_billing_date}</p>
            <ul class="list-unstyled mt-3">
                ${(currentPlan.features || []).map(feature => `<li><i class="fas fa-check text-success me-2"></i>${feature}</li>`).join('')}
            </ul>
        `;

        // Update usage statistics
        const apiUsagePercent = Math.min(100, (usageStats.api_calls_used / usageStats.api_calls_limit) * 100);
        document.getElementById('apiUsageBar').style.width = `${apiUsagePercent}%`;
        document.getElementById('apiUsageText').textContent = `${usageStats.api_calls_used} / ${usageStats.api_calls_limit} calls used`;
        
        const tradesUsagePercent = Math.min(100, (usageStats.trades_this_month / 100) * 100); // Assuming 100 as max
        document.getElementById('tradesUsageBar').style.width = `${tradesUsagePercent}%`;
        document.getElementById('tradesUsageText').textContent = `${usageStats.trades_this_month} trades this month`;

        // Render available plans
        document.getElementById('availablePlans').innerHTML = availablePlans.map(plan => `
            <div class="subscription-plan ${plan.name === currentPlan.name ? 'current' : ''} ${plan.recommended ? 'recommended' : ''}">
                ${plan.recommended ? '<div class="plan-badge recommended">Recommended</div>' : ''}
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h5>${plan.name} Plan</h5>
                        <h4 class="text-primary mb-3">$${plan.price}/month</h4>
                        <ul class="list-unstyled">
                            ${plan.features.map(feature => `<li><i class="fas fa-check text-success me-2"></i>${feature}</li>`).join('')}
                        </ul>
                    </div>
                    <div>
                        ${plan.name !== currentPlan.name ? `
                            <button class="btn btn-primary" onclick="changeSubscription('${plan.name}')">
                                ${plan.price > currentPlan.price ? 'Upgrade' : 'Downgrade'}
                            </button>
                        ` : '<span class="badge bg-success">Current Plan</span>'}
                    </div>
                </div>
            </div>
        `).join('');
    }

    async loadNotificationPreferences() {
        try {
            const response = await fetch('/api/account/notifications');
            const data = await response.json();
            
            if (!data.success) {
                this.showError('Failed to load notification preferences');
                return;
            }

            this.applyNotificationPreferences(data.preferences);

        } catch (error) {
            console.error('Error loading notifications:', error);
            this.showError('Failed to load notification preferences');
        }
    }

    applyNotificationPreferences(preferences) {
        const emailPrefs = preferences.email_notifications || {};
        const pushPrefs = preferences.push_notifications || {};
        const alertFreq = preferences.alert_frequency || {};

        // Set email preferences
        Object.keys(emailPrefs).forEach(key => {
            const element = document.getElementById(`email${key.charAt(0).toUpperCase() + key.slice(1).replace(/_(.)/g, (_, letter) => letter.toUpperCase())}`);
            if (element) element.checked = emailPrefs[key];
        });

        // Set push preferences
        Object.keys(pushPrefs).forEach(key => {
            const element = document.getElementById(`push${key.charAt(0).toUpperCase() + key.slice(1).replace(/_(.)/g, (_, letter) => letter.toUpperCase())}`);
            if (element) element.checked = pushPrefs[key];
        });

        // Set alert frequency
        Object.keys(alertFreq).forEach(key => {
            const element = document.getElementById(key);
            if (element && alertFreq[key]) element.checked = true;
        });
    }

    showError(message) {
        // Create and show error alert
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.tab-content');
        container.insertBefore(alert, container.firstChild);
    }

    showSuccess(message) {
        // Create and show success alert
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.tab-content');
        container.insertBefore(alert, container.firstChild);
    }

    showLoading(show = true) {
        const spinner = document.getElementById('loadingSpinner');
        spinner.style.display = show ? 'block' : 'none';
    }
}

// Global functions for button interactions
async function updateProfile() {
    const accountSettings = window.accountSettings;
    
    const profileData = {
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        email: document.getElementById('email').value
    };

    try {
        accountSettings.showLoading(true);
        const response = await fetch('/api/account/profile', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(profileData)
        });

        const result = await response.json();
        
        if (result.success) {
            accountSettings.showSuccess('Profile updated successfully!');
        } else {
            accountSettings.showError(result.error || 'Failed to update profile');
        }
    } catch (error) {
        console.error('Error updating profile:', error);
        accountSettings.showError('Failed to update profile');
    } finally {
        accountSettings.showLoading(false);
    }
}

async function addPaymentMethod() {
    // In a real implementation, this would integrate with Stripe Elements
    const accountSettings = window.accountSettings;
    accountSettings.showSuccess('Payment method integration coming soon!');
}

async function removePaymentMethod(paymentMethodId) {
    if (!confirm('Are you sure you want to remove this payment method?')) {
        return;
    }

    const accountSettings = window.accountSettings;
    
    try {
        const response = await fetch(`/api/account/payment-methods/${paymentMethodId}`, {
            method: 'DELETE'
        });

        const result = await response.json();
        
        if (result.success) {
            accountSettings.showSuccess('Payment method removed successfully!');
            accountSettings.loadPaymentMethods(); // Reload the list
        } else {
            accountSettings.showError(result.error || 'Failed to remove payment method');
        }
    } catch (error) {
        console.error('Error removing payment method:', error);
        accountSettings.showError('Failed to remove payment method');
    }
}

async function changeSubscription(planName) {
    if (!confirm(`Are you sure you want to change to the ${planName} plan?`)) {
        return;
    }

    const accountSettings = window.accountSettings;
    
    try {
        accountSettings.showLoading(true);
        const response = await fetch('/api/account/subscription', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ plan: planName })
        });

        const result = await response.json();
        
        if (result.success) {
            accountSettings.showSuccess(`Successfully changed to ${planName} plan!`);
            accountSettings.loadSubscriptionDetails(); // Reload subscription details
        } else {
            accountSettings.showError(result.error || 'Failed to change subscription');
        }
    } catch (error) {
        console.error('Error changing subscription:', error);
        accountSettings.showError('Failed to change subscription');
    } finally {
        accountSettings.showLoading(false);
    }
}

async function updateSecuritySettings() {
    const accountSettings = window.accountSettings;
    
    const securityData = {
        two_factor_enabled: document.getElementById('twoFactorAuth').checked,
        login_notifications: document.getElementById('loginNotifications').checked,
        trading_alerts: document.getElementById('tradingAlerts').checked
    };

    try {
        accountSettings.showLoading(true);
        const response = await fetch('/api/account/security', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(securityData)
        });

        const result = await response.json();
        
        if (result.success) {
            accountSettings.showSuccess('Security settings updated successfully!');
        } else {
            accountSettings.showError(result.error || 'Failed to update security settings');
        }
    } catch (error) {
        console.error('Error updating security settings:', error);
        accountSettings.showError('Failed to update security settings');
    } finally {
        accountSettings.showLoading(false);
    }
}

async function updateNotificationPreferences() {
    const accountSettings = window.accountSettings;
    
    const preferences = {
        email_notifications: {
            trade_confirmations: document.getElementById('emailTradeConfirmations').checked,
            market_alerts: document.getElementById('emailMarketAlerts').checked,
            account_updates: document.getElementById('emailAccountUpdates').checked,
            promotional_emails: document.getElementById('emailPromotional').checked,
            weekly_summary: document.getElementById('emailWeeklySummary').checked
        },
        push_notifications: {
            price_alerts: document.getElementById('pushPriceAlerts').checked,
            trade_executions: document.getElementById('pushTradeExecutions').checked,
            market_news: document.getElementById('pushMarketNews').checked,
            account_security: document.getElementById('pushAccountSecurity').checked
        },
        alert_frequency: {
            immediate: document.getElementById('immediate').checked,
            hourly_digest: document.getElementById('hourlyDigest').checked,
            daily_digest: document.getElementById('dailyDigest').checked,
            weekly_digest: document.getElementById('weeklyDigest').checked
        }
    };

    try {
        accountSettings.showLoading(true);
        const response = await fetch('/api/account/notifications', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(preferences)
        });

        const result = await response.json();
        
        if (result.success) {
            accountSettings.showSuccess('Notification preferences updated successfully!');
        } else {
            accountSettings.showError(result.error || 'Failed to update preferences');
        }
    } catch (error) {
        console.error('Error updating notifications:', error);
        accountSettings.showError('Failed to update notification preferences');
    } finally {
        accountSettings.showLoading(false);
    }
}

async function changePassword() {
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    
    if (!currentPassword || !newPassword) {
        window.accountSettings.showError('Please fill in both password fields');
        return;
    }

    if (newPassword.length < 8) {
        window.accountSettings.showError('New password must be at least 8 characters long');
        return;
    }

    // In a real implementation, this would be handled securely
    window.accountSettings.showSuccess('Password change functionality coming soon!');
}

async function deleteAccount() {
    const email = prompt('To confirm account deletion, please enter your email address:');
    
    if (!email) {
        return;
    }

    if (!confirm('This action cannot be undone. Are you absolutely sure you want to delete your account?')) {
        return;
    }

    const accountSettings = window.accountSettings;
    
    try {
        accountSettings.showLoading(true);
        const response = await fetch('/api/account/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                confirmed: true
            })
        });

        const result = await response.json();
        
        if (result.success) {
            alert('Account deletion initiated. You will receive confirmation within 24 hours.');
            // In a real implementation, redirect to logout
        } else {
            accountSettings.showError(result.error || 'Failed to delete account');
        }
    } catch (error) {
        console.error('Error deleting account:', error);
        accountSettings.showError('Failed to delete account');
    } finally {
        accountSettings.showLoading(false);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.accountSettings = new AccountSettings();
});