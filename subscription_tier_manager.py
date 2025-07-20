"""
TradeWise AI - Subscription Tier Manager
Manages subscription-based feature access and UI transformations
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from flask_login import current_user

logger = logging.getLogger(__name__)

class SubscriptionTierManager:
    def __init__(self):
        self.tier_config = {
            'Free': {
                'price_monthly': 0,
                'price_annual': 0,
                'ui_features': {
                    'ai_insights_per_day': 3,
                    'search_suggestions': 5,
                    'portfolio_tracking': True,
                    'basic_alerts': True,
                    'commission_rate': 0.0025,  # 0.25%
                    'theme': 'standard',
                    'advanced_charts': False,
                    'ai_confidence_display': False,
                    'real_time_data': False
                },
                'api_limits': {
                    'stock_searches_per_day': 50,
                    'ai_analysis_per_day': 3,
                    'watchlist_stocks': 10
                },
                'ui_elements': {
                    'upgrade_prompts': True,
                    'feature_locks': True,
                    'premium_badges': False
                }
            },
            'Pro': {
                'price_monthly': 19.99,
                'price_annual': 199.00,
                'ui_features': {
                    'ai_insights_per_day': 50,
                    'search_suggestions': 20,
                    'portfolio_tracking': True,
                    'advanced_alerts': True,
                    'commission_rate': 0.001,  # 0.1%
                    'theme': 'pro',
                    'advanced_charts': True,
                    'ai_confidence_display': True,
                    'real_time_data': True,
                    'level_2_data': True,
                    'smart_order_routing': True
                },
                'api_limits': {
                    'stock_searches_per_day': 500,
                    'ai_analysis_per_day': 50,
                    'watchlist_stocks': 50
                },
                'ui_elements': {
                    'upgrade_prompts': True,
                    'feature_locks': False,
                    'premium_badges': True,
                    'pro_ai_assistant': True
                }
            },
            'Elite': {
                'price_monthly': 39.99,
                'price_annual': 399.00,
                'ui_features': {
                    'ai_insights_per_day': 'unlimited',
                    'search_suggestions': 50,
                    'portfolio_tracking': True,
                    'advanced_alerts': True,
                    'commission_rate': 0.0005,  # 0.05%
                    'theme': 'elite',
                    'advanced_charts': True,
                    'ai_confidence_display': True,
                    'real_time_data': True,
                    'level_2_data': True,
                    'smart_order_routing': True,
                    'dark_pool_intelligence': True,
                    'algorithm_builder': True,
                    'advanced_options_flow': True
                },
                'api_limits': {
                    'stock_searches_per_day': 2000,
                    'ai_analysis_per_day': 'unlimited',
                    'watchlist_stocks': 200
                },
                'ui_elements': {
                    'upgrade_prompts': True,
                    'feature_locks': False,
                    'premium_badges': True,
                    'elite_ai_assistant': True,
                    'advanced_analytics': True
                }
            },
            'Institutional': {
                'price_monthly': 199.99,
                'price_annual': 1999.00,
                'ui_features': {
                    'ai_insights_per_day': 'unlimited',
                    'search_suggestions': 'unlimited',
                    'portfolio_tracking': True,
                    'advanced_alerts': True,
                    'commission_rate': 0.0001,  # 0.01%
                    'theme': 'institutional',
                    'advanced_charts': True,
                    'ai_confidence_display': True,
                    'real_time_data': True,
                    'level_2_data': True,
                    'smart_order_routing': True,
                    'dark_pool_intelligence': True,
                    'algorithm_builder': True,
                    'advanced_options_flow': True,
                    'direct_market_access': True,
                    'custom_api_access': True,
                    'team_management': True
                },
                'api_limits': {
                    'stock_searches_per_day': 'unlimited',
                    'ai_analysis_per_day': 'unlimited',
                    'watchlist_stocks': 'unlimited'
                },
                'ui_elements': {
                    'upgrade_prompts': False,
                    'feature_locks': False,
                    'premium_badges': True,
                    'institutional_ai_assistant': True,
                    'advanced_analytics': True,
                    'white_label_options': True
                }
            }
        }
        
        logger.info("Subscription Tier Manager initialized")

    def get_user_tier(self, user_id: Optional[int] = None) -> str:
        """Get current user's subscription tier"""
        try:
            if current_user.is_authenticated:
                # Check if user is demo user (institutional account)
                if current_user.username == 'demo':
                    logger.info(f"Demo user detected - returning Institutional tier")
                    return 'Institutional'
                
                # Check for subscription_tier attribute
                tier = getattr(current_user, 'subscription_tier', 'Free')
                logger.info(f"User tier check - User: {current_user.username}, Tier: {tier}")
                return tier
            
            logger.info("User not authenticated - returning Free tier")
            return 'Free'
        except Exception as e:
            logger.error(f"Error getting user tier: {e}")
            return 'Free'

    def get_tier_config(self, tier: str) -> Dict[str, Any]:
        """Get configuration for a specific tier"""
        return self.tier_config.get(tier, self.tier_config['Free'])

    def get_ui_features(self, tier: str = None) -> Dict[str, Any]:
        """Get UI features for user's tier"""
        if tier is None:
            tier = self.get_user_tier()
        
        config = self.get_tier_config(tier)
        return config.get('ui_features', {})

    def can_access_feature(self, feature_name: str, tier: str = None) -> bool:
        """Check if user can access a specific feature"""
        if tier is None:
            tier = self.get_user_tier()
        
        ui_features = self.get_ui_features(tier)
        return ui_features.get(feature_name, False)

    def get_search_enhancement_level(self, tier: str = None) -> Dict[str, Any]:
        """Get search interface enhancements based on tier"""
        if tier is None:
            tier = self.get_user_tier()
        
        enhancements = {
            'Free': {
                'suggestions_count': 5,
                'ai_analysis_depth': 'basic',
                'real_time_prices': False,
                'confidence_scores': False,
                'upgrade_prompts': True
            },
            'Pro': {
                'suggestions_count': 20,
                'ai_analysis_depth': 'enhanced',
                'real_time_prices': True,
                'confidence_scores': True,
                'upgrade_prompts': True,
                'level_2_data': True
            },
            'Elite': {
                'suggestions_count': 50,
                'ai_analysis_depth': 'advanced',
                'real_time_prices': True,
                'confidence_scores': True,
                'upgrade_prompts': True,
                'dark_pool_insights': True,
                'options_flow': True
            },
            'Institutional': {
                'suggestions_count': 'unlimited',
                'ai_analysis_depth': 'institutional',
                'real_time_prices': True,
                'confidence_scores': True,
                'upgrade_prompts': False,
                'direct_market_access': True,
                'custom_analytics': True
            }
        }
        
        return enhancements.get(tier, enhancements['Free'])

    def get_ai_assistant_capabilities(self, tier: str = None) -> Dict[str, Any]:
        """Get AI assistant capabilities based on tier"""
        if tier is None:
            tier = self.get_user_tier()
        
        capabilities = {
            'Free': {
                'responses_per_day': 10,
                'analysis_depth': 'basic',
                'market_insights': 'limited',
                'portfolio_advice': 'basic',
                'risk_analysis': False
            },
            'Pro': {
                'responses_per_day': 100,
                'analysis_depth': 'enhanced',
                'market_insights': 'comprehensive',
                'portfolio_advice': 'advanced',
                'risk_analysis': True,
                'smart_alerts': True
            },
            'Elite': {
                'responses_per_day': 'unlimited',
                'analysis_depth': 'advanced',
                'market_insights': 'comprehensive',
                'portfolio_advice': 'expert',
                'risk_analysis': True,
                'smart_alerts': True,
                'predictive_insights': True,
                'options_strategies': True
            },
            'Institutional': {
                'responses_per_day': 'unlimited',
                'analysis_depth': 'institutional',
                'market_insights': 'comprehensive',
                'portfolio_advice': 'expert',
                'risk_analysis': True,
                'smart_alerts': True,
                'predictive_insights': True,
                'options_strategies': True,
                'custom_models': True,
                'team_collaboration': True
            }
        }
        
        return capabilities.get(tier, capabilities['Free'])

    def get_upgrade_recommendations(self, tier: str = None) -> List[Dict[str, Any]]:
        """Get personalized upgrade recommendations"""
        if tier is None:
            tier = self.get_user_tier()
        
        if tier == 'Free':
            return [
                {
                    'target_tier': 'Pro',
                    'headline': 'Unlock Advanced AI Trading',
                    'benefits': [
                        '50 AI insights per day (vs 3)',
                        'Real-time market data',
                        'Smart order routing',
                        'Advanced portfolio analytics'
                    ],
                    'savings': 'Save $1,800/month vs Bloomberg Terminal',
                    'cta': 'Upgrade to Pro for $19.99/month'
                }
            ]
        elif tier == 'Pro':
            return [
                {
                    'target_tier': 'Elite',
                    'headline': 'Access Institutional-Grade Tools',
                    'benefits': [
                        'Unlimited AI insights',
                        'Dark pool intelligence',
                        'Algorithm builder',
                        'Advanced options flow analysis'
                    ],
                    'savings': 'Professional tools at 98% less than institutional platforms',
                    'cta': 'Upgrade to Elite for $39.99/month'
                }
            ]
        elif tier == 'Elite':
            return [
                {
                    'target_tier': 'Institutional',
                    'headline': 'Full Enterprise Capabilities',
                    'benefits': [
                        'Direct market access',
                        'Custom API integration',
                        'Team management',
                        'White-label solutions'
                    ],
                    'savings': 'Enterprise features at $199.99 vs $2,000+ traditional',
                    'cta': 'Contact for Institutional Access'
                }
            ]
        
        return []

    def generate_tier_specific_ui_config(self, tier: str = None) -> Dict[str, Any]:
        """Generate complete UI configuration for user's tier"""
        if tier is None:
            tier = self.get_user_tier()
        
        config = self.get_tier_config(tier)
        
        return {
            'tier': tier,
            'ui_features': config.get('ui_features', {}),
            'api_limits': config.get('api_limits', {}),
            'ui_elements': config.get('ui_elements', {}),
            'search_enhancements': self.get_search_enhancement_level(tier),
            'ai_capabilities': self.get_ai_assistant_capabilities(tier),
            'upgrade_recommendations': self.get_upgrade_recommendations(tier),
            'theme_config': self.get_theme_config(tier)
        }

    def get_theme_config(self, tier: str) -> Dict[str, str]:
        """Get theme configuration for tier"""
        themes = {
            'Free': {
                'primary_color': '#3b82f6',
                'accent_color': '#10b981',
                'badge_style': 'standard',
                'animation_level': 'basic'
            },
            'Pro': {
                'primary_color': '#8b5cf6',
                'accent_color': '#f59e0b',
                'badge_style': 'pro',
                'animation_level': 'enhanced'
            },
            'Elite': {
                'primary_color': '#ef4444',
                'accent_color': '#f97316',
                'badge_style': 'elite',
                'animation_level': 'advanced'
            },
            'Institutional': {
                'primary_color': '#1f2937',
                'accent_color': '#dc2626',
                'badge_style': 'institutional',
                'animation_level': 'professional'
            }
        }
        
        return themes.get(tier, themes['Free'])

# Global instance
subscription_tier_manager = SubscriptionTierManager()