"""
Comprehensive Billing Routes for TradeWise AI
Full-featured subscription management with Stripe integration
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from flask_login import login_required, current_user
from models import User, Team, TeamInvitation, SubscriptionHistory, PlanConfiguration, db
from enhanced_stripe_billing import billing_manager
from enhanced_premium_features import plan_required, EnhancedPremiumFeatures
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')

@billing_bp.route('/plans')
def view_plans():
    """Display available subscription plans"""
    try:
        # Get all active plan configurations
        plans = PlanConfiguration.query.filter_by(is_active=True).all()
        
        plan_data = []
        for plan in plans:
            features = json.loads(plan.features) if plan.features else {}
            plan_info = {
                'name': plan.plan_name,
                'display_name': plan.display_name,
                'description': plan.description,
                'monthly_price': plan.monthly_price,
                'annual_price': plan.annual_price,
                'features': features,
                'limits': {
                    'api_requests_per_day': plan.api_requests_per_day,
                    'max_alerts': plan.max_alerts,
                    'max_watchlist_items': plan.max_watchlist_items,
                    'team_seats': plan.team_seats
                },
                'is_current': current_user.is_authenticated and current_user.plan_type == plan.plan_name,
                'can_upgrade': current_user.is_authenticated and current_user.plan_type != plan.plan_name
            }
            plan_data.append(plan_info)
        
        return render_template('billing/plans.html', 
                             plans=plan_data,
                             current_user_plan=current_user.plan_type if current_user.is_authenticated else 'free')
        
    except Exception as e:
        logger.error(f"Error displaying plans: {e}")
        flash('Error loading subscription plans.', 'error')
        return redirect(url_for('main.index'))

@billing_bp.route('/subscribe/<plan_type>')
@login_required
def subscribe_to_plan(plan_type):
    """Start subscription process for a specific plan"""
    try:
        billing_cycle = request.args.get('billing', 'monthly')  # monthly or annual
        team_size = int(request.args.get('team_size', 1))
        
        # Validate plan
        if plan_type not in billing_manager.plan_configs:
            flash('Invalid subscription plan.', 'error')
            return redirect(url_for('billing.view_plans'))
        
        # Check if already on this plan
        if current_user.plan_type == plan_type and current_user.is_plan_active():
            flash('You are already subscribed to this plan.', 'info')
            return redirect(url_for('billing.manage_subscription'))
        
        # Create checkout session
        result = billing_manager.create_checkout_session(
            plan_type=plan_type,
            billing_cycle=billing_cycle,
            user_id=current_user.id,
            team_size=team_size
        )
        
        if result['success']:
            return redirect(result['checkout_url'])
        else:
            flash(f'Subscription error: {result["error"]}', 'error')
            return redirect(url_for('billing.view_plans'))
            
    except Exception as e:
        logger.error(f"Subscription error: {e}")
        flash('Failed to start subscription process.', 'error')
        return redirect(url_for('billing.view_plans'))

@billing_bp.route('/success')
def payment_success():
    """Handle successful payment from Stripe"""
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            flash('Invalid payment session.', 'error')
            return redirect(url_for('billing.view_plans'))
        
        # Payment success is handled by webhook, just show confirmation
        return render_template('billing/success.html', session_id=session_id)
        
    except Exception as e:
        logger.error(f"Payment success handling error: {e}")
        flash('Payment processing error.', 'error')
        return redirect(url_for('billing.view_plans'))

@billing_bp.route('/cancel')
def payment_cancel():
    """Handle cancelled payment"""
    flash('Payment was cancelled. You can try again anytime.', 'info')
    return redirect(url_for('billing.view_plans'))

@billing_bp.route('/manage')
@login_required
def manage_subscription():
    """Subscription management dashboard"""
    try:
        # Get comprehensive subscription info
        subscription_info = billing_manager.get_subscription_info(current_user.id)
        
        if not subscription_info['success']:
            flash('Error loading subscription information.', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Get subscription history
        history = SubscriptionHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(SubscriptionHistory.created_at.desc()).limit(10).all()
        
        return render_template('billing/manage.html',
                             subscription=subscription_info['subscription'],
                             history=[h.to_dict() for h in history])
        
    except Exception as e:
        logger.error(f"Subscription management error: {e}")
        flash('Error loading subscription management.', 'error')
        return redirect(url_for('main.dashboard'))

@billing_bp.route('/portal')
@login_required
def billing_portal():
    """Redirect to Stripe Customer Portal"""
    try:
        if not current_user.stripe_customer_id:
            flash('No billing information found.', 'error')
            return redirect(url_for('billing.manage_subscription'))
        
        result = billing_manager.create_billing_portal_session(current_user.stripe_customer_id)
        
        if result['success']:
            return redirect(result['portal_url'])
        else:
            flash(f'Portal error: {result["error"]}', 'error')
            return redirect(url_for('billing.manage_subscription'))
            
    except Exception as e:
        logger.error(f"Billing portal error: {e}")
        flash('Failed to access billing portal.', 'error')
        return redirect(url_for('billing.manage_subscription'))

@billing_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    try:
        payload = request.get_data()
        signature = request.headers.get('Stripe-Signature')
        
        if not signature:
            logger.warning("Webhook received without signature")
            return jsonify({'error': 'No signature'}), 400
        
        result = billing_manager.handle_webhook_event(payload, signature)
        
        if result['success']:
            return jsonify({'status': 'success'}), 200
        else:
            logger.error(f"Webhook processing failed: {result['error']}")
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"Webhook handling error: {e}")
        return jsonify({'error': 'Webhook processing failed'}), 500

# API Endpoints for subscription management

@billing_bp.route('/api/subscription/status')
@login_required
def api_subscription_status():
    """Get detailed subscription status via API"""
    try:
        result = billing_manager.get_subscription_info(current_user.id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API subscription status error: {e}")
        return jsonify({'success': False, 'error': 'Failed to get subscription status'}), 500

@billing_bp.route('/api/plans')
def api_get_plans():
    """Get all available plans via API"""
    try:
        plans = PlanConfiguration.query.filter_by(is_active=True).all()
        
        plans_data = []
        for plan in plans:
            plan_data = plan.to_dict()
            plan_data['is_current'] = current_user.is_authenticated and current_user.plan_type == plan.plan_name
            plans_data.append(plan_data)
        
        return jsonify({
            'success': True,
            'plans': plans_data
        })
        
    except Exception as e:
        logger.error(f"API plans error: {e}")
        return jsonify({'success': False, 'error': 'Failed to get plans'}), 500

@billing_bp.route('/api/usage')
@login_required
def api_usage_stats():
    """Get current usage statistics"""
    try:
        plan_config = PlanConfiguration.query.filter_by(plan_name=current_user.plan_type).first()
        
        usage_data = {
            'api_requests': {
                'used': current_user.api_requests_today,
                'limit': plan_config.api_requests_per_day if plan_config else 50,
                'reset_date': current_user.api_requests_reset_date.isoformat() if current_user.api_requests_reset_date else None
            },
            'plan_limits': {
                'max_alerts': plan_config.max_alerts if plan_config else 3,
                'max_watchlist_items': plan_config.max_watchlist_items if plan_config else 10,
                'team_seats': plan_config.team_seats if plan_config else 1
            },
            'current_usage': {
                'alerts_count': 0,  # TODO: Implement alert counting
                'watchlist_items': 0,  # TODO: Implement watchlist counting
                'team_members': User.query.filter_by(team_id=current_user.team_id).count() if current_user.team_id else 1
            }
        }
        
        return jsonify({
            'success': True,
            'usage': usage_data
        })
        
    except Exception as e:
        logger.error(f"API usage stats error: {e}")
        return jsonify({'success': False, 'error': 'Failed to get usage stats'}), 500

# Team Management for Enterprise Plans

@billing_bp.route('/team')
@plan_required('enterprise', 'team management')
def team_dashboard():
    """Team management dashboard for Enterprise users"""
    try:
        team = None
        if current_user.team_id:
            team = Team.query.get(current_user.team_id)
        
        # Get team invitations
        invitations = []
        if team:
            invitations = TeamInvitation.query.filter_by(
                team_id=team.id,
                status='pending'
            ).all()
        
        return render_template('billing/team.html',
                             team=team,
                             invitations=[inv.to_dict() for inv in invitations],
                             can_invite=current_user.can_invite_team_members())
        
    except Exception as e:
        logger.error(f"Team dashboard error: {e}")
        flash('Error loading team dashboard.', 'error')
        return redirect(url_for('main.dashboard'))

@billing_bp.route('/api/team/create', methods=['POST'])
@plan_required('enterprise')
def api_create_team():
    """Create a new team (Enterprise only)"""
    try:
        data = request.get_json()
        team_name = data.get('name', '').strip()
        
        if not team_name:
            return jsonify({'success': False, 'error': 'Team name required'}), 400
        
        if current_user.team_id:
            return jsonify({'success': False, 'error': 'Already member of a team'}), 400
        
        # Create team
        team = Team(
            name=team_name,
            owner_id=current_user.id,
            max_seats=25  # Enterprise default
        )
        db.session.add(team)
        db.session.flush()
        
        # Add user to team
        current_user.team_id = team.id
        current_user.role = 'admin'
        
        db.session.commit()
        
        logger.info(f"Team created: {team_name} by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Team created successfully',
            'team': team.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Team creation error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to create team'}), 500

@billing_bp.route('/api/team/invite', methods=['POST'])
@plan_required('enterprise')
def api_invite_team_member():
    """Invite user to team (Enterprise only)"""
    try:
        if not current_user.can_invite_team_members():
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
        
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        role = data.get('role', 'analyst')
        
        if not email:
            return jsonify({'success': False, 'error': 'Email required'}), 400
        
        if role not in ['admin', 'analyst', 'viewer']:
            return jsonify({'success': False, 'error': 'Invalid role'}), 400
        
        team = Team.query.get(current_user.team_id)
        if not team or not team.can_add_member():
            return jsonify({'success': False, 'error': 'Team is full'}), 400
        
        # Check if already invited
        existing_invitation = TeamInvitation.query.filter_by(
            team_id=team.id,
            email=email,
            status='pending'
        ).first()
        
        if existing_invitation:
            return jsonify({'success': False, 'error': 'User already invited'}), 400
        
        # Create invitation
        invitation = TeamInvitation(
            team_id=team.id,
            email=email,
            role=role,
            invited_by=current_user.id,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        invitation.generate_token()
        
        db.session.add(invitation)
        db.session.commit()
        
        # TODO: Send invitation email
        
        logger.info(f"Team invitation sent to {email} by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Invitation sent successfully',
            'invitation': invitation.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Team invitation error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to send invitation'}), 500

@billing_bp.route('/api/team/members')
@plan_required('enterprise')
def api_get_team_members():
    """Get team members list"""
    try:
        if not current_user.team_id:
            return jsonify({'success': False, 'error': 'Not in a team'}), 400
        
        team = Team.query.get(current_user.team_id)
        members = User.query.filter_by(team_id=team.id).all()
        
        members_data = []
        for member in members:
            member_info = {
                'id': member.id,
                'username': member.username,
                'email': member.email,
                'role': member.role,
                'last_login': member.last_login.isoformat() if member.last_login else None,
                'is_owner': member.id == team.owner_id
            }
            members_data.append(member_info)
        
        return jsonify({
            'success': True,
            'team': team.to_dict(),
            'members': members_data
        })
        
    except Exception as e:
        logger.error(f"Get team members error: {e}")
        return jsonify({'success': False, 'error': 'Failed to get team members'}), 500

@billing_bp.route('/team/join/<token>')
def join_team(token):
    """Join team via invitation token"""
    try:
        invitation = TeamInvitation.query.filter_by(
            invitation_token=token,
            status='pending'
        ).first()
        
        if not invitation or invitation.is_expired():
            flash('Invalid or expired invitation.', 'error')
            return redirect(url_for('main.index'))
        
        team = Team.query.get(invitation.team_id)
        if not team or not team.can_add_member():
            flash('Team is full or no longer exists.', 'error')
            return redirect(url_for('main.index'))
        
        # Check if user is logged in
        if not current_user.is_authenticated:
            session['pending_team_invitation'] = token
            flash('Please log in to join the team.', 'info')
            return redirect(url_for('main.login'))
        
        # Check if user already in a team
        if current_user.team_id:
            flash('You are already in a team.', 'error')
            return redirect(url_for('billing.team_dashboard'))
        
        # Add user to team
        current_user.team_id = team.id
        current_user.role = invitation.role
        invitation.status = 'accepted'
        invitation.user_id = current_user.id
        
        db.session.commit()
        
        flash(f'Successfully joined team: {team.name}', 'success')
        logger.info(f"User {current_user.id} joined team {team.id}")
        
        return redirect(url_for('billing.team_dashboard'))
        
    except Exception as e:
        logger.error(f"Team join error: {e}")
        db.session.rollback()
        flash('Failed to join team.', 'error')
        return redirect(url_for('main.index'))

# Initialize plan configurations - handled in app.py instead of blueprint