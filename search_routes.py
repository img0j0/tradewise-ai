"""
Search API Routes
Provides endpoints for advanced search functionality with autocomplete
"""

from flask import Blueprint, request, jsonify
from advanced_search import advanced_search_engine
import logging

logger = logging.getLogger(__name__)

# Create search blueprint
search_bp = Blueprint('search_api', __name__, url_prefix='/api/search')

@search_bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    """
    Autocomplete endpoint for search suggestions
    
    Query Parameters:
        q (str): Search query
        limit (int): Maximum number of results (default: 8)
    
    Returns:
        JSON response with search results
    """
    try:
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 8)), 20)  # Cap at 20
        
        if not query:
            return jsonify({
                'success': True,
                'results': [],
                'message': 'Empty query'
            })
        
        if len(query) < 1:
            return jsonify({
                'success': True, 
                'results': [],
                'message': 'Query too short'
            })
        
        # Initialize search engine if needed
        if not advanced_search_engine.initialized:
            advanced_search_engine.initialize()
        
        # Perform search
        results = advanced_search_engine.search(query, limit)
        
        # Convert results to dict format
        results_data = []
        for result in results:
            results_data.append({
                'symbol': result.symbol,
                'company_name': result.company_name,
                'sector': result.sector,
                'market_cap': result.market_cap,
                'logo_url': result.logo_url,
                'exchange': result.exchange,
                'confidence_score': result.confidence_score,
                'search_frequency': result.search_frequency
            })
        
        return jsonify({
            'success': True,
            'results': results_data,
            'query': query,
            'count': len(results_data)
        })
        
    except Exception as e:
        logger.error(f"Autocomplete search error: {e}")
        return jsonify({
            'success': False,
            'error': 'Search temporarily unavailable',
            'results': []
        }), 500

@search_bp.route('/popular', methods=['GET'])
def popular_stocks():
    """
    Get popular/frequently searched stocks
    
    Query Parameters:
        limit (int): Maximum number of results (default: 10)
    
    Returns:
        JSON response with popular stocks
    """
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
        
        if not advanced_search_engine.initialized:
            advanced_search_engine.initialize()
        
        results = advanced_search_engine.get_popular_stocks(limit)
        
        results_data = []
        for result in results:
            results_data.append({
                'symbol': result.symbol,
                'company_name': result.company_name,
                'sector': result.sector,
                'market_cap': result.market_cap,
                'logo_url': result.logo_url,
                'exchange': result.exchange,
                'search_frequency': result.search_frequency
            })
        
        return jsonify({
            'success': True,
            'results': results_data,
            'count': len(results_data)
        })
        
    except Exception as e:
        logger.error(f"Popular stocks error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to fetch popular stocks',
            'results': []
        }), 500

@search_bp.route('/sector/<sector_name>', methods=['GET'])
def sector_suggestions(sector_name):
    """
    Get stock suggestions from a specific sector
    
    Path Parameters:
        sector_name (str): Name of the sector
    
    Query Parameters:
        limit (int): Maximum number of results (default: 5)
    
    Returns:
        JSON response with sector stocks
    """
    try:
        limit = min(int(request.args.get('limit', 5)), 20)
        
        if not advanced_search_engine.initialized:
            advanced_search_engine.initialize()
        
        results = advanced_search_engine.get_sector_suggestions(sector_name, limit)
        
        results_data = []
        for result in results:
            results_data.append({
                'symbol': result.symbol,
                'company_name': result.company_name,
                'sector': result.sector,
                'market_cap': result.market_cap,
                'logo_url': result.logo_url,
                'exchange': result.exchange
            })
        
        return jsonify({
            'success': True,
            'results': results_data,
            'sector': sector_name,
            'count': len(results_data)
        })
        
    except Exception as e:
        logger.error(f"Sector suggestions error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to fetch sector suggestions',
            'results': []
        }), 500

@search_bp.route('/refresh', methods=['POST'])
def refresh_search_data():
    """
    Force refresh of search data (admin endpoint)
    
    Returns:
        JSON response confirming refresh
    """
    try:
        advanced_search_engine.refresh_data()
        
        return jsonify({
            'success': True,
            'message': 'Search data refreshed successfully'
        })
        
    except Exception as e:
        logger.error(f"Search data refresh error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to refresh search data'
        }), 500

@search_bp.route('/stats', methods=['GET'])
def search_stats():
    """
    Get search statistics and health info
    
    Returns:
        JSON response with search engine stats
    """
    try:
        if not advanced_search_engine.initialized:
            return jsonify({
                'success': True,
                'initialized': False,
                'message': 'Search engine not initialized'
            })
        
        stats = {
            'initialized': advanced_search_engine.initialized,
            'companies_count': len(advanced_search_engine.companies_data),
            'search_frequencies_count': len(advanced_search_engine.search_frequencies),
            'last_update': advanced_search_engine.last_update,
            'update_interval': advanced_search_engine.update_interval
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Search stats error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to fetch search stats'
        }), 500