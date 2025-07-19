"""
Feature Enhancement Engine
Intelligent system for enhancing existing features and adding new capabilities
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import asyncio
from collections import defaultdict
import threading
import yfinance as yf
import numpy as np
from advanced_performance_optimizer import optimized, profiled, cached

class SmartDataProcessor:
    """Enhanced data processing with intelligent caching and optimization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_cache = {}
        self.processing_stats = defaultdict(list)
        
    @optimized(ttl_seconds=300)  # 5-minute cache
    def get_enhanced_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive stock data with enhanced metrics"""
        try:
            start_time = time.time()
            
            # Get basic stock data
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="1mo")
            
            if hist.empty:
                return {'error': 'No data available'}
            
            # Calculate enhanced metrics
            current_price = float(hist['Close'].iloc[-1])
            price_change = float(hist['Close'].iloc[-1] - hist['Close'].iloc[-2])
            price_change_pct = (price_change / hist['Close'].iloc[-2]) * 100
            
            # Volume analysis
            avg_volume = float(hist['Volume'].mean())
            current_volume = float(hist['Volume'].iloc[-1])
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Volatility analysis
            returns = hist['Close'].pct_change().dropna()
            volatility = float(returns.std()) * np.sqrt(252) * 100  # Annualized volatility
            
            # Support/Resistance levels
            highs = hist['High'].rolling(window=10).max()
            lows = hist['Low'].rolling(window=10).min()
            resistance = float(highs.iloc[-1])
            support = float(lows.iloc[-1])
            
            # Price momentum
            sma_5 = hist['Close'].rolling(window=5).mean()
            sma_20 = hist['Close'].rolling(window=20).mean()
            momentum_short = 'bullish' if current_price > sma_5.iloc[-1] else 'bearish'
            momentum_long = 'bullish' if sma_5.iloc[-1] > sma_20.iloc[-1] else 'bearish'
            
            processing_time = time.time() - start_time
            self.processing_stats[symbol].append(processing_time)
            
            enhanced_data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'current_price': current_price,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'volume': current_volume,
                'avg_volume': avg_volume,
                'volume_ratio': volume_ratio,
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'volatility': volatility,
                'support_level': support,
                'resistance_level': resistance,
                'momentum_short': momentum_short,
                'momentum_long': momentum_long,
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'processing_time': processing_time,
                'data_quality': 'high' if len(hist) >= 20 else 'medium',
                'last_updated': datetime.now().isoformat()
            }
            
            return enhanced_data
            
        except Exception as e:
            self.logger.error(f"Error processing stock data for {symbol}: {e}")
            return {'error': f'Failed to process data for {symbol}'}

class IntelligentAlertSystem:
    """Enhanced alert system with ML-based predictions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_patterns = defaultdict(list)
        self.data_processor = SmartDataProcessor()
        
    @profiled
    def generate_intelligent_alerts(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Generate intelligent alerts based on market conditions"""
        alerts = []
        
        for symbol in symbols:
            try:
                stock_data = self.data_processor.get_enhanced_stock_data(symbol)
                
                if 'error' in stock_data:
                    continue
                
                # Generate alerts based on various conditions
                symbol_alerts = self._analyze_conditions(stock_data)
                alerts.extend(symbol_alerts)
                
            except Exception as e:
                self.logger.error(f"Error generating alerts for {symbol}: {e}")
        
        # Sort alerts by priority and confidence
        alerts.sort(key=lambda x: (x['priority_score'], x['confidence']), reverse=True)
        return alerts[:10]  # Return top 10 alerts
    
    def _analyze_conditions(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze stock data for alert conditions"""
        alerts = []
        symbol = data['symbol']
        
        # Volume spike alert
        if data['volume_ratio'] > 2.0:
            alerts.append({
                'type': 'volume_spike',
                'symbol': symbol,
                'title': f'{symbol} Volume Spike',
                'message': f'Trading volume is {data["volume_ratio"]:.1f}x above average',
                'priority': 'high',
                'priority_score': 90,
                'confidence': min(95, 70 + (data['volume_ratio'] * 5)),
                'action': 'investigate',
                'timestamp': datetime.now().isoformat()
            })
        
        # Price breakout alert
        current_price = data['current_price']
        resistance = data['resistance_level']
        support = data['support_level']
        
        if current_price > resistance * 1.02:  # 2% above resistance
            alerts.append({
                'type': 'breakout_resistance',
                'symbol': symbol,
                'title': f'{symbol} Resistance Breakout',
                'message': f'Price broke above resistance level ${resistance:.2f}',
                'priority': 'high',
                'priority_score': 85,
                'confidence': 80,
                'action': 'consider_buy',
                'timestamp': datetime.now().isoformat()
            })
        
        elif current_price < support * 0.98:  # 2% below support
            alerts.append({
                'type': 'breakdown_support',
                'symbol': symbol,
                'title': f'{symbol} Support Breakdown',
                'message': f'Price broke below support level ${support:.2f}',
                'priority': 'high',
                'priority_score': 85,
                'confidence': 80,
                'action': 'consider_sell',
                'timestamp': datetime.now().isoformat()
            })
        
        # Momentum alerts
        if data['momentum_short'] == 'bullish' and data['momentum_long'] == 'bullish':
            if data['price_change_pct'] > 5:
                alerts.append({
                    'type': 'strong_momentum',
                    'symbol': symbol,
                    'title': f'{symbol} Strong Bullish Momentum',
                    'message': f'Strong upward momentum with {data["price_change_pct"]:.1f}% gain',
                    'priority': 'medium',
                    'priority_score': 75,
                    'confidence': 75,
                    'action': 'monitor',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Volatility alerts
        if data['volatility'] > 50:  # High volatility
            alerts.append({
                'type': 'high_volatility',
                'symbol': symbol,
                'title': f'{symbol} High Volatility Warning',
                'message': f'Volatility at {data["volatility"]:.1f}% - exercise caution',
                'priority': 'medium',
                'priority_score': 60,
                'confidence': 85,
                'action': 'risk_management',
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts

class SmartPortfolioAnalyzer:
    """Enhanced portfolio analysis with risk assessment"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_processor = SmartDataProcessor()
        
    @optimized(ttl_seconds=180)  # 3-minute cache
    def analyze_portfolio_performance(self, portfolio_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive portfolio analysis"""
        try:
            if not portfolio_data:
                return {'error': 'No portfolio data provided'}
            
            total_value = 0
            total_cost = 0
            positions = []
            sector_allocation = defaultdict(float)
            risk_scores = []
            
            for position in portfolio_data:
                symbol = position['symbol']
                quantity = position['quantity']
                avg_price = position['avg_price']
                
                # Get current market data
                stock_data = self.data_processor.get_enhanced_stock_data(symbol)
                
                if 'error' not in stock_data:
                    current_price = stock_data['current_price']
                    current_value = current_price * quantity
                    cost_basis = avg_price * quantity
                    
                    total_value += current_value
                    total_cost += cost_basis
                    
                    # Calculate position metrics
                    position_return = ((current_price - avg_price) / avg_price) * 100
                    position_weight = current_value / total_value if total_value > 0 else 0
                    
                    # Risk assessment
                    volatility = stock_data.get('volatility', 20)
                    position_risk = volatility * position_weight
                    risk_scores.append(position_risk)
                    
                    # Sector allocation
                    sector = stock_data.get('sector', 'Unknown')
                    sector_allocation[sector] += position_weight
                    
                    positions.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'avg_price': avg_price,
                        'current_price': current_price,
                        'current_value': current_value,
                        'cost_basis': cost_basis,
                        'unrealized_pnl': current_value - cost_basis,
                        'return_pct': position_return,
                        'weight': position_weight,
                        'risk_score': position_risk,
                        'volatility': volatility,
                        'sector': sector
                    })
            
            # Calculate portfolio metrics
            total_return = ((total_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0
            portfolio_risk = sum(risk_scores)
            
            # Risk assessment
            risk_level = 'low' if portfolio_risk < 15 else 'medium' if portfolio_risk < 25 else 'high'
            
            # Diversification score
            diversification_score = len(set(p['sector'] for p in positions)) * 10
            diversification_score = min(100, diversification_score)
            
            analysis = {
                'total_value': total_value,
                'total_cost': total_cost,
                'total_return': total_return,
                'unrealized_pnl': total_value - total_cost,
                'portfolio_risk': portfolio_risk,
                'risk_level': risk_level,
                'diversification_score': diversification_score,
                'positions': positions,
                'sector_allocation': dict(sector_allocation),
                'recommendations': self._generate_recommendations(positions, sector_allocation, portfolio_risk),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing portfolio: {e}")
            return {'error': 'Failed to analyze portfolio'}
    
    def _generate_recommendations(self, positions: List[Dict], sector_allocation: Dict, portfolio_risk: float) -> List[str]:
        """Generate portfolio optimization recommendations"""
        recommendations = []
        
        # Risk recommendations
        if portfolio_risk > 30:
            recommendations.append("Portfolio risk is high. Consider reducing position sizes in volatile stocks.")
        
        # Diversification recommendations
        if len(sector_allocation) < 3:
            recommendations.append("Portfolio lacks diversification. Consider adding positions in different sectors.")
        
        # Sector concentration
        max_sector_weight = max(sector_allocation.values()) if sector_allocation else 0
        if max_sector_weight > 0.4:
            recommendations.append(f"High concentration in one sector ({max_sector_weight:.1%}). Consider rebalancing.")
        
        # Position size recommendations
        large_positions = [p for p in positions if p['weight'] > 0.2]
        if large_positions:
            symbols = [p['symbol'] for p in large_positions]
            recommendations.append(f"Large position concentration in {', '.join(symbols)}. Consider reducing exposure.")
        
        # Performance recommendations
        losing_positions = [p for p in positions if p['return_pct'] < -10]
        if losing_positions:
            symbols = [p['symbol'] for p in losing_positions]
            recommendations.append(f"Review positions with significant losses: {', '.join(symbols)}.")
        
        return recommendations

class FeatureEnhancementEngine:
    """Main coordinator for feature enhancements"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_processor = SmartDataProcessor()
        self.alert_system = IntelligentAlertSystem()
        self.portfolio_analyzer = SmartPortfolioAnalyzer()
        
        # Start background enhancement tasks
        self._start_background_tasks()
        
    def _start_background_tasks(self):
        """Start background feature enhancement tasks"""
        def background_enhancements():
            while True:
                try:
                    # Pre-load popular stock data
                    popular_symbols = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA', 'AMZN', 'META', 'NFLX']
                    for symbol in popular_symbols:
                        self.data_processor.get_enhanced_stock_data(symbol)
                    
                    self.logger.info("Background data refresh completed")
                    time.sleep(300)  # Refresh every 5 minutes
                    
                except Exception as e:
                    self.logger.error(f"Background enhancement error: {e}")
                    time.sleep(600)  # Wait longer on error
        
        thread = threading.Thread(target=background_enhancements, daemon=True)
        thread.start()
        self.logger.info("Feature enhancement engine started with background tasks")
    
    def get_enhancement_report(self) -> Dict[str, Any]:
        """Generate feature enhancement status report"""
        return {
            'data_processor_stats': {
                'cached_symbols': len(self.data_processor.data_cache),
                'processing_stats': dict(self.data_processor.processing_stats)
            },
            'alert_system_stats': {
                'pattern_count': len(self.alert_system.alert_patterns)
            },
            'status': 'active',
            'last_updated': datetime.now().isoformat()
        }

# Global enhancement engine instance
feature_enhancement_engine = FeatureEnhancementEngine()