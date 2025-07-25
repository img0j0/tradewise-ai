// Modern Dashboard JavaScript with Chart.js Integration
// Real-time data loading and chart management

class DashboardManager {
    constructor() {
        this.portfolioChart = null;
        this.sectorChart = null;
        this.isInitialized = false;
        this.updateInterval = null;
    }

    async init() {
        if (this.isInitialized) return;
        
        try {
            await this.loadChartJS();
            await this.initializeCharts();
            await this.loadDashboardData();
            this.startRealTimeUpdates();
            this.isInitialized = true;
            console.log('Dashboard initialized successfully');
        } catch (error) {
            console.error('Dashboard initialization error:', error);
            this.showError('Failed to initialize dashboard');
        }
    }

    async loadChartJS() {
        return new Promise((resolve, reject) => {
            if (typeof Chart !== 'undefined') {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    async initializeCharts() {
        await this.createPortfolioChart();
        await this.createSectorChart();
    }

    async createPortfolioChart() {
        const ctx = document.getElementById('portfolio-chart');
        if (!ctx) return;

        // Generate sample portfolio data for the past 30 days
        const portfolioData = this.generatePortfolioData();
        
        this.portfolioChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: portfolioData.labels,
                datasets: [{
                    label: 'Portfolio Value',
                    data: portfolioData.values,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#3b82f6',
                    pointHoverBorderColor: '#ffffff',
                    pointHoverBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#3b82f6',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return `$${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: false,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: false,
                        grid: {
                            display: false
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                elements: {
                    line: {
                        borderJoinStyle: 'round'
                    }
                }
            }
        });
    }

    async createSectorChart() {
        const ctx = document.getElementById('sector-chart');
        if (!ctx) return;

        const sectorData = [
            { name: 'Technology', performance: 2.3, color: '#3b82f6' },
            { name: 'Healthcare', performance: 1.1, color: '#10b981' },
            { name: 'Financial', performance: -0.5, color: '#ef4444' },
            { name: 'Energy', performance: 0.8, color: '#f59e0b' },
            { name: 'Consumer', performance: 1.8, color: '#8b5cf6' }
        ];

        this.sectorChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: sectorData.map(s => s.name),
                datasets: [{
                    data: sectorData.map(s => s.performance),
                    backgroundColor: sectorData.map(s => s.color),
                    borderRadius: 4,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#374151',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.y;
                                const sign = value >= 0 ? '+' : '';
                                return `${sign}${value.toFixed(1)}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 11
                            },
                            maxRotation: 0
                        }
                    },
                    y: {
                        display: false,
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    generatePortfolioData() {
        const days = 30;
        const labels = [];
        const values = [];
        const baseValue = 12450;
        
        for (let i = days; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
            
            // Generate realistic portfolio fluctuation
            const randomChange = (Math.random() - 0.5) * 0.03; // ±1.5% daily
            const previousValue = values[values.length - 1] || baseValue;
            const newValue = previousValue * (1 + randomChange);
            values.push(Math.round(newValue));
        }
        
        return { labels, values };
    }

    async loadDashboardData() {
        try {
            // Load portfolio data
            await this.updatePortfolioData();
            
            // Load AI insights
            await this.updateAIInsights();
            
            // Load market data
            await this.updateMarketData();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async updatePortfolioData() {
        // Simulate portfolio data - in production this would fetch from API
        const portfolioValue = 12450;
        const dailyChange = 287;
        const dailyChangePercent = 2.3;
        const totalReturn = 1850;
        const totalReturnPercent = 17.5;

        // Update UI elements
        this.updateElement('portfolio-value', `$${portfolioValue.toLocaleString()}`);
        this.updateElement('portfolio-change', 
            `+$${dailyChange} (+${dailyChangePercent}%)`, 
            dailyChange >= 0 ? 'text-green-600' : 'text-red-600'
        );
        this.updateElement('daily-change', 
            `$${dailyChange} (${dailyChangePercent}%)`,
            dailyChange >= 0 ? 'text-green-600' : 'text-red-600'
        );
        this.updateElement('total-return', 
            `$${totalReturn} (${totalReturnPercent}%)`,
            totalReturn >= 0 ? 'text-green-600' : 'text-red-600'
        );
    }

    async updateAIInsights() {
        // In production, this would fetch real AI insights from the backend
        try {
            const response = await fetch('/api/dashboard/ai-insights');
            if (response.ok) {
                const insights = await response.json();
                this.renderAIInsights(insights);
            }
        } catch (error) {
            console.log('Using default AI insights');
        }
    }

    async updateMarketData() {
        try {
            // Fetch real market data
            const response = await fetch('/api/market/indices');
            if (response.ok) {
                const marketData = await response.json();
                this.renderMarketData(marketData);
            }
        } catch (error) {
            console.log('Using default market data');
        }
    }

    renderAIInsights(insights) {
        const container = document.getElementById('ai-insights');
        if (!container || !insights) return;

        // This would render dynamic AI insights from the backend
        // For now, the template contains static examples
    }

    renderMarketData(marketData) {
        const indicesContainer = document.getElementById('market-indices');
        const moversContainer = document.getElementById('top-movers');
        
        if (marketData && marketData.indices) {
            // Update market indices with real data
            // Implementation would update the DOM elements
        }
    }

    updateElement(id, content, className = '') {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
            if (className) {
                element.className = element.className.replace(/text-(green|red)-600/g, '') + ' ' + className;
            }
        }
    }

    startRealTimeUpdates() {
        // Update every 5 minutes
        this.updateInterval = setInterval(() => {
            this.loadDashboardData();
        }, 5 * 60 * 1000);
    }

    stopRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    showError(message) {
        console.error('Dashboard Error:', message);
        // Could show a toast notification here
    }

    destroy() {
        this.stopRealTimeUpdates();
        
        if (this.portfolioChart) {
            this.portfolioChart.destroy();
            this.portfolioChart = null;
        }
        
        if (this.sectorChart) {
            this.sectorChart.destroy();
            this.sectorChart = null;
        }
        
        this.isInitialized = false;
    }
}

// Initialize dashboard when DOM is ready
let dashboardManager = null;

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('portfolio-chart')) {
        dashboardManager = new DashboardManager();
        dashboardManager.init();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (dashboardManager) {
        dashboardManager.destroy();
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardManager;
}