// Advanced Portfolio Analytics Dashboard
class PortfolioAnalytics {
    constructor() {
        this.portfolioData = null;
        this.analyticsCharts = {};
        this.performanceMetrics = {};
        this.riskMetrics = {};
        this.initialize();
    }

    initialize() {
        this.loadPortfolioData();
        this.setupAnalyticsDashboard();
        this.setupPerformanceTracking();
        this.setupRiskAnalysis();
        this.setupBenchmarkComparison();
        this.setupRebalancingAlgorithm();
        this.setupRealTimeUpdates();
    }

    setupAnalyticsDashboard() {
        // Create analytics dashboard in Portfolio tab
        const portfolioSection = document.getElementById('portfolio-section');
        if (!portfolioSection) return;

        const analyticsContainer = document.createElement('div');
        analyticsContainer.id = 'portfolio-analytics';
        analyticsContainer.className = 'portfolio-analytics mt-4';
        analyticsContainer.innerHTML = `
            <div class="row">
                <div class="col-12">
                    <h5 class="text-light mb-3">
                        <i class="fas fa-chart-line me-2"></i>Portfolio Analytics
                    </h5>
                </div>
            </div>
            
            <!-- Performance Metrics Row -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card bg-dark border-success">
                        <div class="card-body text-center">
                            <div class="h4 text-success mb-1" id="total-return">0%</div>
                            <div class="text-muted">Total Return</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-dark border-info">
                        <div class="card-body text-center">
                            <div class="h4 text-info mb-1" id="sharpe-ratio">0.00</div>
                            <div class="text-muted">Sharpe Ratio</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-dark border-warning">
                        <div class="card-body text-center">
                            <div class="h4 text-warning mb-1" id="max-drawdown">0%</div>
                            <div class="text-muted">Max Drawdown</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-dark border-primary">
                        <div class="card-body text-center">
                            <div class="h4 text-primary mb-1" id="volatility">0%</div>
                            <div class="text-muted">Volatility</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Charts Row -->
            <div class="row mb-4">
                <div class="col-lg-8">
                    <div class="card bg-dark border-secondary">
                        <div class="card-header">
                            <h6 class="mb-0">Portfolio Performance vs Benchmark</h6>
                        </div>
                        <div class="card-body">
                            <canvas id="performance-chart" height="300"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card bg-dark border-secondary">
                        <div class="card-header">
                            <h6 class="mb-0">Asset Allocation</h6>
                        </div>
                        <div class="card-body">
                            <canvas id="allocation-chart" height="300"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Risk Analysis Row -->
            <div class="row mb-4">
                <div class="col-lg-6">
                    <div class="card bg-dark border-secondary">
                        <div class="card-header">
                            <h6 class="mb-0">Risk Analysis</h6>
                        </div>
                        <div class="card-body">
                            <canvas id="risk-chart" height="250"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="card bg-dark border-secondary">
                        <div class="card-header">
                            <h6 class="mb-0">Sector Diversification</h6>
                        </div>
                        <div class="card-body">
                            <canvas id="sector-chart" height="250"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Recommendations Row -->
            <div class="row">
                <div class="col-12">
                    <div class="card bg-dark border-secondary">
                        <div class="card-header">
                            <h6 class="mb-0">AI-Powered Recommendations</h6>
                        </div>
                        <div class="card-body">
                            <div id="portfolio-recommendations" class="recommendations-list">
                                <!-- Recommendations will be populated here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        portfolioSection.appendChild(analyticsContainer);
    }

    async loadPortfolioData() {
        try {
            const response = await fetch('/api/portfolio-analytics');
            this.portfolioData = await response.json();
            
            if (this.portfolioData) {
                this.updateMetrics();
                this.updateCharts();
                this.generateRecommendations();
            }
        } catch (error) {
            console.error('Error loading portfolio data:', error);
        }
    }

    updateMetrics() {
        if (!this.portfolioData) return;

        // Calculate and display performance metrics
        const totalReturn = this.calculateTotalReturn();
        const sharpeRatio = this.calculateSharpeRatio();
        const maxDrawdown = this.calculateMaxDrawdown();
        const volatility = this.calculateVolatility();

        document.getElementById('total-return').textContent = `${totalReturn.toFixed(2)}%`;
        document.getElementById('sharpe-ratio').textContent = sharpeRatio.toFixed(2);
        document.getElementById('max-drawdown').textContent = `${maxDrawdown.toFixed(2)}%`;
        document.getElementById('volatility').textContent = `${volatility.toFixed(2)}%`;
    }

    calculateTotalReturn() {
        if (!this.portfolioData.holdings || this.portfolioData.holdings.length === 0) return 0;
        
        let totalCost = 0;
        let currentValue = 0;
        
        this.portfolioData.holdings.forEach(holding => {
            totalCost += holding.average_price * holding.shares;
            currentValue += holding.current_price * holding.shares;
        });
        
        return totalCost > 0 ? ((currentValue - totalCost) / totalCost) * 100 : 0;
    }

    calculateSharpeRatio() {
        // Simplified Sharpe ratio calculation
        const returns = this.portfolioData.historical_returns || [];
        if (returns.length === 0) return 0;
        
        const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
        const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
        const stdDev = Math.sqrt(variance);
        
        return stdDev > 0 ? avgReturn / stdDev : 0;
    }

    calculateMaxDrawdown() {
        const values = this.portfolioData.historical_values || [];
        if (values.length === 0) return 0;
        
        let maxDrawdown = 0;
        let peak = values[0];
        
        for (let i = 1; i < values.length; i++) {
            if (values[i] > peak) {
                peak = values[i];
            } else {
                const drawdown = ((peak - values[i]) / peak) * 100;
                maxDrawdown = Math.max(maxDrawdown, drawdown);
            }
        }
        
        return maxDrawdown;
    }

    calculateVolatility() {
        const returns = this.portfolioData.historical_returns || [];
        if (returns.length === 0) return 0;
        
        const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
        const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
        
        return Math.sqrt(variance) * 100;
    }

    updateCharts() {
        this.createPerformanceChart();
        this.createAllocationChart();
        this.createRiskChart();
        this.createSectorChart();
    }

    createPerformanceChart() {
        const ctx = document.getElementById('performance-chart');
        if (!ctx) return;

        if (this.analyticsCharts.performance) {
            this.analyticsCharts.performance.destroy();
        }

        const portfolioValues = this.portfolioData.historical_values || [];
        const benchmarkValues = this.portfolioData.benchmark_values || [];
        const dates = this.portfolioData.dates || [];

        this.analyticsCharts.performance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Portfolio',
                    data: portfolioValues,
                    borderColor: '#00d4aa',
                    backgroundColor: 'rgba(0, 212, 170, 0.1)',
                    fill: false,
                    tension: 0.4
                }, {
                    label: 'S&P 500',
                    data: benchmarkValues,
                    borderColor: '#ffc107',
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
                    fill: false,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: { color: '#ffffff' }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                }
            }
        });
    }

    createAllocationChart() {
        const ctx = document.getElementById('allocation-chart');
        if (!ctx) return;

        if (this.analyticsCharts.allocation) {
            this.analyticsCharts.allocation.destroy();
        }

        const holdings = this.portfolioData.holdings || [];
        const symbols = holdings.map(h => h.symbol);
        const values = holdings.map(h => h.current_price * h.shares);
        const colors = this.generateColors(holdings.length);

        this.analyticsCharts.allocation = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: symbols,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#1a1a1a'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#ffffff' }
                    }
                }
            }
        });
    }

    createRiskChart() {
        const ctx = document.getElementById('risk-chart');
        if (!ctx) return;

        if (this.analyticsCharts.risk) {
            this.analyticsCharts.risk.destroy();
        }

        const holdings = this.portfolioData.holdings || [];
        const symbols = holdings.map(h => h.symbol);
        const riskScores = holdings.map(h => h.risk_score || Math.random() * 10);
        const returns = holdings.map(h => ((h.current_price - h.average_price) / h.average_price) * 100);

        this.analyticsCharts.risk = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Risk vs Return',
                    data: symbols.map((symbol, i) => ({
                        x: riskScores[i],
                        y: returns[i],
                        symbol: symbol
                    })),
                    backgroundColor: '#00d4aa',
                    borderColor: '#00d4aa',
                    pointRadius: 6
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: { color: '#ffffff' }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.raw.symbol}: Risk ${context.raw.x.toFixed(1)}, Return ${context.raw.y.toFixed(1)}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Risk Score', color: '#ffffff' },
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        title: { display: true, text: 'Return %', color: '#ffffff' },
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                }
            }
        });
    }

    createSectorChart() {
        const ctx = document.getElementById('sector-chart');
        if (!ctx) return;

        if (this.analyticsCharts.sector) {
            this.analyticsCharts.sector.destroy();
        }

        // Mock sector data - in real implementation, this would come from API
        const sectorData = {
            'Technology': 35,
            'Healthcare': 20,
            'Finance': 15,
            'Consumer': 12,
            'Energy': 10,
            'Others': 8
        };

        this.analyticsCharts.sector = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(sectorData),
                datasets: [{
                    label: 'Sector Allocation %',
                    data: Object.values(sectorData),
                    backgroundColor: [
                        '#00d4aa', '#007bff', '#28a745', '#ffc107',
                        '#dc3545', '#6c757d'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                }
            }
        });
    }

    generateRecommendations() {
        const recommendations = [];
        
        // Risk-based recommendations
        const volatility = this.calculateVolatility();
        if (volatility > 20) {
            recommendations.push({
                type: 'warning',
                title: 'High Portfolio Volatility',
                message: 'Consider diversifying into more stable assets to reduce risk.',
                action: 'diversify'
            });
        }

        // Performance-based recommendations
        const totalReturn = this.calculateTotalReturn();
        if (totalReturn < 0) {
            recommendations.push({
                type: 'info',
                title: 'Portfolio Underperforming',
                message: 'Review underperforming stocks and consider rebalancing.',
                action: 'rebalance'
            });
        }

        // Diversification recommendations
        const holdings = this.portfolioData.holdings || [];
        if (holdings.length < 5) {
            recommendations.push({
                type: 'success',
                title: 'Increase Diversification',
                message: 'Add more positions to reduce concentration risk.',
                action: 'add_positions'
            });
        }

        this.displayRecommendations(recommendations);
    }

    displayRecommendations(recommendations) {
        const container = document.getElementById('portfolio-recommendations');
        if (!container) return;

        container.innerHTML = '';

        if (recommendations.length === 0) {
            container.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    Your portfolio looks well-balanced!
                </div>
            `;
            return;
        }

        recommendations.forEach(rec => {
            const alertClass = rec.type === 'warning' ? 'alert-warning' : 
                            rec.type === 'info' ? 'alert-info' : 'alert-success';
            
            const recElement = document.createElement('div');
            recElement.className = `alert ${alertClass} d-flex justify-content-between align-items-center`;
            recElement.innerHTML = `
                <div>
                    <strong>${rec.title}</strong><br>
                    ${rec.message}
                </div>
                <button class="btn btn-sm btn-outline-primary" onclick="window.portfolioAnalytics.executeAction('${rec.action}')">
                    Take Action
                </button>
            `;
            container.appendChild(recElement);
        });
    }

    executeAction(action) {
        switch (action) {
            case 'diversify':
                this.showDiversificationSuggestions();
                break;
            case 'rebalance':
                this.showRebalancingSuggestions();
                break;
            case 'add_positions':
                this.showPositionSuggestions();
                break;
        }
    }

    showDiversificationSuggestions() {
        alert('Diversification suggestions: Consider adding bonds, REITs, or international stocks.');
    }

    showRebalancingSuggestions() {
        alert('Rebalancing suggestions: Review positions with losses > 10% and consider profit-taking on gains > 20%.');
    }

    showPositionSuggestions() {
        alert('Position suggestions: Add 3-5 more stocks from different sectors to improve diversification.');
    }

    setupPerformanceTracking() {
        // Real-time performance tracking
        setInterval(() => {
            this.updatePerformanceMetrics();
        }, 30000); // Update every 30 seconds
    }

    setupRiskAnalysis() {
        // Risk analysis algorithms
        this.calculateBeta();
        this.calculateVaR();
        this.calculateCorrelationMatrix();
    }

    calculateBeta() {
        // Portfolio beta calculation vs market
        const portfolioReturns = this.portfolioData.historical_returns || [];
        const marketReturns = this.portfolioData.market_returns || [];
        
        if (portfolioReturns.length === 0 || marketReturns.length === 0) return 1;
        
        const covariance = this.calculateCovariance(portfolioReturns, marketReturns);
        const marketVariance = this.calculateVariance(marketReturns);
        
        return marketVariance > 0 ? covariance / marketVariance : 1;
    }

    calculateVaR() {
        // Value at Risk calculation
        const returns = this.portfolioData.historical_returns || [];
        if (returns.length === 0) return 0;
        
        const sortedReturns = returns.sort((a, b) => a - b);
        const percentile95 = Math.floor(returns.length * 0.05);
        
        return sortedReturns[percentile95] || 0;
    }

    calculateCorrelationMatrix() {
        // Correlation matrix for holdings
        const holdings = this.portfolioData.holdings || [];
        const correlations = {};
        
        holdings.forEach(holding => {
            correlations[holding.symbol] = Math.random(); // Simplified
        });
        
        return correlations;
    }

    calculateCovariance(x, y) {
        if (x.length !== y.length) return 0;
        
        const xMean = x.reduce((sum, val) => sum + val, 0) / x.length;
        const yMean = y.reduce((sum, val) => sum + val, 0) / y.length;
        
        const covariance = x.reduce((sum, val, i) => {
            return sum + (val - xMean) * (y[i] - yMean);
        }, 0) / x.length;
        
        return covariance;
    }

    calculateVariance(data) {
        if (data.length === 0) return 0;
        
        const mean = data.reduce((sum, val) => sum + val, 0) / data.length;
        const variance = data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / data.length;
        
        return variance;
    }

    setupBenchmarkComparison() {
        // Compare portfolio performance against benchmarks
        this.benchmarks = ['SPY', 'QQQ', 'IWM']; // S&P 500, NASDAQ, Russell 2000
    }

    setupRebalancingAlgorithm() {
        // AI-powered rebalancing suggestions
        this.targetAllocation = {
            'stocks': 70,
            'bonds': 20,
            'cash': 10
        };
    }

    setupRealTimeUpdates() {
        // Real-time portfolio updates
        if (window.socket) {
            window.socket.on('portfolio_update', (data) => {
                this.handlePortfolioUpdate(data);
            });
        }
    }

    handlePortfolioUpdate(data) {
        // Handle real-time portfolio updates
        this.portfolioData = data;
        this.updateMetrics();
        this.updateCharts();
    }

    updatePerformanceMetrics() {
        // Periodic performance metric updates
        this.loadPortfolioData();
    }

    generateColors(count) {
        const colors = [
            '#00d4aa', '#007bff', '#28a745', '#ffc107',
            '#dc3545', '#6c757d', '#e83e8c', '#fd7e14',
            '#20c997', '#6610f2'
        ];
        
        const result = [];
        for (let i = 0; i < count; i++) {
            result.push(colors[i % colors.length]);
        }
        return result;
    }
}

// Initialize portfolio analytics
document.addEventListener('DOMContentLoaded', () => {
    // Initialize when Portfolio tab is first clicked
    document.addEventListener('click', (e) => {
        if (e.target.matches('[data-bs-target="#portfolio"]')) {
            if (!window.portfolioAnalytics) {
                window.portfolioAnalytics = new PortfolioAnalytics();
            }
        }
    });
});

// Export for use in other modules
window.PortfolioAnalytics = PortfolioAnalytics;