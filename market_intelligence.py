"""
Market Intelligence Hub
Real-time market analysis, sentiment tracking, and intelligence gathering
"""

import logging
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import yfinance as yf
import pandas as pd
import numpy as np
from textblob import TextBlob
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentType(Enum):
    VERY_BEARISH = "very_bearish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    BULLISH = "bullish"
    VERY_BULLISH = "very_bullish"

class MarketRegime(Enum):
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"

@dataclass
class NewsItem:
    """Represents a market news item"""
    title: str
    summary: str
    source: str
    timestamp: datetime
    url: str
    sentiment_score: float
    sentiment_type: SentimentType
    symbols: List[str]
    relevance_score: float
    category: str

@dataclass
class SentimentAnalysis:
    """Market sentiment analysis results"""
    overall_sentiment: SentimentType
    sentiment_score: float
    confidence: float
    bullish_signals: List[str]
    bearish_signals: List[str]
    neutral_signals: List[str]
    news_count: int
    time_period: str

@dataclass
class EarningsEvent:
    """Earnings event information"""
    symbol: str
    company_name: str
    earnings_date: datetime
    estimated_eps: float
    actual_eps: Optional[float]
    estimated_revenue: float
    actual_revenue: Optional[float]
    surprise_factor: Optional[float]
    guidance: str
    analyst_sentiment: SentimentType

@dataclass
class MarketAlert:
    """Market intelligence alert"""
    alert_id: str
    alert_type: str
    symbol: str
    title: str
    description: str
    severity: str
    timestamp: datetime
    data: Dict[str, Any]

class SentimentAnalyzer:
    """Advanced sentiment analysis for market intelligence"""
    
    def __init__(self):
        self.bullish_keywords = [
            'buy', 'bullish', 'positive', 'upgrade', 'strong', 'growth',
            'rally', 'surge', 'breakout', 'uptrend', 'momentum', 'outperform',
            'beat', 'exceed', 'raise', 'increase', 'expansion', 'recovery'
        ]
        
        self.bearish_keywords = [
            'sell', 'bearish', 'negative', 'downgrade', 'weak', 'decline',
            'crash', 'plunge', 'breakdown', 'downtrend', 'correction', 'underperform',
            'miss', 'below', 'cut', 'reduce', 'recession', 'concern'
        ]
        
        logger.info("Sentiment Analyzer initialized")
    
    def analyze_text(self, text: str) -> Tuple[float, SentimentType]:
        """Analyze sentiment of text"""
        try:
            # Basic sentiment using TextBlob
            blob = TextBlob(text)
            base_sentiment = blob.sentiment.polarity
            
            # Keyword-based enhancement
            text_lower = text.lower()
            bullish_score = sum(1 for word in self.bullish_keywords if word in text_lower)
            bearish_score = sum(1 for word in self.bearish_keywords if word in text_lower)
            
            # Combine scores
            keyword_sentiment = (bullish_score - bearish_score) / max(1, bullish_score + bearish_score)
            
            # Weighted final sentiment
            final_sentiment = (base_sentiment * 0.6) + (keyword_sentiment * 0.4)
            
            # Classify sentiment
            if final_sentiment <= -0.6:
                sentiment_type = SentimentType.VERY_BEARISH
            elif final_sentiment <= -0.2:
                sentiment_type = SentimentType.BEARISH
            elif final_sentiment <= 0.2:
                sentiment_type = SentimentType.NEUTRAL
            elif final_sentiment <= 0.6:
                sentiment_type = SentimentType.BULLISH
            else:
                sentiment_type = SentimentType.VERY_BULLISH
            
            return final_sentiment, sentiment_type
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0.0, SentimentType.NEUTRAL
    
    def analyze_news_batch(self, news_items: List[Dict]) -> SentimentAnalysis:
        """Analyze sentiment across multiple news items"""
        if not news_items:
            return SentimentAnalysis(
                overall_sentiment=SentimentType.NEUTRAL,
                sentiment_score=0.0,
                confidence=0.0,
                bullish_signals=[],
                bearish_signals=[],
                neutral_signals=[],
                news_count=0,
                time_period="N/A"
            )
        
        sentiments = []
        bullish_signals = []
        bearish_signals = []
        neutral_signals = []
        
        for item in news_items:
            text = f"{item.get('title', '')} {item.get('summary', '')}"
            score, sentiment_type = self.analyze_text(text)
            sentiments.append(score)
            
            if sentiment_type in [SentimentType.BULLISH, SentimentType.VERY_BULLISH]:
                bullish_signals.append(item.get('title', ''))
            elif sentiment_type in [SentimentType.BEARISH, SentimentType.VERY_BEARISH]:
                bearish_signals.append(item.get('title', ''))
            else:
                neutral_signals.append(item.get('title', ''))
        
        # Calculate overall sentiment
        avg_sentiment = np.mean(sentiments) if sentiments else 0.0
        confidence = 1.0 - (np.std(sentiments) if len(sentiments) > 1 else 0.0)
        
        if avg_sentiment <= -0.3:
            overall_sentiment = SentimentType.BEARISH
        elif avg_sentiment <= 0.3:
            overall_sentiment = SentimentType.NEUTRAL
        else:
            overall_sentiment = SentimentType.BULLISH
        
        return SentimentAnalysis(
            overall_sentiment=overall_sentiment,
            sentiment_score=avg_sentiment,
            confidence=confidence,
            bullish_signals=bullish_signals[:5],
            bearish_signals=bearish_signals[:5],
            neutral_signals=neutral_signals[:5],
            news_count=len(news_items),
            time_period="24h"
        )

class NewsAggregator:
    """Aggregates news from multiple sources"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        logger.info("News Aggregator initialized")
    
    def get_market_news(self, symbols: List[str] = None, hours: int = 24) -> List[NewsItem]:
        """Get market news for specified symbols"""
        try:
            news_items = []
            
            # For demo, create synthetic news based on real market patterns
            sample_news = self._generate_sample_news(symbols or ['AAPL', 'MSFT', 'GOOGL'])
            
            for item in sample_news:
                sentiment_score, sentiment_type = self.sentiment_analyzer.analyze_text(
                    f"{item['title']} {item['summary']}"
                )
                
                news_item = NewsItem(
                    title=item['title'],
                    summary=item['summary'],
                    source=item['source'],
                    timestamp=datetime.now() - timedelta(hours=item['hours_ago']),
                    url=item['url'],
                    sentiment_score=sentiment_score,
                    sentiment_type=sentiment_type,
                    symbols=item['symbols'],
                    relevance_score=item['relevance'],
                    category=item['category']
                )
                news_items.append(news_item)
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error getting market news: {e}")
            return []
    
    def _generate_sample_news(self, symbols: List[str]) -> List[Dict]:
        """Generate sample news items for demonstration"""
        sample_news = [
            {
                'title': f'{symbols[0]} Reports Strong Q4 Earnings, Beats Analyst Expectations',
                'summary': f'{symbols[0]} delivered robust quarterly results with revenue growth of 15% year-over-year, driven by strong demand and operational efficiency improvements.',
                'source': 'Financial Times',
                'hours_ago': 2,
                'url': 'https://example.com/news/1',
                'symbols': [symbols[0]],
                'relevance': 0.95,
                'category': 'earnings'
            },
            {
                'title': 'Federal Reserve Signals Potential Rate Cut in Next Meeting',
                'summary': 'Fed officials indicate growing confidence in inflation trends, opening door for monetary policy adjustments that could benefit growth stocks.',
                'source': 'Reuters',
                'hours_ago': 4,
                'url': 'https://example.com/news/2',
                'symbols': symbols,
                'relevance': 0.88,
                'category': 'monetary_policy'
            },
            {
                'title': 'Tech Sector Sees Increased Institutional Investment',
                'summary': 'Major pension funds and institutional investors are increasing allocations to technology stocks, citing long-term growth potential.',
                'source': 'Bloomberg',
                'hours_ago': 6,
                'url': 'https://example.com/news/3',
                'symbols': symbols,
                'relevance': 0.82,
                'category': 'sector_analysis'
            },
            {
                'title': 'Market Volatility Expected Due to Geopolitical Tensions',
                'summary': 'Analysts warn of potential market turbulence as international trade discussions remain uncertain, affecting risk-sensitive assets.',
                'source': 'CNBC',
                'hours_ago': 8,
                'url': 'https://example.com/news/4',
                'symbols': symbols,
                'relevance': 0.75,
                'category': 'geopolitical'
            }
        ]
        
        return sample_news

class EarningsTracker:
    """Tracks earnings events and predictions"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        logger.info("Earnings Tracker initialized")
    
    def get_upcoming_earnings(self, days_ahead: int = 7) -> List[EarningsEvent]:
        """Get upcoming earnings events"""
        try:
            # For demo, generate sample earnings data
            sample_earnings = self._generate_sample_earnings()
            
            events = []
            for item in sample_earnings:
                event = EarningsEvent(
                    symbol=item['symbol'],
                    company_name=item['company_name'],
                    earnings_date=datetime.now() + timedelta(days=item['days_ahead']),
                    estimated_eps=item['estimated_eps'],
                    actual_eps=item.get('actual_eps'),
                    estimated_revenue=item['estimated_revenue'],
                    actual_revenue=item.get('actual_revenue'),
                    surprise_factor=item.get('surprise_factor'),
                    guidance=item['guidance'],
                    analyst_sentiment=item['analyst_sentiment']
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting earnings events: {e}")
            return []
    
    def _generate_sample_earnings(self) -> List[Dict]:
        """Generate sample earnings data"""
        return [
            {
                'symbol': 'AAPL',
                'company_name': 'Apple Inc.',
                'days_ahead': 2,
                'estimated_eps': 1.25,
                'estimated_revenue': 85000000000,
                'guidance': 'Positive outlook for next quarter',
                'analyst_sentiment': SentimentType.BULLISH
            },
            {
                'symbol': 'MSFT',
                'company_name': 'Microsoft Corporation',
                'days_ahead': 4,
                'estimated_eps': 2.10,
                'estimated_revenue': 52000000000,
                'guidance': 'Cloud growth expected to continue',
                'analyst_sentiment': SentimentType.BULLISH
            },
            {
                'symbol': 'GOOGL',
                'company_name': 'Alphabet Inc.',
                'days_ahead': 6,
                'estimated_eps': 1.85,
                'estimated_revenue': 68000000000,
                'guidance': 'Ad revenue showing recovery',
                'analyst_sentiment': SentimentType.NEUTRAL
            }
        ]

class MarketRegimeDetector:
    """Detects current market regime and transitions"""
    
    def __init__(self):
        self.lookback_periods = [20, 50, 200]  # Days for different timeframes
        logger.info("Market Regime Detector initialized")
    
    def detect_regime(self, symbol: str = "^GSPC") -> Dict[str, Any]:
        """Detect current market regime"""
        try:
            # Get market data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return self._default_regime()
            
            prices = hist['Close'].values
            volumes = hist['Volume'].values
            
            # Calculate regime indicators
            regime_indicators = {
                'trend_strength': self._calculate_trend_strength(prices),
                'volatility_regime': self._calculate_volatility_regime(prices),
                'volume_regime': self._calculate_volume_regime(volumes),
                'momentum_regime': self._calculate_momentum_regime(prices),
                'market_breadth': self._calculate_market_breadth(prices)
            }
            
            # Determine overall regime
            overall_regime = self._classify_regime(regime_indicators)
            
            return {
                'regime': overall_regime,
                'confidence': regime_indicators['trend_strength'],
                'indicators': regime_indicators,
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol
            }
            
        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            return self._default_regime()
    
    def _calculate_trend_strength(self, prices: np.ndarray) -> float:
        """Calculate trend strength indicator"""
        if len(prices) < 50:
            return 0.5
        
        # Calculate multiple moving averages
        ma_20 = np.mean(prices[-20:])
        ma_50 = np.mean(prices[-50:])
        ma_200 = np.mean(prices[-200:]) if len(prices) >= 200 else ma_50
        
        current_price = prices[-1]
        
        # Trend strength based on price relative to moving averages
        if current_price > ma_20 > ma_50 > ma_200:
            return 0.9  # Strong uptrend
        elif current_price < ma_20 < ma_50 < ma_200:
            return 0.1  # Strong downtrend
        else:
            return 0.5  # Neutral/sideways
    
    def _calculate_volatility_regime(self, prices: np.ndarray) -> str:
        """Calculate volatility regime"""
        if len(prices) < 20:
            return "normal"
        
        # Calculate rolling volatility
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns[-20:]) * np.sqrt(252)  # Annualized
        
        if volatility > 0.3:
            return "high"
        elif volatility < 0.15:
            return "low"
        else:
            return "normal"
    
    def _calculate_volume_regime(self, volumes: np.ndarray) -> str:
        """Calculate volume regime"""
        if len(volumes) < 20:
            return "normal"
        
        recent_volume = np.mean(volumes[-5:])
        avg_volume = np.mean(volumes[-20:])
        
        if recent_volume > avg_volume * 1.5:
            return "high"
        elif recent_volume < avg_volume * 0.7:
            return "low"
        else:
            return "normal"
    
    def _calculate_momentum_regime(self, prices: np.ndarray) -> float:
        """Calculate momentum regime"""
        if len(prices) < 20:
            return 0.5
        
        # Simple momentum calculation
        momentum = (prices[-1] - prices[-20]) / prices[-20]
        
        # Normalize to 0-1 scale
        return max(0, min(1, (momentum + 0.2) / 0.4))
    
    def _calculate_market_breadth(self, prices: np.ndarray) -> float:
        """Calculate market breadth indicator"""
        if len(prices) < 10:
            return 0.5
        
        # Simple breadth using recent price action
        up_days = sum(1 for i in range(1, min(10, len(prices))) if prices[-i] > prices[-i-1])
        breadth = up_days / 9
        
        return breadth
    
    def _classify_regime(self, indicators: Dict[str, Any]) -> MarketRegime:
        """Classify overall market regime"""
        trend_strength = indicators['trend_strength']
        volatility = indicators['volatility_regime']
        
        if trend_strength > 0.7 and volatility != "high":
            return MarketRegime.BULL_MARKET
        elif trend_strength < 0.3 and volatility != "high":
            return MarketRegime.BEAR_MARKET
        elif volatility == "high":
            return MarketRegime.VOLATILE
        else:
            return MarketRegime.SIDEWAYS
    
    def _default_regime(self) -> Dict[str, Any]:
        """Default regime response"""
        return {
            'regime': MarketRegime.SIDEWAYS,
            'confidence': 0.5,
            'indicators': {},
            'timestamp': datetime.now().isoformat(),
            'symbol': '^GSPC'
        }

class MarketIntelligenceHub:
    """Central hub for market intelligence"""
    
    def __init__(self):
        self.news_aggregator = NewsAggregator()
        self.earnings_tracker = EarningsTracker()
        self.regime_detector = MarketRegimeDetector()
        self.alerts = []
        
        logger.info("Market Intelligence Hub initialized")
    
    def get_market_overview(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Get comprehensive market overview"""
        try:
            symbols = symbols or ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
            
            # Get news and sentiment
            news_items = self.news_aggregator.get_market_news(symbols)
            news_dicts = [item.__dict__ for item in news_items]
            sentiment_analysis = self.news_aggregator.sentiment_analyzer.analyze_news_batch(news_dicts)
            
            # Get earnings events
            earnings_events = self.earnings_tracker.get_upcoming_earnings()
            
            # Get market regime
            market_regime = self.regime_detector.detect_regime()
            
            # Generate market alerts
            alerts = self.generate_market_alerts(symbols, news_items, market_regime)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'sentiment_analysis': sentiment_analysis.__dict__,
                'news_items': [item.__dict__ for item in news_items[:10]],
                'earnings_events': [event.__dict__ for event in earnings_events],
                'market_regime': market_regime,
                'alerts': [alert.__dict__ for alert in alerts],
                'summary': self._generate_market_summary(sentiment_analysis, market_regime)
            }
            
        except Exception as e:
            logger.error(f"Error generating market overview: {e}")
            return {'error': str(e)}
    
    def generate_market_alerts(self, symbols: List[str], news_items: List[NewsItem], 
                              market_regime: Dict[str, Any]) -> List[MarketAlert]:
        """Generate intelligent market alerts"""
        alerts = []
        
        try:
            # Sentiment-based alerts
            if any(item.sentiment_type == SentimentType.VERY_BEARISH for item in news_items):
                alerts.append(MarketAlert(
                    alert_id=f"SENT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    alert_type="sentiment_warning",
                    symbol="MARKET",
                    title="Very Bearish Sentiment Detected",
                    description="Multiple news sources showing very bearish sentiment. Consider defensive positioning.",
                    severity="high",
                    timestamp=datetime.now(),
                    data={'bearish_news_count': len([i for i in news_items if i.sentiment_type == SentimentType.VERY_BEARISH])}
                ))
            
            # Regime change alerts
            if market_regime['regime'] == MarketRegime.VOLATILE:
                alerts.append(MarketAlert(
                    alert_id=f"REG_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    alert_type="regime_change",
                    symbol="MARKET",
                    title="High Volatility Regime Detected",
                    description="Market entered high volatility regime. Adjust position sizes accordingly.",
                    severity="medium",
                    timestamp=datetime.now(),
                    data={'volatility_regime': market_regime['indicators'].get('volatility_regime', 'unknown')}
                ))
            
            # Volume alerts
            if market_regime['indicators'].get('volume_regime') == 'high':
                alerts.append(MarketAlert(
                    alert_id=f"VOL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    alert_type="volume_spike",
                    symbol="MARKET",
                    title="High Volume Activity",
                    description="Unusual volume activity detected. Monitor for breakout opportunities.",
                    severity="low",
                    timestamp=datetime.now(),
                    data={'volume_regime': 'high'}
                ))
            
        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
        
        return alerts
    
    def _generate_market_summary(self, sentiment: SentimentAnalysis, 
                                regime: Dict[str, Any]) -> str:
        """Generate human-readable market summary"""
        try:
            sentiment_desc = sentiment.overall_sentiment.value.replace('_', ' ').title()
            regime_desc = regime['regime'].value.replace('_', ' ').title()
            
            summary = f"Market shows {sentiment_desc} sentiment with {regime_desc} regime. "
            summary += f"Sentiment confidence: {sentiment.confidence:.1%}. "
            summary += f"Regime confidence: {regime['confidence']:.1%}. "
            
            if sentiment.bullish_signals:
                summary += f"Key bullish signals: {', '.join(sentiment.bullish_signals[:2])}. "
            
            if sentiment.bearish_signals:
                summary += f"Key bearish signals: {', '.join(sentiment.bearish_signals[:2])}. "
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Market analysis summary unavailable."

# Global market intelligence instance
market_intelligence = MarketIntelligenceHub()

def get_market_intelligence():
    """Get the global market intelligence instance"""
    return market_intelligence