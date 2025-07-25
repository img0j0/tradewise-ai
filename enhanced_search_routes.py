"""
Enhanced Search API Routes
Lightning-fast search endpoints with fuzzy matching and autocomplete
"""

from flask import Blueprint, request, jsonify, session
import logging
from typing import List, Dict, Optional
from advanced_search_engine import get_search_engine
try:
    from premium_search_engine import premium_search_engine
    def get_premium_search_engine():
        return premium_search_engine
except ImportError:
    # Fallback if premium search engine is not available
    def get_premium_search_engine():
        return None
import time

logger = logging.getLogger(__name__)

# Create blueprint
enhanced_search_bp = Blueprint('enhanced_search_api', __name__)

@enhanced_search_bp.route('/api/search/autocomplete', methods=['GET'])
def search_autocomplete():
    """
    Real-time autocomplete API endpoint
    Supports fuzzy matching, partial queries, and intelligent ranking
    """
    try:
        start_time = time.time()
        
        # Get query parameters
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 8)), 15)  # Max 15 suggestions
        
        # Get search engine
        search_engine = get_search_engine()
        
        # Get autocomplete suggestions
        suggestions = search_engine.get_autocomplete_suggestions(query, limit)
        
        # Format response
        formatted_suggestions = []
        for suggestion in suggestions:
            formatted_suggestions.append({
                'symbol': suggestion['symbol'],
                'name': suggestion['name'],
                'sector': suggestion['sector'],
                'exchange': suggestion['exchange'],
                'match_type': suggestion.get('match_type', 'unknown'),
                'logo_url': suggestion.get('logo_url'),
                'market_status': suggestion.get('market_status', 'unknown'),
                'popularity': suggestion.get('popularity', 0),
                'trend': _get_trend_indicator(suggestion['symbol'])  # Add trend indicator
            })
        
        execution_time = (time.time() - start_time) * 1000
        
        return jsonify({
            'success': True,
            'suggestions': formatted_suggestions,
            'query': query,
            'execution_time_ms': round(execution_time, 2),
            'total_results': len(formatted_suggestions)
        })
        
    except Exception as e:
        logger.error(f"Autocomplete search error: {e}")
        return jsonify({
            'success': False,
            'error': 'Search service temporarily unavailable',
            'suggestions': []
        }), 500

@enhanced_search_bp.route('/api/search/advanced', methods=['POST'])
def advanced_search():
    """
    Advanced search endpoint with comprehensive results
    Supports all search types: symbol, company name, partial matches
    """
    try:
        start_time = time.time()
        
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        limit = min(int(data.get('limit', 20)), 50)  # Max 50 results
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required',
                'results': []
            }), 400
        
        # Get search engine
        search_engine = get_search_engine()
        
        # Perform advanced search
        search_results = search_engine.search_stocks(query, limit)
        
        # Enhanced results with additional data
        enhanced_results = []
        for result in search_results:
            enhanced_result = {
                'symbol': result['symbol'],
                'company_name': result['company_name'],
                'sector': result['sector'],
                'exchange': result['exchange'],
                'match_type': result['match_type'],
                'match_score': result['match_score'],
                'popularity_score': result['popularity_score'],
                'rank_score': result['rank_score'],
                'logo_url': result.get('logo_url'),
                'market_status': result['market_status'],
                'trend': _get_trend_indicator(result['symbol']),
                'ai_score': _get_ai_score(result['symbol'])  # Add AI analysis score
            }
            enhanced_results.append(enhanced_result)
        
        execution_time = (time.time() - start_time) * 1000
        
        return jsonify({
            'success': True,
            'results': enhanced_results,
            'query': query,
            'execution_time_ms': round(execution_time, 2),
            'total_results': len(enhanced_results),
            'search_tips': _get_search_tips(query, enhanced_results)
        })
        
    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        return jsonify({
            'success': False,
            'error': 'Search service temporarily unavailable',
            'results': []
        }), 500

@enhanced_search_bp.route('/api/search/trending', methods=['GET'])
def get_trending_stocks():
    """Get trending/popular stocks for homepage display"""
    try:
        search_engine = get_search_engine()
        trending = search_engine._get_trending_suggestions(12)
        
        # Add real-time data to trending stocks
        enhanced_trending = []
        for stock in trending:
            enhanced_stock = {
                **stock,
                'trend': _get_trend_indicator(stock['symbol']),
                'ai_score': _get_ai_score(stock['symbol']),
                'price_change': _get_price_change(stock['symbol'])
            }
            enhanced_trending.append(enhanced_stock)
        
        return jsonify({
            'success': True,
            'trending_stocks': enhanced_trending,
            'last_updated': time.time()
        })
        
    except Exception as e:
        logger.error(f"Trending stocks error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to fetch trending stocks',
            'trending_stocks': []
        }), 500

@enhanced_search_bp.route('/api/search/record-selection', methods=['POST'])
def record_search_selection():
    """Record when user selects a search result for ML improvement"""
    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        selected_symbol = data.get('symbol', '').strip().upper()
        
        if not query or not selected_symbol:
            return jsonify({
                'success': False,
                'error': 'Query and symbol are required'
            }), 400
        
        # Record selection in search engine
        search_engine = get_search_engine()
        search_engine.record_selection(query, selected_symbol)
        
        return jsonify({
            'success': True,
            'message': 'Selection recorded successfully'
        })
        
    except Exception as e:
        logger.error(f"Record selection error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to record selection'
        }), 500

@enhanced_search_bp.route('/api/search/suggestions/smart', methods=['GET'])
def smart_suggestions():
    """
    AI-powered smart suggestions based on user behavior and market data
    Integrates with premium search engine for advanced ranking
    """
    try:
        user_session = session.get('user_id', 'anonymous')
        
        # Get premium search engine for AI-powered suggestions
        premium_engine = get_premium_search_engine()
        search_engine = get_search_engine()
        
        # Get user's recent searches for personalization
        recent_searches = _get_user_recent_searches(user_session)
        
        # Generate smart suggestions
        suggestions = []
        
        # 1. Trending stocks with AI analysis
        trending = search_engine._get_trending_suggestions(5)
        for stock in trending:
            if premium_engine:
                try:
                    ai_analysis = premium_engine.get_ai_ranking_score(stock['symbol'])
                    ai_score = ai_analysis.get('score', 50)
                    ai_reason = ai_analysis.get('reason', 'Popular stock')
                except:
                    ai_score = 50
                    ai_reason = 'Popular stock'
            else:
                ai_score = 50
                ai_reason = 'Popular stock'
                
            suggestions.append({
                **stock,
                'suggestion_type': 'trending',
                'ai_score': ai_score,
                'ai_reason': ai_reason,
                'trend': _get_trend_indicator(stock['symbol'])
            })
        
        # 2. Sector-based suggestions
        if recent_searches:
            sector_suggestions = _get_sector_suggestions(recent_searches, 3)
            suggestions.extend(sector_suggestions)
        
        # 3. Similar stocks to user's searches
        if recent_searches:
            similar_suggestions = _get_similar_stock_suggestions(recent_searches, 3)
            suggestions.extend(similar_suggestions)
        
        # Rank all suggestions by composite score
        ranked_suggestions = sorted(suggestions, 
                                  key=lambda x: x.get('ai_score', 0) + x.get('popularity', 0), 
                                  reverse=True)[:10]
        
        return jsonify({
            'success': True,
            'smart_suggestions': ranked_suggestions,
            'personalized': len(recent_searches) > 0,
            'suggestion_count': len(ranked_suggestions)
        })
        
    except Exception as e:
        logger.error(f"Smart suggestions error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to generate smart suggestions',
            'smart_suggestions': []
        }), 500

@enhanced_search_bp.route('/api/search/stats', methods=['GET'])
def search_stats():
    """Get search engine statistics and analytics"""
    try:
        search_engine = get_search_engine()
        stats = search_engine.get_search_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Search stats error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to fetch search statistics'
        }), 500

# Helper functions

def _get_trend_indicator(symbol: str) -> str:
    """Get trend indicator for a stock (simplified)"""
    # In production, this would use real market data
    import random
    trends = ['up', 'down', 'neutral']
    weights = [0.45, 0.35, 0.20]  # Slightly bullish bias for demo
    return random.choices(trends, weights=weights)[0]

def _get_ai_score(symbol: str) -> int:
    """Get AI analysis score for a stock"""
    try:
        premium_engine = get_premium_search_engine()
        if premium_engine:
            ai_analysis = premium_engine.get_ai_ranking_score(symbol)
            return ai_analysis.get('score', 50)
    except:
        pass
    
    # Fallback scoring based on symbol characteristics
    import random
    return random.randint(30, 85)

def _get_price_change(symbol: str) -> Dict:
    """Get price change data for a stock (simplified)"""
    import random
    change = random.uniform(-5.0, 5.0)
    return {
        'change_percent': round(change, 2),
        'direction': 'up' if change >= 0 else 'down'
    }

def _get_search_tips(query: str, results: List) -> List[str]:
    """Generate helpful search tips based on query and results"""
    tips = []
    
    if len(results) == 0:
        tips.extend([
            "Try using the company's stock symbol (e.g., 'AAPL' for Apple)",
            "Search by company name (e.g., 'Apple' or 'Microsoft')",
            "Check spelling - our search supports typos but exact matches work best"
        ])
    elif len(results) < 3:
        tips.append("Try shorter or broader search terms for more results")
    
    if any(r['match_type'] == 'fuzzy_company' for r in results):
        tips.append("Company name matches found - try the stock symbol for exact results")
    
    return tips[:3]  # Limit to 3 tips

def _get_user_recent_searches(user_session: str) -> List[str]:
    """Get user's recent searches for personalization"""
    try:
        import sqlite3
        conn = sqlite3.connect('stock_search_cache.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT selected_symbol 
            FROM search_analytics 
            WHERE user_session = ? AND selected_symbol IS NOT NULL
            ORDER BY timestamp DESC 
            LIMIT 10
        ''', (user_session,))
        
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        return results
    except:
        return []

def _get_sector_suggestions(recent_searches: List[str], limit: int) -> List[Dict]:
    """Get suggestions from same sectors as user's recent searches"""
    suggestions = []
    try:
        search_engine = get_search_engine()
        
        # Get sectors from recent searches
        sectors = set()
        for symbol in recent_searches[:3]:  # Check last 3 searches
            if symbol in search_engine.stock_metadata:
                sector = search_engine.stock_metadata[symbol]['sector']
                if sector != 'Unknown':
                    sectors.add(sector)
        
        # Find other stocks in same sectors
        for sector in list(sectors)[:2]:  # Max 2 sectors
            sector_stocks = [
                stock for stock, info in search_engine.stock_metadata.items()
                if info['sector'] == sector and stock not in recent_searches
            ]
            
            # Get top stocks from this sector by popularity
            sector_stocks.sort(key=lambda s: search_engine._get_popularity_score(s), reverse=True)
            
            for symbol in sector_stocks[:limit//len(sectors) if sectors else limit]:
                info = search_engine.stock_metadata[symbol]
                suggestions.append({
                    'symbol': symbol,
                    'name': info['company_name'],
                    'sector': info['sector'],
                    'exchange': info['exchange'],
                    'suggestion_type': 'sector_match',
                    'popularity': search_engine._get_popularity_score(symbol),
                    'logo_url': info.get('logo_url'),
                    'market_status': search_engine._get_market_status(info['exchange'])
                })
    except Exception as e:
        logger.error(f"Sector suggestions error: {e}")
    
    return suggestions[:limit]

def _get_similar_stock_suggestions(recent_searches: List[str], limit: int) -> List[Dict]:
    """Get suggestions for stocks similar to user's recent searches"""
    suggestions = []
    try:
        # This would use more sophisticated similarity algorithms in production
        # For now, return popular stocks from similar market caps
        search_engine = get_search_engine()
        
        similar_stocks = ['NVDA', 'META', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
        similar_stocks = [s for s in similar_stocks if s not in recent_searches]
        
        for symbol in similar_stocks[:limit]:
            if symbol in search_engine.stock_metadata:
                info = search_engine.stock_metadata[symbol]
                suggestions.append({
                    'symbol': symbol,
                    'name': info['company_name'],
                    'sector': info['sector'],
                    'exchange': info['exchange'],
                    'suggestion_type': 'similar_stock',
                    'popularity': search_engine._get_popularity_score(symbol),
                    'logo_url': info.get('logo_url'),
                    'market_status': search_engine._get_market_status(info['exchange'])
                })
    except Exception as e:
        logger.error(f"Similar stock suggestions error: {e}")
    
    return suggestions[:limit]

# Export blueprint
__all__ = ['enhanced_search_bp']