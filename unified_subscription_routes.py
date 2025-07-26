"""
Unified Subscription Routes for TradeWise AI
Handles all subscription-related functionality with full Pro and Enterprise support
"""

from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, current_app
from comprehensive_subscription_manager import subscription_manager
from models import User, db
import logging
import os

logger = logging.getLogger(__name__)

# Create unified subscription blueprint
subscription_bp = Blueprint('subscription', __name__, url_prefix='/subscription')

@subscription_bp.route('/billing')
def billing_management():
    """Comprehensive billing management page"""
    try:
        return render_template('billing_management.html')
    except Exception as e:
        logger.error(f"Error loading billing page: {e}")
        return jsonify({'error': 'Billing page loading error'}), 500

@subscription_bp.route('/api/current-plan')
def get_current_plan():
    """Get user's current plan and details"""
    try:
        user_id = session.get('user_id')
        plan = subscription_manager.get_user_plan(user_id)
        plan_config = subscription_manager.get_plan_config(plan)
        
        return jsonify({
            'success': True,
            'plan': plan,
            'config': plan_config,
            'theme': subscription_manager.get_plan_theme_data(plan)
        })
    except Exception as e:
        logger.error(f"Error getting current plan: {e}")
        return jsonify({'success': False, 'error': 'Failed to get plan details'}), 500

@subscription_bp.route('/api/usage-limits')
def get_usage_limits():
    """Get user's current usage against plan limits"""
    try:
        user_id = session.get('user_id')
        
        limits = {}
        for limit_type in ['api_requests_per_day', 'max_alerts', 'max_watchlist_items', 'portfolio_holdings_limit']:
            limits[limit_type] = subscription_manager.check_usage_limits(limit_type, user_id)
        
        return jsonify({
            'success': True,
            'limits': limits
        })
    except Exception as e:
        logger.error(f"Error getting usage limits: {e}")
        return jsonify({'success': False, 'error': 'Failed to get usage data'}), 500

@subscription_bp.route('/api/plan-comparison')
def get_plan_comparison():
    """Get plan comparison data for UI"""
    try:
        comparison_data = subscription_manager.get_plan_comparison()
        user_plan = subscription_manager.get_user_plan(session.get('user_id'))
        
        return jsonify({
            'success': True,
            'comparison': comparison_data,
            'current_plan': user_plan
        })
    except Exception as e:
        logger.error(f"Error getting plan comparison: {e}")
        return jsonify({'success': False, 'error': 'Failed to get plan comparison'}), 500

@subscription_bp.route('/checkout')
def checkout_page():
    """Subscription checkout page"""
    try:
        plan = request.args.get('plan', 'pro')
        billing_cycle = request.args.get('cycle', 'monthly')
        
        # Validate plan
        if plan not in ['pro', 'enterprise']:
            return redirect(url_for('subscription.billing_management'))
        
        plan_config = subscription_manager.get_plan_config(plan)
        
        return render_template('subscription_checkout.html', 
                             plan=plan,
                             billing_cycle=billing_cycle,
                             plan_config=plan_config)
    except Exception as e:
        logger.error(f"Error loading checkout page: {e}")
        return redirect(url_for('subscription.billing_management'))

@subscription_bp.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create Stripe checkout session for subscription"""
    try:
        data = request.get_json()
        plan = data.get('plan', 'pro')
        billing_cycle = data.get('billing_cycle', 'monthly')
        user_id = session.get('user_id')
        
        # Create checkout session
        result = subscription_manager.create_checkout_session(plan, billing_cycle, user_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'checkout_url': result['checkout_url'],
                'session_id': result['session_id']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"Checkout session creation error: {e}")
        return jsonify({
            'success': False,
            'error': 'Checkout creation failed. Please try again.'
        }), 500

@subscription_bp.route('/success')
def subscription_success():
    """Handle successful subscription"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return redirect(url_for('subscription.billing_management'))
        
        # Verify the subscription
        result = subscription_manager.verify_checkout_session(session_id)
        
        if result['success']:
            # Update session for immediate UI update
            session['user_plan'] = result['plan']
            
            return render_template('subscription_success.html',
                                 plan=result['plan'],
                                 billing_cycle=result.get('billing_cycle', 'monthly'),
                                 customer_email=result.get('customer_email'))
        else:
            return redirect(url_for('subscription.billing_management', error='verification_failed'))
            
    except Exception as e:
        logger.error(f"Subscription success error: {e}")
        return redirect(url_for('subscription.billing_management', error='processing_failed'))

@subscription_bp.route('/cancel')
def subscription_cancel():
    """Handle canceled subscription purchase"""
    return render_template('subscription_cancel.html')

@subscription_bp.route('/api/cancel-subscription', methods=['POST'])
def cancel_subscription():
    """Cancel user's subscription"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        result = subscription_manager.cancel_subscription(user_id)
        
        if result['success']:
            # Update session
            session['user_plan'] = 'free'
            
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Subscription cancellation error: {e}")
        return jsonify({
            'success': False,
            'error': 'Cancellation failed. Please contact support.'
        }), 500

@subscription_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    try:
        payload = request.get_data()
        signature = request.headers.get('Stripe-Signature')
        
        # Verify webhook signature (would implement in production)
        # For now, just log the event
        logger.info("Stripe webhook received")
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': 'Webhook processing failed'}), 400

# Feature access control decorators
def require_plan(required_plan):
    """Decorator to require specific plan level"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            user_plan = subscription_manager.get_user_plan(user_id)
            
            plan_hierarchy = {'free': 0, 'pro': 1, 'enterprise': 2}
            user_level = plan_hierarchy.get(user_plan, 0)
            required_level = plan_hierarchy.get(required_plan, 0)
            
            if user_level < required_level:
                return jsonify({
                    'success': False,
                    'error': f'{required_plan.title()} plan required',
                    'required_plan': required_plan,
                    'current_plan': user_plan,
                    'upgrade_required': True
                }), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_feature(feature_name):
    """Decorator to require specific feature access"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            
            if not subscription_manager.has_feature_access(feature_name, user_id):
                user_plan = subscription_manager.get_user_plan(user_id)
                
                return jsonify({
                    'success': False,
                    'error': f'Feature "{feature_name}" requires upgrade',
                    'feature': feature_name,
                    'current_plan': user_plan,
                    'upgrade_required': True
                }), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Demo routes for testing
@subscription_bp.route('/demo/upgrade/<plan>')
def demo_upgrade(plan):
    """Demo route to simulate plan upgrades"""
    if plan in ['free', 'pro', 'enterprise']:
        session['user_plan'] = plan
        logger.info(f"Demo upgrade to {plan} plan")
        return jsonify({'success': True, 'plan': plan})
    else:
        return jsonify({'success': False, 'error': 'Invalid plan'}), 400

# Template filters and functions
@subscription_bp.app_template_filter('plan_badge')
def plan_badge_filter(plan):
    """Template filter for plan badges"""
    theme = subscription_manager.get_plan_theme_data(plan)
    return f'<span class="plan-badge {plan}"><i class="{theme["icon"]}"></i> {theme["display_name"]}</span>'

@subscription_bp.app_template_global('has_feature')
def has_feature_global(feature):
    """Template global function to check feature access"""
    user_id = session.get('user_id')
    return subscription_manager.has_feature_access(feature, user_id)

@subscription_bp.app_template_global('get_user_plan')
def get_user_plan_global():
    """Template global function to get current user plan"""
    user_id = session.get('user_id')
    return subscription_manager.get_user_plan(user_id)

@subscription_bp.app_template_global('get_plan_theme')
def get_plan_theme_global(plan=None):
    """Template global function to get plan theme data"""
    if not plan:
        user_id = session.get('user_id')
        plan = subscription_manager.get_user_plan(user_id)
    return subscription_manager.get_plan_theme_data(plan)