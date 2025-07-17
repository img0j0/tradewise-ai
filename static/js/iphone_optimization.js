// iPhone-Specific Optimizations

class iPhoneOptimization {
    constructor() {
        this.isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        this.isStandalone = window.navigator.standalone;
        this.viewportHeight = window.innerHeight;
        this.keyboardHeight = 0;
        this.isKeyboardVisible = false;
        
        if (this.isIOS) {
            this.init();
        }
    }
    
    init() {
        this.setupViewportHandling();
        this.setupKeyboardHandling();
        this.setupTouchOptimizations();
        this.setupScrollOptimizations();
        this.setupSafeAreaHandling();
        this.setupStatusBarHandling();
        this.setupOrientationHandling();
        this.setupPerformanceOptimizations();
        this.setupAccessibilityEnhancements();
    }
    
    setupViewportHandling() {
        // Set initial viewport height
        const setViewportHeight = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };
        
        setViewportHeight();
        
        // Handle viewport changes
        window.addEventListener('resize', () => {
            setViewportHeight();
            this.handleViewportChange();
        });
        
        // Handle orientation changes
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                setViewportHeight();
                this.handleOrientationChange();
            }, 100);
        });
    }
    
    setupKeyboardHandling() {
        let initialViewportHeight = window.innerHeight;
        
        // Detect keyboard visibility
        window.addEventListener('resize', () => {
            const currentHeight = window.innerHeight;
            const heightDifference = initialViewportHeight - currentHeight;
            
            if (heightDifference > 150) {
                // Keyboard is likely visible
                this.isKeyboardVisible = true;
                this.keyboardHeight = heightDifference;
                document.body.classList.add('keyboard-visible');
                this.handleKeyboardShow();
            } else {
                // Keyboard is likely hidden
                this.isKeyboardVisible = false;
                this.keyboardHeight = 0;
                document.body.classList.remove('keyboard-visible');
                this.handleKeyboardHide();
            }
        });
        
        // Handle input focus
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                this.handleInputFocus(input);
            });
            
            input.addEventListener('blur', () => {
                this.handleInputBlur(input);
            });
        });
    }
    
    setupTouchOptimizations() {
        // Enhanced touch feedback
        const touchableElements = document.querySelectorAll('button, .btn, .nav-link, .card, .table-responsive tr');
        
        touchableElements.forEach(element => {
            element.addEventListener('touchstart', (e) => {
                this.handleTouchStart(e);
            });
            
            element.addEventListener('touchend', (e) => {
                this.handleTouchEnd(e);
            });
            
            element.addEventListener('touchcancel', (e) => {
                this.handleTouchCancel(e);
            });
        });
        
        // Prevent double-tap zoom
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (e) => {
            const now = new Date().getTime();
            if (now - lastTouchEnd <= 300) {
                e.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
    }
    
    setupScrollOptimizations() {
        // Smooth scrolling for all scrollable elements
        const scrollableElements = document.querySelectorAll('.table-responsive, .ai-messages, .nav-tabs, .modal-body');
        
        scrollableElements.forEach(element => {
            element.style.webkitOverflowScrolling = 'touch';
            element.style.scrollBehavior = 'smooth';
        });
        
        // Prevent body scroll when modal is open
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('shown.bs.modal', () => {
                document.body.style.overflow = 'hidden';
            });
            
            modal.addEventListener('hidden.bs.modal', () => {
                document.body.style.overflow = '';
            });
        });
    }
    
    setupSafeAreaHandling() {
        // Dynamically adjust for safe areas
        const updateSafeAreaProperties = () => {
            const safeAreaTop = getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-top');
            const safeAreaBottom = getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-bottom');
            
            if (safeAreaTop && safeAreaBottom) {
                const navbar = document.querySelector('.navbar');
                const aiAssistant = document.querySelector('.ai-assistant-button');
                
                if (navbar) {
                    navbar.style.paddingTop = `calc(0.5rem + ${safeAreaTop})`;
                }
                
                if (aiAssistant) {
                    aiAssistant.style.bottom = `calc(1rem + ${safeAreaBottom})`;
                }
            }
        };
        
        updateSafeAreaProperties();
        window.addEventListener('resize', updateSafeAreaProperties);
    }
    
    setupStatusBarHandling() {
        // Handle status bar appearance
        if (this.isStandalone) {
            document.body.classList.add('standalone-mode');
            
            // Add padding for standalone mode
            const navbar = document.querySelector('.navbar');
            if (navbar) {
                navbar.style.paddingTop = 'calc(0.5rem + 44px)'; // Default status bar height
            }
        }
    }
    
    setupOrientationHandling() {
        const handleOrientationChange = () => {
            const orientation = window.orientation;
            
            if (orientation === 90 || orientation === -90) {
                // Landscape mode
                document.body.classList.add('landscape-mode');
                document.body.classList.remove('portrait-mode');
            } else {
                // Portrait mode
                document.body.classList.add('portrait-mode');
                document.body.classList.remove('landscape-mode');
            }
        };
        
        handleOrientationChange();
        window.addEventListener('orientationchange', handleOrientationChange);
    }
    
    setupPerformanceOptimizations() {
        // Optimize animations for better performance
        const animatedElements = document.querySelectorAll('.card, .btn, .modal-content');
        
        animatedElements.forEach(element => {
            element.style.willChange = 'transform';
            element.style.transform = 'translateZ(0)';
        });
        
        // Throttle scroll events
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            
            scrollTimeout = setTimeout(() => {
                this.handleScroll();
            }, 16); // ~60fps
        });
    }
    
    setupAccessibilityEnhancements() {
        // Improve accessibility for iOS
        const focusableElements = document.querySelectorAll('button, .btn, input, textarea, select, a[href]');
        
        focusableElements.forEach(element => {
            if (!element.hasAttribute('aria-label') && !element.textContent.trim()) {
                element.setAttribute('aria-label', 'Interactive element');
            }
        });
        
        // Add skip link for keyboard navigation
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.textContent = 'Skip to main content';
        skipLink.className = 'sr-only';
        skipLink.style.position = 'absolute';
        skipLink.style.top = '10px';
        skipLink.style.left = '10px';
        skipLink.style.zIndex = '9999';
        
        document.body.insertBefore(skipLink, document.body.firstChild);
    }
    
    // Event handlers
    handleViewportChange() {
        // Update chart sizes if needed
        const charts = document.querySelectorAll('.chart-container');
        charts.forEach(chart => {
            if (window.Chart) {
                const chartInstance = Chart.getChart(chart);
                if (chartInstance) {
                    chartInstance.resize();
                }
            }
        });
    }
    
    handleOrientationChange() {
        // Adjust UI for orientation change
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            modal.style.transform = 'none';
            setTimeout(() => {
                modal.style.transform = '';
            }, 300);
        });
    }
    
    handleKeyboardShow() {
        // Adjust UI when keyboard is shown
        const activeModal = document.querySelector('.modal.show');
        if (activeModal) {
            activeModal.classList.add('keyboard-visible');
        }
        
        // Scroll active input into view
        const activeInput = document.activeElement;
        if (activeInput && (activeInput.tagName === 'INPUT' || activeInput.tagName === 'TEXTAREA')) {
            setTimeout(() => {
                activeInput.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center' 
                });
            }, 300);
        }
    }
    
    handleKeyboardHide() {
        // Restore UI when keyboard is hidden
        const activeModal = document.querySelector('.modal.show');
        if (activeModal) {
            activeModal.classList.remove('keyboard-visible');
        }
    }
    
    handleInputFocus(input) {
        // Enhance input focus behavior
        input.style.transform = 'scale(1.02)';
        input.style.transition = 'transform 0.2s ease';
        
        // Add focus indicator
        const focusIndicator = document.createElement('div');
        focusIndicator.className = 'focus-indicator';
        focusIndicator.style.position = 'absolute';
        focusIndicator.style.top = '0';
        focusIndicator.style.left = '0';
        focusIndicator.style.right = '0';
        focusIndicator.style.bottom = '0';
        focusIndicator.style.border = '2px solid var(--primary-color)';
        focusIndicator.style.borderRadius = '10px';
        focusIndicator.style.pointerEvents = 'none';
        focusIndicator.style.zIndex = '1';
        
        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(focusIndicator);
    }
    
    handleInputBlur(input) {
        // Remove focus enhancements
        input.style.transform = 'scale(1)';
        
        const focusIndicator = input.parentNode.querySelector('.focus-indicator');
        if (focusIndicator) {
            focusIndicator.remove();
        }
    }
    
    handleTouchStart(e) {
        // Add touch feedback
        const element = e.currentTarget;
        element.style.transform = 'scale(0.98)';
        element.style.transition = 'transform 0.1s ease';
        
        // Add haptic feedback simulation
        if (navigator.vibrate) {
            navigator.vibrate(10);
        }
    }
    
    handleTouchEnd(e) {
        // Remove touch feedback
        const element = e.currentTarget;
        setTimeout(() => {
            element.style.transform = 'scale(1)';
            element.style.transition = 'transform 0.2s ease';
        }, 100);
    }
    
    handleTouchCancel(e) {
        // Handle touch cancellation
        const element = e.currentTarget;
        element.style.transform = 'scale(1)';
        element.style.transition = 'transform 0.2s ease';
    }
    
    handleScroll() {
        // Optimize scroll performance
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Update AI assistant position if needed
        const aiAssistant = document.querySelector('.ai-assistant-button');
        if (aiAssistant && scrollTop > 100) {
            aiAssistant.style.opacity = '0.8';
        } else if (aiAssistant) {
            aiAssistant.style.opacity = '1';
        }
    }
    
    // Utility methods
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.textContent = message;
        toast.style.position = 'fixed';
        toast.style.top = 'calc(1rem + var(--safe-area-inset-top))';
        toast.style.left = '50%';
        toast.style.transform = 'translateX(-50%)';
        toast.style.background = 'rgba(0, 0, 0, 0.8)';
        toast.style.color = 'white';
        toast.style.padding = '1rem 1.5rem';
        toast.style.borderRadius = '12px';
        toast.style.fontSize = '15px';
        toast.style.zIndex = '9999';
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '1';
        }, 100);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }
    
    optimizeImages() {
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            img.style.imageRendering = 'auto';
            img.style.imageRendering = '-webkit-optimize-contrast';
        });
    }
}

// Initialize iPhone optimization when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.iPhoneOptimization = new iPhoneOptimization();
});

// Export for use in other scripts
window.iPhoneOptimization = iPhoneOptimization;