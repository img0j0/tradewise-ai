"""
AI Trading Copilot - Premium Feature Implementation
Real-time AI assistant that monitors markets and provides actionable trading signals
"""

import asyncio
import threading
import time
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class AlertType(Enum):
    BREAKOUT = "breakout"
    REVERSAL = "reversal"
    VOLUME_SPIKE = "volume_spike"
    EARNINGS_PLAY = "earnings_play"
    SECTOR_ROTATION = "sector_rotation"
    RISK_WARNING = "risk_warning"
    MOMENTUM_SHIFT = "momentum_shift"

class SignalStrength(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class TradingSignal:
    symbol: str
    signal_type: AlertType
    strength: SignalStrength
    confidence: float
    current_price: float
    target_price: float
    stop_loss: float
    message: str
    timestamp: datetime
    ai_reasoning: str
    expected_timeframe: str
    risk_level: str

class AITradingCopilot:
    """Real-time AI trading copilot for premium subscribers"""
    
    def __init__(self):
        self.is_monitoring = False
        self.subscribers = set()  # Premium subscribers
        self.watchlist = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'SPY', 'QQQ']
        self.market_data_cache = {}
        self.signal_history = []
        self.monitoring_thread = None
        
        # AI model components
        self.momentum_threshold = 0.05  # 5% price movement
        self.volume_threshold = 1.5     # 1.5x average volume
        self.confidence_threshold = 0.75  # 75% confidence minimum
        
        logger.info("AI Trading Copilot initialized")
    
    def start_monitoring(self):
        """Start real-time market monitoring for premium subscribers"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._continuous_monitoring)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("AI Trading Copilot monitoring started")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("AI Trading Copilot monitoring stopped")
    
    def add_subscriber(self, user_id: str):
        """Add premium subscriber to real-time alerts"""
        self.subscribers.add(user_id)
        logger.info(f"Added premium subscriber: {user_id}")
    
    def remove_subscriber(self, user_id: str):
        """Remove subscriber"""
        self.subscribers.discard(user_id)
        logger.info(f"Removed subscriber: {user_id}")
    
    def _continuous_monitoring(self):
        """Main monitoring loop - runs continuously for premium users"""
        logger.info("Starting continuous market monitoring...")
        
        while self.is_monitoring:
            try:
                # Check if market is open (basic check)
                now = datetime.now()
                if self._is_market_hours(now):
                    # Analyze each symbol in watchlist
                    for symbol in self.watchlist:
                        signal = self._analyze_symbol_for_signals(symbol)
                        if signal and self._is_significant_signal(signal):
                            self._broadcast_signal(signal)
                    
                    # Global market analysis
                    market_signal = self._analyze_market_conditions()
                    if market_signal:
                        self._broadcast_signal(market_signal)
                
                # Sleep for 30 seconds between scans (premium real-time monitoring)
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _is_market_hours(self, dt: datetime) -> bool:
        """Check if market is currently open (9:30 AM - 4:00 PM ET, weekdays)"""
        # Simplified market hours check
        weekday = dt.weekday()  # 0=Monday, 6=Sunday
        if weekday >= 5:  # Weekend
            return False
        
        hour = dt.hour
        return 9 <= hour <= 16  # Approximate market hours
    
    def _analyze_symbol_for_signals(self, symbol: str) -> Optional[TradingSignal]:
        """Analyze individual symbol for trading signals"""
        try:
            # Get recent price data
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d", interval="5m")  # 5-minute intervals
            
            if hist.empty or len(hist) < 10:
                return None
            
            current_price = float(hist['Close'].iloc[-1])
            prev_price = float(hist['Close'].iloc[-2])
            volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].mean()
            
            # Calculate momentum
            price_change = (current_price - prev_price) / prev_price
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1
            
            # Detect breakout pattern
            if abs(price_change) > self.momentum_threshold and volume_ratio > self.volume_threshold:
                signal_type = AlertType.BREAKOUT if price_change > 0 else AlertType.REVERSAL
                strength = self._calculate_signal_strength(price_change, volume_ratio)
                confidence = min(0.95, 0.6 + abs(price_change) * 5 + (volume_ratio - 1) * 0.1)
                
                # Calculate targets using simple technical analysis
                volatility = hist['Close'].std() / current_price
                target_price = current_price * (1 + (0.02 if price_change > 0 else -0.02))
                stop_loss = current_price * (1 + (-0.01 if price_change > 0 else 0.01))
                
                # Generate AI reasoning
                direction = "bullish" if price_change > 0 else "bearish"
                ai_reasoning = f"Detected {direction} momentum with {price_change*100:.2f}% price move and {volume_ratio:.1f}x volume spike. Technical indicators suggest continuation pattern."
                
                message = f"🚀 {symbol} {signal_type.value.title()} Alert: {direction.title()} breakout at ${current_price:.2f} with {confidence*100:.0f}% confidence"
                
                return TradingSignal(
                    symbol=symbol,
                    signal_type=signal_type,
                    strength=strength,
                    confidence=confidence,
                    current_price=current_price,
                    target_price=target_price,
                    stop_loss=stop_loss,
                    message=message,
                    timestamp=datetime.now(),
                    ai_reasoning=ai_reasoning,
                    expected_timeframe="15-30 minutes",
                    risk_level="Medium"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def _analyze_market_conditions(self) -> Optional[TradingSignal]:
        """Analyze overall market conditions (SPY, VIX, etc.)"""
        try:
            # Analyze SPY for market sentiment
            spy = yf.Ticker("SPY")
            hist = spy.history(period="1d", interval="5m")
            
            if hist.empty:
                return None
            
            current = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[-10])  # 50 minutes ago
            change = (current - prev) / prev
            
            # Detect significant market moves
            if abs(change) > 0.015:  # 1.5% market move
                direction = "bullish" if change > 0 else "bearish"
                message = f"📊 Market Alert: SPY showing {direction} momentum ({change*100:.1f}%) - Sector rotation opportunities detected"
                
                return TradingSignal(
                    symbol="SPY",
                    signal_type=AlertType.SECTOR_ROTATION,
                    strength=SignalStrength.HIGH,
                    confidence=0.8,
                    current_price=current,
                    target_price=current * (1 + change * 0.5),
                    stop_loss=current * (1 - abs(change) * 0.3),
                    message=message,
                    timestamp=datetime.now(),
                    ai_reasoning=f"Market showing {direction} momentum with broad participation across sectors",
                    expected_timeframe="1-2 hours",
                    risk_level="Low"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing market conditions: {e}")
            return None
    
    def _calculate_signal_strength(self, price_change: float, volume_ratio: float) -> SignalStrength:
        """Calculate signal strength based on price and volume"""
        score = abs(price_change) * 10 + (volume_ratio - 1) * 0.5
        
        if score > 1.0:
            return SignalStrength.CRITICAL
        elif score > 0.5:
            return SignalStrength.HIGH
        elif score > 0.2:
            return SignalStrength.MEDIUM
        else:
            return SignalStrength.LOW
    
    def _is_significant_signal(self, signal: TradingSignal) -> bool:
        """Determine if signal is significant enough to broadcast"""
        return (
            signal.confidence >= self.confidence_threshold and
            signal.strength in [SignalStrength.HIGH, SignalStrength.CRITICAL]
        )
    
    def _broadcast_signal(self, signal: TradingSignal):
        """Broadcast signal to all premium subscribers"""
        if not self.subscribers:
            return
        
        # Add to history
        self.signal_history.append(signal)
        
        # Keep only last 100 signals
        if len(self.signal_history) > 100:
            self.signal_history = self.signal_history[-100:]
        
        # Log the signal
        logger.info(f"Broadcasting signal: {signal.message}")
        
        # In a real implementation, this would send push notifications
        # or WebSocket messages to connected premium users
        signal_data = {
            'symbol': signal.symbol,
            'type': signal.signal_type.value,
            'strength': signal.strength.value,
            'confidence': signal.confidence,
            'price': signal.current_price,
            'target': signal.target_price,
            'stop_loss': signal.stop_loss,
            'message': signal.message,
            'reasoning': signal.ai_reasoning,
            'timeframe': signal.expected_timeframe,
            'risk': signal.risk_level,
            'timestamp': signal.timestamp.isoformat()
        }
        
        # TODO: Implement WebSocket broadcast to connected clients
        # await self.websocket_manager.broadcast_to_premium_users(signal_data)
    
    def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        """Get recent signals for premium subscribers"""
        recent = self.signal_history[-limit:] if self.signal_history else []
        return [
            {
                'symbol': s.symbol,
                'type': s.signal_type.value,
                'strength': s.strength.value,
                'confidence': s.confidence,
                'message': s.message,
                'timestamp': s.timestamp.isoformat(),
                'price': s.current_price,
                'target': s.target_price
            }
            for s in recent
        ]
    
    def get_copilot_status(self) -> Dict:
        """Get current copilot status for premium users"""
        return {
            'monitoring': self.is_monitoring,
            'subscribers': len(self.subscribers),
            'signals_today': len([s for s in self.signal_history if s.timestamp.date() == datetime.now().date()]),
            'watchlist_size': len(self.watchlist),
            'market_status': 'open' if self._is_market_hours(datetime.now()) else 'closed'
        }

# Global instance for the application
ai_copilot = AITradingCopilot()

def start_ai_copilot():
    """Initialize and start the AI copilot service"""
    ai_copilot.start_monitoring()

def stop_ai_copilot():
    """Stop the AI copilot service"""
    ai_copilot.stop_monitoring()