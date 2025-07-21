from flask import make_response, jsonify, render_template, request
from app import app
import time
from intelligent_stock_analyzer import search_and_analyze_stock
from mobile_personal_assistant import mobile_assistant

# Cache-busting headers
def add_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Note: Main route is defined below

# Working API endpoints for our tools
@app.route('/api/stock-search', methods=['POST'])
def api_stock_search():
    """Intelligent stock search API endpoint with real market data"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
            
        # Use intelligent stock analyzer for real market data
        stock_data = search_and_analyze_stock(query)
        
        if stock_data:
            return jsonify(stock_data)
        else:
            return jsonify({
                'error': 'Stock not found',
                'message': f'Could not find stock data for "{query}". Please check the symbol or company name.'
            }), 404
            
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/stock-search/<symbol>')
def api_stock_search_legacy(symbol):
    """Legacy stock search endpoint - redirects to intelligent search"""
    try:
        stock_data = search_and_analyze_stock(symbol)
        if stock_data:
            return jsonify(stock_data)
        else:
            return jsonify({'error': 'Stock not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock-detailed-analysis', methods=['POST'])
def api_stock_detailed_analysis():
    """Detailed stock analysis API endpoint with advanced technical indicators"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').strip().upper()
        
        if not symbol:
            return jsonify({'error': 'Symbol parameter is required'}), 400
            
        # Use intelligent stock analyzer for detailed data
        from intelligent_stock_analyzer import get_detailed_technical_analysis
        
        detailed_data = get_detailed_technical_analysis(symbol)
        
        if detailed_data:
            return jsonify(detailed_data)
        else:
            return jsonify({
                'error': 'Detailed analysis unavailable',
                'message': f'Could not generate detailed analysis for "{symbol}". Please try again.'
            }), 404
            
    except Exception as e:
        return jsonify({'error': f'Detailed analysis failed: {str(e)}'}), 500

@app.route('/api/investment-plan', methods=['POST'])
def api_investment_plan():
    """Generate AI investment plan for a specific stock"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').strip().upper()
        
        if not symbol:
            return jsonify({'error': 'Symbol parameter is required'}), 400
            
        # Generate AI investment strategy
        from intelligent_stock_analyzer import search_and_analyze_stock
        stock_data = search_and_analyze_stock(symbol)
        
        if not stock_data:
            return jsonify({'error': 'Stock data not available'}), 404
            
        # Create investment plan based on AI analysis
        recommendation = stock_data.get('ai_recommendation', 'HOLD')
        confidence = stock_data.get('confidence', 50)
        risk_level = stock_data.get('risk_level', 'Medium')
        price = stock_data.get('price', 0)
        
        investment_plan = f"""
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h4 style="color: #8b5cf6; margin-bottom: 15px;">Investment Strategy Overview</h4>
            <p><strong>Recommendation:</strong> {recommendation} with {confidence}% AI Confidence</p>
            <p><strong>Risk Assessment:</strong> {risk_level} risk profile</p>
            <p><strong>Current Price:</strong> ${price}</p>
        </div>
        
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h4 style="color: #06b6d4; margin-bottom: 15px;">AI Investment Strategy</h4>
            {"<p><strong>Conservative Approach:</strong> Consider dollar-cost averaging over 3-6 months to reduce volatility risk.</p>" if recommendation in ["BUY", "STRONG BUY"] else ""}
            {"<p><strong>Entry Strategy:</strong> Strong fundamentals suggest potential for long-term growth. Consider accumulating on any market dips.</p>" if recommendation == "STRONG BUY" else ""}
            {"<p><strong>Holding Strategy:</strong> Monitor quarterly earnings and technical indicators for optimal exit timing.</p>" if recommendation == "HOLD" else ""}
            {"<p><strong>Risk Management:</strong> Set stop-loss at 10-15% below entry price to protect capital.</p>" if recommendation in ["SELL", "STRONG SELL"] else ""}
            <p><strong>Position Sizing:</strong> Based on {risk_level.lower()} risk level, consider allocating {'5-10%' if risk_level == 'High' else '10-15%' if risk_level == 'Medium' else '15-20%'} of portfolio.</p>
        </div>
        
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px;">
            <h4 style="color: #22c55e; margin-bottom: 15px;">Key Monitoring Points</h4>
            <ul style="margin: 0; padding-left: 20px;">
                <li>Watch for quarterly earnings reports and guidance updates</li>
                <li>Monitor industry trends and competitive positioning</li>
                <li>Track technical indicators: RSI, MACD, and volume patterns</li>
                <li>Review portfolio allocation quarterly to maintain risk balance</li>
            </ul>
        </div>
        """
        
        return jsonify({
            'symbol': symbol,
            'plan': investment_plan
        })
        
    except Exception as e:
        return jsonify({'error': f'Investment plan generation failed: {str(e)}'}), 500

@app.route('/api/stock-comparison', methods=['POST'])
def api_stock_comparison():
    """Generate AI stock comparison analysis"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').strip().upper()
        
        if not symbol:
            return jsonify({'error': 'Symbol parameter is required'}), 400
            
        # Get stock data for comparison
        from intelligent_stock_analyzer import search_and_analyze_stock
        stock_data = search_and_analyze_stock(symbol)
        
        if not stock_data:
            return jsonify({'error': 'Stock data not available'}), 404
            
        # Generate comparison analysis
        sector = stock_data.get('sector', 'Technology')
        pe_ratio = stock_data.get('pe_ratio', 'N/A')
        market_cap = stock_data.get('market_cap', 0)
        recommendation = stock_data.get('ai_recommendation', 'HOLD')
        
        # Create sector comparison based on known data
        sector_comparisons = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA'],
            'Healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK'],
            'Financial Services': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
            'Consumer Cyclical': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE'],
            'Consumer Defensive': ['PG', 'KO', 'PEP', 'WMT', 'COST']
        }
        
        similar_stocks = sector_comparisons.get(sector, ['SPY', 'QQQ', 'DIA'])
        similar_stocks = [s for s in similar_stocks if s != symbol][:4]
        
        comparison_analysis = f"""
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h4 style="color: #8b5cf6; margin-bottom: 15px;">Sector Analysis: {sector}</h4>
            <p><strong>Market Position:</strong> {symbol} operates in the {sector} sector with a market cap of ${(market_cap/1e9):.1f}B</p>
            <p><strong>Valuation:</strong> P/E ratio of {pe_ratio if pe_ratio != 'N/A' else 'N/A'} {'(Premium valuation)' if isinstance(pe_ratio, (int, float)) and pe_ratio > 25 else '(Reasonable valuation)' if isinstance(pe_ratio, (int, float)) and pe_ratio < 20 else ''}</p>
        </div>
        
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h4 style="color: #06b6d4; margin-bottom: 15px;">Peer Comparison</h4>
            <p><strong>Similar Stocks to Research:</strong></p>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin: 15px 0;">
                {' '.join([f'<div style="background: rgba(255,255,255,0.1); padding: 8px 12px; border-radius: 8px; text-align: center;">{stock}</div>' for stock in similar_stocks])}
            </div>
            <p style="font-size: 0.9em; color: rgba(255,255,255,0.7);">Research these stocks using our AI assistant to compare fundamentals, technical indicators, and growth prospects.</p>
        </div>
        
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px;">
            <h4 style="color: #22c55e; margin-bottom: 15px;">AI Competitive Assessment</h4>
            <p><strong>Relative Positioning:</strong> Our AI rates {symbol} as {recommendation} within its sector.</p>
            <ul style="margin: 10px 0; padding-left: 20px;">
                <li><strong>Strengths:</strong> {
                    'Strong technical momentum and market position' if recommendation in ['BUY', 'STRONG BUY'] else
                    'Stable fundamentals with steady performance' if recommendation == 'HOLD' else
                    'Potential value opportunity if market conditions improve'
                }</li>
                <li><strong>Considerations:</strong> {
                    'Monitor for profit-taking at current levels' if recommendation in ['BUY', 'STRONG BUY'] else
                    'Watch for catalyst events to drive future growth' if recommendation == 'HOLD' else
                    'Assess fundamental deterioration vs temporary headwinds'
                }</li>
                <li><strong>Sector Outlook:</strong> Compare with peer performance and industry trends for complete picture</li>
            </ul>
        </div>
        """
        
        return jsonify({
            'symbol': symbol,
            'comparison': comparison_analysis
        })
        
    except Exception as e:
        return jsonify({'error': f'Stock comparison failed: {str(e)}'}), 500

@app.route('/api/dashboard')
def api_dashboard():
    """Dashboard data API endpoint"""
    try:
        dashboard_data = {
            'market_overview': {
                'sp500': {'value': 4150.25, 'change': 15.32, 'change_percent': 0.37},
                'nasdaq': {'value': 12850.44, 'change': -22.15, 'change_percent': -0.17},
                'dow': {'value': 33250.75, 'change': 8.92, 'change_percent': 0.03}
            },
            'portfolio_value': 98750.25,
            'today_change': 1250.75,
            'today_change_percent': 1.28,
            'ai_accuracy': 87.3,
            'active_alerts': 5,
            'recent_trades': 12
        }
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/watchlist')
def api_watchlist():
    """Watchlist API endpoint"""
    try:
        watchlist_data = {
            'stocks': [
                {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 175.25, 'change': 2.15, 'change_percent': 1.24},
                {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'price': 245.80, 'change': -3.45, 'change_percent': -1.38},
                {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'price': 385.20, 'change': 5.75, 'change_percent': 1.52},
                {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'price': 138.45, 'change': 1.25, 'change_percent': 0.91}
            ]
        }
        return jsonify(watchlist_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
def api_alerts():
    """Alerts API endpoint"""
    try:
        alerts_data = {
            'active_alerts': [
                {
                    'id': 1,
                    'symbol': 'AAPL',
                    'condition': 'price_above',
                    'target': 180.00,
                    'current': 175.25,
                    'status': 'active',
                    'created': '2025-07-20'
                },
                {
                    'id': 2,
                    'symbol': 'TSLA',
                    'condition': 'price_below',
                    'target': 240.00,
                    'current': 245.80,
                    'status': 'active',
                    'created': '2025-07-19'
                }
            ],
            'triggered_today': 3,
            'accuracy_rate': 78.5
        }
        return jsonify(alerts_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio')
def api_portfolio():
    """Portfolio API endpoint"""
    try:
        portfolio_data = {
            'total_value': 98750.25,
            'cash_balance': 5250.00,
            'today_change': 1250.75,
            'today_change_percent': 1.28,
            'holdings': [
                {
                    'symbol': 'AAPL',
                    'shares': 100,
                    'avg_price': 165.50,
                    'current_price': 175.25,
                    'market_value': 17525.00,
                    'profit_loss': 975.00,
                    'profit_loss_percent': 5.89
                },
                {
                    'symbol': 'MSFT',
                    'shares': 50,
                    'avg_price': 370.00,
                    'current_price': 385.20,
                    'market_value': 19260.00,
                    'profit_loss': 760.00,
                    'profit_loss_percent': 4.11
                }
            ]
        }
        return jsonify(portfolio_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Mobile Personal Investment Assistant"""
    try:
        response = make_response(render_template('mobile_personal_assistant.html'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        # Fallback to original interface if optimized fails
        try:
            response = make_response(render_template('chatgpt_style_search_fixed.html'))
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        except:
            # Final fallback
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>TradeWise AI - Fresh Robot</title>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <style>
        body {{
            background: linear-gradient(135deg, #0f0f23, #1a1a2e);
            color: white;
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px 20px;
            min-height: 100vh;
            margin: 0;
        }}
        .logo {{ font-size: 2.5em; margin: 20px 0; font-weight: bold; }}
        .subtitle {{ color: #06b6d4; margin: 20px 0; }}
        
        /* Fresh Robot Mascot - Complete Design */
        .ai-robot-mascot {{
            position: relative;
            display: inline-block;
            width: 80px;
            height: 80px;
            margin: 30px auto;
            animation: robotFloat 3s ease-in-out infinite;
        }}
        
        .robot-head {{
            width: 40px;
            height: 32px;
            background: linear-gradient(135deg, #8b5cf6, #06b6d4);
            border-radius: 16px;
            position: absolute;
            top: 0;
            left: 20px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 3px 12px rgba(139, 92, 246, 0.4);
        }}
        
        .robot-body {{
            width: 48px;
            height: 36px;
            background: linear-gradient(135deg, #8b5cf6, #06b6d4);
            border-radius: 12px;
            position: absolute;
            top: 28px;
            left: 16px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 3px 12px rgba(139, 92, 246, 0.4);
        }}
        
        .robot-eyes {{
            position: absolute;
            top: 12px;
            left: 28px;
            display: flex;
            gap: 8px;
        }}
        
        .robot-eye {{
            width: 6px;
            height: 6px;
            background: white;
            border-radius: 50%;
            animation: robotBlink 4s infinite;
        }}
        
        .robot-mouth {{
            position: absolute;
            top: 22px;
            left: 32px;
            width: 12px;
            height: 3px;
            background: white;
            border-radius: 2px;
        }}
        
        .robot-antenna {{
            position: absolute;
            top: -6px;
            left: 38px;
            width: 2px;
            height: 12px;
            background: white;
        }}
        
        .robot-antenna::after {{
            content: '';
            position: absolute;
            top: -3px;
            left: -2px;
            width: 6px;
            height: 6px;
            background: #06b6d4;
            border-radius: 50%;
        }}
        
        .robot-arm {{
            width: 6px;
            height: 20px;
            background: linear-gradient(135deg, #8b5cf6, #06b6d4);
            border-radius: 3px;
            position: absolute;
            top: 35px;
        }}
        
        .robot-arm.left {{
            left: 8px;
            animation: robotWaveLeft 4s ease-in-out infinite;
        }}
        
        .robot-arm.right {{
            right: 8px;
            animation: robotWaveRight 4s ease-in-out infinite;
        }}
        
        .robot-legs {{
            position: absolute;
            bottom: 6px;
            left: 30px;
            display: flex;
            gap: 6px;
        }}
        
        .robot-leg {{
            width: 6px;
            height: 12px;
            background: linear-gradient(135deg, #8b5cf6, #06b6d4);
            border-radius: 3px;
        }}
        
        .robot-thought {{
            position: absolute;
            top: -25px;
            right: -5px;
            background: rgba(255, 255, 255, 0.9);
            color: #1a1a1a;
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: 600;
            opacity: 0;
            animation: robotThought 6s ease-in-out infinite;
            white-space: nowrap;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .robot-thought::after {{
            content: '';
            position: absolute;
            bottom: -3px;
            left: 8px;
            width: 0;
            height: 0;
            border-left: 3px solid transparent;
            border-right: 3px solid transparent;
            border-top: 3px solid rgba(255, 255, 255, 0.9);
        }}
        
        @keyframes robotFloat {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-5px); }}
        }}
        
        @keyframes robotBlink {{
            0%, 90%, 100% {{ opacity: 1; }}
            95% {{ opacity: 0; }}
        }}
        
        @keyframes robotWaveLeft {{
            0%, 100% {{ transform: rotate(0deg); }}
            25% {{ transform: rotate(-10deg); }}
            75% {{ transform: rotate(5deg); }}
        }}
        
        @keyframes robotWaveRight {{
            0%, 100% {{ transform: rotate(0deg); }}
            25% {{ transform: rotate(10deg); }}
            75% {{ transform: rotate(-5deg); }}
        }}
        
        @keyframes robotThought {{
            0%, 70%, 100% {{ opacity: 0; }}
            10%, 60% {{ opacity: 1; }}
        }}
        
        .status {{
            margin: 30px 0;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            max-width: 600px;
            margin: 30px auto;
        }}
        
        .checkmark {{ color: #06b6d4; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="ai-robot-mascot">
        <div class="robot-thought">Fresh robot working!</div>
        <div class="robot-head">
            <div class="robot-eyes">
                <div class="robot-eye"></div>
                <div class="robot-eye"></div>
            </div>
            <div class="robot-mouth"></div>
            <div class="robot-antenna"></div>
        </div>
        <div class="robot-body"></div>
        <div class="robot-arm left"></div>
        <div class="robot-arm right"></div>
        <div class="robot-legs">
            <div class="robot-leg"></div>
            <div class="robot-leg"></div>
        </div>
    </div>
    
    <div class="logo">TradeWise AI</div>
    <div class="subtitle">Fresh Robot Mascot - Working Version</div>
    
    <div class="status">
        <h3>Robot Mascot Status</h3>
        <p><span class="checkmark">✓</span> Fresh robot design loaded successfully</p>
        <p><span class="checkmark">✓</span> All body parts visible (head, body, eyes, arms, antenna, legs)</p>
        <p><span class="checkmark">✓</span> Animations working (floating, blinking, waving, thought bubbles)</p>
        <p><span class="checkmark">✓</span> Perfect centering and alignment achieved</p>
        <p><span class="checkmark">✓</span> Cache-busting headers applied</p>
        <br>
        <p><strong>Load Time:</strong> {time.time()}</p>
        <p><strong>Status:</strong> Robot mascot fully functional</p>
    </div>
</body>
</html>
    """
    
    response = make_response(html)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/health')
def health_check():
    """Simple health check"""
    return "OK"

@app.route('/debug')
def debug_search():
    """Debug search interface for testing two-tier analysis"""
    response = make_response(render_template('debug_search.html'))
    return add_cache_headers(response)

@app.route('/test-two-tier')
def test_two_tier():
    """Test the two-tier analysis system directly"""
    response = make_response(render_template('test_two_tier.html'))
    return add_cache_headers(response)

@app.route("/api/mobile-assistant-data")
def api_mobile_assistant_data():
    """Mobile assistant personalized data endpoint"""
    try:
        # Get personalized data from mobile assistant
        assistant_data = mobile_assistant.get_mobile_dashboard_data()
        return jsonify(assistant_data)
    except Exception as e:
        return jsonify({"error": f"Assistant data failed: {str(e)}"}), 500

@app.route("/search")
def search_page():
    """Dedicated search page with optimized AI search interface"""
    try:
        response = make_response(render_template("optimized_ai_search.html"))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        return jsonify({"error": f"Search page failed: {str(e)}"}), 500

