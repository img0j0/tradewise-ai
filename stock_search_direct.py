"""
Direct stock search implementation for debugging
Bypasses the complex async task queue system while providing immediate stock analysis
"""
import logging
from typing import Dict, Any
from flask import Blueprint, request, jsonify
from external_api_optimizer import yahoo_optimizer
from ai_insights import AIInsightsEngine
from simple_personalization import SimplePersonalization

logger = logging.getLogger(__name__)

# Create direct search blueprint
direct_search_bp = Blueprint('direct_search', __name__)

def get_direct_stock_analysis(symbol: str) -> Dict[str, Any]:
    """Get stock analysis directly without async queue"""
    try:
        # Initialize components
        ai_engine = AIInsightsEngine()
        personalization = SimplePersonalization()
        
        # Get stock data
        stock_data = yahoo_optimizer._fetch_single_stock(symbol)
        if not stock_data:
            return {
                'success': False,
                'error': f'Could not fetch data for {symbol}'
            }
        
        # Generate AI insights
        base_insights = ai_engine.get_insights(symbol, stock_data)
        
        # Apply personalization
        strategy = 'Growth Investor'  # Default strategy
        personalized_insights = personalization.personalize_analysis(symbol, base_insights)
        
        # Create result
        result = {
            'success': True,
            'symbol': symbol,
            'stock_info': stock_data,
            'analysis': personalized_insights,
            'competitive_features': {
                'ai_explanations': personalized_insights.get('ai_explanation', {}),
                'smart_alerts': personalized_insights.get('smart_alerts', []),
                'educational_insights': personalized_insights.get('educational_insights', {})
            },
            'strategy': strategy,
            'processing_mode': 'direct'
        }
        
        logger.info(f"Direct stock analysis completed for {symbol}")
        return result
        
    except Exception as e:
        logger.error(f"Direct stock analysis error for {symbol}: {e}")
        return {
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }

@direct_search_bp.route('/api/stock-analysis-direct/<symbol>', methods=['GET'])
def direct_stock_analysis_endpoint(symbol: str):
    """Direct stock analysis endpoint"""
    try:
        result = get_direct_stock_analysis(symbol.upper())
        return jsonify(result)
    except Exception as e:
        logger.error(f"Direct endpoint error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500