"""
Price Alerts System - Smart notifications for stock price movements
"""
import json
import time
from typing import List, Dict, Any
import yfinance as yf

class PriceAlertSystem:
    def __init__(self):
        self.alerts = []
        
    def create_alert(self, symbol: str, target_price: float, alert_type: str = "above") -> Dict[str, Any]:
        """Create a new price alert"""
        alert = {
            'id': f"alert_{symbol}_{int(time.time())}",
            'symbol': symbol.upper(),
            'target_price': target_price,
            'alert_type': alert_type,  # "above" or "below"
            'created_at': int(time.time()),
            'triggered': False,
            'current_price': self.get_current_price(symbol)
        }
        self.alerts.append(alert)
        return alert
    
    def get_current_price(self, symbol: str) -> float:
        """Get current stock price from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.info
            return float(data.get('currentPrice', data.get('regularMarketPrice', 0)))
        except:
            return 0.0
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check all alerts and return triggered ones"""
        triggered_alerts = []
        
        for alert in self.alerts:
            if alert['triggered']:
                continue
                
            current_price = self.get_current_price(alert['symbol'])
            alert['current_price'] = current_price
            
            # Check if alert should trigger
            should_trigger = False
            if alert['alert_type'] == "above" and current_price >= alert['target_price']:
                should_trigger = True
            elif alert['alert_type'] == "below" and current_price <= alert['target_price']:
                should_trigger = True
            
            if should_trigger:
                alert['triggered'] = True
                alert['triggered_at'] = int(time.time())
                triggered_alerts.append(alert)
        
        return triggered_alerts
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active (non-triggered) alerts"""
        return [alert for alert in self.alerts if not alert['triggered']]
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert"""
        self.alerts = [alert for alert in self.alerts if alert['id'] != alert_id]
        return True
    
    def get_smart_suggestions(self, symbol: str) -> List[Dict[str, Any]]:
        """Generate smart alert suggestions based on technical analysis"""
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period="1mo")
            current_price = self.get_current_price(symbol)
            
            if len(history) < 5 or current_price == 0:
                return []
            
            # Calculate support and resistance levels
            high_20d = history['High'].tail(20).max()
            low_20d = history['Low'].tail(20).min()
            
            suggestions = []
            
            # Resistance level alert
            if current_price < high_20d * 0.95:
                suggestions.append({
                    'type': 'above',
                    'price': round(high_20d * 0.98, 2),
                    'reason': 'Approaching 20-day resistance level',
                    'confidence': 'High'
                })
            
            # Support level alert  
            if current_price > low_20d * 1.05:
                suggestions.append({
                    'type': 'below',
                    'price': round(low_20d * 1.02, 2),
                    'reason': 'Near 20-day support level',
                    'confidence': 'Medium'
                })
            
            # Breakout alert (5% above current)
            suggestions.append({
                'type': 'above',
                'price': round(current_price * 1.05, 2),
                'reason': 'Potential breakout opportunity',
                'confidence': 'Medium'
            })
            
            # Dip alert (5% below current)
            suggestions.append({
                'type': 'below',
                'price': round(current_price * 0.95, 2),
                'reason': 'Buying opportunity on dip',
                'confidence': 'Medium'
            })
            
            return suggestions
        except:
            return []

# Global instance
price_alert_system = PriceAlertSystem()