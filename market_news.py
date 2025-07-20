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
        # For demonstration, provide realistic market news samples
        # In production, this would connect to multiple real news sources
        sample_news = [
            {
                'title': 'Federal Reserve Holds Interest Rates Steady at 5.25-5.50%',
                'summary': 'The Federal Reserve announced it will maintain current interest rates, citing ongoing concerns about inflation and labor market conditions. Fed Chair Jerome Powell indicated future decisions will be data-dependent, with particular focus on employment figures and consumer price index trends.',
                'url': 'https://finance.yahoo.com/news/fed-rates-decision',
                'published': int(time.time() - 3600),  # 1 hour ago
                'source': 'Federal Reserve',
                'category': 'Market Overview',
                'sentiment': -0.1,
                'sentiment_label': 'Neutral'
            },
            {
                'title': 'S&P 500 Reaches New All-Time High Amid Tech Sector Rally',
                'summary': 'The S&P 500 index closed at a record high today, driven by strong performance in technology stocks. Major gainers included semiconductor companies and AI-focused firms, with investors showing renewed confidence in the tech sector outlook for the remainder of 2025.',
                'url': 'https://finance.yahoo.com/news/sp500-record-high',
                'published': int(time.time() - 7200),  # 2 hours ago
                'source': 'MarketWatch',
                'category': 'Market Overview',
                'sentiment': 0.6,
                'sentiment_label': 'Positive'
            },
            {
                'title': 'Oil Prices Surge on Middle East Tensions and Supply Concerns',
                'summary': 'Crude oil futures jumped 4.2% today following geopolitical developments in the Middle East and reports of potential supply disruptions. Brent crude reached $87.50 per barrel, while WTI crude settled at $83.25, marking the highest levels in six months.',
                'url': 'https://finance.yahoo.com/news/oil-prices-surge',
                'published': int(time.time() - 10800),  # 3 hours ago
                'source': 'Reuters',
                'category': 'Market Overview',
                'sentiment': 0.2,
                'sentiment_label': 'Positive'
            },
            {
                'title': 'Dollar Strengthens Against Major Currencies on Economic Data',
                'summary': 'The U.S. dollar gained against major trading partners following better-than-expected economic data releases. Strong retail sales and jobless claims figures boosted investor confidence in the American economy, with the DXY index climbing 0.8% to 104.5.',
                'url': 'https://finance.yahoo.com/news/dollar-strengthens',
                'published': int(time.time() - 14400),  # 4 hours ago
                'source': 'Bloomberg',
                'category': 'Market Overview',
                'sentiment': 0.4,
                'sentiment_label': 'Positive'
            },
            {
                'title': 'European Markets Mixed as ECB Policy Decision Looms',
                'summary': 'European stock markets showed mixed performance ahead of tomorrow\'s European Central Bank policy announcement. The FTSE 100 gained 0.3% while the DAX fell 0.2%. Investors are weighing inflation data against economic growth concerns across the eurozone.',
                'url': 'https://finance.yahoo.com/news/european-markets-mixed',
                'published': int(time.time() - 18000),  # 5 hours ago
                'source': 'Financial Times',
                'category': 'Market Overview',
                'sentiment': -0.1,
                'sentiment_label': 'Neutral'
            },
            {
                'title': 'Cryptocurrency Market Rebounds as Bitcoin Crosses $67,000',
                'summary': 'Bitcoin surged above $67,000 for the first time in three weeks, leading a broader cryptocurrency market recovery. Ethereum also gained 5.8% to reach $3,450, with analysts citing renewed institutional interest and positive regulatory developments as key drivers.',
                'url': 'https://finance.yahoo.com/news/crypto-rebound',
                'published': int(time.time() - 21600),  # 6 hours ago
                'source': 'CoinDesk',
                'category': 'Market Overview',
                'sentiment': 0.7,
                'sentiment_label': 'Positive'
            }
        ]
        
        return sample_news[:6]  # Return 6 articles
    
    def get_trending_stocks_news(self) -> List[Dict[str, Any]]:
        """Get news for trending stocks"""
        # Provide realistic trending stock news samples
        sample_trending_news = [
            {
                'title': 'Apple Reports Strong iPhone 16 Sales in Q1 Amid AI Feature Rollout',
                'summary': 'Apple\'s latest quarterly earnings beat expectations, with iPhone 16 sales driving revenue growth. The new AI features have boosted consumer interest, leading to a 12% increase in smartphone sales compared to the previous quarter.',
                'url': 'https://finance.yahoo.com/news/apple-earnings-q1',
                'published': int(time.time() - 1800),  # 30 minutes ago
                'source': 'Apple Inc.',
                'category': 'AAPL News',
                'sentiment': 0.5,
                'sentiment_label': 'Positive'
            },
            {
                'title': 'Tesla Stock Surges on Record Delivery Numbers for Model Y',
                'summary': 'Tesla announced record delivery numbers for the Model Y, exceeding analyst expectations by 15%. The electric vehicle giant delivered 485,000 vehicles globally this quarter, driving stock price up 8% in after-hours trading.',
                'url': 'https://finance.yahoo.com/news/tesla-deliveries-record',
                'published': int(time.time() - 3600),  # 1 hour ago
                'source': 'Tesla Inc.',
                'category': 'TSLA News',
                'sentiment': 0.7,
                'sentiment_label': 'Positive'
            },
            {
                'title': 'NVIDIA Announces New AI Chip Architecture for 2025',
                'summary': 'NVIDIA unveiled its next-generation AI chip architecture, promising 40% better performance for machine learning workloads. The announcement has strengthened the company\'s position in the rapidly growing AI infrastructure market.',
                'url': 'https://finance.yahoo.com/news/nvidia-ai-chip-2025',
                'published': int(time.time() - 5400),  # 1.5 hours ago
                'source': 'NVIDIA Corp.',
                'category': 'NVDA News',
                'sentiment': 0.6,
                'sentiment_label': 'Positive'
            },
            {
                'title': 'Google Cloud Revenue Grows 35% as AI Services Gain Traction',
                'summary': 'Alphabet\'s Google Cloud division reported 35% year-over-year revenue growth, driven by increased adoption of AI and machine learning services. The strong performance helped offset slower growth in traditional advertising revenue.',
                'url': 'https://finance.yahoo.com/news/google-cloud-growth',
                'published': int(time.time() - 7200),  # 2 hours ago
                'source': 'Alphabet Inc.',
                'category': 'GOOGL News',
                'sentiment': 0.4,
                'sentiment_label': 'Positive'
            },
            {
                'title': 'Microsoft Teams Integration with AI Copilot Drives Enterprise Sales',
                'summary': 'Microsoft reported strong enterprise sales growth driven by the integration of AI Copilot features into Teams and Office 365. The company added 50,000 new enterprise customers this quarter, boosting subscription revenue.',
                'url': 'https://finance.yahoo.com/news/microsoft-teams-ai-growth',
                'published': int(time.time() - 9000),  # 2.5 hours ago
                'source': 'Microsoft Corp.',
                'category': 'MSFT News',
                'sentiment': 0.5,
                'sentiment_label': 'Positive'
            },
            {
                'title': 'Amazon Prime Day 2025 Sets New Sales Records Globally',
                'summary': 'Amazon announced that Prime Day 2025 achieved record-breaking sales figures, with total revenue exceeding $14 billion globally. Strong performance in electronics and home goods categories drove the impressive results.',
                'url': 'https://finance.yahoo.com/news/amazon-prime-day-records',
                'published': int(time.time() - 10800),  # 3 hours ago
                'source': 'Amazon.com Inc.',
                'category': 'AMZN News',
                'sentiment': 0.6,
                'sentiment_label': 'Positive'
            }
        ]
        
        return sample_trending_news
    
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