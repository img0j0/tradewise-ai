"""
Premium Search Engine for TradeWise AI
Implements advanced search capabilities with AI-powered insights for $10/month subscribers
"""

import yfinance as yf
import logging
from datetime import datetime, timedelta
import numpy as np
from textblob import TextBlob

logger = logging.getLogger(__name__)

class PremiumSearchEngine:
    """Advanced search engine with institutional-grade features for premium users"""
    
    def __init__(self):
        self.logger = logger
    
    def check_premium_access(self):
        """Check if user has premium subscription - for demo, returns False (free tier)"""
        # In production, this would check the user's subscription status
        return False
    
    def enhanced_search(self, query, sector='', market_cap='', sort_by='relevance', limit=10):
        """Main enhanced search function with premium/free tier distinction"""
        is_premium = self.check_premium_access()
        
        if is_premium:
            return self._premium_search(query, sector, market_cap, sort_by, limit)
        else:
            return self._free_tier_search(query, sector, market_cap, sort_by, min(limit, 5))
    
    def _premium_search(self, query, sector, market_cap, sort_by, limit):
        """Premium search with advanced AI insights, institutional data, and unlimited results"""
        results = []
        symbols = self._get_relevant_symbols(query, sector, market_cap, limit * 2)
        
        for symbol in symbols[:limit]:
            try:
                stock_data = self._get_premium_stock_data(symbol)
                if stock_data:
                    # Add AI-powered premium features
                    stock_data['ai_sentiment_score'] = self._calculate_ai_sentiment(symbol)
                    stock_data['analyst_consensus'] = self._get_analyst_consensus(symbol)
                    stock_data['risk_assessment'] = self._calculate_risk_score(stock_data)
                    stock_data['momentum_indicators'] = self._calculate_momentum(symbol)
                    stock_data['earnings_forecast'] = self._get_earnings_forecast(symbol)
                    stock_data['institutional_activity'] = self._get_institutional_data(symbol)
                    stock_data['ai_relevance_score'] = self._calculate_ai_relevance(query, stock_data)
                    
                    # Premium: Advanced filtering and scoring
                    stock_data['premium_features'] = {
                        'ai_driven': True,
                        'real_time_sentiment': True,
                        'institutional_data': True,
                        'advanced_metrics': True
                    }
                    
                    results.append(stock_data)
                    
            except Exception as e:
                self.logger.warning(f"Error fetching premium data for {symbol}: {e}")
        
        # Premium: AI-powered intelligent sorting
        return self._sort_premium_results(results, sort_by, query)
    
    def _free_tier_search(self, query, sector, market_cap, sort_by, limit):
        """Free tier search with basic functionality and upgrade prompts"""
        results = []
        symbols = self._get_relevant_symbols(query, sector, market_cap, limit)
        
        for symbol in symbols:
            try:
                stock_data = self._get_basic_stock_data(symbol)
                if stock_data:
                    stock_data['basic_relevance_score'] = self._calculate_basic_relevance(query, stock_data)
                    stock_data['premium_locked'] = True
                    stock_data['upgrade_message'] = "Upgrade to AI Trading Copilot for advanced insights"
                    
                    # Limited free features
                    stock_data['free_features'] = {
                        'basic_pricing': True,
                        'sector_info': True,
                        'limited_results': True
                    }
                    
                    results.append(stock_data)
                    
            except Exception as e:
                self.logger.warning(f"Error fetching basic data for {symbol}: {e}")
        
        # Basic sorting for free tier
        return self._sort_basic_results(results, sort_by)
    
    def _get_premium_stock_data(self, symbol):
        """Get comprehensive stock data with premium features"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="30d")  # Premium: 30-day history
            
            if not info or hist.empty:
                return None
            
            current_price = info.get('currentPrice') or hist['Close'].iloc[-1]
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'current_price': float(current_price),
                'price_change': float(info.get('regularMarketChange', 0)),
                'price_change_pct': float(info.get('regularMarketChangePercent', 0)),
                'volume': int(info.get('volume', 0)),
                'avg_volume': int(info.get('averageVolume', 0)),
                'market_cap': self._format_market_cap(info.get('marketCap', 0)),
                'market_cap_value': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'dividend_yield': info.get('dividendYield'),
                'beta': info.get('beta'),
                'revenue_growth': info.get('revenueGrowth'),
                'profit_margins': info.get('profitMargins'),
                'debt_to_equity': info.get('debtToEquity'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                'analyst_target_price': info.get('targetMeanPrice'),
                'recommendation': info.get('recommendationKey'),
                'historical_volatility': self._calculate_volatility(hist),
                'premium_tier': True
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching premium data for {symbol}: {e}")
            return None
    
    def _get_basic_stock_data(self, symbol):
        """Get basic stock data for free tier"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d")  # Free: 1-day history only
            
            if not info or hist.empty:
                return None
            
            current_price = info.get('currentPrice') or hist['Close'].iloc[-1]
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'current_price': float(current_price),
                'price_change': float(info.get('regularMarketChange', 0)),
                'price_change_pct': float(info.get('regularMarketChangePercent', 0)),
                'volume': int(info.get('volume', 0)),
                'market_cap': self._format_market_cap(info.get('marketCap', 0)),
                'market_cap_value': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'pe_ratio': info.get('trailingPE'),
                'premium_tier': False
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching basic data for {symbol}: {e}")
            return None
    
    def _calculate_ai_sentiment(self, symbol):
        """Premium: AI-powered sentiment analysis from news and social media"""
        try:
            # Simplified sentiment analysis - in production would use news APIs
            ticker = yf.Ticker(symbol)
            news = ticker.news[:5] if hasattr(ticker, 'news') and ticker.news else []
            
            sentiment_scores = []
            for article in news:
                if 'title' in article:
                    blob = TextBlob(article['title'])
                    sentiment_scores.append(blob.sentiment.polarity)
            
            if sentiment_scores:
                avg_sentiment = np.mean(sentiment_scores)
                return {
                    'score': round(avg_sentiment, 3),
                    'classification': 'positive' if avg_sentiment > 0.1 else 'negative' if avg_sentiment < -0.1 else 'neutral',
                    'confidence': min(abs(avg_sentiment) * 2, 1.0)
                }
            
            return {'score': 0, 'classification': 'neutral', 'confidence': 0}
            
        except Exception as e:
            self.logger.warning(f"Error calculating sentiment for {symbol}: {e}")
            return {'score': 0, 'classification': 'neutral', 'confidence': 0}
    
    def _get_analyst_consensus(self, symbol):
        """Premium: Get analyst recommendations and price targets"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'recommendation': info.get('recommendationKey', 'hold'),
                'target_price': info.get('targetMeanPrice'),
                'num_analysts': info.get('numberOfAnalystOpinions', 0),
                'recommendation_score': self._convert_recommendation_to_score(info.get('recommendationKey', 'hold'))
            }
            
        except Exception as e:
            self.logger.warning(f"Error getting analyst data for {symbol}: {e}")
            return {'recommendation': 'hold', 'target_price': None, 'num_analysts': 0, 'recommendation_score': 3}
    
    def _calculate_risk_score(self, stock_data):
        """Premium: Calculate comprehensive risk assessment"""
        try:
            risk_factors = []
            
            # Volatility risk
            if stock_data.get('historical_volatility', 0) > 0.3:
                risk_factors.append('High volatility')
            
            # Liquidity risk
            if stock_data.get('volume', 0) < stock_data.get('avg_volume', 1) * 0.5:
                risk_factors.append('Low trading volume')
            
            # Valuation risk
            pe_ratio = stock_data.get('pe_ratio')
            if pe_ratio and pe_ratio > 50:
                risk_factors.append('High P/E ratio')
            
            # Market cap risk
            if stock_data.get('market_cap_value', 0) < 1e9:
                risk_factors.append('Small market cap')
            
            risk_score = min(len(risk_factors) * 20, 100)  # 0-100 scale
            
            return {
                'score': risk_score,
                'level': 'low' if risk_score < 30 else 'medium' if risk_score < 70 else 'high',
                'factors': risk_factors
            }
            
        except Exception as e:
            self.logger.warning(f"Error calculating risk score: {e}")
            return {'score': 50, 'level': 'medium', 'factors': []}
    
    def _calculate_momentum(self, symbol):
        """Premium: Calculate momentum indicators"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="30d")
            
            if len(hist) < 20:
                return {'score': 0, 'trend': 'neutral'}
            
            # Simple momentum calculation
            recent_avg = hist['Close'].tail(5).mean()
            older_avg = hist['Close'].head(5).mean()
            momentum = (recent_avg - older_avg) / older_avg
            
            return {
                'score': round(momentum * 100, 2),
                'trend': 'bullish' if momentum > 0.02 else 'bearish' if momentum < -0.02 else 'neutral',
                'strength': 'strong' if abs(momentum) > 0.05 else 'weak'
            }
            
        except Exception as e:
            self.logger.warning(f"Error calculating momentum for {symbol}: {e}")
            return {'score': 0, 'trend': 'neutral', 'strength': 'weak'}
    
    def _get_earnings_forecast(self, symbol):
        """Premium: Get earnings forecast and calendar"""
        try:
            ticker = yf.Ticker(symbol)
            calendar = ticker.calendar
            
            if calendar is not None and not calendar.empty:
                next_earnings = calendar.index[0] if len(calendar.index) > 0 else None
                return {
                    'next_earnings_date': next_earnings.strftime('%Y-%m-%d') if next_earnings else None,
                    'has_forecast': True
                }
            
            return {'next_earnings_date': None, 'has_forecast': False}
            
        except Exception as e:
            self.logger.warning(f"Error getting earnings forecast for {symbol}: {e}")
            return {'next_earnings_date': None, 'has_forecast': False}
    
    def _get_institutional_data(self, symbol):
        """Premium: Get institutional ownership data"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'institutional_ownership': info.get('heldByInstitutions', 0),
                'insider_ownership': info.get('heldByInsiders', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'float_shares': info.get('floatShares', 0)
            }
            
        except Exception as e:
            self.logger.warning(f"Error getting institutional data for {symbol}: {e}")
            return {'institutional_ownership': 0, 'insider_ownership': 0}
    
    def _calculate_ai_relevance(self, query, stock_data):
        """Premium: AI-powered relevance scoring with multiple factors"""
        try:
            score = 0
            query_lower = query.lower()
            
            # Exact symbol match
            if query_lower == stock_data['symbol'].lower():
                score += 50
            elif query_lower in stock_data['symbol'].lower():
                score += 30
            
            # Company name match
            if query_lower in stock_data['name'].lower():
                score += 20
            
            # Sector relevance
            if query_lower in stock_data.get('sector', '').lower():
                score += 15
            
            # Premium: Volume and momentum boost
            if stock_data.get('volume', 0) > stock_data.get('avg_volume', 1):
                score += 10
            
            momentum = stock_data.get('momentum_indicators', {}).get('score', 0)
            if abs(momentum) > 5:  # Strong momentum
                score += 10
            
            return min(score, 100)
            
        except Exception as e:
            self.logger.warning(f"Error calculating AI relevance: {e}")
            return 50
    
    def _calculate_basic_relevance(self, query, stock_data):
        """Free tier: Basic relevance calculation"""
        score = 0
        query_lower = query.lower()
        
        if query_lower == stock_data['symbol'].lower():
            score += 50
        elif query_lower in stock_data['symbol'].lower():
            score += 30
        
        if query_lower in stock_data['name'].lower():
            score += 20
        
        return min(score, 100)
    
    def _get_relevant_symbols(self, query, sector, market_cap, limit):
        """Get relevant stock symbols based on search criteria"""
        # Comprehensive symbol database
        all_symbols = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'TSLA', 'PLTR', 'SNOW', 'RIVN'],
            'Healthcare': ['JNJ', 'PFE', 'MRNA', 'ABBV', 'BMY'],
            'Financial': ['JPM', 'BAC', 'GS', 'MS', 'WFC'],
            'Consumer': ['AMZN', 'WMT', 'NFLX', 'DIS', 'SBUX'],
            'Energy': ['XOM', 'CVX', 'COP', 'SLB'],
            'Industrial': ['BA', 'CAT', 'GE', 'MMM']
        }
        
        symbols = []
        
        # Add symbols from specific sector if requested
        if sector and sector in all_symbols:
            symbols.extend(all_symbols[sector])
        else:
            # Add from all sectors
            for sector_symbols in all_symbols.values():
                symbols.extend(sector_symbols)
        
        # Filter by query match
        query_lower = query.lower()
        filtered_symbols = []
        
        for symbol in symbols:
            if (query_lower in symbol.lower() or 
                query_lower in self._get_company_name(symbol).lower()):
                filtered_symbols.append(symbol)
        
        # If no matches, return popular symbols
        if not filtered_symbols:
            filtered_symbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']
        
        return filtered_symbols[:limit]
    
    def _get_company_name(self, symbol):
        """Get company name for symbol matching"""
        names = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'NVDA': 'NVIDIA Corporation',
            'META': 'Meta Platforms Inc.',
            'TSLA': 'Tesla Inc.',
            'PLTR': 'Palantir Technologies Inc.',
            'SNOW': 'Snowflake Inc.',
            'RIVN': 'Rivian Automotive Inc.'
        }
        return names.get(symbol, symbol)
    
    def _format_market_cap(self, market_cap):
        """Format market cap value"""
        if market_cap >= 1e12:
            return f"${market_cap/1e12:.1f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.1f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.1f}M"
        else:
            return f"${market_cap:,.0f}"
    
    def _calculate_volatility(self, hist):
        """Calculate historical volatility"""
        if len(hist) < 2:
            return 0
        returns = hist['Close'].pct_change().dropna()
        return returns.std() * (252 ** 0.5)  # Annualized volatility
    
    def _convert_recommendation_to_score(self, recommendation):
        """Convert recommendation to numeric score"""
        scores = {
            'strong_buy': 5, 'buy': 4, 'hold': 3, 'sell': 2, 'strong_sell': 1
        }
        return scores.get(recommendation, 3)
    
    def _sort_premium_results(self, results, sort_by, query):
        """Premium: Advanced sorting with AI weighting"""
        if sort_by == 'ai_relevance':
            return sorted(results, key=lambda x: x.get('ai_relevance_score', 0), reverse=True)
        elif sort_by == 'momentum':
            return sorted(results, key=lambda x: abs(x.get('momentum_indicators', {}).get('score', 0)), reverse=True)
        elif sort_by == 'analyst_rating':
            return sorted(results, key=lambda x: x.get('analyst_consensus', {}).get('recommendation_score', 3), reverse=True)
        elif sort_by == 'risk':
            return sorted(results, key=lambda x: x.get('risk_assessment', {}).get('score', 50))
        else:
            return self._sort_basic_results(results, sort_by)
    
    def _sort_basic_results(self, results, sort_by):
        """Basic sorting for free tier"""
        if sort_by == 'price':
            return sorted(results, key=lambda x: x.get('current_price', 0), reverse=True)
        elif sort_by == 'volume':
            return sorted(results, key=lambda x: x.get('volume', 0), reverse=True)
        elif sort_by == 'market_cap':
            return sorted(results, key=lambda x: x.get('market_cap_value', 0), reverse=True)
        else:  # relevance
            score_key = 'ai_relevance_score' if (results and 'ai_relevance_score' in results[0]) else 'basic_relevance_score'
            return sorted(results, key=lambda x: x.get(score_key, 0), reverse=True)

# Global instance
premium_search_engine = PremiumSearchEngine()