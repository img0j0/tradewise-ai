"""
User Engagement Routes
API endpoints for enhanced search, peer comparison, and portfolio backtesting
"""

from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from premium_features import premium_required
from enhanced_search_autocomplete import enhanced_search_autocomplete
from peer_comparison_engine import peer_comparison_engine
from portfolio_backtesting_engine import portfolio_backtesting_engine
import logging

logger = logging.getLogger(__name__)

# Create blueprint
engagement_bp = Blueprint('engagement', __name__)

# Enhanced Search Autocomplete Endpoints
@engagement_bp.route('/api/search/autocomplete')
def search_autocomplete():
    """Enhanced search autocomplete with personalization"""
    try:
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 8)), 15)
        
        suggestions = enhanced_search_autocomplete.get_autocomplete_suggestions(query, limit)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'query': query,
            'count': len(suggestions)
        })
        
    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        return jsonify({
            'success': False,
            'error': 'Search suggestions temporarily unavailable'
        }), 500

@engagement_bp.route('/api/search/recent')
def get_recent_searches():
    """Get user's recent searches"""
    try:
        recent_searches = session.get('recent_searches', [])
        
        return jsonify({
            'success': True,
            'recent_searches': recent_searches[:10],
            'count': len(recent_searches)
        })
        
    except Exception as e:
        logger.error(f"Recent searches error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to retrieve recent searches'
        }), 500

@engagement_bp.route('/api/search/starred', methods=['GET', 'POST'])
def manage_starred_symbols():
    """Get or toggle starred symbols"""
    try:
        if request.method == 'GET':
            starred_symbols = enhanced_search_autocomplete.get_starred_symbols()
            
            return jsonify({
                'success': True,
                'starred_symbols': starred_symbols,
                'count': len(starred_symbols)
            })
        
        elif request.method == 'POST':
            data = request.get_json()
            symbol = data.get('symbol', '').upper()
            
            if not symbol:
                return jsonify({
                    'success': False,
                    'error': 'Symbol is required'
                }), 400
            
            action = enhanced_search_autocomplete.toggle_starred_symbol(symbol)
            
            return jsonify({
                'success': True,
                'symbol': symbol,
                'action': action,
                'message': f"Symbol {symbol} {action} from favorites"
            })
            
    except Exception as e:
        logger.error(f"Starred symbols error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to manage starred symbols'
        }), 500

@engagement_bp.route('/api/search/add-recent', methods=['POST'])
def add_recent_search():
    """Add a search to recent searches"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        name = data.get('name', '')
        sector = data.get('sector', '')
        
        if not symbol:
            return jsonify({
                'success': False,
                'error': 'Symbol is required'
            }), 400
        
        enhanced_search_autocomplete.add_to_recent_searches(symbol, name, sector)
        
        return jsonify({
            'success': True,
            'message': 'Added to recent searches'
        })
        
    except Exception as e:
        logger.error(f"Add recent search error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to add to recent searches'
        }), 500

# Peer Comparison Endpoints (Premium)
@engagement_bp.route('/api/peer-comparison/<symbol>')
@premium_required
def get_peer_comparison(symbol):
    """Get peer comparison analysis (Premium feature)"""
    try:
        comparison_data = peer_comparison_engine.get_peer_comparison(symbol)
        
        if not comparison_data.get('success'):
            return jsonify(comparison_data), 404
        
        return jsonify(comparison_data)
        
    except Exception as e:
        logger.error(f"Peer comparison error for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': 'Peer comparison service temporarily unavailable'
        }), 500

@engagement_bp.route('/api/sector-benchmark/<sector>')
@premium_required
def get_sector_benchmark(sector):
    """Get sector benchmarking analysis (Premium feature)"""
    try:
        benchmark_data = peer_comparison_engine.get_sector_benchmark(sector)
        
        if not benchmark_data.get('success'):
            return jsonify(benchmark_data), 404
        
        return jsonify(benchmark_data)
        
    except Exception as e:
        logger.error(f"Sector benchmark error for {sector}: {e}")
        return jsonify({
            'success': False,
            'error': 'Sector benchmark service temporarily unavailable'
        }), 500

@engagement_bp.route('/api/sectors/available')
def get_available_sectors():
    """Get list of available sectors for benchmarking"""
    try:
        sectors = list(peer_comparison_engine.sector_symbols.keys())
        
        return jsonify({
            'success': True,
            'sectors': sectors,
            'count': len(sectors)
        })
        
    except Exception as e:
        logger.error(f"Available sectors error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to retrieve available sectors'
        }), 500

# Portfolio Backtesting Endpoints (Premium)
@engagement_bp.route('/api/portfolio/backtest', methods=['POST'])
@premium_required
def run_portfolio_backtest():
    """Run portfolio backtesting analysis (Premium feature)"""
    try:
        data = request.get_json()
        
        portfolio_data = data.get('portfolio', [])
        strategy_params = data.get('strategy_params', {})
        benchmark = data.get('benchmark', 'SPY')
        
        if not portfolio_data:
            return jsonify({
                'success': False,
                'error': 'Portfolio data is required'
            }), 400
        
        # Run backtest
        backtest_results = portfolio_backtesting_engine.run_backtest(
            portfolio_data, strategy_params, benchmark
        )
        
        if not backtest_results.get('success'):
            return jsonify(backtest_results), 400
        
        return jsonify(backtest_results)
        
    except Exception as e:
        logger.error(f"Portfolio backtest error: {e}")
        return jsonify({
            'success': False,
            'error': 'Portfolio backtesting service temporarily unavailable'
        }), 500

@engagement_bp.route('/api/portfolio/backtest/benchmarks')
def get_available_benchmarks():
    """Get available benchmark options for backtesting"""
    try:
        benchmarks = portfolio_backtesting_engine.benchmarks
        
        return jsonify({
            'success': True,
            'benchmarks': [
                {'symbol': symbol, 'name': name} 
                for symbol, name in benchmarks.items()
            ],
            'count': len(benchmarks)
        })
        
    except Exception as e:
        logger.error(f"Available benchmarks error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to retrieve available benchmarks'
        }), 500

@engagement_bp.route('/api/portfolio/validate', methods=['POST'])
def validate_portfolio():
    """Validate portfolio structure before backtesting"""
    try:
        data = request.get_json()
        portfolio_data = data.get('portfolio', [])
        
        if not portfolio_data:
            return jsonify({
                'success': False,
                'error': 'Portfolio data is required'
            }), 400
        
        # Validate portfolio structure
        total_weight = 0
        valid_holdings = []
        
        for holding in portfolio_data:
            symbol = holding.get('symbol', '').upper()
            weight = holding.get('weight', 0)
            
            try:
                weight = float(weight)
                if weight <= 0:
                    continue
            except (ValueError, TypeError):
                continue
            
            if symbol:
                valid_holdings.append({
                    'symbol': symbol,
                    'weight': weight
                })
                total_weight += weight
        
        is_valid = len(valid_holdings) > 0 and total_weight > 0
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'valid_holdings': valid_holdings,
            'total_weight': total_weight,
            'normalized_weights': [
                {
                    'symbol': h['symbol'], 
                    'weight': h['weight'] / total_weight
                } for h in valid_holdings
            ] if total_weight > 0 else [],
            'validation_errors': [] if is_valid else ['Portfolio must contain at least one valid holding with positive weight']
        })
        
    except Exception as e:
        logger.error(f"Portfolio validation error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to validate portfolio'
        }), 500

# Enhanced Search Analytics (Free tier)
@engagement_bp.route('/api/search/analytics')
def get_search_analytics():
    """Get search analytics and trending symbols"""
    try:
        # Get popular search terms from autocomplete engine
        popular_stocks = enhanced_search_autocomplete.popular_stocks
        
        # Get top trending stocks (simulated based on popular stocks)
        trending = []
        for symbol, info in list(popular_stocks.items())[:10]:
            trending.append({
                'symbol': symbol,
                'name': info['name'],
                'sector': info['sector'],
                'tags': info.get('tags', []),
                'trend_score': hash(symbol) % 100  # Simulated trend score
            })
        
        # Sort by trend score
        trending.sort(key=lambda x: x['trend_score'], reverse=True)
        
        from datetime import datetime
        
        return jsonify({
            'success': True,
            'trending_stocks': trending[:5],
            'popular_sectors': ['Technology', 'Healthcare', 'Financial Services', 'Consumer Discretionary'],
            'hot_tags': ['ai', 'ev', 'cloud', 'biotech', 'fintech'],
            'analytics_date': str(datetime.now().date())
        })
        
    except Exception as e:
        logger.error(f"Search analytics error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to retrieve search analytics'
        }), 500

# User engagement metrics (internal)
@engagement_bp.route('/api/engagement/metrics')
def get_engagement_metrics():
    """Get user engagement metrics for analytics"""
    try:
        # Get session-based metrics
        recent_searches = session.get('recent_searches', [])
        starred_symbols = session.get('starred_symbols', [])
        
        metrics = {
            'recent_searches_count': len(recent_searches),
            'starred_symbols_count': len(starred_symbols),
            'last_search_date': recent_searches[0].get('timestamp') if recent_searches else None,
            'favorite_sectors': {},
            'search_patterns': {
                'symbol_searches': 0,
                'company_name_searches': 0,
                'sector_searches': 0
            }
        }
        
        # Analyze search patterns
        for search in recent_searches:
            sector = search.get('sector', 'Unknown')
            metrics['favorite_sectors'][sector] = metrics['favorite_sectors'].get(sector, 0) + 1
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
        
    except Exception as e:
        logger.error(f"Engagement metrics error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to retrieve engagement metrics'
        }), 500

# Export blueprint
__all__ = ['engagement_bp']