"""
Real-time Data Engine - Provides live market data feeds and updates
"""

import yfinance as yf
import logging
import json
import time
from datetime import datetime, timedelta
from threading import Thread, Lock
import requests
from flask_socketio import emit
import pandas as pd

logger = logging.getLogger(__name__)

class RealTimeDataEngine:
    """Engine for real-time market data and live updates"""
    
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.active_subscriptions = set()
        self.data_cache = {}
        self.cache_lock = Lock()
        self.last_update = {}
        self.update_interval = 30  # seconds
        self.is_running = False
        
    def start_realtime_updates(self):
        """Start the real-time data update thread"""
        if not self.is_running:
            self.is_running = True
            update_thread = Thread(target=self._update_loop, daemon=True)
            update_thread.start()
            logger.info("Real-time data engine started")
    
    def stop_realtime_updates(self):
        """Stop the real-time data updates"""
        self.is_running = False
        logger.info("Real-time data engine stopped")
    
    def subscribe_to_symbol(self, symbol, client_id=None):
        """Subscribe to real-time updates for a symbol"""
        symbol = symbol.upper()
        self.active_subscriptions.add(symbol)
        logger.info(f"Subscribed to real-time data for {symbol}")
        
        # Send immediate data if available
        if symbol in self.data_cache:
            self._emit_update(symbol, self.data_cache[symbol])
        else:
            # Fetch initial data
            initial_data = self.get_live_quote(symbol)
            if initial_data:
                self._cache_data(symbol, initial_data)
                self._emit_update(symbol, initial_data)
    
    def unsubscribe_from_symbol(self, symbol):
        """Unsubscribe from real-time updates for a symbol"""
        symbol = symbol.upper()
        self.active_subscriptions.discard(symbol)
        logger.info(f"Unsubscribed from real-time data for {symbol}")
    
    def get_live_quote(self, symbol):
        """Get live quote data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get real-time quote
            info = ticker.info
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            previous_close = info.get('previousClose', latest['Close'])
            
            quote_data = {
                'symbol': symbol,
                'price': float(latest['Close']),
                'change': float(latest['Close'] - previous_close),
                'change_percent': float((latest['Close'] - previous_close) / previous_close * 100),
                'volume': int(latest['Volume']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'open': float(latest['Open']),
                'timestamp': datetime.now().isoformat(),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'is_market_open': self._is_market_open()
            }
            
            return quote_data
            
        except Exception as e:
            logger.error(f"Error fetching live quote for {symbol}: {e}")
            return None
    
    def get_market_movers(self):
        """Get top market movers (gainers/losers)"""
        try:
            # Popular stocks to check
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
            movers_data = []
            
            for symbol in symbols:
                quote = self.get_live_quote(symbol)
                if quote:
                    movers_data.append({
                        'symbol': symbol,
                        'price': quote['price'],
                        'change_percent': quote['change_percent'],
                        'volume': quote['volume']
                    })
            
            # Sort by absolute change percent
            movers_data.sort(key=lambda x: abs(x['change_percent']), reverse=True)
            
            return {
                'top_gainers': [m for m in movers_data if m['change_percent'] > 0][:5],
                'top_losers': [m for m in movers_data if m['change_percent'] < 0][:5],
                'most_active': sorted(movers_data, key=lambda x: x['volume'], reverse=True)[:5],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching market movers: {e}")
            return None
    
    def get_market_overview(self):
        """Get overall market indices and sentiment"""
        try:
            indices = ['^GSPC', '^DJI', '^IXIC', '^RUT']  # S&P 500, Dow, NASDAQ, Russell
            index_names = ['S&P 500', 'Dow Jones', 'NASDAQ', 'Russell 2000']
            
            overview_data = {
                'indices': [],
                'market_sentiment': 'Neutral',
                'vix': None,
                'timestamp': datetime.now().isoformat()
            }
            
            positive_count = 0
            total_count = 0
            
            for i, symbol in enumerate(indices):
                quote = self.get_live_quote(symbol)
                if quote:
                    overview_data['indices'].append({
                        'name': index_names[i],
                        'symbol': symbol,
                        'price': quote['price'],
                        'change': quote['change'],
                        'change_percent': quote['change_percent']
                    })
                    
                    if quote['change_percent'] > 0:
                        positive_count += 1
                    total_count += 1
            
            # Calculate market sentiment
            if total_count > 0:
                positive_ratio = positive_count / total_count
                if positive_ratio >= 0.75:
                    overview_data['market_sentiment'] = 'Bullish'
                elif positive_ratio >= 0.5:
                    overview_data['market_sentiment'] = 'Positive'
                elif positive_ratio >= 0.25:
                    overview_data['market_sentiment'] = 'Neutral'
                else:
                    overview_data['market_sentiment'] = 'Bearish'
            
            # Get VIX (fear index)
            vix_quote = self.get_live_quote('^VIX')
            if vix_quote:
                overview_data['vix'] = {
                    'value': vix_quote['price'],
                    'change_percent': vix_quote['change_percent']
                }
            
            return overview_data
            
        except Exception as e:
            logger.error(f"Error fetching market overview: {e}")
            return None
    
    def get_sector_performance(self):
        """Get sector performance data"""
        try:
            # Sector ETFs as proxies
            sectors = {
                'XLK': 'Technology',
                'XLF': 'Financial',
                'XLV': 'Healthcare', 
                'XLE': 'Energy',
                'XLI': 'Industrial',
                'XLY': 'Consumer Discretionary',
                'XLP': 'Consumer Staples',
                'XLB': 'Materials',
                'XLRE': 'Real Estate',
                'XLU': 'Utilities'
            }
            
            sector_data = []
            
            for etf, sector_name in sectors.items():
                quote = self.get_live_quote(etf)
                if quote:
                    sector_data.append({
                        'sector': sector_name,
                        'symbol': etf,
                        'change_percent': quote['change_percent'],
                        'price': quote['price']
                    })
            
            # Sort by performance
            sector_data.sort(key=lambda x: x['change_percent'], reverse=True)
            
            return {
                'sectors': sector_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching sector performance: {e}")
            return None
    
    def _update_loop(self):
        """Main update loop for real-time data"""
        while self.is_running:
            try:
                if self.active_subscriptions:
                    for symbol in list(self.active_subscriptions):
                        # Check if we need to update this symbol
                        last_update = self.last_update.get(symbol, 0)
                        if time.time() - last_update >= self.update_interval:
                            
                            # Fetch new data
                            new_data = self.get_live_quote(symbol)
                            if new_data:
                                # Check if data has changed significantly
                                old_data = self.data_cache.get(symbol)
                                if self._should_update(old_data, new_data):
                                    self._cache_data(symbol, new_data)
                                    self._emit_update(symbol, new_data)
                                    
                                self.last_update[symbol] = time.time()
                
                # Sleep between update cycles
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                time.sleep(10)  # Wait longer on error
    
    def _should_update(self, old_data, new_data):
        """Check if data has changed enough to warrant an update"""
        if not old_data:
            return True
            
        # Update if price changed by more than 0.01% or volume changed significantly
        price_change = abs(new_data['price'] - old_data.get('price', 0)) / old_data.get('price', 1)
        volume_change = abs(new_data['volume'] - old_data.get('volume', 0)) / old_data.get('volume', 1)
        
        return price_change > 0.0001 or volume_change > 0.1
    
    def _cache_data(self, symbol, data):
        """Cache data with thread safety"""
        with self.cache_lock:
            self.data_cache[symbol] = data
    
    def _emit_update(self, symbol, data):
        """Emit real-time update via WebSocket"""
        if self.socketio:
            self.socketio.emit('market_update', {
                'symbol': symbol,
                'data': data
            }, room=f'stock_{symbol}')
    
    def _is_market_open(self):
        """Check if US stock market is currently open"""
        now = datetime.now()
        # Simplified - assume EST/EDT for now
        hour = now.hour
        weekday = now.weekday()
        
        # Market is open Monday-Friday, 9:30 AM to 4:00 PM EST
        return (weekday < 5 and 
                ((hour == 9 and now.minute >= 30) or 
                 (10 <= hour < 16) or 
                 (hour == 16 and now.minute == 0)))

# Global instance
realtime_engine = RealTimeDataEngine()