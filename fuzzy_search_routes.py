"""
Fuzzy Search Routes
Enhanced search endpoints with RapidFuzz integration
"""

from flask import Blueprint, request, jsonify
from fuzzy_search_engine import search_stocks_fuzzy, get_autocomplete_fuzzy, fuzzy_search_engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
fuzzy_search_bp = Blueprint('fuzzy_search', __name__)

@fuzzy_search_bp.route('/api/search/fuzzy', methods=['GET'])
def fuzzy_search_endpoint():
    """Enhanced fuzzy search with typo correction"""
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 8))
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Search query is required",
                "results": [],
                "suggestions": []
            }), 400
        
        # Perform fuzzy search
        result = search_stocks_fuzzy(query, limit)
        
        logger.info(f"Fuzzy search API: '{query}' -> {result['result_count']} results")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Fuzzy search API error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Search service temporarily unavailable",
            "results": [],
            "suggestions": []
        }), 500

@fuzzy_search_bp.route('/api/search/autocomplete-enhanced', methods=['GET'])
def enhanced_autocomplete():
    """Enhanced autocomplete with logos and metadata"""
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 6))
        
        # Get enhanced autocomplete suggestions
        result = get_autocomplete_fuzzy(query, limit)
        
        logger.info(f"Enhanced autocomplete: '{query}' -> {result['count']} suggestions")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Enhanced autocomplete API error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Autocomplete service temporarily unavailable",
            "suggestions": []
        }), 500

@fuzzy_search_bp.route('/api/search/suggestions', methods=['GET'])
def search_suggestions():
    """Get 'Did you mean?' suggestions for failed searches"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Query is required",
                "suggestions": []
            }), 400
        
        suggestions = fuzzy_search_engine.get_search_suggestions(query)
        
        return jsonify({
            "success": True,
            "query": query,
            "suggestions": suggestions,
            "count": len(suggestions)
        })
        
    except Exception as e:
        logger.error(f"Search suggestions API error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Suggestions service temporarily unavailable",
            "suggestions": []
        }), 500

@fuzzy_search_bp.route('/api/search/analytics', methods=['GET'])
def search_analytics():
    """Get search analytics and insights"""
    try:
        analytics = fuzzy_search_engine.get_search_analytics()
        
        return jsonify({
            "success": True,
            "analytics": analytics
        })
        
    except Exception as e:
        logger.error(f"Search analytics API error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Analytics service temporarily unavailable"
        }), 500

# Health check endpoint
@fuzzy_search_bp.route('/api/search/health', methods=['GET'])
def search_health():
    """Health check for fuzzy search service"""
    try:
        # Test search functionality
        test_result = search_stocks_fuzzy("AAPL", 1)
        
        return jsonify({
            "success": True,
            "status": "healthy",
            "database_size": len(fuzzy_search_engine.stock_database),
            "test_search": test_result['success']
        })
        
    except Exception as e:
        logger.error(f"Search health check error: {str(e)}")
        return jsonify({
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        }), 500