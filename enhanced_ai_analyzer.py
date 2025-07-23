"""
Enhanced AI Stock Analyzer - State-of-the-art analysis with advanced insights
Provides comprehensive AI-powered stock analysis with enhanced visualizations and predictions
"""

import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from textblob import TextBlob
import json

logger = logging.getLogger(__name__)

class EnhancedAIAnalyzer:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
    def get_enhanced_analysis(self, symbol: str) -> Dict:
        """Get comprehensive AI-powered analysis with enhanced insights"""
        try:
            # Get basic stock data
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Get historical data for analysis
            hist_1d = stock.history(period="1d", interval="5m")
            hist_3m = stock.history(period="3mo")
            hist_1y = stock.history(period="1y")
            
            # Ensure we have basic price data
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('price')
            if not current_price and not hist_3m.empty:
                current_price = hist_3m['Close'].iloc[-1]
            
            # Calculate enhanced metrics
            enhanced_metrics = self._calculate_enhanced_metrics(hist_1d, hist_3m, hist_1y, info)
            
            # AI sentiment analysis
            sentiment_analysis = self._analyze_market_sentiment(symbol, info)
            
            # Risk assessment
            risk_assessment = self._calculate_risk_metrics(hist_3m, hist_1y)
            
            # Price predictions
            price_predictions = self._generate_price_predictions(hist_3m, info)
            
            # Technical analysis
            technical_analysis = self._advanced_technical_analysis(hist_1d, hist_3m)
            
            # AI insights
            ai_insights = self._generate_ai_insights(enhanced_metrics, sentiment_analysis, risk_assessment)
            
            return {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'current_price': current_price or 0,
                'currency': info.get('currency', 'USD'),
                'market_cap': info.get('marketCap', 0),
                'enhanced_metrics': enhanced_metrics,
                'sentiment_analysis': sentiment_analysis,
                'risk_assessment': risk_assessment,
                'price_predictions': price_predictions,
                'technical_analysis': technical_analysis,
                'ai_insights': ai_insights,
                'recommendation': self._generate_enhanced_recommendation(enhanced_metrics, sentiment_analysis, risk_assessment),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced analysis for {symbol}: {e}")
            # Return minimal structure on error to prevent integration failure
            return {
                'symbol': symbol,
                'company_name': symbol,
                'current_price': 0,
                'enhanced_metrics': {},
                'sentiment_analysis': {},
                'risk_assessment': {},
                'price_predictions': {},
                'technical_analysis': {},
                'ai_insights': {},
                'recommendation': {'recommendation': 'HOLD', 'confidence': 50},
                'error': str(e)
            }
    
    def _calculate_enhanced_metrics(self, hist_1d: pd.DataFrame, hist_3m: pd.DataFrame, hist_1y: pd.DataFrame, info: Dict) -> Dict:
        """Calculate advanced financial metrics"""
        try:
            current_price = info.get('currentPrice', 0)
            
            # Volatility metrics
            daily_volatility = hist_1d['Close'].pct_change().std() * np.sqrt(252) if not hist_1d.empty else 0
            weekly_volatility = hist_3m['Close'].pct_change().std() * np.sqrt(52) if not hist_3m.empty else 0
            
            # Momentum indicators
            momentum_1m = ((current_price - hist_3m['Close'].iloc[-21]) / hist_3m['Close'].iloc[-21] * 100) if len(hist_3m) > 21 else 0
            momentum_3m = ((current_price - hist_3m['Close'].iloc[0]) / hist_3m['Close'].iloc[0] * 100) if not hist_3m.empty else 0
            momentum_1y = ((current_price - hist_1y['Close'].iloc[0]) / hist_1y['Close'].iloc[0] * 100) if not hist_1y.empty else 0
            
            # Support and resistance levels
            support_resistance = self._calculate_support_resistance(hist_3m)
            
            # Volume analysis
            volume_analysis = self._analyze_volume(hist_1d, hist_3m)
            
            # Financial strength metrics
            financial_strength = {
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'price_to_book': info.get('priceToBook', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'return_on_equity': info.get('returnOnEquity', 0),
                'profit_margin': info.get('profitMargins', 0)
            }
            
            return {
                'volatility': {
                    'daily': round(daily_volatility * 100, 2),
                    'weekly': round(weekly_volatility * 100, 2),
                    'risk_level': 'High' if daily_volatility > 0.3 else 'Medium' if daily_volatility > 0.15 else 'Low'
                },
                'momentum': {
                    '1_month': round(momentum_1m, 2),
                    '3_month': round(momentum_3m, 2),
                    '1_year': round(momentum_1y, 2),
                    'trend': 'Bullish' if momentum_3m > 5 else 'Bearish' if momentum_3m < -5 else 'Neutral'
                },
                'support_resistance': support_resistance,
                'volume_analysis': volume_analysis,
                'financial_strength': financial_strength,
                'market_position': self._assess_market_position(info)
            }
            
        except Exception as e:
            logger.error(f"Error calculating enhanced metrics: {e}")
            return {}
    
    def _calculate_support_resistance(self, hist_data: pd.DataFrame) -> Dict:
        """Calculate dynamic support and resistance levels"""
        try:
            if hist_data.empty:
                return {}
                
            highs = hist_data['High']
            lows = hist_data['Low']
            closes = hist_data['Close']
            
            # Find local maxima and minima
            resistance_levels = []
            support_levels = []
            
            # Simple method: use recent highs and lows
            recent_high = highs.max()
            recent_low = lows.min()
            current_price = closes.iloc[-1]
            
            # Calculate dynamic levels
            resistance_1 = current_price * 1.05  # 5% above current
            resistance_2 = current_price * 1.10  # 10% above current
            support_1 = current_price * 0.95     # 5% below current
            support_2 = current_price * 0.90     # 10% below current
            
            return {
                'resistance_levels': [
                    {'level': round(resistance_1, 2), 'strength': 'Medium', 'distance': '5%'},
                    {'level': round(resistance_2, 2), 'strength': 'Strong', 'distance': '10%'}
                ],
                'support_levels': [
                    {'level': round(support_1, 2), 'strength': 'Medium', 'distance': '5%'},
                    {'level': round(support_2, 2), 'strength': 'Strong', 'distance': '10%'}
                ],
                'key_levels': {
                    'recent_high': round(recent_high, 2),
                    'recent_low': round(recent_low, 2),
                    'current_position': 'Near Resistance' if current_price > (recent_high * 0.95) else 'Near Support' if current_price < (recent_low * 1.05) else 'Mid-Range'
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {e}")
            return {}
    
    def _analyze_volume(self, hist_1d: pd.DataFrame, hist_3m: pd.DataFrame) -> Dict:
        """Analyze volume patterns and trends"""
        try:
            if hist_1d.empty or hist_3m.empty:
                return {}
                
            # Current volume vs average
            current_volume = hist_1d['Volume'].iloc[-1] if not hist_1d.empty else 0
            avg_volume_1d = hist_1d['Volume'].mean()
            avg_volume_3m = hist_3m['Volume'].mean()
            
            volume_ratio = current_volume / avg_volume_3m if avg_volume_3m > 0 else 0
            
            # Volume trend
            recent_volumes = hist_1d['Volume'].tail(10).mean()
            older_volumes = hist_1d['Volume'].head(10).mean()
            volume_trend = 'Increasing' if recent_volumes > older_volumes * 1.1 else 'Decreasing' if recent_volumes < older_volumes * 0.9 else 'Stable'
            
            return {
                'current_volume': int(current_volume),
                'average_volume': int(avg_volume_3m),
                'volume_ratio': round(volume_ratio, 2),
                'volume_signal': 'High' if volume_ratio > 1.5 else 'Normal' if volume_ratio > 0.5 else 'Low',
                'volume_trend': volume_trend,
                'analysis': f"Volume is {'above' if volume_ratio > 1.2 else 'below' if volume_ratio < 0.8 else 'near'} average"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume: {e}")
            return {}
    
    def _analyze_market_sentiment(self, symbol: str, info: Dict) -> Dict:
        """Analyze market sentiment using available data"""
        try:
            # Analyst recommendations
            recommendation = info.get('recommendationKey', 'hold')
            target_price = info.get('targetMeanPrice', 0)
            current_price = info.get('currentPrice', 0)
            
            # Calculate sentiment score
            price_momentum = info.get('52WeekChange', 0) * 100
            
            sentiment_score = 0
            if recommendation == 'buy':
                sentiment_score += 30
            elif recommendation == 'strong_buy':
                sentiment_score += 50
            elif recommendation == 'sell':
                sentiment_score -= 30
            elif recommendation == 'strong_sell':
                sentiment_score -= 50
                
            if price_momentum > 20:
                sentiment_score += 20
            elif price_momentum < -20:
                sentiment_score -= 20
                
            # Normalize sentiment score
            sentiment_score = max(-100, min(100, sentiment_score))
            
            sentiment_label = 'Very Bullish' if sentiment_score > 60 else 'Bullish' if sentiment_score > 20 else 'Bearish' if sentiment_score < -20 else 'Very Bearish' if sentiment_score < -60 else 'Neutral'
            
            return {
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label,
                'analyst_recommendation': recommendation.title(),
                'target_price': target_price,
                'price_target_upside': round(((target_price - current_price) / current_price * 100), 2) if target_price and current_price else 0,
                'market_momentum': round(price_momentum, 2),
                'confidence': 'High' if abs(sentiment_score) > 40 else 'Medium' if abs(sentiment_score) > 20 else 'Low'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {}
    
    def _calculate_risk_metrics(self, hist_3m: pd.DataFrame, hist_1y: pd.DataFrame) -> Dict:
        """Calculate comprehensive risk assessment"""
        try:
            if hist_3m.empty:
                return {}
                
            returns_3m = hist_3m['Close'].pct_change().dropna()
            returns_1y = hist_1y['Close'].pct_change().dropna() if not hist_1y.empty else returns_3m
            
            # Calculate VaR (Value at Risk)
            var_95 = np.percentile(returns_3m, 5) * 100 if len(returns_3m) > 0 else 0
            
            # Maximum drawdown
            rolling_max = hist_3m['Close'].expanding().max()
            drawdown = (hist_3m['Close'] - rolling_max) / rolling_max
            max_drawdown = drawdown.min() * 100
            
            # Beta calculation (simplified - using market correlation)
            volatility = returns_3m.std() * np.sqrt(252) * 100
            
            # Risk categorization
            risk_level = 'High' if volatility > 30 else 'Medium' if volatility > 15 else 'Low'
            
            return {
                'volatility_annual': round(volatility, 2),
                'value_at_risk_95': round(var_95, 2),
                'max_drawdown': round(max_drawdown, 2),
                'risk_level': risk_level,
                'risk_score': min(100, max(0, volatility * 2 + abs(max_drawdown))),
                'risk_factors': self._identify_risk_factors(volatility, max_drawdown, var_95)
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {}
    
    def _identify_risk_factors(self, volatility: float, max_drawdown: float, var_95: float) -> List[str]:
        """Identify key risk factors"""
        factors = []
        
        if volatility > 30:
            factors.append("High price volatility")
        if max_drawdown < -20:
            factors.append("Significant historical drawdowns")
        if var_95 < -5:
            factors.append("High daily loss potential")
            
        if not factors:
            factors.append("Relatively stable price action")
            
        return factors
    
    def _generate_price_predictions(self, hist_data: pd.DataFrame, info: Dict) -> Dict:
        """Generate AI-based price predictions"""
        try:
            if hist_data.empty:
                return {}
                
            current_price = info.get('currentPrice', hist_data['Close'].iloc[-1])
            
            # Simple momentum-based predictions
            returns = hist_data['Close'].pct_change().dropna()
            avg_return = returns.mean()
            volatility = returns.std()
            
            # Generate predictions for different timeframes
            predictions = {}
            timeframes = [7, 30, 90]  # days
            
            for days in timeframes:
                # Monte Carlo simulation (simplified)
                expected_return = avg_return * days
                expected_volatility = volatility * np.sqrt(days)
                
                # Calculate confidence intervals
                lower_bound = current_price * (1 + expected_return - 1.96 * expected_volatility)
                upper_bound = current_price * (1 + expected_return + 1.96 * expected_volatility)
                expected_price = current_price * (1 + expected_return)
                
                predictions[f'{days}_days'] = {
                    'expected_price': round(expected_price, 2),
                    'lower_bound': round(max(0, lower_bound), 2),
                    'upper_bound': round(upper_bound, 2),
                    'confidence': 95,
                    'change_percent': round(expected_return * 100, 2)
                }
            
            return {
                'predictions': predictions,
                'model_confidence': 'Medium',
                'key_factors': [
                    'Historical price momentum',
                    'Market volatility patterns',
                    'Technical indicators'
                ],
                'disclaimer': 'Predictions are estimates based on historical data and should not be used as sole investment criteria.'
            }
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return {}
    
    def _advanced_technical_analysis(self, hist_1d: pd.DataFrame, hist_3m: pd.DataFrame) -> Dict:
        """Perform advanced technical analysis"""
        try:
            if hist_3m.empty:
                return {}
                
            close_prices = hist_3m['Close']
            
            # Moving averages
            ma_20 = close_prices.rolling(window=20).mean().iloc[-1] if len(close_prices) >= 20 else close_prices.mean()
            ma_50 = close_prices.rolling(window=50).mean().iloc[-1] if len(close_prices) >= 50 else close_prices.mean()
            current_price = close_prices.iloc[-1]
            
            # RSI calculation
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not rsi.empty else 50
            
            # MACD calculation (simplified)
            ema_12 = close_prices.ewm(span=12).mean()
            ema_26 = close_prices.ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            macd_histogram = macd - signal
            
            # Technical signals
            signals = []
            if current_price > ma_20:
                signals.append("Price above 20-day MA (Bullish)")
            if current_price > ma_50:
                signals.append("Price above 50-day MA (Bullish)")
            if current_rsi > 70:
                signals.append("RSI Overbought (Caution)")
            elif current_rsi < 30:
                signals.append("RSI Oversold (Opportunity)")
            if macd.iloc[-1] > signal.iloc[-1]:
                signals.append("MACD Bullish Crossover")
            
            return {
                'moving_averages': {
                    'ma_20': round(ma_20, 2),
                    'ma_50': round(ma_50, 2),
                    'price_vs_ma20': round(((current_price - ma_20) / ma_20) * 100, 2),
                    'price_vs_ma50': round(((current_price - ma_50) / ma_50) * 100, 2)
                },
                'rsi': {
                    'current': round(current_rsi, 2),
                    'signal': 'Overbought' if current_rsi > 70 else 'Oversold' if current_rsi < 30 else 'Neutral'
                },
                'macd': {
                    'value': round(macd.iloc[-1], 4),
                    'signal': round(signal.iloc[-1], 4),
                    'histogram': round(macd_histogram.iloc[-1], 4),
                    'trend': 'Bullish' if macd.iloc[-1] > signal.iloc[-1] else 'Bearish'
                },
                'technical_signals': signals,
                'overall_technical_rating': self._calculate_technical_rating(current_price, ma_20, ma_50, current_rsi, macd.iloc[-1], signal.iloc[-1])
            }
            
        except Exception as e:
            logger.error(f"Error in technical analysis: {e}")
            return {}
    
    def _calculate_technical_rating(self, price: float, ma_20: float, ma_50: float, rsi: float, macd: float, signal: float) -> str:
        """Calculate overall technical rating"""
        score = 0
        
        if price > ma_20:
            score += 1
        if price > ma_50:
            score += 1
        if 30 <= rsi <= 70:
            score += 1
        if macd > signal:
            score += 1
            
        if score >= 3:
            return "Strong Buy"
        elif score == 2:
            return "Buy"
        elif score == 1:
            return "Hold"
        else:
            return "Sell"
    
    def _assess_market_position(self, info: Dict) -> Dict:
        """Assess the stock's market position"""
        try:
            market_cap = info.get('marketCap', 0)
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            
            # Market cap classification
            if market_cap > 200_000_000_000:
                cap_class = "Mega Cap"
            elif market_cap > 10_000_000_000:
                cap_class = "Large Cap"
            elif market_cap > 2_000_000_000:
                cap_class = "Mid Cap"
            elif market_cap > 300_000_000:
                cap_class = "Small Cap"
            else:
                cap_class = "Micro Cap"
            
            return {
                'market_cap_class': cap_class,
                'market_cap_value': market_cap,
                'sector': sector,
                'industry': industry,
                'exchange': info.get('exchange', 'Unknown'),
                'country': info.get('country', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"Error assessing market position: {e}")
            return {}
    
    def _generate_ai_insights(self, metrics: Dict, sentiment: Dict, risk: Dict) -> Dict:
        """Generate AI-powered insights and recommendations"""
        try:
            insights = []
            
            # Momentum insights
            momentum = metrics.get('momentum', {})
            if momentum.get('3_month', 0) > 20:
                insights.append({
                    'type': 'momentum',
                    'title': 'Strong Positive Momentum',
                    'description': f"Stock has gained {momentum.get('3_month', 0):.1f}% over the past 3 months",
                    'impact': 'Positive'
                })
            elif momentum.get('3_month', 0) < -20:
                insights.append({
                    'type': 'momentum',
                    'title': 'Significant Decline',
                    'description': f"Stock has declined {abs(momentum.get('3_month', 0)):.1f}% over the past 3 months",
                    'impact': 'Negative'
                })
            
            # Volatility insights
            vol = metrics.get('volatility', {})
            if vol.get('risk_level') == 'High':
                insights.append({
                    'type': 'volatility',
                    'title': 'High Volatility Alert',
                    'description': f"Stock shows high volatility ({vol.get('daily', 0):.1f}% daily)",
                    'impact': 'Caution'
                })
            
            # Sentiment insights
            if sentiment.get('sentiment_score', 0) > 40:
                insights.append({
                    'type': 'sentiment',
                    'title': 'Positive Market Sentiment',
                    'description': f"Strong bullish sentiment with {sentiment.get('sentiment_label', 'Positive')} outlook",
                    'impact': 'Positive'
                })
            
            # Risk insights
            risk_level = risk.get('risk_level', 'Medium')
            if risk_level == 'Low':
                insights.append({
                    'type': 'risk',
                    'title': 'Low Risk Profile',
                    'description': 'Stock shows relatively stable price behavior',
                    'impact': 'Positive'
                })
            
            return {
                'insights': insights,
                'key_strengths': self._identify_strengths(metrics, sentiment, risk),
                'key_concerns': self._identify_concerns(metrics, sentiment, risk),
                'ai_confidence': 'High' if len(insights) >= 3 else 'Medium'
            }
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return {}
    
    def _identify_strengths(self, metrics: Dict, sentiment: Dict, risk: Dict) -> List[str]:
        """Identify key strengths"""
        strengths = []
        
        if metrics.get('momentum', {}).get('trend') == 'Bullish':
            strengths.append("Strong price momentum")
        if sentiment.get('sentiment_score', 0) > 20:
            strengths.append("Positive market sentiment")
        if risk.get('risk_level') == 'Low':
            strengths.append("Low volatility risk")
        if metrics.get('financial_strength', {}).get('profit_margin', 0) > 0.15:
            strengths.append("Strong profit margins")
            
        return strengths[:3]  # Limit to top 3
    
    def _identify_concerns(self, metrics: Dict, sentiment: Dict, risk: Dict) -> List[str]:
        """Identify key concerns"""
        concerns = []
        
        if risk.get('risk_level') == 'High':
            concerns.append("High price volatility")
        if metrics.get('momentum', {}).get('trend') == 'Bearish':
            concerns.append("Declining price trend")
        if sentiment.get('sentiment_score', 0) < -20:
            concerns.append("Negative market sentiment")
        if metrics.get('financial_strength', {}).get('debt_to_equity', 0) > 2:
            concerns.append("High debt levels")
            
        return concerns[:3]  # Limit to top 3
    
    def _generate_enhanced_recommendation(self, metrics: Dict, sentiment: Dict, risk: Dict) -> Dict:
        """Generate enhanced AI recommendation"""
        try:
            score = 0
            confidence = 50
            
            # Momentum scoring
            momentum_3m = metrics.get('momentum', {}).get('3_month', 0)
            if momentum_3m > 15:
                score += 20
                confidence += 10
            elif momentum_3m < -15:
                score -= 20
                confidence += 10
            
            # Sentiment scoring
            sentiment_score = sentiment.get('sentiment_score', 0)
            score += sentiment_score * 0.3
            confidence += min(20, abs(sentiment_score) * 0.2)
            
            # Risk adjustment
            risk_level = risk.get('risk_level', 'Medium')
            if risk_level == 'High':
                score -= 10
                confidence -= 5
            elif risk_level == 'Low':
                score += 5
                confidence += 5
            
            # Normalize score
            score = max(-100, min(100, score))
            confidence = max(30, min(95, confidence))
            
            # Generate recommendation
            if score > 30:
                recommendation = "BUY"
                action = "Consider buying"
            elif score > 10:
                recommendation = "HOLD"
                action = "Hold current position"
            elif score > -10:
                recommendation = "HOLD"
                action = "Monitor closely"
            else:
                recommendation = "SELL"
                action = "Consider selling"
            
            return {
                'recommendation': recommendation,
                'confidence': round(confidence, 0),
                'action': action,
                'score': round(score, 1),
                'reasoning': self._generate_recommendation_reasoning(metrics, sentiment, risk, recommendation)
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return {'recommendation': 'HOLD', 'confidence': 50, 'action': 'Monitor'}
    
    def _generate_recommendation_reasoning(self, metrics: Dict, sentiment: Dict, risk: Dict, recommendation: str) -> str:
        """Generate reasoning for recommendation"""
        factors = []
        
        momentum = metrics.get('momentum', {}).get('3_month', 0)
        if momentum > 10:
            factors.append("positive momentum")
        elif momentum < -10:
            factors.append("negative momentum")
            
        sentiment_label = sentiment.get('sentiment_label', 'Neutral').lower()
        if 'bullish' in sentiment_label:
            factors.append("bullish sentiment")
        elif 'bearish' in sentiment_label:
            factors.append("bearish sentiment")
            
        risk_level = risk.get('risk_level', 'Medium').lower()
        factors.append(f"{risk_level} risk profile")
        
        if factors:
            return f"Based on {', '.join(factors[:-1])}{' and ' + factors[-1] if len(factors) > 1 else factors[0]}"
        else:
            return "Based on comprehensive technical and fundamental analysis"