#!/usr/bin/env python3
"""
Market Data Collector
Collects real-time market data during trading hours for analysis
"""

import yfinance as yf
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, List
import threading
import schedule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataCollector:
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.market_data = {}
        self.intraday_data = {}
        self.is_collecting = False
        self.collection_thread = None
        
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        now = datetime.now()
        # Market hours: 9:30 AM - 4:00 PM EST (Monday-Friday)
        if now.weekday() >= 5:  # Weekend
            return False
        
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    
    def collect_snapshot(self) -> Dict:
        """Collect current market snapshot"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'data': {}
        }
        
        for symbol in self.symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Get current price and key metrics
                current_price = info.get('currentPrice', 0)
                if current_price == 0:
                    # Fallback to regular market price
                    current_price = info.get('regularMarketPrice', 0)
                
                snapshot['data'][symbol] = {
                    'price': current_price,
                    'volume': info.get('volume', 0),
                    'market_cap': info.get('marketCap', 0),
                    'pe_ratio': info.get('trailingPE', 0),
                    'day_high': info.get('dayHigh', 0),
                    'day_low': info.get('dayLow', 0),
                    'change_percent': info.get('regularMarketChangePercent', 0),
                    'fifty_day_avg': info.get('fiftyDayAverage', 0),
                    'two_hundred_day_avg': info.get('twoHundredDayAverage', 0)
                }
                
                logger.info(f"Collected data for {symbol}: ${current_price}")
                
            except Exception as e:
                logger.error(f"Error collecting data for {symbol}: {e}")
                snapshot['data'][symbol] = {'error': str(e)}
        
        return snapshot
    
    def collect_intraday_data(self, symbol: str) -> pd.DataFrame:
        """Collect detailed intraday data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            # Get 1-minute data for current day
            hist = ticker.history(period='1d', interval='1m')
            
            if not hist.empty:
                self.intraday_data[symbol] = hist
                logger.info(f"Collected intraday data for {symbol}: {len(hist)} data points")
            
            return hist
            
        except Exception as e:
            logger.error(f"Error collecting intraday data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, symbol: str) -> Dict:
        """Calculate technical indicators for a symbol"""
        if symbol not in self.intraday_data:
            return {}
        
        df = self.intraday_data[symbol].copy()
        
        if df.empty or len(df) < 20:
            return {}
        
        try:
            # Simple Moving Averages
            df['SMA_10'] = df['Close'].rolling(window=10).mean()
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = df['Close'].ewm(span=12).mean()
            exp2 = df['Close'].ewm(span=26).mean()
            df['MACD'] = exp1 - exp2
            df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
            
            # Bollinger Bands
            df['BB_Middle'] = df['Close'].rolling(window=20).mean()
            bb_std = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            
            # Volume indicators
            df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
            
            # Get latest values
            latest = df.iloc[-1]
            
            indicators = {
                'rsi': float(latest['RSI']) if not pd.isna(latest['RSI']) else 0,
                'macd': float(latest['MACD']) if not pd.isna(latest['MACD']) else 0,
                'macd_signal': float(latest['MACD_Signal']) if not pd.isna(latest['MACD_Signal']) else 0,
                'bb_upper': float(latest['BB_Upper']) if not pd.isna(latest['BB_Upper']) else 0,
                'bb_middle': float(latest['BB_Middle']) if not pd.isna(latest['BB_Middle']) else 0,
                'bb_lower': float(latest['BB_Lower']) if not pd.isna(latest['BB_Lower']) else 0,
                'sma_10': float(latest['SMA_10']) if not pd.isna(latest['SMA_10']) else 0,
                'sma_20': float(latest['SMA_20']) if not pd.isna(latest['SMA_20']) else 0,
                'volume_ratio': float(latest['Volume_Ratio']) if not pd.isna(latest['Volume_Ratio']) else 0,
                'price': float(latest['Close']),
                'volume': int(latest['Volume'])
            }
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators for {symbol}: {e}")
            return {}
    
    def start_collection(self):
        """Start continuous data collection"""
        if not self.is_market_open():
            logger.info("Market is closed. Collection will start when market opens.")
            return
        
        self.is_collecting = True
        logger.info("Starting market data collection...")
        
        def collect_data():
            while self.is_collecting and self.is_market_open():
                try:
                    # Collect snapshot
                    snapshot = self.collect_snapshot()
                    
                    # Save snapshot
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f'market_snapshot_{timestamp}.json'
                    with open(filename, 'w') as f:
                        json.dump(snapshot, f, indent=2)
                    
                    # Collect intraday data and calculate indicators
                    for symbol in self.symbols:
                        self.collect_intraday_data(symbol)
                        indicators = self.calculate_technical_indicators(symbol)
                        
                        if indicators:
                            # Save indicators
                            indicator_file = f'indicators_{symbol}_{timestamp}.json'
                            with open(indicator_file, 'w') as f:
                                json.dump(indicators, f, indent=2)
                    
                    logger.info(f"Data collection cycle completed at {datetime.now()}")
                    
                    # Wait 5 minutes before next collection
                    time.sleep(300)
                    
                except Exception as e:
                    logger.error(f"Error in data collection cycle: {e}")
                    time.sleep(60)  # Wait 1 minute before retry
        
        self.collection_thread = threading.Thread(target=collect_data)
        self.collection_thread.daemon = True
        self.collection_thread.start()
    
    def stop_collection(self):
        """Stop data collection"""
        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join()
        logger.info("Market data collection stopped.")
    
    def get_market_summary(self) -> Dict:
        """Get current market summary"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'market_open': self.is_market_open(),
            'symbols': {},
            'overall_metrics': {}
        }
        
        prices = []
        volumes = []
        changes = []
        
        for symbol in self.symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                volume = info.get('volume', 0)
                change = info.get('regularMarketChangePercent', 0)
                
                summary['symbols'][symbol] = {
                    'price': price,
                    'volume': volume,
                    'change_percent': change,
                    'market_cap': info.get('marketCap', 0)
                }
                
                if price > 0:
                    prices.append(price)
                if volume > 0:
                    volumes.append(volume)
                if change != 0:
                    changes.append(change)
                
            except Exception as e:
                logger.error(f"Error getting summary for {symbol}: {e}")
        
        # Calculate overall metrics
        if prices:
            summary['overall_metrics'] = {
                'average_price': sum(prices) / len(prices),
                'total_volume': sum(volumes),
                'average_change': sum(changes) / len(changes) if changes else 0,
                'positive_movers': len([c for c in changes if c > 0]),
                'negative_movers': len([c for c in changes if c < 0])
            }
        
        return summary
    
    def save_end_of_day_report(self) -> str:
        """Save comprehensive end-of-day report"""
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'collection_summary': {
                'symbols_tracked': self.symbols,
                'total_symbols': len(self.symbols),
                'data_points_collected': sum(len(df) for df in self.intraday_data.values())
            },
            'market_summary': self.get_market_summary(),
            'technical_indicators': {}
        }
        
        # Add technical indicators for each symbol
        for symbol in self.symbols:
            indicators = self.calculate_technical_indicators(symbol)
            if indicators:
                report['technical_indicators'][symbol] = indicators
        
        # Save report
        filename = f'market_report_{datetime.now().strftime("%Y%m%d")}.json'
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"End-of-day report saved to {filename}")
        return filename

def main():
    """Main function to run market data collection"""
    # AI trading bot watchlist
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
    
    collector = MarketDataCollector(symbols)
    
    # Get current market summary
    summary = collector.get_market_summary()
    print("Current Market Summary:")
    print(json.dumps(summary, indent=2))
    
    # Start collection if market is open
    if collector.is_market_open():
        print("Market is open. Starting data collection...")
        collector.start_collection()
        
        # Run until market closes
        while collector.is_market_open():
            time.sleep(300)  # Check every 5 minutes
        
        collector.stop_collection()
        collector.save_end_of_day_report()
        print("Market closed. Data collection completed.")
    else:
        print("Market is closed. Collection will start when market opens.")

if __name__ == "__main__":
    main()