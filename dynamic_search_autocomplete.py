"""
Dynamic Search Autocomplete with AI Suggestions
Advanced autocomplete system that provides intelligent stock suggestions with AI-powered insights
"""

import yfinance as yf
import json
from datetime import datetime, timedelta
import re
from typing import List, Dict, Any, Optional
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

class DynamicSearchAutocomplete:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Popular stocks database with additional metadata
        self.popular_stocks = {
            'AAPL': {
                'name': 'Apple Inc.',
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'keywords': ['apple', 'iphone', 'mac', 'technology', 'consumer electronics'],
                'market_cap': 'Large Cap',
                'volatility': 'Low'
            },
            'MSFT': {
                'name': 'Microsoft Corporation',
                'sector': 'Technology',
                'industry': 'Software',
                'keywords': ['microsoft', 'windows', 'office', 'azure', 'cloud', 'software'],
                'market_cap': 'Large Cap',
                'volatility': 'Low'
            },
            'GOOGL': {
                'name': 'Alphabet Inc.',
                'sector': 'Technology',
                'industry': 'Internet Services',
                'keywords': ['google', 'alphabet', 'search', 'advertising', 'youtube', 'cloud'],
                'market_cap': 'Large Cap',
                'volatility': 'Medium'
            },
            'TSLA': {
                'name': 'Tesla Inc.',
                'sector': 'Automotive',
                'industry': 'Electric Vehicles',
                'keywords': ['tesla', 'electric', 'ev', 'musk', 'automotive', 'battery'],
                'market_cap': 'Large Cap',
                'volatility': 'High'
            },
            'NVDA': {
                'name': 'NVIDIA Corporation',
                'sector': 'Technology',
                'industry': 'Semiconductors',
                'keywords': ['nvidia', 'gpu', 'ai', 'gaming', 'semiconductors', 'chips'],
                'market_cap': 'Large Cap',
                'volatility': 'High'
            },
            'AMZN': {
                'name': 'Amazon.com Inc.',
                'sector': 'E-commerce',
                'industry': 'Online Retail',
                'keywords': ['amazon', 'ecommerce', 'aws', 'cloud', 'retail', 'logistics'],
                'market_cap': 'Large Cap',
                'volatility': 'Medium'
            },
            'META': {
                'name': 'Meta Platforms Inc.',
                'sector': 'Technology',
                'industry': 'Social Media',
                'keywords': ['meta', 'facebook', 'instagram', 'social', 'metaverse', 'vr'],
                'market_cap': 'Large Cap',
                'volatility': 'High'
            },
            'NFLX': {
                'name': 'Netflix Inc.',
                'sector': 'Entertainment',
                'industry': 'Streaming',
                'keywords': ['netflix', 'streaming', 'entertainment', 'content', 'media'],
                'market_cap': 'Large Cap',
                'volatility': 'Medium'
            },
            'JPM': {
                'name': 'JPMorgan Chase & Co.',
                'sector': 'Banking',
                'industry': 'Investment Banking',
                'keywords': ['jpmorgan', 'chase', 'banking', 'finance', 'investment'],
                'market_cap': 'Large Cap',
                'volatility': 'Medium'
            },
            'V': {
                'name': 'Visa Inc.',
                'sector': 'Financial Services',
                'industry': 'Payment Processing',
                'keywords': ['visa', 'payments', 'credit', 'financial', 'processing'],
                'market_cap': 'Large Cap',
                'volatility': 'Low'
            },
            'JNJ': {
                'name': 'Johnson & Johnson',
                'sector': 'Healthcare',
                'industry': 'Pharmaceuticals',
                'keywords': ['johnson', 'healthcare', 'pharmaceutical', 'medical', 'drugs'],
                'market_cap': 'Large Cap',
                'volatility': 'Low'
            },
            'WMT': {
                'name': 'Walmart Inc.',
                'sector': 'Retail',
                'industry': 'Discount Stores',
                'keywords': ['walmart', 'retail', 'grocery', 'discount', 'stores'],
                'market_cap': 'Large Cap',
                'volatility': 'Low'
            },
            'DIS': {
                'name': 'The Walt Disney Company',
                'sector': 'Entertainment',
                'industry': 'Media & Entertainment',
                'keywords': ['disney', 'entertainment', 'movies', 'parks', 'streaming'],
                'market_cap': 'Large Cap',
                'volatility': 'Medium'
            },
            'PG': {
                'name': 'Procter & Gamble Co.',
                'sector': 'Consumer Goods',
                'industry': 'Personal Care',
                'keywords': ['procter', 'gamble', 'consumer', 'personal care', 'household'],
                'market_cap': 'Large Cap',
                'volatility': 'Low'
            },
            'KO': {
                'name': 'The Coca-Cola Company',
                'sector': 'Beverages',
                'industry': 'Soft Drinks',
                'keywords': ['coca cola', 'coke', 'beverages', 'drinks', 'consumer'],
                'market_cap': 'Large Cap',
                'volatility': 'Low'
            }
        }
        
        # Trending sectors and themes
        self.trending_themes = {
            'AI': ['NVDA', 'GOOGL', 'MSFT', 'AMZN'],
            'Electric Vehicles': ['TSLA', 'F', 'GM', 'NIO'],
            'Streaming': ['NFLX', 'DIS', 'ROKU', 'SPOT'],
            'Cloud Computing': ['MSFT', 'GOOGL', 'AMZN', 'CRM'],
            'Fintech': ['SQ', 'PYPL', 'V', 'MA'],
            'Healthcare': ['JNJ', 'UNH', 'PFE', 'MRNA'],
            'Renewable Energy': ['ENPH', 'SEDG', 'NEE', 'ICLN']
        }
    
    def get_intelligent_suggestions(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Get intelligent stock suggestions based on user query with AI-powered insights
        """
        suggestions = []
        query_lower = query.lower().strip()
        
        if not query_lower:
            return self._get_popular_suggestions(limit)
        
        # Direct symbol match
        symbol_matches = self._get_symbol_matches(query_lower)
        suggestions.extend(symbol_matches)
        
        # Company name matches
        name_matches = self._get_name_matches(query_lower)
        suggestions.extend(name_matches)
        
        # Keyword and theme matches
        keyword_matches = self._get_keyword_matches(query_lower)
        suggestions.extend(keyword_matches)
        
        # Sector matches
        sector_matches = self._get_sector_matches(query_lower)
        suggestions.extend(sector_matches)
        
        # Remove duplicates while preserving order
        unique_suggestions = []
        seen_symbols = set()
        
        for suggestion in suggestions:
            if suggestion['symbol'] not in seen_symbols:
                unique_suggestions.append(suggestion)
                seen_symbols.add(suggestion['symbol'])
        
        # Enhance suggestions with AI insights
        enhanced_suggestions = self._enhance_with_ai_insights(unique_suggestions[:limit])
        
        return enhanced_suggestions
    
    def _get_symbol_matches(self, query: str) -> List[Dict[str, Any]]:
        """Get matches based on stock symbol"""
        matches = []
        
        for symbol, data in self.popular_stocks.items():
            if symbol.lower().startswith(query):
                matches.append({
                    'symbol': symbol,
                    'name': data['name'],
                    'sector': data['sector'],
                    'industry': data['industry'],
                    'market_cap': data['market_cap'],
                    'volatility': data['volatility'],
                    'match_type': 'symbol',
                    'confidence': 95
                })
        
        return matches
    
    def _get_name_matches(self, query: str) -> List[Dict[str, Any]]:
        """Get matches based on company name"""
        matches = []
        
        for symbol, data in self.popular_stocks.items():
            name_lower = data['name'].lower()
            if query in name_lower or any(word in name_lower for word in query.split()):
                confidence = 85 if query in name_lower else 70
                matches.append({
                    'symbol': symbol,
                    'name': data['name'],
                    'sector': data['sector'],
                    'industry': data['industry'],
                    'market_cap': data['market_cap'],
                    'volatility': data['volatility'],
                    'match_type': 'name',
                    'confidence': confidence
                })
        
        return matches
    
    def _get_keyword_matches(self, query: str) -> List[Dict[str, Any]]:
        """Get matches based on keywords and themes"""
        matches = []
        
        for symbol, data in self.popular_stocks.items():
            for keyword in data['keywords']:
                if query in keyword or keyword in query:
                    confidence = 75 if query == keyword else 60
                    matches.append({
                        'symbol': symbol,
                        'name': data['name'],
                        'sector': data['sector'],
                        'industry': data['industry'],
                        'market_cap': data['market_cap'],
                        'volatility': data['volatility'],
                        'match_type': 'keyword',
                        'confidence': confidence,
                        'matched_keyword': keyword
                    })
                    break
        
        return matches
    
    def _get_sector_matches(self, query: str) -> List[Dict[str, Any]]:
        """Get matches based on sector"""
        matches = []
        
        for symbol, data in self.popular_stocks.items():
            if query in data['sector'].lower() or query in data['industry'].lower():
                confidence = 65 if query in data['sector'].lower() else 55
                matches.append({
                    'symbol': symbol,
                    'name': data['name'],
                    'sector': data['sector'],
                    'industry': data['industry'],
                    'market_cap': data['market_cap'],
                    'volatility': data['volatility'],
                    'match_type': 'sector',
                    'confidence': confidence
                })
        
        return matches
    
    def _get_popular_suggestions(self, limit: int) -> List[Dict[str, Any]]:
        """Get popular stock suggestions when no query provided"""
        suggestions = []
        
        popular_order = ['AAPL', 'TSLA', 'NVDA', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NFLX']
        
        for symbol in popular_order[:limit]:
            if symbol in self.popular_stocks:
                data = self.popular_stocks[symbol]
                suggestions.append({
                    'symbol': symbol,
                    'name': data['name'],
                    'sector': data['sector'],
                    'industry': data['industry'],
                    'market_cap': data['market_cap'],
                    'volatility': data['volatility'],
                    'match_type': 'popular',
                    'confidence': 90
                })
        
        return suggestions
    
    def _enhance_with_ai_insights(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance suggestions with AI-powered insights"""
        enhanced = []
        
        for suggestion in suggestions:
            try:
                # Get real-time price data
                stock_data = self._get_stock_data(suggestion['symbol'])
                
                if stock_data:
                    suggestion.update({
                        'current_price': stock_data.get('current_price', 0),
                        'price_change': stock_data.get('price_change', 0),
                        'price_change_percent': stock_data.get('price_change_percent', 0),
                        'volume': stock_data.get('volume', 0),
                        'ai_sentiment': self._generate_ai_sentiment(stock_data),
                        'trending_score': self._calculate_trending_score(stock_data),
                        'suggestion_reason': self._generate_suggestion_reason(suggestion, stock_data)
                    })
                
                enhanced.append(suggestion)
                
            except Exception as e:
                self.logger.error(f"Error enhancing suggestion for {suggestion['symbol']}: {e}")
                enhanced.append(suggestion)
        
        # Sort by confidence and trending score
        enhanced.sort(key=lambda x: (x.get('confidence', 0) + x.get('trending_score', 0)), reverse=True)
        
        return enhanced
    
    def _get_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time stock data"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="2d")
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            
            price_change = current_price - previous_close
            price_change_percent = (price_change / previous_close) * 100 if previous_close != 0 else 0
            
            return {
                'current_price': float(current_price),
                'previous_close': float(previous_close),
                'price_change': float(price_change),
                'price_change_percent': float(price_change_percent),
                'volume': int(hist['Volume'].iloc[-1]) if not hist['Volume'].empty else 0,
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('forwardPE', 0),
                'beta': info.get('beta', 1.0)
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching stock data for {symbol}: {e}")
            return None
    
    def _generate_ai_sentiment(self, stock_data: Dict[str, Any]) -> str:
        """Generate AI sentiment based on stock data"""
        price_change_percent = stock_data.get('price_change_percent', 0)
        
        if price_change_percent > 3:
            return 'Very Bullish'
        elif price_change_percent > 1:
            return 'Bullish'
        elif price_change_percent > -1:
            return 'Neutral'
        elif price_change_percent > -3:
            return 'Bearish'
        else:
            return 'Very Bearish'
    
    def _calculate_trending_score(self, stock_data: Dict[str, Any]) -> int:
        """Calculate trending score based on various factors"""
        score = 0
        
        # Price momentum
        price_change_percent = abs(stock_data.get('price_change_percent', 0))
        if price_change_percent > 5:
            score += 30
        elif price_change_percent > 2:
            score += 20
        elif price_change_percent > 1:
            score += 10
        
        # Volume factor
        volume = stock_data.get('volume', 0)
        if volume > 50000000:  # High volume
            score += 20
        elif volume > 20000000:  # Medium volume
            score += 10
        
        # Volatility (beta)
        beta = stock_data.get('beta', 1.0)
        if beta > 1.5:
            score += 15
        elif beta > 1.2:
            score += 10
        
        return min(score, 100)
    
    def _generate_suggestion_reason(self, suggestion: Dict[str, Any], stock_data: Dict[str, Any]) -> str:
        """Generate reason for suggestion"""
        match_type = suggestion.get('match_type', 'popular')
        price_change_percent = stock_data.get('price_change_percent', 0)
        
        if match_type == 'symbol':
            reason = f"Direct symbol match"
        elif match_type == 'name':
            reason = f"Company name match"
        elif match_type == 'keyword':
            keyword = suggestion.get('matched_keyword', '')
            reason = f"Related to '{keyword}'"
        elif match_type == 'sector':
            reason = f"In {suggestion['sector']} sector"
        else:
            reason = f"Popular stock"
        
        # Add price movement context
        if price_change_percent > 2:
            reason += f" • Up {price_change_percent:.1f}% today"
        elif price_change_percent < -2:
            reason += f" • Down {abs(price_change_percent):.1f}% today"
        
        return reason
    
    def get_themed_suggestions(self, theme: str) -> List[Dict[str, Any]]:
        """Get suggestions based on investment themes"""
        if theme not in self.trending_themes:
            return []
        
        symbols = self.trending_themes[theme]
        suggestions = []
        
        for symbol in symbols:
            if symbol in self.popular_stocks:
                data = self.popular_stocks[symbol]
                suggestions.append({
                    'symbol': symbol,
                    'name': data['name'],
                    'sector': data['sector'],
                    'industry': data['industry'],
                    'market_cap': data['market_cap'],
                    'volatility': data['volatility'],
                    'match_type': 'theme',
                    'confidence': 80,
                    'theme': theme
                })
        
        return self._enhance_with_ai_insights(suggestions)
    
    def search_external_stocks(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for stocks not in popular database using external APIs"""
        try:
            # This would integrate with external stock APIs for broader search
            # For now, we'll implement a basic yfinance search
            
            # Try to fetch the stock directly
            try:
                ticker = yf.Ticker(query.upper())
                info = ticker.info
                
                if info and info.get('symbol'):
                    stock_data = self._get_stock_data(query.upper())
                    
                    return [{
                        'symbol': query.upper(),
                        'name': info.get('longName', 'Unknown Company'),
                        'sector': info.get('sector', 'Unknown'),
                        'industry': info.get('industry', 'Unknown'),
                        'market_cap': 'Unknown',
                        'volatility': 'Unknown',
                        'match_type': 'external',
                        'confidence': 60,
                        'current_price': stock_data.get('current_price', 0) if stock_data else 0,
                        'price_change_percent': stock_data.get('price_change_percent', 0) if stock_data else 0,
                        'suggestion_reason': f"External stock search result"
                    }]
                    
            except Exception as e:
                self.logger.error(f"Error searching external stock {query}: {e}")
                
        except Exception as e:
            self.logger.error(f"Error in external stock search: {e}")
        
        return []

# Global instance
autocomplete_engine = DynamicSearchAutocomplete()