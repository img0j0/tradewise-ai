/**
 * Modern Dashboard JavaScript
 * Handles UI interactions, charts, and premium features
 */

class ModernDashboard {
    constructor() {
        this.sidebarCollapsed = false;
        this.isDarkMode = localStorage.getItem('theme') === 'dark';
        this.portfolioChart = null;
        
        this.init();
    }
    
    init() {
        this.initEventListeners();
        this.initTheme();
        this.initCharts();
        this.loadDashboardData();
    }
    
    initEventListeners() {
        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }
        
        if (mobileMenuBtn) {
            mobileMenuBtn.addEventListener('click', () => this.toggleMobileSidebar());
        }
        
        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        
        // User menu dropdown
        const userMenuBtn = document.getElementById('user-menu-btn');
        const userDropdown = document.getElementById('user-dropdown');
        
        if (userMenuBtn && userDropdown) {
            userMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                userDropdown.classList.toggle('hidden');
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', () => {
                userDropdown.classList.add('hidden');
            });
        }
        
        // Premium modal close on background click
        document.addEventListener('click', (e) => {
            const modal = document.getElementById('premium-modal');
            if (e.target === modal) {
                this.closeUpgradeModal();
            }
        });
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
        
        // Reinitialize charts with new theme colors
        if (this.portfolioChart) {
            this.updateChartTheme();
        }
    }
    
    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('main-content');
        
        this.sidebarCollapsed = !this.sidebarCollapsed;
        
        if (sidebar) {
            sidebar.classList.toggle('collapsed', this.sidebarCollapsed);
        }
        
        if (mainContent) {
            mainContent.classList.toggle('sidebar-collapsed', this.sidebarCollapsed);
        }
    }
    
    toggleMobileSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.toggle('mobile-open');
        }
    }
    
    initCharts() {
        this.initPortfolioChart();
    }
    
    initPortfolioChart() {
        const ctx = document.getElementById('portfolioChart');
        if (!ctx) return;
        
        const isDark = this.isDarkMode;
        const textColor = isDark ? '#e5e7eb' : '#374151';
        const gridColor = isDark ? '#374151' : '#e5e7eb';
        
        // Sample portfolio data
        const data = {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
            datasets: [{
                label: 'Portfolio Value',
                data: [100000, 105000, 98000, 112000, 118000, 125000, 125847],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        };
        
        const config = {
            type: 'line',
            data: data,
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
                            color: textColor
                        },
                        grid: {
                            color: gridColor
                        }
                    },
                    y: {
                        ticks: {
                            color: textColor,
                            callback: function(value) {
                                return '$' + (value / 1000) + 'K';
                            }
                        },
                        grid: {
                            color: gridColor
                        }
                    }
                }
            }
        };
        
        this.portfolioChart = new Chart(ctx, config);
    }
    
    updateChartTheme() {
        if (!this.portfolioChart) return;
        
        const isDark = this.isDarkMode;
        const textColor = isDark ? '#e5e7eb' : '#374151';
        const gridColor = isDark ? '#374151' : '#e5e7eb';
        
        this.portfolioChart.options.scales.x.ticks.color = textColor;
        this.portfolioChart.options.scales.x.grid.color = gridColor;
        this.portfolioChart.options.scales.y.ticks.color = textColor;
        this.portfolioChart.options.scales.y.grid.color = gridColor;
        
        this.portfolioChart.update();
    }
    
    async loadDashboardData() {
        try {
            // Load portfolio data
            await this.loadPortfolioData();
            
            // Load AI insights
            await this.loadAIInsights();
            
            // Load market data
            await this.loadMarketData();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showErrorMessage('Unable to load dashboard data. Please refresh the page.');
        }
    }
    
    async loadPortfolioData() {
        try {
            const response = await fetch('/api/portfolio/summary');
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.updatePortfolioMetrics(data.portfolio);
                }
            }
        } catch (error) {
            console.log('Portfolio data not available - using demo data');
            // Keep demo data displayed
        }
    }
    
    async loadAIInsights() {
        try {
            const response = await fetch('/api/ai/dashboard-insights');
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.updateAIInsights(data.insights);
                }
            }
        } catch (error) {
            console.log('AI insights not available - using demo insights');
            // Keep demo insights displayed
        }
    }
    
    async loadMarketData() {
        try {
            const response = await fetch('/api/market/overview');
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.updateMarketOverview(data.market);
                }
            }
        } catch (error) {
            console.log('Market data not available - using demo data');
            // Keep demo market data displayed
        }
    }
    
    updatePortfolioMetrics(portfolio) {
        const valueElement = document.getElementById('portfolio-value');
        const returnElement = document.getElementById('portfolio-return');
        const positionsElement = document.getElementById('portfolio-positions');
        
        if (valueElement && portfolio.total_value) {
            valueElement.textContent = this.formatCurrency(portfolio.total_value);
        }
        
        if (returnElement && portfolio.total_return) {
            const returnValue = portfolio.total_return;
            returnElement.textContent = this.formatPercentage(returnValue);
            returnElement.className = `metric-value ${returnValue >= 0 ? 'status-positive' : 'status-negative'}`;
        }
        
        if (positionsElement && portfolio.positions_count) {
            positionsElement.textContent = portfolio.positions_count;
        }
    }
    
    updateAIInsights(insights) {
        // Update AI insights section with real data
        console.log('AI Insights updated:', insights);
    }
    
    updateMarketOverview(market) {
        // Update market overview with real data
        console.log('Market data updated:', market);
    }
    
    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    }
    
    formatPercentage(value) {
        const sign = value >= 0 ? '+' : '';
        return `${sign}${value.toFixed(1)}%`;
    }
    
    showErrorMessage(message) {
        // Create and show error notification
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
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
}

// Premium Feature Handlers
function handlePremiumFeature(feature) {
    // Check if user has premium access
    const userTier = getUserTier();
    
    if (userTier === 'free') {
        showUpgradeModal();
        return;
    }
    
    // Redirect to feature
    window.location.href = feature;
}

function showUpgradeModal() {
    const modal = document.getElementById('premium-modal');
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeUpgradeModal() {
    const modal = document.getElementById('premium-modal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

function getUserTier() {
    // Check user tier - could be from a data attribute or API call
    const tierElement = document.querySelector('[data-user-tier]');
    return tierElement ? tierElement.dataset.userTier : 'free';
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new ModernDashboard();
});

// Global functions for template access
window.showUpgradeModal = showUpgradeModal;
window.closeUpgradeModal = closeUpgradeModal;
window.handlePremiumFeature = handlePremiumFeature;