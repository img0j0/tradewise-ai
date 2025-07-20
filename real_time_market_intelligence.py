"""
Real-Time AI Market Intelligence System
Advanced market analysis with live news sentiment, volatility prediction, and intelligent alerts
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from textblob import TextBlob
import yfinance as yf
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import threading
import schedule
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MarketAlert:
    symbol: str
    alert_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    message: str
    confidence: float
    timestamp: datetime
    source: str

@dataclass
class NewsArticle:
    title: str
    content: str
    source: str
    timestamp: datetime
    sentiment_score: float
    relevance_score: float
    symbols: List[str]

class RealTimeMarketIntelligence:
    def __init__(self):
        self.active_alerts = []
        self.news_cache = {}
        self.sentiment_cache = {}
        self.volatility_predictions = {}
        self.monitoring_symbols = set()
        self.is_monitoring = False
        
        # Initialize news sources (free alternatives to Reuters/Bloomberg)
        self.news_sources = {
            'marketwatch': 'https://www.marketwatch.com/rss/topstories',
            'yahoo_finance': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'investing': 'https://www.investing.com/rss/news.rss'
        }
        
        logger.info("Real-Time Market Intelligence initialized")

    def start_monitoring(self):
        """Start continuous market monitoring"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        
        # Schedule regular updates
        schedule.every(30).seconds.do(self._update_market_sentiment)
        schedule.every(2).minutes.do(self._analyze_volatility_patterns)
        schedule.every(5).minutes.do(self._generate_intelligence_alerts)
        schedule.every(10).minutes.do(self._fetch_market_news)
        
        # Start monitoring thread
        monitoring_thread = threading.Thread(target=self._monitoring_loop)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        logger.info("Market intelligence monitoring started")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)

    def add_symbol_to_monitor(self, symbol: str):
        """Add symbol to monitoring list"""
        self.monitoring_symbols.add(symbol.upper())
        logger.info(f"Added {symbol} to monitoring")

    def remove_symbol_from_monitor(self, symbol: str):
        """Remove symbol from monitoring"""
        self.monitoring_symbols.discard(symbol.upper())
        logger.info(f"Removed {symbol} from monitoring")

    def _fetch_market_news(self):
        """Fetch and analyze market news from multiple sources"""
        try:
            news_articles = []
            
            # Simulate news fetching (in production, integrate with real news APIs)
            sample_news = [
                {
                    'title': 'Federal Reserve Signals Potential Rate Changes Ahead',
                    'content': 'The Federal Reserve indicated today that monetary policy adjustments may be necessary to address current economic conditions...',
                    'source': 'MarketWatch',
                    'symbols': ['SPY', 'QQQ', 'IWM']
                },
                {
                    'title': 'Technology Sector Shows Strong Earnings Growth',
                    'content': 'Major technology companies report better-than-expected quarterly earnings, driving sector optimism...',
                    'source': 'Yahoo Finance',
                    'symbols': ['AAPL', 'MSFT', 'GOOGL', 'META']
                },
                {
                    'title': 'Energy Stocks Rally on Supply Concerns',
                    'content': 'Geopolitical tensions and supply chain disruptions boost energy sector performance across major indices...',
                    'source': 'Investing.com',
                    'symbols': ['XOM', 'CVX', 'COP', 'SLB']
                }
            ]
            
            for news_item in sample_news:
                # Analyze sentiment using TextBlob
                sentiment = TextBlob(news_item['content'])
                sentiment_score = sentiment.sentiment.polarity
                
                article = NewsArticle(
                    title=news_item['title'],
                    content=news_item['content'],
                    source=news_item['source'],
                    timestamp=datetime.now(),
                    sentiment_score=sentiment_score,
                    relevance_score=0.8,  # Would be calculated based on symbol relevance
                    symbols=news_item['symbols']
                )
                
                news_articles.append(article)
                
                # Cache news for symbols
                for symbol in article.symbols:
                    if symbol not in self.news_cache:
                        self.news_cache[symbol] = []
                    self.news_cache[symbol].append(article)
                    
                    # Keep only recent news (last 24 hours)
                    cutoff_time = datetime.now() - timedelta(hours=24)
                    self.news_cache[symbol] = [
                        n for n in self.news_cache[symbol] 
                        if n.timestamp > cutoff_time
                    ]
            
            logger.info(f"Fetched and analyzed {len(news_articles)} news articles")
            
        except Exception as e:
            logger.error(f"Error fetching market news: {e}")

    def _update_market_sentiment(self):
        """Update market sentiment for monitored symbols"""
        try:
            for symbol in self.monitoring_symbols:
                sentiment_data = self._calculate_symbol_sentiment(symbol)
                self.sentiment_cache[symbol] = sentiment_data
                
            logger.info(f"Updated sentiment for {len(self.monitoring_symbols)} symbols")
            
        except Exception as e:
            logger.error(f"Error updating market sentiment: {e}")

    def _calculate_symbol_sentiment(self, symbol: str) -> Dict:
        """Calculate comprehensive sentiment for a symbol"""
        try:
            # Get recent news sentiment
            news_sentiment = 0.0
            news_count = 0
            
            if symbol in self.news_cache:
                for article in self.news_cache[symbol]:
                    news_sentiment += article.sentiment_score
                    news_count += 1
            
            avg_news_sentiment = news_sentiment / max(news_count, 1)
            
            # Get price momentum sentiment
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if len(hist) >= 2:
                price_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]
                price_sentiment = min(max(price_change * 5, -1), 1)  # Normalize to -1 to 1
            else:
                price_sentiment = 0.0
            
            # Calculate volume sentiment
            if len(hist) >= 5:
                avg_volume = hist['Volume'].mean()
                recent_volume = hist['Volume'].iloc[-1]
                volume_sentiment = min(max((recent_volume - avg_volume) / avg_volume, -1), 1)
            else:
                volume_sentiment = 0.0
            
            # Combine sentiments with weights
            overall_sentiment = (
                avg_news_sentiment * 0.4 +
                price_sentiment * 0.4 +
                volume_sentiment * 0.2
            )
            
            return {
                'overall_sentiment': overall_sentiment,
                'news_sentiment': avg_news_sentiment,
                'price_sentiment': price_sentiment,
                'volume_sentiment': volume_sentiment,
                'news_count': news_count,
                'confidence': min(news_count * 0.2 + 0.3, 1.0),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error calculating sentiment for {symbol}: {e}")
            return {
                'overall_sentiment': 0.0,
                'news_sentiment': 0.0,
                'price_sentiment': 0.0,
                'volume_sentiment': 0.0,
                'news_count': 0,
                'confidence': 0.0,
                'timestamp': datetime.now()
            }

    def _analyze_volatility_patterns(self):
        """Analyze and predict market volatility"""
        try:
            for symbol in self.monitoring_symbols:
                volatility_data = self._predict_symbol_volatility(symbol)
                self.volatility_predictions[symbol] = volatility_data
                
            logger.info(f"Analyzed volatility for {len(self.monitoring_symbols)} symbols")
            
        except Exception as e:
            logger.error(f"Error analyzing volatility: {e}")

    def _predict_symbol_volatility(self, symbol: str) -> Dict:
        """Predict volatility for a symbol using historical data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="30d")
            
            if len(hist) < 10:
                return {'error': 'Insufficient data'}
            
            # Calculate historical volatility
            returns = hist['Close'].pct_change().dropna()
            historical_vol = returns.std() * np.sqrt(252)  # Annualized
            
            # Calculate recent volatility (last 5 days)
            recent_returns = returns.tail(5)
            recent_vol = recent_returns.std() * np.sqrt(252)
            
            # Volatility trend
            vol_trend = (recent_vol - historical_vol) / historical_vol
            
            # Predict next day volatility using simple model
            predicted_vol = recent_vol * (1 + vol_trend * 0.1)
            
            # Volume-based volatility indicator
            volume_vol = hist['Volume'].pct_change().std()
            
            return {
                'historical_volatility': historical_vol,
                'recent_volatility': recent_vol,
                'predicted_volatility': predicted_vol,
                'volatility_trend': vol_trend,
                'volume_volatility': volume_vol,
                'volatility_regime': self._classify_volatility_regime(recent_vol),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error predicting volatility for {symbol}: {e}")
            return {'error': str(e)}

    def _classify_volatility_regime(self, volatility: float) -> str:
        """Classify volatility into regimes"""
        if volatility < 0.15:
            return "LOW"
        elif volatility < 0.25:
            return "MEDIUM"
        elif volatility < 0.35:
            return "HIGH"
        else:
            return "EXTREME"

    def _generate_intelligence_alerts(self):
        """Generate intelligent market alerts"""
        try:
            new_alerts = []
            
            for symbol in self.monitoring_symbols:
                # Check sentiment alerts
                if symbol in self.sentiment_cache:
                    sentiment_data = self.sentiment_cache[symbol]
                    
                    if sentiment_data['overall_sentiment'] < -0.7:
                        alert = MarketAlert(
                            symbol=symbol,
                            alert_type="NEGATIVE_SENTIMENT",
                            severity="HIGH",
                            message=f"Strong negative sentiment detected for {symbol} (score: {sentiment_data['overall_sentiment']:.2f})",
                            confidence=sentiment_data['confidence'],
                            timestamp=datetime.now(),
                            source="Sentiment Analysis"
                        )
                        new_alerts.append(alert)
                    
                    elif sentiment_data['overall_sentiment'] > 0.7:
                        alert = MarketAlert(
                            symbol=symbol,
                            alert_type="POSITIVE_SENTIMENT",
                            severity="MEDIUM",
                            message=f"Strong positive sentiment detected for {symbol} (score: {sentiment_data['overall_sentiment']:.2f})",
                            confidence=sentiment_data['confidence'],
                            timestamp=datetime.now(),
                            source="Sentiment Analysis"
                        )
                        new_alerts.append(alert)
                
                # Check volatility alerts
                if symbol in self.volatility_predictions:
                    vol_data = self.volatility_predictions[symbol]
                    
                    if 'volatility_regime' in vol_data and vol_data['volatility_regime'] == "EXTREME":
                        alert = MarketAlert(
                            symbol=symbol,
                            alert_type="HIGH_VOLATILITY",
                            severity="CRITICAL",
                            message=f"Extreme volatility detected for {symbol} (predicted: {vol_data.get('predicted_volatility', 0):.1%})",
                            confidence=0.8,
                            timestamp=datetime.now(),
                            source="Volatility Analysis"
                        )
                        new_alerts.append(alert)
            
            # Add new alerts and remove old ones
            cutoff_time = datetime.now() - timedelta(hours=6)
            self.active_alerts = [
                alert for alert in self.active_alerts 
                if alert.timestamp > cutoff_time
            ]
            self.active_alerts.extend(new_alerts)
            
            if new_alerts:
                logger.info(f"Generated {len(new_alerts)} new intelligence alerts")
            
        except Exception as e:
            logger.error(f"Error generating alerts: {e}")

    def get_market_overview(self) -> Dict:
        """Get comprehensive market overview"""
        try:
            # Market sentiment summary
            sentiments = []
            for symbol, data in self.sentiment_cache.items():
                sentiments.append(data['overall_sentiment'])
            
            avg_sentiment = np.mean(sentiments) if sentiments else 0.0
            
            # Volatility summary
            volatilities = []
            high_vol_count = 0
            for symbol, data in self.volatility_predictions.items():
                if 'recent_volatility' in data:
                    volatilities.append(data['recent_volatility'])
                    if data.get('volatility_regime') in ['HIGH', 'EXTREME']:
                        high_vol_count += 1
            
            avg_volatility = np.mean(volatilities) if volatilities else 0.0
            
            # Alert summary
            alert_counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
            for alert in self.active_alerts:
                alert_counts[alert.severity] += 1
            
            return {
                'market_sentiment': {
                    'average_sentiment': avg_sentiment,
                    'sentiment_direction': 'POSITIVE' if avg_sentiment > 0.1 else 'NEGATIVE' if avg_sentiment < -0.1 else 'NEUTRAL',
                    'confidence': min(len(sentiments) * 0.1 + 0.5, 1.0)
                },
                'volatility_analysis': {
                    'average_volatility': avg_volatility,
                    'high_volatility_stocks': high_vol_count,
                    'volatility_regime': 'HIGH' if avg_volatility > 0.25 else 'MEDIUM' if avg_volatility > 0.15 else 'LOW'
                },
                'active_alerts': alert_counts,
                'total_alerts': len(self.active_alerts),
                'monitoring_symbols': list(self.monitoring_symbols),
                'last_updated': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {'error': str(e)}

    def get_symbol_intelligence(self, symbol: str) -> Dict:
        """Get comprehensive intelligence for a specific symbol"""
        symbol = symbol.upper()
        
        intelligence = {
            'symbol': symbol,
            'sentiment_analysis': self.sentiment_cache.get(symbol, {}),
            'volatility_prediction': self.volatility_predictions.get(symbol, {}),
            'recent_news': [],
            'alerts': [],
            'timestamp': datetime.now()
        }
        
        # Add recent news
        if symbol in self.news_cache:
            intelligence['recent_news'] = [
                {
                    'title': article.title,
                    'source': article.source,
                    'sentiment_score': article.sentiment_score,
                    'timestamp': article.timestamp.isoformat()
                }
                for article in self.news_cache[symbol][-5:]  # Last 5 articles
            ]
        
        # Add relevant alerts
        intelligence['alerts'] = [
            {
                'type': alert.alert_type,
                'severity': alert.severity,
                'message': alert.message,
                'confidence': alert.confidence,
                'timestamp': alert.timestamp.isoformat()
            }
            for alert in self.active_alerts
            if alert.symbol == symbol
        ]
        
        return intelligence

    def get_trending_topics(self) -> List[Dict]:
        """Get trending market topics based on news analysis"""
        try:
            topic_counts = {}
            topic_sentiments = {}
            
            # Analyze news for trending topics
            for symbol, articles in self.news_cache.items():
                for article in articles:
                    # Simple keyword extraction (in production, use NLP)
                    keywords = ['earnings', 'fed', 'rate', 'growth', 'merger', 'acquisition', 
                               'revenue', 'profit', 'guidance', 'forecast', 'expansion']
                    
                    content_lower = article.content.lower()
                    for keyword in keywords:
                        if keyword in content_lower:
                            if keyword not in topic_counts:
                                topic_counts[keyword] = 0
                                topic_sentiments[keyword] = []
                            topic_counts[keyword] += 1
                            topic_sentiments[keyword].append(article.sentiment_score)
            
            # Create trending topics list
            trending = []
            for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                avg_sentiment = np.mean(topic_sentiments[topic])
                trending.append({
                    'topic': topic.title(),
                    'mention_count': count,
                    'sentiment': avg_sentiment,
                    'trend_strength': min(count * 0.2, 1.0)
                })
            
            return trending
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []

# Global instance
market_intelligence = RealTimeMarketIntelligence()