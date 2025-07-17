/**
 * Simple Micro-interactions for Data Engagement
 * Lightweight implementation without class dependencies
 */

// Initialize micro-interactions when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initMicroInteractions();
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
    
    console.log('Micro-interactions initialized successfully!');
}

// Card hover effects
function setupCardHoverEffects() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.3)';
            this.style.transition = 'all 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
            this.style.transition = 'all 0.3s ease';
        });
    });
}

// Button ripple effects
function setupButtonRippleEffects() {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('div');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255,255,255,0.3);
                transform: scale(0);
                animation: ripple 0.6s linear;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
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
    const searchInputs = document.querySelectorAll('input[type="text"]');
    
    searchInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.transform = 'scale(1.02)';
            this.style.borderColor = '#007bff';
            this.style.boxShadow = '0 0 0 0.2rem rgba(0,123,255,0.25)';
            this.style.transition = 'all 0.3s ease';
        });
        
        input.addEventListener('blur', function() {
            this.style.transform = 'scale(1)';
            this.style.borderColor = '';
            this.style.boxShadow = '';
            this.style.transition = 'all 0.3s ease';
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
                width: 8px;
                height: 8px;
                background: #28a745;
                border-radius: 50%;
                animation: pulse 2s ease-in-out infinite;
            `;
        }
    });
}

// Initialize live data indicators after DOM load
setTimeout(addLiveDataIndicators, 1000);