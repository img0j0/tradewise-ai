"""
Universal Stock Search Enhancement
Fallback system for any publicly traded stock not in our S&P 500 database
"""

import yfinance as yf
import logging
from sp500_stocks import get_symbol_from_name, is_sp500

logger = logging.getLogger(__name__)

class UniversalStockSearch:
    """Enhanced stock search with universal coverage"""
    
    def __init__(self):
        self.cache = {}  # Simple cache for recent searches
    
    def search_any_stock(self, search_term):
        """
        Search for any publicly traded stock with intelligent fallback
        """
        try:
            # First try our intelligent S&P 500 mapping
            symbol = get_symbol_from_name(search_term)
            
            # Check cache first
            if symbol in self.cache:
                logger.info(f"Cache hit for {symbol}")
                return self.cache[symbol]
            
            # Try the mapped symbol
            result = self._fetch_stock_data(symbol)
            if result:
                self.cache[symbol] = result
                return result
            
            # If that fails, try the original search term as a symbol
            if symbol != search_term.upper():
                logger.info(f"Trying original term as symbol: {search_term}")
                result = self._fetch_stock_data(search_term.upper())
                if result:
                    self.cache[search_term.upper()] = result
                    return result
            
            # Try common variations for international stocks
            variations = self._generate_symbol_variations(search_term)
            for variation in variations:
                logger.info(f"Trying variation: {variation}")
                result = self._fetch_stock_data(variation)
                if result:
                    self.cache[variation] = result
                    return result
            
            logger.warning(f"No valid stock found for: {search_term}")
            return None
            
        except Exception as e:
            logger.error(f"Error in universal stock search for {search_term}: {e}")
            return None
    
    def _fetch_stock_data(self, symbol):
        """Fetch stock data with enhanced validation"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Check if we have valid stock data
            has_name = info.get('longName') or info.get('shortName')
            has_price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose')
            
            if not (has_name and has_price):
                return None
            
            # Get current price with multiple fallbacks
            current_price = None
            if info.get('regularMarketPrice'):
                current_price = float(info['regularMarketPrice'])
            elif info.get('currentPrice'):
                current_price = float(info['currentPrice'])
            elif info.get('previousClose'):
                current_price = float(info['previousClose'])
            else:
                # Last resort: try historical data
                history = stock.history(period="1d")
                if not history.empty:
                    current_price = float(history['Close'].iloc[-1])
                else:
                    return None
            
            # Build basic stock info
            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'current_price': current_price,
                'sector': info.get('sector', 'Unknown'),
                'market_cap': info.get('marketCap'),
                'is_sp500': is_sp500(symbol.lower())
            }
            
        except Exception as e:
            logger.debug(f"Failed to fetch data for {symbol}: {e}")
            return None
    
    def _generate_symbol_variations(self, search_term):
        """Generate common symbol variations for international stocks"""
        variations = []
        base_term = search_term.upper().strip()
        
        # Common international suffixes
        international_suffixes = [
            '.TO',    # Toronto Stock Exchange
            '.L',     # London Stock Exchange  
            '.T',     # Tokyo Stock Exchange
            '.HK',    # Hong Kong Stock Exchange
            '.SS',    # Shanghai Stock Exchange
            '.SZ',    # Shenzhen Stock Exchange
            '.PA',    # Euronext Paris
            '.DE',    # Deutsche Börse
            '.MI',    # Borsa Italiana
            '.AS',    # Euronext Amsterdam
            '.SW',    # SIX Swiss Exchange
            'Y',      # ADR suffix (e.g., TOYOY for Toyota ADR)
            'F',      # Foreign stock suffix
        ]
        
        for suffix in international_suffixes:
            if suffix.startswith('.'):
                variations.append(f"{base_term}{suffix}")
            else:
                variations.append(f"{base_term}{suffix}")
        
        # Try removing common prefixes
        if base_term.startswith('THE '):
            variations.append(base_term[4:])
        
        # Try adding common company endings as symbols
        if len(base_term) <= 3:
            for ending in ['', 'A', 'B', 'C']:
                variations.append(f"{base_term}{ending}")
        
        return variations
    
    def clear_cache(self):
        """Clear the search cache"""
        self.cache = {}
        logger.info("Search cache cleared")

# Global instance
universal_search = UniversalStockSearch()