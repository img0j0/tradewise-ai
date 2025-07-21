# Smart Notifications System for TradeWise AI
from flask import Blueprint, jsonify, request
import json
import os
from datetime import datetime, timedelta
import yfinance as yf

notifications_bp = Blueprint('notifications', __name__)

# Notification storage (use database in production)
USER_NOTIFICATIONS = {}
NOTIFICATION_PREFERENCES = {}

@notifications_bp.route('/api/notifications/subscribe', methods=['POST'])
def subscribe_to_notifications():
    """Subscribe user to push notifications"""
    data = request.json
    user_id = data.get('user_id', 'demo_user')
    subscription = data.get('subscription')
    
    # Store subscription info (in production, use database)
    if user_id not in USER_NOTIFICATIONS:
        USER_NOTIFICATIONS[user_id] = {
            'subscriptions': [],
            'notifications': [],
            'preferences': {}
        }
    
    USER_NOTIFICATIONS[user_id]['subscriptions'].append(subscription)
    
    return jsonify({
        'success': True,
        'message': 'Successfully subscribed to notifications'
    })

@notifications_bp.route('/api/notifications/preferences', methods=['POST'])
def update_notification_preferences():
    """Update user notification preferences"""
    data = request.json
    user_id = data.get('user_id', 'demo_user')
    
    preferences = {
        'price_alerts': data.get('price_alerts', True),
        'portfolio_updates': data.get('portfolio_updates', True),
        'ai_recommendations': data.get('ai_recommendations', True),
        'market_news': data.get('market_news', False),
        'earnings_reminders': data.get('earnings_reminders', True),
        'unusual_activity': data.get('unusual_activity', True),
        'quiet_hours_start': data.get('quiet_hours_start', '22:00'),
        'quiet_hours_end': data.get('quiet_hours_end', '08:00'),
        'frequency': data.get('frequency', 'normal')  # low, normal, high
    }
    
    NOTIFICATION_PREFERENCES[user_id] = preferences
    
    return jsonify({
        'success': True,
        'preferences': preferences,
        'message': 'Notification preferences updated'
    })

@notifications_bp.route('/api/notifications/send', methods=['POST'])
def send_notification():
    """Send immediate notification to user"""
    data = request.json
    user_id = data.get('user_id', 'demo_user')
    
    notification = {
        'id': f"notif_{int(datetime.now().timestamp())}",
        'timestamp': datetime.now().isoformat(),
        'type': data.get('type', 'info'),
        'title': data.get('title', 'TradeWise AI'),
        'message': data.get('message', ''),
        'symbol': data.get('symbol'),
        'action_url': data.get('action_url'),
        'priority': data.get('priority', 'normal'),
        'read': False
    }
    
    if user_id not in USER_NOTIFICATIONS:
        USER_NOTIFICATIONS[user_id] = {'notifications': []}
    
    USER_NOTIFICATIONS[user_id]['notifications'].append(notification)
    
    # In production, send actual push notification here
    
    return jsonify({
        'success': True,
        'notification_id': notification['id'],
        'message': 'Notification sent successfully'
    })

@notifications_bp.route('/api/notifications/smart-alerts')
def generate_smart_alerts():
    """Generate AI-powered smart alerts based on market conditions"""
    try:
        # Get market data for analysis
        symbols = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN']
        alerts = []
        
        for symbol in symbols:
            stock_alerts = analyze_stock_for_alerts(symbol)
            alerts.extend(stock_alerts)
        
        # Market-wide alerts
        market_alerts = analyze_market_conditions()
        alerts.extend(market_alerts)
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/api/notifications/earnings-calendar')
def get_earnings_calendar():
    """Get upcoming earnings with AI predictions"""
    # Mock earnings data (in production, use real earnings API)
    upcoming_earnings = [
        {
            'symbol': 'AAPL',
            'company': 'Apple Inc.',
            'date': '2025-07-25',
            'time': 'after_market',
            'ai_prediction': {
                'expected_move': '+2.5%',
                'confidence': 82,
                'direction': 'positive',
                'key_factors': ['iPhone sales', 'Services growth', 'China market']
            }
        },
        {
            'symbol': 'MSFT',
            'company': 'Microsoft Corporation',
            'date': '2025-07-26',
            'time': 'after_market',
            'ai_prediction': {
                'expected_move': '+1.8%',
                'confidence': 78,
                'direction': 'positive',
                'key_factors': ['Azure growth', 'AI integration', 'Cloud demand']
            }
        },
        {
            'symbol': 'GOOGL',
            'company': 'Alphabet Inc.',
            'date': '2025-07-27',
            'time': 'after_market',
            'ai_prediction': {
                'expected_move': '+1.2%',
                'confidence': 74,
                'direction': 'positive',
                'key_factors': ['Ad revenue', 'YouTube growth', 'AI investments']
            }
        }
    ]
    
    return jsonify({
        'success': True,
        'earnings': upcoming_earnings,
        'total_companies': len(upcoming_earnings)
    })

@notifications_bp.route('/api/notifications/market-timing')
def get_optimal_timing():
    """Get AI-suggested optimal times to check portfolio"""
    current_hour = datetime.now().hour
    
    # AI-suggested optimal times based on market activity
    optimal_times = [
        {
            'time': '09:30',
            'reason': 'Market open - highest volatility and opportunities',
            'priority': 'high'
        },
        {
            'time': '12:00',
            'reason': 'Mid-day check - good for trend confirmation',
            'priority': 'medium'
        },
        {
            'time': '15:30',
            'reason': 'Pre-close hour - institutional activity peaks',
            'priority': 'high'
        },
        {
            'time': '16:00',
            'reason': 'Market close - daily performance review',
            'priority': 'medium'
        }
    ]
    
    # Find next optimal time
    next_optimal = None
    for time_slot in optimal_times:
        hour = int(time_slot['time'].split(':')[0])
        if hour > current_hour:
            next_optimal = time_slot
            break
    
    if not next_optimal:
        next_optimal = optimal_times[0]  # Next day's first optimal time
    
    return jsonify({
        'success': True,
        'current_time': datetime.now().strftime('%H:%M'),
        'next_optimal_time': next_optimal,
        'all_optimal_times': optimal_times,
        'market_status': get_market_status()
    })

@notifications_bp.route('/api/notifications/user/<user_id>')
def get_user_notifications(user_id):
    """Get all notifications for a user"""
    if user_id not in USER_NOTIFICATIONS:
        return jsonify({
            'notifications': [],
            'unread_count': 0
        })
    
    notifications = USER_NOTIFICATIONS[user_id]['notifications']
    unread_count = len([n for n in notifications if not n['read']])
    
    # Sort by timestamp (newest first)
    notifications.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify({
        'notifications': notifications[-50:],  # Last 50 notifications
        'unread_count': unread_count,
        'total_count': len(notifications)
    })

@notifications_bp.route('/api/notifications/mark-read', methods=['POST'])
def mark_notification_read():
    """Mark notification as read"""
    data = request.json
    user_id = data.get('user_id', 'demo_user')
    notification_id = data.get('notification_id')
    
    if user_id in USER_NOTIFICATIONS:
        for notification in USER_NOTIFICATIONS[user_id]['notifications']:
            if notification['id'] == notification_id:
                notification['read'] = True
                break
    
    return jsonify({'success': True})

def analyze_stock_for_alerts(symbol):
    """Analyze individual stock for alert-worthy conditions"""
    alerts = []
    
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        hist = stock.history(period='5d')
        
        if hist.empty:
            return alerts
        
        current_price = hist['Close'].iloc[-1]
        previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        volume = hist['Volume'].iloc[-1]
        avg_volume = hist['Volume'].mean()
        
        # Price movement alert
        price_change = ((current_price - previous_close) / previous_close) * 100
        if abs(price_change) > 3:
            alerts.append({
                'type': 'price_movement',
                'symbol': symbol,
                'title': f'{symbol} {"Surge" if price_change > 0 else "Drop"}',
                'message': f'{symbol} is {"up" if price_change > 0 else "down"} {abs(price_change):.1f}% today',
                'priority': 'high' if abs(price_change) > 5 else 'medium',
                'action_url': f'/search?symbol={symbol}'
            })
        
        # Volume spike alert
        if volume > avg_volume * 2:
            alerts.append({
                'type': 'volume_spike',
                'symbol': symbol,
                'title': f'{symbol} Volume Spike',
                'message': f'Unusual trading volume detected - {volume/avg_volume:.1f}x normal volume',
                'priority': 'medium',
                'action_url': f'/search?symbol={symbol}'
            })
        
        # Breakout alert (simple resistance level)
        high_5d = hist['High'].max()
        if current_price >= high_5d * 0.99:
            alerts.append({
                'type': 'breakout',
                'symbol': symbol,
                'title': f'{symbol} Breakout Alert',
                'message': f'{symbol} approaching 5-day high - potential breakout',
                'priority': 'medium',
                'action_url': f'/search?symbol={symbol}'
            })
        
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
    
    return alerts

def analyze_market_conditions():
    """Analyze overall market conditions for alerts"""
    alerts = []
    
    try:
        # Market indices
        spy = yf.Ticker('SPY')
        spy_hist = spy.history(period='2d')
        
        if not spy_hist.empty:
            spy_change = ((spy_hist['Close'].iloc[-1] - spy_hist['Close'].iloc[-2]) / 
                         spy_hist['Close'].iloc[-2]) * 100
            
            if abs(spy_change) > 2:
                alerts.append({
                    'type': 'market_movement',
                    'symbol': 'SPY',
                    'title': f'Market {"Rally" if spy_change > 0 else "Decline"}',
                    'message': f'S&P 500 is {"up" if spy_change > 0 else "down"} {abs(spy_change):.1f}% today',
                    'priority': 'high' if abs(spy_change) > 3 else 'medium',
                    'action_url': '/dashboard'
                })
        
        # VIX (volatility index) - mock data
        vix_level = 18.5  # Current VIX level
        if vix_level > 25:
            alerts.append({
                'type': 'volatility_spike',
                'symbol': 'VIX',
                'title': 'High Market Volatility',
                'message': f'VIX at {vix_level} - increased market uncertainty',
                'priority': 'high',
                'action_url': '/dashboard'
            })
        
    except Exception as e:
        print(f"Error analyzing market conditions: {e}")
    
    return alerts

def get_market_status():
    """Get current market status"""
    now = datetime.now()
    current_time = now.time()
    
    # Market hours: 9:30 AM - 4:00 PM ET (simplified)
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0).time()
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0).time()
    
    # Check if weekend
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return 'closed_weekend'
    
    if market_open <= current_time <= market_close:
        return 'open'
    elif current_time < market_open:
        return 'pre_market'
    else:
        return 'after_hours'

def get_notification_javascript():
    """Return JavaScript for notification functionality"""
    return '''
    class SmartNotifications {
        constructor() {
            this.isSupported = 'Notification' in window;
            this.permission = this.isSupported ? Notification.permission : 'denied';
            this.userId = 'demo_user';
        }

        async requestPermission() {
            if (!this.isSupported) {
                console.log('Notifications not supported');
                return false;
            }

            if (this.permission === 'granted') {
                return true;
            }

            const permission = await Notification.requestPermission();
            this.permission = permission;
            return permission === 'granted';
        }

        async showNotification(title, options = {}) {
            if (this.permission !== 'granted') {
                console.log('Notification permission not granted');
                return;
            }

            const notification = new Notification(title, {
                body: options.message || '',
                icon: '/static/icons/icon-192x192.png',
                badge: '/static/icons/badge-72x72.png',
                tag: options.tag || 'tradewise-notification',
                vibrate: options.vibrate || [100, 50, 100],
                data: options.data || {},
                actions: options.actions || [],
                ...options
            });

            notification.onclick = (event) => {
                event.preventDefault();
                if (options.action_url) {
                    window.open(options.action_url, '_blank');
                }
                notification.close();
            };

            // Auto-close after 10 seconds
            setTimeout(() => notification.close(), 10000);

            return notification;
        }

        async loadUserNotifications() {
            try {
                const response = await fetch(`/api/notifications/user/${this.userId}`);
                const data = await response.json();
                
                this.updateNotificationBadge(data.unread_count);
                return data.notifications;
            } catch (error) {
                console.error('Error loading notifications:', error);
                return [];
            }
        }

        updateNotificationBadge(count) {
            // Update notification badge in UI
            const badge = document.querySelector('.notification-badge');
            if (badge) {
                badge.textContent = count > 0 ? count : '';
                badge.style.display = count > 0 ? 'block' : 'none';
            }
        }

        async checkForAlerts() {
            try {
                const response = await fetch('/api/notifications/smart-alerts');
                const data = await response.json();
                
                if (data.success && data.alerts.length > 0) {
                    // Show high priority alerts as notifications
                    data.alerts.forEach(alert => {
                        if (alert.priority === 'high') {
                            this.showNotification(alert.title, {
                                message: alert.message,
                                tag: `alert-${alert.symbol}`,
                                action_url: alert.action_url,
                                data: { type: 'alert', symbol: alert.symbol }
                            });
                        }
                    });
                }
            } catch (error) {
                console.error('Error checking for alerts:', error);
            }
        }

        async getOptimalTiming() {
            try {
                const response = await fetch('/api/notifications/market-timing');
                const data = await response.json();
                
                if (data.success) {
                    return data;
                }
            } catch (error) {
                console.error('Error getting optimal timing:', error);
            }
            return null;
        }

        startPeriodicChecks() {
            // Check for alerts every 5 minutes
            setInterval(() => {
                this.checkForAlerts();
            }, 5 * 60 * 1000);

            // Load notifications every minute
            setInterval(() => {
                this.loadUserNotifications();
            }, 60 * 1000);
        }

        async updatePreferences(preferences) {
            try {
                const response = await fetch('/api/notifications/preferences', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: this.userId,
                        ...preferences
                    })
                });
                
                const data = await response.json();
                return data.success;
            } catch (error) {
                console.error('Error updating preferences:', error);
                return false;
            }
        }
    }

    // Initialize notifications
    const smartNotifications = new SmartNotifications();

    // Auto-request permission on first visit
    document.addEventListener('DOMContentLoaded', async function() {
        await smartNotifications.requestPermission();
        await smartNotifications.loadUserNotifications();
        smartNotifications.startPeriodicChecks();
    });
    '''

def install_smart_notifications(app):
    """Install smart notifications into Flask app"""
    app.register_blueprint(notifications_bp)
    return app