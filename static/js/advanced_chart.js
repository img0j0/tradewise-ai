// Advanced charting functionality
class AdvancedChart {
    constructor() {
        this.currentSymbol = null;
        this.charts = {};
        this.indicators = {};
        this.chartData = null;
        this.initialize();
    }

    initialize() {
        // Set up event listeners
        document.getElementById('chart-period').addEventListener('change', () => this.updateChart());
        document.getElementById('chart-type').addEventListener('change', () => this.updateChart());
        
        // Indicator toggles
        ['sma', 'ema', 'bb', 'volume'].forEach(indicator => {
            document.getElementById(`indicator-${indicator}`).addEventListener('change', () => this.updateChart());
        });
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
        try {
            const period = document.getElementById('chart-period').value;
            const response = await fetch(`/api/technical-indicators/${this.currentSymbol}?period=${period}`);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.chartData = data;
            this.updateChart();
            this.updateLevels();
            
        } catch (error) {
            console.error('Error loading chart data:', error);
            showError('Failed to load chart data');
        }
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
        
        // Main price dataset
        if (chartType === 'candlestick') {
            // For candlestick, we need a different approach
            datasets.push({
                label: 'Price',
                data: this.chartData.prices,
                type: 'line',
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                pointRadius: 0
            });
        } else {
            datasets.push({
                label: 'Price',
                data: this.chartData.prices,
                type: chartType,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: chartType === 'area' ? 'rgba(75, 192, 192, 0.2)' : 'transparent',
                borderWidth: 2,
                pointRadius: chartType === 'line' ? 0 : 3,
                fill: chartType === 'area'
            });
        }
        
        // Add indicators
        if (document.getElementById('indicator-sma').checked && this.chartData.sma_20) {
            datasets.push({
                label: 'SMA 20',
                data: this.padIndicator(this.chartData.sma_20, 19),
                type: 'line',
                borderColor: 'rgba(255, 206, 86, 1)',
                borderWidth: 1,
                pointRadius: 0,
                fill: false
            });
        }
        
        if (document.getElementById('indicator-ema').checked && this.chartData.ema_12) {
            datasets.push({
                label: 'EMA 12',
                data: this.padIndicator(this.chartData.ema_12, 11),
                type: 'line',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
                pointRadius: 0,
                fill: false
            });
        }
        
        if (document.getElementById('indicator-bb').checked && this.chartData.bollinger) {
            datasets.push({
                label: 'BB Upper',
                data: this.padIndicator(this.chartData.bollinger.upper, 19),
                type: 'line',
                borderColor: 'rgba(153, 102, 255, 0.5)',
                borderWidth: 1,
                pointRadius: 0,
                fill: false,
                borderDash: [5, 5]
            });
            
            datasets.push({
                label: 'BB Lower',
                data: this.padIndicator(this.chartData.bollinger.lower, 19),
                type: 'line',
                borderColor: 'rgba(153, 102, 255, 0.5)',
                borderWidth: 1,
                pointRadius: 0,
                fill: false,
                borderDash: [5, 5]
            });
        }
        
        // Create chart
        this.charts.price = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.chartData.dates,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
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

    addVolumeOverlay() {
        // This would add volume bars as a secondary y-axis
        // Implementation depends on Chart.js configuration
    }

    updateLevels() {
        if (!this.chartData.support_resistance) return;
        
        // Update support levels
        const supportList = document.getElementById('support-levels');
        supportList.innerHTML = '';
        this.chartData.support_resistance.support.forEach(level => {
            const li = document.createElement('li');
            li.innerHTML = `$${level.toFixed(2)} <small class="text-muted">Strong Support</small>`;
            supportList.appendChild(li);
        });
        
        // Update resistance levels
        const resistanceList = document.getElementById('resistance-levels');
        resistanceList.innerHTML = '';
        this.chartData.support_resistance.resistance.forEach(level => {
            const li = document.createElement('li');
            li.innerHTML = `$${level.toFixed(2)} <small class="text-muted">Strong Resistance</small>`;
            resistanceList.appendChild(li);
        });
    }

    padIndicator(data, padLength) {
        // Pad indicator data with null values to align with price data
        const padding = new Array(padLength).fill(null);
        return [...padding, ...data];
    }

    exportChart() {
        // Export the chart as an image
        const canvas = document.getElementById('advanced-price-chart');
        const url = canvas.toDataURL('image/png');
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.currentSymbol}_chart_${new Date().toISOString().split('T')[0]}.png`;
        a.click();
    }
}

// Initialize advanced chart
window.advancedChart = new AdvancedChart();