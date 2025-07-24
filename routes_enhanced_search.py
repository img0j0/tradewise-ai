"""
Enhanced Search Routes for TradeWise AI
Provides advanced search functionality with filters, sorting, and contextual search
"""

from flask import Blueprint, request, jsonify, session
from models import db, SearchHistory, FavoriteStock
import yfinance as yf
from datetime import datetime, timedelta
import logging

enhanced_search_bp = Blueprint('enhanced_search', __name__)

@enhanced_search_bp.route('/api/search/enhanced', methods=['GET'])
def enhanced_search():
    """Enhanced search with premium/free tier distinction"""
    try:
        from premium_search_engine import premium_search_engine
        
        query = request.args.get('q', '').strip()
        sector_filter = request.args.get('sector', '')
        market_cap_filter = request.args.get('market_cap', '')  # small, mid, large
        sort_by = request.args.get('sort', 'relevance')  # relevance, price, volume, market_cap
        limit = min(int(request.args.get('limit', 20)), 50)
        
        if not query or len(query) < 2:
            return jsonify({'error': 'Query too short', 'success': False}), 400
        
        # Use premium search engine for advanced capabilities
        results = premium_search_engine.enhanced_search(
            query=query,
            sector=sector_filter,
            market_cap=market_cap_filter,
            sort_by=sort_by,
            limit=limit
        )
        
        # Check if premium features are available
        is_premium = premium_search_engine.check_premium_access()
        
        return jsonify({
            'success': True,
            'results': results,
            'total_results': len(results),
            'is_premium': is_premium,
            'premium_features_available': not is_premium,  # Show upgrade prompts for free users
            'filters_applied': {
                'query': query,
                'sector': sector_filter,
                'market_cap': market_cap_filter,
                'sort_by': sort_by
            }
        })
        
    except Exception as e:
        logging.error(f"Enhanced search error: {e}")
        return jsonify({'error': 'Search failed', 'success': False}), 500

@enhanced_search_bp.route('/api/search/filters', methods=['GET'])
def get_search_filters():
    """Get available search filters and their options"""
    try:
        return jsonify({
            'success': True,
            'filters': {
                'sectors': [
                    {'value': 'technology', 'label': 'Technology', 'count': 8},
                    {'value': 'healthcare', 'label': 'Healthcare', 'count': 3},
                    {'value': 'financial', 'label': 'Financial', 'count': 3},
                    {'value': 'consumer', 'label': 'Consumer', 'count': 3},
                    {'value': 'energy', 'label': 'Energy', 'count': 2},
                    {'value': 'industrial', 'label': 'Industrial', 'count': 2}
                ],
                'market_caps': [
                    {'value': 'large', 'label': 'Large Cap', 'description': '$10B+'},
                    {'value': 'mid', 'label': 'Mid Cap', 'description': '$2B-$10B'},
                    {'value': 'small', 'label': 'Small Cap', 'description': '<$2B'}
                ],
                'sort_options': [
                    {'value': 'relevance', 'label': 'Relevance'},
                    {'value': 'price', 'label': 'Price (High to Low)'},
                    {'value': 'volume', 'label': 'Volume (High to Low)'},
                    {'value': 'market_cap', 'label': 'Market Cap (High to Low)'},
                    {'value': 'change', 'label': 'Price Change % (High to Low)'}
                ]
            }
        })
    except Exception as e:
        logging.error(f"Get filters error: {e}")
        return jsonify({'error': 'Failed to get filters', 'success': False}), 500

@enhanced_search_bp.route('/api/search/trending', methods=['GET'])
def get_trending_searches():
    """Get trending searches based on recent search history"""
    try:
        # Get top searched stocks from last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        
        trending_stocks = db.session.query(SearchHistory.symbol, db.func.count(SearchHistory.id).label('count'))\
                                  .filter(SearchHistory.searched_at >= week_ago)\
                                  .group_by(SearchHistory.symbol)\
                                  .order_by(db.func.count(SearchHistory.id).desc())\
                                  .limit(10).all()
        
        trending_list = []
        for symbol, count in trending_stocks:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                trending_list.append({
                    'symbol': symbol,
                    'name': info.get('longName', symbol),
                    'current_price': info.get('currentPrice', 0),
                    'price_change_pct': info.get('regularMarketChangePercent', 0),
                    'search_count': count
                })
            except:
                continue
        
        return jsonify({
            'success': True,
            'trending': trending_list
        })
        
    except Exception as e:
        logging.error(f"Get trending error: {e}")
        return jsonify({'error': 'Failed to get trending', 'success': False}), 500