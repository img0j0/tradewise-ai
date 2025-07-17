// Real-time price updates handler
if (!window.RealtimeUpdates) {
    window.RealtimeUpdates = class {
    constructor() {
        this.socket = null;
        this.subscribedSymbols = new Set();
        this.priceUpdateCallbacks = new Map();
        this.connectionRetries = 0;
        this.maxRetries = 5;
        this.initialize();
    }

    initialize() {
        // Connect to WebSocket
        this.socket = io();
        
        // Set up event handlers
        this.socket.on('connect', () => {
            console.log('Connected to real-time updates');
            this.connectionRetries = 0;
            
            // Re-subscribe to all symbols
            this.subscribedSymbols.forEach(symbol => {
                this.socket.emit('subscribe_symbol', { symbol: symbol });
            });
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from real-time updates');
            this.handleReconnect();
        });

        this.socket.on('price_update', (data) => {
            this.handlePriceUpdate(data);
        });

        this.socket.on('subscription_confirmed', (data) => {
            console.log(`Subscribed to ${data.symbol}`);
        });
    }

    handleReconnect() {
        if (this.connectionRetries < this.maxRetries) {
            this.connectionRetries++;
            console.log(`Attempting to reconnect... (${this.connectionRetries}/${this.maxRetries})`);
            setTimeout(() => {
                this.socket.connect();
            }, 2000 * this.connectionRetries);
        }
    }

    subscribe(symbol, callback) {
        // Add to subscribed symbols
        this.subscribedSymbols.add(symbol);
        
        // Store callback
        if (!this.priceUpdateCallbacks.has(symbol)) {
            this.priceUpdateCallbacks.set(symbol, new Set());
        }
        this.priceUpdateCallbacks.get(symbol).add(callback);
        
        // Send subscription request
        if (this.socket && this.socket.connected) {
            this.socket.emit('subscribe_symbol', { symbol: symbol });
        }
    }

    unsubscribe(symbol, callback) {
        // Remove callback
        const callbacks = this.priceUpdateCallbacks.get(symbol);
        if (callbacks) {
            callbacks.delete(callback);
            
            // If no more callbacks, unsubscribe completely
            if (callbacks.size === 0) {
                this.subscribedSymbols.delete(symbol);
                this.priceUpdateCallbacks.delete(symbol);
                
                if (this.socket && this.socket.connected) {
                    this.socket.emit('unsubscribe_symbol', { symbol: symbol });
                }
            }
        }
    }

    handlePriceUpdate(data) {
        const updates = data.updates;
        
        Object.keys(updates).forEach(symbol => {
            const priceData = updates[symbol];
            
            // Update UI elements
            this.updatePriceDisplay(symbol, priceData);
            
            // Call registered callbacks
            const callbacks = this.priceUpdateCallbacks.get(symbol);
            if (callbacks) {
                callbacks.forEach(callback => {
                    try {
                        callback(priceData);
                    } catch (error) {
                        console.error('Error in price update callback:', error);
                    }
                });
            }
        });
    }

    updatePriceDisplay(symbol, data) {
        // Update price elements
        const priceElements = document.querySelectorAll(`[data-symbol="${symbol}"] .price`);
        priceElements.forEach(element => {
            const oldPrice = parseFloat(element.textContent.replace('$', ''));
            const newPrice = data.price;
            
            // Update price
            element.textContent = `$${newPrice.toFixed(2)}`;
            
            // Add flash effect
            if (newPrice > oldPrice) {
                element.classList.add('price-up-flash');
                setTimeout(() => element.classList.remove('price-up-flash'), 1000);
            } else if (newPrice < oldPrice) {
                element.classList.add('price-down-flash');
                setTimeout(() => element.classList.remove('price-down-flash'), 1000);
            }
        });
        
        // Update change elements
        const changeElements = document.querySelectorAll(`[data-symbol="${symbol}"] .change`);
        changeElements.forEach(element => {
            const changeClass = data.change >= 0 ? 'text-success' : 'text-danger';
            const changeSign = data.change >= 0 ? '+' : '';
            element.className = `change ${changeClass}`;
            element.textContent = `${changeSign}${data.change.toFixed(2)} (${changeSign}${data.change_percent.toFixed(2)}%)`;
        });
        
        // Update portfolio value if needed
        if (window.updatePortfolioValue) {
            window.updatePortfolioValue();
        }
    }

    // Subscribe to all visible stocks
    subscribeToVisibleStocks() {
        const stockElements = document.querySelectorAll('[data-symbol]');
        stockElements.forEach(element => {
            const symbol = element.getAttribute('data-symbol');
            if (symbol && !this.subscribedSymbols.has(symbol)) {
                this.subscribe(symbol, (data) => {
                    // Optional: Add custom handling per stock
                });
            }
        });
    }

    // Clean up subscriptions for hidden stocks
    cleanupSubscriptions() {
        const visibleSymbols = new Set();
        const stockElements = document.querySelectorAll('[data-symbol]');
        stockElements.forEach(element => {
            visibleSymbols.add(element.getAttribute('data-symbol'));
        });
        
        // Unsubscribe from symbols no longer visible
        this.subscribedSymbols.forEach(symbol => {
            if (!visibleSymbols.has(symbol)) {
                this.unsubscribe(symbol, () => {});
            }
        });
    }
}

// Initialize real-time updates
if (!window.realtimeUpdates) {
    window.realtimeUpdates = new RealtimeUpdates();
}

// Add CSS for price flash effects
const style = document.createElement('style');
style.textContent = `
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
document.head.appendChild(style);