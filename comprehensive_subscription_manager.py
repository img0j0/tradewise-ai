"""
Comprehensive Subscription Management System for TradeWise AI
Handles Pro and Enterprise plan functionality with Stripe integration
"""

import stripe
import os
import json
import logging
from datetime import datetime, timedelta
from flask import session, request, current_app
from models import User, db
from typing import Dict, Optional, List, Any

logger = logging.getLogger(__name__)

class ComprehensiveSubscriptionManager:
    """Manages all subscription tiers with full functionality"""
    
    def __init__(self):
        self.stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')
        if self.stripe_secret_key:
            stripe.api_key = self.stripe_secret_key
        
        # Plan configurations with full feature sets
        self.plan_configs = {
            'free': {
                'display_name': 'Free',
                'monthly_price': 0,
                'annual_price': 0,
                'color_theme': '#6c6c70',
                'icon': 'fas fa-user',
                'api_requests_per_day': 50,
                'max_alerts': 5,
                'max_watchlist_items': 10,
                'portfolio_holdings_limit': 10,
                'features': {
                    'basic_stock_analysis': True,
                    'market_data_access': True,
                    'portfolio_tracking': True,
                    'watchlist_management': True,
                    'basic_alerts': True,
                    'ai_insights': False,
                    'advanced_portfolio_analytics': False,
                    'portfolio_backtesting': False,
                    'market_scanner': False,
                    'earnings_predictions': False,
                    'sector_analysis': False,
                    'peer_comparison': False,
                    'risk_analysis': False,
                    'real_time_alerts': False,
                    'custom_reports': False,
                    'api_access': False,
                    'priority_support': False,
                    'team_collaboration': False
                },
                'limitations': {
                    'analysis_depth': 'Basic',
                    'data_history': '1 year',
                    'alert_frequency': 'Daily',
                    'export_formats': ['CSV']
                }
            },
            'pro': {
                'display_name': 'Pro',
                'monthly_price': 29.99,
                'annual_price': 299.99,
                'color_theme': '#007AFF',
                'icon': 'fas fa-star',
                'stripe_monthly_price_id': os.environ.get('STRIPE_PRO_MONTHLY_PRICE_ID', 'price_pro_monthly'),
                'stripe_annual_price_id': os.environ.get('STRIPE_PRO_ANNUAL_PRICE_ID', 'price_pro_annual'),
                'api_requests_per_day': 1000,
                'max_alerts': 100,
                'max_watchlist_items': 200,
                'portfolio_holdings_limit': 100,
                'trial_days': 14,
                'features': {
                    'basic_stock_analysis': True,
                    'market_data_access': True,
                    'portfolio_tracking': True,
                    'watchlist_management': True,
                    'basic_alerts': True,
                    'ai_insights': True,
                    'advanced_portfolio_analytics': True,
                    'portfolio_backtesting': True,
                    'market_scanner': True,
                    'earnings_predictions': True,
                    'sector_analysis': True,
                    'peer_comparison': True,
                    'risk_analysis': True,
                    'real_time_alerts': True,
                    'custom_reports': True,
                    'api_access': False,
                    'priority_support': True,
                    'team_collaboration': False
                },
                'limitations': {
                    'analysis_depth': 'Advanced',
                    'data_history': '10 years',
                    'alert_frequency': 'Real-time',
                    'export_formats': ['CSV', 'PDF', 'Excel']
                }
            },
            'enterprise': {
                'display_name': 'Enterprise',
                'monthly_price': 99.99,
                'annual_price': 999.99,
                'color_theme': '#FF9500',
                'icon': 'fas fa-crown',
                'stripe_monthly_price_id': os.environ.get('STRIPE_ENTERPRISE_MONTHLY_PRICE_ID', 'price_enterprise_monthly'),
                'stripe_annual_price_id': os.environ.get('STRIPE_ENTERPRISE_ANNUAL_PRICE_ID', 'price_enterprise_annual'),
                'api_requests_per_day': 10000,
                'max_alerts': 500,
                'max_watchlist_items': 1000,
                'portfolio_holdings_limit': 500,
                'team_seats': 25,
                'trial_days': 14,
                'features': {
                    'basic_stock_analysis': True,
                    'market_data_access': True,
                    'portfolio_tracking': True,
                    'watchlist_management': True,
                    'basic_alerts': True,
                    'ai_insights': True,
                    'advanced_portfolio_analytics': True,
                    'portfolio_backtesting': True,
                    'market_scanner': True,
                    'earnings_predictions': True,
                    'sector_analysis': True,
                    'peer_comparison': True,
                    'risk_analysis': True,
                    'real_time_alerts': True,
                    'custom_reports': True,
                    'api_access': True,
                    'priority_support': True,
                    'team_collaboration': True,
                    'white_label_reports': True,
                    'dedicated_support': True,
                    'custom_integrations': True
                },
                'limitations': {
                    'analysis_depth': 'Institutional',
                    'data_history': 'Unlimited',
                    'alert_frequency': 'Real-time',
                    'export_formats': ['CSV', 'PDF', 'Excel', 'JSON', 'API']
                }
            }
        }
    
    def get_user_plan(self, user_id: Optional[int] = None) -> str:
        """Get user's current plan"""
        if user_id:
            user = User.query.get(user_id)
            if user and user.is_plan_active():
                return user.plan_type
        
        # Fallback to session
        return session.get('user_plan', 'free')
    
    def get_plan_config(self, plan_name: str) -> Dict[str, Any]:
        """Get configuration for specific plan"""
        return self.plan_configs.get(plan_name, self.plan_configs['free'])
    
    def has_feature_access(self, feature: str, user_id: Optional[int] = None) -> bool:
        """Check if user has access to specific feature"""
        plan = self.get_user_plan(user_id)
        plan_config = self.get_plan_config(plan)
        return plan_config['features'].get(feature, False)
    
    def check_usage_limits(self, limit_type: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Check usage against plan limits"""
        plan = self.get_user_plan(user_id)
        plan_config = self.get_plan_config(plan)
        
        if user_id:
            user = User.query.get(user_id)
            if user:
                current_usage = self._get_current_usage(user, limit_type)
            else:
                current_usage = 0
        else:
            current_usage = 0
        
        limit = plan_config.get(limit_type, 0)
        
        return {
            'current_usage': current_usage,
            'limit': limit,
            'remaining': max(0, limit - current_usage),
            'percentage_used': (current_usage / limit * 100) if limit > 0 else 0,
            'can_continue': current_usage < limit if limit > 0 else True
        }
    
    def _get_current_usage(self, user: User, limit_type: str) -> int:
        """Get current usage for specific limit type"""
        if limit_type == 'api_requests_per_day':
            from datetime import date
            if user.api_requests_reset_date != date.today():
                return 0
            return user.api_requests_today
        elif limit_type == 'max_alerts':
            # Count active alerts - would need Alert model
            return 0  # Placeholder
        elif limit_type == 'max_watchlist_items':
            # Count watchlist items
            if user.watchlists:
                try:
                    watchlists = json.loads(user.watchlists)
                    return len(watchlists.get('stocks', []))
                except:
                    return 0
            return 0
        elif limit_type == 'portfolio_holdings_limit':
            # Count portfolio holdings
            return 0  # Placeholder
        
        return 0
    
    def create_checkout_session(self, plan: str, billing_cycle: str = 'monthly', user_id: Optional[int] = None) -> Dict[str, Any]:
        """Create Stripe checkout session"""
        if not self.stripe_secret_key:
            return {
                'success': False,
                'error': 'Stripe not configured'
            }
        
        try:
            plan_config = self.get_plan_config(plan)
            
            if plan == 'free':
                return {
                    'success': False,
                    'error': 'Free plan does not require checkout'
                }
            
            # Get price ID based on billing cycle
            price_id = plan_config.get(f'stripe_{billing_cycle}_price_id')
            if not price_id:
                return {
                    'success': False,
                    'error': f'Price ID not configured for {plan} {billing_cycle}'
                }
            
            # Create checkout session
            domain = os.environ.get('REPLIT_DEV_DOMAIN') or 'localhost:5000'
            protocol = 'https' if 'replit.dev' in domain else 'http'
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f'{protocol}://{domain}/premium/success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{protocol}://{domain}/premium/cancel',
                automatic_tax={'enabled': False},
                metadata={
                    'plan': plan,
                    'billing_cycle': billing_cycle,
                    'user_id': str(user_id) if user_id else 'session'
                }
            )
            
            return {
                'success': True,
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            }
            
        except Exception as e:
            logger.error(f"Stripe checkout error: {e}")
            return {
                'success': False,
                'error': f'Checkout creation failed: {str(e)}'
            }
    
    def verify_checkout_session(self, session_id: str) -> Dict[str, Any]:
        """Verify and process completed checkout session"""
        if not self.stripe_secret_key:
            return {
                'success': False,
                'error': 'Stripe not configured'
            }
        
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                # Update user subscription
                plan = session.metadata.get('plan')
                billing_cycle = session.metadata.get('billing_cycle', 'monthly')
                user_id = session.metadata.get('user_id')
                
                if user_id and user_id != 'session':
                    user = User.query.get(int(user_id))
                    if user:
                        self._update_user_subscription(user, plan, session)
                else:
                    # Update session for demo
                    session['user_plan'] = plan
                
                return {
                    'success': True,
                    'plan': plan,
                    'billing_cycle': billing_cycle,
                    'customer_email': session.customer_details.email if session.customer_details else None,
                    'subscription_id': session.subscription
                }
            else:
                return {
                    'success': False,
                    'error': 'Payment not completed'
                }
                
        except Exception as e:
            logger.error(f"Session verification error: {e}")
            return {
                'success': False,
                'error': f'Verification failed: {str(e)}'
            }
    
    def _update_user_subscription(self, user: User, plan: str, stripe_session):
        """Update user's subscription in database"""
        try:
            user.plan_type = plan
            user.subscription_status = 'active'
            user.subscription_start = datetime.utcnow()
            user.stripe_customer_id = stripe_session.customer
            user.stripe_subscription_id = stripe_session.subscription
            
            # Set subscription end date (1 month or 1 year from now)
            if 'annual' in stripe_session.metadata.get('billing_cycle', ''):
                user.subscription_end = datetime.utcnow() + timedelta(days=365)
            else:
                user.subscription_end = datetime.utcnow() + timedelta(days=30)
            
            db.session.commit()
            logger.info(f"Updated user {user.id} to {plan} plan")
            
        except Exception as e:
            logger.error(f"Database update error: {e}")
            db.session.rollback()
    
    def cancel_subscription(self, user_id: int) -> Dict[str, Any]:
        """Cancel user's subscription"""
        if not self.stripe_secret_key:
            return {
                'success': False,
                'error': 'Stripe not configured'
            }
        
        try:
            user = User.query.get(user_id)
            if not user or not user.stripe_subscription_id:
                return {
                    'success': False,
                    'error': 'No active subscription found'
                }
            
            # Cancel subscription in Stripe
            stripe.Subscription.delete(user.stripe_subscription_id)
            
            # Update user status
            user.subscription_status = 'canceled'
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Subscription canceled successfully'
            }
            
        except Exception as e:
            logger.error(f"Subscription cancellation error: {e}")
            return {
                'success': False,
                'error': f'Cancellation failed: {str(e)}'
            }
    
    def get_plan_comparison(self) -> Dict[str, Any]:
        """Get plan comparison data for UI"""
        return {
            'plans': self.plan_configs,
            'feature_categories': {
                'Analysis & Insights': [
                    'basic_stock_analysis',
                    'ai_insights',
                    'advanced_portfolio_analytics',
                    'risk_analysis',
                    'sector_analysis',
                    'peer_comparison'
                ],
                'Portfolio Management': [
                    'portfolio_tracking',
                    'portfolio_backtesting',
                    'watchlist_management',
                    'market_scanner'
                ],
                'Alerts & Monitoring': [
                    'basic_alerts',
                    'real_time_alerts',
                    'earnings_predictions'
                ],
                'Data & Reporting': [
                    'market_data_access',
                    'custom_reports',
                    'api_access'
                ],
                'Support & Collaboration': [
                    'priority_support',
                    'team_collaboration',
                    'dedicated_support'
                ]
            }
        }
    
    def get_plan_theme_data(self, plan: str) -> Dict[str, str]:
        """Get theme colors and styling for plan"""
        plan_config = self.get_plan_config(plan)
        return {
            'color': plan_config['color_theme'],
            'icon': plan_config['icon'],
            'display_name': plan_config['display_name'],
            'css_class': f'plan-{plan}'
        }

# Global instance
subscription_manager = ComprehensiveSubscriptionManager()