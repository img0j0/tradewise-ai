/**
 * Frontend Error Recovery System
 * Provides seamless error handling, retry logic, and graceful degradation
 */

class ErrorRecovery {
    constructor() {
        this.errorLog = [];
        this.retryConfigs = {
            network: { maxAttempts: 3, delay: 1000, backoffFactor: 2 },
            api: { maxAttempts: 3, delay: 2000, backoffFactor: 2 },
            authentication: { maxAttempts: 1, delay: 0, backoffFactor: 1 },
            validation: { maxAttempts: 0, delay: 0, backoffFactor: 1 },
            system: { maxAttempts: 2, delay: 1000, backoffFactor: 2 },
            realtime: { maxAttempts: 5, delay: 200, backoffFactor: 1.2 }
        };
        this.circuitBreakers = new Map();
        this.fallbackStrategies = new Map();
        this.healthChecks = new Map();
        this.isOnline = navigator.onLine;
        this.setupEventListeners();
        this.initializeFallbackStrategies();
        
        console.log('Frontend Error Recovery System initialized');
    }

    setupEventListeners() {
        // Online/offline detection
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.handleConnectionRestored();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.handleConnectionLost();
        });

        // Global error handler
        window.addEventListener('error', (event) => {
            this.handleError(event.error, {
                type: 'javascript',
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno
            });
        });

        // Unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError(event.reason, {
                type: 'promise',
                promise: event.promise
            });
        });

        // Fetch error interceptor
        this.interceptFetch();
    }

    interceptFetch() {
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            try {
                const response = await originalFetch(...args);
                
                if (!response.ok) {
                    const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
                    error.response = response;
                    throw error;
                }
                
                return response;
            } catch (error) {
                const context = {
                    url: args[0],
                    options: args[1],
                    type: 'fetch'
                };
                
                return await this.handleFetchError(error, context, originalFetch, args);
            }
        };
    }

    async handleFetchError(error, context, originalFetch, args) {
        const errorCategory = this.categorizeError(error);
        const retryConfig = this.retryConfigs[errorCategory] || this.retryConfigs.network;
        
        // Check circuit breaker
        const circuitBreaker = this.getCircuitBreaker(context.url);
        if (circuitBreaker && circuitBreaker.isOpen()) {
            return await this.useFallbackStrategy(context.url, args);
        }

        // Retry with exponential backoff
        for (let attempt = 1; attempt <= retryConfig.maxAttempts; attempt++) {
            try {
                if (attempt > 1) {
                    const delay = retryConfig.delay * Math.pow(retryConfig.backoffFactor, attempt - 1);
                    await this.sleep(delay);
                    
                    this.showRetryNotification(context.url, attempt, retryConfig.maxAttempts);
                }

                const response = await originalFetch(...args);
                
                if (response.ok) {
                    this.onSuccess(context.url);
                    return response;
                }
                
                if (attempt === retryConfig.maxAttempts) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
            } catch (retryError) {
                this.onFailure(context.url, retryError);
                
                if (attempt === retryConfig.maxAttempts) {
                    return await this.useFallbackStrategy(context.url, args);
                }
            }
        }
    }

    categorizeError(error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            return 'network';
        }
        if (error.response && error.response.status === 401) {
            return 'authentication';
        }
        if (error.response && error.response.status >= 400 && error.response.status < 500) {
            return 'validation';
        }
        if (error.response && error.response.status >= 500) {
            return 'api';
        }
        return 'system';
    }

    getCircuitBreaker(url) {
        if (!this.circuitBreakers.has(url)) {
            this.circuitBreakers.set(url, new CircuitBreaker(url));
        }
        return this.circuitBreakers.get(url);
    }

    onSuccess(url) {
        const circuitBreaker = this.getCircuitBreaker(url);
        if (circuitBreaker) {
            circuitBreaker.onSuccess();
        }
    }

    onFailure(url, error) {
        const circuitBreaker = this.getCircuitBreaker(url);
        if (circuitBreaker) {
            circuitBreaker.onFailure();
        }
        
        this.logError(error, { url, timestamp: new Date().toISOString() });
    }

    async useFallbackStrategy(url, args) {
        console.log(`Using fallback strategy for ${url}`);
        
        // Check for cached response
        const cachedResponse = await this.getCachedResponse(url);
        if (cachedResponse) {
            this.showFallbackNotification('Using cached data');
            return cachedResponse;
        }

        // Use fallback endpoint
        const fallbackUrl = this.getFallbackUrl(url);
        if (fallbackUrl) {
            try {
                const response = await fetch(fallbackUrl, args[1]);
                this.showFallbackNotification('Using backup server');
                return response;
            } catch (fallbackError) {
                console.error('Fallback strategy failed:', fallbackError);
            }
        }

        // Use mock data as last resort
        const mockData = this.getMockData(url);
        if (mockData) {
            this.showFallbackNotification('Using offline data');
            return new Response(JSON.stringify(mockData), {
                status: 200,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        // If all else fails, throw the original error
        throw new Error(`All fallback strategies failed for ${url}`);
    }

    initializeFallbackStrategies() {
        // Dashboard data fallback
        this.fallbackStrategies.set('/api/dashboard-data', {
            cache: true,
            fallbackUrl: '/api/dashboard-data-backup',
            mockData: {
                market_overview: {
                    total_value: 0,
                    daily_change: 0,
                    volatility: 'low'
                },
                recent_trades: [],
                active_alerts: [],
                performance_summary: {
                    total_return: 0,
                    win_rate: 0
                }
            }
        });

        // Stock data fallback
        this.fallbackStrategies.set('/api/stocks', {
            cache: true,
            fallbackUrl: '/api/stocks-backup',
            mockData: {
                stocks: []
            }
        });

        // Portfolio data fallback
        this.fallbackStrategies.set('/api/portfolio', {
            cache: true,
            fallbackUrl: '/api/portfolio-backup',
            mockData: {
                holdings: [],
                total_value: 0,
                cash_balance: 0
            }
        });

        // Real-time data fallback
        this.fallbackStrategies.set('/api/realtime', {
            cache: true,
            polling: true,
            mockData: {
                prices: {},
                last_updated: new Date().toISOString()
            }
        });
    }

    async getCachedResponse(url) {
        try {
            const cached = localStorage.getItem(`cache_${url}`);
            if (cached) {
                const data = JSON.parse(cached);
                const now = Date.now();
                
                // Check if cache is still valid (5 minutes)
                if (now - data.timestamp < 300000) {
                    return new Response(JSON.stringify(data.response), {
                        status: 200,
                        headers: { 'Content-Type': 'application/json' }
                    });
                }
            }
        } catch (error) {
            console.error('Error getting cached response:', error);
        }
        return null;
    }

    cacheResponse(url, response) {
        try {
            const cacheData = {
                response: response,
                timestamp: Date.now()
            };
            localStorage.setItem(`cache_${url}`, JSON.stringify(cacheData));
        } catch (error) {
            console.error('Error caching response:', error);
        }
    }

    getFallbackUrl(url) {
        const strategy = this.fallbackStrategies.get(url);
        return strategy?.fallbackUrl || null;
    }

    getMockData(url) {
        const strategy = this.fallbackStrategies.get(url);
        return strategy?.mockData || null;
    }

    handleConnectionLost() {
        this.showConnectionNotification('Connection lost. Switching to offline mode.', 'warning');
        
        // Enable offline mode features
        this.enableOfflineMode();
    }

    handleConnectionRestored() {
        this.showConnectionNotification('Connection restored. Syncing data...', 'success');
        
        // Disable offline mode and sync
        this.disableOfflineMode();
        this.syncOfflineData();
    }

    enableOfflineMode() {
        document.body.classList.add('offline-mode');
        
        // Show offline indicator
        const offlineIndicator = document.createElement('div');
        offlineIndicator.id = 'offline-indicator';
        offlineIndicator.className = 'offline-indicator';
        offlineIndicator.innerHTML = `
            <i class="fas fa-wifi-slash"></i>
            <span>Offline Mode</span>
        `;
        document.body.appendChild(offlineIndicator);
    }

    disableOfflineMode() {
        document.body.classList.remove('offline-mode');
        
        // Remove offline indicator
        const offlineIndicator = document.getElementById('offline-indicator');
        if (offlineIndicator) {
            offlineIndicator.remove();
        }
    }

    async syncOfflineData() {
        // Implement data synchronization logic
        console.log('Syncing offline data...');
        
        try {
            // Refresh dashboard data
            if (typeof refreshData === 'function') {
                await refreshData();
            }
            
            // Refresh real-time data
            if (typeof window.realtimeUpdates !== 'undefined') {
                window.realtimeUpdates.reconnect();
            }
            
            this.showConnectionNotification('Data synchronized successfully', 'success');
        } catch (error) {
            console.error('Error syncing offline data:', error);
            this.showConnectionNotification('Error syncing data', 'error');
        }
    }

    showRetryNotification(url, attempt, maxAttempts) {
        const message = `Retrying request (${attempt}/${maxAttempts})...`;
        this.showNotification(message, 'info', 3000);
    }

    showFallbackNotification(message) {
        this.showNotification(message, 'warning', 5000);
    }

    showConnectionNotification(message, type) {
        this.showNotification(message, type, 4000);
    }

    showNotification(message, type = 'info', duration = 3000) {
        // Use existing notification system if available
        if (typeof window.NotificationManager !== 'undefined') {
            window.NotificationManager.show(message, type, duration);
            return;
        }

        // Fallback notification system
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 12px 20px;
            border-radius: 4px;
            z-index: 10000;
            max-width: 300px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            animation: slideIn 0.3s ease-out;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in forwards';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }

    getNotificationColor(type) {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        return colors[type] || colors.info;
    }

    handleError(error, context) {
        const errorEvent = {
            timestamp: new Date().toISOString(),
            error: error.toString(),
            stack: error.stack,
            context: context,
            category: this.categorizeError(error)
        };

        this.logError(error, context);
        
        // Report to backend if possible
        this.reportError(errorEvent);
    }

    logError(error, context) {
        this.errorLog.push({
            timestamp: new Date().toISOString(),
            error: error.toString(),
            context: context
        });

        // Keep only last 100 errors
        if (this.errorLog.length > 100) {
            this.errorLog = this.errorLog.slice(-100);
        }

        console.error('Error logged:', error, context);
    }

    async reportError(errorEvent) {
        try {
            // Only report if online
            if (!this.isOnline) return;

            await fetch('/api/error-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(errorEvent)
            });
        } catch (error) {
            console.error('Failed to report error:', error);
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    getErrorStatistics() {
        const now = Date.now();
        const oneHourAgo = now - 3600000;
        
        const recentErrors = this.errorLog.filter(error => 
            new Date(error.timestamp).getTime() > oneHourAgo
        );

        const errorsByCategory = {};
        recentErrors.forEach(error => {
            const category = error.context?.category || 'unknown';
            errorsByCategory[category] = (errorsByCategory[category] || 0) + 1;
        });

        return {
            totalErrors: this.errorLog.length,
            recentErrors: recentErrors.length,
            errorsByCategory: errorsByCategory,
            isOnline: this.isOnline,
            circuitBreakers: Array.from(this.circuitBreakers.entries()).map(([url, breaker]) => ({
                url,
                state: breaker.state,
                failureCount: breaker.failureCount
            }))
        };
    }
}

class CircuitBreaker {
    constructor(name, failureThreshold = 5, recoveryTimeout = 60000) {
        this.name = name;
        this.failureThreshold = failureThreshold;
        this.recoveryTimeout = recoveryTimeout;
        this.failureCount = 0;
        this.lastFailureTime = null;
        this.state = 'closed'; // closed, open, half-open
    }

    isOpen() {
        if (this.state === 'open') {
            if (this.shouldAttemptReset()) {
                this.state = 'half-open';
                return false;
            }
            return true;
        }
        return false;
    }

    shouldAttemptReset() {
        if (!this.lastFailureTime) return true;
        return Date.now() - this.lastFailureTime > this.recoveryTimeout;
    }

    onSuccess() {
        this.failureCount = 0;
        this.state = 'closed';
    }

    onFailure() {
        this.failureCount++;
        this.lastFailureTime = Date.now();
        
        if (this.failureCount >= this.failureThreshold) {
            this.state = 'open';
            console.warn(`Circuit breaker opened for ${this.name}`);
        }
    }
}

// Initialize global error recovery
window.errorRecovery = new ErrorRecovery();

// Add CSS for offline mode and notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .offline-indicator {
        position: fixed;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        background: #ff6b6b;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .offline-mode {
        filter: grayscale(0.3);
    }
    
    .offline-mode .btn:not(.btn-secondary) {
        opacity: 0.7;
        pointer-events: none;
    }
    
    .error-boundary {
        padding: 20px;
        border: 1px solid #dc3545;
        border-radius: 4px;
        background: #f8d7da;
        color: #721c24;
        margin: 10px 0;
    }
    
    .retry-button {
        background: #007bff;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        margin-top: 10px;
    }
    
    .retry-button:hover {
        background: #0056b3;
    }
`;

document.head.appendChild(style);

// Export for use in other modules
window.ErrorRecovery = ErrorRecovery;
window.CircuitBreaker = CircuitBreaker;