"""
Market News & Sentiment Analysis - Real-time news for informed trading decisions
"""
import requests
import json
import time
from typing import List, Dict, Any
from textblob import TextBlob
import yfinance as yf

class MarketNewsService:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        
    def get_stock_news(self, symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent news for a specific stock"""
        cache_key = f"news_{symbol}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_timeout:
                return cached_data[:limit]
        
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            processed_news = []
            for item in news[:limit]:
                # Analyze sentiment
                sentiment_score = self.analyze_sentiment(item.get('title', ''))
                
                processed_item = {
                    'title': item.get('title', 'No title'),
                    'summary': item.get('summary', '')[:200] + "..." if len(item.get('summary', '')) > 200 else item.get('summary', ''),
                    'url': item.get('link', ''),
                    'published': item.get('providerPublishTime', int(time.time())),
                    'source': item.get('publisher', 'Unknown'),
                    'sentiment': sentiment_score,
                    'sentiment_label': self.get_sentiment_label(sentiment_score)
                }
                processed_news.append(processed_item)
            
            # Cache the results
            self.cache[cache_key] = (processed_news, time.time())
            return processed_news
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []
    
    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text (-1 to 1)"""
        try:
            blob = TextBlob(text)
            return float(blob.sentiment.polarity)
        except:
            return 0.0
    
    def get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.1:
            return "Positive"
        elif score < -0.1:
            return "Negative"
        else:
            return "Neutral"
    
    def get_market_overview_news(self) -> List[Dict[str, Any]]:
        """Get general market news"""
        major_indices = ['SPY', 'QQQ', 'IWM']  # S&P 500, NASDAQ, Russell 2000
        all_news = []
        
        for symbol in major_indices:
            news = self.get_stock_news(symbol, 2)
            for item in news:
                item['category'] = 'Market Overview'
                all_news.append(item)
        
        # Sort by published date
        all_news.sort(key=lambda x: x['published'], reverse=True)
        return all_news[:6]
    
    def get_trending_stocks_news(self) -> List[Dict[str, Any]]:
        """Get news for trending stocks"""
        trending_symbols = ['AAPL', 'TSLA', 'NVDA', 'GOOGL', 'MSFT', 'AMZN']
        trending_news = []
        
        for symbol in trending_symbols:
            news = self.get_stock_news(symbol, 1)
            if news:
                news[0]['category'] = f'{symbol} News'
                trending_news.append(news[0])
        
        return trending_news
    
    def get_sector_sentiment(self) -> Dict[str, Any]:
        """Analyze sentiment across major sectors"""
        sectors = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'NVDA'],
            'Energy': ['XOM', 'CVX', 'COP'],
            'Healthcare': ['JNJ', 'PFE', 'UNH'],
            'Finance': ['JPM', 'BAC', 'WFC']
        }
        
        sector_sentiment = {}
        
        for sector, symbols in sectors.items():
            total_sentiment = 0
            count = 0
            
            for symbol in symbols:
                news = self.get_stock_news(symbol, 3)
                for item in news:
                    total_sentiment += item['sentiment']
                    count += 1
            
            if count > 0:
                avg_sentiment = total_sentiment / count
                sector_sentiment[sector] = {
                    'sentiment_score': round(avg_sentiment, 3),
                    'sentiment_label': self.get_sentiment_label(avg_sentiment),
                    'articles_analyzed': count
                }
        
        return sector_sentiment

# Global instance
market_news_service = MarketNewsService()