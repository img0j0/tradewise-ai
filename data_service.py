import json
import os
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self):
        self.data_file = os.path.join(os.path.dirname(__file__), 'data', 'sample_stocks.json')
        self.stocks_data = self._load_sample_data()
        
    def _load_sample_data(self):
        """Load sample stock data from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Sample data file not found, using default data")
            return self._generate_default_data()
        except json.JSONDecodeError:
            logger.error("Error decoding sample data, using default data")
            return self._generate_default_data()
    
    def _generate_default_data(self):
        """Generate default sample data if file is not available"""
        return {
            "stocks": [
                {
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "sector": "Technology",
                    "current_price": 150.25,
                    "previous_close": 148.50,
                    "high": 152.00,
                    "low": 147.80,
                    "volume": 45000000,
                    "avg_volume": 42000000,
                    "market_cap": 2500000000000,
                    "moving_avg_20": 145.30,
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "symbol": "GOOGL",
                    "name": "Alphabet Inc.",
                    "sector": "Technology",
                    "current_price": 2750.80,
                    "previous_close": 2720.15,
                    "high": 2765.00,
                    "low": 2735.20,
                    "volume": 1200000,
                    "avg_volume": 1150000,
                    "market_cap": 1800000000000,
                    "moving_avg_20": 2680.45,
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "symbol": "TSLA",
                    "name": "Tesla Inc.",
                    "sector": "Automotive",
                    "current_price": 245.67,
                    "previous_close": 250.12,
                    "high": 252.33,
                    "low": 242.10,
                    "volume": 28000000,
                    "avg_volume": 25000000,
                    "market_cap": 780000000000,
                    "moving_avg_20": 240.85,
                    "last_updated": datetime.now().isoformat()
                }
            ]
        }
    
    def get_all_stocks(self):
        """Get all available stocks data"""
        # Simulate real-time price updates
        updated_stocks = []
        for stock in self.stocks_data['stocks']:
            updated_stock = stock.copy()
            # Add small random price movements
            price_change = random.uniform(-0.05, 0.05) * stock['current_price']
            updated_stock['current_price'] = round(stock['current_price'] + price_change, 2)
            updated_stock['last_updated'] = datetime.now().isoformat()
            updated_stocks.append(updated_stock)
        
        return updated_stocks
    
    def get_stock_by_symbol(self, symbol):
        """Get specific stock data by symbol"""
        stocks = self.get_all_stocks()
        for stock in stocks:
            if stock['symbol'].upper() == symbol.upper():
                return stock
        return None
    
    def get_filtered_stocks(self, sector=None, min_price=None, max_price=None):
        """Get stocks filtered by criteria"""
        stocks = self.get_all_stocks()
        filtered_stocks = []
        
        for stock in stocks:
            # Sector filter
            if sector and stock['sector'].lower() != sector.lower():
                continue
            
            # Price range filter
            if min_price and stock['current_price'] < min_price:
                continue
            if max_price and stock['current_price'] > max_price:
                continue
            
            filtered_stocks.append(stock)
        
        return filtered_stocks
    
    def get_market_overview(self):
        """Get market overview statistics"""
        stocks = self.get_all_stocks()
        
        if not stocks:
            return {
                'total_stocks': 0,
                'gainers': 0,
                'losers': 0,
                'avg_change': 0,
                'total_volume': 0
            }
        
        gainers = 0
        losers = 0
        total_change = 0
        total_volume = 0
        
        for stock in stocks:
            change = stock['current_price'] - stock['previous_close']
            total_change += change
            total_volume += stock['volume']
            
            if change > 0:
                gainers += 1
            elif change < 0:
                losers += 1
        
        return {
            'total_stocks': len(stocks),
            'gainers': gainers,
            'losers': losers,
            'unchanged': len(stocks) - gainers - losers,
            'avg_change': total_change / len(stocks) if stocks else 0,
            'total_volume': total_volume
        }
    
    def get_top_movers(self, limit=5):
        """Get top gaining and losing stocks"""
        stocks = self.get_all_stocks()
        
        # Calculate percentage changes
        for stock in stocks:
            change_pct = ((stock['current_price'] - stock['previous_close']) / 
                         stock['previous_close']) * 100
            stock['change_pct'] = change_pct
        
        # Sort by percentage change
        sorted_stocks = sorted(stocks, key=lambda x: x['change_pct'], reverse=True)
        
        return {
            'top_gainers': sorted_stocks[:limit],
            'top_losers': sorted_stocks[-limit:]
        }
    
    def get_sectors(self):
        """Get list of available sectors"""
        stocks = self.get_all_stocks()
        sectors = set()
        
        for stock in stocks:
            sectors.add(stock['sector'])
        
        return sorted(list(sectors))
    
    def update_stock_data(self, symbol, data):
        """Update stock data (for future real-time integration)"""
        try:
            for i, stock in enumerate(self.stocks_data['stocks']):
                if stock['symbol'].upper() == symbol.upper():
                    self.stocks_data['stocks'][i].update(data)
                    return True
            return False
        except Exception as e:
            logger.error(f"Error updating stock data: {e}")
            return False
