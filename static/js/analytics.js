// Advanced Analytics and Performance Monitoring for Trading Platform

if (!window.AnalyticsManager) {
    window.AnalyticsManager = class {
    constructor() {
        this.metrics = {
            pageLoads: 0,
            tradesExecuted: 0,
            stockSearches: 0,
            aiQueries: 0,
            errorCount: 0,
            avgResponseTime: 0,
            sessionStart: Date.now(),
            performanceMetrics: []
        };
        this.initializeTracking();
    }

    initializeTracking() {
        // Track page performance
        this.trackPagePerformance();
        
        // Track user interactions
        this.trackUserInteractions();
        
        // Track API calls
        this.trackAPIPerformance();
        
        // Send metrics periodically
        setInterval(() => this.sendMetrics(), 60000); // Every minute
    }

    trackPagePerformance() {
        if (typeof performance !== 'undefined') {
            const navigation = performance.getEntriesByType('navigation')[0];
            if (navigation) {
                this.metrics.pageLoadTime = navigation.loadEventEnd - navigation.loadEventStart;
                this.metrics.domContentLoaded = navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart;
                this.metrics.firstPaint = performance.getEntriesByType('paint').find(p => p.name === 'first-paint')?.startTime || 0;
            }
        }
    }

    trackUserInteractions() {
        // Track clicks on important elements
        document.addEventListener('click', (event) => {
            const element = event.target;
            if (element.matches('[data-track]')) {
                this.trackEvent(element.dataset.track, {
                    element: element.tagName,
                    timestamp: Date.now()
                });
            }
        });

        // Track form submissions
        document.addEventListener('submit', (event) => {
            const form = event.target;
            if (form.matches('[data-track-form]')) {
                this.trackEvent('form_submit', {
                    form: form.dataset.trackForm,
                    timestamp: Date.now()
                });
            }
        });
    }

    trackAPIPerformance() {
        // Override fetch to track API calls
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const startTime = Date.now();
            const url = args[0];
            
            try {
                const response = await originalFetch(...args);
                const endTime = Date.now();
                
                this.trackAPICall(url, endTime - startTime, response.status);
                return response;
            } catch (error) {
                const endTime = Date.now();
                this.trackAPICall(url, endTime - startTime, 'error');
                throw error;
            }
        };
    }

    trackEvent(eventName, data = {}) {
        console.log('Analytics Event:', eventName, data);
        
        // Update specific metrics
        switch(eventName) {
            case 'trade_executed':
                this.metrics.tradesExecuted++;
                break;
            case 'stock_search':
                this.metrics.stockSearches++;
                break;
            case 'ai_query':
                this.metrics.aiQueries++;
                break;
            case 'error':
                this.metrics.errorCount++;
                break;
        }

        // Store the event
        if (!this.metrics.events) {
            this.metrics.events = [];
        }
        
        this.metrics.events.push({
            name: eventName,
            data: data,
            timestamp: Date.now()
        });
    }

    trackAPICall(url, duration, status) {
        if (!this.metrics.apiCalls) {
            this.metrics.apiCalls = [];
        }

        this.metrics.apiCalls.push({
            url: url,
            duration: duration,
            status: status,
            timestamp: Date.now()
        });

        // Update average response time
        const apiCalls = this.metrics.apiCalls;
        this.metrics.avgResponseTime = apiCalls.reduce((sum, call) => sum + call.duration, 0) / apiCalls.length;
    }

    trackError(error, context = {}) {
        this.trackEvent('error', {
            message: error.message,
            stack: error.stack,
            context: context,
            timestamp: Date.now()
        });
    }

    getPerformanceMetrics() {
        return {
            ...this.metrics,
            sessionDuration: Date.now() - this.metrics.sessionStart,
            timestamp: Date.now()
        };
    }

    sendMetrics() {
        const metrics = this.getPerformanceMetrics();
        
        // Send to analytics endpoint (in a real app, this would go to your analytics service)
        fetch('/api/analytics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(metrics)
        }).catch(err => {
            console.warn('Failed to send analytics:', err);
        });
    }

    // Real-time performance monitoring
    startPerformanceMonitoring() {
        setInterval(() => {
            const memoryInfo = performance.memory;
            if (memoryInfo) {
                this.trackEvent('memory_usage', {
                    usedJSHeapSize: memoryInfo.usedJSHeapSize,
                    totalJSHeapSize: memoryInfo.totalJSHeapSize,
                    jsHeapSizeLimit: memoryInfo.jsHeapSizeLimit
                });
            }
        }, 30000); // Every 30 seconds
    }
}

// Portfolio Performance Calculator
class PortfolioAnalytics {
    constructor() {
        this.performanceData = [];
    }

    calculateReturns(portfolio) {
        let totalInvestment = 0;
        let currentValue = 0;
        let dailyChange = 0;
        let positions = [];

        portfolio.forEach(position => {
            const invested = position.quantity * position.avg_price;
            const current = position.quantity * position.current_price;
            const change = current - invested;
            const changePercent = (change / invested) * 100;

            totalInvestment += invested;
            currentValue += current;
            dailyChange += position.quantity * (position.current_price - position.prev_close);

            positions.push({
                symbol: position.symbol,
                quantity: position.quantity,
                avgPrice: position.avg_price,
                currentPrice: position.current_price,
                invested: invested,
                currentValue: current,
                unrealizedPnL: change,
                unrealizedPnLPercent: changePercent,
                dayChange: position.quantity * (position.current_price - position.prev_close),
                dayChangePercent: ((position.current_price - position.prev_close) / position.prev_close) * 100
            });
        });

        const totalReturn = currentValue - totalInvestment;
        const totalReturnPercent = totalInvestment > 0 ? (totalReturn / totalInvestment) * 100 : 0;
        const dailyChangePercent = totalInvestment > 0 ? (dailyChange / totalInvestment) * 100 : 0;

        return {
            totalInvestment,
            currentValue,
            totalReturn,
            totalReturnPercent,
            dailyChange,
            dailyChangePercent,
            positions
        };
    }

    calculateRiskMetrics(portfolio) {
        const returns = this.calculateReturns(portfolio);
        const positions = returns.positions;
        
        // Calculate portfolio volatility (simplified)
        const weights = positions.map(pos => pos.currentValue / returns.currentValue);
        const volatilities = positions.map(pos => this.estimateVolatility(pos.symbol));
        
        // Weighted average volatility
        const portfolioVolatility = weights.reduce((sum, weight, index) => {
            return sum + (weight * volatilities[index]);
        }, 0);

        // Risk-adjusted return (Sharpe ratio approximation)
        const riskFreeRate = 0.02; // 2% annual risk-free rate
        const excessReturn = (returns.totalReturnPercent / 100) - riskFreeRate;
        const sharpeRatio = portfolioVolatility > 0 ? excessReturn / portfolioVolatility : 0;

        return {
            volatility: portfolioVolatility,
            sharpeRatio: sharpeRatio,
            riskLevel: this.getRiskLevel(portfolioVolatility),
            diversificationScore: this.calculateDiversification(positions)
        };
    }

    estimateVolatility(symbol) {
        // In a real implementation, this would use historical price data
        // For now, return a reasonable estimate based on symbol characteristics
        const volatilityMap = {
            'AAPL': 0.25,
            'GOOGL': 0.30,
            'MSFT': 0.22,
            'AMZN': 0.35,
            'TSLA': 0.60,
            'NVDA': 0.45,
            'SPY': 0.15,
            'QQQ': 0.20
        };
        
        return volatilityMap[symbol] || 0.30; // Default 30% volatility
    }

    getRiskLevel(volatility) {
        if (volatility < 0.15) return 'Low';
        if (volatility < 0.25) return 'Moderate';
        if (volatility < 0.35) return 'High';
        return 'Very High';
    }

    calculateDiversification(positions) {
        if (positions.length <= 1) return 0;
        
        // Simple diversification score based on number of positions and concentration
        const concentration = Math.max(...positions.map(p => p.currentValue)) / 
                            positions.reduce((sum, p) => sum + p.currentValue, 0);
        
        const positionScore = Math.min(positions.length / 10, 1); // Max score at 10+ positions
        const concentrationScore = 1 - concentration; // Lower concentration = higher score
        
        return (positionScore + concentrationScore) / 2;
    }
    }
}

// Initialize analytics
if (!window.analyticsManager) {
    window.analyticsManager = new AnalyticsManager();
}

// Start performance monitoring
if (window.analyticsManager) {
    window.analyticsManager.startPerformanceMonitoring();
}