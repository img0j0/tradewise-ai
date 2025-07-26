/**
 * Dashboard Charts Module
 * Handles chart creation and market data visualization
 */

class DashboardCharts {
    constructor() {
        this.charts = {};
        this.init();
    }

    init() {
        this.loadMarketData();
        this.createPortfolioChart();
        this.createMarketOverviewChart();
    }

    async loadMarketData() {
        try {
            const response = await fetch('/api/market-data');
            if (response.ok) {
                const data = await response.json();
                this.updateDashboardData(data);
            } else {
                console.log('Market data not available, using defaults');
                this.useDefaultData();
            }
        } catch (error) {
            console.log('Using default market data');
            this.useDefaultData();
        }
    }

    updateDashboardData(data) {
        // Update portfolio value
        const portfolioValue = document.getElementById('portfolio-value');
        const portfolioChange = document.getElementById('portfolio-change');
        
        if (portfolioValue && data.portfolio) {
            portfolioValue.textContent = `$${data.portfolio.value.toLocaleString()}`;
        }
        
        if (portfolioChange && data.portfolio) {
            const changeClass = data.portfolio.change >= 0 ? 'text-success-600' : 'text-error-600';
            portfolioChange.textContent = `+${data.portfolio.change_percent}%`;
            portfolioChange.className = `text-2xl font-bold ${changeClass}`;
        }
    }

    useDefaultData() {
        // Set default portfolio data
        const portfolioValue = document.getElementById('portfolio-value');
        const portfolioChange = document.getElementById('portfolio-change');
        
        if (portfolioValue) {
            portfolioValue.textContent = '$125,430';
        }
        
        if (portfolioChange) {
            portfolioChange.textContent = '+2.34%';
            portfolioChange.className = 'text-2xl font-bold text-success-600';
        }
    }

    createPortfolioChart() {
        const canvas = document.getElementById('portfolio-sparkline');
        if (!canvas || typeof Chart === 'undefined') return;

        const ctx = canvas.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 60);
        gradient.addColorStop(0, 'rgba(16, 185, 129, 0.3)');
        gradient.addColorStop(1, 'rgba(16, 185, 129, 0.0)');

        this.charts.portfolio = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['', '', '', '', '', '', ''],
                datasets: [{
                    data: [100000, 105000, 102000, 108000, 115000, 120000, 125430],
                    borderColor: '#10b981',
                    backgroundColor: gradient,
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                },
                elements: {
                    point: { radius: 0 }
                }
            }
        });
    }

    createMarketOverviewChart() {
        const canvas = document.getElementById('market-overview-chart');
        if (!canvas || typeof Chart === 'undefined') return;

        const ctx = canvas.getContext('2d');
        
        this.charts.market = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer'],
                datasets: [{
                    data: [30, 20, 15, 20, 15],
                    backgroundColor: [
                        '#8b5cf6',
                        '#06b6d4',
                        '#f59e0b',
                        '#10b981',
                        '#ef4444'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: { size: 12 }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }
}

// Initialize dashboard charts when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DashboardCharts();
});

// Export for global access
window.DashboardCharts = DashboardCharts;