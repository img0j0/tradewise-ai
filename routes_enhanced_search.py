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
    """Enhanced search with filters and sorting options"""
    try:
        query = request.args.get('q', '').strip()
        sector_filter = request.args.get('sector', '')
        market_cap_filter = request.args.get('market_cap', '')  # small, mid, large
        sort_by = request.args.get('sort', 'relevance')  # relevance, price, volume, market_cap
        limit = min(int(request.args.get('limit', 20)), 50)
        
        if not query or len(query) < 2:
            return jsonify({'error': 'Query too short', 'success': False}), 400
        
        # Enhanced stock database with more detailed information
        enhanced_stocks = [
            # Technology - Large Cap
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology', 'market_cap': 'large', 'industry': 'Consumer Electronics'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'sector': 'Technology', 'market_cap': 'large', 'industry': 'Software'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'sector': 'Technology', 'market_cap': 'large', 'industry': 'Internet Services'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'sector': 'Technology', 'market_cap': 'large', 'industry': 'Semiconductors'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'sector': 'Technology', 'market_cap': 'large', 'industry': 'Social Media'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'sector': 'Technology', 'market_cap': 'large', 'industry': 'Electric Vehicles'},
            
            # Healthcare - Various Caps
            {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'sector': 'Healthcare', 'market_cap': 'large', 'industry': 'Pharmaceuticals'},
            {'symbol': 'PFE', 'name': 'Pfizer Inc.', 'sector': 'Healthcare', 'market_cap': 'large', 'industry': 'Pharmaceuticals'},
            {'symbol': 'MRNA', 'name': 'Moderna Inc.', 'sector': 'Healthcare', 'market_cap': 'mid', 'industry': 'Biotechnology'},
            
            # Financial Services
            {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.', 'sector': 'Financial', 'market_cap': 'large', 'industry': 'Banking'},
            {'symbol': 'BAC', 'name': 'Bank of America Corporation', 'sector': 'Financial', 'market_cap': 'large', 'industry': 'Banking'},
            {'symbol': 'GS', 'name': 'Goldman Sachs Group Inc.', 'sector': 'Financial', 'market_cap': 'large', 'industry': 'Investment Banking'},
            
            # Consumer & Retail
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'sector': 'Consumer', 'market_cap': 'large', 'industry': 'E-commerce'},
            {'symbol': 'WMT', 'name': 'Walmart Inc.', 'sector': 'Consumer', 'market_cap': 'large', 'industry': 'Retail'},
            {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'sector': 'Consumer', 'market_cap': 'large', 'industry': 'Streaming'},
            
            # Energy & Materials
            {'symbol': 'XOM', 'name': 'Exxon Mobil Corporation', 'sector': 'Energy', 'market_cap': 'large', 'industry': 'Oil & Gas'},
            {'symbol': 'CVX', 'name': 'Chevron Corporation', 'sector': 'Energy', 'market_cap': 'large', 'industry': 'Oil & Gas'},
            
            # Industrial
            {'symbol': 'BA', 'name': 'Boeing Company', 'sector': 'Industrial', 'market_cap': 'large', 'industry': 'Aerospace'},
            {'symbol': 'CAT', 'name': 'Caterpillar Inc.', 'sector': 'Industrial', 'market_cap': 'large', 'industry': 'Machinery'},
            
            # Emerging/Mid-cap
            {'symbol': 'RIVN', 'name': 'Rivian Automotive Inc.', 'sector': 'Technology', 'market_cap': 'mid', 'industry': 'Electric Vehicles'},
            {'symbol': 'PLTR', 'name': 'Palantir Technologies Inc.', 'sector': 'Technology', 'market_cap': 'mid', 'industry': 'Data Analytics'},
            {'symbol': 'SNOW', 'name': 'Snowflake Inc.', 'sector': 'Technology', 'market_cap': 'mid', 'industry': 'Cloud Computing'},
        ]
        
        # Filter by query (symbol or name)
        query_lower = query.lower()
        filtered_stocks = [
            stock for stock in enhanced_stocks
            if query_lower in stock['symbol'].lower() or query_lower in stock['name'].lower()
        ]
        
        # Apply sector filter
        if sector_filter:
            filtered_stocks = [s for s in filtered_stocks if s['sector'].lower() == sector_filter.lower()]
        
        # Apply market cap filter
        if market_cap_filter:
            filtered_stocks = [s for s in filtered_stocks if s['market_cap'] == market_cap_filter.lower()]
        
        # Get real-time data for matched stocks
        enhanced_results = []
        for stock in filtered_stocks[:limit]:
            try:
                ticker = yf.Ticker(stock['symbol'])
                info = ticker.info
                hist = ticker.history(period='1d', interval='1m')
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = info.get('previousClose', current_price)
                    price_change = current_price - prev_close
                    price_change_pct = (price_change / prev_close * 100) if prev_close else 0
                    
                    enhanced_results.append({
                        'symbol': stock['symbol'],
                        'name': stock['name'],
                        'sector': stock['sector'],
                        'industry': stock['industry'],
                        'market_cap': stock['market_cap'],
                        'current_price': round(current_price, 2),
                        'price_change': round(price_change, 2),
                        'price_change_pct': round(price_change_pct, 2),
                        'volume': info.get('volume', 0),
                        'market_cap_value': info.get('marketCap', 0),
                        'pe_ratio': info.get('trailingPE', 0),
                        'relevance_score': calculate_relevance_score(stock, query)
                    })
            except Exception as e:
                logging.warning(f"Failed to get data for {stock['symbol']}: {e}")
                continue
        
        # Sort results
        if sort_by == 'price':
            enhanced_results.sort(key=lambda x: x['current_price'], reverse=True)
        elif sort_by == 'volume':
            enhanced_results.sort(key=lambda x: x['volume'], reverse=True)
        elif sort_by == 'market_cap':
            enhanced_results.sort(key=lambda x: x['market_cap_value'], reverse=True)
        elif sort_by == 'change':
            enhanced_results.sort(key=lambda x: x['price_change_pct'], reverse=True)
        else:  # relevance (default)
            enhanced_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'results': enhanced_results,
            'total_results': len(enhanced_results),
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

def calculate_relevance_score(stock, query):
    """Calculate relevance score for search ranking"""
    score = 0
    query_lower = query.lower()
    
    # Exact symbol match gets highest score
    if query_lower == stock['symbol'].lower():
        score += 100
    elif stock['symbol'].lower().startswith(query_lower):
        score += 80
    elif query_lower in stock['symbol'].lower():
        score += 60
    
    # Name matching
    if query_lower in stock['name'].lower():
        score += 40
        if stock['name'].lower().startswith(query_lower):
            score += 20
    
    return score

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
        
        trending_queries = db.session.query(
            SearchHistory.symbol,
            SearchHistory.company_name,
            db.func.count(SearchHistory.id).label('search_count'),
            db.func.max(SearchHistory.timestamp).label('last_search')
        ).filter(
            SearchHistory.timestamp >= week_ago
        ).group_by(
            SearchHistory.symbol, SearchHistory.company_name
        ).order_by(
            db.func.count(SearchHistory.id).desc()
        ).limit(10).all()
        
        trending_results = []
        for trend in trending_queries:
            trending_results.append({
                'symbol': trend.symbol,
                'company_name': trend.company_name or trend.symbol,
                'search_count': trend.search_count,
                'last_search': trend.last_search.isoformat() if trend.last_search else None
            })
        
        return jsonify({
            'success': True,
            'trending': trending_results,
            'period': '7 days'
        })
        
    except Exception as e:
        logging.error(f"Get trending searches error: {e}")
        return jsonify({'error': 'Failed to get trending searches', 'success': False}), 500

@enhanced_search_bp.route('/api/search/context', methods=['GET'])
def get_search_context():
    """Get contextual information for enhanced search experience"""
    try:
        symbol = request.args.get('symbol', '').upper()
        
        if not symbol:
            return jsonify({'error': 'Symbol required', 'success': False}), 400
        
        context_info = {
            'symbol': symbol,
            'related_searches': [],
            'sector_peers': [],
            'recent_news_count': 0,
            'earnings_proximity': None,
            'market_events': []
        }
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get sector information
            sector = info.get('sector', '')
            industry = info.get('industry', '')
            
            # Find sector peers (simplified)
            sector_mapping = {
                'Technology': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META'],
                'Healthcare': ['JNJ', 'PFE', 'MRNA'],
                'Financial Services': ['JPM', 'BAC', 'GS'],
                'Consumer Cyclical': ['AMZN', 'NFLX', 'TSLA'],
                'Energy': ['XOM', 'CVX'],
                'Industrials': ['BA', 'CAT']
            }
            
            peers = sector_mapping.get(sector, [])
            context_info['sector_peers'] = [p for p in peers if p != symbol][:5]
            
            # Check for upcoming earnings (simplified)
            # In a real implementation, you'd use a financial calendar API
            context_info['earnings_proximity'] = "Earnings in 12 days"  # Placeholder
            
            context_info['sector'] = sector
            context_info['industry'] = industry
            
        except Exception as e:
            logging.warning(f"Failed to get context for {symbol}: {e}")
        
        return jsonify({
            'success': True,
            'context': context_info
        })
        
    except Exception as e:
        logging.error(f"Get search context error: {e}")
        return jsonify({'error': 'Failed to get search context', 'success': False}), 500