"""
Advanced Search Engine with Fuzzy Matching and Caching
Provides intelligent stock/company search with autocomplete capabilities
"""

import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from rapidfuzz import fuzz, process
import yfinance as yf
import logging
import threading

# Simple cache implementation since cache_optimizer might not be available
class SimpleCache:
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
    
    def get(self, key):
        with self._lock:
            return self._cache.get(key)
    
    def set(self, key, value, timeout=None):
        with self._lock:
            self._cache[key] = value
    
    def delete(self, key):
        with self._lock:
            self._cache.pop(key, None)

# Try to import the real cache, fall back to simple cache
try:
    from cache_optimizer import search_cache
except ImportError:
    search_cache = SimpleCache()

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    symbol: str
    company_name: str
    sector: str
    market_cap: Optional[float]
    logo_url: Optional[str]
    exchange: str
    confidence_score: float
    search_frequency: int = 0

class AdvancedSearchEngine:
    def __init__(self):
        self.companies_data = {}
        self.search_frequencies = {}
        self.last_update = 0
        self.update_interval = 24 * 3600  # 24 hours
        self.lock = threading.Lock()
        self.initialized = False
        
    def initialize(self):
        """Initialize the search engine with company data"""
        if self.initialized:
            return
            
        try:
            self._load_companies_data()
            self._load_search_frequencies()
            self.initialized = True
            logger.info("Advanced Search Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Advanced Search Engine: {e}")
            
    def _load_companies_data(self):
        """Load companies data from cache or fetch from API"""
        cached_data = search_cache.get('companies_metadata')
        
        if cached_data and time.time() - cached_data.get('timestamp', 0) < self.update_interval:
            self.companies_data = cached_data['data']
            logger.info(f"Loaded {len(self.companies_data)} companies from cache")
            return
            
        # Fetch fresh data
        self._fetch_companies_data()
        
    def _fetch_companies_data(self):
        """Fetch companies data from multiple sources"""
        logger.info("Fetching fresh companies data...")
        
        # Core S&P 500 and popular stocks
        popular_symbols = [
            # Tech Giants
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX', 'CRM',
            # Financial
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BRK.A', 'BRK.B', 'V', 'MA',
            # Healthcare
            'JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'DHR', 'ABT', 'CVS', 'MRK', 'LLY',
            # Consumer
            'PG', 'KO', 'PEP', 'WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'COST',
            # Industrial
            'BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'LMT', 'RTX', 'DE', 'EMR',
            # Energy
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'VLO', 'PSX', 'KMI', 'OKE',
            # Crypto/Fintech
            'COIN', 'PYPL', 'SQ', 'HOOD', 'SOFI', 'AFRM', 'UPST',
            # EV/Clean Energy
            'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'PLUG', 'FCEL', 'ENPH', 'SEDG',
            # Meme/Popular
            'GME', 'AMC', 'BB', 'NOK', 'PLTR', 'WISH', 'CLOV', 'SPCE',
            # Biotech
            'MRNA', 'BNTX', 'GILD', 'REGN', 'VRTX', 'BIIB', 'ILMN', 'AMGN',
            # Semiconductors
            'AMD', 'INTC', 'QCOM', 'AVGO', 'MU', 'AMAT', 'LRCX', 'KLAC', 'MRVL',
            # Streaming/Media
            'DIS', 'CMCSA', 'T', 'VZ', 'CHTR', 'FOXA', 'PARA', 'WBD',
            # REITs
            'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'EXR', 'AVB', 'EQR',
            # Utilities
            'NEE', 'DUK', 'SO', 'AEP', 'EXC', 'XEL', 'ED', 'ETR'
        ]
        
        companies_data = {}
        
        for symbol in popular_symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info and info.get('longName'):
                    companies_data[symbol] = {
                        'symbol': symbol,
                        'company_name': info.get('longName', ''),
                        'short_name': info.get('shortName', ''),
                        'sector': info.get('sector', 'Unknown'),
                        'industry': info.get('industry', 'Unknown'),
                        'market_cap': info.get('marketCap'),
                        'exchange': info.get('exchange', 'NASDAQ'),
                        'logo_url': f"https://logo.clearbit.com/{info.get('website', '').replace('https://', '').replace('http://', '').split('/')[0]}" if info.get('website') else None,
                        'website': info.get('website'),
                        'employees': info.get('fullTimeEmployees'),
                        'country': info.get('country', 'US')
                    }
                    
            except Exception as e:
                logger.warning(f"Failed to fetch data for {symbol}: {e}")
                # Add basic fallback data
                companies_data[symbol] = {
                    'symbol': symbol,
                    'company_name': symbol,
                    'short_name': symbol,
                    'sector': 'Unknown',
                    'industry': 'Unknown',
                    'market_cap': None,
                    'exchange': 'NASDAQ',
                    'logo_url': None,
                    'website': None,
                    'employees': None,
                    'country': 'US'
                }
        
        self.companies_data = companies_data
        
        # Cache the data
        search_cache.set('companies_metadata', {
            'data': companies_data,
            'timestamp': time.time()
        }, timeout=self.update_interval)
        
        logger.info(f"Fetched and cached {len(companies_data)} companies")
        
    def _load_search_frequencies(self):
        """Load search frequency data from cache"""
        cached_frequencies = search_cache.get('search_frequencies')
        if cached_frequencies:
            self.search_frequencies = cached_frequencies
        else:
            self.search_frequencies = {}
            
    def _save_search_frequencies(self):
        """Save search frequency data to cache"""
        search_cache.set('search_frequencies', self.search_frequencies, timeout=7*24*3600)  # 1 week
        
    def search(self, query: str, limit: int = 8) -> List[SearchResult]:
        """
        Search for companies using fuzzy matching
        
        Args:
            query: Search query (symbol or company name)
            limit: Maximum number of results to return
            
        Returns:
            List of SearchResult objects sorted by relevance
        """
        if not self.initialized:
            self.initialize()
            
        if not query or len(query.strip()) < 1:
            return []
            
        query = query.strip().upper()
        
        # Record search frequency
        self._record_search(query)
        
        # Check cache first
        cache_key = f"search_results_{query}_{limit}"
        cached_results = search_cache.get(cache_key)
        if cached_results:
            return [SearchResult(**result) for result in cached_results]
        
        results = []
        
        # 1. Exact symbol match (highest priority)
        if query in self.companies_data:
            company = self.companies_data[query]
            results.append(self._create_search_result(company, 100.0))
        
        # 2. Fuzzy symbol matching
        symbol_matches = process.extract(
            query, 
            self.companies_data.keys(), 
            scorer=fuzz.ratio,
            limit=limit * 2
        )
        
        for match in symbol_matches:
            symbol, score = match[0], match[1]
            if score >= 70 and symbol not in [r.symbol for r in results]:
                company = self.companies_data[symbol]
                confidence = min(score, 95.0)  # Cap at 95 for fuzzy matches
                results.append(self._create_search_result(company, confidence))
        
        # 3. Company name fuzzy matching
        company_names = {data['company_name']: data['symbol'] 
                        for data in self.companies_data.values() 
                        if data['company_name']}
        
        name_matches = process.extract(
            query,
            company_names.keys(),
            scorer=fuzz.partial_ratio,
            limit=limit * 2
        )
        
        for match in name_matches:
            company_name, score = match[0], match[1]
            if score >= 60:
                symbol = company_names[company_name]
                if symbol not in [r.symbol for r in results]:
                    company = self.companies_data[symbol]
                    confidence = min(score * 0.9, 90.0)  # Slightly lower for name matches
                    results.append(self._create_search_result(company, confidence))
        
        # 4. Short name matching
        short_names = {data['short_name']: data['symbol'] 
                      for data in self.companies_data.values() 
                      if data.get('short_name')}
        
        short_name_matches = process.extract(
            query,
            short_names.keys(),
            scorer=fuzz.ratio,
            limit=limit
        )
        
        for match in short_name_matches:
            short_name, score = match[0], match[1]
            if score >= 70:
                symbol = short_names[short_name]
                if symbol not in [r.symbol for r in results]:
                    company = self.companies_data[symbol]
                    confidence = min(score * 0.8, 85.0)
                    results.append(self._create_search_result(company, confidence))
        
        # Sort by confidence score and search frequency
        results.sort(key=lambda x: (x.confidence_score, x.search_frequency), reverse=True)
        
        # Limit results
        results = results[:limit]
        
        # Cache results for 5 minutes
        search_cache.set(cache_key, [result.__dict__ for result in results], timeout=300)
        
        return results
    
    def _create_search_result(self, company_data: Dict, confidence: float) -> SearchResult:
        """Create a SearchResult object from company data"""
        symbol = company_data['symbol']
        search_freq = self.search_frequencies.get(symbol, 0)
        
        return SearchResult(
            symbol=symbol,
            company_name=company_data['company_name'],
            sector=company_data['sector'],
            market_cap=company_data.get('market_cap'),
            logo_url=company_data.get('logo_url'),
            exchange=company_data['exchange'],
            confidence_score=confidence,
            search_frequency=search_freq
        )
    
    def _record_search(self, query: str):
        """Record search frequency for analytics"""
        with self.lock:
            # Record query frequency
            if query in self.search_frequencies:
                self.search_frequencies[query] += 1
            else:
                self.search_frequencies[query] = 1
            
            # Also record if it's a direct symbol match
            if query in self.companies_data:
                if query in self.search_frequencies:
                    self.search_frequencies[query] += 1
                else:
                    self.search_frequencies[query] = 1
            
            # Periodically save to cache
            if len(self.search_frequencies) % 10 == 0:
                self._save_search_frequencies()
    
    def get_popular_stocks(self, limit: int = 10) -> List[SearchResult]:
        """Get most frequently searched stocks"""
        if not self.initialized:
            self.initialize()
            
        # Sort by search frequency
        popular = sorted(
            self.search_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        results = []
        for symbol, freq in popular:
            if symbol in self.companies_data:
                company = self.companies_data[symbol]
                result = self._create_search_result(company, 100.0)
                results.append(result)
        
        return results
    
    def get_sector_suggestions(self, sector: str, limit: int = 5) -> List[SearchResult]:
        """Get stock suggestions from a specific sector"""
        if not self.initialized:
            self.initialize()
            
        sector_stocks = [
            data for data in self.companies_data.values()
            if data['sector'].lower() == sector.lower()
        ]
        
        results = []
        for company in sector_stocks[:limit]:
            result = self._create_search_result(company, 90.0)
            results.append(result)
        
        return results
    
    def refresh_data(self):
        """Force refresh of companies data"""
        logger.info("Forcing refresh of companies data...")
        search_cache.delete('companies_metadata')
        self._fetch_companies_data()

# Global search engine instance
advanced_search_engine = AdvancedSearchEngine()