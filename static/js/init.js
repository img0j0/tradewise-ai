// Initialize all trading platform modules
document.addEventListener('DOMContentLoaded', function() {
    // Initialize core modules only once
    if (!window.tradingPlatformInitialized) {
        // Initialize notification manager
        if (!window.notificationManager) {
            window.notificationManager = new NotificationManager();
        }
        
        // Initialize analytics
        if (!window.analyticsManager) {
            window.analyticsManager = new AnalyticsManager();
        }
        
        // Initialize mobile optimization
        if (!window.mobileOptimization && typeof MobileOptimization !== 'undefined') {
            window.mobileOptimization = new MobileOptimization();
        }
        
        // Initialize micro-interactions
        if (!window.microInteractions && typeof MicroInteractions !== 'undefined') {
            window.microInteractions = new MicroInteractions();
        }
        
        // Initialize advanced chart
        if (!window.advancedChart) {
            window.advancedChart = new AdvancedChart();
        }
        
        // Initialize realtime updates
        if (!window.realtimeUpdates) {
            window.realtimeUpdates = new RealtimeUpdates();
        }
        
        // Initialize portfolio analytics
        if (!window.portfolioAnalytics) {
            window.portfolioAnalytics = new PortfolioAnalytics();
        }
        
        // Mark as initialized
        window.tradingPlatformInitialized = true;
        
        console.log('Trading platform initialized successfully');
    }
});

// Global helper functions
function showAdvancedChart(symbol) {
    if (window.advancedChart) {
        window.advancedChart.showChart(symbol);
    }
}

function showBuyModal(symbol) {
    const modal = document.getElementById('buy-modal');
    if (modal) {
        document.getElementById('buy-symbol').value = symbol;
        new bootstrap.Modal(modal).show();
    }
}

function showSellModal(symbol) {
    const modal = document.getElementById('sell-modal');
    if (modal) {
        document.getElementById('sell-symbol').value = symbol;
        new bootstrap.Modal(modal).show();
    }
}

function showTradeModal(symbol) {
    showBuyModal(symbol);
}