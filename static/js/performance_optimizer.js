/**
 * Performance Optimization Manager
 * Handles lazy loading, resource optimization, and performance monitoring
 */

class PerformanceOptimizer {
    constructor() {
        this.observers = {};
        this.loadedResources = new Set();
        this.performanceMetrics = {};
        
        this.init();
    }
    
    init() {
        this.setupLazyLoading();
        this.optimizeImages();
        this.preloadCriticalResources();
        this.setupResourceHints();
        this.initPerformanceMonitoring();
        console.log('Performance Optimizer initialized');
    }
    
    setupLazyLoading() {
        // Intersection Observer for lazy loading
        if ('IntersectionObserver' in window) {
            this.observers.lazy = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.loadLazyElement(entry.target);
                        this.observers.lazy.unobserve(entry.target);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });
            
            // Observe lazy elements
            this.observeLazyElements();
        } else {
            // Fallback for older browsers
            this.loadAllLazyElements();
        }
    }
    
    observeLazyElements() {
        // Charts
        const lazyCharts = document.querySelectorAll('[data-lazy-chart]');
        lazyCharts.forEach(chart => this.observers.lazy.observe(chart));
        
        // Images
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => this.observers.lazy.observe(img));
        
        // Components
        const lazyComponents = document.querySelectorAll('[data-lazy-component]');
        lazyComponents.forEach(component => this.observers.lazy.observe(component));
    }
    
    loadLazyElement(element) {
        if (element.hasAttribute('data-lazy-chart')) {
            this.loadLazyChart(element);
        } else if (element.hasAttribute('data-src')) {
            this.loadLazyImage(element);
        } else if (element.hasAttribute('data-lazy-component')) {
            this.loadLazyComponent(element);
        }
    }
    
    loadLazyChart(chartElement) {
        const chartType = chartElement.dataset.lazyChart;
        const chartId = chartElement.id;
        
        // Show loading skeleton
        chartElement.innerHTML = '<div class="loading-skeleton" style="height: 200px; border-radius: 8px;"></div>';
        
        // Load chart based on type
        switch (chartType) {
            case 'portfolio':
                this.loadPortfolioChart(chartId);
                break;
            case 'market':
                this.loadMarketChart(chartId);
                break;
            case 'performance':
                this.loadPerformanceChart(chartId);
                break;
            default:
                console.warn('Unknown chart type:', chartType);
        }
    }
    
    loadLazyImage(img) {
        const src = img.dataset.src;
        const placeholder = img.dataset.placeholder;
        
        // Create new image for preloading
        const imageLoader = new Image();
        imageLoader.onload = () => {
            img.src = src;
            img.classList.add('loaded');
            img.removeAttribute('data-src');
        };
        imageLoader.onerror = () => {
            if (placeholder) {
                img.src = placeholder;
            }
            img.classList.add('error');
        };
        imageLoader.src = src;
    }
    
    loadLazyComponent(element) {
        const component = element.dataset.lazyComponent;
        const componentPath = element.dataset.componentPath || `/api/components/${component}`;
        
        // Show loading state
        element.innerHTML = '<div class="loading-skeleton" style="height: 100px; border-radius: 8px;"></div>';
        
        // Load component data
        fetch(componentPath)
            .then(response => response.text())
            .then(html => {
                element.innerHTML = html;
                element.classList.add('loaded');
                
                // Initialize any JavaScript in the component
                this.initializeComponentScripts(element);
            })
            .catch(error => {
                console.error('Failed to load component:', component, error);
                element.innerHTML = '<div class="error-state">Failed to load component</div>';
            });
    }
    
    optimizeImages() {
        // Add responsive image attributes
        const images = document.querySelectorAll('img:not([data-optimized])');
        images.forEach(img => {
            // Add loading="lazy" for native lazy loading support
            if ('loading' in HTMLImageElement.prototype) {
                img.loading = 'lazy';
            }
            
            // Add decoding="async" for better performance
            img.decoding = 'async';
            
            // Mark as optimized
            img.setAttribute('data-optimized', 'true');
        });
    }
    
    preloadCriticalResources() {
        const criticalResources = [
            // Critical CSS
            { href: '/static/css/modern_saas_theme.css', as: 'style' },
            { href: '/static/css/desktop_optimization.css', as: 'style' },
            
            // Critical JavaScript
            { href: '/static/js/dark_mode.js', as: 'script' },
            { href: '/static/js/premium_features.js', as: 'script' },
            
            // Critical fonts
            { href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap', as: 'style' }
        ];
        
        criticalResources.forEach(resource => {
            if (!this.loadedResources.has(resource.href)) {
                const link = document.createElement('link');
                link.rel = 'preload';
                link.href = resource.href;
                link.as = resource.as;
                if (resource.as === 'style') {
                    link.onload = () => {
                        link.rel = 'stylesheet';
                    };
                }
                document.head.appendChild(link);
                this.loadedResources.add(resource.href);
            }
        });
    }
    
    setupResourceHints() {
        // DNS prefetch for external resources
        const externalDomains = [
            'fonts.googleapis.com',
            'fonts.gstatic.com',
            'cdn.tailwindcss.com',
            'cdn.jsdelivr.net',
            'cdnjs.cloudflare.com'
        ];
        
        externalDomains.forEach(domain => {
            const link = document.createElement('link');
            link.rel = 'dns-prefetch';
            link.href = `//${domain}`;
            document.head.appendChild(link);
        });
        
        // Preconnect to critical origins
        const criticalOrigins = [
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com'
        ];
        
        criticalOrigins.forEach(origin => {
            const link = document.createElement('link');
            link.rel = 'preconnect';
            link.href = origin;
            link.crossOrigin = 'anonymous';
            document.head.appendChild(link);
        });
    }
    
    initPerformanceMonitoring() {
        // Core Web Vitals monitoring
        if ('web-vital' in window) {
            this.monitorWebVitals();
        }
        
        // Navigation timing
        if ('performance' in window && 'getEntriesByType' in performance) {
            this.monitorNavigationTiming();
        }
        
        // Resource timing
        this.monitorResourceTiming();
        
        // Custom performance markers
        this.setupCustomMarkers();
    }
    
    monitorWebVitals() {
        // This would require the web-vitals library
        // For now, we'll use basic performance API
        if (performance.getEntriesByType) {
            const paintEntries = performance.getEntriesByType('paint');
            paintEntries.forEach(entry => {
                this.performanceMetrics[entry.name] = entry.startTime;
            });
        }
    }
    
    monitorNavigationTiming() {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const navigation = performance.getEntriesByType('navigation')[0];
                if (navigation) {
                    this.performanceMetrics.pageLoadTime = navigation.loadEventEnd - navigation.fetchStart;
                    this.performanceMetrics.domContentLoaded = navigation.domContentLoadedEventEnd - navigation.fetchStart;
                    this.performanceMetrics.timeToInteractive = navigation.domInteractive - navigation.fetchStart;
                    
                    // Report metrics
                    this.reportPerformanceMetrics();
                }
            }, 0);
        });
    }
    
    monitorResourceTiming() {
        // Monitor slow resources
        const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            entries.forEach(entry => {
                if (entry.duration > 1000) { // Resources taking >1s
                    console.warn('Slow resource:', entry.name, `${entry.duration}ms`);
                }
            });
        });
        
        if ('PerformanceObserver' in window) {
            observer.observe({ entryTypes: ['resource'] });
        }
    }
    
    setupCustomMarkers() {
        // Mark critical rendering path completion
        window.addEventListener('DOMContentLoaded', () => {
            performance.mark('critical-path-complete');
        });
        
        // Mark when charts are loaded
        document.addEventListener('chartLoaded', (e) => {
            performance.mark(`chart-${e.detail.chartId}-loaded`);
        });
        
        // Mark when premium features are initialized
        document.addEventListener('premiumFeaturesReady', () => {
            performance.mark('premium-features-ready');
        });
    }
    
    reportPerformanceMetrics() {
        // Send metrics to analytics (if available)
        if (typeof gtag !== 'undefined') {
            gtag('event', 'page_performance', {
                page_load_time: Math.round(this.performanceMetrics.pageLoadTime),
                dom_content_loaded: Math.round(this.performanceMetrics.domContentLoaded),
                time_to_interactive: Math.round(this.performanceMetrics.timeToInteractive)
            });
        }
        
        // Internal performance tracking
        if (window.premiumManager && window.premiumManager.trackEvent) {
            window.premiumManager.trackEvent('performance_metrics', this.performanceMetrics);
        }
        
        console.log('Performance Metrics:', this.performanceMetrics);
    }
    
    // Chart loading methods
    loadPortfolioChart(chartId) {
        fetch('/api/dashboard/portfolio-chart')
            .then(response => response.json())
            .then(data => {
                this.renderChart(chartId, 'doughnut', data);
            })
            .catch(error => {
                console.error('Failed to load portfolio chart:', error);
                document.getElementById(chartId).innerHTML = '<div class="error-state">Failed to load chart</div>';
            });
    }
    
    loadMarketChart(chartId) {
        fetch('/api/dashboard/market-chart')
            .then(response => response.json())
            .then(data => {
                this.renderChart(chartId, 'line', data);
            })
            .catch(error => {
                console.error('Failed to load market chart:', error);
                document.getElementById(chartId).innerHTML = '<div class="error-state">Failed to load chart</div>';
            });
    }
    
    loadPerformanceChart(chartId) {
        fetch('/api/dashboard/performance-chart')
            .then(response => response.json())
            .then(data => {
                this.renderChart(chartId, 'line', data);
            })
            .catch(error => {
                console.error('Failed to load performance chart:', error);
                document.getElementById(chartId).innerHTML = '<div class="error-state">Failed to load chart</div>';
            });
    }
    
    renderChart(canvasId, type, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !window.Chart) {
            console.error('Chart.js not available or canvas not found:', canvasId);
            return;
        }
        
        // Apply dark mode theme
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const config = {
            type: type,
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: isDark ? '#cbd5e1' : '#64748b'
                        }
                    }
                },
                scales: type !== 'doughnut' ? {
                    x: {
                        ticks: { color: isDark ? '#cbd5e1' : '#64748b' },
                        grid: { color: isDark ? '#334155' : '#f1f5f9' }
                    },
                    y: {
                        ticks: { color: isDark ? '#cbd5e1' : '#64748b' },
                        grid: { color: isDark ? '#334155' : '#f1f5f9' }
                    }
                } : {}
            }
        };
        
        new Chart(canvas, config);
        
        // Dispatch chart loaded event
        document.dispatchEvent(new CustomEvent('chartLoaded', {
            detail: { chartId: canvasId }
        }));
    }
    
    initializeComponentScripts(element) {
        // Execute any script tags in the loaded component
        const scripts = element.querySelectorAll('script');
        scripts.forEach(script => {
            const newScript = document.createElement('script');
            newScript.textContent = script.textContent;
            if (script.src) {
                newScript.src = script.src;
            }
            document.body.appendChild(newScript);
        });
    }
    
    // Public API
    loadAllLazyElements() {
        const lazyElements = document.querySelectorAll('[data-lazy-chart], img[data-src], [data-lazy-component]');
        lazyElements.forEach(element => this.loadLazyElement(element));
    }
    
    getPerformanceMetrics() {
        return this.performanceMetrics;
    }
    
    // Utility methods
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
}

// Initialize performance optimizer
function initializePerformanceOptimizer() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createPerformanceOptimizer);
    } else {
        createPerformanceOptimizer();
    }
}

function createPerformanceOptimizer() {
    window.performanceOptimizer = new PerformanceOptimizer();
}

// Initialize on load
initializePerformanceOptimizer();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceOptimizer;
}