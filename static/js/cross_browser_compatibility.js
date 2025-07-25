/**
 * Cross-Browser Compatibility Manager
 * Ensures TradeWise AI works consistently across Chrome, Safari, Edge, and Firefox
 */

class CrossBrowserCompatibility {
    constructor() {
        this.browser = this.detectBrowser();
        this.browserVersion = this.getBrowserVersion();
        this.isSupported = true;
        
        this.init();
    }
    
    init() {
        this.checkBrowserSupport();
        this.applyBrowserSpecificFixes();
        this.setupFeatureDetection();
        this.initializePolyfills();
        console.log(`Cross-browser compatibility initialized for ${this.browser} ${this.browserVersion}`);
    }
    
    detectBrowser() {
        const userAgent = navigator.userAgent.toLowerCase();
        
        if (userAgent.includes('chrome') && !userAgent.includes('edg')) {
            return 'chrome';
        } else if (userAgent.includes('firefox')) {
            return 'firefox';
        } else if (userAgent.includes('safari') && !userAgent.includes('chrome')) {
            return 'safari';
        } else if (userAgent.includes('edg')) {
            return 'edge';
        } else if (userAgent.includes('opera')) {
            return 'opera';
        } else {
            return 'unknown';
        }
    }
    
    getBrowserVersion() {
        const userAgent = navigator.userAgent;
        let version = 'unknown';
        
        try {
            switch (this.browser) {
                case 'chrome':
                    version = userAgent.match(/chrome\/(\d+\.\d+)/i)?.[1] || 'unknown';
                    break;
                case 'firefox':
                    version = userAgent.match(/firefox\/(\d+\.\d+)/i)?.[1] || 'unknown';
                    break;
                case 'safari':
                    version = userAgent.match(/version\/(\d+\.\d+)/i)?.[1] || 'unknown';
                    break;
                case 'edge':
                    version = userAgent.match(/edg\/(\d+\.\d+)/i)?.[1] || 'unknown';
                    break;
            }
        } catch (error) {
            console.log('Could not detect browser version');
        }
        
        return version;
    }
    
    checkBrowserSupport() {
        const minVersions = {
            chrome: 80,
            firefox: 75,
            safari: 13,
            edge: 80
        };
        
        const currentVersion = parseInt(this.browserVersion.split('.')[0]);
        const minVersion = minVersions[this.browser];
        
        if (minVersion && currentVersion < minVersion) {
            this.isSupported = false;
            this.showBrowserWarning();
        }
        
        // Check for critical features
        const criticalFeatures = [
            'fetch',
            'Promise',
            'addEventListener',
            'querySelector'
        ];
        
        criticalFeatures.forEach(feature => {
            if (!(feature in window)) {
                this.isSupported = false;
                console.error(`Critical feature missing: ${feature}`);
            }
        });
    }
    
    applyBrowserSpecificFixes() {
        // Add browser class to body
        document.body.classList.add(`browser-${this.browser}`);
        
        switch (this.browser) {
            case 'safari':
                this.applySafariFixes();
                break;
            case 'firefox':
                this.applyFirefoxFixes();
                break;
            case 'edge':
                this.applyEdgeFixes();
                break;
            case 'chrome':
                this.applyChromeFixes();
                break;
        }
    }
    
    applySafariFixes() {
        // Safari-specific CSS fixes
        const safariStyles = `
            /* Safari backdrop-filter fix */
            .sidebar, .modal, .dropdown-menu {
                -webkit-backdrop-filter: blur(10px);
                backdrop-filter: blur(10px);
            }
            
            /* Safari flexbox fixes */
            .flex {
                display: -webkit-flex;
                display: flex;
            }
            
            /* Safari grid fixes */
            .desktop-grid {
                display: -ms-grid;
                display: grid;
            }
            
            /* Safari transform fixes */
            .sidebar-icon:hover {
                -webkit-transform: scale(1.05);
                transform: scale(1.05);
            }
            
            /* Safari smooth scrolling */
            html {
                -webkit-overflow-scrolling: touch;
            }
            
            /* Safari input appearance fixes */
            input, select, textarea {
                -webkit-appearance: none;
                appearance: none;
            }
        `;
        
        this.injectStyles(safariStyles, 'safari-fixes');
        
        // Safari-specific JavaScript fixes
        this.fixSafariDateInput();
        this.fixSafariScrollBehavior();
    }
    
    applyFirefoxFixes() {
        const firefoxStyles = `
            /* Firefox scrollbar styling */
            * {
                scrollbar-width: thin;
                scrollbar-color: var(--gray-400) var(--gray-100);
            }
            
            /* Firefox flexbox fixes */
            .desktop-grid {
                display: -moz-grid;
                display: grid;
            }
            
            /* Firefox button appearance */
            button {
                -moz-appearance: none;
                appearance: none;
            }
            
            /* Firefox focus outline */
            *:focus-visible {
                outline: 2px solid var(--accent-blue);
                outline-offset: 2px;
            }
        `;
        
        this.injectStyles(firefoxStyles, 'firefox-fixes');
        
        // Firefox-specific fixes
        this.fixFirefoxFlexGap();
    }
    
    applyEdgeFixes() {
        const edgeStyles = `
            /* Edge CSS variable fallbacks */
            .saas-card {
                background: #ffffff;
                background: var(--card-bg, #ffffff);
            }
            
            /* Edge grid fixes */
            .desktop-grid {
                display: -ms-grid;
                display: grid;
            }
            
            /* Edge transform fixes */
            .premium-card:hover {
                -ms-transform: translateY(-2px);
                transform: translateY(-2px);
            }
        `;
        
        this.injectStyles(edgeStyles, 'edge-fixes');
    }
    
    applyChromeFixes() {
        // Chrome generally has good standards support
        // Apply performance optimizations
        const chromeStyles = `
            /* Chrome optimization */
            .saas-card, .sidebar-icon {
                will-change: transform;
                backface-visibility: hidden;
            }
            
            /* Chrome scrollbar styling */
            ::-webkit-scrollbar {
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: var(--gray-100);
            }
            
            ::-webkit-scrollbar-thumb {
                background: var(--gray-400);
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: var(--gray-500);
            }
        `;
        
        this.injectStyles(chromeStyles, 'chrome-fixes');
    }
    
    setupFeatureDetection() {
        // Feature detection and polyfill loading
        const features = {
            // CSS features
            cssGrid: this.supportsCSSGrid(),
            cssFlexbox: this.supportsCSSFlexbox(),
            cssCustomProperties: this.supportsCSSCustomProperties(),
            cssBackdropFilter: this.supportsCSSBackdropFilter(),
            
            // JavaScript features
            intersectionObserver: 'IntersectionObserver' in window,
            webGL: this.supportsWebGL(),
            localStorage: this.supportsLocalStorage(),
            
            // HTML features
            inputTypes: this.getInputTypeSupport()
        };
        
        // Store feature support
        window.featureSupport = features;
        
        // Apply fallbacks for unsupported features
        this.applyFeatureFallbacks(features);
        
        console.log('Feature detection complete:', features);
    }
    
    initializePolyfills() {
        // Load polyfills for missing features
        const polyfills = [];
        
        // Intersection Observer polyfill
        if (!('IntersectionObserver' in window)) {
            polyfills.push(this.loadIntersectionObserverPolyfill());
        }
        
        // CSS Custom Properties polyfill for IE
        if (!this.supportsCSSCustomProperties()) {
            polyfills.push(this.loadCSSCustomPropertiesPolyfill());
        }
        
        // Promise polyfill for older browsers
        if (!('Promise' in window)) {
            polyfills.push(this.loadPromisePolyfill());
        }
        
        // Fetch polyfill for older browsers
        if (!('fetch' in window)) {
            polyfills.push(this.loadFetchPolyfill());
        }
        
        return Promise.all(polyfills);
    }
    
    // Feature detection methods
    supportsCSSGrid() {
        return CSS.supports('display', 'grid');
    }
    
    supportsCSSFlexbox() {
        return CSS.supports('display', 'flex');
    }
    
    supportsCSSCustomProperties() {
        return CSS.supports('--test', 'value');
    }
    
    supportsCSSBackdropFilter() {
        return CSS.supports('backdrop-filter', 'blur(1px)') || 
               CSS.supports('-webkit-backdrop-filter', 'blur(1px)');
    }
    
    supportsWebGL() {
        try {
            const canvas = document.createElement('canvas');
            return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
        } catch (e) {
            return false;
        }
    }
    
    supportsLocalStorage() {
        try {
            const test = 'localStorage-test';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (e) {
            return false;
        }
    }
    
    getInputTypeSupport() {
        const input = document.createElement('input');
        const types = ['date', 'time', 'color', 'range', 'email', 'url'];
        const support = {};
        
        types.forEach(type => {
            input.setAttribute('type', type);
            support[type] = input.type === type;
        });
        
        return support;
    }
    
    // Fallback implementations
    applyFeatureFallbacks(features) {
        if (!features.cssGrid) {
            this.applyGridFallback();
        }
        
        if (!features.cssFlexbox) {
            this.applyFlexboxFallback();
        }
        
        if (!features.cssCustomProperties) {
            this.applyCSSVariableFallback();
        }
        
        if (!features.intersectionObserver) {
            this.applyIntersectionObserverFallback();
        }
    }
    
    applyGridFallback() {
        const fallbackStyles = `
            .desktop-grid {
                display: block;
            }
            
            .desktop-grid > * {
                display: inline-block;
                width: calc(33.333% - 16px);
                margin: 8px;
                vertical-align: top;
            }
            
            @media (max-width: 1023px) {
                .desktop-grid > * {
                    width: calc(50% - 16px);
                }
            }
            
            @media (max-width: 767px) {
                .desktop-grid > * {
                    width: calc(100% - 16px);
                }
            }
        `;
        
        this.injectStyles(fallbackStyles, 'grid-fallback');
    }
    
    applyFlexboxFallback() {
        const fallbackStyles = `
            .flex {
                display: block;
            }
            
            .flex > * {
                display: inline-block;
                vertical-align: top;
            }
            
            .justify-between > *:last-child {
                float: right;
            }
            
            .items-center > * {
                vertical-align: middle;
            }
        `;
        
        this.injectStyles(fallbackStyles, 'flexbox-fallback');
    }
    
    applyCSSVariableFallback() {
        // Basic color fallbacks
        const fallbackStyles = `
            .saas-navbar {
                background: #ffffff;
            }
            
            .saas-card {
                background: #ffffff;
                border: 1px solid #e2e8f0;
            }
            
            .text-primary {
                color: #1e293b;
            }
            
            .text-secondary {
                color: #64748b;
            }
            
            .bg-primary {
                background: #1e40af;
            }
            
            .bg-secondary {
                background: #7c3aed;
            }
        `;
        
        this.injectStyles(fallbackStyles, 'css-variable-fallback');
    }
    
    applyIntersectionObserverFallback() {
        // Simple scroll-based lazy loading
        let lazyElements = [];
        
        function checkLazyElements() {
            lazyElements = lazyElements.filter(element => {
                const rect = element.getBoundingClientRect();
                const inView = rect.top < window.innerHeight && rect.bottom > 0;
                
                if (inView) {
                    // Trigger lazy loading
                    if (window.performanceOptimizer) {
                        window.performanceOptimizer.loadLazyElement(element);
                    }
                    return false; // Remove from array
                }
                
                return true; // Keep in array
            });
        }
        
        // Find all lazy elements
        document.addEventListener('DOMContentLoaded', () => {
            lazyElements = Array.from(document.querySelectorAll('[data-lazy-chart], img[data-src], [data-lazy-component]'));
            checkLazyElements();
        });
        
        // Check on scroll
        window.addEventListener('scroll', this.throttle(checkLazyElements, 100));
        window.addEventListener('resize', this.throttle(checkLazyElements, 100));
    }
    
    // Browser-specific fixes
    fixSafariDateInput() {
        const dateInputs = document.querySelectorAll('input[type="date"]');
        dateInputs.forEach(input => {
            if (input.type !== 'date') {
                // Fallback for Safari that doesn't support date input
                input.type = 'text';
                input.placeholder = 'YYYY-MM-DD';
                input.pattern = '\\d{4}-\\d{2}-\\d{2}';
            }
        });
    }
    
    fixSafariScrollBehavior() {
        // Fix smooth scrolling in Safari
        const scrollElements = document.querySelectorAll('[data-smooth-scroll]');
        scrollElements.forEach(element => {
            element.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(element.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    }
    
    fixFirefoxFlexGap() {
        // Firefox flex gap fallback
        if (!CSS.supports('gap', '1rem')) {
            const flexElements = document.querySelectorAll('.flex, .desktop-grid');
            flexElements.forEach(element => {
                const children = Array.from(element.children);
                children.forEach((child, index) => {
                    if (index > 0) {
                        child.style.marginLeft = '1rem';
                    }
                });
            });
        }
    }
    
    // Polyfill loaders
    loadIntersectionObserverPolyfill() {
        return new Promise((resolve) => {
            const script = document.createElement('script');
            script.src = 'https://polyfill.io/v3/polyfill.min.js?features=IntersectionObserver';
            script.onload = resolve;
            document.head.appendChild(script);
        });
    }
    
    loadCSSCustomPropertiesPolyfill() {
        return new Promise((resolve) => {
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/css-vars-ponyfill@2';
            script.onload = () => {
                if (window.cssVars) {
                    window.cssVars();
                }
                resolve();
            };
            document.head.appendChild(script);
        });
    }
    
    loadPromisePolyfill() {
        return new Promise((resolve) => {
            const script = document.createElement('script');
            script.src = 'https://polyfill.io/v3/polyfill.min.js?features=Promise';
            script.onload = resolve;
            document.head.appendChild(script);
        });
    }
    
    loadFetchPolyfill() {
        return new Promise((resolve) => {
            const script = document.createElement('script');
            script.src = 'https://polyfill.io/v3/polyfill.min.js?features=fetch';
            script.onload = resolve;
            document.head.appendChild(script);
        });
    }
    
    // Utility methods
    injectStyles(css, id) {
        if (document.getElementById(id)) return;
        
        const style = document.createElement('style');
        style.id = id;
        style.textContent = css;
        document.head.appendChild(style);
    }
    
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    showBrowserWarning() {
        const warning = document.createElement('div');
        warning.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; right: 0; background: #fee2e2; border-bottom: 1px solid #fecaca; padding: 12px; text-align: center; z-index: 9999; font-family: system-ui, sans-serif;">
                <p style="margin: 0; color: #991b1b; font-size: 14px;">
                    <strong>Browser Update Recommended:</strong> For the best experience, please update your ${this.browser} browser to the latest version.
                    <button onclick="this.parentElement.parentElement.remove()" style="margin-left: 12px; background: none; border: none; color: #991b1b; text-decoration: underline; cursor: pointer;">Dismiss</button>
                </p>
            </div>
        `;
        
        document.body.insertBefore(warning, document.body.firstChild);
    }
    
    // Public API
    getBrowserInfo() {
        return {
            browser: this.browser,
            version: this.browserVersion,
            isSupported: this.isSupported,
            features: window.featureSupport || {}
        };
    }
    
    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
    
    isTablet() {
        return /iPad|Android(?=.*Mobile)/i.test(navigator.userAgent);
    }
    
    getViewportSize() {
        return {
            width: window.innerWidth || document.documentElement.clientWidth,
            height: window.innerHeight || document.documentElement.clientHeight
        };
    }
}

// Initialize cross-browser compatibility
function initializeCrossBrowserCompatibility() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createCrossBrowserCompatibility);
    } else {
        createCrossBrowserCompatibility();
    }
}

function createCrossBrowserCompatibility() {
    window.crossBrowserCompatibility = new CrossBrowserCompatibility();
}

// Initialize on load
initializeCrossBrowserCompatibility();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CrossBrowserCompatibility;
}