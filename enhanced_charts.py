# Enhanced Interactive Charts System for TradeWise AI
from flask import Blueprint, jsonify, request, render_template_string
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

charts_bp = Blueprint('charts', __name__)

@charts_bp.route('/api/charts/advanced/<symbol>')
def get_advanced_chart_data(symbol):
    """Get comprehensive chart data with technical indicators"""
    try:
        # Get timeframe from query params
        timeframe = request.args.get('timeframe', '1mo')
        interval = request.args.get('interval', '1d')
        
        # Fetch stock data
        stock = yf.Ticker(symbol)
        hist = stock.history(period=timeframe, interval=interval)
        
        if hist.empty:
            return jsonify({'error': 'No data found for symbol'}), 404
        
        # Calculate technical indicators
        indicators = calculate_technical_indicators(hist)
        
        # Format data for Chart.js
        chart_data = format_chart_data(hist, indicators, symbol)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'chart_data': chart_data,
            'indicators': indicators,
            'timeframe': timeframe,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@charts_bp.route('/api/charts/technical-analysis/<symbol>')
def get_technical_analysis(symbol):
    """Get technical analysis signals and patterns"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period='6mo', interval='1d')
        
        if hist.empty:
            return jsonify({'error': 'No data found'}), 404
        
        # Detect patterns and signals
        patterns = detect_chart_patterns(hist)
        signals = generate_trading_signals(hist)
        support_resistance = find_support_resistance(hist)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'patterns': patterns,
            'signals': signals,
            'support_resistance': support_resistance,
            'analysis_timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_technical_indicators(data):
    """Calculate various technical indicators"""
    indicators = {}
    
    # Simple Moving Averages
    indicators['sma_20'] = data['Close'].rolling(window=20).mean().tolist()
    indicators['sma_50'] = data['Close'].rolling(window=50).mean().tolist()
    indicators['sma_200'] = data['Close'].rolling(window=200).mean().tolist()
    
    # Exponential Moving Averages
    indicators['ema_12'] = data['Close'].ewm(span=12).mean().tolist()
    indicators['ema_26'] = data['Close'].ewm(span=26).mean().tolist()
    
    # MACD
    ema12 = data['Close'].ewm(span=12).mean()
    ema26 = data['Close'].ewm(span=26).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9).mean()
    histogram = macd_line - signal_line
    
    indicators['macd'] = {
        'macd_line': macd_line.tolist(),
        'signal_line': signal_line.tolist(),
        'histogram': histogram.tolist()
    }
    
    # RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    indicators['rsi'] = rsi.tolist()
    
    # Bollinger Bands
    bb_period = 20
    bb_std = 2
    bb_middle = data['Close'].rolling(window=bb_period).mean()
    bb_std_dev = data['Close'].rolling(window=bb_period).std()
    bb_upper = bb_middle + (bb_std_dev * bb_std)
    bb_lower = bb_middle - (bb_std_dev * bb_std)
    
    indicators['bollinger_bands'] = {
        'upper': bb_upper.tolist(),
        'middle': bb_middle.tolist(),
        'lower': bb_lower.tolist()
    }
    
    # Volume indicators
    indicators['volume_sma'] = data['Volume'].rolling(window=20).mean().tolist()
    
    # Average True Range (ATR)
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=14).mean()
    indicators['atr'] = atr.tolist()
    
    # Stochastic Oscillator
    lowest_low = data['Low'].rolling(window=14).min()
    highest_high = data['High'].rolling(window=14).max()
    k_percent = 100 * ((data['Close'] - lowest_low) / (highest_high - lowest_low))
    d_percent = k_percent.rolling(window=3).mean()
    
    indicators['stochastic'] = {
        'k': k_percent.tolist(),
        'd': d_percent.tolist()
    }
    
    return indicators

def format_chart_data(hist, indicators, symbol):
    """Format data for Chart.js consumption"""
    
    # Convert timestamps to ISO format
    timestamps = [date.isoformat() for date in hist.index]
    
    # OHLCV data
    ohlcv_data = []
    for i, (date, row) in enumerate(hist.iterrows()):
        ohlcv_data.append({
            'x': date.isoformat(),
            'o': float(row['Open']),
            'h': float(row['High']),
            'l': float(row['Low']),
            'c': float(row['Close']),
            'v': int(row['Volume'])
        })
    
    # Price data for line charts
    price_data = [{'x': timestamps[i], 'y': float(price)} 
                  for i, price in enumerate(hist['Close']) if not np.isnan(price)]
    
    # Volume data
    volume_data = [{'x': timestamps[i], 'y': int(vol)} 
                   for i, vol in enumerate(hist['Volume']) if not np.isnan(vol)]
    
    # Format indicator data
    formatted_indicators = {}
    for indicator, values in indicators.items():
        if isinstance(values, dict):
            formatted_indicators[indicator] = {}
            for key, value_list in values.items():
                formatted_indicators[indicator][key] = [
                    {'x': timestamps[i], 'y': float(val)} 
                    for i, val in enumerate(value_list) 
                    if i < len(timestamps) and not (isinstance(val, float) and np.isnan(val))
                ]
        else:
            formatted_indicators[indicator] = [
                {'x': timestamps[i], 'y': float(val)} 
                for i, val in enumerate(values) 
                if i < len(timestamps) and not (isinstance(val, float) and np.isnan(val))
            ]
    
    return {
        'ohlcv': ohlcv_data,
        'price': price_data,
        'volume': volume_data,
        'indicators': formatted_indicators,
        'timestamps': timestamps,
        'symbol': symbol
    }

def detect_chart_patterns(data):
    """Detect common chart patterns"""
    patterns = []
    
    # Simple pattern detection logic
    recent_data = data.tail(50)  # Last 50 days
    
    # Double top pattern
    if detect_double_top(recent_data):
        patterns.append({
            'type': 'double_top',
            'signal': 'bearish',
            'confidence': 0.75,
            'description': 'Double top pattern detected - potential reversal'
        })
    
    # Support/Resistance breakout
    if detect_breakout(recent_data):
        patterns.append({
            'type': 'breakout',
            'signal': 'bullish',
            'confidence': 0.8,
            'description': 'Resistance breakout - potential upward momentum'
        })
    
    # Triangle pattern
    if detect_triangle(recent_data):
        patterns.append({
            'type': 'triangle',
            'signal': 'neutral',
            'confidence': 0.65,
            'description': 'Triangle consolidation - prepare for breakout'
        })
    
    return patterns

def generate_trading_signals(data):
    """Generate trading signals based on technical analysis"""
    signals = []
    
    # Calculate indicators for signals
    sma_20 = data['Close'].rolling(window=20).mean()
    sma_50 = data['Close'].rolling(window=50).mean()
    
    # RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = data['Close'].ewm(span=12).mean()
    ema26 = data['Close'].ewm(span=26).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9).mean()
    
    latest_values = {
        'price': data['Close'].iloc[-1],
        'sma_20': sma_20.iloc[-1],
        'sma_50': sma_50.iloc[-1],
        'rsi': rsi.iloc[-1],
        'macd': macd_line.iloc[-1],
        'macd_signal': signal_line.iloc[-1]
    }
    
    # Generate signals
    if latest_values['price'] > latest_values['sma_20'] > latest_values['sma_50']:
        signals.append({
            'type': 'golden_cross',
            'signal': 'buy',
            'strength': 'strong',
            'description': 'Price above moving averages - bullish trend'
        })
    
    if latest_values['rsi'] < 30:
        signals.append({
            'type': 'oversold',
            'signal': 'buy',
            'strength': 'medium',
            'description': 'RSI indicates oversold conditions'
        })
    elif latest_values['rsi'] > 70:
        signals.append({
            'type': 'overbought',
            'signal': 'sell',
            'strength': 'medium',
            'description': 'RSI indicates overbought conditions'
        })
    
    if latest_values['macd'] > latest_values['macd_signal']:
        signals.append({
            'type': 'macd_bullish',
            'signal': 'buy',
            'strength': 'medium',
            'description': 'MACD bullish crossover'
        })
    
    return signals

def find_support_resistance(data):
    """Find support and resistance levels"""
    # Simple support/resistance detection
    prices = data['Close'].values
    
    # Find local minima and maxima
    support_levels = []
    resistance_levels = []
    
    window = 10
    for i in range(window, len(prices) - window):
        # Check for local minimum (support)
        if all(prices[i] <= prices[i-j] for j in range(1, window+1)) and \
           all(prices[i] <= prices[i+j] for j in range(1, window+1)):
            support_levels.append(float(prices[i]))
        
        # Check for local maximum (resistance)
        if all(prices[i] >= prices[i-j] for j in range(1, window+1)) and \
           all(prices[i] >= prices[i+j] for j in range(1, window+1)):
            resistance_levels.append(float(prices[i]))
    
    # Remove duplicates and sort
    support_levels = sorted(list(set(support_levels)))[-3:]  # Last 3 support levels
    resistance_levels = sorted(list(set(resistance_levels)))[-3:]  # Last 3 resistance levels
    
    return {
        'support': support_levels,
        'resistance': resistance_levels,
        'current_price': float(data['Close'].iloc[-1])
    }

def detect_double_top(data):
    """Simple double top pattern detection"""
    highs = data['High'].values
    if len(highs) < 20:
        return False
    
    # Look for two similar peaks
    recent_highs = highs[-20:]
    max_high = np.max(recent_highs)
    
    # Count peaks near max high
    threshold = max_high * 0.98
    peak_count = np.sum(recent_highs > threshold)
    
    return peak_count >= 2

def detect_breakout(data):
    """Simple breakout detection"""
    recent_data = data.tail(20)
    resistance = recent_data['High'].rolling(window=10).max()
    current_price = data['Close'].iloc[-1]
    
    return current_price > resistance.iloc[-2] * 1.02

def detect_triangle(data):
    """Simple triangle pattern detection"""
    recent_data = data.tail(30)
    highs = recent_data['High']
    lows = recent_data['Low']
    
    # Check if highs are decreasing and lows are increasing
    high_trend = np.polyfit(range(len(highs)), highs, 1)[0] < 0
    low_trend = np.polyfit(range(len(lows)), lows, 1)[0] > 0
    
    return high_trend and low_trend

def get_chart_template():
    """Return HTML template for enhanced charts"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enhanced Charts - {{symbol}}</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: white;
                margin: 0;
                padding: 20px;
            }
            .chart-container {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                backdrop-filter: blur(10px);
            }
            .chart-title {
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 15px;
                text-align: center;
            }
            .chart-canvas {
                height: 400px;
            }
            .indicators-panel {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .indicator-card {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
            }
            .controls {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            .btn {
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                background: rgba(139, 92, 246, 0.8);
                color: white;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .btn:hover {
                background: rgba(139, 92, 246, 1);
                transform: scale(1.05);
            }
            .btn.active {
                background: #8b5cf6;
            }
        </style>
    </head>
    <body>
        <div class="chart-container">
            <div class="chart-title">{{symbol}} - Advanced Chart Analysis</div>
            
            <div class="controls">
                <button class="btn active" onclick="switchTimeframe('1d')">1D</button>
                <button class="btn" onclick="switchTimeframe('5d')">5D</button>
                <button class="btn" onclick="switchTimeframe('1mo')">1M</button>
                <button class="btn" onclick="switchTimeframe('3mo')">3M</button>
                <button class="btn" onclick="switchTimeframe('6mo')">6M</button>
                <button class="btn" onclick="switchTimeframe('1y')">1Y</button>
            </div>
            
            <canvas id="priceChart" class="chart-canvas"></canvas>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">Technical Indicators</div>
            <canvas id="indicatorsChart" class="chart-canvas"></canvas>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">Volume Analysis</div>
            <canvas id="volumeChart" class="chart-canvas"></canvas>
        </div>
        
        <div class="indicators-panel">
            <div class="indicator-card">
                <h4>RSI (14)</h4>
                <div id="rsi-value">--</div>
            </div>
            <div class="indicator-card">
                <h4>MACD</h4>
                <div id="macd-value">--</div>
            </div>
            <div class="indicator-card">
                <h4>Moving Averages</h4>
                <div id="ma-values">--</div>
            </div>
            <div class="indicator-card">
                <h4>Support/Resistance</h4>
                <div id="sr-levels">--</div>
            </div>
        </div>
        
        <script>
            let priceChart, indicatorsChart, volumeChart;
            let currentSymbol = '{{symbol}}';
            let currentTimeframe = '1mo';
            
            async function loadChartData(symbol, timeframe) {
                try {
                    const response = await fetch(`/api/charts/advanced/${symbol}?timeframe=${timeframe}`);
                    const data = await response.json();
                    
                    if (data.success) {
                        updateCharts(data.chart_data);
                        updateIndicators(data.indicators);
                    }
                } catch (error) {
                    console.error('Error loading chart data:', error);
                }
            }
            
            function updateCharts(chartData) {
                // Update price chart
                if (priceChart) priceChart.destroy();
                
                const priceCtx = document.getElementById('priceChart').getContext('2d');
                priceChart = new Chart(priceCtx, {
                    type: 'line',
                    data: {
                        datasets: [
                            {
                                label: 'Price',
                                data: chartData.price,
                                borderColor: '#8b5cf6',
                                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                                fill: true,
                                tension: 0.1
                            },
                            {
                                label: 'SMA 20',
                                data: chartData.indicators.sma_20,
                                borderColor: '#06b6d4',
                                backgroundColor: 'transparent',
                                borderWidth: 1,
                                pointRadius: 0
                            },
                            {
                                label: 'SMA 50',
                                data: chartData.indicators.sma_50,
                                borderColor: '#f59e0b',
                                backgroundColor: 'transparent',
                                borderWidth: 1,
                                pointRadius: 0
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                labels: { color: 'white' }
                            }
                        },
                        scales: {
                            x: {
                                type: 'time',
                                ticks: { color: 'white' },
                                grid: { color: 'rgba(255, 255, 255, 0.1)' }
                            },
                            y: {
                                ticks: { color: 'white' },
                                grid: { color: 'rgba(255, 255, 255, 0.1)' }
                            }
                        }
                    }
                });
                
                // Update volume chart
                if (volumeChart) volumeChart.destroy();
                
                const volumeCtx = document.getElementById('volumeChart').getContext('2d');
                volumeChart = new Chart(volumeCtx, {
                    type: 'bar',
                    data: {
                        datasets: [{
                            label: 'Volume',
                            data: chartData.volume,
                            backgroundColor: 'rgba(16, 185, 129, 0.6)',
                            borderColor: '#10b981',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                labels: { color: 'white' }
                            }
                        },
                        scales: {
                            x: {
                                type: 'time',
                                ticks: { color: 'white' },
                                grid: { color: 'rgba(255, 255, 255, 0.1)' }
                            },
                            y: {
                                ticks: { color: 'white' },
                                grid: { color: 'rgba(255, 255, 255, 0.1)' }
                            }
                        }
                    }
                });
            }
            
            function updateIndicators(indicators) {
                // Update indicator displays
                const rsiValue = indicators.rsi[indicators.rsi.length - 1];
                document.getElementById('rsi-value').textContent = rsiValue ? rsiValue.y.toFixed(2) : '--';
                
                // Update other indicators...
            }
            
            function switchTimeframe(timeframe) {
                currentTimeframe = timeframe;
                
                // Update button states
                document.querySelectorAll('.btn').forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
                
                loadChartData(currentSymbol, timeframe);
            }
            
            // Initialize charts
            document.addEventListener('DOMContentLoaded', function() {
                loadChartData(currentSymbol, currentTimeframe);
            });
        </script>
    </body>
    </html>
    '''

@charts_bp.route('/charts/<symbol>')
def show_enhanced_chart(symbol):
    """Show enhanced chart page for a symbol"""
    template = get_chart_template()
    return render_template_string(template, symbol=symbol.upper())

def install_charts(app):
    """Install enhanced charts into Flask app"""
    app.register_blueprint(charts_bp)
    return app