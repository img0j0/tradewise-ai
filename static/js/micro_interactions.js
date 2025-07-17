/**
 * Micro-interactions for Data Engagement
 * Adds smooth animations and visual feedback to enhance user experience
 */

class MicroInteractions {
    constructor() {
        this.init();
    }

    init() {
        this.setupCardInteractions();
        this.setupButtonInteractions();
        this.setupDataAnimations();
        this.setupPriceUpdates();
        this.setupProgressAnimations();
        this.setupNotificationAnimations();
        this.setupSearchInteractions();
        this.setupTabAnimations();
        this.setupModalAnimations();
        this.observeElementsForAnimation();
    }

    // Card hover and click interactions
    setupCardInteractions() {
        document.querySelectorAll('.card').forEach(card => {
            card.classList.add('card-interactive');
            
            card.addEventListener('mouseenter', () => {
                this.addHoverEffect(card);
            });
            
            card.addEventListener('mouseleave', () => {
                this.removeHoverEffect(card);
            });
            
            card.addEventListener('click', () => {
                this.addClickEffect(card);
            });
        });
    }

    // Button interactions with ripple effect
    setupButtonInteractions() {
        document.querySelectorAll('.btn').forEach(btn => {
            btn.classList.add('btn-interactive');
            
            btn.addEventListener('click', (e) => {
                this.createRippleEffect(e);
            });
        });
    }

    // Animate data updates
    setupDataAnimations() {
        this.animateCounters();
        this.animateBadges();
        this.animateAlerts();
    }

    // Price update animations
    setupPriceUpdates() {
        const priceElements = document.querySelectorAll('[data-price]');
        priceElements.forEach(element => {
            element.classList.add('price-update');
            this.observePriceChanges(element);
        });
    }

    // Progress bar animations
    setupProgressAnimations() {
        document.querySelectorAll('.progress').forEach(progress => {
            progress.classList.add('progress-animated');
            this.animateProgressBar(progress);
        });
    }

    // Notification animations
    setupNotificationAnimations() {
        this.observeNotifications();
    }

    // Search input interactions
    setupSearchInteractions() {
        document.querySelectorAll('input[type="search"], input[type="text"]').forEach(input => {
            input.classList.add('search-interactive', 'focus-indicator');
            
            input.addEventListener('focus', () => {
                this.animateSearchFocus(input);
            });
            
            input.addEventListener('blur', () => {
                this.animateSearchBlur(input);
            });
        });
    }

    // Tab switching animations
    setupTabAnimations() {
        document.querySelectorAll('.nav-link').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.animateTabSwitch(e.target);
            });
        });
    }

    // Modal animations
    setupModalAnimations() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.add('modal-animated');
        });
    }

    // Helper methods
    addHoverEffect(element) {
        element.style.transform = 'translateY(-5px)';
        element.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    }

    removeHoverEffect(element) {
        element.style.transform = 'translateY(0)';
    }

    addClickEffect(element) {
        element.style.transform = 'translateY(-2px)';
        setTimeout(() => {
            element.style.transform = 'translateY(-5px)';
        }, 150);
    }

    createRippleEffect(event) {
        const button = event.currentTarget;
        const rect = button.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const ripple = document.createElement('span');
        ripple.style.position = 'absolute';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.style.width = '0';
        ripple.style.height = '0';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(255, 255, 255, 0.3)';
        ripple.style.transform = 'translate(-50%, -50%)';
        ripple.style.animation = 'ripple 0.6s ease-out';

        button.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    animateCounters() {
        document.querySelectorAll('.counter-animated').forEach(counter => {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'childList' || mutation.type === 'characterData') {
                        counter.classList.add('updating');
                        setTimeout(() => {
                            counter.classList.remove('updating');
                        }, 600);
                    }
                });
            });
            
            observer.observe(counter, { childList: true, subtree: true, characterData: true });
        });
    }

    animateBadges() {
        document.querySelectorAll('.badge').forEach(badge => {
            badge.classList.add('badge-animated');
        });
    }

    animateAlerts() {
        document.querySelectorAll('.alert').forEach(alert => {
            alert.classList.add('alert-interactive');
            
            if (alert.textContent.toLowerCase().includes('buy')) {
                alert.classList.add('alert-buy');
            } else if (alert.textContent.toLowerCase().includes('sell')) {
                alert.classList.add('alert-sell');
            }
        });
    }

    observePriceChanges(element) {
        let lastValue = element.textContent;
        
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' || mutation.type === 'characterData') {
                    const currentValue = element.textContent;
                    if (currentValue !== lastValue) {
                        this.animatePriceChange(element, lastValue, currentValue);
                        lastValue = currentValue;
                    }
                }
            });
        });
        
        observer.observe(element, { childList: true, subtree: true, characterData: true });
    }

    animatePriceChange(element, oldValue, newValue) {
        const oldPrice = parseFloat(oldValue.replace(/[^0-9.-]+/g, ''));
        const newPrice = parseFloat(newValue.replace(/[^0-9.-]+/g, ''));
        
        if (newPrice > oldPrice) {
            element.classList.add('price-increase');
            setTimeout(() => element.classList.remove('price-increase'), 600);
        } else if (newPrice < oldPrice) {
            element.classList.add('price-decrease');
            setTimeout(() => element.classList.remove('price-decrease'), 600);
        }
    }

    animateProgressBar(progress) {
        const progressBar = progress.querySelector('.progress-bar');
        if (progressBar) {
            const width = progressBar.style.width || progressBar.getAttribute('style');
            if (width) {
                progressBar.style.width = '0%';
                setTimeout(() => {
                    progressBar.style.width = width.includes('%') ? width : width + '%';
                }, 100);
            }
        }
    }

    observeNotifications() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.classList.contains('alert') || node.classList.contains('notification')) {
                            node.classList.add('notification-slide');
                        }
                    }
                });
            });
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
    }

    animateSearchFocus(input) {
        input.style.transform = 'scale(1.02)';
        input.style.boxShadow = '0 0 20px rgba(0, 123, 255, 0.2)';
    }

    animateSearchBlur(input) {
        input.style.transform = 'scale(1)';
        input.style.boxShadow = 'none';
    }

    animateTabSwitch(tab) {
        const tabContent = document.querySelector('.tab-content');
        if (tabContent) {
            tabContent.classList.add('tab-content-animated');
            setTimeout(() => {
                tabContent.classList.remove('tab-content-animated');
            }, 400);
        }
    }

    // Intersection Observer for scroll animations
    observeElementsForAnimation() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, {
            threshold: 0.1
        });

        // Observe various elements
        document.querySelectorAll('.card, .stock-item, .portfolio-item, .ai-recommendation').forEach(el => {
            observer.observe(el);
        });
    }

    // Live data indicators
    addLiveDataIndicator(element) {
        element.classList.add('live-data-indicator');
    }

    removeLiveDataIndicator(element) {
        element.classList.remove('live-data-indicator');
    }

    // Loading states
    showLoadingState(element) {
        element.classList.add('data-loading');
    }

    hideLoadingState(element) {
        element.classList.remove('data-loading');
    }

    // Stock item animations
    animateStockItems() {
        document.querySelectorAll('.stock-item').forEach((item, index) => {
            item.style.animationDelay = `${index * 0.1}s`;
            item.classList.add('stock-item');
        });
    }

    // Portfolio item animations
    animatePortfolioItems() {
        document.querySelectorAll('.portfolio-item').forEach((item, index) => {
            item.style.animationDelay = `${index * 0.1}s`;
            item.classList.add('portfolio-item');
        });
    }

    // AI recommendation animations
    animateAIRecommendations() {
        document.querySelectorAll('.ai-recommendation').forEach((item, index) => {
            item.style.animationDelay = `${index * 0.2}s`;
            item.classList.add('ai-recommendation');
        });
    }

    // Update animations for real-time data
    updateWithAnimation(element, newContent) {
        element.style.opacity = '0';
        element.style.transform = 'translateY(10px)';
        
        setTimeout(() => {
            element.innerHTML = newContent;
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 150);
    }

    // Notification system
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification-slide`;
        notification.textContent = message;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.minWidth = '300px';
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('removing');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
}

// CSS for ripple effect
const rippleCSS = `
@keyframes ripple {
    0% {
        width: 0;
        height: 0;
        opacity: 1;
    }
    100% {
        width: 100px;
        height: 100px;
        opacity: 0;
    }
}

.animate-in {
    animation: slideInUp 0.6s ease-out;
}
`;

// Add CSS to document
const style = document.createElement('style');
style.textContent = rippleCSS;
document.head.appendChild(style);

// Initialize micro-interactions when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.microInteractions = new MicroInteractions();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MicroInteractions;
}