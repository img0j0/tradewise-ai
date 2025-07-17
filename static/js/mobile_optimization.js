// Mobile-First Responsive Design Optimization
if (!window.MobileOptimization) {
    window.MobileOptimization = class {
    constructor() {
        this.isMobile = window.innerWidth <= 768;
        this.isTablet = window.innerWidth > 768 && window.innerWidth <= 1024;
        this.touchSupport = 'ontouchstart' in window;
        this.initialize();
    }

    initialize() {
        this.setupViewportHandling();
        this.setupTouchOptimizations();
        this.setupResponsiveCharts();
        this.setupMobileNavigation();
        this.setupGestureHandling();
        this.optimizeScrolling();
        this.setupKeyboardHandling();
    }

    setupViewportHandling() {
        // Dynamic viewport height handling for mobile browsers
        const setViewportHeight = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };

        setViewportHeight();
        window.addEventListener('resize', setViewportHeight);
        window.addEventListener('orientationchange', () => {
            setTimeout(setViewportHeight, 100);
        });
    }

    setupTouchOptimizations() {
        if (!this.touchSupport) return;

        // Enhanced touch targets
        const buttons = document.querySelectorAll('button, .btn, .nav-link');
        buttons.forEach(btn => {
            btn.style.minHeight = '44px';
            btn.style.minWidth = '44px';
        });

        // Touch feedback
        document.addEventListener('touchstart', (e) => {
            if (e.target.matches('button, .btn, .card, .nav-link')) {
                e.target.style.transform = 'scale(0.98)';
                e.target.style.transition = 'transform 0.1s ease';
            }
        });

        document.addEventListener('touchend', (e) => {
            if (e.target.matches('button, .btn, .card, .nav-link')) {
                setTimeout(() => {
                    e.target.style.transform = 'scale(1)';
                }, 100);
            }
        });
    }

    setupResponsiveCharts() {
        // Chart container responsive behavior
        const chartContainers = document.querySelectorAll('.chart-container');
        chartContainers.forEach(container => {
            if (this.isMobile) {
                container.style.height = '250px';
            } else if (this.isTablet) {
                container.style.height = '300px';
            }
        });

        // Chart legend optimization for mobile
        if (window.Chart && this.isMobile) {
            Chart.defaults.plugins.legend.display = false;
            Chart.defaults.plugins.legend.position = 'bottom';
        }
    }

    setupMobileNavigation() {
        const navTabs = document.querySelectorAll('.nav-tabs .nav-link');
        
        if (this.isMobile) {
            // Create horizontal scrollable nav for mobile
            const navContainer = document.querySelector('.nav-tabs');
            if (navContainer) {
                navContainer.style.display = 'flex';
                navContainer.style.overflowX = 'auto';
                navContainer.style.scrollbarWidth = 'none';
                navContainer.style.msOverflowStyle = 'none';
                navContainer.style.webkitScrollbar = 'none';
                
                navTabs.forEach(tab => {
                    tab.style.whiteSpace = 'nowrap';
                    tab.style.flexShrink = '0';
                });
            }
        }

        // Tab switching optimization
        navTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                if (this.isMobile) {
                    // Smooth scroll to active tab
                    setTimeout(() => {
                        tab.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'nearest',
                            inline: 'center' 
                        });
                    }, 100);
                }
            });
        });
    }

    setupGestureHandling() {
        if (!this.touchSupport) return;

        let startX, startY, currentX, currentY;
        let isScrolling = false;

        // Swipe gestures for tab navigation
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            isScrolling = false;
        });

        document.addEventListener('touchmove', (e) => {
            if (!startX || !startY) return;

            currentX = e.touches[0].clientX;
            currentY = e.touches[0].clientY;

            const diffX = Math.abs(currentX - startX);
            const diffY = Math.abs(currentY - startY);

            if (diffY > diffX) {
                isScrolling = true;
            }
        });

        document.addEventListener('touchend', (e) => {
            if (!startX || !startY || isScrolling) return;

            const diffX = currentX - startX;
            const threshold = 50;

            if (Math.abs(diffX) > threshold) {
                const activeTab = document.querySelector('.nav-tabs .nav-link.active');
                if (activeTab) {
                    const tabs = Array.from(document.querySelectorAll('.nav-tabs .nav-link'));
                    const currentIndex = tabs.indexOf(activeTab);
                    
                    if (diffX > 0 && currentIndex > 0) {
                        // Swipe right - previous tab
                        tabs[currentIndex - 1].click();
                    } else if (diffX < 0 && currentIndex < tabs.length - 1) {
                        // Swipe left - next tab
                        tabs[currentIndex + 1].click();
                    }
                }
            }

            startX = startY = currentX = currentY = null;
        });
    }

    optimizeScrolling() {
        // Smooth scrolling for mobile
        if (this.isMobile) {
            document.documentElement.style.scrollBehavior = 'smooth';
            
            // Virtual scrolling for large lists
            const stockLists = document.querySelectorAll('.stock-list, .portfolio-list');
            stockLists.forEach(list => {
                if (list.children.length > 20) {
                    list.style.height = '300px';
                    list.style.overflowY = 'auto';
                }
            });
        }
    }

    setupKeyboardHandling() {
        // Handle virtual keyboard on mobile
        if (this.isMobile) {
            const inputs = document.querySelectorAll('input, textarea');
            
            inputs.forEach(input => {
                input.addEventListener('focus', () => {
                    // Scroll input into view when keyboard appears
                    setTimeout(() => {
                        input.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'center' 
                        });
                    }, 300);
                });
            });
        }
    }

    // Utility methods
    adaptLayoutForScreen() {
        const cards = document.querySelectorAll('.card');
        
        if (this.isMobile) {
            cards.forEach(card => {
                card.style.marginBottom = '1rem';
                card.style.borderRadius = '8px';
            });
        }
    }

    optimizePerformance() {
        // Lazy loading for images
        const images = document.querySelectorAll('img[data-src]');
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        }

        // Reduce animations on mobile for better performance
        if (this.isMobile) {
            const styleSheet = document.createElement('style');
            styleSheet.textContent = `
                @media (max-width: 768px) {
                    *, *::before, *::after {
                        animation-duration: 0.01ms !important;
                        animation-iteration-count: 1 !important;
                        transition-duration: 0.01ms !important;
                    }
                }
            `;
            document.head.appendChild(styleSheet);
        }
    }
}

// Initialize mobile optimization
document.addEventListener('DOMContentLoaded', () => {
    if (!window.mobileOptimization) {
        window.mobileOptimization = new MobileOptimization();
    }
});

// Export for use in other modules
if (!window.MobileOptimization) {
    window.MobileOptimization = MobileOptimization;
}