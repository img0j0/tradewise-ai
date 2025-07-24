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
        
        # Semiconductor & Hardware
        'ADVANCED MICRO DEVICES': 'AMD',
        'AMD': 'AMD',
        'QUALCOMM': 'QCOM',
        'BROADCOM': 'AVGO',
        'TEXAS INSTRUMENTS': 'TXN',
        'ANALOG DEVICES': 'ADI',
        'MICRON': 'MU',
        'MICRON TECHNOLOGY': 'MU',
        'APPLIED MATERIALS': 'AMAT',
        'LAM RESEARCH': 'LRCX',
        'KLA': 'KLAC',
        'MARVELL': 'MRVL',
        'MARVELL TECHNOLOGY': 'MRVL',
        
        # Healthcare & Biotech
        'MODERNA': 'MRNA',
        'BIONTECH': 'BNTX',
        'GILEAD': 'GILD',
        'GILEAD SCIENCES': 'GILD',
        'AMGEN': 'AMGN',
        'BIOGEN': 'BIIB',
        'REGENERON': 'REGN',
        'VERTEX': 'VRTX',
        'VERTEX PHARMACEUTICALS': 'VRTX',
        'ILLUMINA': 'ILMN',
        'DEXCOM': 'DXCM',
        'INTUITIVE SURGICAL': 'ISRG',
        'EDWARDS LIFESCIENCES': 'EW',
        'STRYKER': 'SYK',
        'MEDTRONIC': 'MDT',
        'ABBOTT': 'ABT',
        'BRISTOL MYERS': 'BMY',
        'BRISTOL-MYERS SQUIBB': 'BMY',
        'ELI LILLY': 'LLY',
        'LILLY': 'LLY',
        'MERCK': 'MRK',
        
        # Energy & Oil
        'EXXONMOBIL': 'XOM',
        'CONOCOPHILLIPS': 'COP',
        'CONOCOPHILLIPS': 'COP',
        'PIONEER': 'PXD',
        'PIONEER NATURAL': 'PXD',
        'EOG RESOURCES': 'EOG',
        'SCHLUMBERGER': 'SLB',
        'HALLIBURTON': 'HAL',
        'MARATHON PETROLEUM': 'MPC',
        'VALERO': 'VLO',
        'PHILLIPS 66': 'PSX',
        'KINDER MORGAN': 'KMI',
        'ENBRIDGE': 'ENB',
        
        # Financial Services
        'GOLDMAN SACHS': 'GS',
        'MORGAN STANLEY': 'MS',
        'CITIGROUP': 'C',
        'CITI': 'C',
        'AMERICAN EXPRESS': 'AXP',
        'AMEX': 'AXP',
        'BLACKROCK': 'BLK',
        'CHARLES SCHWAB': 'SCHW',
        'SCHWAB': 'SCHW',
        'US BANCORP': 'USB',
        'TRUIST': 'TFC',
        'PNC': 'PNC',
        'CAPITAL ONE': 'COF',
        'DISCOVER': 'DIS',
        'MASTERCARD': 'MA',
        'PAYPAL': 'PYPL',
        'AMERICAN INTERNATIONAL GROUP': 'AIG',
        'AIG': 'AIG',
        'PROGRESSIVE': 'PGR',
        'ALLSTATE': 'ALL',
        'TRAVELERS': 'TRV',
        
        # Consumer & Retail
        'TARGET': 'TGT',
        'COSTCO': 'COST',
        'HOME DEPOT': 'HD',
        'LOWES': 'LOW',
        'LOWE\'S': 'LOW',
        'STARBUCKS': 'SBUX',
        'CHIPOTLE': 'CMG',
        'DOMINOS': 'DPZ',
        'DOMINO\'S': 'DPZ',
        'YUM BRANDS': 'YUM',
        'GENERAL MILLS': 'GIS',
        'KELLOGG': 'K',
        'PEPSI': 'PEP',
        'PEPSICO': 'PEP',
        'KRAFT HEINZ': 'KHC',
        'MONDELEZ': 'MDLZ',
        'COLGATE': 'CL',
        'COLGATE-PALMOLIVE': 'CL',
        'UNILEVER': 'UL',
        'ESTEE LAUDER': 'EL',
        'L\'OREAL': 'OR',
        
        # Industrial & Manufacturing
        'BOEING': 'BA',
        'LOCKHEED MARTIN': 'LMT',
        'RAYTHEON': 'RTX',
        'NORTHROP GRUMMAN': 'NOC',
        'GENERAL ELECTRIC': 'GE',
        'GE': 'GE',
        '3M': 'MMM',
        'CATERPILLAR': 'CAT',
        'DEERE': 'DE',
        'JOHN DEERE': 'DE',
        'HONEYWELL': 'HON',
        'UNITED TECHNOLOGIES': 'RTX',
        'PARKER HANNIFIN': 'PH',
        'EMERSON': 'EMR',
        'ILLINOIS TOOL WORKS': 'ITW',
        'FEDEX': 'FDX',
        'UPS': 'UPS',
        'UNITED PARCEL SERVICE': 'UPS',
        
        # Technology Services
        'ORACLE': 'ORCL',
        'SALESFORCE': 'CRM',
        'ADOBE': 'ADBE',
        'SERVICENOW': 'NOW',
        'WORKDAY': 'WDAY',
        'SPLUNK': 'SPLK',
        'VMWARE': 'VMW',
        'CROWDSTRIKE': 'CRWD',
        'ZSCALER': 'ZS',
        'OKTA': 'OKTA',
        'PALO ALTO NETWORKS': 'PANW',
        'FORTINET': 'FTNT',
        'CLOUDFLARE': 'NET',
        'FASTLY': 'FSLY',
        'ELASTIC': 'ESTC',
        'ATLASSIAN': 'TEAM',
        'SLACK': 'WORK',
        'ASANA': 'ASAN',
        'MONDAY.COM': 'MNDY',
        'HUBSPOT': 'HUBS',
        'ZENDESK': 'ZEN',
        
        # Media & Entertainment
        'COMCAST': 'CMCSA',
        'CHARTER': 'CHTR',
        'CHARTER COMMUNICATIONS': 'CHTR',
        'DISCOVERY': 'WBD',
        'WARNER BROS': 'WBD',
        'PARAMOUNT': 'PARA',
        'VIACOM': 'PARA',
        'FOX': 'FOXA',
        'NEWS CORP': 'NWSA',
        'LIVE NATION': 'LYV',
        'ACTIVISION': 'ATVI',
        'ACTIVISION BLIZZARD': 'ATVI',
        'ELECTRONIC ARTS': 'EA',
        'EA': 'EA',
        'TAKE-TWO': 'TTWO',
        'TAKE TWO': 'TTWO',
        
        # Real Estate & REITs
        'AMERICAN TOWER': 'AMT',
        'CROWN CASTLE': 'CCI',
        'DIGITAL REALTY': 'DLR',
        'EQUINIX': 'EQIX',
        'PROLOGIS': 'PLD',
        'PUBLIC STORAGE': 'PSA',
        'REALTY INCOME': 'O',
        'SIMON PROPERTY': 'SPG',
        'WELLTOWER': 'WELL',
        'VENTAS': 'VTR',
        
        # Utilities
        'NEXTERA': 'NEE',
        'NEXTERA ENERGY': 'NEE',
        'DUKE ENERGY': 'DUK',
        'SOUTHERN COMPANY': 'SO',
        'DOMINION': 'D',
        'DOMINION ENERGY': 'D',
        'AMERICAN ELECTRIC POWER': 'AEP',
        'EXELON': 'EXC',
        'XCEL ENERGY': 'XEL',
        'CONSOLIDATED EDISON': 'ED',
        'SEMPRA': 'SRE',
        'SEMPRA ENERGY': 'SRE',
        
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

def get_stock_symbol(input_text):
    """Convert company name to stock symbol or validate existing symbol"""
    if not input_text:
        return None
    
    # Convert to uppercase for mapping
    input_upper = input_text.upper().strip()
    
    # Get the symbol mapping
    mapping = get_symbol_mapping()
    
    # Check if it's a company name in our mapping
    if input_upper in mapping:
        return mapping[input_upper]
    
    # Check if it's already a valid stock symbol (basic validation)
    if len(input_upper) <= 5 and input_upper.replace('.', '').replace('-', '').isalpha():
        return input_upper
    
    # If not found, return the input as-is (let Yahoo Finance handle validation)
    return input_upper

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
    # Also check for partial matches for fuzzy searching
    return normalized

def validate_symbol(symbol):
    """
    Enhanced validation for stock symbols including various formats
    
    Args:
        symbol (str): Stock symbol to validate
        
    Returns:
        bool: True if symbol format is valid
    """
    if not symbol or len(symbol) < 1:
        return False
        
    # Remove dots and hyphens for validation (BRK.A, BRK-A formats)
    clean_symbol = symbol.replace('.', '').replace('-', '')
    
    # Enhanced format check: 1-6 characters, letters and numbers
    if len(clean_symbol) > 6 or not clean_symbol.isalnum():
        return False
        
    return True

def get_symbol_suggestions(query):
    """
    Get symbol suggestions based on partial input with fuzzy matching
    
    Args:
        query (str): Partial company name or symbol
        
    Returns:
        list: List of suggested symbols with company names
    """
    if not query:
        return []
        
    query = query.upper().strip()
    symbol_mapping = get_symbol_mapping()
    suggestions = []
    
    # Direct matches first
    for company_name, symbol in symbol_mapping.items():
        if query in company_name or query == symbol:
            suggestions.append({
                'symbol': symbol,
                'company_name': company_name,
                'match_type': 'exact'
            })
    
    # Partial matches
    for company_name, symbol in symbol_mapping.items():
        if query in company_name.split() and len(suggestions) < 10:
            suggestions.append({
                'symbol': symbol,
                'company_name': company_name,
                'match_type': 'partial'
            })
    
    return suggestions[:10]  # Limit to top 10 suggestions

def create_comprehensive_fallback_search(query):
    """
    Creates a fallback search strategy for symbols not in our mapping
    This allows the system to attempt API calls for any reasonable stock symbol
    
    Args:
        query (str): User search query
        
    Returns:
        str: Processed symbol that might work with the API
    """
    if not query:
        return None
        
    # Clean and normalize
    normalized = query.upper().strip()
    
    # If it looks like a ticker (short, letters only), try it directly
    if len(normalized) <= 6 and normalized.replace('.', '').replace('-', '').isalpha():
        return normalized
    
    # If it's a longer name, try common abbreviation patterns
    words = normalized.split()
    if len(words) >= 2:
        # Try first letters of each word (e.g., "Bank of America" -> "BOA")
        abbreviation = ''.join(word[0] for word in words if word[0].isalpha())
        if 2 <= len(abbreviation) <= 5:
            return abbreviation
    
    return None
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