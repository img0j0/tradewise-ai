"""
Advanced Stock Search Engine
Lightning-fast search with fuzzy matching, autocomplete, and comprehensive data sources
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from rapidfuzz import fuzz, process
import requests
import yfinance as yf
from flask import session
import sqlite3
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

logger = logging.getLogger(__name__)

class AdvancedSearchEngine:
    def __init__(self):
        self.search_cache = {}
        self.stock_metadata = {}
        self.search_history = {}
        self.popularity_scores = {}
        self.last_update = None
        self.db_path = 'stock_search_cache.db'
        self.lock = threading.Lock()
        
        # Initialize database
        self.init_database()
        
        # Load initial data
        self.load_stock_metadata()
        
        logger.info("Advanced Search Engine initialized")
    
    def init_database(self):
        """Initialize SQLite database for search cache and metadata"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Stock metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_metadata (
                    symbol TEXT PRIMARY KEY,
                    company_name TEXT,
                    sector TEXT,
                    industry TEXT,
                    exchange TEXT,
                    market_cap REAL,
                    logo_url TEXT,
                    last_updated TIMESTAMP,
                    search_count INTEGER DEFAULT 0
                )
            ''')
            
            # Search cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_cache (
                    query TEXT PRIMARY KEY,
                    results TEXT,
                    timestamp TIMESTAMP,
                    hit_count INTEGER DEFAULT 0
                )
            ''')
            
            # Search analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT,
                    selected_symbol TEXT,
                    timestamp TIMESTAMP,
                    user_session TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Search database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def load_stock_metadata(self):
        """Load comprehensive stock metadata from database and external sources"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load existing metadata
            cursor.execute('SELECT * FROM stock_metadata')
            rows = cursor.fetchall()
            
            for row in rows:
                symbol = row[0]
                self.stock_metadata[symbol] = {
                    'symbol': row[0],
                    'company_name': row[1],
                    'sector': row[2] or 'Unknown',
                    'industry': row[3] or 'Unknown',
                    'exchange': row[4] or 'Unknown',
                    'market_cap': row[5],
                    'logo_url': row[6],
                    'last_updated': row[7],
                    'search_count': row[8] or 0
                }
            
            conn.close()
            
            # If database is empty or outdated, populate with initial data
            if len(self.stock_metadata) < 100 or self._needs_update():
                self.populate_initial_metadata()
                
            logger.info(f"Loaded {len(self.stock_metadata)} stocks from metadata cache")
            
        except Exception as e:
            logger.error(f"Error loading stock metadata: {e}")
            self.populate_initial_metadata()
    
    def _needs_update(self):
        """Check if metadata needs updating (daily update)"""
        if not self.last_update:
            return True
        
        try:
            last_update = datetime.fromisoformat(self.last_update)
            return datetime.now() - last_update > timedelta(days=1)
        except:
            return True
    
    def populate_initial_metadata(self):
        """Populate initial stock metadata from popular stocks"""
        popular_stocks = [
            # Tech Giants
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'META', 'AMZN', 'TSLA', 'NVDA', 'NFLX', 'CRM',
            # Financial
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'V', 'MA', 'PYPL', 'SQ',
            # Healthcare
            'JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'ABT', 'DHR', 'BMY', 'LLY', 'MRK',
            # Consumer
            'WMT', 'HD', 'PG', 'KO', 'PEP', 'COST', 'TGT', 'SBUX', 'MCD', 'NKE',
            # Industrial
            'BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'LMT', 'RTX', 'DE', 'NOC',
            # Energy
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'OXY', 'PSX', 'VLO', 'MPC', 'KMI',
            # Meme/Popular
            'GME', 'AMC', 'BB', 'NOK', 'PLTR', 'RIVN', 'LCID', 'COIN', 'HOOD', 'SOFI',
            # ETFs
            'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'GLD', 'SLV', 'TLT'
        ]
        
        logger.info("Populating initial stock metadata...")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_symbol = {
                executor.submit(self._fetch_stock_info, symbol): symbol 
                for symbol in popular_stocks
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    stock_info = future.result(timeout=10)
                    if stock_info:
                        self._save_stock_metadata(stock_info)
                except Exception as e:
                    logger.warning(f"Failed to fetch info for {symbol}: {e}")
        
        self.last_update = datetime.now().isoformat()
        logger.info(f"Initial metadata population completed: {len(self.stock_metadata)} stocks")
    
    def _fetch_stock_info(self, symbol: str) -> Optional[Dict]:
        """Fetch comprehensive stock information from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'symbol' not in info:
                return None
            
            # Extract relevant information
            stock_info = {
                'symbol': symbol.upper(),
                'company_name': info.get('longName') or info.get('shortName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'exchange': info.get('exchange', 'Unknown'),
                'market_cap': info.get('marketCap'),
                'logo_url': info.get('logo_url'),
                'last_updated': datetime.now().isoformat(),
                'search_count': 0
            }
            
            return stock_info
            
        except Exception as e:
            logger.warning(f"Error fetching info for {symbol}: {e}")
            return None
    
    def _save_stock_metadata(self, stock_info: Dict):
        """Save stock metadata to database and cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO stock_metadata 
                (symbol, company_name, sector, industry, exchange, market_cap, logo_url, last_updated, search_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stock_info['symbol'],
                stock_info['company_name'],
                stock_info['sector'],
                stock_info['industry'],
                stock_info['exchange'],
                stock_info['market_cap'],
                stock_info['logo_url'],
                stock_info['last_updated'],
                stock_info.get('search_count', 0)
            ))
            
            conn.commit()
            conn.close()
            
            # Update in-memory cache
            self.stock_metadata[stock_info['symbol']] = stock_info
            
        except Exception as e:
            logger.error(f"Error saving stock metadata: {e}")
    
    def search_stocks(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Advanced stock search with fuzzy matching and intelligent ranking
        Supports symbol, company name, and partial matches
        """
        if not query or len(query.strip()) < 1:
            return []
        
        query = query.strip().upper()
        
        # Check cache first
        cache_key = f"{query}:{limit}"
        if cache_key in self.search_cache:
            cached_result = self.search_cache[cache_key]
            if time.time() - cached_result['timestamp'] < 300:  # 5 minute cache
                self._update_cache_hit_count(query)
                return cached_result['results']
        
        # Record search analytics
        self._record_search_analytics(query)
        
        # Perform search
        results = self._perform_fuzzy_search(query, limit)
        
        # Cache results
        self.search_cache[cache_key] = {
            'results': results,
            'timestamp': time.time()
        }
        
        return results
    
    def _perform_fuzzy_search(self, query: str, limit: int) -> List[Dict]:
        """Perform fuzzy search across symbols and company names"""
        results = []
        
        # Prepare search targets
        search_targets = []
        for symbol, info in self.stock_metadata.items():
            # Add symbol for exact/fuzzy matching
            search_targets.append({
                'text': symbol,
                'type': 'symbol',
                'info': info,
                'boost': 100  # Exact symbol matches get highest boost
            })
            
            # Add company name for fuzzy matching
            company_name = info.get('company_name', '')
            if company_name and company_name != symbol:
                search_targets.append({
                    'text': company_name.upper(),
                    'type': 'company',
                    'info': info,
                    'boost': 50  # Company name matches get medium boost
                })
        
        # Exact symbol match (highest priority)
        exact_matches = []
        if query in self.stock_metadata:
            exact_matches.append({
                'symbol': query,
                'company_name': self.stock_metadata[query]['company_name'],
                'sector': self.stock_metadata[query]['sector'],
                'exchange': self.stock_metadata[query]['exchange'],
                'match_type': 'exact_symbol',
                'match_score': 100,
                'popularity_score': self._get_popularity_score(query),
                'logo_url': self.stock_metadata[query].get('logo_url'),
                'market_status': self._get_market_status(self.stock_metadata[query]['exchange']),
                'rank_score': 100
            })
        
        # Fuzzy matching for partial queries
        fuzzy_matches = []
        
        # Symbol fuzzy matching
        symbol_texts = [(target['text'], target) for target in search_targets if target['type'] == 'symbol']
        if symbol_texts:
            symbol_matches = process.extract(
                query, 
                [text for text, _ in symbol_texts], 
                scorer=fuzz.WRatio,
                limit=limit * 2
            )
            
            for match_text, score, _ in symbol_matches:
                if score >= 60:  # Minimum similarity threshold
                    target = next(target for text, target in symbol_texts if text == match_text)
                    info = target['info']
                    
                    fuzzy_matches.append({
                        'symbol': info['symbol'],
                        'company_name': info['company_name'],
                        'sector': info['sector'],
                        'exchange': info['exchange'],
                        'match_type': 'fuzzy_symbol',
                        'match_score': score,
                        'popularity_score': self._get_popularity_score(info['symbol']),
                        'logo_url': info.get('logo_url'),
                        'market_status': self._get_market_status(info['exchange']),
                        'rank_score': score
                    })
        
        # Company name fuzzy matching
        company_texts = [(target['text'], target) for target in search_targets if target['type'] == 'company']
        if company_texts:
            company_matches = process.extract(
                query, 
                [text for text, _ in company_texts], 
                scorer=fuzz.partial_ratio,
                limit=limit * 2
            )
            
            for match_text, score, _ in company_matches:
                if score >= 70:  # Higher threshold for company names
                    target = next(target for text, target in company_texts if text == match_text)
                    info = target['info']
                    
                    # Avoid duplicates
                    if not any(r['symbol'] == info['symbol'] for r in fuzzy_matches + exact_matches):
                        fuzzy_matches.append({
                            'symbol': info['symbol'],
                            'company_name': info['company_name'],
                            'sector': info['sector'],
                            'exchange': info['exchange'],
                            'match_type': 'fuzzy_company',
                            'match_score': score * 0.8,  # Slight penalty for company name matches
                            'popularity_score': self._get_popularity_score(info['symbol']),
                            'logo_url': info.get('logo_url'),
                            'market_status': self._get_market_status(info['exchange']),
                            'rank_score': score * 0.8
                        })
        
        # Combine and rank results
        all_matches = exact_matches + fuzzy_matches
        
        # Remove duplicates
        seen_symbols = set()
        unique_matches = []
        for match in all_matches:
            if match['symbol'] not in seen_symbols:
                unique_matches.append(match)
                seen_symbols.add(match['symbol'])
        
        # Advanced ranking algorithm
        ranked_results = self._rank_search_results(unique_matches, query)
        
        return ranked_results[:limit]
    
    def _rank_search_results(self, matches: List[Dict], query: str) -> List[Dict]:
        """Advanced ranking algorithm considering multiple factors"""
        
        def calculate_rank_score(match):
            base_score = match['match_score']
            popularity_score = match['popularity_score']
            
            # Boost exact matches
            if match['match_type'] == 'exact_symbol':
                base_score += 50
            
            # Boost popular stocks
            popularity_boost = min(popularity_score * 0.1, 20)
            
            # Boost if query matches beginning of symbol or company name
            if match['symbol'].startswith(query):
                base_score += 30
            elif match['company_name'].upper().startswith(query):
                base_score += 20
            
            # Sector popularity boost (tech stocks tend to be more searched)
            sector_boost = 0
            if match['sector'] in ['Technology', 'Communication Services', 'Consumer Discretionary']:
                sector_boost = 5
            
            # Final composite score
            final_score = base_score + popularity_boost + sector_boost
            
            return final_score
        
        # Calculate and sort by rank score
        for match in matches:
            match['rank_score'] = calculate_rank_score(match)
        
        return sorted(matches, key=lambda x: x['rank_score'], reverse=True)
    
    def _get_popularity_score(self, symbol: str) -> int:
        """Get popularity score based on search history and market metrics"""
        # Base popularity from search count
        search_count = self.stock_metadata.get(symbol, {}).get('search_count', 0)
        
        # Market cap boost (larger companies are generally more popular)
        market_cap = self.stock_metadata.get(symbol, {}).get('market_cap', 0)
        market_cap_score = 0
        if market_cap:
            if market_cap > 1e12:  # > $1T
                market_cap_score = 50
            elif market_cap > 1e11:  # > $100B
                market_cap_score = 30
            elif market_cap > 1e10:  # > $10B
                market_cap_score = 20
            elif market_cap > 1e9:  # > $1B
                market_cap_score = 10
        
        return search_count + market_cap_score
    
    def _get_market_status(self, exchange: str) -> str:
        """Get current market status for the exchange"""
        # Simplified market status - in production, this would check actual market hours
        from datetime import datetime
        now = datetime.now()
        
        # Basic US market hours check (EST/EDT)
        if exchange in ['NASDAQ', 'NYSE', 'NYSEArca', 'Unknown']:
            hour = now.hour
            weekday = now.weekday()
            
            # Weekend
            if weekday >= 5:
                return 'closed'
            
            # Market hours: 9:30 AM - 4:00 PM EST (simplified)
            if 9 <= hour < 16:
                return 'open'
            elif 4 <= hour < 9:
                return 'pre_market'
            else:
                return 'after_hours'
        
        return 'unknown'
    
    def _record_search_analytics(self, query: str):
        """Record search analytics for improving results"""
        try:
            user_session = session.get('user_id', 'anonymous')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO search_analytics (query, selected_symbol, timestamp, user_session)
                VALUES (?, ?, ?, ?)
            ''', (query, None, datetime.now().isoformat(), user_session))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error recording search analytics: {e}")
    
    def _update_cache_hit_count(self, query: str):
        """Update cache hit count for popular queries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE search_cache 
                SET hit_count = hit_count + 1 
                WHERE query = ?
            ''', (query,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating cache hit count: {e}")
    
    def get_autocomplete_suggestions(self, query: str, limit: int = 8) -> List[Dict]:
        """Get real-time autocomplete suggestions"""
        if len(query.strip()) < 1:
            return self._get_trending_suggestions(limit)
        
        # Use search engine but format for autocomplete
        search_results = self.search_stocks(query, limit)
        
        suggestions = []
        for result in search_results:
            suggestions.append({
                'symbol': result['symbol'],
                'name': result['company_name'],
                'sector': result['sector'],
                'exchange': result['exchange'],
                'match_type': result['match_type'],
                'logo_url': result.get('logo_url'),
                'market_status': result['market_status'],
                'popularity': result['popularity_score']
            })
        
        return suggestions
    
    def _get_trending_suggestions(self, limit: int) -> List[Dict]:
        """Get trending/popular stock suggestions when no query"""
        trending_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'META', 'AMZN', 'NFLX']
        
        suggestions = []
        for symbol in trending_symbols[:limit]:
            if symbol in self.stock_metadata:
                info = self.stock_metadata[symbol]
                suggestions.append({
                    'symbol': symbol,
                    'name': info['company_name'],
                    'sector': info['sector'],
                    'exchange': info['exchange'],
                    'match_type': 'trending',
                    'logo_url': info.get('logo_url'),
                    'market_status': self._get_market_status(info['exchange']),
                    'popularity': self._get_popularity_score(symbol)
                })
        
        return suggestions
    
    def record_selection(self, query: str, selected_symbol: str):
        """Record when a user selects a search result for ML improvement"""
        try:
            # Update search count for the selected symbol
            if selected_symbol in self.stock_metadata:
                self.stock_metadata[selected_symbol]['search_count'] += 1
                
                # Update database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE stock_metadata 
                    SET search_count = search_count + 1 
                    WHERE symbol = ?
                ''', (selected_symbol,))
                conn.commit()
                conn.close()
            
            # Record selection analytics
            user_session = session.get('user_id', 'anonymous')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO search_analytics (query, selected_symbol, timestamp, user_session)
                VALUES (?, ?, ?, ?)
            ''', (query, selected_symbol, datetime.now().isoformat(), user_session))
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded selection: {query} -> {selected_symbol}")
            
        except Exception as e:
            logger.error(f"Error recording selection: {e}")
    
    def get_search_stats(self) -> Dict:
        """Get search engine statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total searches
            cursor.execute('SELECT COUNT(*) FROM search_analytics')
            total_searches = cursor.fetchone()[0]
            
            # Popular queries
            cursor.execute('''
                SELECT query, COUNT(*) as count 
                FROM search_analytics 
                WHERE query IS NOT NULL 
                GROUP BY query 
                ORDER BY count DESC 
                LIMIT 10
            ''')
            popular_queries = cursor.fetchall()
            
            # Popular symbols
            cursor.execute('''
                SELECT selected_symbol, COUNT(*) as count 
                FROM search_analytics 
                WHERE selected_symbol IS NOT NULL 
                GROUP BY selected_symbol 
                ORDER BY count DESC 
                LIMIT 10
            ''')
            popular_symbols = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_searches': total_searches,
                'total_symbols': len(self.stock_metadata),
                'cache_size': len(self.search_cache),
                'popular_queries': popular_queries,
                'popular_symbols': popular_symbols
            }
            
        except Exception as e:
            logger.error(f"Error getting search stats: {e}")
            return {'error': str(e)}

# Global search engine instance
search_engine = None

def get_search_engine():
    """Get or create global search engine instance"""
    global search_engine
    if search_engine is None:
        search_engine = AdvancedSearchEngine()
    return search_engine

# Initialize search engine
search_engine = AdvancedSearchEngine()