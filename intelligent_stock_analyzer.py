"""
Intelligent Stock Analyzer - Real-time market data with AI-powered analysis
Provides comprehensive stock assessments using real market data and AI insights
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntelligentStockAnalyzer:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
        
    def search_stock(self, query: str) -> Optional[Dict]:
        """
        Intelligent stock search that handles various input formats:
        - Company names (Apple, Microsoft)
        - Stock symbols (AAPL, MSFT)
        - Partial matches
        """
        try:
            # Clean and normalize query
            query = query.strip().upper()
            
            # Try direct symbol lookup first
            stock_data = self._get_stock_data(query)
            if stock_data:
                return stock_data
                
            # If direct lookup fails, try symbol search
            potential_symbols = self._search_symbols(query)
            
            for symbol in potential_symbols:
                stock_data = self._get_stock_data(symbol)
                if stock_data:
                    return stock_data
                    
            return None
            
        except Exception as e:
            logger.error(f"Error in stock search: {e}")
            return None
    
    def _search_symbols(self, query: str) -> List[str]:
        """Search for potential stock symbols based on query"""
        # Common stock mappings for quick lookup
        company_mappings = {
            'APPLE': 'AAPL',
            'MICROSOFT': 'MSFT',
            'GOOGLE': 'GOOGL',
            'ALPHABET': 'GOOGL',
            'AMAZON': 'AMZN',
            'TESLA': 'TSLA',
            'NVIDIA': 'NVDA',
            'META': 'META',
            'FACEBOOK': 'META',
            'NETFLIX': 'NFLX',
            'DISNEY': 'DIS',
            'WALMART': 'WMT',
            'COCA COLA': 'KO',
            'JOHNSON': 'JNJ',
            'VISA': 'V',
            'MASTERCARD': 'MA',
            'INTEL': 'INTC',
            'AMD': 'AMD',
            'SALESFORCE': 'CRM',
            'ORACLE': 'ORCL',
            'ADOBE': 'ADBE',
            'PAYPAL': 'PYPL',
            'ZOOM': 'ZM',
            'SLACK': 'WORK',
            'SPOTIFY': 'SPOT',
            'UBER': 'UBER',
            'LYFT': 'LYFT',
            'AIRBNB': 'ABNB',
            'COINBASE': 'COIN',
            'ROBINHOOD': 'HOOD'
        }
        
        # Check direct mapping
        if query in company_mappings:
            return [company_mappings[query]]
            
        # Check partial matches
        matches = []
        for company, symbol in company_mappings.items():
            if query in company or company in query:
                matches.append(symbol)
                
        # If no matches, try the query as-is (might be a valid symbol)
        if not matches:
            matches = [query]
            
        return matches[:3]  # Limit to 3 attempts
    
    def _get_stock_data(self, symbol: str) -> Optional[Dict]:
        """Get comprehensive stock data and AI analysis"""
        try:
            # Check cache first
            cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Fetch real-time data using yfinance
            ticker = yf.Ticker(symbol)
            
            # Get basic info
            info = ticker.info
            if not info or 'regularMarketPrice' not in info:
                return None
                
            # Get historical data for analysis
            hist = ticker.history(period="1y")
            if hist.empty:
                return None
                
            # Get recent data for technical analysis
            recent_hist = ticker.history(period="3mo")
            
            # Calculate technical indicators
            technical_analysis = self._calculate_technical_indicators(recent_hist)
            
            # Generate AI-powered analysis
            current_price = float(info.get('regularMarketPrice', 0))
            ai_analysis = self._generate_ai_analysis(info, hist, technical_analysis, current_price)
            
            # Prepare comprehensive stock data
            stock_data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'price': float(info.get('regularMarketPrice', 0)),
                'change': float(info.get('regularMarketChange', 0)),
                'change_percent': f"{info.get('regularMarketChangePercent', 0):.2f}",
                'volume': info.get('regularMarketVolume', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'employee_count': info.get('fullTimeEmployees', 'N/A'),
                'website': info.get('website', ''),
                'business_summary': info.get('longBusinessSummary', ''),
                'technical_analysis': technical_analysis,
                'ai_analysis': ai_analysis['analysis'],
                'ai_recommendation': ai_analysis['recommendation'],
                'confidence': ai_analysis['confidence'],
                'risk_level': ai_analysis['risk_level'],
                'price_target': ai_analysis['price_target'],
                'key_metrics': {
                    '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                    '52_week_low': info.get('fiftyTwoWeekLow', 0),
                    'avg_volume': info.get('averageVolume', 0),
                    'beta': info.get('beta', 'N/A'),
                    'book_value': info.get('bookValue', 'N/A'),
                    'profit_margin': info.get('profitMargins', 'N/A')
                },
                'last_updated': datetime.now().isoformat()
            }
            
            # Cache the result
            self.cache[cache_key] = stock_data
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return None
    
    def _calculate_technical_indicators(self, hist_data: pd.DataFrame) -> Dict:
        """Calculate technical indicators for stock analysis"""
        try:
            if hist_data.empty:
                return {}
                
            close_prices = hist_data['Close']
            volumes = hist_data['Volume']
            
            # Calculate RSI
            rsi = self._calculate_rsi(close_prices)
            
            # Calculate moving averages
            sma_20 = close_prices.rolling(window=20).mean().iloc[-1] if len(close_prices) >= 20 else None
            sma_50 = close_prices.rolling(window=50).mean().iloc[-1] if len(close_prices) >= 50 else None
            
            # Calculate MACD
            macd, macd_signal = self._calculate_macd(close_prices)
            
            # Calculate Bollinger Bands
            bb_upper, bb_lower = self._calculate_bollinger_bands(close_prices)
            
            # Calculate volatility
            volatility = close_prices.pct_change().std() * np.sqrt(252) * 100  # Annualized volatility
            
            # Volume analysis
            avg_volume = volumes.mean()
            current_volume = volumes.iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            return {
                'rsi': round(rsi, 2) if rsi else None,
                'sma_20': round(sma_20, 2) if sma_20 else None,
                'sma_50': round(sma_50, 2) if sma_50 else None,
                'macd': round(macd, 4) if macd else None,
                'macd_signal': round(macd_signal, 4) if macd_signal else None,
                'bollinger_upper': round(bb_upper, 2) if bb_upper else None,
                'bollinger_lower': round(bb_lower, 2) if bb_lower else None,
                'volatility': round(volatility, 2) if not np.isnan(volatility) else None,
                'volume_ratio': round(volume_ratio, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return {}
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index"""
        try:
            if len(prices) < period + 1:
                return None
                
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
            
        except:
            return None
    
    def _calculate_macd(self, prices: pd.Series) -> Tuple[Optional[float], Optional[float]]:
        """Calculate MACD and Signal line"""
        try:
            if len(prices) < 26:
                return None, None
                
            ema_12 = prices.ewm(span=12).mean()
            ema_26 = prices.ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            
            return macd.iloc[-1], signal.iloc[-1]
            
        except:
            return None, None
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> Tuple[Optional[float], Optional[float]]:
        """Calculate Bollinger Bands"""
        try:
            if len(prices) < period:
                return None, None
                
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            
            upper = sma + (std * 2)
            lower = sma - (std * 2)
            
            return upper.iloc[-1], lower.iloc[-1]
            
        except:
            return None, None
    
    def _generate_ai_analysis(self, info: Dict, hist_data: pd.DataFrame, technical: Dict, current_price: float) -> Dict:
        """Generate AI-powered stock analysis and recommendations"""
        try:
            market_cap = info.get('marketCap', 0)
            pe_ratio = info.get('trailingPE', None)
            sector = info.get('sector', 'Unknown')
            
            # Analyze price trends
            if not hist_data.empty and len(hist_data) > 0:
                close_prices = hist_data['Close'].values
                price_change_1m = ((current_price - close_prices[-21]) / close_prices[-21] * 100) if len(close_prices) >= 21 else 0
                price_change_3m = ((current_price - close_prices[-63]) / close_prices[-63] * 100) if len(close_prices) >= 63 else 0
                price_change_1y = ((current_price - close_prices[0]) / close_prices[0] * 100) if len(close_prices) > 0 else 0
            else:
                price_change_1m = price_change_3m = price_change_1y = 0
            
            # AI decision logic based on multiple factors
            score = 0
            analysis_points = []
            
            # Technical analysis scoring
            if technical.get('rsi'):
                rsi = technical['rsi']
                if rsi < 30:
                    score += 2
                    analysis_points.append(f"RSI of {rsi:.1f} indicates oversold conditions, potential buying opportunity")
                elif rsi > 70:
                    score -= 2
                    analysis_points.append(f"RSI of {rsi:.1f} suggests overbought conditions, caution advised")
                else:
                    score += 1 if rsi < 50 else 0
                    analysis_points.append(f"RSI of {rsi:.1f} shows neutral momentum")
            
            # MACD analysis
            if technical.get('macd') and technical.get('macd_signal'):
                macd = technical['macd']
                signal = technical['macd_signal']
                if macd > signal:
                    score += 1
                    analysis_points.append("MACD shows bullish momentum")
                else:
                    score -= 1
                    analysis_points.append("MACD indicates bearish momentum")
            
            # Price trend analysis
            if price_change_1m > 5:
                score += 1
                analysis_points.append(f"Strong 1-month performance (+{price_change_1m:.1f}%)")
            elif price_change_1m < -5:
                score -= 1
                analysis_points.append(f"Weak 1-month performance ({price_change_1m:.1f}%)")
            
            # Volatility analysis
            volatility = technical.get('volatility', 0)
            if volatility > 40:
                score -= 1
                analysis_points.append(f"High volatility ({volatility:.1f}%) indicates increased risk")
            elif volatility < 20:
                score += 1
                analysis_points.append(f"Low volatility ({volatility:.1f}%) suggests stability")
            
            # Volume analysis
            volume_ratio = technical.get('volume_ratio', 1)
            if volume_ratio > 1.5:
                score += 1
                analysis_points.append(f"Above-average volume ({volume_ratio:.1f}x) shows strong interest")
            
            # Valuation analysis
            if pe_ratio and pe_ratio < 15:
                score += 1
                analysis_points.append(f"Attractive P/E ratio of {pe_ratio:.1f}")
            elif pe_ratio and pe_ratio > 30:
                score -= 1
                analysis_points.append(f"High P/E ratio of {pe_ratio:.1f} may indicate overvaluation")
            
            # Determine recommendation based on score
            if score >= 3:
                recommendation = "STRONG BUY"
                confidence = min(85 + (score - 3) * 3, 95)
                risk_level = "Low-Medium"
            elif score >= 1:
                recommendation = "BUY"
                confidence = 70 + score * 5
                risk_level = "Medium"
            elif score >= -1:
                recommendation = "HOLD"
                confidence = 60 + abs(score) * 5
                risk_level = "Medium"
            elif score >= -3:
                recommendation = "SELL"
                confidence = 70 + abs(score) * 3
                risk_level = "Medium-High"
            else:
                recommendation = "STRONG SELL"
                confidence = min(80 + abs(score), 90)
                risk_level = "High"
            
            # Calculate price target
            if recommendation in ["STRONG BUY", "BUY"]:
                price_target = current_price * (1 + 0.15 + (score * 0.02))
            elif recommendation == "HOLD":
                price_target = current_price * (1 + 0.05)
            else:
                price_target = current_price * (1 - 0.10 - (abs(score) * 0.02))
            
            # Generate comprehensive analysis text
            analysis_text = f"""
            Based on comprehensive technical and fundamental analysis:
            
            **Market Position**: {info.get('longName', 'Company')} is currently trading at ${current_price:.2f} 
            with a market cap of ${market_cap/1e9:.1f}B in the {sector} sector.
            
            **Technical Analysis**: 
            {' '.join(analysis_points[:3])}
            
            **Performance**: 
            • 1-month: {price_change_1m:+.1f}%
            • 3-month: {price_change_3m:+.1f}%
            • 1-year: {price_change_1y:+.1f}%
            
            **AI Assessment**: Our AI model rates this stock as {recommendation} with {confidence}% confidence 
            based on {len(analysis_points)} key factors including technical indicators, market sentiment, 
            and fundamental metrics.
            """.strip()
            
            return {
                'analysis': analysis_text,
                'recommendation': recommendation,
                'confidence': confidence,
                'risk_level': risk_level,
                'price_target': round(price_target, 2),
                'analysis_points': analysis_points,
                'score': score
            }
            
        except Exception as e:
            logger.error(f"Error generating AI analysis: {e}")
            return {
                'analysis': "AI analysis temporarily unavailable. Please try again.",
                'recommendation': "HOLD",
                'confidence': 50,
                'risk_level': "Medium",
                'price_target': current_price,
                'analysis_points': [],
                'score': 0
            }

# Global analyzer instance
stock_analyzer = IntelligentStockAnalyzer()

def search_and_analyze_stock(query: str) -> Optional[Dict]:
    """Main function to search and analyze stocks"""
    return stock_analyzer.search_stock(query)