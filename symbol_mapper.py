# Symbol Mapping and Validation for Stock Search
# Maps common company names to proper stock symbols

def get_symbol_mapping():
    """Common company name to stock symbol mappings"""
    return {
        # Major Tech Companies
        'APPLE': 'AAPL',
        'APPLE INC': 'AAPL',
        'APPLE COMPUTER': 'AAPL',
        'MICROSOFT': 'MSFT',
        'MICROSOFT CORP': 'MSFT',
        'MICROSOFT CORPORATION': 'MSFT',
        'GOOGLE': 'GOOGL',
        'ALPHABET': 'GOOGL',
        'ALPHABET INC': 'GOOGL',
        'TESLA': 'TSLA',
        'TESLA INC': 'TSLA',
        'TESLA MOTORS': 'TSLA',
        'AMAZON': 'AMZN',
        'AMAZON.COM': 'AMZN',
        'NVIDIA': 'NVDA',
        'NVIDIA CORP': 'NVDA',
        'NVIDIA CORPORATION': 'NVDA',
        'META': 'META',
        'FACEBOOK': 'META',
        'META PLATFORMS': 'META',
        'NETFLIX': 'NFLX',
        'NETFLIX INC': 'NFLX',
        
        # Financial
        'JPMORGAN': 'JPM',
        'JP MORGAN': 'JPM',
        'JPMORGAN CHASE': 'JPM',
        'VISA': 'V',
        'VISA INC': 'V',
        'BERKSHIRE': 'BRK.A',
        'BERKSHIRE HATHAWAY': 'BRK.A',
        'BANK OF AMERICA': 'BAC',
        'WELLS FARGO': 'WFC',
        
        # Electric Vehicle & Automotive
        'RIVIAN': 'RIVN',
        'RIVIAN AUTOMOTIVE': 'RIVN',
        'LUCID': 'LCID',
        'LUCID MOTORS': 'LCID',
        'LUCID GROUP': 'LCID',
        'FORD': 'F',
        'FORD MOTOR': 'F',
        'GENERAL MOTORS': 'GM',
        'GM': 'GM',
        'NIO': 'NIO',
        'XPENG': 'XPEV',
        'LI AUTO': 'LI',
        
        # Popular Meme Stocks & Recent IPOs
        'GAMESTOP': 'GME', 
        'GAME STOP': 'GME',
        'AMC': 'AMC',
        'AMC ENTERTAINMENT': 'AMC',
        'BLACKBERRY': 'BB',
        'PALANTIR': 'PLTR',
        'PALANTIR TECHNOLOGIES': 'PLTR',
        'SNOWFLAKE': 'SNOW',
        'COINBASE': 'COIN',
        'ROBLOX': 'RBLX',
        'UNITY': 'U',
        'ZOOM': 'ZM',
        'ZOOM VIDEO': 'ZM',
        'PELOTON': 'PTON',
        'ROKU': 'ROKU',
        'SQUARE': 'SQ',
        'BLOCK': 'SQ',
        'SHOPIFY': 'SHOP',
        'SPOTIFY': 'SPOT',
        'UBER': 'UBER',
        'UBER TECHNOLOGIES': 'UBER',
        'LYFT': 'LYFT',
        'AIRBNB': 'ABNB',
        'DOORDASH': 'DASH',
        'TWILIO': 'TWLO',
        'MONGODB': 'MDB',
        'DATADOG': 'DDOG',
        
        # Other Major Companies
        'COCA COLA': 'KO',
        'COCA-COLA': 'KO',
        'JOHNSON & JOHNSON': 'JNJ',
        'JOHNSON AND JOHNSON': 'JNJ',
        'PROCTER & GAMBLE': 'PG',
        'WALMART': 'WMT',
        'WAL-MART': 'WMT',
        'EXXON': 'XOM',
        'EXXON MOBIL': 'XOM',
        'CHEVRON': 'CVX',
        'PFIZER': 'PFE',
        'INTEL': 'INTC',
        'INTEL CORP': 'INTC',
        'CISCO': 'CSCO',
        'CISCO SYSTEMS': 'CSCO',
        'VERIZON': 'VZ',
        'AT&T': 'T',
        'DISNEY': 'DIS',
        'WALT DISNEY': 'DIS',
        'MCDONALDS': 'MCD',
        'MCDONALD\'S': 'MCD',
        'NIKE': 'NKE',
        'NIKE INC': 'NKE',
        'IBM': 'IBM',
        'INTERNATIONAL BUSINESS MACHINES': 'IBM'
    }

def normalize_symbol(query):
    """
    Normalize user input to proper stock symbol
    
    Args:
        query (str): User input (company name or symbol)
        
    Returns:
        str: Proper stock symbol
    """
    if not query:
        return query
        
    # Convert to uppercase and strip whitespace
    normalized = query.strip().upper()
    
    # Remove common suffixes
    suffixes_to_remove = [
        ' STOCK', ' SHARES', ' COMPANY', ' CORP', ' CORPORATION', 
        ' INC', ' INC.', ' LIMITED', ' LTD', ' CLASS A', ' CLASS B',
        ' COMMON STOCK', ' ORDINARY SHARES'
    ]
    
    for suffix in suffixes_to_remove:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()
    
    # Check mapping
    symbol_mapping = get_symbol_mapping()
    if normalized in symbol_mapping:
        return symbol_mapping[normalized]
    
    # If no mapping found, return original (might be valid symbol)
    return normalized

def validate_symbol(symbol):
    """
    Basic validation for stock symbols
    
    Args:
        symbol (str): Stock symbol to validate
        
    Returns:
        bool: True if symbol format is valid
    """
    if not symbol or len(symbol) < 1:
        return False
        
    # Remove dots for validation (some symbols have dots like BRK.A)
    clean_symbol = symbol.replace('.', '')
    
    # Basic format check: 1-5 characters, letters only
    if len(clean_symbol) > 5 or not clean_symbol.isalpha():
        return False
        
    return True

def get_symbol_suggestions(query):
    """
    Get symbol suggestions based on partial input
    
    Args:
        query (str): Partial company name or symbol
        
    Returns:
        list: List of suggested symbols with company names
    """
    if not query or len(query) < 2:
        return []
        
    query_upper = query.upper()
    symbol_mapping = get_symbol_mapping()
    suggestions = []
    
    # Direct symbol matches
    for company, symbol in symbol_mapping.items():
        if query_upper in company or query_upper == symbol:
            suggestions.append({
                'symbol': symbol,
                'company': company.title(),
                'match_type': 'direct'
            })
    
    # Limit to top 10 suggestions
    return suggestions[:10]

# Additional popular symbols for autocomplete
POPULAR_SYMBOLS = [
    {'symbol': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology'},
    {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'sector': 'Technology'},
    {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'sector': 'Technology'},
    {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'sector': 'Automotive'},
    {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'sector': 'Technology'},
    {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'sector': 'E-commerce'},
    {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'sector': 'Technology'},
    {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'sector': 'Entertainment'},
    {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.', 'sector': 'Banking'},
    {'symbol': 'V', 'name': 'Visa Inc.', 'sector': 'Financial Services'},
    {'symbol': 'BRK.A', 'name': 'Berkshire Hathaway Inc.', 'sector': 'Conglomerate'},
    {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'sector': 'Healthcare'},
    {'symbol': 'WMT', 'name': 'Walmart Inc.', 'sector': 'Retail'},
    {'symbol': 'PG', 'name': 'Procter & Gamble Co.', 'sector': 'Consumer Goods'},
    {'symbol': 'KO', 'name': 'The Coca-Cola Company', 'sector': 'Beverages'}
]