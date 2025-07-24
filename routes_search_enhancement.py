# Search Enhancement API Endpoints
from flask import jsonify, request
from symbol_mapper import get_symbol

def get_search_suggestions():
    """Get real-time search suggestions for autocomplete"""
    query = request.args.get('q', '').strip().lower()
    if len(query) < 2:
        return jsonify({'suggestions': []})
    
    # Popular stocks and common searches
    popular_stocks = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology'},
        {'symbol': 'TSLA', 'name': 'Tesla, Inc.', 'sector': 'Automotive'},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'sector': 'Technology'},
        {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'sector': 'Consumer Discretionary'},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'sector': 'Technology'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'sector': 'Technology'},
        {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'sector': 'Technology'},
        {'symbol': 'RIVN', 'name': 'Rivian Automotive Inc.', 'sector': 'Automotive'},
        {'symbol': 'PLTR', 'name': 'Palantir Technologies Inc.', 'sector': 'Technology'},
        {'symbol': 'AMD', 'name': 'Advanced Micro Devices Inc.', 'sector': 'Technology'},
        {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'sector': 'Communication Services'},
        {'symbol': 'COIN', 'name': 'Coinbase Global Inc.', 'sector': 'Financial Services'},
        {'symbol': 'SNOW', 'name': 'Snowflake Inc.', 'sector': 'Technology'},
        {'symbol': 'ZM', 'name': 'Zoom Video Communications Inc.', 'sector': 'Technology'},
        {'symbol': 'SQ', 'name': 'Block Inc.', 'sector': 'Financial Services'},
        {'symbol': 'PYPL', 'name': 'PayPal Holdings Inc.', 'sector': 'Financial Services'},
        {'symbol': 'DIS', 'name': 'The Walt Disney Company', 'sector': 'Communication Services'},
        {'symbol': 'BA', 'name': 'The Boeing Company', 'sector': 'Industrials'},
        {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.', 'sector': 'Financial Services'},
        {'symbol': 'V', 'name': 'Visa Inc.', 'sector': 'Financial Services'}
    ]
    
    suggestions = []
    
    # Search by symbol and company name
    for stock in popular_stocks:
        symbol_match = query in stock['symbol'].lower()
        name_match = query in stock['name'].lower()
        
        if symbol_match or name_match:
            match_type = 'symbol' if symbol_match else 'name'
            suggestions.append({
                'symbol': stock['symbol'],
                'name': stock['name'],
                'sector': stock['sector'],
                'match_type': match_type,
                'display': f"{stock['symbol']} - {stock['name']}"
            })
    
    # Limit to top 6 suggestions
    suggestions = suggestions[:6]
    
    return jsonify({
        'success': True,
        'query': query,
        'suggestions': suggestions
    })

def get_recent_searches():
    """Get user's recent search history (mock implementation)"""
    # In production, this would pull from user's search history in database
    recent = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'timestamp': '2 hours ago'},
        {'symbol': 'TSLA', 'name': 'Tesla, Inc.', 'timestamp': '1 day ago'},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'timestamp': '3 days ago'}
    ]
    
    return jsonify({
        'success': True,
        'recent_searches': recent
    })

def get_trending_stocks():
    """Get currently trending stocks"""
    trending = [
        {'symbol': 'RIVN', 'name': 'Rivian Automotive', 'change': '+2.5%', 'volume': 'High'},
        {'symbol': 'PLTR', 'name': 'Palantir Technologies', 'change': '-1.2%', 'volume': 'High'},
        {'symbol': 'AMD', 'name': 'Advanced Micro Devices', 'change': '+3.1%', 'volume': 'Above Average'}
    ]
    
    return jsonify({
        'success': True,
        'trending': trending
    })