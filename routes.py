from flask import render_template, jsonify, request, make_response
from app import app, db
from models import User, StockAnalysis, WatchlistItem
from ai_insights import AIInsightsEngine
from data_service import DataService
from stock_search import StockSearchService
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize core services only
data_service = DataService()
ai_engine = AIInsightsEngine()
stock_search_service = StockSearchService()

# Simple demo watchlist for stock analysis tracking
demo_watchlist = set(['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA'])

# Train AI model on startup for stock analysis
try:
    stocks_data = data_service.get_all_stocks()
    ai_engine.train_model(stocks_data)
    logger.info("AI analysis model trained successfully")
except Exception as e:
    logger.error(f"Error training AI analysis model: {e}")

def save_analysis_to_history(symbol, stock_data, insights):
    """Save analysis results for historical tracking and comparison"""
    try:
        analysis = StockAnalysis()
        analysis.symbol = symbol
        analysis.price_at_analysis = float(stock_data.get('current_price', 0))
        analysis.recommendation = insights.get('recommendation', 'HOLD')
        analysis.confidence_score = float(insights.get('confidence', 50))
        analysis.fundamental_score = float(insights.get('fundamental_score', 50))
        analysis.technical_score = float(insights.get('technical_score', 50))
        analysis.risk_level = insights.get('risk_level', 'Medium')
        analysis.analysis_details = json.dumps({
            'market_sentiment': insights.get('market_sentiment', 'Neutral'),
            'investment_thesis': insights.get('analysis', 'Analysis not available'),
            'pe_ratio': stock_data.get('pe_ratio'),
            'market_cap': stock_data.get('market_cap')
        })
        analysis.market_conditions = json.dumps({
            'analysis_timestamp': datetime.now().isoformat(),
            'data_source': 'Yahoo Finance'
        })
        db.session.add(analysis)
        db.session.commit()
        logger.info(f"Saved analysis for {symbol} to history")
    except Exception as e:
        logger.error(f"Error saving analysis to history: {e}")

@app.route('/')
def index():
    """Clean stock analysis interface powered by AI"""
    try:
        response = make_response(render_template('clean_chatgpt_search.html'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        logger.error(f"Error loading analysis interface: {e}")
        return jsonify({'error': 'Analysis interface loading error'}), 500

@app.route('/api/stock-analysis', methods=['POST'])
def stock_analysis_api():
    """AI-powered stock analysis API for comprehensive investment research"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        # Use existing stock search service for real-time data
        stock_service = StockSearchService()
        
        # Get real-time stock data
        stock_data = stock_service.search_stock(query)
        
        if not stock_data:
            return jsonify({
                'error': 'Stock not found',
                'message': f'No data found for "{query}"'
            }), 404
        
        # Get comprehensive AI analysis insights
        ai_engine = AIInsightsEngine()
        insights = ai_engine.get_insights(query.upper(), stock_data)
        
        # Save analysis to history for tracking and comparison
        save_analysis_to_history(query.upper(), stock_data, insights)
        
        # Build comprehensive analysis response
        response = {
            'success': True,
            'symbol': stock_data.get('symbol', query.upper()),
            'name': stock_data.get('name', 'Unknown Company'),
            'price': float(stock_data.get('current_price', 0)) if stock_data.get('current_price') else 0,
            'change': float(stock_data.get('price_change', 0)),
            'change_percent': float(stock_data.get('price_change_percent', 0)),
            'market_cap': float(stock_data.get('market_cap', 0)) if stock_data.get('market_cap') else 0,
            'pe_ratio': stock_data.get('pe_ratio'),
            'data_source': 'Yahoo Finance (Real-time)',
            
            # AI Analysis Results
            'recommendation': insights.get('recommendation', 'HOLD'),
            'confidence': int(insights.get('confidence', 50)),
            'investment_thesis': insights.get('analysis', 'Analysis not available'),
            'market_sentiment': insights.get('market_sentiment', 'Neutral'),
            'risk_level': insights.get('risk_level', 'Medium'),
            'fundamental_score': int(insights.get('fundamental_score', 50)),
            'technical_score': int(insights.get('technical_score', 50)),
            
            # Mobile-optimized styling
            'mobile_analysis_html': f'''
            <div class="mobile-analysis-container">
                <div class="stock-header">
                    <div class="company-name">{stock_data.get('name', 'Unknown Company')} ({stock_data.get('symbol', query.upper())})</div>
                    <div class="current-price">${float(stock_data.get('current_price', 0)):.2f}</div>
                    <div class="price-change">
                        {'+' if float(stock_data.get('price_change', 0)) >= 0 else ''}{float(stock_data.get('price_change', 0)):.2f} 
                        ({'+' if float(stock_data.get('price_change_percent', 0)) >= 0 else ''}{float(stock_data.get('price_change_percent', 0)):.2f}%)
                    </div>
                </div>
                <div class="ai-recommendation">
                    <span class="recommendation-badge">{insights.get('recommendation', 'HOLD')}</span>
                    <span class="confidence-score">{int(insights.get('confidence', 50))}% Confidence</span>
                </div>
                <div class="ai-analysis">{insights.get('analysis', 'Analysis not available')}</div>
            </div>
            ''',
            
            'analysis_actions': [
                {'action': 'addToWatchlist("' + query.upper() + '")', 'text': f'Add {query.upper()} to Watchlist'},
                {'action': 'getHistoricalAnalysis("' + query.upper() + '")', 'text': 'View Analysis History'},
                {'action': 'getDetailedAnalysis("' + query.upper() + '")', 'text': 'Deep Dive Analysis'},
                {'action': 'comparePeers("' + query.upper() + '")', 'text': 'Compare with Competitors'}
            ]
        }
        
        logger.info(f"Stock analysis successful for {query}: {response['symbol']} at ${response['price']} - {response['recommendation']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f'Error in stock_analysis_api: {e}')
        return jsonify({
            'error': 'Analysis failed',
            'message': 'Unable to retrieve analysis data. Please try again.',
            'analysis': f'Unable to analyze {query} - analysis service temporarily unavailable'
        }), 500

@app.route('/api/analysis-history/<symbol>')
def get_analysis_history(symbol):
    """Get historical analysis data for a stock"""
    try:
        analyses = StockAnalysis.query.filter_by(symbol=symbol.upper()).order_by(StockAnalysis.analysis_date.desc()).limit(10).all()
        
        history = []
        for analysis in analyses:
            history.append({
                'date': analysis.analysis_date.isoformat(),
                'price': analysis.price_at_analysis,
                'recommendation': analysis.recommendation,
                'confidence': analysis.confidence_score,
                'fundamental_score': analysis.fundamental_score,
                'technical_score': analysis.technical_score,
                'risk_level': analysis.risk_level
            })
        
        return jsonify({
            'success': True, 
            'symbol': symbol.upper(),
            'analysis_history': history
        })
        
    except Exception as e:
        logger.error(f'Error getting analysis history for {symbol}: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/watchlist/add', methods=['POST'])
def add_to_analysis_watchlist():
    """Add stock to analysis watchlist for tracking"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        notes = data.get('notes', '')
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Symbol required'}), 400
            
        # Add to demo watchlist (in production, save to database)
        demo_watchlist.add(symbol)
        
        # Save to database for future tracking
        watchlist_item = WatchlistItem()
        watchlist_item.symbol = symbol
        watchlist_item.notes = notes
        db.session.add(watchlist_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{symbol} added to analysis watchlist',
            'watchlist': list(demo_watchlist)
        })
        
    except Exception as e:
        logger.error(f'Error adding to analysis watchlist: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analysis-watchlist')
def get_analysis_watchlist():
    """Get analysis watchlist with current data and latest analysis results"""
    try:
        watchlist_data = []
        
        for symbol in demo_watchlist:
            try:
                stock_data = stock_search_service.search_stock(symbol)
                latest_analysis = StockAnalysis.query.filter_by(symbol=symbol).order_by(StockAnalysis.analysis_date.desc()).first()
                
                if stock_data:
                    item = {
                        'symbol': symbol,
                        'name': stock_data.get('name', symbol),
                        'price': float(stock_data.get('current_price', 0)),
                        'change': float(stock_data.get('price_change', 0)),
                        'change_percent': float(stock_data.get('price_change_percent', 0))
                    }
                    
                    # Add latest analysis if available
                    if latest_analysis:
                        item.update({
                            'latest_recommendation': latest_analysis.recommendation,
                            'latest_confidence': latest_analysis.confidence_score,
                            'analysis_date': latest_analysis.analysis_date.isoformat()
                        })
                    
                    watchlist_data.append(item)
            except Exception as e:
                logger.error(f'Error getting analysis data for {symbol}: {e}')
        
        return jsonify({
            'success': True,
            'watchlist': watchlist_data
        })
        
    except Exception as e:
        logger.error(f'Error getting analysis watchlist: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/alerts/suggestions/<symbol>')
def get_alert_suggestions(symbol):
    """Get smart alert suggestions for a stock symbol"""
    try:
        symbol = symbol.upper()
        
        # Get current stock data for alert suggestions
        stock_data = stock_search_service.search_stock(symbol)
        if not stock_data:
            return jsonify({'success': False, 'error': 'Stock not found'}), 404
            
        current_price = float(stock_data.get('current_price', 0))
        
        # Generate intelligent alert suggestions based on current price and analysis
        suggestions = [
            {
                'type': 'price_target',
                'label': f'Price above ${(current_price * 1.05):.2f}',
                'description': f'Alert when {symbol} rises 5% from current price',
                'condition': 'above',
                'value': current_price * 1.05,
                'category': 'bullish'
            },
            {
                'type': 'price_target', 
                'label': f'Price below ${(current_price * 0.95):.2f}',
                'description': f'Alert when {symbol} drops 5% from current price',
                'condition': 'below',
                'value': current_price * 0.95,
                'category': 'bearish'
            },
            {
                'type': 'technical',
                'label': 'RSI Oversold (< 30)',
                'description': f'Alert when {symbol} RSI indicates oversold conditions',
                'condition': 'rsi_below',
                'value': 30,
                'category': 'technical'
            },
            {
                'type': 'technical', 
                'label': 'RSI Overbought (> 70)',
                'description': f'Alert when {symbol} RSI indicates overbought conditions',
                'condition': 'rsi_above',
                'value': 70,
                'category': 'technical'
            },
            {
                'type': 'volume',
                'label': 'High Volume Spike',
                'description': f'Alert when {symbol} volume exceeds 2x average',
                'condition': 'volume_spike',
                'value': 2.0,
                'category': 'volume'
            }
        ]
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'current_price': current_price,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f'Error getting alert suggestions for {symbol}: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/alerts/create', methods=['POST'])
def create_alert():
    """Create a new price or technical alert for a stock"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        alert_type = data.get('type', 'price_target')
        condition = data.get('condition', 'above')
        value = float(data.get('value', 0))
        description = data.get('description', '')
        
        if not symbol or not value:
            return jsonify({'success': False, 'error': 'Symbol and value required'}), 400
            
        # In production, save alert to database
        # For demo, return success message
        alert_id = f"alert_{symbol}_{int(datetime.now().timestamp())}"
        
        return jsonify({
            'success': True,
            'alert_id': alert_id,
            'message': f'Alert created: {description}',
            'details': {
                'symbol': symbol,
                'type': alert_type,
                'condition': condition,
                'value': value,
                'created_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f'Error creating alert: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/alerts/create-smart', methods=['POST'])
def create_smart_alert():
    """Create smart alerts from AI suggestions"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        alert_configs = data.get('alert_configs', [])
        
        if not symbol or not alert_configs:
            return jsonify({'success': False, 'error': 'Symbol and alert configurations required'}), 400
        
        created_alerts = []
        for config in alert_configs:
            condition = config.get('condition', 'above')
            value = float(config.get('value', 0))
            title = config.get('title', 'Smart Alert')
            
            # Create alert entry
            alert_id = f"smart_alert_{symbol}_{condition}_{int(datetime.now().timestamp())}"
            
            alert_details = {
                'alert_id': alert_id,
                'symbol': symbol,
                'condition': condition,
                'value': value,
                'title': title,
                'created_at': datetime.now().isoformat(),
                'type': 'smart_alert'
            }
            
            created_alerts.append(alert_details)
        
        return jsonify({
            'success': True,
            'message': f'Created {len(created_alerts)} smart alert(s) for {symbol}',
            'alerts': created_alerts
        })
        
    except Exception as e:
        logger.error(f'Error creating smart alerts: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

# Create database tables
with app.app_context():
    db.create_all()