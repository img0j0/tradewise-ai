/**
 * Modern Dashboard JavaScript
 * Handles dashboard interactions, charts, and user engagement
 */

// Global variables
let portfolioChart = null;
let marketChart = null;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadDashboardData();
    setupEventListeners();
});

// Initialize dashboard components
function initializeDashboard() {
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializePortfolioChart();
        initializeMarketChart();
    }
    
    // Setup dark mode
    initializeDarkMode();
    
    // Setup sidebar collapse
    setupSidebarToggle();
}

// Portfolio performance chart
function initializePortfolioChart() {
    const ctx = document.getElementById('portfolio-chart');
    if (!ctx) return;
    
    portfolioChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Portfolio Value',
                data: [10000, 10500, 10200, 11000, 10800, 11500],
                borderColor: '#1e40af',
                backgroundColor: 'rgba(30, 64, 175, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
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
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Market overview chart
function initializeMarketChart() {
    const ctx = document.getElementById('market-chart');
    if (!ctx) return;
    
    marketChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer'],
            datasets: [{
                data: [35, 20, 18, 12, 15],
                backgroundColor: [
                    '#1e40af',
                    '#7c3aed', 
                    '#059669',
                    '#dc2626',
                    '#d97706'
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
                        usePointStyle: true,
                        padding: 15
                    }
                }
            }
        }
    });
}

// Load dashboard data from API
async function loadDashboardData() {
    try {
        // Load portfolio data
        const portfolioResponse = await fetch('/api/portfolio/summary');
        if (portfolioResponse.ok) {
            const portfolioData = await portfolioResponse.json();
            updatePortfolioCard(portfolioData);
        }
        
        // Load market data
        const marketResponse = await fetch('/api/market/overview');
        if (marketResponse.ok) {
            const marketData = await marketResponse.json();
            updateMarketCard(marketData);
        }
        
        // Load recent analyses
        const analysesResponse = await fetch('/api/analyses/recent');
        if (analysesResponse.ok) {
            const analysesData = await analysesResponse.json();
            updateRecentAnalyses(analysesData);
        }
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Update portfolio card with real data
function updatePortfolioCard(data) {
    const valueElement = document.getElementById('portfolio-value');
    const changeElement = document.getElementById('portfolio-change');
    
    if (valueElement && data.totalValue) {
        valueElement.textContent = `$${data.totalValue.toLocaleString()}`;
    }
    
    if (changeElement && data.dayChange) {
        const isPositive = data.dayChange >= 0;
        changeElement.textContent = `${isPositive ? '+' : ''}${data.dayChange.toFixed(2)}%`;
        changeElement.className = `font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`;
    }
}

// Update market card with real data
function updateMarketCard(data) {
    const spxElement = document.getElementById('spx-value');
    const spxChangeElement = document.getElementById('spx-change');
    
    if (spxElement && data.spx) {
        spxElement.textContent = data.spx.value;
    }
    
    if (spxChangeElement && data.spx) {
        const isPositive = data.spx.change >= 0;
        spxChangeElement.innerHTML = `
            <i class="fas fa-arrow-${isPositive ? 'up' : 'down'} mr-1"></i>
            ${isPositive ? '+' : ''}${data.spx.change}%
        `;
        spxChangeElement.className = `font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`;
    }
}

// Update recent analyses section
function updateRecentAnalyses(data) {
    const container = document.getElementById('recent-analyses');
    if (!container || !data.analyses) return;
    
    container.innerHTML = data.analyses.map(analysis => `
        <div class="flex items-start gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer" 
             onclick="viewAnalysis('${analysis.symbol}')">
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <i class="fas fa-chart-line text-blue-600"></i>
            </div>
            <div class="flex-1">
                <div class="font-semibold text-gray-800 mb-1">${analysis.symbol} - ${analysis.company}</div>
                <p class="text-gray-600 text-sm mb-2">${analysis.summary}</p>
                <div class="text-xs text-gray-500">${formatDate(analysis.timestamp)}</div>
            </div>
            <div class="text-right">
                <div class="text-sm font-medium ${analysis.recommendation === 'BUY' ? 'text-green-600' : 
                    analysis.recommendation === 'SELL' ? 'text-red-600' : 'text-yellow-600'}">
                    ${analysis.recommendation}
                </div>
                <div class="text-xs text-gray-500">${analysis.confidence}% confidence</div>
            </div>
        </div>
    `).join('');
}

// Setup event listeners
function setupEventListeners() {
    // Quick action buttons
    document.getElementById('quick-search')?.addEventListener('click', () => {
        window.location.href = '/search';
    });
    
    document.getElementById('quick-backtest')?.addEventListener('click', () => {
        window.location.href = '/backtest';
    });
    
    document.getElementById('quick-portfolio')?.addEventListener('click', () => {
        window.location.href = '/portfolio';
    });
    
    // Upgrade modal
    document.getElementById('show-upgrade')?.addEventListener('click', showUpgradeModal);
    document.getElementById('close-upgrade')?.addEventListener('click', closeUpgradeModal);
}

// Dark mode functionality
function initializeDarkMode() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const isDark = localStorage.getItem('darkMode') === 'true';
    
    if (isDark) {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
    
    darkModeToggle?.addEventListener('click', toggleDarkMode);
}

function toggleDarkMode() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('darkMode', newTheme === 'dark');
}

// Sidebar toggle functionality
function setupSidebarToggle() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    
    sidebarToggle?.addEventListener('click', () => {
        sidebar?.classList.toggle('collapsed');
    });
    
    // Auto-collapse on mobile
    if (window.innerWidth <= 768) {
        sidebar?.classList.add('collapsed');
    }
}

// Upgrade modal functions
function showUpgradeModal() {
    const modal = document.getElementById('upgrade-modal');
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function closeUpgradeModal() {
    const modal = document.getElementById('upgrade-modal');
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

// Navigate to analysis
function viewAnalysis(symbol) {
    window.location.href = `/search?q=${symbol}`;
}

// Utility functions
function formatDate(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
}

// Search functionality
function performQuickSearch() {
    const searchInput = document.getElementById('global-search-input');
    if (searchInput && searchInput.value.trim()) {
        window.location.href = `/search?q=${encodeURIComponent(searchInput.value.trim())}`;
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search focus
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('global-search-input');
        searchInput?.focus();
    }
    
    // Esc to close modals
    if (e.key === 'Escape') {
        closeUpgradeModal();
    }
});

// Export for external use
window.DashboardManager = {
    showUpgradeModal,
    closeUpgradeModal,
    performQuickSearch,
    toggleDarkMode
};