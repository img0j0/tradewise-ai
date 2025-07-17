// Real-time updates service for the trading platform

class RealtimeUpdates {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        this.subscribedSymbols = new Set();
        this.priceUpdateCallbacks = new Map();
        
        this.init();
    }

    init() {
        if (typeof io !== 'undefined') {
            this.connect();
        } else {
            console.warn('Socket.IO not available, real-time updates disabled');
        }
    }

    connect() {
        try {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('Connected to real-time updates');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000;
                
                // Re-subscribe to all symbols
                this.subscribedSymbols.forEach(symbol => {
                    this.socket.emit('subscribe', symbol);
                });
            });

            this.socket.on('disconnect', () => {
                console.log('Disconnected from real-time updates');
                this.isConnected = false;
                this.scheduleReconnect();
            });

            this.socket.on('price_update', (data) => {
                this.handlePriceUpdate(data);
            });

            this.socket.on('connect_error', (error) => {
                console.error('Connection error:', error);
                this.scheduleReconnect();
            });

        } catch (error) {
            console.error('Failed to initialize Socket.IO:', error);
        }
    }

    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
            
            // Exponential backoff
            this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
        } else {
            console.error('Max reconnection attempts reached');
        }
    }

    subscribe(symbol, callback) {
        if (!symbol) return;
        
        this.subscribedSymbols.add(symbol);
        
        if (callback) {
            if (!this.priceUpdateCallbacks.has(symbol)) {
                this.priceUpdateCallbacks.set(symbol, []);
            }
            this.priceUpdateCallbacks.get(symbol).push(callback);
        }
        
        if (this.isConnected && this.socket) {
            this.socket.emit('subscribe', symbol);
        }
    }

    unsubscribe(symbol, callback) {
        if (!symbol) return;
        
        this.subscribedSymbols.delete(symbol);
        
        if (callback) {
            const callbacks = this.priceUpdateCallbacks.get(symbol);
            if (callbacks) {
                const index = callbacks.indexOf(callback);
                if (index > -1) {
                    callbacks.splice(index, 1);
                }
                if (callbacks.length === 0) {
                    this.priceUpdateCallbacks.delete(symbol);
                }
            }
        } else {
            this.priceUpdateCallbacks.delete(symbol);
        }
        
        if (this.isConnected && this.socket) {
            this.socket.emit('unsubscribe', symbol);
        }
    }

    handlePriceUpdate(data) {
        const { symbol, price, change, changePercent } = data;
        
        // Update price displays
        this.updatePriceDisplay(symbol, price, change, changePercent);
        
        // Call registered callbacks
        const callbacks = this.priceUpdateCallbacks.get(symbol);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Error in price update callback:', error);
                }
            });
        }
    }

    updatePriceDisplay(symbol, price, change, changePercent) {
        // Update main price displays
        const priceElements = document.querySelectorAll(`[data-symbol="${symbol}"] .stock-price`);
        priceElements.forEach(element => {
            const oldPrice = parseFloat(element.textContent.replace('$', ''));
            element.textContent = `$${price.toFixed(2)}`;
            
            // Add flash animation
            if (oldPrice !== price) {
                element.classList.remove('price-up-flash', 'price-down-flash');
                element.classList.add(price > oldPrice ? 'price-up-flash' : 'price-down-flash');
            }
        });

        // Update change displays
        const changeElements = document.querySelectorAll(`[data-symbol="${symbol}"] .price-change`);
        changeElements.forEach(element => {
            const changeClass = change >= 0 ? 'text-success' : 'text-danger';
            const changeSymbol = change >= 0 ? '+' : '';
            element.className = `price-change ${changeClass}`;
            element.textContent = `${changeSymbol}${change.toFixed(2)} (${changePercent.toFixed(2)}%)`;
        });

        // Update portfolio values if applicable
        this.updatePortfolioValues(symbol, price);
    }

    updatePortfolioValues(symbol, price) {
        const portfolioElements = document.querySelectorAll(`[data-portfolio-symbol="${symbol}"]`);
        portfolioElements.forEach(element => {
            const shares = parseFloat(element.dataset.shares || 0);
            const value = shares * price;
            
            const valueElement = element.querySelector('.portfolio-value');
            if (valueElement) {
                valueElement.textContent = `$${value.toFixed(2)}`;
            }
        });
    }

    // Auto-manage subscriptions based on visible elements
    autoManageSubscriptions() {
        // Get all visible stock symbols
        const visibleSymbols = new Set();
        
        // Check dashboard stock cards
        document.querySelectorAll('.stock-card[data-symbol]').forEach(card => {
            if (this.isElementVisible(card)) {
                visibleSymbols.add(card.dataset.symbol);
            }
        });
        
        // Check portfolio items
        document.querySelectorAll('[data-portfolio-symbol]').forEach(item => {
            if (this.isElementVisible(item)) {
                visibleSymbols.add(item.dataset.portfolioSymbol);
            }
        });
        
        // Subscribe to new symbols
        visibleSymbols.forEach(symbol => {
            if (!this.subscribedSymbols.has(symbol)) {
                this.subscribe(symbol);
            }
        });
        
        // Unsubscribe from symbols no longer visible
        this.subscribedSymbols.forEach(symbol => {
            if (!visibleSymbols.has(symbol)) {
                this.unsubscribe(symbol);
            }
        });
    }

    isElementVisible(element) {
        if (!element) return false;
        
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
}

// Initialize real-time updates
if (!window.realtimeUpdates) {
    window.realtimeUpdates = new RealtimeUpdates();
}

// Auto-manage subscriptions when page content changes
document.addEventListener('DOMContentLoaded', () => {
    if (window.realtimeUpdates) {
        window.realtimeUpdates.autoManageSubscriptions();
    }
});

// Update subscriptions when scrolling or resizing
if (!window.subscriptionUpdateTimeout) {
    window.subscriptionUpdateTimeout = null;
}
function scheduleSubscriptionUpdate() {
    clearTimeout(window.subscriptionUpdateTimeout);
    window.subscriptionUpdateTimeout = setTimeout(() => {
        if (window.realtimeUpdates) {
            window.realtimeUpdates.autoManageSubscriptions();
        }
    }, 500);
}

window.addEventListener('scroll', scheduleSubscriptionUpdate);
window.addEventListener('resize', scheduleSubscriptionUpdate);

// Add CSS for price flash effects
const realtimeStyle = document.createElement('style');
realtimeStyle.textContent = `
    .price-up-flash {
        animation: flash-green 1s ease-out;
    }
    
    .price-down-flash {
        animation: flash-red 1s ease-out;
    }
    
    @keyframes flash-green {
        0% { background-color: rgba(40, 167, 69, 0.3); }
        100% { background-color: transparent; }
    }
    
    @keyframes flash-red {
        0% { background-color: rgba(220, 53, 69, 0.3); }
        100% { background-color: transparent; }
    }
`;
document.head.appendChild(realtimeStyle);