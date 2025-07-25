"""
Premium routes for upgrade pages and subscription management
"""

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from premium_plan_manager import plan_manager, PLAN_CONFIGS
import logging

logger = logging.getLogger(__name__)

# Create premium routes blueprint
premium_routes_bp = Blueprint('premium_routes', __name__)

@premium_routes_bp.route('/premium/upgrade')
def premium_upgrade():
    """Premium upgrade page"""
    user_plan = session.get('user_plan', 'free')
    
    # If user is already on a premium plan, redirect to account settings
    if user_plan != 'free':
        return redirect(url_for('account_settings'))
    
    return render_template('premium_upgrade.html', 
                         current_plan=user_plan,
                         plans=PLAN_CONFIGS)

@premium_routes_bp.route('/premium/success')
def premium_success():
    """Premium upgrade success page"""
    session_id = request.args.get('session_id')
    
    # In production, you would verify the session and update user plan
    # For demo, we'll simulate upgrade to pro
    session['user_plan'] = 'pro'
    
    return render_template('premium_success.html', 
                         session_id=session_id,
                         new_plan='pro')

@premium_routes_bp.route('/premium/cancel')
def premium_cancel():
    """Premium upgrade cancellation page"""
    return render_template('premium_cancel.html')

@premium_routes_bp.route('/demo/upgrade-plan/<plan>')
def demo_upgrade_plan(plan):
    """Demo endpoint to simulate plan upgrades for testing"""
    if plan in PLAN_CONFIGS:
        session['user_plan'] = plan
        return jsonify({
            'success': True,
            'message': f'Upgraded to {plan} plan',
            'plan': plan
        })
    
    return jsonify({
        'success': False,
        'error': 'Invalid plan'
    }), 400

@premium_routes_bp.route('/demo/reset-plan')
def demo_reset_plan():
    """Demo endpoint to reset to free plan for testing"""
    session['user_plan'] = 'free'
    return jsonify({
        'success': True,
        'message': 'Reset to free plan',
        'plan': 'free'
    })

@premium_routes_bp.route('/demo/premium-features')
def demo_premium_features():
    """Demo page showing premium features with locks"""
    return render_template('demo_premium_features.html')