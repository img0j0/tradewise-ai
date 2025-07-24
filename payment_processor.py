import os
import stripe
from flask import current_app
import logging

# Import specific Stripe error classes with fallback
try:
    from stripe.error import StripeError
except ImportError:
    # Fallback for different Stripe versions
    try:
        from stripe._error import StripeError
    except ImportError:
        StripeError = Exception

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class PaymentProcessor:
    def __init__(self):
        self.domain = self._get_domain()
    
    def _get_domain(self):
        """Get the current domain for Stripe redirect URLs"""
        if os.environ.get('REPLIT_DEPLOYMENT'):
            return f"https://{os.environ.get('REPLIT_DEV_DOMAIN')}"
        else:
            domains = os.environ.get('REPLIT_DOMAINS', 'localhost:5000')
            return f"https://{domains.split(',')[0]}"
    
    def create_premium_subscription(self):
        """Create a Stripe checkout session for premium subscription"""
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'TradeWise AI Premium',
                            'description': 'AI Portfolio Optimizer, Market Scanner, DCF Calculator, Earnings Predictor, Unlimited Alerts',
                            'images': [],
                        },
                        'unit_amount': 1000,  # $10.00 in cents
                        'recurring': {
                            'interval': 'month',
                        },
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f'{self.domain}/premium/success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{self.domain}/premium/upgrade?canceled=true',
                metadata={
                    'subscription_type': 'premium',
                    'features': 'ai_portfolio_optimizer,market_scanner,dcf_calculator,earnings_predictor,unlimited_alerts'
                }
            )
            
            logging.info(f"Created Stripe checkout session: {checkout_session.id}")
            return {
                'success': True,
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            }
            
        except StripeError as e:
            logging.error(f"Stripe error: {str(e)}")
            return {
                'success': False,
                'error': 'Payment processing error. Please try again.',
                'details': str(e)
            }
        except Exception as e:
            logging.error(f"Payment processor error: {str(e)}")
            return {
                'success': False,
                'error': 'Unexpected error. Please try again.',
                'details': str(e)
            }
    
    def verify_session(self, session_id):
        """Verify a completed Stripe checkout session"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                return {
                    'success': True,
                    'customer_id': session.customer,
                    'subscription_id': session.subscription,
                    'customer_email': session.customer_details.email if session.customer_details else None
                }
            else:
                return {
                    'success': False,
                    'error': 'Payment not completed'
                }
                
        except StripeError as e:
            logging.error(f"Session verification error: {str(e)}")
            return {
                'success': False,
                'error': 'Session verification failed',
                'details': str(e)
            }
    
    def cancel_subscription(self, subscription_id):
        """Cancel a Stripe subscription"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            
            return {
                'success': True,
                'canceled_at': getattr(subscription, 'canceled_at', None),
                'current_period_end': getattr(subscription, 'current_period_end', None)
            }
            
        except StripeError as e:
            logging.error(f"Subscription cancellation error: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to cancel subscription',
                'details': str(e)
            }
    
    def get_subscription_status(self, subscription_id):
        """Get current subscription status"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                'success': True,
                'status': subscription.status,
                'current_period_start': getattr(subscription, 'current_period_start', None),
                'current_period_end': getattr(subscription, 'current_period_end', None),
                'cancel_at_period_end': getattr(subscription, 'cancel_at_period_end', False)
            }
            
        except StripeError as e:
            logging.error(f"Subscription status error: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to get subscription status',
                'details': str(e)
            }

# Global payment processor instance
payment_processor = PaymentProcessor()