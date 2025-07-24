"""
AI Capability Enhancer - Makes our AI features more powerful
Integrates with existing AI engines to provide superior capabilities
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import yfinance as yf
import numpy as np
import pandas as pd
from textblob import TextBlob
import requests
import json

logger = logging.getLogger(__name__)

class AICapabilityEnhancer:
    """
    Enhances existing AI capabilities to create industry-leading features
    Focus: Real-time analysis, predictive insights, opportunity detection
    """
    
    def __init__(self):
        self.market_data_cache = {}
        self.ai_insights_cache = {}
        self.opportunity_patterns = []
        self.risk_models = {}
        
        logger.info("AI Capability Enhancer initialized")
    
    def enhance_stock_analysis(self, symbol: str, base_analysis: Dict, user_strategy: str = None) -> Dict:
        """
        Enhance basic stock analysis with advanced AI capabilities
        """
        try:
            enhanced_analysis = base_analysis.copy()
            
            # Add real-time market intelligence
            market_intelligence = self._get_real_time_intelligence(symbol)
            enhanced_analysis['market_intelligence'] = market_intelligence
            
            # Add predictive insights
            predictions = self._generate_predictions(symbol)
            enhanced_analysis['ai_predictions'] = predictions
            
            # Add opportunity scoring
            opportunity_score = self._calculate_opportunity_score(symbol, user_strategy)
            enhanced_analysis['opportunity_metrics'] = opportunity_score
            
            # Add risk intelligence
            risk_intelligence = self._assess_intelligent_risk(symbol, user_strategy)
            enhanced_analysis['risk_intelligence'] = risk_intelligence
            
            # Add competitive intelligence
            competitive_intel = self._get_competitive_intelligence(symbol)
            enhanced_analysis['competitive_intelligence'] = competitive_intel
            
            # Generate AI confidence with reasoning
            ai_confidence = self._calculate_enhanced_confidence(enhanced_analysis)
            enhanced_analysis['ai_confidence_detailed'] = ai_confidence
            
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"AI enhancement failed for {symbol}: {e}")
            return base_analysis
    
    def get_real_time_opportunities(self, watchlist: List[str] = None, user_strategy: str = None) -> Dict:
        """
        Scan for real-time investment opportunities
        """
        if not watchlist:
            watchlist = self._get_default_watchlist()
        
        opportunities = []
        
        for symbol in watchlist:
            try:
                opportunity = self._scan_symbol_for_opportunities(symbol, user_strategy)
                if opportunity and opportunity.get('score', 0) > 60:
                    opportunities.append(opportunity)
                    
            except Exception as e:
                logger.error(f"Opportunity scan failed for {symbol}: {e}")
                continue
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return {
            'opportunities': opportunities[:10],
            'scan_timestamp': datetime.now().isoformat(),
            'total_scanned': len(watchlist),
            'ai_confidence': self._calculate_scan_confidence(opportunities)
        }
    
    def generate_ai_insights(self, symbol: str, analysis_type: str = 'comprehensive') -> Dict:
        """
        Generate deep AI insights beyond basic analysis
        """
        try:
            insights = {}
            
            # Market psychology analysis
            if analysis_type in ['comprehensive', 'psychology']:
                insights['market_psychology'] = self._analyze_market_psychology(symbol)
            
            # Institutional activity detection
            if analysis_type in ['comprehensive', 'institutional']:
                insights['institutional_signals'] = self._detect_institutional_activity(symbol)
            
            # Momentum analysis
            if analysis_type in ['comprehensive', 'momentum']:
                insights['momentum_analysis'] = self._analyze_momentum_patterns(symbol)
            
            # Volatility intelligence
            if analysis_type in ['comprehensive', 'volatility']:
                insights['volatility_intelligence'] = self._analyze_volatility_patterns(symbol)
            
            # News impact analysis
            if analysis_type in ['comprehensive', 'news']:
                insights['news_impact'] = self._analyze_news_impact(symbol)
            
            return {
                'symbol': symbol,
                'insights': insights,
                'insight_timestamp': datetime.now().isoformat(),
                'insight_confidence': self._calculate_insight_confidence(insights)
            }
            
        except Exception as e:
            logger.error(f"AI insights generation failed for {symbol}: {e}")
            return {'error': str(e)}
    
    def _get_real_time_intelligence(self, symbol: str) -> Dict:
        """Get real-time market intelligence"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get latest data
            hist_1h = ticker.history(period="2d", interval="1h")
            hist_daily = ticker.history(period="30d", interval="1d")
            
            if len(hist_1h) < 5 or len(hist_daily) < 10:
                return {'status': 'insufficient_data'}
            
            # Calculate real-time metrics
            current_price = hist_1h['Close'].iloc[-1]
            price_1h_ago = hist_1h['Close'].iloc[-2]
            volume_trend = self._analyze_volume_trend(hist_1h)
            price_momentum = self._calculate_price_momentum(hist_daily)
            
            return {
                'current_price': round(current_price, 2),
                'hourly_change': round((current_price / price_1h_ago - 1) * 100, 2),
                'volume_trend': volume_trend,
                'price_momentum': price_momentum,
                'market_position': self._determine_market_position(hist_daily),
                'intelligence_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Real-time intelligence failed for {symbol}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _generate_predictions(self, symbol: str) -> Dict:
        """Generate AI-powered predictions"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="3mo", interval="1d")
            
            if len(hist) < 30:
                return {'status': 'insufficient_data'}
            
            # Calculate prediction features
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std()
            trend_strength = self._calculate_trend_strength(hist)
            
            # Simple prediction model (in production, would use ML models)
            current_price = hist['Close'].iloc[-1]
            
            # Predict next day, week, month
            predictions = {
                'next_day': {
                    'direction': 'up' if trend_strength > 0.6 else 'down' if trend_strength < 0.4 else 'sideways',
                    'confidence': min(85, max(35, trend_strength * 100)),
                    'target_price': round(current_price * (1 + returns.mean()), 2)
                },
                'next_week': {
                    'direction': 'up' if trend_strength > 0.55 else 'down' if trend_strength < 0.45 else 'sideways',
                    'confidence': min(75, max(40, trend_strength * 90)),
                    'target_price': round(current_price * (1 + returns.mean() * 5), 2)
                },
                'next_month': {
                    'direction': 'up' if trend_strength > 0.5 else 'down' if trend_strength < 0.5 else 'sideways',
                    'confidence': min(65, max(45, trend_strength * 80)),
                    'target_price': round(current_price * (1 + returns.mean() * 20), 2)
                }
            }
            
            return {
                'predictions': predictions,
                'model_confidence': min(80, max(50, (1 - volatility) * 100)),
                'key_factors': ['Recent momentum', 'Volatility patterns', 'Technical indicators']
            }
            
        except Exception as e:
            logger.error(f"Prediction generation failed for {symbol}: {e}")
            return {'status': 'error'}
    
    def _calculate_opportunity_score(self, symbol: str, user_strategy: str) -> Dict:
        """Calculate comprehensive opportunity score"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="60d", interval="1d")
            
            if len(hist) < 20:
                return {'score': 50, 'confidence': 30}
            
            # Calculate multiple opportunity factors
            factors = {
                'momentum_score': self._calculate_momentum_score(hist),
                'value_score': self._calculate_value_score(symbol),
                'technical_score': self._calculate_technical_score(hist),
                'volume_score': self._calculate_volume_score(hist),
                'volatility_score': self._calculate_volatility_opportunity_score(hist)
            }
            
            # Weight factors based on user strategy
            weights = self._get_strategy_weights(user_strategy)
            
            # Calculate weighted opportunity score
            opportunity_score = sum(factors[factor] * weights.get(factor, 0.2) for factor in factors)
            
            return {
                'score': min(95, max(15, opportunity_score)),
                'factor_breakdown': factors,
                'strategy_alignment': self._assess_strategy_fit(factors, user_strategy),
                'confidence': 75
            }
            
        except Exception as e:
            logger.error(f"Opportunity scoring failed for {symbol}: {e}")
            return {'score': 50, 'confidence': 40}
    
    def _assess_intelligent_risk(self, symbol: str, user_strategy: str) -> Dict:
        """Assess risk using AI intelligence"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="6mo", interval="1d")
            info = ticker.info
            
            if len(hist) < 30:
                return {'risk_level': 'Medium', 'confidence': 40}
            
            # Calculate risk factors
            risk_factors = {
                'volatility_risk': self._calculate_volatility_risk(hist),
                'liquidity_risk': self._calculate_liquidity_risk(hist),
                'market_risk': self._calculate_market_risk(symbol, info),
                'fundamental_risk': self._calculate_fundamental_risk(info),
                'sentiment_risk': self._calculate_sentiment_risk(symbol)
            }
            
            # Calculate composite risk score
            risk_score = np.mean(list(risk_factors.values()))
            
            # Risk level classification
            if risk_score > 75:
                risk_level = 'High'
            elif risk_score > 50:
                risk_level = 'Medium'
            else:
                risk_level = 'Low'
            
            return {
                'risk_level': risk_level,
                'risk_score': round(risk_score, 1),
                'risk_breakdown': risk_factors,
                'mitigation_suggestions': self._generate_risk_mitigation(risk_factors, user_strategy),
                'confidence': 80
            }
            
        except Exception as e:
            logger.error(f"Risk assessment failed for {symbol}: {e}")
            return {'risk_level': 'Medium', 'risk_score': 50}
    
    def _get_competitive_intelligence(self, symbol: str) -> Dict:
        """Get competitive intelligence for the stock"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get sector and industry information
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            
            # Analyze competitive position (simplified)
            market_cap = info.get('marketCap', 0)
            
            if market_cap > 200e9:  # > $200B
                competitive_position = 'Market Leader'
                position_score = 85
            elif market_cap > 50e9:  # > $50B
                competitive_position = 'Major Player'
                position_score = 70
            elif market_cap > 10e9:  # > $10B
                competitive_position = 'Established Company'
                position_score = 60
            else:
                competitive_position = 'Growing Company'
                position_score = 45
            
            return {
                'sector': sector,
                'industry': industry,
                'competitive_position': competitive_position,
                'position_score': position_score,
                'market_cap_category': self._categorize_market_cap(market_cap),
                'competitive_advantages': self._identify_competitive_advantages(info)
            }
            
        except Exception as e:
            logger.error(f"Competitive intelligence failed for {symbol}: {e}")
            return {'status': 'error'}
    
    def _analyze_market_psychology(self, symbol: str) -> Dict:
        """Analyze market psychology indicators"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="30d", interval="1d")
            
            if len(hist) < 10:
                return {'sentiment': 'neutral', 'confidence': 30}
            
            # Analyze price patterns for psychology
            closes = hist['Close']
            volumes = hist['Volume']
            
            # Fear/Greed indicators
            price_volatility = closes.pct_change().std()
            volume_trend = volumes.rolling(5).mean().iloc[-1] / volumes.rolling(20).mean().iloc[-1]
            
            # Psychology classification
            if price_volatility > 0.04 and volume_trend > 1.5:
                psychology = 'High Fear/Excitement'
                score = 80
            elif price_volatility < 0.02 and volume_trend < 0.8:
                psychology = 'Complacency'
                score = 40
            else:
                psychology = 'Balanced'
                score = 60
            
            return {
                'market_psychology': psychology,
                'psychology_score': score,
                'fear_greed_index': min(100, max(0, volume_trend * 50)),
                'volatility_sentiment': 'High' if price_volatility > 0.03 else 'Normal'
            }
            
        except Exception as e:
            logger.error(f"Market psychology analysis failed for {symbol}: {e}")
            return {'market_psychology': 'Unknown'}
    
    def _detect_institutional_activity(self, symbol: str) -> Dict:
        """Detect signs of institutional activity"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d", interval="1h")
            
            if len(hist) < 20:
                return {'activity_level': 'Unknown', 'confidence': 30}
            
            # Look for institutional patterns
            volumes = hist['Volume']
            avg_volume = volumes.mean()
            large_volume_periods = (volumes > avg_volume * 2).sum()
            
            # Institutional activity indicators
            if large_volume_periods > 5:
                activity_level = 'High Institutional Activity'
                confidence = 75
            elif large_volume_periods > 2:
                activity_level = 'Moderate Activity'
                confidence = 60
            else:
                activity_level = 'Normal Activity'
                confidence = 50
            
            return {
                'activity_level': activity_level,
                'unusual_volume_periods': int(large_volume_periods),
                'volume_pattern': 'Accumulation' if large_volume_periods > 3 else 'Normal',
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Institutional activity detection failed for {symbol}: {e}")
            return {'activity_level': 'Unknown'}
    
    # Helper methods for calculations
    def _calculate_momentum_score(self, hist: pd.DataFrame) -> float:
        """Calculate momentum score from price data"""
        try:
            returns = hist['Close'].pct_change().dropna()
            recent_returns = returns.tail(5).mean()
            return min(95, max(5, (recent_returns + 0.02) * 2500))
        except:
            return 50
    
    def _calculate_technical_score(self, hist: pd.DataFrame) -> float:
        """Calculate technical analysis score"""
        try:
            closes = hist['Close']
            sma_20 = closes.rolling(20).mean()
            current_price = closes.iloc[-1]
            sma_current = sma_20.iloc[-1]
            
            if current_price > sma_current * 1.05:
                return 80
            elif current_price > sma_current:
                return 65
            elif current_price > sma_current * 0.95:
                return 45
            else:
                return 25
        except:
            return 50
    
    def _get_default_watchlist(self) -> List[str]:
        """Get default watchlist for opportunity scanning"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 
            'NFLX', 'AMD', 'CRM', 'ZOOM', 'PLTR', 'SNOW', 'COIN'
        ]
    
    def _get_strategy_weights(self, user_strategy: str) -> Dict:
        """Get factor weights based on user strategy"""
        if user_strategy == 'growth_investor':
            return {
                'momentum_score': 0.3,
                'value_score': 0.1,
                'technical_score': 0.25,
                'volume_score': 0.2,
                'volatility_score': 0.15
            }
        elif user_strategy == 'value_investor':
            return {
                'momentum_score': 0.15,
                'value_score': 0.4,
                'technical_score': 0.2,
                'volume_score': 0.15,
                'volatility_score': 0.1
            }
        else:  # Default balanced
            return {
                'momentum_score': 0.25,
                'value_score': 0.25,
                'technical_score': 0.25,
                'volume_score': 0.15,
                'volatility_score': 0.1
            }


    def _scan_symbol_for_opportunities(self, symbol: str, user_strategy: str) -> Optional[Dict]:
        """Scan individual symbol for investment opportunities"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d", interval="1d")
            info = ticker.info
            
            if len(hist) < 3:
                return None
            
            # Calculate opportunity metrics
            current_price = hist['Close'].iloc[-1]
            price_change_1d = (current_price / hist['Close'].iloc[-2] - 1) * 100 if len(hist) >= 2 else 0
            volume_ratio = hist['Volume'].iloc[-1] / hist['Volume'].mean() if hist['Volume'].mean() > 0 else 1.0
            
            # Calculate opportunity score
            opportunity_score = 50
            
            # Price momentum factor
            if price_change_1d > 2:
                opportunity_score += 20
            elif price_change_1d > 1:
                opportunity_score += 10
            elif price_change_1d < -2:
                opportunity_score -= 15
            
            # Volume factor
            if volume_ratio > 1.5:
                opportunity_score += 15
            elif volume_ratio > 1.2:
                opportunity_score += 8
            
            # Market cap factor (based on strategy)
            market_cap = info.get('marketCap', 0)
            if user_strategy == 'growth_investor' and market_cap > 10e9:
                opportunity_score += 10
            elif user_strategy == 'value_investor' and market_cap < 50e9:
                opportunity_score += 10
            
            # Only return if score is meaningful
            if opportunity_score > 60:
                return {
                    'symbol': symbol,
                    'score': min(95, opportunity_score),
                    'opportunity_type': 'Growth Momentum' if price_change_1d > 0 else 'Value Entry',
                    'reasoning': f"{symbol} shows {abs(price_change_1d):.1f}% movement with {volume_ratio:.1f}x volume",
                    'action_required': 'Monitor' if opportunity_score < 75 else 'Consider Entry',
                    'time_sensitivity': 'Medium',
                    'risk_level': 'Medium',
                    'current_price': round(current_price, 2),
                    'price_change_1d': round(price_change_1d, 2),
                    'volume_ratio': round(volume_ratio, 1)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Symbol scan failed for {symbol}: {e}")
            return None
    
    def _calculate_scan_confidence(self, opportunities: List[Dict]) -> float:
        """Calculate confidence in the opportunity scan results"""
        if not opportunities:
            return 40
        
        # Calculate average opportunity score
        avg_score = sum(opp.get('score', 50) for opp in opportunities) / len(opportunities)
        
        # Factor in number of opportunities found
        opportunity_factor = min(100, len(opportunities) * 10)
        
        # Combine factors
        confidence = (avg_score * 0.7) + (opportunity_factor * 0.3)
        
        return min(90, max(45, confidence))
    
    def _calculate_insight_confidence(self, insights: Dict) -> float:
        """Calculate confidence in AI insights"""
        # Simple confidence based on number of insights provided
        insight_count = len([v for v in insights.values() if v is not None])
        base_confidence = min(85, max(50, insight_count * 15))
        return base_confidence


# Global enhancer instance
enhancer = AICapabilityEnhancer()

def enhance_analysis(symbol: str, base_analysis: Dict, user_strategy: str = None) -> Dict:
    """Enhance stock analysis with AI capabilities"""
    return enhancer.enhance_stock_analysis(symbol, base_analysis, user_strategy)

def get_live_opportunities(watchlist: List[str] = None, user_strategy: str = None) -> Dict:
    """Get real-time investment opportunities"""
    return enhancer.get_real_time_opportunities(watchlist, user_strategy)

def generate_deep_insights(symbol: str, analysis_type: str = 'comprehensive') -> Dict:
    """Generate deep AI insights"""
    return enhancer.generate_ai_insights(symbol, analysis_type)