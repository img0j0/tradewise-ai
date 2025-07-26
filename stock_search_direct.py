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

# Comprehensive symbol mapping for better search results
SYMBOL_MAPPING = {
    # Popular companies
    'apple': 'AAPL', 'microsoft': 'MSFT', 'google': 'GOOGL', 'alphabet': 'GOOGL',
    'amazon': 'AMZN', 'tesla': 'TSLA', 'meta': 'META', 'facebook': 'META',
    'netflix': 'NFLX', 'nvidia': 'NVDA', 'amd': 'AMD', 'intel': 'INTC',
    
    # Automotive (including Toyota fix)
    'rivian': 'RIVN', 'lucid': 'LCID', 'lucid motors': 'LCID', 'ford': 'F',
    'ford motor': 'F', 'gm': 'GM', 'general motors': 'GM', 'toyota': 'TM',
    'toyota motor': 'TM', 'honda': 'HMC', 'nissan': 'NSANY', 'bmw': 'BMWYY',
    'volkswagen': 'VWAGY', 'mercedes': 'MBGAF', 'ferrari': 'RACE', 'nio': 'NIO',
    
    # Financial Services
    'jpmorgan': 'JPM', 'jp morgan': 'JPM', 'bank of america': 'BAC',
    'wells fargo': 'WFC', 'goldman sachs': 'GS', 'morgan stanley': 'MS',
    'visa': 'V', 'mastercard': 'MA', 'paypal': 'PYPL', 'berkshire': 'BRK-B',
    
    # Technology & Software
    'salesforce': 'CRM', 'oracle': 'ORCL', 'ibm': 'IBM', 'cisco': 'CSCO',
    'adobe': 'ADBE', 'snowflake': 'SNOW', 'palantir': 'PLTR', 'zoom': 'ZM',
    'shopify': 'SHOP', 'square': 'SQ', 'block': 'SQ',
    
    # Healthcare & Pharma
    'johnson & johnson': 'JNJ', 'j&j': 'JNJ', 'pfizer': 'PFE', 'moderna': 'MRNA',
    'biontech': 'BNTX', 'merck': 'MRK', 'abbvie': 'ABBV', 'gilead': 'GILD',
    
    # Retail & Consumer
    'walmart': 'WMT', 'target': 'TGT', 'costco': 'COST', 'home depot': 'HD',
    'mcdonalds': 'MCD', 'starbucks': 'SBUX', 'nike': 'NKE', 'coca cola': 'KO',
    
    # Energy & Utilities
    'exxon': 'XOM', 'exxon mobil': 'XOM', 'chevron': 'CVX', 'shell': 'SHEL',
    'bp': 'BP', 'conocophillips': 'COP',
    
    # Aerospace & Industrial
    'boeing': 'BA', 'lockheed martin': 'LMT', 'caterpillar': 'CAT', '3m': 'MMM',
    'ge': 'GE', 'general electric': 'GE', 'honeywell': 'HON',
    
    # Communications & Media
    'att': 'T', 'at&t': 'T', 'verizon': 'VZ', 'tmobile': 'TMUS', 't-mobile': 'TMUS',
    'comcast': 'CMCSA', 'disney': 'DIS', 'warner bros': 'WBD',
    
    # Semiconductors
    'tsmc': 'TSM', 'taiwan semiconductor': 'TSM', 'qualcomm': 'QCOM',
    'broadcom': 'AVGO', 'micron': 'MU', 'applied materials': 'AMAT',
    
    # Chinese ADRs
    'alibaba': 'BABA', 'tencent': 'TCEHY', 'baidu': 'BIDU', 'jd.com': 'JD',
    'pinduoduo': 'PDD',
    
    # Crypto/Fintech
    'coinbase': 'COIN', 'microstrategy': 'MSTR', 'robinhood': 'HOOD',
    'sofi': 'SOFI', 'affirm': 'AFRM',
    
    # Meme Stocks
    'gamestop': 'GME', 'amc': 'AMC', 'blackberry': 'BB', 'nokia': 'NOK',
    
    # Airlines & Travel
    'southwest': 'LUV', 'american airlines': 'AAL', 'delta': 'DAL',
    'united': 'UAL', 'booking': 'BKNG', 'airbnb': 'ABNB', 'uber': 'UBER',
}

def map_symbol(query: str) -> str:
    """Map company name or common term to stock symbol"""
    query_lower = query.lower().strip()
    
    # Direct symbol mapping
    if query_lower in SYMBOL_MAPPING:
        return SYMBOL_MAPPING[query_lower]
    
    # Check if it's already a valid symbol (uppercase)
    if query.isupper() and len(query) <= 5:
        return query
    
    # Partial matching for common variations
    for name, symbol in SYMBOL_MAPPING.items():
        if query_lower in name or name in query_lower:
            return symbol
    
    # Return original query uppercase as fallback
    return query.upper()

def get_direct_stock_analysis(symbol: str) -> Dict[str, Any]:
    """Get stock analysis directly without async queue"""
    try:
        # Map symbol first
        mapped_symbol = map_symbol(symbol)
        logger.info(f"Original query: \"{symbol}\" -> Mapped symbol: \"{mapped_symbol}\"")
        
        # Initialize components
        ai_engine = AIInsightsEngine()
        personalization = SimplePersonalization()
        
        # Get stock data
        stock_data = yahoo_optimizer._fetch_single_stock(mapped_symbol)
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
            'symbol': mapped_symbol,
            'original_query': symbol,
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