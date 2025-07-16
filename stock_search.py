import yfinance as yf
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StockSearchService:
    """Service for searching and fetching real-time stock data"""
    
    def search_stock(self, symbol):
        """Search for a stock by symbol and return its current data"""
        try:
            # Get stock data from yfinance
            stock = yf.Ticker(symbol.upper())
            info = stock.info
            
            # Get current price data
            history = stock.history(period="1d", interval="1m")
            if history.empty:
                return None
                
            current_price = history['Close'].iloc[-1]
            
            # Get historical data for moving average
            hist_data = stock.history(period="1mo")
            moving_avg_20 = hist_data['Close'].tail(20).mean() if len(hist_data) >= 20 else current_price
            
            # Build stock data object
            stock_data = {
                'symbol': symbol.upper(),
                'name': info.get('longName', info.get('shortName', symbol.upper())),
                'sector': info.get('sector', 'Unknown'),
                'current_price': round(current_price, 2),
                'previous_close': round(info.get('previousClose', current_price), 2),
                'high': round(info.get('dayHigh', current_price), 2),
                'low': round(info.get('dayLow', current_price), 2),
                'volume': info.get('volume', 0),
                'avg_volume': info.get('averageVolume', 0),
                'market_cap': info.get('marketCap', 0),
                'moving_avg_20': round(moving_avg_20, 2),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 1.0),
                'week_52_high': info.get('fiftyTwoWeekHigh', current_price),
                'week_52_low': info.get('fiftyTwoWeekLow', current_price),
                'last_updated': datetime.now().isoformat()
            }
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Error searching for stock {symbol}: {str(e)}")
            return None
    
    def get_stock_fundamentals(self, symbol):
        """Get additional fundamental data for risk analysis"""
        try:
            stock = yf.Ticker(symbol.upper())
            info = stock.info
            
            fundamentals = {
                'profit_margin': info.get('profitMargins', 0),
                'operating_margin': info.get('operatingMargins', 0),
                'return_on_equity': info.get('returnOnEquity', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'earnings_growth': info.get('earningsGrowth', 0),
                'recommendation_key': info.get('recommendationKey', 'none'),
                'analyst_rating': info.get('recommendationMean', 3.0)
            }
            
            return fundamentals
            
        except Exception as e:
            logger.error(f"Error getting fundamentals for {symbol}: {str(e)}")
            return None
    
    def validate_symbol(self, symbol):
        """Validate if a stock symbol exists"""
        try:
            stock = yf.Ticker(symbol.upper())
            info = stock.info
            # Check if we got valid data
            return 'regularMarketPrice' in info or 'currentPrice' in info
        except:
            return False

# For backwards compatibility with existing code
def search_stock_by_symbol(symbol):
    """Legacy function for searching stocks"""
    service = StockSearchService()
    return service.search_stock(symbol)