"""
Enhanced Search Autocomplete System
Provides real-time typeahead, recent searches, starred symbols, and AI-powered ranking
"""

import json
import logging
from datetime import datetime, timedelta
from flask import session, request
from flask_login import current_user
from models import db, User
from ai_insights import AIInsightsEngine
import yfinance as yf
from functools import lru_cache
import re

logger = logging.getLogger(__name__)

class EnhancedSearchAutocomplete:
    def __init__(self):
        self.ai_engine = AIInsightsEngine()
        
        # Popular stocks database for fast lookups
        self.popular_stocks = {
            'AAPL': {'name': 'Apple Inc.', 'sector': 'Technology', 'tags': ['tech', 'consumer', 'iPhone']},
            'MSFT': {'name': 'Microsoft Corporation', 'sector': 'Technology', 'tags': ['tech', 'cloud', 'software']},
            'GOOGL': {'name': 'Alphabet Inc.', 'sector': 'Technology', 'tags': ['tech', 'search', 'advertising']},
            'AMZN': {'name': 'Amazon.com Inc.', 'sector': 'Consumer Discretionary', 'tags': ['e-commerce', 'cloud', 'aws']},
            'TSLA': {'name': 'Tesla Inc.', 'sector': 'Consumer Discretionary', 'tags': ['ev', 'automotive', 'energy']},
            'NVDA': {'name': 'NVIDIA Corporation', 'sector': 'Technology', 'tags': ['semiconductor', 'ai', 'gaming']},
            'META': {'name': 'Meta Platforms Inc.', 'sector': 'Technology', 'tags': ['social', 'metaverse', 'advertising']},
            'NFLX': {'name': 'Netflix Inc.', 'sector': 'Communication Services', 'tags': ['streaming', 'entertainment']},
            'AMD': {'name': 'Advanced Micro Devices', 'sector': 'Technology', 'tags': ['semiconductor', 'cpu', 'gpu']},
            'CRM': {'name': 'Salesforce Inc.', 'sector': 'Technology', 'tags': ['saas', 'crm', 'cloud']},
            'PLTR': {'name': 'Palantir Technologies', 'sector': 'Technology', 'tags': ['data', 'analytics', 'defense']},
            'SNOW': {'name': 'Snowflake Inc.', 'sector': 'Technology', 'tags': ['cloud', 'data', 'warehouse']},
            'COIN': {'name': 'Coinbase Global Inc.', 'sector': 'Financial Services', 'tags': ['crypto', 'exchange']},
            'PYPL': {'name': 'PayPal Holdings Inc.', 'sector': 'Financial Services', 'tags': ['payments', 'fintech']},
            'UBER': {'name': 'Uber Technologies Inc.', 'sector': 'Technology', 'tags': ['rideshare', 'mobility']},
            'RIVN': {'name': 'Rivian Automotive Inc.', 'sector': 'Consumer Discretionary', 'tags': ['ev', 'automotive']},
            'LCID': {'name': 'Lucid Group Inc.', 'sector': 'Consumer Discretionary', 'tags': ['ev', 'luxury']},
            'F': {'name': 'Ford Motor Company', 'sector': 'Consumer Discretionary', 'tags': ['automotive', 'legacy']},
            'GM': {'name': 'General Motors Company', 'sector': 'Consumer Discretionary', 'tags': ['automotive', 'legacy']},
            'BA': {'name': 'Boeing Company', 'sector': 'Industrials', 'tags': ['aerospace', 'defense']},
            'JPM': {'name': 'JPMorgan Chase & Co.', 'sector': 'Financial Services', 'tags': ['banking', 'finance']},
            'V': {'name': 'Visa Inc.', 'sector': 'Financial Services', 'tags': ['payments', 'credit']},
            'MA': {'name': 'Mastercard Incorporated', 'sector': 'Financial Services', 'tags': ['payments', 'credit']},
            'DIS': {'name': 'Walt Disney Company', 'sector': 'Communication Services', 'tags': ['entertainment', 'streaming']},
            'MRNA': {'name': 'Moderna Inc.', 'sector': 'Healthcare', 'tags': ['biotech', 'vaccine', 'mrna']}
        }
        
        # Sector mappings
        self.sectors = {
            'Technology': ['tech', 'software', 'hardware', 'semiconductors', 'cloud'],
            'Healthcare': ['biotech', 'pharma', 'medical', 'healthcare'],
            'Financial Services': ['banking', 'fintech', 'payments', 'insurance'],
            'Consumer Discretionary': ['retail', 'automotive', 'entertainment'],
            'Consumer Staples': ['food', 'beverages', 'household'],
            'Energy': ['oil', 'gas', 'renewable', 'solar'],
            'Industrials': ['aerospace', 'defense', 'manufacturing'],
            'Communication Services': ['telecom', 'media', 'social'],
            'Utilities': ['electric', 'water', 'gas'],
            'Real Estate': ['reit', 'property', 'commercial'],
            'Materials': ['chemicals', 'metals', 'mining']
        }

    def get_autocomplete_suggestions(self, query, limit=8):
        """Get autocomplete suggestions with personalization and AI ranking"""
        try:
            query = query.strip().upper()
            if len(query) < 1:
                return self._get_default_suggestions(limit)
            
            suggestions = []
            
            # 1. Recent searches (personalized)
            recent_suggestions = self._get_recent_searches(query, limit//4)
            suggestions.extend(recent_suggestions)
            
            # 2. Starred symbols (favorites)
            starred_suggestions = self._get_starred_symbols(query, limit//4)
            suggestions.extend(starred_suggestions)
            
            # 3. Symbol and company name matches
            symbol_matches = self._get_symbol_matches(query, limit//2)
            suggestions.extend(symbol_matches)
            
            # 4. Sector and tag matches
            sector_matches = self._get_sector_matches(query, limit//4)
            suggestions.extend(sector_matches)
            
            # Remove duplicates and apply AI ranking
            unique_suggestions = self._deduplicate_suggestions(suggestions)
            ranked_suggestions = self._apply_ai_ranking(unique_suggestions, query)
            
            return ranked_suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Autocomplete error: {e}")
            return self._get_fallback_suggestions(query, limit)

    def _get_recent_searches(self, query, limit):
        """Get recent searches matching query"""
        recent_searches = session.get('recent_searches', [])
        matches = []
        
        for search in recent_searches:
            symbol = search.get('symbol', '').upper()
            name = search.get('name', '').upper()
            
            if query in symbol or query in name:
                matches.append({
                    'symbol': symbol,
                    'name': search.get('name', ''),
                    'sector': search.get('sector', ''),
                    'type': 'recent',
                    'priority': 10,  # High priority for recent searches
                    'timestamp': search.get('timestamp', '')
                })
        
        return matches[:limit]

    def _get_starred_symbols(self, query, limit):
        """Get starred/favorite symbols matching query"""
        starred_symbols = session.get('starred_symbols', [])
        matches = []
        
        for symbol in starred_symbols:
            symbol_upper = symbol.upper()
            stock_info = self.popular_stocks.get(symbol_upper, {})
            name = stock_info.get('name', '').upper()
            
            if query in symbol_upper or query in name:
                matches.append({
                    'symbol': symbol_upper,
                    'name': stock_info.get('name', symbol_upper),
                    'sector': stock_info.get('sector', ''),
                    'type': 'starred',
                    'priority': 9,  # High priority for starred symbols
                    'star': True
                })
        
        return matches[:limit]

    def _get_symbol_matches(self, query, limit):
        """Get symbol and company name matches"""
        matches = []
        
        for symbol, info in self.popular_stocks.items():
            symbol_match = query in symbol
            name_match = query in info['name'].upper()
            
            if symbol_match or name_match:
                priority = 8 if symbol_match else 6  # Symbol matches get higher priority
                
                matches.append({
                    'symbol': symbol,
                    'name': info['name'],
                    'sector': info['sector'],
                    'type': 'symbol',
                    'priority': priority,
                    'tags': info.get('tags', [])
                })
        
        return sorted(matches, key=lambda x: x['priority'], reverse=True)[:limit]

    def _get_sector_matches(self, query, limit):
        """Get matches based on sector and tags"""
        matches = []
        
        # Search by sector name
        for sector, tags in self.sectors.items():
            if query in sector.upper() or any(query in tag.upper() for tag in tags):
                # Find stocks in this sector
                sector_stocks = [(symbol, info) for symbol, info in self.popular_stocks.items() 
                               if info['sector'] == sector]
                
                for symbol, info in sector_stocks[:2]:  # Limit per sector
                    matches.append({
                        'symbol': symbol,
                        'name': info['name'],
                        'sector': info['sector'],
                        'type': 'sector',
                        'priority': 5,
                        'matched_sector': sector
                    })
        
        return matches[:limit]

    def _apply_ai_ranking(self, suggestions, query):
        """Apply AI-powered ranking to suggestions"""
        try:
            # Get AI insights for ranking
            for suggestion in suggestions:
                try:
                    # Add AI relevance score
                    suggestion['ai_score'] = self._calculate_relevance_score(suggestion, query)
                    
                    # Add market momentum (if available)
                    suggestion['momentum'] = self._get_market_momentum(suggestion['symbol'])
                    
                except Exception as e:
                    logger.debug(f"AI ranking error for {suggestion['symbol']}: {e}")
                    suggestion['ai_score'] = suggestion.get('priority', 5)
                    suggestion['momentum'] = 'neutral'
            
            # Sort by combined priority and AI score
            return sorted(suggestions, 
                         key=lambda x: (x.get('priority', 0) + x.get('ai_score', 0)), 
                         reverse=True)
            
        except Exception as e:
            logger.error(f"AI ranking error: {e}")
            return sorted(suggestions, key=lambda x: x.get('priority', 0), reverse=True)

    def _calculate_relevance_score(self, suggestion, query):
        """Calculate AI relevance score for suggestion"""
        score = 0
        
        # Exact symbol match gets highest score
        if query == suggestion['symbol']:
            score += 10
        elif query in suggestion['symbol']:
            score += 7
        
        # Company name match
        if query in suggestion['name'].upper():
            score += 5
        
        # Sector relevance
        if suggestion.get('matched_sector'):
            score += 3
        
        # Tag relevance
        if suggestion.get('tags'):
            tag_matches = [tag for tag in suggestion['tags'] if query.lower() in tag]
            score += len(tag_matches) * 2
        
        return score

    @lru_cache(maxsize=100)
    def _get_market_momentum(self, symbol):
        """Get market momentum indicator (cached)"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='5d')
            
            if len(data) >= 2:
                recent_change = (data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]
                
                if recent_change > 0.02:
                    return 'strong_up'
                elif recent_change > 0:
                    return 'up'
                elif recent_change < -0.02:
                    return 'strong_down'
                elif recent_change < 0:
                    return 'down'
            
            return 'neutral'
            
        except Exception:
            return 'neutral'

    def _deduplicate_suggestions(self, suggestions):
        """Remove duplicate suggestions"""
        seen = set()
        unique = []
        
        for suggestion in suggestions:
            symbol = suggestion['symbol']
            if symbol not in seen:
                seen.add(symbol)
                unique.append(suggestion)
        
        return unique

    def _get_default_suggestions(self, limit):
        """Get default suggestions when no query"""
        # Return a mix of popular stocks and recent searches
        recent = self._get_recent_searches('', limit//2)
        starred = self._get_starred_symbols('', limit//4)
        
        # Add popular stocks
        popular = []
        for symbol in ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']:
            info = self.popular_stocks[symbol]
            popular.append({
                'symbol': symbol,
                'name': info['name'],
                'sector': info['sector'],
                'type': 'popular',
                'priority': 7
            })
        
        all_suggestions = recent + starred + popular
        unique = self._deduplicate_suggestions(all_suggestions)
        return unique[:limit]

    def _get_fallback_suggestions(self, query, limit):
        """Fallback suggestions when main logic fails"""
        fallback = []
        
        # Simple string matching on popular stocks
        for symbol, info in list(self.popular_stocks.items())[:limit]:
            if not query or query in symbol or query.lower() in info['name'].lower():
                fallback.append({
                    'symbol': symbol,
                    'name': info['name'],
                    'sector': info['sector'],
                    'type': 'fallback',
                    'priority': 3
                })
        
        return fallback[:limit]

    def add_to_recent_searches(self, symbol, name, sector):
        """Add search to recent searches"""
        recent_searches = session.get('recent_searches', [])
        
        # Remove if already exists
        recent_searches = [s for s in recent_searches if s.get('symbol') != symbol]
        
        # Add to front
        recent_searches.insert(0, {
            'symbol': symbol,
            'name': name,
            'sector': sector,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10
        session['recent_searches'] = recent_searches[:10]

    def toggle_starred_symbol(self, symbol):
        """Toggle starred status of a symbol"""
        starred_symbols = session.get('starred_symbols', [])
        
        if symbol in starred_symbols:
            starred_symbols.remove(symbol)
            action = 'removed'
        else:
            starred_symbols.append(symbol)
            action = 'added'
        
        session['starred_symbols'] = starred_symbols
        return action

    def get_starred_symbols(self):
        """Get list of starred symbols with full info"""
        starred_symbols = session.get('starred_symbols', [])
        starred_info = []
        
        for symbol in starred_symbols:
            info = self.popular_stocks.get(symbol, {})
            starred_info.append({
                'symbol': symbol,
                'name': info.get('name', symbol),
                'sector': info.get('sector', ''),
                'tags': info.get('tags', [])
            })
        
        return starred_info

# Global instance
enhanced_search_autocomplete = EnhancedSearchAutocomplete()