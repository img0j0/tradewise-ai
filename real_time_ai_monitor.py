"""
Real-Time AI Market Monitor
Continuously monitors markets for opportunities, risks, and events
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf
import threading
import time
import json
from collections import defaultdict

logger = logging.getLogger(__name__)

class RealTimeAIMonitor:
    """
    Real-time market monitoring system that runs continuously
    Provides live alerts and opportunities to users
    """
    
    def __init__(self):
        self.is_running = False
        self.watchlists = defaultdict(list)  # user_id -> [symbols]
        self.alert_callbacks = []
        self.monitoring_thread = None
        self.last_scan_time = {}
        
        # AI models for real-time analysis
        self.opportunity_detector = None
        self.risk_monitor = None
        self.event_detector = None
        
        logger.info("Real-Time AI Monitor initialized")
    
    def start_monitoring(self, watchlist: List[str] = None):
        """Start real-time monitoring"""
        if self.is_running:
            return
        
        if not watchlist:
            watchlist = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META']
        
        self.current_watchlist = watchlist
        self.is_running = True
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info(f"Started real-time monitoring for {len(watchlist)} stocks")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Stopped real-time monitoring")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Scan for opportunities every 5 minutes
                current_time = datetime.now()
                
                for symbol in self.current_watchlist:
                    last_scan = self.last_scan_time.get(symbol, datetime.min)
                    
                    if current_time - last_scan > timedelta(minutes=5):
                        self._scan_symbol(symbol)
                        self.last_scan_time[symbol] = current_time
                
                # Sleep for 30 seconds before next iteration
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _scan_symbol(self, symbol: str):
        """Scan individual symbol for opportunities and alerts"""
        try:
            # Get real-time data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d", interval="1h")
            
            if len(hist) < 10:
                return
            
            # Check for various conditions
            alerts = []
            
            # Volume surge detection
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].mean()
            
            if current_volume > avg_volume * 2:
                alerts.append({
                    'type': 'volume_surge',
                    'symbol': symbol,
                    'message': f'{symbol} showing {current_volume/avg_volume:.1f}x normal volume',
                    'urgency': 'high',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Price breakout detection
            current_price = hist['Close'].iloc[-1]
            high_20 = hist['High'].rolling(20).max().iloc[-1]
            
            if current_price > high_20 * 1.02:  # 2% above 20-period high
                alerts.append({
                    'type': 'price_breakout',
                    'symbol': symbol,
                    'message': f'{symbol} breaking above 20-period high at ${current_price:.2f}',
                    'urgency': 'medium',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Send alerts if any found
            for alert in alerts:
                self._send_alert(alert)
                
        except Exception as e:
            logger.error(f"Error scanning {symbol}: {e}")
    
    def _send_alert(self, alert: Dict):
        """Send alert to registered callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error sending alert: {e}")
    
    def register_alert_callback(self, callback):
        """Register callback for receiving alerts"""
        self.alert_callbacks.append(callback)
    
    def get_current_opportunities(self) -> List[Dict]:
        """Get current opportunities from monitoring"""
        opportunities = []
        
        for symbol in self.current_watchlist:
            try:
                # Quick opportunity check
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d", interval="1h")
                
                if len(hist) < 5:
                    continue
                
                current_price = hist['Close'].iloc[-1]
                price_1h_ago = hist['Close'].iloc[-2]
                price_change = (current_price / price_1h_ago - 1) * 100
                
                if abs(price_change) > 1:  # 1% movement in last hour
                    opportunities.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'price_change_1h': price_change,
                        'opportunity_type': 'momentum' if price_change > 0 else 'dip_buying',
                        'detected_at': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                logger.error(f"Error getting opportunities for {symbol}: {e}")
        
        return opportunities[:10]  # Return top 10


# Global monitor instance
monitor = RealTimeAIMonitor()

def start_ai_monitoring(watchlist: List[str] = None):
    """Start AI monitoring for given watchlist"""
    return monitor.start_monitoring(watchlist)

def stop_ai_monitoring():
    """Stop AI monitoring"""
    return monitor.stop_monitoring()

def get_live_opportunities() -> List[Dict]:
    """Get current live opportunities"""
    return monitor.get_current_opportunities()