
// Accessibility Enhancement Script
class AccessibilityOptimizer {
    constructor() {
        this.init();
    }
    
    init() {
        this.addAriaLabels();
        this.addKeyboardNavigation();
        this.addFocusManagement();
        this.addScreenReaderSupport();
        this.addReducedMotionSupport();
    }
    
    addAriaLabels() {
        // Add ARIA labels to interactive elements
        const searchInput = document.getElementById('main-search-input');
        if (searchInput) {
            searchInput.setAttribute('aria-label', 'Search stocks by symbol or company name');
            searchInput.setAttribute('role', 'searchbox');
        }
        
        // Add ARIA labels to buttons
        const buttons = document.querySelectorAll('button, .action-btn');
        buttons.forEach(button => {
            if (!button.getAttribute('aria-label')) {
                const text = button.textContent.trim();
                if (text) {
                    button.setAttribute('aria-label', text);
                }
            }
        });
    }
    
    addKeyboardNavigation() {
        // Enhanced keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
            
            // Global search shortcut
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.getElementById('main-search-input');
                if (searchInput) {
                    searchInput.focus();
                }
            }
        });
        
        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
    }
    
    addFocusManagement() {
        // Improved focus management
        const focusableElements = [
            'button', 'input', 'select', 'textarea', 'a[href]',
            '[tabindex]:not([tabindex="-1"])'
        ];
        
        focusableElements.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                element.addEventListener('focus', (e) => {
                    e.target.classList.add('focused');
                });
                
                element.addEventListener('blur', (e) => {
                    e.target.classList.remove('focused');
                });
            });
        });
    }
    
    addScreenReaderSupport() {
        // Add screen reader support
        const announcements = document.createElement('div');
        announcements.setAttribute('aria-live', 'polite');
        announcements.setAttribute('aria-atomic', 'true');
        announcements.className = 'sr-only';
        document.body.appendChild(announcements);
        
        window.announceToScreenReader = (message) => {
            announcements.textContent = message;
            setTimeout(() => {
                announcements.textContent = '';
            }, 1000);
        };
    }
    
    addReducedMotionSupport() {
        // Respect reduced motion preferences
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        
        if (prefersReducedMotion.matches) {
            document.body.classList.add('reduced-motion');
        }
        
        prefersReducedMotion.addEventListener('change', (e) => {
            if (e.matches) {
                document.body.classList.add('reduced-motion');
            } else {
                document.body.classList.remove('reduced-motion');
            }
        });
    }
}

// Initialize accessibility optimizer
document.addEventListener('DOMContentLoaded', () => {
    new AccessibilityOptimizer();
});
