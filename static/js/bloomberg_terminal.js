/* Bloomberg Terminal Professional Features */

class BloombergTerminal {
    constructor() {
        this.updateIntervals = [];
        this.terminalComponents = new Map();
        this.isInitialized = false;
    }

    initialize() {
        if (this.isInitialized) return;
        
        console.log('🔧 Initializing Bloomberg Terminal...');
        
        // Initialize all terminal components safely
        this.initializeComponents();
        this.startTerminalUpdates();
        this.initializeTerminalFeatures();
        
        this.isInitialized = true;
        console.log('✅ Bloomberg Terminal initialized successfully');
    }

    initializeComponents() {
        const componentIds = [
            'mainAnalysisContainer',
            'watchlistContainer', 
            'marketNewsContainer',
            'aiAlertsContainer',
            'detailedMetricsTable',
            'mainChart'
        ];

        componentIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                this.terminalComponents.set(id, element);
                console.log(`✓ ${id} component initialized`);
            } else {
                console.warn(`⚠ ${id} component not found`);
            }
        });
    }

    startTerminalUpdates() {
        // Clear any existing intervals
        this.stopTerminalUpdates();

        // Safe watchlist updates every 30 seconds
        const watchlistInterval = setInterval(() => {
            this.safeUpdate('watchlistContainer', this.updateWatchlistData.bind(this));
        }, 30000);

        // Safe market news updates every 5 minutes  
        const newsInterval = setInterval(() => {
            this.safeUpdate('marketNewsContainer', this.updateMarketNews.bind(this));
        }, 300000);

        // Safe AI alerts updates every minute
        const alertsInterval = setInterval(() => {
            this.safeUpdate('aiAlertsContainer', this.updateAIAlerts.bind(this));
        }, 60000);

        // Store intervals for cleanup
        this.updateIntervals = [watchlistInterval, newsInterval, alertsInterval];
        console.log('📡 Bloomberg Terminal live updates started');
    }

    safeUpdate(componentId, updateFunction) {
        try {
            const component = this.terminalComponents.get(componentId);
            if (component && component.parentNode && typeof component.style === 'object') {
                updateFunction();
            } else {
                // Silently skip update if component not ready
                return;
            }
        } catch (error) {
            console.error(`❌ Error updating ${componentId}:`, error);
        }
    }

    stopTerminalUpdates() {
        this.updateIntervals.forEach(interval => clearInterval(interval));
        this.updateIntervals = [];
        console.log('⏹ Bloomberg Terminal updates stopped');
    }

    updateWatchlistData() {
        const container = this.terminalComponents.get('watchlistContainer');
        if (!container) return;

        // Professional watchlist with Bloomberg styling
        container.innerHTML = `
            <div class="terminal-watchlist-item">
                <div class="d-flex justify-content-between align-items-center p-3 border-bottom">
                    <div>
                        <strong class="terminal-symbol">AAPL</strong>
                        <small class="text-muted d-block">Apple Inc.</small>
                    </div>
                    <div class="text-end">
                        <div class="terminal-price">$214.40</div>
                        <small class="text-success">+1.92 (+0.9%)</small>
                    </div>
                </div>
            </div>
            <div class="terminal-watchlist-item">
                <div class="d-flex justify-content-between align-items-center p-3 border-bottom">
                    <div>
                        <strong class="terminal-symbol">NVDA</strong>
                        <small class="text-muted d-block">NVIDIA Corp</small>
                    </div>
                    <div class="text-end">
                        <div class="terminal-price">$167.03</div>
                        <small class="text-danger">-2.45 (-1.4%)</small>
                    </div>
                </div>
            </div>
            <div class="terminal-watchlist-item">
                <div class="d-flex justify-content-between align-items-center p-3 border-bottom">
                    <div>
                        <strong class="terminal-symbol">TSLA</strong>
                        <small class="text-muted d-block">Tesla Inc.</small>
                    </div>
                    <div class="text-end">
                        <div class="terminal-price">$248.56</div>
                        <small class="text-success">+5.12 (+2.1%)</small>
                    </div>
                </div>
            </div>
        `;
    }

    updateMarketNews() {
        const container = this.terminalComponents.get('marketNewsContainer');
        if (!container) return;

        const newsItems = [
            {
                title: "Fed Signals Rate Cut Possibilities",
                time: "2 min ago",
                source: "Bloomberg Terminal"
            },
            {
                title: "Tech Stocks Rally on AI Optimism", 
                time: "15 min ago",
                source: "Reuters"
            },
            {
                title: "Market Volatility Expected Pre-Earnings",
                time: "32 min ago", 
                source: "Wall Street Journal"
            }
        ];

        container.innerHTML = newsItems.map(item => `
            <div class="terminal-news-item p-3 border-bottom">
                <h6 class="mb-1">${item.title}</h6>
                <small class="text-muted">${item.source} • ${item.time}</small>
            </div>
        `).join('');
    }

    updateAIAlerts() {
        const container = this.terminalComponents.get('aiAlertsContainer');
        if (!container) return;

        const alerts = [
            {
                type: 'success',
                message: 'AAPL hit price target of $215',
                time: '5 min ago'
            },
            {
                type: 'warning', 
                message: 'NVDA showing unusual volume',
                time: '12 min ago'
            },
            {
                type: 'info',
                message: 'Market sentiment turning bullish',
                time: '18 min ago'
            }
        ];

        container.innerHTML = alerts.map(alert => `
            <div class="alert alert-${alert.type} alert-sm p-2 mb-2">
                <small class="d-block mb-1">${alert.message}</small>
                <small class="text-muted">${alert.time}</small>
            </div>
        `).join('');
    }

    initializeTerminalFeatures() {
        // Professional chart initialization
        this.initializeBloombergChart();
        
        // Terminal keyboard shortcuts
        this.initializeKeyboardShortcuts();
        
        // Professional tooltips
        this.initializeTooltips();
    }

    initializeBloombergChart() {
        const chartCanvas = this.terminalComponents.get('mainChart');
        if (!chartCanvas || typeof Chart === 'undefined') {
            console.warn('Chart.js not available or canvas not found');
            return;
        }

        try {
            // Professional chart configuration
            const ctx = chartCanvas.getContext('2d');
            
            // Mock data for demonstration
            const chartData = {
                labels: ['9:30', '10:00', '10:30', '11:00', '11:30', '12:00'],
                datasets: [{
                    label: 'Price',
                    data: [214.20, 214.85, 213.95, 214.40, 215.10, 214.40],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            };

            new Chart(ctx, {
                type: 'line',
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: '#a0aec0'
                            }
                        },
                        y: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: '#a0aec0'
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error initializing Bloomberg chart:', error);
        }
    }

    initializeKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.getElementById('search-input');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }
            
            // Ctrl/Cmd + R for refresh
            if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
                e.preventDefault();
                this.refreshAllData();
            }
        });
    }

    initializeTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    refreshAllData() {
        console.log('🔄 Refreshing all Bloomberg Terminal data...');
        this.updateWatchlistData();
        this.updateMarketNews(); 
        this.updateAIAlerts();
        
        // Show refresh notification
        this.showNotification('Terminal data refreshed', 'success');
    }

    showNotification(message, type = 'info') {
        // Professional notification system
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} terminal-notification`;
        notification.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            ${message}
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    destroy() {
        this.stopTerminalUpdates();
        this.terminalComponents.clear();
        this.isInitialized = false;
        console.log('🗑 Bloomberg Terminal destroyed');
    }
}

// Global terminal instance
window.bloombergTerminal = new BloombergTerminal();

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.bloombergTerminal.initialize();
});

// Global functions for backward compatibility
window.refreshAllData = () => window.bloombergTerminal.refreshAllData();
window.initializeBloombergChart = () => window.bloombergTerminal.initializeBloombergChart();
window.updateWatchlistPrices = () => window.bloombergTerminal.updateWatchlistData();
window.loadMarketNews = () => window.bloombergTerminal.updateMarketNews();
window.updateAIAlerts = () => window.bloombergTerminal.updateAIAlerts();