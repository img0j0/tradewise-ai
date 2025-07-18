
// Performance Optimization Script
class PerformanceOptimizer {
    constructor() {
        this.init();
    }
    
    init() {
        this.optimizeImages();
        this.addLazyLoading();
        this.optimizeAnimations();
        this.addCaching();
        this.monitorPerformance();
    }
    
    optimizeImages() {
        // Optimize image loading
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            if (!img.loading) {
                img.loading = 'lazy';
            }
        });
    }
    
    addLazyLoading() {
        // Lazy load non-critical content
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    element.classList.add('loaded');
                    observer.unobserve(element);
                }
            });
        });
        
        const lazyElements = document.querySelectorAll('.lazy-load');
        lazyElements.forEach(element => {
            observer.observe(element);
        });
    }
    
    optimizeAnimations() {
        // Optimize animations for 60fps
        const animatedElements = document.querySelectorAll('.animated');
        animatedElements.forEach(element => {
            element.style.willChange = 'transform, opacity';
        });
    }
    
    addCaching() {
        // Add service worker for caching
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('SW registered:', registration);
                })
                .catch(registrationError => {
                    console.log('SW registration failed:', registrationError);
                });
        }
    }
    
    monitorPerformance() {
        // Monitor performance metrics
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    if (entry.entryType === 'largest-contentful-paint') {
                        console.log('LCP:', entry.startTime);
                    }
                });
            });
            
            observer.observe({ entryTypes: ['largest-contentful-paint'] });
        }
    }
}

// Initialize performance optimizer
document.addEventListener('DOMContentLoaded', () => {
    new PerformanceOptimizer();
});
