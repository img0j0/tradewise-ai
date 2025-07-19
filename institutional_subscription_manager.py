"""
Institutional Subscription Manager
Manages advanced institutional trading features and subscription tiers
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)

class InstitutionalSubscriptionManager:
    def __init__(self):
        self.subscription_tiers = {
            'Pro': {
                'price_monthly': 19.99,
                'price_annual': 199.00,
                'features': [
                    'Level 2 Market Data',
                    'Basic Options Flow Analysis',
                    'Smart Order Routing',
                    'Portfolio Risk Analytics',
                    'Extended Trading Hours'
                ],
                'limits': {
                    'api_calls_per_day': 10000,
                    'real_time_quotes': True,
                    'advanced_charts': True,
                    'portfolio_positions': 100
                }
            },
            'Elite': {
                'price_monthly': 39.99,
                'price_annual': 399.00,
                'features': [
                    'All Pro features',
                    'Dark Pool Intelligence',
                    'Advanced Options Flow Analysis',
                    'Algorithm Builder & Backtesting',
                    'Institutional Order Flow',
                    'Market Microstructure Analysis',
                    'Custom Technical Indicators',
                    'Priority Support'
                ],
                'limits': {
                    'api_calls_per_day': 50000,
                    'real_time_quotes': True,
                    'advanced_charts': True,
                    'portfolio_positions': 1000,
                    'custom_algorithms': 10
                }
            },
            'Institutional': {
                'price_monthly': 199.99,
                'price_annual': 1999.00,
                'features': [
                    'All Elite features',
                    'Direct Market Access (DMA)',
                    'Prime Brokerage Integration',
                    'Custom API Access',
                    'Dedicated Account Manager',
                    'White-label Solutions',
                    'Regulatory Reporting Tools',
                    'Multi-user Team Access'
                ],
                'limits': {
                    'api_calls_per_day': 1000000,
                    'real_time_quotes': True,
                    'advanced_charts': True,
                    'portfolio_positions': 'unlimited',
                    'custom_algorithms': 100,
                    'team_members': 25
                }
            }
        }
        
        logger.info("Institutional Subscription Manager initialized")

    def get_subscription_tiers(self) -> Dict:
        """Get all available subscription tiers"""
        return self.subscription_tiers

    def check_feature_access(self, user_subscription: str, feature: str) -> bool:
        """Check if user has access to specific feature"""
        if user_subscription not in self.subscription_tiers:
            return False
        
        tier_features = self.subscription_tiers[user_subscription]['features']
        
        # Check direct feature access
        if feature in tier_features:
            return True
        
        # Check inherited features from lower tiers
        if user_subscription == 'Elite' and feature in self.subscription_tiers['Pro']['features']:
            return True
        elif user_subscription == 'Institutional':
            if (feature in self.subscription_tiers['Elite']['features'] or 
                feature in self.subscription_tiers['Pro']['features']):
                return True
        
        return False

    def get_feature_limits(self, user_subscription: str) -> Dict:
        """Get usage limits for user's subscription tier"""
        if user_subscription not in self.subscription_tiers:
            return {
                'api_calls_per_day': 100,
                'real_time_quotes': False,
                'advanced_charts': False,
                'portfolio_positions': 10
            }
        
        return self.subscription_tiers[user_subscription]['limits']

    def calculate_upgrade_savings(self, current_tier: str, target_tier: str) -> Dict:
        """Calculate savings and benefits of upgrading"""
        if current_tier not in self.subscription_tiers or target_tier not in self.subscription_tiers:
            return {}
        
        current_price = self.subscription_tiers[current_tier]['price_monthly']
        target_price = self.subscription_tiers[target_tier]['price_monthly']
        
        # Calculate annual savings
        annual_current = self.subscription_tiers[current_tier]['price_annual']
        annual_target = self.subscription_tiers[target_tier]['price_annual']
        
        monthly_difference = target_price - current_price
        annual_savings = (target_price * 12) - annual_target
        
        # Get additional features
        current_features = set(self.subscription_tiers[current_tier]['features'])
        target_features = set(self.subscription_tiers[target_tier]['features'])
        new_features = list(target_features - current_features)
        
        return {
            'monthly_cost_increase': monthly_difference,
            'annual_plan_savings': annual_savings,
            'new_features': new_features,
            'upgrade_value': len(new_features) * 50  # Estimated value per feature
        }

    def get_institutional_demo_features(self) -> Dict:
        """Get institutional features available in demo mode"""
        return {
            'Smart Order Routing': {
                'description': 'Find best execution across 50+ venues',
                'demo_available': True,
                'full_access_tier': 'Pro'
            },
            'Level 2 Market Data': {
                'description': 'Real-time order book depth and liquidity',
                'demo_available': True,
                'full_access_tier': 'Pro'
            },
            'Options Flow Analysis': {
                'description': 'Track unusual options activity and flow',
                'demo_available': True,
                'full_access_tier': 'Elite'
            },
            'Dark Pool Intelligence': {
                'description': 'Institutional block trading analysis',
                'demo_available': True,
                'full_access_tier': 'Elite'
            },
            'Algorithm Builder': {
                'description': 'Create and backtest custom strategies',
                'demo_available': True,
                'full_access_tier': 'Elite'
            }
        }

    def generate_upgrade_recommendation(self, user_activity: Dict) -> Dict:
        """Generate personalized upgrade recommendation based on user activity"""
        # Analyze user behavior
        daily_api_calls = user_activity.get('daily_api_calls', 0)
        uses_advanced_features = user_activity.get('uses_advanced_features', False)
        portfolio_size = user_activity.get('portfolio_positions', 0)
        trading_frequency = user_activity.get('trades_per_week', 0)
        
        recommended_tier = 'Pro'
        reasons = []
        
        # Determine recommended tier based on usage
        if daily_api_calls > 5000 or portfolio_size > 50:
            recommended_tier = 'Elite'
            reasons.append('High API usage and large portfolio')
        
        if trading_frequency > 20:
            recommended_tier = 'Elite'
            reasons.append('Active trading requires advanced tools')
        
        if uses_advanced_features:
            recommended_tier = 'Elite'
            reasons.append('Using advanced analytical features')
        
        # Calculate potential value
        potential_value = self._calculate_user_value(user_activity, recommended_tier)
        
        return {
            'recommended_tier': recommended_tier,
            'reasons': reasons,
            'potential_monthly_value': potential_value,
            'upgrade_urgency': 'High' if len(reasons) > 2 else 'Medium'
        }

    def _calculate_user_value(self, user_activity: Dict, tier: str) -> float:
        """Calculate potential monthly value for user"""
        base_value = {
            'Pro': 150,
            'Elite': 300,
            'Institutional': 2000
        }
        
        # Adjust based on trading frequency
        trading_multiplier = min(user_activity.get('trades_per_week', 1) / 10, 3)
        
        return base_value.get(tier, 100) * trading_multiplier

    def get_institutional_onboarding_flow(self, target_tier: str) -> List[Dict]:
        """Get step-by-step onboarding flow for institutional features"""
        base_steps = [
            {
                'step': 1,
                'title': 'Subscription Activation',
                'description': 'Complete subscription setup and payment',
                'estimated_time': '2 minutes'
            },
            {
                'step': 2,
                'title': 'Account Verification',
                'description': 'Verify identity and trading experience',
                'estimated_time': '5 minutes'
            },
            {
                'step': 3,
                'title': 'Platform Tutorial',
                'description': 'Interactive guide to advanced features',
                'estimated_time': '15 minutes'
            }
        ]
        
        tier_specific_steps = {
            'Pro': [
                {
                    'step': 4,
                    'title': 'Level 2 Data Setup',
                    'description': 'Configure real-time market data feeds',
                    'estimated_time': '5 minutes'
                }
            ],
            'Elite': [
                {
                    'step': 4,
                    'title': 'Algorithm Builder Introduction',
                    'description': 'Create your first custom strategy',
                    'estimated_time': '20 minutes'
                },
                {
                    'step': 5,
                    'title': 'Dark Pool Intelligence Setup',
                    'description': 'Configure institutional flow monitoring',
                    'estimated_time': '10 minutes'
                }
            ],
            'Institutional': [
                {
                    'step': 4,
                    'title': 'API Access Configuration',
                    'description': 'Set up custom API endpoints',
                    'estimated_time': '30 minutes'
                },
                {
                    'step': 5,
                    'title': 'Team Management Setup',
                    'description': 'Add team members and permissions',
                    'estimated_time': '15 minutes'
                },
                {
                    'step': 6,
                    'title': 'Dedicated Support Introduction',
                    'description': 'Meet your account manager',
                    'estimated_time': '30 minutes'
                }
            ]
        }
        
        return base_steps + tier_specific_steps.get(target_tier, [])

# Global instance
institutional_subscription_manager = InstitutionalSubscriptionManager()