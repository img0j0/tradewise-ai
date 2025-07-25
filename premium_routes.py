"""
Premium Routes for TradeWise AI
Handles premium subscription and premium-only features
"""

from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from premium_features import PremiumFeatures, premium_required
from models import User, db
from payment_processor import payment_processor
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

premium_bp = Blueprint('premium', __name__, url_prefix='/premium')

@premium_bp.route('/upgrade')
@premium_required
def upgrade_page():
    """Premium upgrade page"""
    canceled = request.args.get('canceled') == 'true'
    return render_template('premium_upgrade.html', payment_canceled=canceled)

@premium_bp.route('/purchase', methods=['POST'])
@premium_required
def create_checkout_session():
    """Create Stripe checkout session for premium subscription"""
    try:
        result = payment_processor.create_premium_subscription()
        
        if result['success']:
            return jsonify({
                'success': True,
                'checkout_url': result['checkout_url']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logging.error(f"Checkout session creation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Payment processing error. Please try again.'
        }), 500

@premium_bp.route('/success')
def payment_success():
    """Handle successful payment"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        return redirect(url_for('premium.upgrade_page'))
    
    # Verify the payment session
    result = payment_processor.verify_session(session_id)
    
    if result['success']:
        # TODO: Update user's subscription status in database
        # user_id = session.get('user_id')
        # if user_id:
        #     user = User.query.get(user_id)
        #     if user:
        #         user.is_premium = True
        #         user.stripe_customer_id = result['customer_id']
        #         user.stripe_subscription_id = result['subscription_id']
        #         db.session.commit()
        
        return render_template('payment_success.html', 
                             customer_email=result.get('customer_email'),
                             subscription_id=result.get('subscription_id'))
    else:
        return redirect(url_for('premium.upgrade_page', error='payment_verification_failed'))

@premium_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks with signature verification"""
    payload = request.get_data()
    signature = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    if not endpoint_secret:
        logger.error("Stripe webhook secret not configured")
        return jsonify({'error': 'Webhook not configured'}), 400
    
    # Verify webhook signature
    result = payment_processor.verify_webhook_signature(payload, signature, endpoint_secret)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    event = result['event']
    
    # Handle different event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # TODO: Update user subscription status in database
        logger.info(f"Checkout completed for session: {session['id']}")
        
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        logger.info(f"Payment succeeded for invoice: {invoice['id']}")
        
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        logger.info(f"Subscription canceled: {subscription['id']}")
    
    return jsonify({'status': 'success'}), 200

@premium_bp.route('/cancel')
def payment_cancel():
    """Handle canceled payment"""
    return redirect(url_for('premium.upgrade_page', canceled='true'))

@premium_bp.route('/api/portfolio/optimization')
@premium_required
def portfolio_optimization():
    """Premium API: Portfolio optimization suggestions"""
    try:
        user_id = session.get('user_id')
        
        # Get user's portfolio/watchlist symbols
        # For now, use some sample symbols - integrate with actual portfolio later
        portfolio_symbols = request.args.get('symbols', 'AAPL,GOOGL,MSFT').split(',')
        
        optimization_data = PremiumFeatures.get_portfolio_optimization_suggestions(
            portfolio_symbols, user_id
        )
        
        return jsonify({
            'success': True,
            'optimization': optimization_data
        })
        
    except Exception as e:
        logger.error(f"Portfolio optimization API error: {e}")
        return jsonify({'success': False, 'error': 'Portfolio optimization failed'}), 500

@premium_bp.route('/api/market/scanner')
@premium_required  
def ai_market_scanner():
    """Premium API: AI Market Scanner"""
    try:
        scanner_data = PremiumFeatures.get_ai_market_scanner()
        
        return jsonify({
            'success': True,
            'scanner': scanner_data
        })
        
    except Exception as e:
        logger.error(f"Market scanner API error: {e}")
        return jsonify({'success': False, 'error': 'Market scanner failed'}), 500

@premium_bp.route('/api/earnings/prediction/<symbol>')
@premium_required
def earnings_prediction(symbol):
    """Premium API: Earnings predictions"""
    try:
        prediction_data = PremiumFeatures.get_earnings_predictions(symbol.upper())
        
        return jsonify({
            'success': True,
            'prediction': prediction_data
        })
        
    except Exception as e:
        logger.error(f"Earnings prediction API error: {e}")
        return jsonify({'success': False, 'error': 'Earnings prediction failed'}), 500

@premium_bp.route('/api/subscription/status')
def subscription_status():
    """Get user's subscription status"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'subscription': {
                'tier': user.subscription_tier,
                'status': user.subscription_status,
                'is_active': user.is_premium_active(),
                'start_date': user.subscription_start.isoformat() if user.subscription_start else None,
                'end_date': user.subscription_end.isoformat() if user.subscription_end else None
            }
        })
        
    except Exception as e:
        logger.error(f"Subscription status error: {e}")
        return jsonify({'success': False, 'error': 'Status check failed'}), 500

@premium_bp.route('/api/subscription/demo-upgrade', methods=['POST'])
def demo_upgrade():
    """Demo upgrade for testing (in production, integrate with Stripe)"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Demo upgrade - in production, this would be handled by Stripe webhooks
        user.subscription_tier = 'premium'
        user.subscription_status = 'active'
        user.subscription_start = datetime.utcnow()
        user.subscription_end = datetime.utcnow() + timedelta(days=30)  # 30-day trial
        
        db.session.commit()
        
        logger.info(f"Demo upgrade successful for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Premium activated! Welcome to TradeWise AI Premium.',
            'subscription': {
                'tier': user.subscription_tier,
                'status': user.subscription_status,
                'end_date': user.subscription_end.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Demo upgrade error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Upgrade failed'}), 500