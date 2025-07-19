import yfinance as yf
import json
from datetime import datetime, timedelta
import logging
from sp500_stocks import get_symbol_from_name, is_sp500, get_all_symbols
from universal_stock_search import universal_search

logger = logging.getLogger(__name__)

class StockSearchService:
    """Service for searching and fetching real-time stock data"""
    
    def search_stock(self, symbol):
        """Search for a stock by symbol and return its current data"""
        try:
            # First try to convert company name to symbol using our comprehensive database
            clean_symbol = get_symbol_from_name(symbol.strip())
            
            if not clean_symbol or len(clean_symbol) > 10:
                logger.warning(f"Invalid symbol format: {symbol}")
                return None
            
            logger.info(f"Searching for stock: {symbol} -> {clean_symbol} (S&P 500: {is_sp500(clean_symbol)})")
            
            # Get stock data from yfinance
            stock = yf.Ticker(clean_symbol)
            info = stock.info
            
            # Enhanced validation - check multiple indicators of valid stock
            valid_indicators = [
                info.get('longName'),
                info.get('shortName'), 
                info.get('symbol'),
                info.get('regularMarketPrice'),
                info.get('currentPrice'),
                info.get('previousClose')
            ]
            
            # Allow stocks with minimal data if they have a price
            has_price_data = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose')
            has_basic_info = info.get('longName') or info.get('shortName') or info.get('symbol')
            
            if not (has_price_data and has_basic_info):
                logger.warning(f"Stock {clean_symbol} not found - insufficient data available")
                return None
            
            # Try to get current price from multiple sources
            current_price = None
            previous_close = None
            
            # First try from info object (real-time)
            if info.get('regularMarketPrice'):
                current_price = float(info['regularMarketPrice'])
                previous_close = float(info.get('previousClose', current_price))
            elif info.get('currentPrice'):
                current_price = float(info['currentPrice'])
                previous_close = float(info.get('previousClose', current_price))
            else:
                # Fallback to historical data
                history = stock.history(period="2d", interval="1d")
                if not history.empty:
                    current_price = float(history['Close'].iloc[-1])
                    previous_close = float(history['Close'].iloc[-2]) if len(history) > 1 else current_price
                else:
                    logger.warning(f"No price data available for {clean_symbol}")
                    return None
            
            # Get intraday data for volatility analysis
            intraday = stock.history(period="1d", interval="5m")
            day_high = intraday['High'].max() if not intraday.empty else current_price
            day_low = intraday['Low'].min() if not intraday.empty else current_price
            
            # Get historical data for technical analysis
            hist_data = stock.history(period="3mo")
            moving_avg_20 = hist_data['Close'].tail(20).mean() if len(hist_data) >= 20 else current_price
            moving_avg_50 = hist_data['Close'].tail(50).mean() if len(hist_data) >= 50 else current_price
            
            # Calculate price change
            price_change = current_price - previous_close
            price_change_percent = (price_change / previous_close * 100) if previous_close > 0 else 0
            
            # Build comprehensive stock data object
            stock_data = {
                'symbol': clean_symbol,
                'name': info.get('longName', info.get('shortName', symbol.upper())),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'country': info.get('country', 'Unknown'),
                'website': info.get('website', ''),
                'business_summary': info.get('longBusinessSummary', ''),
                'current_price': float(current_price),
                'previous_close': float(previous_close),
                'price_change': float(price_change),
                'price_change_percent': round(price_change_percent, 2),
                'day_high': float(day_high),
                'day_low': float(day_low),
                'volume': info.get('volume', 0),
                'avg_volume': info.get('averageVolume', 0),
                'avg_volume_10d': info.get('averageVolume10days', 0),
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'moving_avg_20': float(moving_avg_20),
                'moving_avg_50': float(moving_avg_50),
                'pe_ratio': info.get('trailingPE', None),
                'forward_pe': info.get('forwardPE', None),
                'peg_ratio': info.get('pegRatio', None),
                'price_to_book': info.get('priceToBook', None),
                'dividend_yield': info.get('dividendYield', None),
                'dividend_rate': info.get('dividendRate', None),
                'payout_ratio': info.get('payoutRatio', None),
                'beta': info.get('beta', None),
                'week_52_high': info.get('fiftyTwoWeekHigh', current_price),
                'week_52_low': info.get('fiftyTwoWeekLow', current_price),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'float_shares': info.get('floatShares', 0),
                'institutional_holdings': info.get('heldByInstitutions', None),
                'analyst_target_price': info.get('targetMeanPrice', None),
                'recommendation_key': info.get('recommendationKey', 'none'),
                'recommendation_mean': info.get('recommendationMean', None),
                'last_updated': datetime.now().isoformat()
            }
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Error searching for stock {symbol}: {str(e)}")
            
            # Fallback to universal search for any publicly traded stock
            logger.info(f"Trying universal search fallback for: {symbol}")
            try:
                fallback_result = universal_search.search_any_stock(symbol)
                if fallback_result:
                    logger.info(f"Universal search found: {fallback_result['symbol']}")
                    # Convert to our standard format
                    return {
                        'symbol': fallback_result['symbol'],
                        'name': fallback_result['name'],
                        'current_price': fallback_result['current_price'],
                        'previous_close': fallback_result['current_price'],  # Use same price as fallback
                        'price_change': 0.0,
                        'price_change_percent': 0.0,
                        'sector': fallback_result['sector'],
                        'market_cap': fallback_result.get('market_cap'),
                        'is_sp500': fallback_result['is_sp500']
                    }
            except Exception as fallback_error:
                logger.error(f"Universal search also failed: {fallback_error}")
            
            return None
    
    def get_stock_fundamentals(self, symbol):
        """Get comprehensive fundamental data for analysis"""
        try:
            stock = yf.Ticker(symbol.upper())
            info = stock.info
            
            # Get financial statements for deeper analysis
            try:
                financials = stock.financials
                balance_sheet = stock.balance_sheet
                cash_flow = stock.cashflow
                
                # Calculate additional ratios from financial statements
                total_revenue = financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in financials.index and len(financials.columns) > 0 else None
                total_assets = balance_sheet.loc['Total Assets'].iloc[0] if 'Total Assets' in balance_sheet.index and len(balance_sheet.columns) > 0 else None
                total_debt = balance_sheet.loc['Total Debt'].iloc[0] if 'Total Debt' in balance_sheet.index and len(balance_sheet.columns) > 0 else None
                
            except Exception as fs_error:
                logger.warning(f"Could not fetch financial statements for {symbol}: {fs_error}")
                total_revenue = None
                total_assets = None
                total_debt = None
            
            fundamentals = {
                'profit_margin': info.get('profitMargins', None),
                'operating_margin': info.get('operatingMargins', None),
                'gross_margin': info.get('grossMargins', None),
                'return_on_equity': info.get('returnOnEquity', None),
                'return_on_assets': info.get('returnOnAssets', None),
                'debt_to_equity': info.get('debtToEquity', None),
                'current_ratio': info.get('currentRatio', None),
                'quick_ratio': info.get('quickRatio', None),
                'revenue_growth': info.get('revenueGrowth', None),
                'earnings_growth': info.get('earningsGrowth', None),
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth', None),
                'revenue_per_share': info.get('revenuePerShare', None),
                'book_value_per_share': info.get('bookValue', None),
                'operating_cash_flow': info.get('operatingCashflow', None),
                'free_cash_flow': info.get('freeCashflow', None),
                'total_cash': info.get('totalCash', None),
                'total_debt': info.get('totalDebt', None),
                'ebitda': info.get('ebitda', None),
                'recommendation_key': info.get('recommendationKey', 'none'),
                'analyst_rating': info.get('recommendationMean', None),
                'number_of_analysts': info.get('numberOfAnalystOpinions', None),
                'price_target_high': info.get('targetHighPrice', None),
                'price_target_low': info.get('targetLowPrice', None),
                'price_target_mean': info.get('targetMeanPrice', None),
                # ESG and other metrics
                'esg_scores': info.get('esgScores', None),
                'audit_risk': info.get('auditRisk', None),
                'board_risk': info.get('boardRisk', None),
                'compensation_risk': info.get('compensationRisk', None),
                'shareholder_rights_risk': info.get('shareHolderRightsRisk', None),
                'overall_risk': info.get('overallRisk', None)
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