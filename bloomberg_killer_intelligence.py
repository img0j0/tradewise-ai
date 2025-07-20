"""
Bloomberg Killer Intelligence Engine - Professional Trading Data Optimization
Focused on the most critical data points that professional traders actually use
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class BloombergKillerIntelligence:
    """Optimized intelligence engine focused on critical trading data"""
    
    def __init__(self):
        self.cache = {}
        logger.info("Bloomberg Killer Intelligence initialized")
    
    def get_professional_analysis(self, symbol: str) -> Dict:
        """Get comprehensive professional-grade analysis for any stock"""
        try:
            stock = yf.Ticker(symbol)
            
            # Get essential data
            info = stock.info
            hist = stock.history(period="6mo", interval="1d")
            
            if len(hist) < 30:
                return {'error': 'Insufficient data'}
            
            # Core professional metrics
            analysis = {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                
                # Critical Price Data
                'price_data': self._get_critical_price_data(hist, info),
                
                # Professional Trading Metrics
                'trading_metrics': self._get_professional_trading_metrics(hist, info),
                
                # Risk & Volatility (Key for Position Sizing)
                'risk_analysis': self._get_professional_risk_analysis(hist, info),
                
                # Momentum & Trend (Critical for Entry/Exit)
                'momentum_analysis': self._get_momentum_analysis(hist),
                
                # Volume Analysis (Essential for Liquidity)
                'volume_intelligence': self._get_volume_intelligence(hist),
                
                # Key Levels (Support/Resistance)
                'key_levels': self._calculate_key_levels(hist),
                
                # Professional Ratings
                'professional_rating': self._generate_professional_rating(hist, info),
                
                # Market Context
                'market_context': self._get_market_context(info),
                
                'generated_at': datetime.now().isoformat()
            }
            
            # Convert any numpy types to native Python types for JSON serialization
            analysis = self._convert_to_json_serializable(analysis)
            return analysis
            
        except Exception as e:
            logger.error(f"Error in professional analysis for {symbol}: {str(e)}")
            return {'error': str(e)}
    
    def _convert_to_json_serializable(self, obj):
        """Convert any numpy types to JSON serializable types"""
        if isinstance(obj, dict):
            return {key: self._convert_to_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif hasattr(obj, 'item'):  # numpy types
            return float(obj.item()) if obj.dtype.kind in 'fc' else int(obj.item())
        elif isinstance(obj, (bool, type(None))):
            return obj
        elif isinstance(obj, (int, float, str)):
            return obj
        else:
            return str(obj)
    
    def _get_critical_price_data(self, hist: pd.DataFrame, info: Dict) -> Dict:
        """Most critical price data that traders watch"""
        current_price = float(hist['Close'].iloc[-1])
        
        # Key price levels
        high_52w = info.get('fiftyTwoWeekHigh', hist['High'].max())
        low_52w = info.get('fiftyTwoWeekLow', hist['Low'].min())
        
        # Position in range
        price_position = (current_price - low_52w) / (high_52w - low_52w) * 100
        
        return {
            'current_price': round(current_price, 2),
            'change_1d': round(hist['Close'].pct_change().iloc[-1] * 100, 2),
            'change_5d': round(hist['Close'].pct_change(5).iloc[-1] * 100, 2),
            'change_1m': round(hist['Close'].pct_change(20).iloc[-1] * 100, 2),
            'high_52w': round(high_52w, 2),
            'low_52w': round(low_52w, 2),
            'position_in_range': round(price_position, 1),
            'distance_from_high': round((high_52w - current_price) / high_52w * 100, 1),
            'distance_from_low': round((current_price - low_52w) / low_52w * 100, 1)
        }
    
    def _get_professional_trading_metrics(self, hist: pd.DataFrame, info: Dict) -> Dict:
        """Key metrics professional traders use for decisions"""
        
        # Moving averages (critical trend indicators)
        ma_20 = hist['Close'].rolling(20).mean().iloc[-1]
        ma_50 = hist['Close'].rolling(50).mean().iloc[-1]
        ma_200 = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else None
        
        current_price = hist['Close'].iloc[-1]
        
        # Relative strength
        rsi = self._calculate_rsi(hist['Close'])
        
        # MACD
        ema_12 = hist['Close'].ewm(span=12).mean()
        ema_26 = hist['Close'].ewm(span=26).mean()
        macd = ema_12.iloc[-1] - ema_26.iloc[-1]
        
        return {
            'ma_20': round(ma_20, 2),
            'ma_50': round(ma_50, 2),
            'ma_200': round(ma_200, 2) if ma_200 else None,
            'price_vs_ma20': round((current_price - ma_20) / ma_20 * 100, 2),
            'price_vs_ma50': round((current_price - ma_50) / ma_50 * 100, 2),
            'rsi': round(rsi, 1),
            'macd': round(macd, 4),
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('forwardPE') or info.get('trailingPE'),
            'beta': info.get('beta'),
            'avg_volume_3m': info.get('averageVolume3Month')
        }
    
    def _get_professional_risk_analysis(self, hist: pd.DataFrame, info: Dict) -> Dict:
        """Risk metrics critical for position sizing and risk management"""
        
        returns = hist['Close'].pct_change().dropna()
        
        # Volatility measures
        vol_1m = returns.tail(20).std() * np.sqrt(252)  # Annualized
        vol_3m = returns.tail(60).std() * np.sqrt(252)
        
        # Drawdown analysis
        peak = hist['Close'].expanding().max()
        drawdown = (hist['Close'] - peak) / peak
        max_drawdown = drawdown.min()
        current_drawdown = drawdown.iloc[-1]
        
        # Sharpe approximation
        avg_return = returns.mean() * 252
        sharpe = avg_return / vol_3m if vol_3m > 0 else 0
        
        # Risk classification
        risk_level = self._classify_risk_level(vol_1m, info.get('beta', 1))
        
        return {
            'volatility_1m': round(vol_1m * 100, 1),
            'volatility_3m': round(vol_3m * 100, 1),
            'max_drawdown': round(max_drawdown * 100, 1),
            'current_drawdown': round(current_drawdown * 100, 1),
            'sharpe_estimate': round(sharpe, 2),
            'risk_level': risk_level,
            'beta': info.get('beta'),
            'var_95': round(np.percentile(returns, 5) * 100, 2)  # Value at Risk
        }
    
    def _get_momentum_analysis(self, hist: pd.DataFrame) -> Dict:
        """Momentum indicators critical for timing entries/exits"""
        
        # Price momentum
        momentum_1w = hist['Close'].pct_change(5).iloc[-1]
        momentum_1m = hist['Close'].pct_change(20).iloc[-1]
        momentum_3m = hist['Close'].pct_change(60).iloc[-1]
        
        # Acceleration (change in momentum)
        recent_momentum = hist['Close'].pct_change(5).tail(5).mean()
        earlier_momentum = hist['Close'].pct_change(5).tail(10).head(5).mean()
        acceleration = recent_momentum - earlier_momentum
        
        # Trend strength
        trend_strength = self._calculate_trend_strength(hist)
        
        return {
            'momentum_1w': round(momentum_1w * 100, 2),
            'momentum_1m': round(momentum_1m * 100, 2),
            'momentum_3m': round(momentum_3m * 100, 2),
            'acceleration': round(acceleration * 100, 3),
            'trend_strength': trend_strength,
            'momentum_ranking': self._rank_momentum(momentum_1w, momentum_1m)
        }
    
    def _get_volume_intelligence(self, hist: pd.DataFrame) -> Dict:
        """Volume analysis for liquidity and conviction assessment"""
        
        avg_volume = hist['Volume'].rolling(20).mean()
        current_volume = hist['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume.iloc[-1]
        
        # Volume trend
        volume_trend = self._analyze_volume_trend(hist)
        
        # Volume-price relationship
        vp_correlation = self._calculate_volume_price_correlation(hist)
        
        return {
            'current_volume': int(current_volume),
            'avg_volume_20d': int(avg_volume.iloc[-1]),
            'volume_ratio': round(volume_ratio, 2),
            'volume_trend': volume_trend,
            'volume_price_correlation': round(vp_correlation, 2),
            'unusual_volume': bool(volume_ratio > 1.5)
        }
    
    def _calculate_key_levels(self, hist: pd.DataFrame) -> Dict:
        """Support and resistance levels - critical for entries/exits"""
        
        highs = hist['High']
        lows = hist['Low']
        
        # Recent support/resistance
        resistance_levels = self._find_resistance_levels(highs)
        support_levels = self._find_support_levels(lows)
        
        current_price = hist['Close'].iloc[-1]
        
        return {
            'nearest_resistance': self._find_nearest_level(current_price, resistance_levels, 'above'),
            'nearest_support': self._find_nearest_level(current_price, support_levels, 'below'),
            'resistance_levels': resistance_levels[:3],  # Top 3
            'support_levels': support_levels[:3],  # Top 3
            'key_level_proximity': self._assess_level_proximity(current_price, resistance_levels + support_levels)
        }
    
    def _generate_professional_rating(self, hist: pd.DataFrame, info: Dict) -> Dict:
        """Professional-grade rating based on key factors"""
        
        scores = {}
        
        # Technical score (40%)
        rsi = self._calculate_rsi(hist['Close'])
        price_vs_ma20 = (hist['Close'].iloc[-1] - hist['Close'].rolling(20).mean().iloc[-1]) / hist['Close'].rolling(20).mean().iloc[-1]
        
        technical_score = 0
        if 30 <= rsi <= 70:  # Not overbought/oversold
            technical_score += 0.5
        if price_vs_ma20 > 0:  # Above MA20
            technical_score += 0.3
        if hist['Close'].pct_change().iloc[-1] > 0:  # Positive day
            technical_score += 0.2
        
        scores['technical'] = technical_score
        
        # Momentum score (30%)
        momentum_1m = hist['Close'].pct_change(20).iloc[-1]
        momentum_score = max(0, min(1, 0.5 + momentum_1m * 5))
        scores['momentum'] = momentum_score
        
        # Risk score (30%)
        beta = info.get('beta', 1)
        vol_score = max(0, min(1, 1 - (abs(beta - 1) * 0.5)))
        scores['risk'] = vol_score
        
        # Overall rating
        overall_score = (scores['technical'] * 0.4 + scores['momentum'] * 0.3 + scores['risk'] * 0.3)
        
        if overall_score >= 0.8:
            rating = 'STRONG BUY'
        elif overall_score >= 0.6:
            rating = 'BUY'
        elif overall_score >= 0.4:
            rating = 'HOLD'
        elif overall_score >= 0.2:
            rating = 'SELL'
        else:
            rating = 'STRONG SELL'
        
        return {
            'overall_rating': rating,
            'overall_score': round(overall_score, 2),
            'technical_score': round(scores['technical'], 2),
            'momentum_score': round(scores['momentum'], 2),
            'risk_score': round(scores['risk'], 2),
            'confidence': round(min(0.95, 0.5 + overall_score * 0.4), 2)
        }
    
    def _get_market_context(self, info: Dict) -> Dict:
        """Market context and positioning"""
        
        return {
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'market_cap_category': self._categorize_market_cap(info.get('marketCap')),
            'dividend_yield': info.get('dividendYield'),
            'earnings_date': info.get('earningsDate'),
            'analyst_target': info.get('targetMeanPrice')
        }
    
    # Helper methods
    def _calculate_rsi(self, prices, window=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else 50
    
    def _classify_risk_level(self, volatility, beta):
        """Classify risk level for position sizing"""
        risk_score = volatility * 100 + abs(beta - 1) * 10
        
        if risk_score < 15:
            return 'LOW'
        elif risk_score < 25:
            return 'MODERATE'
        elif risk_score < 40:
            return 'HIGH'
        else:
            return 'EXTREME'
    
    def _calculate_trend_strength(self, hist):
        """Calculate trend strength"""
        ma_20 = hist['Close'].rolling(20).mean()
        ma_50 = hist['Close'].rolling(50).mean()
        
        if len(ma_50.dropna()) == 0:
            return 'NEUTRAL'
        
        current_price = hist['Close'].iloc[-1]
        ma20_current = ma_20.iloc[-1]
        ma50_current = ma_50.iloc[-1]
        
        if current_price > ma20_current > ma50_current:
            return 'STRONG BULLISH'
        elif current_price > ma20_current:
            return 'BULLISH'
        elif current_price < ma20_current < ma50_current:
            return 'STRONG BEARISH'
        elif current_price < ma20_current:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def _rank_momentum(self, momentum_1w, momentum_1m):
        """Rank momentum strength"""
        avg_momentum = (momentum_1w + momentum_1m) / 2
        
        if avg_momentum > 0.05:
            return 'STRONG POSITIVE'
        elif avg_momentum > 0.02:
            return 'POSITIVE'
        elif avg_momentum > -0.02:
            return 'NEUTRAL'
        elif avg_momentum > -0.05:
            return 'NEGATIVE'
        else:
            return 'STRONG NEGATIVE'
    
    def _analyze_volume_trend(self, hist):
        """Analyze volume trend"""
        recent_vol = hist['Volume'].tail(5).mean()
        earlier_vol = hist['Volume'].tail(20).head(15).mean()
        
        ratio = recent_vol / earlier_vol
        
        if ratio > 1.3:
            return 'INCREASING'
        elif ratio < 0.7:
            return 'DECREASING'
        else:
            return 'STABLE'
    
    def _calculate_volume_price_correlation(self, hist):
        """Volume-price correlation"""
        price_changes = hist['Close'].pct_change()
        volume_changes = hist['Volume'].pct_change()
        
        return price_changes.corr(volume_changes)
    
    def _find_resistance_levels(self, highs):
        """Find key resistance levels"""
        recent_highs = highs.tail(60)
        peaks = []
        
        for i in range(2, len(recent_highs)-2):
            if (recent_highs.iloc[i] > recent_highs.iloc[i-1] and 
                recent_highs.iloc[i] > recent_highs.iloc[i-2] and
                recent_highs.iloc[i] > recent_highs.iloc[i+1] and 
                recent_highs.iloc[i] > recent_highs.iloc[i+2]):
                peaks.append(recent_highs.iloc[i])
        
        return sorted(set(peaks), reverse=True)
    
    def _find_support_levels(self, lows):
        """Find key support levels"""
        recent_lows = lows.tail(60)
        troughs = []
        
        for i in range(2, len(recent_lows)-2):
            if (recent_lows.iloc[i] < recent_lows.iloc[i-1] and 
                recent_lows.iloc[i] < recent_lows.iloc[i-2] and
                recent_lows.iloc[i] < recent_lows.iloc[i+1] and 
                recent_lows.iloc[i] < recent_lows.iloc[i+2]):
                troughs.append(recent_lows.iloc[i])
        
        return sorted(set(troughs), reverse=True)
    
    def _find_nearest_level(self, current_price, levels, direction):
        """Find nearest support/resistance level"""
        if not levels:
            return None
        
        if direction == 'above':
            above_levels = [l for l in levels if l > current_price]
            return min(above_levels) if above_levels else None
        else:
            below_levels = [l for l in levels if l < current_price]
            return max(below_levels) if below_levels else None
    
    def _assess_level_proximity(self, current_price, levels):
        """Assess proximity to key levels"""
        if not levels:
            return 'CLEAR'
        
        min_distance = min(abs(current_price - level) / current_price for level in levels)
        
        if min_distance < 0.02:  # Within 2%
            return 'AT_KEY_LEVEL'
        elif min_distance < 0.05:  # Within 5%
            return 'NEAR_KEY_LEVEL'
        else:
            return 'CLEAR'
    
    def _categorize_market_cap(self, market_cap):
        """Categorize by market cap"""
        if not market_cap:
            return 'Unknown'
        
        if market_cap > 200_000_000_000:
            return 'Mega Cap'
        elif market_cap > 10_000_000_000:
            return 'Large Cap'
        elif market_cap > 2_000_000_000:
            return 'Mid Cap'
        elif market_cap > 300_000_000:
            return 'Small Cap'
        else:
            return 'Micro Cap'

# Global instance
bloomberg_killer = BloombergKillerIntelligence()