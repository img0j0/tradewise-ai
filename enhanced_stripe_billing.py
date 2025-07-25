"""
Enhanced Stripe Billing Integration for TradeWise AI
Comprehensive subscription management with multiple tiers
"""

import stripe
import os
import logging
import json
from datetime import datetime, timedelta
from flask import session, request
from models import User, Team, SubscriptionHistory, PlanConfiguration, db
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class StripeBillingManager:
    """Enhanced Stripe billing manager for multiple plan tiers"""
    
    def __init__(self):
        self.stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')
        if not self.stripe_secret_key:
            logger.warning("STRIPE_SECRET_KEY not configured - Stripe integration disabled")
            return
        
        stripe.api_key = self.stripe_secret_key
        self.webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
        
        # Plan configurations
        self.plan_configs = {
            'free': {
                'display_name': 'Free',
                'monthly_price': 0,
                'annual_price': 0,
                'api_requests_per_day': 50,
                'max_alerts': 3,
                'max_watchlist_items': 10,
                'team_seats': 1,
                'features': {
                    'basic_analysis': True,
                    'ai_insights': False,
                    'portfolio_optimization': False,
                    'advanced_alerts': False,
                    'market_scanner': False,
                    'earnings_predictions': False,
                    'team_collaboration': False,
                    'priority_support': False,
                    'custom_reports': False
                }
            },
            'pro': {
                'display_name': 'Pro',
                'monthly_price': 29.99,
                'annual_price': 299.99,
                'stripe_monthly_price_id': os.environ.get('STRIPE_PRO_MONTHLY_PRICE_ID'),
                'stripe_annual_price_id': os.environ.get('STRIPE_PRO_ANNUAL_PRICE_ID'),
                'api_requests_per_day': 1000,
                'max_alerts': 50,
                'max_watchlist_items': 100,
                'team_seats': 1,
                'trial_days': 14,
                'features': {
                    'basic_analysis': True,
                    'ai_insights': True,
                    'portfolio_optimization': True,
                    'advanced_alerts': True,
                    'market_scanner': True,
                    'earnings_predictions': True,
                    'team_collaboration': False,
                    'priority_support': True,
                    'custom_reports': True
                }
            },
            'enterprise': {
                'display_name': 'Enterprise',
                'monthly_price': 99.99,
                'annual_price': 999.99,
                'stripe_monthly_price_id': os.environ.get('STRIPE_ENTERPRISE_MONTHLY_PRICE_ID'),
                'stripe_annual_price_id': os.environ.get('STRIPE_ENTERPRISE_ANNUAL_PRICE_ID'),
                'api_requests_per_day': 10000,
                'max_alerts': 200,
                'max_watchlist_items': 500,
                'team_seats': 25,
                'trial_days': 14,
                'features': {
                    'basic_analysis': True,
                    'ai_insights': True,
                    'portfolio_optimization': True,
                    'advanced_alerts': True,
                    'market_scanner': True,
                    'earnings_predictions': True,
                    'team_collaboration': True,
                    'priority_support': True,
                    'custom_reports': True,
                    'api_access': True,
                    'white_label': True,
                    'dedicated_support': True
                }
            }
        }
    
    def initialize_plan_configurations(self):
        """Initialize plan configurations in database"""
        try:
            for plan_name, config in self.plan_configs.items():
                existing_plan = PlanConfiguration.query.filter_by(plan_name=plan_name).first()
                
                if not existing_plan:
                    plan = PlanConfiguration(
                        plan_name=plan_name,
                        display_name=config['display_name'],
                        description=f"{config['display_name']} plan with advanced features",
                        monthly_price=config['monthly_price'],
                        annual_price=config['annual_price'],
                        stripe_monthly_price_id=config.get('stripe_monthly_price_id'),
                        stripe_annual_price_id=config.get('stripe_annual_price_id'),
                        api_requests_per_day=config['api_requests_per_day'],
                        max_alerts=config['max_alerts'],
                        max_watchlist_items=config['max_watchlist_items'],
                        team_seats=config['team_seats'],
                        features=json.dumps(config['features'])
                    )
                    db.session.add(plan)
            
            db.session.commit()
            logger.info("Plan configurations initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing plan configurations: {e}")
            db.session.rollback()
    
    def create_checkout_session(self, plan_type: str, billing_cycle: str = 'monthly', 
                              user_id: Optional[int] = None, team_size: int = 1) -> Dict:
        """Create Stripe checkout session for subscription"""
        try:
            if not self.stripe_secret_key:
                return {'success': False, 'error': 'Stripe not configured'}
            
            if plan_type not in self.plan_configs:
                return {'success': False, 'error': 'Invalid plan type'}
            
            plan_config = self.plan_configs[plan_type]
            
            # Get price ID based on billing cycle
            if billing_cycle == 'annual':
                price_id = plan_config.get('stripe_annual_price_id')
            else:
                price_id = plan_config.get('stripe_monthly_price_id')
            
            if not price_id:
                return {'success': False, 'error': 'Price not configured for this plan'}
            
            # Get or create customer
            customer_id = None
            customer_email = None
            
            if user_id:
                user = User.query.get(user_id)
                if user:
                    customer_email = user.email
                    if user.stripe_customer_id:
                        customer_id = user.stripe_customer_id
                    else:
                        # Create new customer
                        customer = stripe.Customer.create(
                            email=user.email,
                            metadata={'user_id': user_id}
                        )
                        customer_id = customer.id
                        user.stripe_customer_id = customer_id
                        db.session.commit()
            
            # Create line items
            line_items = [{
                'price': price_id,
                'quantity': team_size if plan_type == 'enterprise' else 1
            }]
            
            # Session parameters
            success_url = f"{request.host_url}billing/success?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{request.host_url}billing/cancel"
            
            session_params = {
                'payment_method_types': ['card'],
                'line_items': line_items,
                'mode': 'subscription',
                'success_url': success_url,
                'cancel_url': cancel_url,
                'metadata': {
                    'plan_type': plan_type,
                    'billing_cycle': billing_cycle,
                    'user_id': str(user_id) if user_id else '',
                    'team_size': str(team_size)
                }
            }
            
            # Add customer if available
            if customer_id:
                session_params['customer'] = customer_id
            elif customer_email:
                session_params['customer_email'] = customer_email
            
            # Add trial if configured
            if plan_config.get('trial_days') and billing_cycle == 'monthly':
                session_params['subscription_data'] = {
                    'trial_period_days': plan_config['trial_days']
                }
            
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(**session_params)
            
            return {
                'success': True,
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            return {'success': False, 'error': 'Failed to create checkout session'}
    
    def create_billing_portal_session(self, customer_id: str) -> Dict:
        """Create Stripe customer portal session for self-service billing"""
        try:
            if not self.stripe_secret_key:
                return {'success': False, 'error': 'Stripe not configured'}
            
            portal_session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=f"{request.host_url}settings/billing"
            )
            
            return {
                'success': True,
                'portal_url': portal_session.url
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating portal session: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error creating portal session: {e}")
            return {'success': False, 'error': 'Failed to create portal session'}
    
    def handle_webhook_event(self, payload: bytes, signature: str) -> Dict:
        """Handle Stripe webhook events with signature verification"""
        try:
            if not self.webhook_secret:
                return {'success': False, 'error': 'Webhook secret not configured'}
            
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            # Handle different event types
            if event['type'] == 'checkout.session.completed':
                return self._handle_checkout_completed(event['data']['object'])
            
            elif event['type'] == 'customer.subscription.created':
                return self._handle_subscription_created(event['data']['object'])
            
            elif event['type'] == 'customer.subscription.updated':
                return self._handle_subscription_updated(event['data']['object'])
            
            elif event['type'] == 'customer.subscription.deleted':
                return self._handle_subscription_deleted(event['data']['object'])
            
            elif event['type'] == 'invoice.payment_succeeded':
                return self._handle_payment_succeeded(event['data']['object'])
            
            elif event['type'] == 'invoice.payment_failed':
                return self._handle_payment_failed(event['data']['object'])
            
            else:
                logger.info(f"Unhandled webhook event type: {event['type']}")
                return {'success': True, 'message': 'Event received but not processed'}
            
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return {'success': False, 'error': 'Invalid signature'}
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return {'success': False, 'error': 'Webhook processing failed'}
    
    def _handle_checkout_completed(self, session) -> Dict:
        """Handle successful checkout completion"""
        try:
            user_id = session['metadata'].get('user_id')
            if not user_id:
                return {'success': False, 'error': 'User ID not found in session metadata'}
            
            user = User.query.get(int(user_id))
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Update user subscription details
            plan_type = session['metadata'].get('plan_type', 'pro')
            billing_cycle = session['metadata'].get('billing_cycle', 'monthly')
            
            user.plan_type = plan_type
            user.subscription_status = 'active'
            user.stripe_customer_id = session['customer']
            user.subscription_start = datetime.utcnow()
            
            # Set trial end date if applicable
            if session.get('subscription'):
                subscription = stripe.Subscription.retrieve(session['subscription'])
                if subscription.trial_end:
                    user.trial_end_date = datetime.fromtimestamp(subscription.trial_end)
                user.stripe_subscription_id = subscription.id
                user.stripe_price_id = subscription['items']['data'][0]['price']['id']
            
            db.session.commit()
            
            # Log subscription history
            self._log_subscription_history(
                user_id=user.id,
                plan_type=plan_type,
                action='subscribed',
                amount=session.get('amount_total', 0) / 100,  # Convert from cents
                stripe_payment_intent_id=session.get('payment_intent'),
                additional_data={'billing_cycle': billing_cycle, 'session_id': session['id']}
            )
            
            logger.info(f"Subscription activated for user {user_id}, plan: {plan_type}")
            return {'success': True, 'message': 'Subscription activated'}
            
        except Exception as e:
            logger.error(f"Error handling checkout completion: {e}")
            db.session.rollback()
            return {'success': False, 'error': 'Failed to process checkout completion'}
    
    def _handle_subscription_created(self, subscription) -> Dict:
        """Handle subscription creation"""
        try:
            customer_id = subscription['customer']
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            
            if user:
                user.stripe_subscription_id = subscription['id']
                user.subscription_status = subscription['status']
                
                if subscription['trial_end']:
                    user.trial_end_date = datetime.fromtimestamp(subscription['trial_end'])
                
                db.session.commit()
                logger.info(f"Subscription created for user {user.id}")
            
            return {'success': True, 'message': 'Subscription created'}
            
        except Exception as e:
            logger.error(f"Error handling subscription creation: {e}")
            return {'success': False, 'error': 'Failed to process subscription creation'}
    
    def _handle_subscription_updated(self, subscription) -> Dict:
        """Handle subscription updates (upgrades, downgrades, etc.)"""
        try:
            customer_id = subscription['customer']
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            
            if user:
                old_plan = user.plan_type
                user.subscription_status = subscription['status']
                
                # Determine new plan type from price ID
                price_id = subscription['items']['data'][0]['price']['id']
                new_plan = self._get_plan_from_price_id(price_id)
                
                if new_plan and new_plan != old_plan:
                    user.plan_type = new_plan
                    
                    # Log the change
                    action = 'upgraded' if self._is_plan_upgrade(old_plan, new_plan) else 'downgraded'
                    self._log_subscription_history(
                        user_id=user.id,
                        plan_type=new_plan,
                        action=action,
                        additional_data={'old_plan': old_plan, 'subscription_id': subscription['id']}
                    )
                
                db.session.commit()
                logger.info(f"Subscription updated for user {user.id}")
            
            return {'success': True, 'message': 'Subscription updated'}
            
        except Exception as e:
            logger.error(f"Error handling subscription update: {e}")
            return {'success': False, 'error': 'Failed to process subscription update'}
    
    def _handle_subscription_deleted(self, subscription) -> Dict:
        """Handle subscription cancellation"""
        try:
            customer_id = subscription['customer']
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            
            if user:
                old_plan = user.plan_type
                user.plan_type = 'free'
                user.subscription_status = 'canceled'
                user.subscription_end = datetime.utcnow()
                
                # Log cancellation
                self._log_subscription_history(
                    user_id=user.id,
                    plan_type='free',
                    action='canceled',
                    additional_data={'old_plan': old_plan, 'subscription_id': subscription['id']}
                )
                
                db.session.commit()
                logger.info(f"Subscription canceled for user {user.id}")
            
            return {'success': True, 'message': 'Subscription canceled'}
            
        except Exception as e:
            logger.error(f"Error handling subscription deletion: {e}")
            return {'success': False, 'error': 'Failed to process subscription cancellation'}
    
    def _handle_payment_succeeded(self, invoice) -> Dict:
        """Handle successful payment"""
        try:
            customer_id = invoice['customer']
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            
            if user:
                # Log successful payment
                self._log_subscription_history(
                    user_id=user.id,
                    plan_type=user.plan_type,
                    action='renewed',
                    amount=invoice['amount_paid'] / 100,  # Convert from cents
                    stripe_invoice_id=invoice['id'],
                    additional_data={'invoice_id': invoice['id']}
                )
                
                logger.info(f"Payment succeeded for user {user.id}, amount: ${invoice['amount_paid']/100}")
            
            return {'success': True, 'message': 'Payment processed'}
            
        except Exception as e:
            logger.error(f"Error handling payment success: {e}")
            return {'success': False, 'error': 'Failed to process payment success'}
    
    def _handle_payment_failed(self, invoice) -> Dict:
        """Handle failed payment"""
        try:
            customer_id = invoice['customer']
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            
            if user:
                user.subscription_status = 'past_due'
                db.session.commit()
                
                logger.warning(f"Payment failed for user {user.id}, invoice: {invoice['id']}")
                
                # TODO: Send notification email to user about payment failure
            
            return {'success': True, 'message': 'Payment failure processed'}
            
        except Exception as e:
            logger.error(f"Error handling payment failure: {e}")
            return {'success': False, 'error': 'Failed to process payment failure'}
    
    def _log_subscription_history(self, user_id: int, plan_type: str, action: str, 
                                amount: float = None, currency: str = 'USD',
                                stripe_invoice_id: str = None, stripe_payment_intent_id: str = None,
                                additional_data: Dict = None):
        """Log subscription history entry"""
        try:
            history_entry = SubscriptionHistory(
                user_id=user_id,
                plan_type=plan_type,
                action=action,
                amount=amount,
                currency=currency,
                stripe_invoice_id=stripe_invoice_id,
                stripe_payment_intent_id=stripe_payment_intent_id,
                additional_data=json.dumps(additional_data) if additional_data else None
            )
            db.session.add(history_entry)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error logging subscription history: {e}")
            db.session.rollback()
    
    def _get_plan_from_price_id(self, price_id: str) -> Optional[str]:
        """Determine plan type from Stripe price ID"""
        for plan_name, config in self.plan_configs.items():
            if (config.get('stripe_monthly_price_id') == price_id or 
                config.get('stripe_annual_price_id') == price_id):
                return plan_name
        return None
    
    def _is_plan_upgrade(self, old_plan: str, new_plan: str) -> bool:
        """Check if plan change is an upgrade"""
        plan_hierarchy = {'free': 0, 'pro': 1, 'enterprise': 2}
        return plan_hierarchy.get(new_plan, 0) > plan_hierarchy.get(old_plan, 0)
    
    def get_subscription_info(self, user_id: int) -> Dict:
        """Get comprehensive subscription information for a user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            plan_config = self.plan_configs.get(user.plan_type, self.plan_configs['free'])
            
            subscription_info = {
                'user_id': user_id,
                'plan_type': user.plan_type,
                'plan_display_name': plan_config['display_name'],
                'subscription_status': user.subscription_status,
                'is_active': user.is_plan_active(),
                'is_premium': user.is_premium_active(),
                'trial_end_date': user.trial_end_date.isoformat() if user.trial_end_date else None,
                'subscription_start': user.subscription_start.isoformat() if user.subscription_start else None,
                'subscription_end': user.subscription_end.isoformat() if user.subscription_end else None,
                'features': plan_config['features'],
                'limits': {
                    'api_requests_per_day': plan_config['api_requests_per_day'],
                    'max_alerts': plan_config['max_alerts'],
                    'max_watchlist_items': plan_config['max_watchlist_items'],
                    'team_seats': plan_config['team_seats']
                },
                'usage': {
                    'api_requests_today': user.api_requests_today,
                    'api_requests_reset_date': user.api_requests_reset_date.isoformat() if user.api_requests_reset_date else None
                },
                'can_upgrade': user.plan_type != 'enterprise',
                'can_manage_billing': bool(user.stripe_customer_id)
            }
            
            return {'success': True, 'subscription': subscription_info}
            
        except Exception as e:
            logger.error(f"Error getting subscription info: {e}")
            return {'success': False, 'error': 'Failed to get subscription info'}

# Global billing manager instance
billing_manager = StripeBillingManager()