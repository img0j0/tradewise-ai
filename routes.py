from flask import render_template, jsonify, request, make_response
from app import app, db
from models import Trade, Portfolio, Alert, UserAccount, Transaction, User
from ai_insights import AIInsightsEngine
from data_service import DataService
from stock_search import StockSearchService
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize core services only
data_service = DataService()
ai_engine = AIInsightsEngine()
stock_search_service = StockSearchService()

# Simple demo watchlist storage
demo_watchlist = set(['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA'])

# Train AI model on startup
try:
    stocks_data = data_service.get_all_stocks()
    ai_engine.train_model(stocks_data)
    logger.info("AI model trained successfully")
except Exception as e:
    logger.error(f"Error training AI model: {e}")

@app.route('/')
def index():
    """Clean ChatGPT-style search interface"""
    try:
        response = make_response(render_template('clean_chatgpt_search.html'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        logger.error(f"Error loading template: {e}")
        return jsonify({'error': 'Template loading error'}), 500

@app.route('/api/stock-search', methods=['POST'])
def stock_search_api():
    """Enhanced real-time stock search API for ChatGPT-style interface"""
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
        
        # Get comprehensive AI insights with real-time analysis
        ai_engine = AIInsightsEngine()
        insights = ai_engine.get_insights(query.upper(), stock_data)
        
        # Build comprehensive real-time response
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
            
            # AI Analysis
            'analysis': insights.get('recommendation', 'HOLD'),
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
            
            'quick_actions': [
                {'action': 'addToWatchlist("' + query.upper() + '")', 'text': f'Add {query.upper()} to Watchlist'},
                {'action': 'setAlert("' + query.upper() + '")', 'text': 'Set Price Alert'},
                {'action': 'getDetailedAnalysis("' + query.upper() + '")', 'text': 'Get Detailed Analysis'},
                {'action': 'comparePeers("' + query.upper() + '")', 'text': 'Compare with Peers'}
            ]
        }
        
        logger.info(f"Stock search successful for {query}: {response['symbol']} at ${response['price']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f'Error in stock_search_api: {e}')
        return jsonify({
            'error': 'Search failed',
            'message': 'Unable to retrieve real-time data. Please try again.',
            'analysis': f'Unable to analyze {query} - service temporarily unavailable'
        }), 500

@app.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist():
    """Add stock to watchlist"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Symbol required'}), 400
            
        # Add to demo watchlist
        demo_watchlist.add(symbol)
        
        return jsonify({
            'success': True,
            'message': f'{symbol} added to watchlist',
            'watchlist': list(demo_watchlist)
        })
        
    except Exception as e:
        logger.error(f'Error adding to watchlist: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """Get user watchlist with real-time data"""
    try:
        watchlist_data = []
        
        for symbol in demo_watchlist:
            try:
                stock_data = stock_search_service.search_stock(symbol)
                if stock_data:
                    watchlist_data.append({
                        'symbol': symbol,
                        'name': stock_data.get('name', symbol),
                        'price': float(stock_data.get('current_price', 0)),
                        'change': float(stock_data.get('price_change', 0)),
                        'change_percent': float(stock_data.get('price_change_percent', 0))
                    })
            except Exception as e:
                logger.error(f'Error getting data for {symbol}: {e}')
        
        return jsonify({
            'success': True,
            'watchlist': watchlist_data
        })
        
    except Exception as e:
        logger.error(f'Error getting watchlist: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

# Create database tables
with app.app_context():
    db.create_all()