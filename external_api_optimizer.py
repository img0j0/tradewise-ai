"""
External API call optimization for TradeWise AI
Implements batching, caching, and rate limiting for Yahoo Finance and other APIs
"""

import yfinance as yf
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import requests
from typing import List, Dict, Any
from app import cache
from performance_monitor import performance_optimized, track_cache_hit, track_cache_miss

logger = logging.getLogger(__name__)

class YahooFinanceOptimizer:
    """Optimized Yahoo Finance API client with batching and caching"""
    
    def __init__(self, max_workers=5, timeout=10):
        self.max_workers = max_workers
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure session for better performance
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (TradeWise AI Bot)',
            'Accept': 'application/json'
        })
    
    @performance_optimized()
    def get_stock_data_batch(self, symbols: List[str]) -> Dict[str, Any]:
        """Get stock data for multiple symbols in parallel with caching"""
        results = {}
        cache_hits = 0
        cache_misses = 0
        
        # Check cache first
        symbols_to_fetch = []
        for symbol in symbols:
            cache_key = f"stock_data:{symbol}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                results[symbol] = cached_data
                cache_hits += 1
                track_cache_hit()
            else:
                symbols_to_fetch.append(symbol)
                cache_misses += 1
                track_cache_miss()
        
        logger.info(f"Cache performance: {cache_hits} hits, {cache_misses} misses")
        
        # Fetch uncached symbols in parallel
        if symbols_to_fetch:
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_symbol = {
                    executor.submit(self._fetch_single_stock, symbol): symbol 
                    for symbol in symbols_to_fetch
                }
                
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        stock_data = future.result(timeout=self.timeout)
                        if stock_data:
                            results[symbol] = stock_data
                            
                            # Cache the result
                            cache_key = f"stock_data:{symbol}"
                            cache.set(cache_key, stock_data, timeout=180)  # 3 minutes
                            
                    except Exception as e:
                        logger.error(f"Error fetching {symbol}: {e}")
                        results[symbol] = None
            
            fetch_time = (time.time() - start_time) * 1000
            logger.info(f"Fetched {len(symbols_to_fetch)} symbols in {fetch_time:.2f}ms")
        
        return results
    
    def _fetch_single_stock(self, symbol: str) -> Dict[str, Any]:
        """Fetch data for a single stock symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if not info or not info.get('symbol'):
                return None
            
            current_price = (
                info.get('currentPrice') or 
                info.get('regularMarketPrice') or 
                info.get('price')
            )
            
            if not current_price and not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
            
            prev_close = (
                info.get('previousClose') or 
                info.get('regularMarketPreviousClose')
            )
            
            if not prev_close and len(hist) > 1:
                prev_close = float(hist['Close'].iloc[-2])
            
            price_change = 0
            price_change_percent = 0
            
            if current_price and prev_close:
                price_change = current_price - prev_close
                price_change_percent = (price_change / prev_close) * 100
            
            return {
                'symbol': symbol.upper(),
                'name': info.get('longName') or info.get('shortName') or symbol,
                'current_price': float(current_price) if current_price else 0,
                'price_change': float(price_change),
                'price_change_percent': float(price_change_percent),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'volume': info.get('volume', 0),
                'avg_volume': info.get('averageVolume', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'fetch_timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    @performance_optimized()
    def get_market_data_batch(self, symbols: List[str]) -> Dict[str, Any]:
        """Get market data for multiple symbols with advanced caching"""
        cache_key = f"market_batch:{':'.join(sorted(symbols))}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            track_cache_hit()
            logger.debug(f"Market batch cache HIT for {len(symbols)} symbols")
            return cached_result
        
        track_cache_miss()
        logger.debug(f"Market batch cache MISS for {len(symbols)} symbols")
        
        # Fetch data using batch method
        results = self.get_stock_data_batch(symbols)
        
        # Cache the batch result
        if results:
            cache.set(cache_key, results, timeout=300)  # 5 minutes for market data
        
        return results

class APICallOptimizer:
    """General API call optimization utilities"""
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_cached_market_overview():
        """Cached market overview data with LRU caching"""
        try:
            # Popular market indices
            indices = ['^GSPC', '^DJI', '^IXIC', '^RUT']
            optimizer = YahooFinanceOptimizer()
            
            market_data = optimizer.get_stock_data_batch(indices)
            
            overview = {
                'S&P 500': market_data.get('^GSPC'),
                'Dow Jones': market_data.get('^DJI'), 
                'NASDAQ': market_data.get('^IXIC'),
                'Russell 2000': market_data.get('^RUT'),
                'last_updated': time.time()
            }
            
            return {
                'success': True,
                'data': overview
            }
            
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    @performance_optimized()
    def get_popular_stocks_data():
        """Get data for popular stocks with optimized batching"""
        popular_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
            'META', 'NVDA', 'NFLX', 'AMD', 'CRM'
        ]
        
        optimizer = YahooFinanceOptimizer()
        return optimizer.get_market_data_batch(popular_symbols)
    
    @staticmethod
    def preload_cache_for_popular_stocks():
        """Preload cache with popular stock data"""
        try:
            start_time = time.time()
            
            # Get popular stocks data (this will cache it)
            APICallOptimizer.get_popular_stocks_data()
            
            # Get market overview (this will cache it)
            APICallOptimizer.get_cached_market_overview()
            
            preload_time = (time.time() - start_time) * 1000
            
            logger.info(f"Cache preloaded in {preload_time:.2f}ms")
            
            return {
                'success': True,
                'preload_time_ms': preload_time,
                'stocks_cached': 10,
                'indices_cached': 4
            }
            
        except Exception as e:
            logger.error(f"Error preloading cache: {e}")
            return {
                'success': False,
                'error': str(e)
            }

class RateLimiter:
    """Advanced rate limiting for external API calls"""
    
    def __init__(self, max_calls=60, window=60):
        self.max_calls = max_calls
        self.window = window
        self.calls = []
    
    def can_make_call(self):
        """Check if a call can be made within rate limits"""
        now = time.time()
        
        # Remove old calls outside the window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.window]
        
        # Check if we can make another call
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        
        return False
    
    def time_until_next_call(self):
        """Calculate time until next call is allowed"""
        if not self.calls:
            return 0
        
        oldest_call = min(self.calls)
        time_since_oldest = time.time() - oldest_call
        
        if time_since_oldest >= self.window:
            return 0
        
        return self.window - time_since_oldest

# Initialize optimizers
yahoo_optimizer = YahooFinanceOptimizer()
api_optimizer = APICallOptimizer()
rate_limiter = RateLimiter(max_calls=100, window=60)  # 100 calls per minute