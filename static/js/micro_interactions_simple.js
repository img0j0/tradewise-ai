/**
 * Simple Micro-interactions for Data Engagement
 * Lightweight implementation without class dependencies
 */

// Initialize micro-interactions when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for the DOM to be fully loaded
    setTimeout(initMicroInteractions, 500);
});

function initMicroInteractions() {
    console.log('Initializing micro-interactions...');
    
    // Card hover effects
    setupCardHoverEffects();
    
    // Button ripple effects
    setupButtonRippleEffects();
    
    // Price animations
    setupPriceAnimations();
    
    // Loading animations
    setupLoadingAnimations();
    
    // Search input effects
    setupSearchEffects();
    
    // Add live data indicators
    addLiveDataIndicators();
    
    console.log('Micro-interactions initialized successfully!');
    
    // Re-run setup every 2 seconds to catch new elements
    setInterval(function() {
        setupCardHoverEffects();
        setupButtonRippleEffects();
        setupSearchEffects();
    }, 2000);
}

// Card hover effects
function setupCardHoverEffects() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        // Remove existing listeners to avoid duplicates
        card.removeEventListener('mouseenter', cardHoverIn);
        card.removeEventListener('mouseleave', cardHoverOut);
        
        // Add new listeners
        card.addEventListener('mouseenter', cardHoverIn);
        card.addEventListener('mouseleave', cardHoverOut);
        
        // Add visual indicator that hover is active
        card.style.cursor = 'pointer';
        card.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    });
}

function cardHoverIn() {
    this.style.transform = 'translateY(-8px) scale(1.02)';
    this.style.boxShadow = '0 20px 40px rgba(0,0,0,0.4)';
    this.style.borderColor = '#007bff';
}

function cardHoverOut() {
    this.style.transform = 'translateY(0) scale(1)';
    this.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    this.style.borderColor = '';
}

// Button ripple effects
function setupButtonRippleEffects() {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        // Remove existing listener to avoid duplicates
        button.removeEventListener('click', buttonClickRipple);
        
        // Add new listener
        button.addEventListener('click', buttonClickRipple);
        
        // Set up button for ripple effects
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.style.transition = 'all 0.2s ease';
        
        // Add hover effect
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
            this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = '';
        });
    });
}

function buttonClickRipple(e) {
    const button = this;
    const ripple = document.createElement('div');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        border-radius: 50%;
        background: rgba(255,255,255,0.4);
        transform: scale(0);
        animation: ripple 0.6s linear;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        pointer-events: none;
        z-index: 1000;
    `;
    
    button.appendChild(ripple);
    
    // Add button press animation
    button.style.transform = 'scale(0.98)';
    setTimeout(() => {
        button.style.transform = 'scale(1)';
    }, 150);
    
    setTimeout(() => {
        if (ripple.parentNode) {
            ripple.remove();
        }
    }, 600);
}

// Price animations with heartbeat effect
function setupPriceAnimations() {
    const priceElements = document.querySelectorAll('[data-price]');
    
    priceElements.forEach(element => {
        // Store original content
        const originalText = element.textContent;
        
        // Add heartbeat animation on hover
        element.addEventListener('mouseenter', function() {
            this.style.animation = 'heartbeat 1s ease-in-out infinite';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.animation = 'none';
        });
        
        // Simulate price updates with color changes
        setInterval(() => {
            const isIncrease = Math.random() > 0.5;
            if (isIncrease) {
                element.style.color = '#28a745';
                element.style.textShadow = '0 0 10px rgba(40, 167, 69, 0.5)';
            } else {
                element.style.color = '#dc3545';
                element.style.textShadow = '0 0 10px rgba(220, 53, 69, 0.5)';
            }
            
            // Reset after animation
            setTimeout(() => {
                element.style.color = '';
                element.style.textShadow = '';
            }, 1000);
        }, 5000 + Math.random() * 10000); // Random interval between 5-15 seconds
    });
}

// Loading animations
function setupLoadingAnimations() {
    const loadingElements = document.querySelectorAll('.data-loading');
    
    loadingElements.forEach(element => {
        element.style.animation = 'shimmer 2s ease-in-out infinite';
    });
}

// Search input effects
function setupSearchEffects() {
    const searchInputs = document.querySelectorAll('input[type="text"], input.form-control');
    
    searchInputs.forEach(input => {
        // Set up transitions
        input.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        
        input.addEventListener('focus', function() {
            this.style.transform = 'scale(1.05)';
            this.style.borderColor = '#007bff';
            this.style.boxShadow = '0 0 0 0.3rem rgba(0,123,255,0.4), 0 8px 16px rgba(0,123,255,0.2)';
            this.style.backgroundColor = '#f8f9fa';
        });
        
        input.addEventListener('blur', function() {
            this.style.transform = 'scale(1)';
            this.style.borderColor = '';
            this.style.boxShadow = '';
            this.style.backgroundColor = '';
        });
        
        // Add typing animation
        input.addEventListener('input', function() {
            this.style.borderColor = '#28a745';
            setTimeout(() => {
                this.style.borderColor = '#007bff';
            }, 300);
        });
    });
}

// Add live data indicators
function addLiveDataIndicators() {
    const indicators = document.querySelectorAll('.live-data-indicator');
    
    indicators.forEach(indicator => {
        indicator.innerHTML = '<div class="pulse-dot"></div>';
        indicator.style.cssText = `
            display: inline-block;
            margin-left: 8px;
        `;
        
        const dot = indicator.querySelector('.pulse-dot');
        if (dot) {
            dot.style.cssText = `
                width: 10px;
                height: 10px;
                background: #28a745;
                border-radius: 50%;
                animation: pulse 1.5s ease-in-out infinite;
                box-shadow: 0 0 8px rgba(40, 167, 69, 0.6);
            `;
        }
    });
}

// Visual feedback for successful interactions
function showSuccessAnimation(element) {
    element.style.animation = 'bounceIn 0.5s ease-out';
    setTimeout(() => {
        element.style.animation = '';
    }, 500);
}

// Add visual feedback to form submissions
function setupFormAnimations() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.style.transform = 'scale(0.95)';
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
                setTimeout(() => {
                    submitBtn.style.transform = 'scale(1)';
                }, 200);
            }
        });
    });
}

// Initialize live data indicators after DOM load
setTimeout(addLiveDataIndicators, 1000);
setTimeout(setupFormAnimations, 1000);