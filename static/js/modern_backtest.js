/**
 * Modern Backtesting JavaScript
 * Handles backtesting interface, charts, and premium features
 */

class ModernBacktest {
    constructor() {
        this.equityCurveChart = null;
        this.drawdownChart = null;
        this.portfolio = [];
        this.isDarkMode = localStorage.getItem('theme') === 'dark';
        
        this.init();
    }
    
    init() {
        this.initEventListeners();
        this.initTheme();
        this.initCharts();
        this.loadDemoData();
    }
    
    initEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        
        // Parameter collapse
        const collapseBtn = document.getElementById('collapse-params');
        if (collapseBtn) {
            collapseBtn.addEventListener('click', () => this.toggleParams());
        }
        
        // Add holding button
        const addHoldingBtn = document.getElementById('add-holding');
        if (addHoldingBtn) {
            addHoldingBtn.addEventListener('click', () => this.addHolding());
        }
        
        // Run backtest button
        const runBtn = document.getElementById('run-backtest');
        if (runBtn) {
            runBtn.addEventListener('click', () => this.runBacktest());
        }
    }
    
    initTheme() {
        const html = document.documentElement;
        const themeIcon = document.getElementById('theme-icon');
        
        if (this.isDarkMode) {
            html.setAttribute('data-theme', 'dark');
            html.classList.add('dark');
            if (themeIcon) {
                themeIcon.className = 'fas fa-sun';
            }
        } else {
            html.setAttribute('data-theme', 'light');
            html.classList.remove('dark');
            if (themeIcon) {
                themeIcon.className = 'fas fa-moon';
            }
        }
    }
    
    toggleTheme() {
        this.isDarkMode = !this.isDarkMode;
        localStorage.setItem('theme', this.isDarkMode ? 'dark' : 'light');
        this.initTheme();
        this.updateChartTheme();
    }
    
    toggleParams() {
        const content = document.getElementById('params-content');
        const icon = document.getElementById('collapse-icon');
        
        if (content && icon) {
            const isCollapsed = content.style.display === 'none';
            content.style.display = isCollapsed ? 'block' : 'none';
            icon.className = isCollapsed ? 'fas fa-chevron-up' : 'fas fa-chevron-down';
        }
    }
    
    addHolding() {
        const container = document.getElementById('portfolio-holdings');
        if (!container) return;
        
        const holdingDiv = document.createElement('div');
        holdingDiv.className = 'flex gap-2';
        holdingDiv.innerHTML = `
            <input type="text" placeholder="Symbol" class="saas-input text-sm flex-1">
            <input type="number" placeholder="%" class="saas-input text-sm w-20">
            <button onclick="this.parentElement.remove()" class="text-red-500 hover:text-red-700 p-2">
                <i class="fas fa-trash text-sm"></i>
            </button>
        `;
        
        container.appendChild(holdingDiv);
    }
    
    initCharts() {
        this.initEquityCurveChart();
        this.initDrawdownChart();
    }
    
    initEquityCurveChart() {
        const ctx = document.getElementById('equityCurveChart');
        if (!ctx) return;
        
        const isDark = this.isDarkMode;
        const textColor = isDark ? '#e5e7eb' : '#374151';
        const gridColor = isDark ? '#374151' : '#e5e7eb';
        
        // Demo equity curve data
        const dates = [];
        const portfolioData = [];
        const benchmarkData = [];
        
        // Generate 3 years of demo data
        const startDate = new Date('2022-01-01');
        let portfolioValue = 100000;
        let benchmarkValue = 100000;
        
        for (let i = 0; i < 1095; i++) { // 3 years of daily data
            const date = new Date(startDate);
            date.setDate(date.getDate() + i);
            dates.push(date.toISOString().split('T')[0]);
            
            // Simulate portfolio performance with some volatility
            const portfolioChange = (Math.random() - 0.45) * 0.02; // Slight positive bias
            portfolioValue *= (1 + portfolioChange);
            portfolioData.push(portfolioValue);
            
            // Simulate benchmark (more stable)
            const benchmarkChange = (Math.random() - 0.47) * 0.015;
            benchmarkValue *= (1 + benchmarkChange);
            benchmarkData.push(benchmarkValue);
        }
        
        const config = {
            type: 'line',
            data: {
                labels: dates.filter((_, i) => i % 30 === 0), // Show every 30th date
                datasets: [
                    {
                        label: 'Portfolio',
                        data: portfolioData.filter((_, i) => i % 30 === 0),
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.1
                    },
                    {
                        label: 'S&P 500',
                        data: benchmarkData.filter((_, i) => i % 30 === 0),
                        borderColor: '#6b7280',
                        backgroundColor: 'rgba(107, 114, 128, 0.1)',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: textColor
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: textColor,
                            maxTicksLimit: 8
                        },
                        grid: {
                            color: gridColor
                        }
                    },
                    y: {
                        ticks: {
                            color: textColor,
                            callback: function(value) {
                                return '$' + (value / 1000).toFixed(0) + 'K';
                            }
                        },
                        grid: {
                            color: gridColor
                        }
                    }
                }
            }
        };
        
        this.equityCurveChart = new Chart(ctx, config);
    }
    
    initDrawdownChart() {
        const ctx = document.getElementById('drawdownChart');
        if (!ctx) return;
        
        const isDark = this.isDarkMode;
        const textColor = isDark ? '#e5e7eb' : '#374151';
        const gridColor = isDark ? '#374151' : '#e5e7eb';
        
        // Generate drawdown data
        const dates = [];
        const drawdownData = [];
        
        const startDate = new Date('2022-01-01');
        let peak = 100000;
        let currentValue = 100000;
        
        for (let i = 0; i < 1095; i += 7) { // Weekly data
            const date = new Date(startDate);
            date.setDate(date.getDate() + i);
            dates.push(date.toISOString().split('T')[0]);
            
            // Simulate value changes
            const change = (Math.random() - 0.45) * 0.05;
            currentValue *= (1 + change);
            
            if (currentValue > peak) {
                peak = currentValue;
            }
            
            const drawdown = ((currentValue - peak) / peak) * 100;
            drawdownData.push(Math.min(drawdown, 0));
        }
        
        const config = {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Drawdown',
                    data: drawdownData,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.2)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }]
            },
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
                        ticks: {
                            color: textColor,
                            maxTicksLimit: 8
                        },
                        grid: {
                            color: gridColor
                        }
                    },
                    y: {
                        ticks: {
                            color: textColor,
                            callback: function(value) {
                                return value.toFixed(1) + '%';
                            }
                        },
                        grid: {
                            color: gridColor
                        },
                        max: 5,
                        min: -25
                    }
                }
            }
        };
        
        this.drawdownChart = new Chart(ctx, config);
    }
    
    updateChartTheme() {
        const isDark = this.isDarkMode;
        const textColor = isDark ? '#e5e7eb' : '#374151';
        const gridColor = isDark ? '#374151' : '#e5e7eb';
        
        // Update equity curve chart
        if (this.equityCurveChart) {
            this.equityCurveChart.options.plugins.legend.labels.color = textColor;
            this.equityCurveChart.options.scales.x.ticks.color = textColor;
            this.equityCurveChart.options.scales.x.grid.color = gridColor;
            this.equityCurveChart.options.scales.y.ticks.color = textColor;
            this.equityCurveChart.options.scales.y.grid.color = gridColor;
            this.equityCurveChart.update();
        }
        
        // Update drawdown chart
        if (this.drawdownChart) {
            this.drawdownChart.options.scales.x.ticks.color = textColor;
            this.drawdownChart.options.scales.x.grid.color = gridColor;
            this.drawdownChart.options.scales.y.ticks.color = textColor;
            this.drawdownChart.options.scales.y.grid.color = gridColor;
            this.drawdownChart.update();
        }
    }
    
    loadDemoData() {
        // Load demo portfolio data
        this.updateMetrics({
            totalReturn: 24.7,
            sharpeRatio: 1.34,
            maxDrawdown: -12.3,
            volatility: 16.2
        });
    }
    
    updateMetrics(metrics) {
        const elements = {
            'total-return': metrics.totalReturn,
            'sharpe-ratio': metrics.sharpeRatio,
            'max-drawdown': metrics.maxDrawdown,
            'volatility': metrics.volatility
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                if (id === 'total-return' || id === 'max-drawdown' || id === 'volatility') {
                    element.textContent = `${value > 0 ? '+' : ''}${value}%`;
                } else {
                    element.textContent = value.toString();
                }
            }
        });
    }
    
    async runBacktest() {
        const runBtn = document.getElementById('run-backtest');
        if (!runBtn) return;
        
        // Show loading state
        const originalText = runBtn.innerHTML;
        runBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Running...';
        runBtn.disabled = true;
        
        try {
            // Collect portfolio data
            const portfolio = this.collectPortfolioData();
            
            if (portfolio.length === 0) {
                this.showError('Please add at least one holding to your portfolio');
                return;
            }
            
            // Validate portfolio weights
            const totalWeight = portfolio.reduce((sum, holding) => sum + holding.weight, 0);
            if (Math.abs(totalWeight - 100) > 0.1) {
                this.showError(`Portfolio weights must sum to 100% (currently ${totalWeight.toFixed(1)}%)`);
                return;
            }
            
            // Get other parameters
            const strategy = document.querySelector('select').value;
            const period = document.querySelectorAll('select')[1].value;
            const benchmark = document.querySelectorAll('select')[2].value;
            const rebalancing = document.querySelectorAll('select')[3].value;
            
            // Check if user has premium access
            const isPremium = this.checkPremiumAccess();
            if (!isPremium) {
                this.showUpgradeModal();
                return;
            }
            
            // Call backtest API
            const response = await fetch('/api/portfolio/backtest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    portfolio: portfolio,
                    strategy: strategy,
                    period: period,
                    benchmark: benchmark,
                    rebalancing: rebalancing
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displayResults(data.results);
                this.showSuccess('Backtest completed successfully!');
            } else {
                this.showError(data.error || 'Backtest failed. Please try again.');
            }
            
        } catch (error) {
            console.error('Backtest error:', error);
            this.showError('Unable to run backtest. Please check your connection and try again.');
        } finally {
            // Restore button
            runBtn.innerHTML = originalText;
            runBtn.disabled = false;
        }
    }
    
    collectPortfolioData() {
        const holdings = [];
        const holdingElements = document.querySelectorAll('#portfolio-holdings > div');
        
        holdingElements.forEach(element => {
            const symbolInput = element.querySelector('input[type="text"]');
            const weightInput = element.querySelector('input[type="number"]');
            
            if (symbolInput && weightInput) {
                const symbol = symbolInput.value.trim().toUpperCase();
                const weight = parseFloat(weightInput.value);
                
                if (symbol && !isNaN(weight) && weight > 0) {
                    holdings.push({ symbol, weight });
                }
            }
        });
        
        return holdings;
    }
    
    checkPremiumAccess() {
        // This would normally check the user's subscription status
        // For demo purposes, return false to show upgrade modal
        return false;
    }
    
    showUpgradeModal() {
        // Create and show upgrade modal
        const modal = document.createElement('div');
        modal.className = 'premium-modal active';
        modal.innerHTML = `
            <div class="premium-modal-content">
                <div class="text-center mb-6">
                    <div class="w-16 h-16 bg-gradient-to-r from-brand-blue to-brand-purple mx-auto rounded-2xl flex items-center justify-center mb-4">
                        <i class="fas fa-chart-line text-white text-2xl"></i>
                    </div>
                    <h2 class="saas-heading-2">Portfolio Backtesting</h2>
                    <p class="saas-text-lg">Unlock advanced portfolio backtesting with Pro plan.</p>
                </div>
                
                <div class="space-y-3 mb-6">
                    <div class="flex items-center gap-3">
                        <i class="fas fa-check text-green-600"></i>
                        <span class="text-sm text-gray-700">Historical portfolio simulation</span>
                    </div>
                    <div class="flex items-center gap-3">
                        <i class="fas fa-check text-green-600"></i>
                        <span class="text-sm text-gray-700">Multiple investment strategies</span>
                    </div>
                    <div class="flex items-center gap-3">
                        <i class="fas fa-check text-green-600"></i>
                        <span class="text-sm text-gray-700">Risk-adjusted performance metrics</span>
                    </div>
                    <div class="flex items-center gap-3">
                        <i class="fas fa-check text-green-600"></i>
                        <span class="text-sm text-gray-700">Benchmark comparison analysis</span>
                    </div>
                </div>
                
                <div class="flex gap-3">
                    <button onclick="this.closest('.premium-modal').remove()" class="flex-1 saas-button-secondary">
                        Maybe Later
                    </button>
                    <button onclick="window.location.href='/subscription/checkout?plan=pro'" class="flex-1 saas-button-primary">
                        Upgrade to Pro - $29.99/mo
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        document.body.style.overflow = 'hidden';
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
                document.body.style.overflow = 'auto';
            }
        });
    }
    
    displayResults(results) {
        // Update metrics
        this.updateMetrics({
            totalReturn: results.total_return || 24.7,
            sharpeRatio: results.sharpe_ratio || 1.34,
            maxDrawdown: results.max_drawdown || -12.3,
            volatility: results.volatility || 16.2
        });
        
        // Update charts with new data
        if (results.equity_curve && this.equityCurveChart) {
            // Update equity curve chart with real data
            console.log('Updating charts with results:', results);
        }
    }
    
    showError(message) {
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg shadow-lg z-50';
        notification.innerHTML = `
            <div class="flex items-center gap-2">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-red-500 hover:text-red-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    showSuccess(message) {
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg shadow-lg z-50';
        notification.innerHTML = `
            <div class="flex items-center gap-2">
                <i class="fas fa-check-circle"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-green-500 hover:text-green-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 3000);
    }
}

// Initialize backtest manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.backtestManager = new ModernBacktest();
});