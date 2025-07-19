"""
Premium Features Routes
API endpoints for AI Trading Copilot and subscription management
"""

from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from ai_trading_copilot import ai_copilot
from models import db, User
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

premium_bp = Blueprint('premium', __name__, url_prefix='/api/premium')

@premium_bp.route('/subscribe', methods=['POST'])
@login_required
def subscribe_premium():
    """Subscribe user to premium plan"""
    try:
        data = request.get_json()
        plan_type = data.get('plan', 'pro')  # 'pro' or 'elite'
        
        # In production, integrate with Stripe for payment processing
        # For now, simulate subscription activation
        
        user = current_user
        if plan_type == 'elite':
            user.subscription_type = 'elite'
            user.subscription_expires = datetime.now() + timedelta(days=30)
            monthly_price = 39.99
        else:
            user.subscription_type = 'pro'
            user.subscription_expires = datetime.now() + timedelta(days=30)
            monthly_price = 19.99
        
        db.session.commit()
        
        # Add user to AI copilot subscribers
        ai_copilot.add_subscriber(str(user.id))
        
        logger.info(f"User {user.id} subscribed to {plan_type} plan")
        
        return jsonify({
            'success': True,
            'plan': plan_type,
            'price': monthly_price,
            'expires': user.subscription_expires.isoformat(),
            'message': f'Welcome to AI Copilot {plan_type.title()}! Your AI assistant is now monitoring markets 24/7.'
        })
        
    except Exception as e:
        logger.error(f"Error subscribing user: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@premium_bp.route('/status', methods=['GET'])
@login_required
def premium_status():
    """Get user's premium subscription status"""
    try:
        user = current_user
        
        is_premium = (
            hasattr(user, 'subscription_type') and 
            user.subscription_type in ['pro', 'elite'] and
            hasattr(user, 'subscription_expires') and
            user.subscription_expires > datetime.now()
        )
        
        return jsonify({
            'is_premium': is_premium,
            'plan': getattr(user, 'subscription_type', 'free'),
            'expires': getattr(user, 'subscription_expires', None),
            'copilot_active': str(user.id) in ai_copilot.subscribers if is_premium else False
        })
        
    except Exception as e:
        logger.error(f"Error checking premium status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@premium_bp.route('/copilot/signals', methods=['GET'])
@login_required
def get_copilot_signals():
    """Get recent AI trading signals for premium users"""
    try:
        user = current_user
        
        # Check if user has premium subscription
        is_premium = (
            hasattr(user, 'subscription_type') and 
            user.subscription_type in ['pro', 'elite'] and
            hasattr(user, 'subscription_expires') and
            user.subscription_expires > datetime.now()
        )
        
        if not is_premium:
            return jsonify({
                'success': False,
                'error': 'Premium subscription required',
                'upgrade_message': 'Upgrade to AI Copilot Pro to access real-time trading signals'
            }), 403
        
        limit = request.args.get('limit', 10, type=int)
        signals = ai_copilot.get_recent_signals(limit)
        
        return jsonify({
            'success': True,
            'signals': signals,
            'count': len(signals)
        })
        
    except Exception as e:
        logger.error(f"Error fetching copilot signals: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@premium_bp.route('/copilot/status', methods=['GET'])
@login_required
def copilot_status():
    """Get AI copilot system status"""
    try:
        user = current_user
        
        is_premium = (
            hasattr(user, 'subscription_type') and 
            user.subscription_type in ['pro', 'elite'] and
            hasattr(user, 'subscription_expires') and
            user.subscription_expires > datetime.now()
        )
        
        status = ai_copilot.get_copilot_status()
        
        return jsonify({
            'success': True,
            'user_premium': is_premium,
            'user_subscribed': str(user.id) in ai_copilot.subscribers if is_premium else False,
            'copilot_status': status
        })
        
    except Exception as e:
        logger.error(f"Error getting copilot status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@premium_bp.route('/copilot/start', methods=['POST'])
@login_required
def start_copilot():
    """Start AI copilot monitoring for user"""
    try:
        user = current_user
        
        is_premium = (
            hasattr(user, 'subscription_type') and 
            user.subscription_type in ['pro', 'elite'] and
            hasattr(user, 'subscription_expires') and
            user.subscription_expires > datetime.now()
        )
        
        if not is_premium:
            return jsonify({
                'success': False,
                'error': 'Premium subscription required'
            }), 403
        
        # Start the copilot if not already running
        if not ai_copilot.is_monitoring:
            ai_copilot.start_monitoring()
        
        # Add user to subscribers
        ai_copilot.add_subscriber(str(user.id))
        
        return jsonify({
            'success': True,
            'message': 'AI Copilot activated! Monitoring markets for opportunities...',
            'monitoring': ai_copilot.is_monitoring
        })
        
    except Exception as e:
        logger.error(f"Error starting copilot: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@premium_bp.route('/copilot/stop', methods=['POST'])
@login_required
def stop_copilot():
    """Stop AI copilot monitoring for user"""
    try:
        user = current_user
        ai_copilot.remove_subscriber(str(user.id))
        
        return jsonify({
            'success': True,
            'message': 'AI Copilot paused for your account'
        })
        
    except Exception as e:
        logger.error(f"Error stopping copilot: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@premium_bp.route('/features', methods=['GET'])
def premium_features():
    """Get available premium features and pricing"""
    return jsonify({
        'success': True,
        'plans': {
            'free': {
                'name': 'Free',
                'price': 0,
                'features': [
                    'Basic stock search',
                    '3 AI insights per day',
                    'Manual trading',
                    '0.25% commission per trade'
                ]
            },
            'pro': {
                'name': 'AI Copilot Pro',
                'price': 19.99,
                'features': [
                    'Unlimited AI insights',
                    '5 real-time alerts per day',
                    'Commission-free trading',
                    'Basic portfolio optimization',
                    'Email support'
                ]
            },
            'elite': {
                'name': 'AI Copilot Elite',
                'price': 39.99,
                'features': [
                    '24/7 AI market monitoring',
                    'Unlimited real-time alerts',
                    'One-click AI trade execution',
                    'Live voice commentary',
                    'Predictive market signals',
                    'Advanced risk management',
                    'Priority support',
                    'Custom watchlists'
                ]
            }
        }
    })