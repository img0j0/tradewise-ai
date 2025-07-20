"""
Smart Stock Alerts System - Intuitive stock-focused alerts with AI insights
"""
import json
import time
from typing import List, Dict, Any, Optional
import yfinance as yf
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SmartStockAlerts:
    def __init__(self):
        self.alerts = []
        
    def create_stock_alert(self, symbol: str, alert_configs: List[Dict]) -> Dict[str, Any]:
        """Create comprehensive stock alerts with multiple conditions"""
        try:
            # Get current stock data
            ticker = yf.Ticker(symbol)
            info = ticker.info
            current_price = float(info.get('currentPrice', info.get('regularMarketPrice', 0)))
            
            if current_price == 0:
                return {'success': False, 'error': 'Unable to fetch stock data'}
            
            alert_id = f"alert_{symbol}_{int(time.time())}"
            
            alert = {
                'id': alert_id,
                'symbol': symbol.upper(),
                'company_name': info.get('longName', symbol),
                'current_price': current_price,
                'created_at': datetime.now().isoformat(),
                'active': True,
                'conditions': alert_configs,
                'triggered_conditions': [],
                'last_checked': None,
                'notification_count': 0
            }
            
            self.alerts.append(alert)
            logger.info(f"Created stock alert for {symbol} with {len(alert_configs)} conditions")
            
            return {
                'success': True,
                'alert': alert,
                'message': f"Alert created for {symbol} with {len(alert_configs)} conditions"
            }
            
        except Exception as e:
            logger.error(f"Error creating stock alert for {symbol}: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_alert_suggestions(self, symbol: str) -> List[Dict[str, Any]]:
        """Generate smart alert suggestions based on AI analysis"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="3mo")
            
            if len(history) < 20:
                return []
            
            current_price = float(info.get('currentPrice', info.get('regularMarketPrice', 0)))
            if current_price == 0:
                return []
            
            suggestions = []
            
            # Calculate key levels
            high_52w = float(info.get('fiftyTwoWeekHigh', history['High'].max()))
            low_52w = float(info.get('fiftyTwoWeekLow', history['Low'].min()))
            high_20d = history['High'].tail(20).max()
            low_20d = history['Low'].tail(20).min()
            avg_volume = history['Volume'].mean()
            
            # 1. Price Movement Alerts
            suggestions.append({
                'type': 'price_movement',
                'title': 'Price Breakout Alert',
                'description': f'Notify when {symbol} breaks above recent resistance',
                'condition': 'price_above',
                'value': round(high_20d * 1.02, 2),
                'reasoning': f'Above 20-day high of ${high_20d:.2f}',
                'confidence': 'High',
                'icon': '📈'
            })
            
            suggestions.append({
                'type': 'price_movement',
                'title': 'Buying Opportunity Alert',
                'description': f'Notify when {symbol} dips for potential entry',
                'condition': 'price_below',
                'value': round(current_price * 0.95, 2),
                'reasoning': '5% below current price',
                'confidence': 'Medium',
                'icon': '🛒'
            })
            
            # 2. Volume Alerts
            suggestions.append({
                'type': 'volume_spike',
                'title': 'Unusual Activity Alert',
                'description': f'Notify when {symbol} has unusual trading volume',
                'condition': 'volume_above',
                'value': int(avg_volume * 2),
                'reasoning': f'2x average volume ({avg_volume:,.0f})',
                'confidence': 'High',
                'icon': '🔥'
            })
            
            # 3. Performance Alerts
            suggestions.append({
                'type': 'performance',
                'title': 'Strong Gain Alert',
                'description': f'Notify when {symbol} has significant daily gains',
                'condition': 'daily_change_above',
                'value': 5.0,
                'reasoning': 'Daily gain exceeds 5%',
                'confidence': 'Medium',
                'icon': '🚀'
            })
            
            suggestions.append({
                'type': 'performance',
                'title': 'Major Drop Alert',
                'description': f'Notify when {symbol} drops significantly',
                'condition': 'daily_change_below',
                'value': -5.0,
                'reasoning': 'Daily loss exceeds 5%',
                'confidence': 'High',
                'icon': '⚠️'
            })
            
            # 4. Technical Alerts
            suggestions.append({
                'type': 'technical',
                'title': '52-Week High Alert',
                'description': f'Notify when {symbol} approaches new highs',
                'condition': 'price_above',
                'value': round(high_52w * 0.98, 2),
                'reasoning': f'Near 52-week high of ${high_52w:.2f}',
                'confidence': 'High',
                'icon': '🏆'
            })
            
            # 5. Market Cap / News Alerts
            market_cap = info.get('marketCap', 0)
            if market_cap > 1e9:  # Only for larger companies
                suggestions.append({
                    'type': 'news_sentiment',
                    'title': 'News & Sentiment Alert',
                    'description': f'Notify on major news affecting {symbol}',
                    'condition': 'news_sentiment',
                    'value': 'significant',
                    'reasoning': 'Major positive/negative news detected',
                    'confidence': 'Medium',
                    'icon': '📰'
                })
            
            return suggestions[:6]  # Return top 6 suggestions
            
        except Exception as e:
            logger.error(f"Error generating alert suggestions for {symbol}: {e}")
            return []
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check all active alerts and return triggered ones"""
        triggered_alerts = []
        
        for alert in self.alerts:
            if not alert['active']:
                continue
            
            try:
                # Get current stock data
                ticker = yf.Ticker(alert['symbol'])
                info = ticker.info
                current_price = float(info.get('currentPrice', info.get('regularMarketPrice', 0)))
                
                if current_price == 0:
                    continue
                
                alert['current_price'] = current_price
                alert['last_checked'] = datetime.now().isoformat()
                
                # Check each condition
                for condition in alert['conditions']:
                    if self._check_condition(alert['symbol'], current_price, condition):
                        # Mark as triggered
                        triggered_condition = {
                            **condition,
                            'triggered_at': datetime.now().isoformat(),
                            'triggered_price': current_price
                        }
                        
                        alert['triggered_conditions'].append(triggered_condition)
                        alert['notification_count'] += 1
                        
                        triggered_alerts.append({
                            'alert': alert,
                            'condition': triggered_condition,
                            'current_price': current_price
                        })
                
            except Exception as e:
                logger.error(f"Error checking alert for {alert['symbol']}: {e}")
                continue
        
        return triggered_alerts
    
    def _check_condition(self, symbol: str, current_price: float, condition: Dict) -> bool:
        """Check if a specific condition is met"""
        try:
            condition_type = condition['condition']
            value = condition['value']
            
            if condition_type == 'price_above':
                return current_price >= value
            elif condition_type == 'price_below':
                return current_price <= value
            elif condition_type == 'volume_above':
                ticker = yf.Ticker(symbol)
                current_volume = ticker.info.get('volume', 0)
                return current_volume >= value
            elif condition_type == 'daily_change_above':
                ticker = yf.Ticker(symbol)
                info = ticker.info
                change_pct = info.get('regularMarketChangePercent', 0)
                return change_pct >= value
            elif condition_type == 'daily_change_below':
                ticker = yf.Ticker(symbol)
                info = ticker.info
                change_pct = info.get('regularMarketChangePercent', 0)
                return change_pct <= value
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking condition for {symbol}: {e}")
            return False
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts with current status"""
        active_alerts = []
        
        for alert in self.alerts:
            if alert['active']:
                try:
                    # Get current price
                    ticker = yf.Ticker(alert['symbol'])
                    info = ticker.info
                    current_price = float(info.get('currentPrice', info.get('regularMarketPrice', 0)))
                    
                    alert_copy = alert.copy()
                    alert_copy['current_price'] = current_price
                    alert_copy['status'] = self._get_alert_status(alert, current_price)
                    
                    active_alerts.append(alert_copy)
                    
                except Exception as e:
                    logger.error(f"Error getting status for alert {alert['id']}: {e}")
                    continue
        
        return active_alerts
    
    def _get_alert_status(self, alert: Dict, current_price: float) -> Dict[str, Any]:
        """Get current status of an alert"""
        status = {
            'active_conditions': len(alert['conditions']),
            'triggered_conditions': len(alert['triggered_conditions']),
            'closest_trigger': None,
            'distance_to_trigger': float('inf')
        }
        
        # Find closest condition to triggering
        for condition in alert['conditions']:
            if condition['condition'] == 'price_above':
                distance = (condition['value'] - current_price) / current_price * 100
                if 0 < distance < status['distance_to_trigger']:
                    status['distance_to_trigger'] = distance
                    status['closest_trigger'] = f"{distance:.1f}% to ${condition['value']:.2f}"
            elif condition['condition'] == 'price_below':
                distance = (current_price - condition['value']) / current_price * 100
                if 0 < distance < status['distance_to_trigger']:
                    status['distance_to_trigger'] = distance
                    status['closest_trigger'] = f"{distance:.1f}% to ${condition['value']:.2f}"
        
        return status
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete a stock alert"""
        self.alerts = [alert for alert in self.alerts if alert['id'] != alert_id]
        return True
    
    def pause_alert(self, alert_id: str) -> bool:
        """Pause/unpause a stock alert"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['active'] = not alert['active']
                return True
        return False

# Global instance
smart_stock_alerts = SmartStockAlerts()