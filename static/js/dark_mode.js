/**
 * Enhanced Dark Mode Manager
 * Cross-browser compatible dark mode with localStorage persistence
 */

class DarkModeManager {
    constructor() {
        this.themeKey = 'tradewise-theme';
        this.toggleButton = null;
        this.themeIcon = null;
        this.currentTheme = 'light';
        
        this.init();
    }
    
    init() {
        this.loadSavedTheme();
        this.setupToggleButton();
        this.applyTheme(this.currentTheme);
        this.bindEvents();
        console.log('Dark Mode Manager initialized');
    }
    
    loadSavedTheme() {
        try {
            const savedTheme = localStorage.getItem(this.themeKey);
            
            // Check system preference if no saved theme
            if (!savedTheme) {
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                this.currentTheme = prefersDark ? 'dark' : 'light';
            } else {
                this.currentTheme = savedTheme;
            }
        } catch (error) {
            console.log('localStorage not available, using light theme');
            this.currentTheme = 'light';
        }
    }
    
    setupToggleButton() {
        this.toggleButton = document.getElementById('theme-toggle');
        this.themeIcon = document.getElementById('theme-icon');
        
        if (!this.toggleButton || !this.themeIcon) {
            console.log('Theme toggle elements not found');
            return;
        }
        
        // Update icon based on current theme
        this.updateIcon();
    }
    
    applyTheme(theme) {
        const html = document.documentElement;
        const body = document.body;
        
        // Set data-theme attribute
        html.setAttribute('data-theme', theme);
        
        // Update class-based theme support
        if (theme === 'dark') {
            html.classList.add('dark');
            body.classList.add('dark');
        } else {
            html.classList.remove('dark');
            body.classList.remove('dark');
        }
        
        // Update CSS variables for charts and dynamic content
        this.updateChartThemes(theme);
        
        // Dispatch theme change event
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme } 
        }));
    }
    
    updateIcon() {
        if (!this.themeIcon) return;
        
        if (this.currentTheme === 'dark') {
            this.themeIcon.className = 'fas fa-sun';
            this.toggleButton.title = 'Switch to Light Mode';
        } else {
            this.themeIcon.className = 'fas fa-moon';
            this.toggleButton.title = 'Switch to Dark Mode';
        }
    }
    
    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
        
        // Track theme change
        this.trackThemeChange(newTheme);
    }
    
    setTheme(theme) {
        this.currentTheme = theme;
        this.applyTheme(theme);
        this.updateIcon();
        this.saveTheme(theme);
    }
    
    saveTheme(theme) {
        try {
            localStorage.setItem(this.themeKey, theme);
        } catch (error) {
            console.log('Could not save theme preference');
        }
    }
    
    updateChartThemes(theme) {
        // Update Chart.js themes if available
        if (window.Chart) {
            const isDark = theme === 'dark';
            Chart.defaults.color = isDark ? '#cbd5e1' : '#64748b';
            Chart.defaults.borderColor = isDark ? '#334155' : '#e2e8f0';
            Chart.defaults.backgroundColor = isDark ? '#1e293b' : '#ffffff';
            
            // Redraw existing charts
            Object.values(Chart.instances).forEach(chart => {
                if (chart && chart.update) {
                    chart.update('none');
                }
            });
        }
        
        // Update any custom chart libraries
        this.updateCustomCharts(theme);
    }
    
    updateCustomCharts(theme) {
        // Hook for updating custom chart libraries
        const chartContainers = document.querySelectorAll('.chart-container');
        chartContainers.forEach(container => {
            if (theme === 'dark') {
                container.style.backgroundColor = 'var(--card-bg)';
                container.style.borderColor = 'var(--card-border)';
            } else {
                container.style.backgroundColor = 'var(--card-bg)';
                container.style.borderColor = 'var(--card-border)';
            }
        });
    }
    
    bindEvents() {
        // Toggle button click
        if (this.toggleButton) {
            this.toggleButton.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
        
        // Keyboard shortcut (Ctrl/Cmd + D)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                e.preventDefault();
                this.toggleTheme();
            }
        });
        
        // System theme change detection
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addListener((e) => {
                // Only auto-switch if user hasn't manually set a preference
                if (!localStorage.getItem(this.themeKey)) {
                    this.setTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
        
        // Listen for theme changes from other components
        window.addEventListener('setTheme', (e) => {
            this.setTheme(e.detail.theme);
        });
    }
    
    trackThemeChange(theme) {
        // Analytics tracking
        if (typeof gtag !== 'undefined') {
            gtag('event', 'theme_changed', {
                theme: theme,
                source: 'manual_toggle'
            });
        }
        
        // Internal analytics
        if (window.premiumManager && window.premiumManager.trackEvent) {
            window.premiumManager.trackEvent('theme_changed', { theme });
        }
    }
    
    // Public API
    getCurrentTheme() {
        return this.currentTheme;
    }
    
    isDark() {
        return this.currentTheme === 'dark';
    }
    
    isLight() {
        return this.currentTheme === 'light';
    }
    
    // Force theme update (useful for testing)
    forceUpdate() {
        this.applyTheme(this.currentTheme);
        this.updateIcon();
    }
}

// Cross-browser support functions
function initializeDarkMode() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createDarkModeManager);
    } else {
        createDarkModeManager();
    }
}

function createDarkModeManager() {
    // Create global instance
    window.darkModeManager = new DarkModeManager();
    
    // Expose theme utilities globally
    window.setTheme = (theme) => {
        window.darkModeManager.setTheme(theme);
    };
    
    window.toggleTheme = () => {
        window.darkModeManager.toggleTheme();
    };
    
    window.getCurrentTheme = () => {
        return window.darkModeManager.getCurrentTheme();
    };
}

// Browser compatibility polyfills
if (!window.matchMedia) {
    window.matchMedia = function() {
        return {
            matches: false,
            addListener: function() {},
            removeListener: function() {}
        };
    };
}

if (!window.CustomEvent) {
    window.CustomEvent = function(event, params) {
        params = params || { bubbles: false, cancelable: false, detail: null };
        var evt = document.createEvent('CustomEvent');
        evt.initCustomEvent(event, params.bubbles, params.cancelable, params.detail);
        return evt;
    };
}

// Initialize dark mode
initializeDarkMode();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DarkModeManager;
}