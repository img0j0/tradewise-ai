"""
Premium Notification Routes - Phase 5
API endpoints for handling premium upgrade notifications
"""

from flask import Blueprint, request, jsonify, session
from comprehensive_subscription_manager import ComprehensiveSubscriptionManager
from notification_system import send_upgrade_email, send_downgrade_email, send_alert_email
import logging

logger = logging.getLogger(__name__)

premium_notification_bp = Blueprint('premium_notifications', __name__)
subscription_manager = ComprehensiveSubscriptionManager()

@premium_notification_bp.route('/api/notifications/upgrade-success', methods=['POST'])
def handle_upgrade_success():
    """Handle successful plan upgrade with email notification"""
    try:
        data = request.get_json()
        
        # Required fields
        user_email = data.get('user_email')
        user_name = data.get('user_name', 'User')
        old_plan = data.get('old_plan', 'Free')
        new_plan = data.get('new_plan')
        amount = data.get('amount')
        
        if not user_email or not new_plan:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: user_email, new_plan'
            }), 400
        
        # Send upgrade notification email
        email_sent = send_upgrade_email(
            user_email=user_email,
            user_name=user_name,
            old_plan=old_plan,
            new_plan=new_plan,
            amount=amount
        )
        
        if email_sent:
            logger.info(f"✅ Upgrade notification sent to {user_email}: {old_plan} → {new_plan}")
            return jsonify({
                'success': True,
                'message': 'Upgrade notification sent successfully'
            })
        else:
            logger.warning(f"⚠️ Failed to send upgrade notification to {user_email}")
            return jsonify({
                'success': False,
                'error': 'Failed to send email notification'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error handling upgrade notification: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@premium_notification_bp.route('/api/notifications/downgrade', methods=['POST'])
def handle_downgrade_notification():
    """Handle plan downgrade with email notification"""
    try:
        data = request.get_json()
        
        user_email = data.get('user_email')
        user_name = data.get('user_name', 'User')
        old_plan = data.get('old_plan')
        new_plan = data.get('new_plan', 'Free')
        
        if not user_email or not old_plan:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: user_email, old_plan'
            }), 400
        
        # Send downgrade notification email
        email_sent = send_downgrade_email(
            user_email=user_email,
            user_name=user_name,
            old_plan=old_plan,
            new_plan=new_plan
        )
        
        if email_sent:
            logger.info(f"✅ Downgrade notification sent to {user_email}: {old_plan} → {new_plan}")
            return jsonify({
                'success': True,
                'message': 'Downgrade notification sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send email notification'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error handling downgrade notification: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@premium_notification_bp.route('/api/notifications/alert-saved', methods=['POST'])
def handle_alert_saved():
    """Handle alert saved notification"""
    try:
        data = request.get_json()
        
        # Extract alert data
        symbol = data.get('symbol')
        alert_type = data.get('type', 'price')
        target_value = data.get('target_value')
        condition = data.get('condition', 'above')
        
        if not symbol or not target_value:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: symbol, target_value'
            }), 400
        
        # Log alert saved
        logger.info(f"✅ Alert saved: {symbol} {alert_type} {condition} {target_value}")
        
        # Trigger browser notification
        alert_data = {
            'symbol': symbol,
            'type': alert_type,
            'target_value': target_value,
            'condition': condition,
            'message': f"{symbol} {alert_type} alert saved for {condition} {target_value}"
        }
        
        return jsonify({
            'success': True,
            'message': 'Alert saved successfully',
            'alert_data': alert_data
        })
        
    except Exception as e:
        logger.error(f"❌ Error handling alert saved: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@premium_notification_bp.route('/api/notifications/alert-triggered', methods=['POST'])
def handle_alert_triggered():
    """Handle alert triggered notification with email"""
    try:
        data = request.get_json()
        
        # Required fields
        user_email = data.get('user_email')
        user_name = data.get('user_name', 'User')
        alert_data = data.get('alert_data', {})
        
        if not user_email or not alert_data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: user_email, alert_data'
            }), 400
        
        # Send alert trigger email
        email_sent = send_alert_email(
            user_email=user_email,
            user_name=user_name,
            alert_data=alert_data
        )
        
        if email_sent:
            symbol = alert_data.get('symbol', 'Stock')
            logger.info(f"✅ Alert trigger notification sent to {user_email}: {symbol}")
            return jsonify({
                'success': True,
                'message': 'Alert trigger notification sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send email notification'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error handling alert trigger notification: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@premium_notification_bp.route('/api/notifications/test-upgrade', methods=['POST'])
def test_upgrade_notification():
    """Test endpoint for upgrade notifications (development only)"""
    try:
        # Test data
        test_data = {
            'user_email': 'tradewise.founder@gmail.com',
            'user_name': 'Test User',
            'old_plan': 'Free',
            'new_plan': 'Pro',
            'amount': 29.99
        }
        
        email_sent = send_upgrade_email(**test_data)
        
        return jsonify({
            'success': email_sent,
            'message': 'Test upgrade notification sent' if email_sent else 'Failed to send test notification',
            'test_data': test_data
        })
        
    except Exception as e:
        logger.error(f"❌ Error testing upgrade notification: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@premium_notification_bp.route('/api/notifications/test-alert', methods=['POST'])
def test_alert_notification():
    """Test endpoint for alert notifications (development only)"""
    try:
        # Test alert data
        test_alert_data = {
            'symbol': 'AAPL',
            'type': 'Price',
            'current_value': '150.25',
            'target_value': '150.00',
            'message': 'AAPL has reached your target price of $150.00'
        }
        
        email_sent = send_alert_email(
            user_email='tradewise.founder@gmail.com',
            user_name='Test User',
            alert_data=test_alert_data
        )
        
        return jsonify({
            'success': email_sent,
            'message': 'Test alert notification sent' if email_sent else 'Failed to send test notification',
            'alert_data': test_alert_data
        })
        
    except Exception as e:
        logger.error(f"❌ Error testing alert notification: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@premium_notification_bp.route('/api/notifications/health', methods=['GET'])
def notification_health_check():
    """Health check for notification system"""
    try:
        return jsonify({
            'success': True,
            'service': 'Premium Notification System',
            'status': 'operational',
            'endpoints': [
                '/api/notifications/upgrade-success',
                '/api/notifications/downgrade',
                '/api/notifications/alert-saved',
                '/api/notifications/alert-triggered'
            ],
            'email_configured': bool(os.getenv('NOTIFICATION_EMAIL_PASSWORD')),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500