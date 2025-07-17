// Advanced charting functionality with professional features
class AdvancedChart {
    constructor() {
        this.currentSymbol = null;
        this.charts = {};
        this.indicators = {};
        this.chartData = null;
        this.isLoading = false;
        this.darkMode = true;
        this.initialize();
    }

    initialize() {
        // Set up event listeners
        document.getElementById('chart-period').addEventListener('change', () => this.updateChart());
        document.getElementById('chart-type').addEventListener('change', () => this.updateChart());
        
        // Indicator toggles
        ['sma', 'sma50', 'ema', 'ema26', 'bb', 'volume', 'rsi', 'macd', 'vwap', 'stoch', 'support', 'resistance', 'atr', 'mfi'].forEach(indicator => {
            const element = document.getElementById(`indicator-${indicator}`);
            if (element) {
                element.addEventListener('change', () => this.updateChart());
            }
        });

        // Drawing tools
        this.setupDrawingTools();
        
        // Keyboard shortcuts
        this.setupKeyboardShortcuts();
    }

    setupDrawingTools() {
        // Enhanced drawing tools with professional features
        this.drawingMode = false;
        this.drawings = [];
        this.currentDrawingTool = null;
        this.isDrawing = false;
        this.startPoint = null;
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 's':
                        e.preventDefault();
                        this.exportChart();
                        break;
                    case 'r':
                        e.preventDefault();
                        this.resetChart();
                        break;
                }
            }
        });
    }

    exportChart() {
        if (!this.charts.price) return;
        
        const canvas = document.getElementById('advanced-price-chart');
        const link = document.createElement('a');
        link.download = `${this.currentSymbol}_chart_${new Date().toISOString().split('T')[0]}.png`;
        link.href = canvas.toDataURL();
        link.click();
    }
    
    resetChart() {
        this.drawings = [];
        this.currentDrawingTool = null;
        this.isDrawing = false;
        
        // Reset all indicators
        ['sma', 'sma50', 'ema', 'ema26', 'bb', 'volume', 'rsi', 'macd', 'vwap', 'stoch', 'support', 'resistance', 'atr', 'mfi'].forEach(indicator => {
            const element = document.getElementById(`indicator-${indicator}`);
            if (element) {
                element.checked = ['volume', 'rsi', 'macd'].includes(indicator);
            }
        });
        
        // Reset chart period and type
        document.getElementById('chart-period').value = '1mo';
        document.getElementById('chart-type').value = 'line';
        
        this.loadChartData();
    }

    async showChart(symbol) {
        this.currentSymbol = symbol;
        
        // Update modal header
        document.getElementById('chart-symbol').textContent = symbol;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('advanced-chart-modal'));
        modal.show();
        
        // Load chart data
        await this.loadChartData();
    }

    async loadChartData() {
        if (this.isLoading) return;
        
        try {
            this.isLoading = true;
            this.showLoadingState();
            
            const period = document.getElementById('chart-period').value;
            const response = await fetch(`/api/technical-indicators/${this.currentSymbol}?period=${period}`);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.chartData = data;
            this.updateChart();
            this.updateLevels();
            this.updateStockInfo();
            
        } catch (error) {
            console.error('Error loading chart data:', error);
            this.showError('Failed to load chart data. Please try again.');
        } finally {
            this.isLoading = false;
            this.hideLoadingState();
        }
    }

    showLoadingState() {
        const loadingHtml = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div class="mt-2">Loading chart data...</div>
            </div>
        `;
        document.querySelector('.chart-container').innerHTML = loadingHtml;
    }

    hideLoadingState() {
        document.querySelector('.chart-container').innerHTML = '<canvas id="advanced-price-chart"></canvas>';
    }

    showError(message) {
        const errorHtml = `
            <div class="alert alert-danger text-center" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
                <button class="btn btn-sm btn-outline-danger ms-2" onclick="window.advancedChart.loadChartData()">
                    Retry
                </button>
            </div>
        `;
        document.querySelector('.chart-container').innerHTML = errorHtml;
    }

    updateStockInfo() {
        if (!this.chartData || !this.chartData.prices.length) return;
        
        const latestPrice = this.chartData.prices[this.chartData.prices.length - 1];
        const previousPrice = this.chartData.prices[this.chartData.prices.length - 2];
        const change = latestPrice - previousPrice;
        const changePercent = (change / previousPrice) * 100;
        
        document.getElementById('chart-price').textContent = `$${latestPrice.toFixed(2)}`;
        
        const changeElement = document.getElementById('chart-change');
        changeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)} (${changePercent.toFixed(2)}%)`;
        changeElement.className = `badge ${change >= 0 ? 'bg-success' : 'bg-danger'}`;
        
        // Update market info panel
        if (this.chartData.market_data) {
            const marketData = this.chartData.market_data;
            
            document.getElementById('chart-volume').textContent = this.formatVolume(marketData.current_volume);
            document.getElementById('chart-high').textContent = `$${marketData.daily_high.toFixed(2)}`;
            document.getElementById('chart-low').textContent = `$${marketData.daily_low.toFixed(2)}`;
            document.getElementById('chart-avg-volume').textContent = this.formatVolume(marketData.avg_volume);
        }
    }

    formatVolume(volume) {
        if (volume >= 1000000) {
            return `${(volume / 1000000).toFixed(1)}M`;
        } else if (volume >= 1000) {
            return `${(volume / 1000).toFixed(1)}K`;
        }
        return volume.toLocaleString();
    }

    updateChart() {
        if (!this.chartData) return;
        
        const chartType = document.getElementById('chart-type').value;
        
        // Update main price chart
        this.updatePriceChart(chartType);
        
        // Update RSI chart
        this.updateRSIChart();
        
        // Update MACD chart
        this.updateMACDChart();
    }

    updatePriceChart(chartType) {
        const ctx = document.getElementById('advanced-price-chart').getContext('2d');
        
        // Destroy existing chart
        if (this.charts.price) {
            this.charts.price.destroy();
        }
        
        const datasets = [];
        
        // Main price dataset with improved styling
        if (chartType === 'candlestick') {
            // Create OHLC candlestick data
            const candlestickData = this.createCandlestickData();
            datasets.push({
                label: 'Price',
                data: candlestickData,
                type: 'line',
                borderColor: '#00d4aa',
                backgroundColor: 'rgba(0, 212, 170, 0.1)',
                borderWidth: 1.5,
                pointRadius: 0,
                pointHoverRadius: 4,
                tension: 0.1
            });
        } else {
            const gradientFill = this.createGradient(ctx, chartType === 'area');
            datasets.push({
                label: 'Price',
                data: this.chartData.prices,
                type: chartType === 'bar' ? 'bar' : 'line',
                borderColor: '#00d4aa',
                backgroundColor: gradientFill,
                borderWidth: chartType === 'line' ? 2 : 1,
                pointRadius: chartType === 'line' ? 0 : 3,
                pointHoverRadius: 6,
                pointBackgroundColor: '#00d4aa',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                fill: chartType === 'area',
                tension: 0.4
            });
        }
        
        // Add enhanced indicators
        if (document.getElementById('indicator-sma').checked && this.chartData.sma_20) {
            datasets.push({
                label: 'SMA 20',
                data: this.padIndicator(this.chartData.sma_20, 19),
                type: 'line',
                borderColor: '#ffce56',
                borderWidth: 1.5,
                pointRadius: 0,
                fill: false,
                borderDash: [8, 4]
            });
        }
        
        if (document.getElementById('indicator-ema').checked && this.chartData.ema_12) {
            datasets.push({
                label: 'EMA 12',
                data: this.padIndicator(this.chartData.ema_12, 11),
                type: 'line',
                borderColor: '#ff6384',
                borderWidth: 1.5,
                pointRadius: 0,
                fill: false,
                borderDash: [4, 4]
            });
        }
        
        if (document.getElementById('indicator-bb').checked && this.chartData.bollinger) {
            datasets.push({
                label: 'BB Upper',
                data: this.padIndicator(this.chartData.bollinger.upper, 19),
                type: 'line',
                borderColor: 'rgba(153, 102, 255, 0.8)',
                borderWidth: 1,
                pointRadius: 0,
                fill: '+1',
                backgroundColor: 'rgba(153, 102, 255, 0.1)',
                borderDash: [5, 5]
            });
            
            datasets.push({
                label: 'BB Lower',
                data: this.padIndicator(this.chartData.bollinger.lower, 19),
                type: 'line',
                borderColor: 'rgba(153, 102, 255, 0.8)',
                borderWidth: 1,
                pointRadius: 0,
                fill: false,
                borderDash: [5, 5]
            });
        }

        // Add VWAP if available
        if (document.getElementById('indicator-vwap')?.checked && this.chartData.vwap) {
            datasets.push({
                label: 'VWAP',
                data: this.chartData.vwap,
                type: 'line',
                borderColor: '#e67e22',
                borderWidth: 2,
                pointRadius: 0,
                fill: false,
                borderDash: [10, 5]
            });
        }
        
        // Add SMA 50 if available
        if (document.getElementById('indicator-sma50')?.checked && this.chartData.sma_50) {
            datasets.push({
                label: 'SMA 50',
                data: this.padIndicator(this.chartData.sma_50, 49),
                type: 'line',
                borderColor: '#9966ff',
                borderWidth: 2,
                pointRadius: 0,
                fill: false,
                borderDash: [12, 6]
            });
        }
        
        // Add EMA 26 if available
        if (document.getElementById('indicator-ema26')?.checked && this.chartData.ema_26) {
            datasets.push({
                label: 'EMA 26',
                data: this.padIndicator(this.chartData.ema_26, 25),
                type: 'line',
                borderColor: '#34495e',
                borderWidth: 1.5,
                pointRadius: 0,
                fill: false,
                borderDash: [6, 3]
            });
        }
        
        // Add support and resistance levels
        if (this.chartData.support_resistance) {
            this.chartData.support_resistance.support.forEach((level, index) => {
                datasets.push({
                    label: `Support ${index + 1}`,
                    data: Array(this.chartData.prices.length).fill(level),
                    type: 'line',
                    borderColor: '#27ae60',
                    backgroundColor: 'rgba(39, 174, 96, 0.1)',
                    borderWidth: 1,
                    pointRadius: 0,
                    fill: false,
                    borderDash: [2, 8]
                });
            });
            
            this.chartData.support_resistance.resistance.forEach((level, index) => {
                datasets.push({
                    label: `Resistance ${index + 1}`,
                    data: Array(this.chartData.prices.length).fill(level),
                    type: 'line',
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    borderWidth: 1,
                    pointRadius: 0,
                    fill: false,
                    borderDash: [2, 8]
                });
            });
        }
        
        // Create enhanced chart with professional styling
        this.charts.price = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.chartData.dates,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                },
                interaction: {
                    mode: 'index',
                    intersect: false,
                    axis: 'x'
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#ffffff',
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'line',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#00d4aa',
                        borderWidth: 1,
                        cornerRadius: 8,
                        padding: 12,
                        displayColors: true,
                        callbacks: {
                            title: function(context) {
                                return `Date: ${context[0].label}`;
                            },
                            label: function(context) {
                                if (context.datasetIndex === 0) {
                                    return `Price: $${context.parsed.y.toFixed(2)}`;
                                }
                                return `${context.dataset.label}: $${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)',
                            lineWidth: 0.5
                        },
                        ticks: {
                            color: '#ffffff',
                            maxTicksLimit: 10,
                            font: {
                                size: 10
                            }
                        }
                    },
                    y: {
                        display: true,
                        position: 'right',
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)',
                            lineWidth: 0.5
                        },
                        ticks: {
                            color: '#ffffff',
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            },
                            font: {
                                size: 10
                            }
                        }
                    }
                },
                elements: {
                    point: {
                        hoverRadius: 8
                    }
                }
            }
        });
        
        // Add volume bars if enabled
        if (document.getElementById('indicator-volume').checked) {
            this.addVolumeOverlay();
        }
    }

    updateRSIChart() {
        const ctx = document.getElementById('rsi-chart').getContext('2d');
        
        if (this.charts.rsi) {
            this.charts.rsi.destroy();
        }
        
        if (!this.chartData.rsi || this.chartData.rsi.length === 0) return;
        
        const rsiData = this.padIndicator(this.chartData.rsi, this.chartData.prices.length - this.chartData.rsi.length);
        
        this.charts.rsi = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.chartData.dates,
                datasets: [{
                    label: 'RSI',
                    data: rsiData,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    annotation: {
                        annotations: {
                            overbought: {
                                type: 'line',
                                yMin: 70,
                                yMax: 70,
                                borderColor: 'rgba(255, 99, 132, 0.5)',
                                borderWidth: 1,
                                borderDash: [5, 5]
                            },
                            oversold: {
                                type: 'line',
                                yMin: 30,
                                yMax: 30,
                                borderColor: 'rgba(75, 192, 192, 0.5)',
                                borderWidth: 1,
                                borderDash: [5, 5]
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: false
                    },
                    y: {
                        display: true,
                        position: 'right',
                        min: 0,
                        max: 100,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });
    }

    updateMACDChart() {
        const ctx = document.getElementById('macd-chart').getContext('2d');
        
        if (this.charts.macd) {
            this.charts.macd.destroy();
        }
        
        if (!this.chartData.macd || !this.chartData.macd.macd || this.chartData.macd.macd.length === 0) return;
        
        const macdData = this.padIndicator(this.chartData.macd.macd, this.chartData.prices.length - this.chartData.macd.macd.length);
        const signalData = this.padIndicator(this.chartData.macd.signal, this.chartData.prices.length - this.chartData.macd.signal.length);
        const histogramData = this.padIndicator(this.chartData.macd.histogram, this.chartData.prices.length - this.chartData.macd.histogram.length);
        
        this.charts.macd = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.chartData.dates,
                datasets: [{
                    label: 'MACD',
                    data: macdData,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false
                }, {
                    label: 'Signal',
                    data: signalData,
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false
                }, {
                    label: 'Histogram',
                    data: histogramData,
                    type: 'bar',
                    backgroundColor: (context) => {
                        const value = context.parsed.y;
                        return value >= 0 ? 'rgba(75, 192, 192, 0.5)' : 'rgba(255, 99, 132, 0.5)';
                    }
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
                        display: false
                    },
                    y: {
                        display: true,
                        position: 'right',
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });
    }

    createGradient(ctx, isArea = false) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        if (isArea) {
            gradient.addColorStop(0, 'rgba(0, 212, 170, 0.6)');
            gradient.addColorStop(0.5, 'rgba(0, 212, 170, 0.3)');
            gradient.addColorStop(1, 'rgba(0, 212, 170, 0.1)');
        } else {
            gradient.addColorStop(0, 'rgba(0, 212, 170, 0.2)');
            gradient.addColorStop(1, 'rgba(0, 212, 170, 0.02)');
        }
        return gradient;
    }

    createCandlestickData() {
        // Convert price data to candlestick format
        // This is a simplified version - in real implementation, you'd need OHLC data
        return this.chartData.prices.map((price, index) => ({
            x: this.chartData.dates[index],
            y: price
        }));
    }

    addVolumeOverlay() {
        if (!this.chartData.volume) return;
        
        // Create volume chart as overlay
        const volumeCtx = document.getElementById('volume-chart')?.getContext('2d');
        if (!volumeCtx) return;
        
        if (this.charts.volume) {
            this.charts.volume.destroy();
        }
        
        this.charts.volume = new Chart(volumeCtx, {
            type: 'bar',
            data: {
                labels: this.chartData.dates,
                datasets: [{
                    label: 'Volume',
                    data: this.chartData.volume,
                    backgroundColor: this.chartData.volume.map((_, index) => {
                        const current = this.chartData.prices[index];
                        const previous = this.chartData.prices[index - 1];
                        return current >= previous ? 'rgba(0, 212, 170, 0.6)' : 'rgba(255, 99, 132, 0.6)';
                    }),
                    borderColor: 'transparent',
                    borderWidth: 0
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
                        display: false
                    },
                    y: {
                        display: true,
                        position: 'right',
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#ffffff',
                            callback: function(value) {
                                return (value / 1000000).toFixed(1) + 'M';
                            }
                        }
                    }
                }
            }
        });
    }

    resetChart() {
        // Reset all indicators and settings
        ['sma', 'ema', 'bb', 'volume', 'rsi', 'macd', 'vwap', 'stoch'].forEach(indicator => {
            const element = document.getElementById(`indicator-${indicator}`);
            if (element) {
                element.checked = false;
            }
        });
        
        document.getElementById('chart-type').value = 'line';
        document.getElementById('chart-period').value = '1mo';
        
        this.updateChart();
    }

    updateLevels() {
        if (!this.chartData.support_resistance) return;
        
        // Update support levels
        const supportContainer = document.getElementById('support-levels');
        supportContainer.innerHTML = '';
        this.chartData.support_resistance.support.forEach(level => {
            const badge = document.createElement('span');
            badge.className = 'badge bg-success me-1';
            badge.textContent = `$${level.toFixed(2)}`;
            supportContainer.appendChild(badge);
        });
        
        // Update resistance levels
        const resistanceContainer = document.getElementById('resistance-levels');
        resistanceContainer.innerHTML = '';
        this.chartData.support_resistance.resistance.forEach(level => {
            const badge = document.createElement('span');
            badge.className = 'badge bg-danger me-1';
            badge.textContent = `$${level.toFixed(2)}`;
            resistanceContainer.appendChild(badge);
        });
    }

    padIndicator(data, padLength) {
        // Pad indicator data with null values to align with price data
        const padding = new Array(padLength).fill(null);
        return [...padding, ...data];
    }

    exportChart() {
        // Export the chart as a high-quality image
        const canvas = document.getElementById('advanced-price-chart');
        const url = canvas.toDataURL('image/png', 1.0);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.currentSymbol}_chart_${new Date().toISOString().split('T')[0]}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        // Show success message
        this.showNotification('Chart exported successfully!', 'success');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '1';
        }, 100);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Initialize advanced chart
window.advancedChart = new AdvancedChart();