/**
 * Mobile Optimization for TradeWise AI
 * Ensures optimal performance and UX on mobile devices
 */

class MobileOptimization {
    constructor() {
        this.isMobile = this.detectMobile();
        this.init();
    }

    detectMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || 
               window.innerWidth <= 768;
    }

    init() {
        this.setupViewportMeta();
        this.optimizePerformance();
    }

    setupViewportMeta() {
        // Ensure proper viewport meta tag
        let viewport = document.querySelector('meta[name="viewport"]');
        if (!viewport) {
            viewport = document.createElement('meta');
            viewport.name = 'viewport';
            document.head.appendChild(viewport);
        }
        viewport.content = 'width=device-width, initial-scale=1.0, user-scalable=no';
    }

    optimizePerformance() {
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
    if (typeof window !== 'undefined' && !window.mobileOptimization) {
        window.mobileOptimization = new MobileOptimization();
    }
});

// Export for use in other modules
if (typeof window !== 'undefined' && !window.MobileOptimization) {
    window.MobileOptimization = MobileOptimization;
}