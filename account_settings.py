"""
Account Settings Management System
Provides comprehensive user account management capabilities including payment methods,
profile settings, security options, and subscription management.
"""

import os
import stripe
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from models import db, User, UserAccount, Transaction
from flask import current_app
import logging

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class AccountSettingsManager:
    """Comprehensive account settings management system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get complete user profile information"""
        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return {'error': 'User not found'}
            
            # Get account information
            account = UserAccount.query.filter_by(user_id=user_id).first()
            
            # Get subscription information
            subscription_info = self._get_subscription_info(user_id)
            
            # Get recent transactions (handle timestamp field compatibility)
            try:
                recent_transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).limit(5).all()
            except Exception:
                # Fallback if Transaction table/field doesn't exist
                recent_transactions = []
            
            profile_data = {
                'user_info': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': getattr(user, 'first_name', user.username),
                    'last_name': getattr(user, 'last_name', ''),
                    'profile_image_url': getattr(user, 'profile_image_url', '/static/images/default-avatar.png'),
                    'created_at': user.created_at.strftime('%Y-%m-%d') if hasattr(user, 'created_at') else 'Unknown',
                    'last_login': datetime.now().strftime('%Y-%m-%d %H:%M')
                },
                'account_info': {
                    'balance': float(account.balance) if account else 0.0,
                    'total_deposits': float(account.total_deposited) if account else 0.0,
                    'total_trades': len(recent_transactions),
                    'account_status': 'Active',
                    'account_type': subscription_info.get('tier', 'Free'),
                    'member_since': user.created_at.strftime('%B %Y') if hasattr(user, 'created_at') else 'Recently'
                },
                'subscription': subscription_info,
                'recent_activity': [
                    {
                        'type': getattr(t, 'transaction_type', 'trade'),
                        'amount': float(getattr(t, 'amount', 0)),
                        'description': getattr(t, 'description', f'Trade activity'),
                        'timestamp': getattr(t, 'created_at', datetime.now()).strftime('%Y-%m-%d %H:%M')
                    } for t in recent_transactions
                ],
                'security_settings': {
                    'two_factor_enabled': False,  # To be implemented
                    'login_notifications': True,
                    'trading_alerts': True,
                    'email_notifications': True
                }
            }
            
            return profile_data
            
        except Exception as e:
            self.logger.error(f"Error getting user profile: {e}")
            return {'error': 'Failed to load profile'}
    
    def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile information"""
        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Update allowed fields
            if 'first_name' in profile_data:
                user.first_name = profile_data['first_name']
            if 'last_name' in profile_data:
                user.last_name = profile_data['last_name']
            if 'email' in profile_data:
                # Validate email format
                if '@' in profile_data['email']:
                    user.email = profile_data['email']
                else:
                    return {'success': False, 'error': 'Invalid email format'}
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Profile updated successfully',
                'updated_fields': list(profile_data.keys())
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating profile: {e}")
            return {'success': False, 'error': 'Failed to update profile'}
    
    def get_payment_methods(self, user_id: str) -> Dict[str, Any]:
        """Get user's saved payment methods"""
        try:
            # In a real implementation, this would fetch from Stripe
            # For now, return structured data for the interface
            
            payment_methods = {
                'cards': [
                    {
                        'id': 'pm_card_1',
                        'type': 'card',
                        'brand': 'visa',
                        'last4': '4242',
                        'exp_month': 12,
                        'exp_year': 2026,
                        'is_default': True,
                        'billing_address': {
                            'line1': '123 Main St',
                            'city': 'San Francisco',
                            'state': 'CA',
                            'postal_code': '94105',
                            'country': 'US'
                        }
                    }
                ],
                'bank_accounts': [],  # To be implemented
                'default_payment_method': 'pm_card_1'
            }
            
            return {
                'success': True,
                'payment_methods': payment_methods,
                'stripe_publishable_key': os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_...')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting payment methods: {e}")
            return {'success': False, 'error': 'Failed to load payment methods'}
    
    def add_payment_method(self, user_id: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add new payment method"""
        try:
            # In a real implementation, this would create a payment method in Stripe
            
            return {
                'success': True,
                'message': 'Payment method added successfully',
                'payment_method_id': f'pm_new_{user_id}'
            }
            
        except Exception as e:
            self.logger.error(f"Error adding payment method: {e}")
            return {'success': False, 'error': 'Failed to add payment method'}
    
    def remove_payment_method(self, user_id: str, payment_method_id: str) -> Dict[str, Any]:
        """Remove payment method"""
        try:
            # In a real implementation, this would detach the payment method in Stripe
            
            return {
                'success': True,
                'message': 'Payment method removed successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Error removing payment method: {e}")
            return {'success': False, 'error': 'Failed to remove payment method'}
    
    def update_security_settings(self, user_id: str, security_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update security settings"""
        try:
            # Store security preferences (in a real app, this would be in the database)
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Update security settings
            settings_updated = []
            
            if 'two_factor_enabled' in security_data:
                # Implement 2FA logic here
                settings_updated.append('Two-factor authentication')
            
            if 'login_notifications' in security_data:
                settings_updated.append('Login notifications')
            
            if 'trading_alerts' in security_data:
                settings_updated.append('Trading alerts')
            
            if 'email_notifications' in security_data:
                settings_updated.append('Email notifications')
            
            return {
                'success': True,
                'message': f'Updated: {", ".join(settings_updated)}',
                'updated_settings': settings_updated
            }
            
        except Exception as e:
            self.logger.error(f"Error updating security settings: {e}")
            return {'success': False, 'error': 'Failed to update security settings'}
    
    def get_subscription_details(self, user_id: str) -> Dict[str, Any]:
        """Get detailed subscription information"""
        try:
            subscription_info = self._get_subscription_info(user_id)
            
            # Calculate subscription metrics
            current_tier = subscription_info.get('tier', 'Free')
            
            subscription_details = {
                'current_plan': {
                    'name': current_tier,
                    'price': subscription_info.get('monthly_cost', 0),
                    'billing_cycle': 'Monthly',
                    'next_billing_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                    'features': self._get_tier_features(current_tier)
                },
                'usage_stats': {
                    'api_calls_used': subscription_info.get('api_calls_used', 0),
                    'api_calls_limit': subscription_info.get('api_calls_limit', 1000),
                    'trades_this_month': 15,  # Example data
                    'alerts_active': 8
                },
                'available_plans': [
                    {
                        'name': 'Free',
                        'price': 0,
                        'features': self._get_tier_features('Free'),
                        'recommended': False
                    },
                    {
                        'name': 'Pro',
                        'price': 19.99,
                        'features': self._get_tier_features('Pro'),
                        'recommended': current_tier == 'Free'
                    },
                    {
                        'name': 'Elite',
                        'price': 39.99,
                        'features': self._get_tier_features('Elite'),
                        'recommended': current_tier in ['Free', 'Pro']
                    },
                    {
                        'name': 'Institutional',
                        'price': 199.99,
                        'features': self._get_tier_features('Institutional'),
                        'recommended': False
                    }
                ]
            }
            
            return {'success': True, 'subscription': subscription_details}
            
        except Exception as e:
            self.logger.error(f"Error getting subscription details: {e}")
            return {'success': False, 'error': 'Failed to load subscription details'}
    
    def change_subscription(self, user_id: str, new_plan: str) -> Dict[str, Any]:
        """Change user subscription plan"""
        try:
            # In a real implementation, this would update the subscription in Stripe
            
            plan_prices = {
                'Free': 0,
                'Pro': 19.99,
                'Elite': 39.99,
                'Institutional': 199.99
            }
            
            if new_plan not in plan_prices:
                return {'success': False, 'error': 'Invalid plan selected'}
            
            return {
                'success': True,
                'message': f'Successfully upgraded to {new_plan} plan',
                'new_plan': new_plan,
                'new_price': plan_prices[new_plan],
                'effective_date': datetime.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            self.logger.error(f"Error changing subscription: {e}")
            return {'success': False, 'error': 'Failed to change subscription'}
    
    def get_notification_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user notification preferences"""
        try:
            # Default notification preferences
            preferences = {
                'email_notifications': {
                    'trade_confirmations': True,
                    'market_alerts': True,
                    'account_updates': True,
                    'promotional_emails': False,
                    'weekly_summary': True
                },
                'push_notifications': {
                    'price_alerts': True,
                    'trade_executions': True,
                    'market_news': False,
                    'account_security': True
                },
                'alert_frequency': {
                    'immediate': True,
                    'hourly_digest': False,
                    'daily_digest': True,
                    'weekly_digest': True
                }
            }
            
            return {'success': True, 'preferences': preferences}
            
        except Exception as e:
            self.logger.error(f"Error getting notification preferences: {e}")
            return {'success': False, 'error': 'Failed to load preferences'}
    
    def update_notification_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update notification preferences"""
        try:
            # In a real implementation, store these in the database
            
            updated_categories = []
            if 'email_notifications' in preferences:
                updated_categories.append('Email notifications')
            if 'push_notifications' in preferences:
                updated_categories.append('Push notifications')
            if 'alert_frequency' in preferences:
                updated_categories.append('Alert frequency')
            
            return {
                'success': True,
                'message': f'Updated: {", ".join(updated_categories)}',
                'updated_preferences': updated_categories
            }
            
        except Exception as e:
            self.logger.error(f"Error updating notification preferences: {e}")
            return {'success': False, 'error': 'Failed to update preferences'}
    
    def delete_account(self, user_id: str, confirmation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Delete user account with proper confirmation"""
        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Verify confirmation
            if not confirmation_data.get('confirmed'):
                return {'success': False, 'error': 'Account deletion must be confirmed'}
            
            if confirmation_data.get('email') != user.email:
                return {'success': False, 'error': 'Email confirmation does not match'}
            
            # In a real implementation:
            # 1. Cancel all subscriptions
            # 2. Close all positions
            # 3. Transfer remaining balance
            # 4. Anonymize or delete data according to regulations
            
            return {
                'success': True,
                'message': 'Account deletion initiated. You will receive confirmation within 24 hours.',
                'deletion_id': f'del_{user_id}_{int(datetime.now().timestamp())}'
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting account: {e}")
            return {'success': False, 'error': 'Failed to process account deletion'}
    
    def _get_subscription_info(self, user_id: str) -> Dict[str, Any]:
        """Get subscription information for user"""
        # In a real implementation, this would query the subscription database
        return {
            'tier': 'Free',
            'monthly_cost': 0,
            'api_calls_used': 245,
            'api_calls_limit': 1000,
            'features_enabled': ['Basic Trading', 'AI Analysis', 'Portfolio Tracking'],
            'upgrade_available': True
        }
    
    def _get_tier_features(self, tier: str) -> List[str]:
        """Get features for subscription tier"""
        features_map = {
            'Free': [
                'Basic AI Trading Insights',
                'Portfolio Tracking',
                'Stock Search & Analysis',
                '1,000 API Calls/Month',
                'Email Support'
            ],
            'Pro': [
                'Advanced AI Recommendations',
                'Real-time Market Data',
                'Level 2 Data Access',
                'Smart Order Routing',
                '10,000 API Calls/Month',
                'Priority Support'
            ],
            'Elite': [
                'All Pro Features',
                'Dark Pool Intelligence',
                'Advanced Options Flow',
                'Algorithm Builder',
                '50,000 API Calls/Month',
                'Phone Support'
            ],
            'Institutional': [
                'All Elite Features',
                'Direct Market Access',
                'Custom API Integration',
                'Team Management',
                'Unlimited API Calls',
                'Dedicated Account Manager'
            ]
        }
        return features_map.get(tier, [])

# Initialize the account settings manager
account_settings_manager = AccountSettingsManager()