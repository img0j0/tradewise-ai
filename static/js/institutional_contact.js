/**
 * Institutional Contact Functions
 * Simple navigation functions for institutional contact features
 */

// Open institutional contact page
function openInstitutionalContact() {
    window.location.href = '/institutional-contact';
}

// Open settings page  
function openSettings() {
    window.location.href = '/settings';
}

// Open subscription plans modal
function openSubscriptionPlans() {
    const modal = document.getElementById('subscription-plans-modal');
    if (modal) {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
}

// Add this to global scope for immediate availability
window.openInstitutionalContact = openInstitutionalContact;
window.openSettings = openSettings;
window.openSubscriptionPlans = openSubscriptionPlans;

console.log('Institutional contact functions loaded successfully');