"""
Premium Plan Manager
Handles user subscription plans, premium features, and billing integration
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for
from models import User, db
import logging
import stripe
import os

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Create premium plan blueprint
premium_bp = Blueprint('premium_api', __name__, url_prefix='/api')

# Plan configurations
PLAN_CONFIGS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'features': ['basic_search', 'stock_analysis', 'watchlist'],
        'limits': {
            'searches_per_day': 50,
            'watchlist_stocks': 10,
            'analysis_history': 7
        }
    },
    'pro': {
        'name': 'Pro',
        'price': 29.99,
        'stripe_price_id': 'price_1234567890',
        'features': ['all_free', 'backtesting', 'peer_comparison', 'ai_scanner', 'advanced_charts'],
        'limits': {
            'searches_per_day': 500,
            'watchlist_stocks': 100,
            'analysis_history': 90,
            'backtests_per_month': 50
        }
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 99.99,
        'stripe_price_id': 'price_0987654321',
        'features': ['all_pro', 'api_access', 'custom_alerts', 'priority_support', 'team_features'],
        'limits': {
            'searches_per_day': -1,  # unlimited
            'watchlist_stocks': -1,
            'analysis_history': -1,
            'backtests_per_month': -1,
            'team_members': 10
        }
    }
}

class PremiumPlanManager:
    def __init__(self):
        self.plans = PLAN_CONFIGS
    
    def get_user_plan(self, user_id=None):
        """Get current user's plan"""
        if user_id:
            user = User.query.get(user_id)
            return user.subscription_plan if user else 'free'
        
        # For session-based users
        return session.get('user_plan', 'free')
    
    def has_feature(self, feature, user_id=None):
        """Check if user has access to a specific feature"""
        plan = self.get_user_plan(user_id)
        plan_config = self.plans.get(plan, self.plans['free'])
        
        return feature in plan_config['features'] or 'all_free' in plan_config['features'] or 'all_pro' in plan_config['features']
    
    def get_plan_limits(self, user_id=None):
        """Get current user's plan limits"""
        plan = self.get_user_plan(user_id)
        return self.plans.get(plan, self.plans['free'])['limits']
    
    def check_usage_limit(self, limit_type, current_usage, user_id=None):
        """Check if user has exceeded usage limit"""
        limits = self.get_plan_limits(user_id)
        limit = limits.get(limit_type, 0)
        
        if limit == -1:  # unlimited
            return True
        
        return current_usage < limit
    
    def upgrade_user_plan(self, user_id, new_plan, stripe_subscription_id=None):
        """Upgrade user to new plan"""
        try:
            user = User.query.get(user_id)
            if user:
                user.subscription_plan = new_plan
                user.stripe_subscription_id = stripe_subscription_id
                db.session.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to upgrade user {user_id} to {new_plan}: {e}")
            db.session.rollback()
        
        return False

# Global plan manager instance
plan_manager = PremiumPlanManager()

@premium_bp.route('/user/plan', methods=['GET'])
def get_user_plan():
    """Get current user's plan information"""
    try:
        # For demo purposes, we'll use session-based plan detection
        user_plan = session.get('user_plan', 'free')
        plan_config = PLAN_CONFIGS.get(user_plan, PLAN_CONFIGS['free'])
        
        return jsonify({
            'success': True,
            'plan': user_plan,
            'plan_name': plan_config['name'],
            'features': plan_config['features'],
            'limits': plan_config['limits']
        })
        
    except Exception as e:
        logger.error(f"Error getting user plan: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to fetch plan information',
            'plan': 'free'
        }), 500

@premium_bp.route('/premium/check-feature', methods=['POST'])
def check_premium_feature():
    """Check if user has access to a premium feature"""
    try:
        data = request.get_json()
        feature = data.get('feature')
        
        if not feature:
            return jsonify({'success': False, 'error': 'Feature not specified'}), 400
        
        user_plan = session.get('user_plan', 'free')
        has_access = plan_manager.has_feature(feature)
        
        return jsonify({
            'success': True,
            'has_access': has_access,
            'plan': user_plan,
            'upgrade_required': not has_access
        })
        
    except Exception as e:
        logger.error(f"Error checking premium feature: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to check feature access'
        }), 500

@premium_bp.route('/stripe/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create Stripe checkout session for plan upgrade"""
    try:
        data = request.get_json()
        plan = data.get('plan', 'pro')
        success_url = data.get('success_url', request.url_root + 'premium/success')
        cancel_url = data.get('cancel_url', request.url_root + 'premium/upgrade')
        
        if plan not in PLAN_CONFIGS:
            return jsonify({'success': False, 'error': 'Invalid plan'}), 400
        
        plan_config = PLAN_CONFIGS[plan]
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(plan_config['price'] * 100),  # Convert to cents
                    'product_data': {
                        'name': f'TradeWise AI {plan_config["name"]} Plan',
                        'description': f'Monthly subscription to TradeWise AI {plan_config["name"]} features',
                    },
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            client_reference_id=session.get('user_id', 'demo_user'),
            metadata={
                'plan': plan,
                'user_plan': session.get('user_plan', 'free')
            }
        )
        
        return jsonify({
            'success': True,
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        })
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {e}")
        return jsonify({
            'success': False,
            'error': 'Payment processing error'
        }), 500
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to create checkout session'
        }), 500

@premium_bp.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks for subscription updates"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session_data = event['data']['object']
        client_reference_id = session_data.get('client_reference_id')
        plan = session_data.get('metadata', {}).get('plan', 'pro')
        subscription_id = session_data.get('subscription')
        
        # Update user plan (for demo, we'll just log it)
        logger.info(f"User {client_reference_id} upgraded to {plan} plan")
        
        # In production, you would update the user's database record here
        # plan_manager.upgrade_user_plan(client_reference_id, plan, subscription_id)
        
    elif event['type'] in ['customer.subscription.updated', 'customer.subscription.deleted']:
        subscription = event['data']['object']
        # Handle subscription changes
        logger.info(f"Subscription {subscription['id']} {event['type']}")
    
    return jsonify({'status': 'success'})

@premium_bp.route('/analytics/track', methods=['POST'])
def track_analytics():
    """Track premium feature analytics"""
    try:
        data = request.get_json()
        event = data.get('event')
        event_data = data.get('data', {})
        
        # In production, you would save this to your analytics database
        logger.info(f"Analytics event: {event} - {event_data}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error tracking analytics: {e}")
        return jsonify({'success': False}), 500

# Utility functions for templates
def get_user_plan_badge():
    """Get user plan badge HTML for templates"""
    user_plan = session.get('user_plan', 'free')
    plan_config = PLAN_CONFIGS.get(user_plan, PLAN_CONFIGS['free'])
    
    badges = {
        'free': '<span class="plan-badge free"><i class="fas fa-user"></i> Free</span>',
        'pro': '<span class="plan-badge pro"><i class="fas fa-star"></i> Pro</span>',
        'enterprise': '<span class="plan-badge enterprise"><i class="fas fa-crown"></i> Enterprise</span>'
    }
    
    return badges.get(user_plan, badges['free'])

def should_show_upgrade_button():
    """Check if upgrade button should be shown"""
    return session.get('user_plan', 'free') == 'free'

def premium_required(feature):
    """Decorator to check if user has premium access to a feature"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if not plan_manager.has_feature(feature):
                return jsonify({
                    'success': False,
                    'error': 'Premium feature requires upgrade',
                    'feature': feature,
                    'upgrade_required': True
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Make utilities available to templates
from flask import current_app

def register_premium_template_functions(app):
    """Register premium functions for use in templates"""
    app.jinja_env.globals.update({
        'get_user_plan_badge': get_user_plan_badge,
        'should_show_upgrade_button': should_show_upgrade_button,
        'user_plan': lambda: session.get('user_plan', 'free')
    })