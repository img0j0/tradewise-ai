/**
 * Modern SaaS Core JavaScript
 * Handles navigation, dark mode, user interactions, and base functionality
 */

const SaaSApp = {
    // Configuration
    config: {
        darkModeKey: 'tradewise-dark-mode',
        searchDebounceMs: 300,
        animationDuration: 200
    },
    
    // State management
    state: {
        darkMode: false,
        userPlan: 'free',
        searchActive: false,
        mobileMenuOpen: false
    },
    
    // Initialize the application
    init() {
        this.initDarkMode();
        this.initNavigation();
        this.initUserMenu();
        this.initMobileMenu();
        this.initKeyboardShortcuts();
        this.initTooltips();
        this.loadUserPlan();
        
        console.log('SaaS App initialized');
    },
    
    // Dark mode functionality
    initDarkMode() {
        const savedMode = localStorage.getItem(this.config.darkModeKey);
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        this.state.darkMode = savedMode ? savedMode === 'true' : prefersDark;
        this.applyDarkMode();
        
        const toggle = document.getElementById('dark-mode-toggle');
        if (toggle) {
            toggle.addEventListener('click', () => this.toggleDarkMode());
        }
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addListener((e) => {
            if (!localStorage.getItem(this.config.darkModeKey)) {
                this.state.darkMode = e.matches;
                this.applyDarkMode();
            }
        });
    },
    
    toggleDarkMode() {
        this.state.darkMode = !this.state.darkMode;
        this.applyDarkMode();
        localStorage.setItem(this.config.darkModeKey, this.state.darkMode.toString());
        
        // Show feedback
        this.showToast(
            `${this.state.darkMode ? 'Dark' : 'Light'} mode enabled`,
            'success'
        );
    },
    
    applyDarkMode() {
        const html = document.documentElement;
        const darkIcon = document.querySelector('.dark-icon');
        const lightIcon = document.querySelector('.light-icon');
        
        if (this.state.darkMode) {
            html.setAttribute('data-theme', 'dark');
            darkIcon?.classList.add('hidden');
            lightIcon?.classList.remove('hidden');
        } else {
            html.setAttribute('data-theme', 'light');
            darkIcon?.classList.remove('hidden');
            lightIcon?.classList.add('hidden');
        }
    },
    
    // Navigation functionality
    initNavigation() {
        // Highlight active navigation links
        const currentPath = window.location.pathname;
        document.querySelectorAll('.navbar-nav-link').forEach(link => {
            const linkPath = new URL(link.href).pathname;
            if (linkPath === currentPath) {
                link.classList.add('active');
            }
        });
        
        // Add navigation tracking
        document.querySelectorAll('.navbar-nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                this.trackNavigation(link.textContent.trim());
            });
        });
    },
    
    // User menu functionality
    initUserMenu() {
        const menuToggle = document.getElementById('user-menu-toggle');
        const dropdown = document.getElementById('user-dropdown');
        
        if (menuToggle && dropdown) {
            menuToggle.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleUserMenu();
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', (e) => {
                if (!menuToggle.contains(e.target) && !dropdown.contains(e.target)) {
                    this.closeUserMenu();
                }
            });
            
            // Close dropdown on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.closeUserMenu();
                }
            });
        }
    },
    
    toggleUserMenu() {
        const dropdown = document.getElementById('user-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('hidden');
        }
    },
    
    closeUserMenu() {
        const dropdown = document.getElementById('user-dropdown');
        if (dropdown) {
            dropdown.classList.add('hidden');
        }
    },
    
    // Mobile menu functionality
    initMobileMenu() {
        const toggle = document.getElementById('mobile-menu-toggle');
        const menu = document.getElementById('mobile-menu');
        
        if (toggle && menu) {
            toggle.addEventListener('click', () => this.toggleMobileMenu());
            
            // Close mobile menu when clicking links
            menu.querySelectorAll('.mobile-nav-link').forEach(link => {
                link.addEventListener('click', () => this.closeMobileMenu());
            });
        }
    },
    
    toggleMobileMenu() {
        const menu = document.getElementById('mobile-menu');
        const toggle = document.getElementById('mobile-menu-toggle');
        
        if (menu && toggle) {
            this.state.mobileMenuOpen = !this.state.mobileMenuOpen;
            
            if (this.state.mobileMenuOpen) {
                menu.classList.remove('hidden');
                toggle.innerHTML = '<i class="fas fa-times"></i>';
                document.body.style.overflow = 'hidden';
            } else {
                menu.classList.add('hidden');
                toggle.innerHTML = '<i class="fas fa-bars"></i>';
                document.body.style.overflow = '';
            }
        }
    },
    
    closeMobileMenu() {
        const menu = document.getElementById('mobile-menu');
        const toggle = document.getElementById('mobile-menu-toggle');
        
        if (menu && toggle) {
            this.state.mobileMenuOpen = false;
            menu.classList.add('hidden');
            toggle.innerHTML = '<i class="fas fa-bars"></i>';
            document.body.style.overflow = '';
        }
    },
    
    // Keyboard shortcuts
    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for search focus
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.focusSearch();
            }
            
            // Ctrl/Cmd + D for dark mode toggle
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                e.preventDefault();
                this.toggleDarkMode();
            }
            
            // Escape to close modals/dropdowns
            if (e.key === 'Escape') {
                this.closeAllOverlays();
            }
        });
    },
    
    focusSearch() {
        const searchInput = document.getElementById('global-search-input') || 
                          document.getElementById('mobile-search-input');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    },
    
    closeAllOverlays() {
        this.closeUserMenu();
        this.closeMobileMenu();
        
        // Close any open modals
        document.querySelectorAll('.modal-overlay:not(.hidden)').forEach(modal => {
            modal.classList.add('hidden');
        });
    },
    
    // Tooltips
    initTooltips() {
        // Create tooltip elements for premium locks
        document.querySelectorAll('.premium-lock').forEach(lock => {
            lock.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target, 'This is a premium feature. Upgrade to unlock.');
            });
            
            lock.addEventListener('mouseleave', (e) => {
                this.hideTooltip(e.target);
            });
        });
    },
    
    showTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'premium-tooltip';
        tooltip.textContent = text;
        element.appendChild(tooltip);
        
        setTimeout(() => {
            tooltip.style.opacity = '1';
        }, 10);
    },
    
    hideTooltip(element) {
        const tooltip = element.querySelector('.premium-tooltip');
        if (tooltip) {
            tooltip.style.opacity = '0';
            setTimeout(() => {
                tooltip.remove();
            }, 200);
        }
    },
    
    // User plan management
    async loadUserPlan() {
        try {
            const response = await fetch('/api/user/plan');
            if (response.ok) {
                const data = await response.json();
                this.updateUserPlan(data.plan || 'free');
            }
        } catch (error) {
            console.warn('Could not load user plan:', error);
        }
    },
    
    updateUserPlan(plan) {
        this.state.userPlan = plan.toLowerCase();
        
        // Update plan badge
        const badge = document.getElementById('plan-badge');
        if (badge) {
            badge.textContent = plan.charAt(0).toUpperCase() + plan.slice(1);
            badge.className = `plan-badge ${plan.toLowerCase()}`;
        }
        
        // Show/hide upgrade button
        const upgradeBtn = document.getElementById('upgrade-btn');
        if (upgradeBtn) {
            upgradeBtn.style.display = plan === 'free' ? 'flex' : 'none';
        }
        
        // Update premium locks
        this.updatePremiumLocks();
    },
    
    updatePremiumLocks() {
        const locks = document.querySelectorAll('.premium-lock');
        locks.forEach(lock => {
            const feature = lock.dataset.feature;
            const isLocked = this.state.userPlan === 'free';
            
            lock.style.display = isLocked ? 'inline-flex' : 'none';
            
            // Add click handlers for upsell
            if (isLocked) {
                lock.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    PremiumSystem.showUpsellModal(feature);
                });
            }
        });
    },
    
    // Toast notifications
    showToast(message, type = 'info', duration = 3000) {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} fade-in`;
        
        const icon = this.getToastIcon(type);
        toast.innerHTML = `
            <div class="toast-content">
                <i class="${icon}"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(toast);
        
        // Auto remove
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.add('fade-out');
                setTimeout(() => toast.remove(), 200);
            }
        }, duration);
    },
    
    getToastIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    },
    
    // Analytics and tracking
    trackNavigation(section) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'navigation', {
                'section': section
            });
        }
    },
    
    trackFeatureClick(feature) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'feature_click', {
                'feature': feature,
                'user_plan': this.state.userPlan
            });
        }
    },
    
    // Utility functions
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },
    
    formatPercentage(value, decimals = 2) {
        return `${(value * 100).toFixed(decimals)}%`;
    },
    
    // Error handling
    handleError(error, context = 'Unknown') {
        console.error(`Error in ${context}:`, error);
        this.showToast('Something went wrong. Please try again.', 'error');
    }
};

// Export for use in other modules
window.SaaSApp = SaaSApp;