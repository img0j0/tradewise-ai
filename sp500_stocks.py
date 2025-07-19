"""
S&P 500 Stock Database
Complete list of S&P 500 companies with symbols and names for intelligent search
"""

SP500_STOCKS = {
    # Technology
    'aapl': 'Apple Inc.',
    'msft': 'Microsoft Corporation',
    'googl': 'Alphabet Inc. Class A',
    'goog': 'Alphabet Inc. Class C',
    'amzn': 'Amazon.com Inc.',
    'nvda': 'NVIDIA Corporation',
    'tsla': 'Tesla Inc.',
    'meta': 'Meta Platforms Inc.',
    'avgo': 'Broadcom Inc.',
    'orcl': 'Oracle Corporation',
    'adbe': 'Adobe Inc.',
    'crm': 'Salesforce Inc.',
    'nflx': 'Netflix Inc.',
    'intc': 'Intel Corporation',
    'amd': 'Advanced Micro Devices Inc.',
    'now': 'ServiceNow Inc.',
    'intu': 'Intuit Inc.',
    'csco': 'Cisco Systems Inc.',
    'qcom': 'QUALCOMM Incorporated',
    'amat': 'Applied Materials Inc.',
    'anet': 'Arista Networks Inc.',
    'panw': 'Palo Alto Networks Inc.',
    'pltr': 'Palantir Technologies Inc.',
    'snow': 'Snowflake Inc.',
    'team': 'Atlassian Corporation',
    'ddog': 'Datadog Inc.',
    'crwd': 'CrowdStrike Holdings Inc.',
    'ftnt': 'Fortinet Inc.',
    'mrvl': 'Marvell Technology Inc.',
    'mu': 'Micron Technology Inc.',
    'lrcx': 'Lam Research Corporation',
    'klac': 'KLA Corporation',
    'cdns': 'Cadence Design Systems Inc.',
    'snps': 'Synopsys Inc.',
    'mchp': 'Microchip Technology Incorporated',
    'adsk': 'Autodesk Inc.',
    'ctsh': 'Cognizant Technology Solutions Corporation',
    'fisv': 'Fiserv Inc.',
    'payx': 'Paychex Inc.',
    'gddy': 'GoDaddy Inc.',
    'tyl': 'Tyler Technologies Inc.',
    
    # Communication Services  
    'googl': 'Alphabet Inc.',
    'meta': 'Meta Platforms Inc.',
    'nflx': 'Netflix Inc.',
    'dis': 'The Walt Disney Company',
    'cmcsa': 'Comcast Corporation',
    'vz': 'Verizon Communications Inc.',
    't': 'AT&T Inc.',
    'tmus': 'T-Mobile US Inc.',
    'chtr': 'Charter Communications Inc.',
    'ea': 'Electronic Arts Inc.',
    'ttd': 'The Trade Desk Inc.',
    'mtch': 'Match Group Inc.',
    'lumn': 'Lumen Technologies Inc.',
    'dish': 'DISH Network Corporation',
    'nwsa': 'News Corporation Class A',
    'fox': 'Fox Corporation Class A',
    'foxa': 'Fox Corporation Class A',
    'om': 'Outfront Media Inc.',
    'para': 'Paramount Global Class B',
    'wbd': 'Warner Bros. Discovery Inc.',
    
    # Financials
    'brk.b': 'Berkshire Hathaway Inc. Class B',
    'jpm': 'JPMorgan Chase & Co.',
    'bac': 'Bank of America Corporation',
    'wfc': 'Wells Fargo & Company',
    'gs': 'The Goldman Sachs Group Inc.',
    'ms': 'Morgan Stanley',
    'c': 'Citigroup Inc.',
    'schw': 'The Charles Schwab Corporation',
    'axp': 'American Express Company',
    'usb': 'U.S. Bancorp',
    'pnc': 'The PNC Financial Services Group Inc.',
    'truist': 'Truist Financial Corporation',
    'cod': 'Comerica Incorporated',
    'fitb': 'Fifth Third Bancorp',
    'mtb': 'M&T Bank Corporation',
    'stfc': 'State Street Corporation',
    'bk': 'The Bank of New York Mellon Corporation',
    'ntrs': 'Northern Trust Corporation',
    'rf': 'Regions Financial Corporation',
    'key': 'KeyCorp',
    'cfg': 'Citizens Financial Group Inc.',
    'hban': 'Huntington Bancshares Incorporated',
    'dfs': 'Discover Financial Services',
    'syn': 'Synchrony Financial',
    'cof': 'Capital One Financial Corporation',
    'aig': 'American International Group Inc.',
    'met': 'MetLife Inc.',
    'pru': 'Prudential Financial Inc.',
    'afl': 'AFLAC Incorporated',
    'all': 'The Allstate Corporation',
    'pgr': 'The Progressive Corporation',
    'trv': 'The Travelers Companies Inc.',
    'cb': 'Chubb Limited',
    'aon': 'Aon plc',
    'mmc': 'Marsh & McLennan Companies Inc.',
    'wltw': 'Willis Towers Watson Public Limited Company',
    'ajg': 'Arthur J. Gallagher & Co.',
    'bro': 'Brown & Brown Inc.',
    'bre': 'BRE Properties Inc.',
    'spgi': 'S&P Global Inc.',
    'mco': 'Moody\'s Corporation',
    'msci': 'MSCI Inc.',
    'ice': 'Intercontinental Exchange Inc.',
    'cme': 'CME Group Inc.',
    'ndaq': 'Nasdaq Inc.',
    'cboe': 'Cboe Global Markets Inc.',
    
    # Healthcare
    'jnj': 'Johnson & Johnson',
    'unh': 'UnitedHealth Group Incorporated',
    'pfizer': 'Pfizer Inc.',
    'abbv': 'AbbVie Inc.',
    'tmo': 'Thermo Fisher Scientific Inc.',
    'mck': 'McKesson Corporation',
    'cvs': 'CVS Health Corporation',
    'eli': 'Eli Lilly and Company',
    'abt': 'Abbott Laboratories',
    'dhf': 'Danaher Corporation',
    'bmy': 'Bristol-Myers Squibb Company',
    'amgn': 'Amgen Inc.',
    'isrg': 'Intuitive Surgical Inc.',
    'gild': 'Gilead Sciences Inc.',
    'mdlz': 'Mondelez International Inc.',
    'bsx': 'Boston Scientific Corporation',
    'regn': 'Regeneron Pharmaceuticals Inc.',
    'ci': 'Cigna Corporation',
    'hum': 'Humana Inc.',
    'antm': 'Anthem Inc.',
    'mrk': 'Merck & Co. Inc.',
    'pfe': 'Pfizer Inc.',
    'rmd': 'ResMed Inc.',
    'dxcm': 'DexCom Inc.',
    'algn': 'Align Technology Inc.',
    'ilmn': 'Illumina Inc.',
    'biib': 'Biogen Inc.',
    'vrtx': 'Vertex Pharmaceuticals Incorporated',
    'mrna': 'Moderna Inc.',
    'zts': 'Zoetis Inc.',
    'idxx': 'IDEXX Laboratories Inc.',
    'holx': 'Hologic Inc.',
    'dhi': 'D.R. Horton Inc.',
    'var': 'Varian Medical Systems Inc.',
    'a': 'Agilent Technologies Inc.',
    'wat': 'Waters Corporation',
    'mdt': 'Medtronic plc',
    'syk': 'Stryker Corporation',
    'zm': 'Zimmer Biomet Holdings Inc.',
    'eds': 'Edwards Lifesciences Corporation',
    'pen': 'Penumbra Inc.',
    'ste': 'STERIS plc',
    'tech': 'Bio-Techne Corporation',
    'pkd': 'Parker-Hannifin Corporation',
    
    # Consumer Discretionary
    'amzn': 'Amazon.com Inc.',
    'hd': 'The Home Depot Inc.',
    'mcd': 'McDonald\'s Corporation',
    'nike': 'NIKE Inc.',
    'sbux': 'Starbucks Corporation',
    'low': 'Lowe\'s Companies Inc.',
    'tjx': 'The TJX Companies Inc.',
    'f': 'Ford Motor Company',
    'gm': 'General Motors Company',
    'ccl': 'Carnival Corporation',
    'nclh': 'Norwegian Cruise Line Holdings Ltd.',
    'rcl': 'Royal Caribbean Cruises Ltd.',
    'mar': 'Marriott International Inc.',
    'hilton': 'Hilton Worldwide Holdings Inc.',
    'mgm': 'MGM Resorts International',
    'wynn': 'Wynn Resorts Limited',
    'lvs': 'Las Vegas Sands Corp.',
    'yum': 'Yum! Brands Inc.',
    'qsr': 'Restaurant Brands International Inc.',
    'dri': 'Darden Restaurants Inc.',
    'cmg': 'Chipotle Mexican Grill Inc.',
    'domino': 'Domino\'s Pizza Inc.',
    'kss': 'Kohl\'s Corporation',
    'jwn': 'Nordstrom Inc.',
    'm': 'Macy\'s Inc.',
    'gps': 'The Gap Inc.',
    'anf': 'Abercrombie & Fitch Co.',
    'urbag': 'Urban Outfitters Inc.',
    'rl': 'Ralph Lauren Corporation',
    'pvh': 'PVH Corp.',
    'vfc': 'V.F. Corporation',
    'hw': 'Hanesbrands Inc.',
    'under': 'Under Armour Inc.',
    'nke': 'NIKE Inc.',
    'lulu': 'Lululemon Athletica Inc.',
    'deck': 'Deckers Outdoor Corporation',
    'crox': 'Crocs Inc.',
    'skechers': 'Skechers U.S.A. Inc.',
    
    # Consumer Staples
    'pg': 'The Procter & Gamble Company',
    'ko': 'The Coca-Cola Company',
    'pep': 'PepsiCo Inc.',
    'wmt': 'Walmart Inc.',
    'cost': 'Costco Wholesale Corporation',
    'cl': 'Colgate-Palmolive Company',
    'kmbp': 'Kimberly-Clark Corporation',
    'kr': 'The Kroger Co.',
    'syw': 'Sears Holdings Corporation',
    'syy': 'Sysco Corporation',
    'adm': 'Archer-Daniels-Midland Company',
    'tyson': 'Tyson Foods Inc.',
    'hrs': 'Hormel Foods Corporation',
    'cpb': 'Campbell Soup Company',
    'gis': 'General Mills Inc.',
    'k': 'Kellogg Company',
    'mkc': 'McCormick & Company Incorporated',
    'sju': 'The J. M. Smucker Company',
    'hsy': 'The Hershey Company',
    'mdlz': 'Mondelez International Inc.',
    'kao': 'The Kao Corporation',
    'unilever': 'Unilever PLC',
    'nestle': 'Nestle S.A.',
    'danone': 'Danone S.A.',
    
    # Energy
    'xom': 'Exxon Mobil Corporation',
    'cvx': 'Chevron Corporation',
    'cop': 'ConocoPhillips',
    'slb': 'Schlumberger Limited',
    'pxd': 'Pioneer Natural Resources Company',
    'eog': 'EOG Resources Inc.',
    'mpc': 'Marathon Petroleum Corporation',
    'vlo': 'Valero Energy Corporation',
    'psx': 'Phillips 66',
    'kmi': 'Kinder Morgan Inc.',
    'oxy': 'Occidental Petroleum Corporation',
    'hal': 'Halliburton Company',
    'bkr': 'Baker Hughes Company',
    'fti': 'TechnipFMC plc',
    'nov': 'National Oilwell Varco Inc.',
    'dvn': 'Devon Energy Corporation',
    'fang': 'Diamondback Energy Inc.',
    'ctra': 'Coterra Energy Inc.',
    'mrk': 'Merck & Co. Inc.',
    'apa': 'APA Corporation',
    'ovv': 'Ovintiv Inc.',
    'cvr': 'CVR Energy Inc.',
    
    # Utilities
    'nee': 'NextEra Energy Inc.',
    'so': 'The Southern Company',
    'duk': 'Duke Energy Corporation',
    'd': 'Dominion Energy Inc.',
    'aep': 'American Electric Power Company Inc.',
    'exc': 'Exelon Corporation',
    'xel': 'Xcel Energy Inc.',
    'peg': 'Public Service Enterprise Group Incorporated',
    'ed': 'Consolidated Edison Inc.',
    'eix': 'Edison International',
    'aes': 'The AES Corporation',
    'ppl': 'PPL Corporation',
    'fe': 'FirstEnergy Corp.',
    'etf': 'Eaton Corporation plc',
    'wec': 'WEC Energy Group Inc.',
    'dte': 'DTE Energy Company',
    'pcg': 'PG&E Corporation',
    'scg': 'SCANA Corporation',
    'cms': 'CMS Energy Corporation',
    'aep': 'American Electric Power Company Inc.',
    
    # Materials
    'lin': 'Linde plc',
    'lyw': 'Air Products and Chemicals Inc.',
    'shw': 'The Sherwin-Williams Company',
    'dow': 'Dow Inc.',
    'dd': 'DuPont de Nemours Inc.',
    'ppg': 'PPG Industries Inc.',
    'iff': 'International Flavors & Fragrances Inc.',
    'lyb': 'LyondellBasell Industries N.V.',
    'ce': 'Celanese Corporation',
    'emd': 'Eastman Chemical Company',
    'cf': 'CF Industries Holdings Inc.',
    'mos': 'The Mosaic Company',
    'fmc': 'FMC Corporation',
    'ecl': 'Ecolab Inc.',
    'alb': 'Albemarle Corporation',
    'vmm': 'Valmont Industries Inc.',
    'pkg': 'Packaging Corporation of America',
    'ip': 'International Paper Company',
    'kimberly': 'Kimberly-Clark Corporation',
    'wlk': 'Westlake Corporation',
    'og': 'Owens & Minor Inc.',
    'ball': 'Ball Corporation',
    'ccrn': 'Crown Holdings Inc.',
    'sial': 'Sigma-Aldrich Corporation',
    'nem': 'Newmont Corporation',
    'fcx': 'Freeport-McMoRan Inc.',
    'sw': 'Smurfit WestRock plc',
    
    # Industrials
    'ba': 'The Boeing Company',
    'cat': 'Caterpillar Inc.',
    'hon': 'Honeywell International Inc.',
    'ups': 'United Parcel Service Inc.',
    'rtx': 'Raytheon Technologies Corporation',
    'lmt': 'Lockheed Martin Corporation',
    'noc': 'Northrop Grumman Corporation',
    'gd': 'General Dynamics Corporation',
    'de': 'Deere & Company',
    'mmm': '3M Company',
    'ge': 'General Electric Company',
    'emi': 'EMC Corporation',
    'wm': 'Waste Management Inc.',
    'rsg': 'Republic Services Inc.',
    'fedex': 'FedEx Corporation',
    'dal': 'Delta Air Lines Inc.',
    'ual': 'United Airlines Holdings Inc.',
    'aal': 'American Airlines Group Inc.',
    'luv': 'Southwest Airlines Co.',
    'jblu': 'JetBlue Airways Corporation',
    'alaska': 'Alaska Air Group Inc.',
    'spirit': 'Spirit Airlines Inc.',
    'save': 'Spirit Airlines Inc.',
    'ryanair': 'Ryanair Holdings plc',
    'csx': 'CSX Corporation',
    'unp': 'Union Pacific Corporation',
    'nsc': 'Norfolk Southern Corporation',
    'ksu': 'Kansas City Southern',
    'rail': 'FreightCar America Inc.',
    'uber': 'Uber Technologies Inc.',
    'lyft': 'Lyft Inc.',
    'avis': 'Avis Budget Group Inc.',
    'hertz': 'Hertz Global Holdings Inc.',
    'enterprise': 'Enterprise Products Partners L.P.',
    
    # Real Estate
    'pld': 'Prologis Inc.',
    'amt': 'American Tower Corporation',
    'cci': 'Crown Castle Inc.',
    'eqix': 'Equinix Inc.',
    'dlr': 'Digital Realty Trust Inc.',
    'sbac': 'SBA Communications Corporation',
    'are': 'Alexandria Real Estate Equities Inc.',
    'avb': 'AvalonBay Communities Inc.',
    'eqr': 'Equity Residential',
    'ess': 'Essex Property Trust Inc.',
    'mad': 'Mid-America Apartment Communities Inc.',
    'cpp': 'Camden Property Trust',
    'udr': 'UDR Inc.',
    'air': 'AAR Corp.',
    'irt': 'Independence Realty Trust Inc.',
    'sun': 'Sunstone Hotel Investors Inc.',
    'ryt': 'Realty Income Corporation',
    'o': 'Realty Income Corporation',
    'store': 'STORE Capital Corporation',
    'nnn': 'National Retail Properties Inc.',
    'adi': 'Agree Realty Corporation',
    'frt': 'Federal Realty Investment Trust',
    'reg': 'Regency Centers Corporation',
    'kim': 'Kimco Realty Corporation',
    'bxp': 'Boston Properties Inc.',
    'vno': 'Vornado Realty Trust',
    'slg': 'SL Green Realty Corp.',
    'hcp': 'Healthpeak Properties Inc.',
    'well': 'Welltower Inc.',
    'vnq': 'Vanguard Real Estate ETF',
    'reit': 'SPDR Dow Jones REIT ETF'
}

# Company name to symbol mapping for natural language search
COMPANY_NAME_MAPPING = {}
for symbol, name in SP500_STOCKS.items():
    # Add full company name
    COMPANY_NAME_MAPPING[name.lower()] = symbol.upper()
    
    # Add simplified names (removing Inc., Corp., etc.)
    simplified = name.lower()
    for suffix in [' inc.', ' inc', ' corporation', ' corp.', ' corp', ' company', ' co.', ' co', ' ltd.', ' ltd', ' llc', ' plc']:
        simplified = simplified.replace(suffix, '')
    COMPANY_NAME_MAPPING[simplified.strip()] = symbol.upper()
    
    # Add common abbreviations and variations
    words = simplified.split()
    if len(words) > 1:
        # First word
        COMPANY_NAME_MAPPING[words[0]] = symbol.upper()
        # First two words
        if len(words) > 1:
            COMPANY_NAME_MAPPING[' '.join(words[:2])] = symbol.upper()

# Additional common search terms
ADDITIONAL_MAPPINGS = {
    # Popular names
    'alphabet': 'GOOGL',
    'google': 'GOOGL', 
    'facebook': 'META',
    'tesla': 'TSLA',
    'apple': 'AAPL',
    'apple inc': 'AAPL',
    'microsoft': 'MSFT',
    'microsoft corp': 'MSFT',
    'amazon': 'AMZN',
    'nvidia': 'NVDA',
    'netflix': 'NFLX',
    'disney': 'DIS',
    'walmart': 'WMT',
    'coca cola': 'KO',
    'pepsi': 'PEP',
    'mcdonalds': 'MCD',
    'starbucks': 'SBUX',
    'nike': 'NKE',
    'home depot': 'HD',
    'lowes': 'LOW',
    'target': 'TGT',
    'costco': 'COST',
    'berkshire': 'BRK.B',
    'warren buffett': 'BRK.B',
    'jpmorgan': 'JPM',
    'bank of america': 'BAC',
    'wells fargo': 'WFC',
    'goldman sachs': 'GS',
    'morgan stanley': 'MS',
    'visa': 'V',
    'mastercard': 'MA',
    'american express': 'AXP',
    'boeing': 'BA',
    'caterpillar': 'CAT',
    'general electric': 'GE',
    'johnson & johnson': 'JNJ',
    'pfizer': 'PFE',
    'merck': 'MRK',
    'exxon': 'XOM',
    'chevron': 'CVX',
    
    # Additional popular stocks not in S&P 500
    'lucid': 'LCID',
    'lucid motors': 'LCID',
    'rivian': 'RIVN',
    'toyota': 'TM',
    'toyota motor': 'TM',
    'honda': 'HMC',
    'nissan': 'NSANY',
    'robinhood': 'HOOD',
    'coinbase': 'COIN',
    'palantir': 'PLTR',
    'snowflake': 'SNOW',
    'gamestop': 'GME',
    'amc': 'AMC',
    'blackberry': 'BB',
    'nokia': 'NOK',
    'zoom': 'ZM',
    'peloton': 'PTON',
    'roku': 'ROKU',
    'square': 'SQ',
    'block': 'SQ',
    'paypal': 'PYPL',
    'shopify': 'SHOP',
    'spotify': 'SPOT',
    'uber': 'UBER',
    'lyft': 'LYFT',
    'airbnb': 'ABNB',
    'doordash': 'DASH',
    'beyond meat': 'BYND',
    'moderna': 'MRNA',
    'roblox': 'RBLX',
    'unity': 'U',
    'ferrari': 'RACE',
    'stellantis': 'STLA'
}

# Merge additional mappings
COMPANY_NAME_MAPPING.update(ADDITIONAL_MAPPINGS)

def get_symbol_from_name(search_term):
    """
    Convert company name or search term to stock symbol
    """
    search_term = search_term.strip()
    search_lower = search_term.lower()
    
    # If it looks like a symbol (short, uppercase), return as-is
    if len(search_term) <= 5 and search_term.isupper():
        return search_term
    
    # If it's already a known symbol in our database, return uppercase
    if search_lower in SP500_STOCKS:
        return search_lower.upper()
    
    # Check additional mappings first (for non-S&P stocks like LCID, TM)
    if search_lower in ADDITIONAL_MAPPINGS:
        return ADDITIONAL_MAPPINGS[search_lower]
    
    # Special handling for common search terms that should map directly
    direct_mappings = {
        'lucid': 'LCID',
        'toyota': 'TM', 
        'costco': 'COST',
        'rambus': 'RMBS'
    }
    if search_lower in direct_mappings:
        return direct_mappings[search_lower]
    
    # Exact match in company name mapping
    if search_lower in COMPANY_NAME_MAPPING:
        return COMPANY_NAME_MAPPING[search_lower]
    
    # Partial matching - check if search term contains company name
    for name, symbol in COMPANY_NAME_MAPPING.items():
        if search_lower in name or name in search_lower:
            return symbol
    
    # Word matching for multi-word searches
    search_words = search_lower.split()
    if len(search_words) > 1:
        for name, symbol in COMPANY_NAME_MAPPING.items():
            name_words = name.split()
            # Check if all search words are found in company name
            if all(any(search_word in name_word for name_word in name_words) for search_word in search_words if len(search_word) > 2):
                return symbol
    
    # Single word matching for major companies
    if len(search_words) == 1 and len(search_lower) > 2:
        for name, symbol in COMPANY_NAME_MAPPING.items():
            name_words = name.split()
            if search_lower in name_words or any(search_lower in word for word in name_words):
                return symbol
    
    # Return original as symbol if no match found
    return search_term.upper()

def get_all_symbols():
    """Get all available stock symbols"""
    symbols = list(SP500_STOCKS.keys())
    additional_symbols = list(set(ADDITIONAL_MAPPINGS.values()))
    return list(set(symbols + additional_symbols))

def is_sp500(symbol):
    """Check if a symbol is in S&P 500"""
    return symbol.lower() in SP500_STOCKS