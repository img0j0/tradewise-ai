"""
Enhanced Premium Features Module for TradeWise AI
Comprehensive plan-based feature access control and advanced functionality
"""

import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Any
from flask import jsonify, session, request
from models import User, PlanConfiguration, db
import json

logger = logging.getLogger(__name__)

class PlanAccessError(Exception):
    """Exception for plan access violations"""
    pass

def plan_required(required_plan: str = 'pro', feature_name: str = None):
    """
    Enhanced decorator to check plan access with detailed error messages
    
    Args:
        required_plan: Minimum plan required ('free', 'pro', 'enterprise')
        feature_name: Name of the feature for better error messages
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({
                    'success': False, 
                    'error': 'Authentication required',
                    'requires_login': True
                }), 401
            
            user = User.query.get(user_id)
            if not user:
                return jsonify({
                    'success': False, 
                    'error': 'User not found',
                    'requires_login': True
                }), 401
            
            # Check if user has required plan access
            if not user.has_plan_access(required_plan):
                plan_config = PlanConfiguration.query.filter_by(plan_name=required_plan).first()
                
                upgrade_message = f"Upgrade to {plan_config.display_name if plan_config else required_plan.title()} to access"
                if feature_name:
                    upgrade_message += f" {feature_name}"
                
                return jsonify({
                    'success': False, 
                    'error': upgrade_message,
                    'requires_upgrade': True,
                    'current_plan': user.plan_type,
                    'required_plan': required_plan,
                    'upgrade_url': '/billing/plans'
                }), 403
            
            # Check API rate limits for non-enterprise users
            if user.plan_type != 'enterprise':
                plan_config = PlanConfiguration.query.filter_by(plan_name=user.plan_type).first()
                if plan_config and not user.check_api_rate_limit(plan_config.api_requests_per_day):
                    return jsonify({
                        'success': False,
                        'error': 'Daily API limit reached',
                        'rate_limited': True,
                        'limit': plan_config.api_requests_per_day,
                        'reset_time': 'midnight UTC'
                    }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Backward compatibility
def premium_required(f):
    """Legacy premium_required decorator - now uses plan_required"""
    return plan_required('pro', 'premium features')(f)

class EnhancedPremiumFeatures:
    """Enhanced premium features with comprehensive plan-based access"""
    
    @staticmethod
    def get_plan_features(plan_type: str) -> Dict[str, Any]:
        """Get features available for a specific plan"""
        plan_config = PlanConfiguration.query.filter_by(plan_name=plan_type).first()
        if plan_config:
            return {
                'plan_name': plan_config.plan_name,
                'display_name': plan_config.display_name,
                'features': json.loads(plan_config.features) if plan_config.features else {},
                'limits': {
                    'api_requests_per_day': plan_config.api_requests_per_day,
                    'max_alerts': plan_config.max_alerts,
                    'max_watchlist_items': plan_config.max_watchlist_items,
                    'team_seats': plan_config.team_seats
                }
            }
        return {'plan_name': plan_type, 'features': {}, 'limits': {}}
    
    @staticmethod
    def get_advanced_portfolio_analysis(symbols: List[str], user_id: int) -> Dict[str, Any]:
        """Advanced portfolio analysis with risk metrics and optimization"""
        try:
            import yfinance as yf
            import numpy as np
            import pandas as pd
            from datetime import datetime, timedelta
            
            # Get user's plan to determine analysis depth
            user = User.query.get(user_id)
            plan_features = EnhancedPremiumFeatures.get_plan_features(user.plan_type)
            
            if not plan_features['features'].get('portfolio_optimization', False):
                raise PlanAccessError("Portfolio optimization requires Pro or Enterprise plan")
            
            # Fetch stock data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=252)  # 1 year of data
            
            portfolio_data = {}
            returns_data = []
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(start=start_date, end=end_date)
                    
                    if not hist.empty:
                        # Calculate returns
                        returns = hist['Close'].pct_change().dropna()
                        returns_data.append(returns)
                        
                        # Basic stock info
                        info = ticker.info
                        portfolio_data[symbol] = {
                            'current_price': hist['Close'].iloc[-1],
                            'returns_annualized': returns.mean() * 252,
                            'volatility_annualized': returns.std() * np.sqrt(252),
                            'sharpe_ratio': (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0,
                            'sector': info.get('sector', 'Unknown'),
                            'market_cap': info.get('marketCap', 0),
                            'beta': info.get('beta', 1.0)
                        }
                        
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol}: {e}")
                    continue
            
            if not portfolio_data:
                return {
                    'success': False,
                    'error': 'No valid stock data found for analysis'
                }
            
            # Calculate portfolio metrics
            portfolio_metrics = EnhancedPremiumFeatures._calculate_portfolio_metrics(
                portfolio_data, returns_data, user.plan_type
            )
            
            # Risk analysis
            risk_analysis = EnhancedPremiumFeatures._calculate_risk_metrics(
                portfolio_data, returns_data
            )
            
            # Optimization suggestions (Enterprise only)
            optimization_suggestions = []
            if plan_features['features'].get('team_collaboration', False):  # Enterprise feature
                optimization_suggestions = EnhancedPremiumFeatures._generate_optimization_suggestions(
                    portfolio_data, risk_analysis
                )
            
            return {
                'success': True,
                'analysis': {
                    'portfolio_metrics': portfolio_metrics,
                    'risk_analysis': risk_analysis,
                    'individual_stocks': portfolio_data,
                    'optimization_suggestions': optimization_suggestions,
                    'analysis_date': datetime.now().isoformat(),
                    'plan_level': user.plan_type
                }
            }
            
        except PlanAccessError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Portfolio analysis error: {e}")
            return {'success': False, 'error': 'Portfolio analysis failed'}
    
    @staticmethod
    def get_ai_market_scanner(user_id: int, filters: Dict = None) -> Dict[str, Any]:
        """AI-powered market scanner with intelligent filtering"""
        try:
            user = User.query.get(user_id)
            plan_features = EnhancedPremiumFeatures.get_plan_features(user.plan_type)
            
            if not plan_features['features'].get('market_scanner', False):
                raise PlanAccessError("AI Market Scanner requires Pro or Enterprise plan")
            
            # Default filters
            if not filters:
                filters = {
                    'market_cap_min': 1000000000,  # $1B minimum
                    'volume_min': 1000000,        # 1M shares minimum
                    'price_change_min': -10,      # -10% to +10% price change
                    'price_change_max': 10,
                    'sectors': ['Technology', 'Healthcare', 'Financial Services'],
                    'max_results': 50 if user.plan_type == 'enterprise' else 20
                }
            
            # Simulated AI scanner results (in production, integrate with real market data)
            scanner_results = EnhancedPremiumFeatures._generate_scanner_results(filters, user.plan_type)
            
            return {
                'success': True,
                'scanner_results': scanner_results,
                'filters_applied': filters,
                'scan_time': datetime.now().isoformat(),
                'plan_level': user.plan_type
            }
            
        except PlanAccessError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Market scanner error: {e}")
            return {'success': False, 'error': 'Market scanner failed'}
    
    @staticmethod
    def get_earnings_predictions(symbol: str, user_id: int) -> Dict[str, Any]:
        """AI-powered earnings predictions and analysis"""
        try:
            user = User.query.get(user_id)
            plan_features = EnhancedPremiumFeatures.get_plan_features(user.plan_type)
            
            if not plan_features['features'].get('earnings_predictions', False):
                raise PlanAccessError("Earnings predictions require Pro or Enterprise plan")
            
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get earnings data
            earnings_dates = ticker.calendar
            financials = ticker.financials
            
            # Generate AI predictions (simplified for demo)
            predictions = {
                'next_earnings_date': earnings_dates.index[0].strftime('%Y-%m-%d') if not earnings_dates.empty else None,
                'predicted_eps': {
                    'estimate': round(info.get('forwardEps', 0) * 1.05, 2),
                    'confidence': 0.78,
                    'range': {
                        'low': round(info.get('forwardEps', 0) * 0.95, 2),
                        'high': round(info.get('forwardEps', 0) * 1.15, 2)
                    }
                },
                'revenue_prediction': {
                    'estimate': info.get('revenueQuarterlyGrowth', 0.05) * 100,
                    'confidence': 0.72
                },
                'price_impact': {
                    'beat_scenario': '+3.5% to +7.2%',
                    'meet_scenario': '-1.0% to +2.0%',
                    'miss_scenario': '-5.5% to -2.8%'
                },
                'analyst_sentiment': 'Cautiously Optimistic',
                'key_factors': [
                    'Strong market position',
                    'Improving margins',
                    'Headwinds from competition'
                ]
            }
            
            # Enhanced analysis for Enterprise users
            if user.plan_type == 'enterprise':
                predictions['advanced_metrics'] = {
                    'surprise_probability': 0.65,
                    'institutional_expectations': 'Slightly Above Consensus',
                    'options_market_sentiment': 'Neutral to Bullish',
                    'historical_beat_rate': 0.72
                }
            
            return {
                'success': True,
                'symbol': symbol.upper(),
                'predictions': predictions,
                'analysis_date': datetime.now().isoformat(),
                'plan_level': user.plan_type
            }
            
        except PlanAccessError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Earnings prediction error for {symbol}: {e}")
            return {'success': False, 'error': 'Earnings prediction failed'}
    
    @staticmethod
    def _calculate_portfolio_metrics(portfolio_data: Dict, returns_data: List, plan_type: str) -> Dict:
        """Calculate comprehensive portfolio metrics"""
        import numpy as np
        
        if not portfolio_data:
            return {}
        
        # Basic metrics
        total_value = sum(stock['current_price'] for stock in portfolio_data.values())
        avg_returns = np.mean([stock['returns_annualized'] for stock in portfolio_data.values()])
        avg_volatility = np.mean([stock['volatility_annualized'] for stock in portfolio_data.values()])
        
        metrics = {
            'total_positions': len(portfolio_data),
            'average_return': avg_returns,
            'average_volatility': avg_volatility,
            'portfolio_beta': np.mean([stock.get('beta', 1.0) for stock in portfolio_data.values()]),
            'diversification_score': min(len(set(stock.get('sector', 'Unknown') for stock in portfolio_data.values())) / 11.0, 1.0)
        }
        
        # Advanced metrics for Pro+ users
        if plan_type in ['pro', 'enterprise']:
            if len(returns_data) > 1:
                correlation_matrix = np.corrcoef([r.values for r in returns_data if len(r) > 0])
                avg_correlation = np.mean(correlation_matrix[np.triu_indices_from(correlation_matrix, k=1)])
                
                metrics.update({
                    'correlation_score': avg_correlation,
                    'concentration_risk': max([stock['current_price']/total_value for stock in portfolio_data.values()]) if total_value > 0 else 0,
                    'sector_concentration': EnhancedPremiumFeatures._calculate_sector_concentration(portfolio_data)
                })
        
        return metrics
    
    @staticmethod
    def _calculate_risk_metrics(portfolio_data: Dict, returns_data: List) -> Dict:
        """Calculate comprehensive risk metrics"""
        import numpy as np
        
        if not returns_data:
            return {'overall_risk': 'Unknown'}
        
        volatilities = [stock['volatility_annualized'] for stock in portfolio_data.values()]
        avg_volatility = np.mean(volatilities)
        
        # Risk categorization
        if avg_volatility < 0.15:
            risk_level = 'Low'
        elif avg_volatility < 0.25:
            risk_level = 'Moderate'
        elif avg_volatility < 0.35:
            risk_level = 'High'
        else:
            risk_level = 'Very High'
        
        return {
            'overall_risk': risk_level,
            'average_volatility': avg_volatility,
            'volatility_range': {
                'min': min(volatilities),
                'max': max(volatilities)
            },
            'risk_factors': EnhancedPremiumFeatures._identify_risk_factors(portfolio_data)
        }
    
    @staticmethod
    def _generate_optimization_suggestions(portfolio_data: Dict, risk_analysis: Dict) -> List[Dict]:
        """Generate portfolio optimization suggestions"""
        suggestions = []
        
        # Diversification suggestions
        sectors = [stock.get('sector', 'Unknown') for stock in portfolio_data.values()]
        sector_counts = {}
        for sector in sectors:
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        overweight_sectors = [sector for sector, count in sector_counts.items() if count > 3]
        if overweight_sectors:
            suggestions.append({
                'type': 'diversification',
                'priority': 'high',
                'title': 'Reduce Sector Concentration',
                'description': f"Consider reducing exposure to {', '.join(overweight_sectors)} sectors",
                'action': 'rebalance'
            })
        
        # Risk-based suggestions
        if risk_analysis['overall_risk'] in ['High', 'Very High']:
            suggestions.append({
                'type': 'risk_reduction',
                'priority': 'medium',
                'title': 'Consider Lower Volatility Assets',
                'description': 'Portfolio volatility is elevated. Consider adding defensive positions.',
                'action': 'hedge'
            })
        
        # Performance suggestions
        underperformers = [symbol for symbol, data in portfolio_data.items() 
                          if data['returns_annualized'] < 0]
        if len(underperformers) > len(portfolio_data) * 0.4:
            suggestions.append({
                'type': 'performance',
                'priority': 'medium',
                'title': 'Review Underperforming Positions',
                'description': f"Several positions showing negative returns: {', '.join(underperformers[:3])}",
                'action': 'review'
            })
        
        return suggestions
    
    @staticmethod
    def _generate_scanner_results(filters: Dict, plan_type: str) -> List[Dict]:
        """Generate simulated market scanner results"""
        # Simulated results - in production, integrate with real market data APIs
        base_results = [
            {
                'symbol': 'NVDA',
                'company_name': 'NVIDIA Corporation',
                'price': 875.45,
                'change_percent': 2.34,
                'volume': 15234567,
                'market_cap': 2150000000000,
                'sector': 'Technology',
                'ai_score': 0.89,
                'momentum': 'Strong Bullish',
                'signals': ['Technical Breakout', 'Volume Surge', 'Analyst Upgrade']
            },
            {
                'symbol': 'TSLA',
                'company_name': 'Tesla, Inc.',
                'price': 245.67,
                'change_percent': -1.23,
                'volume': 8765432,
                'market_cap': 780000000000,
                'sector': 'Technology',
                'ai_score': 0.76,
                'momentum': 'Neutral',
                'signals': ['Support Level Hold', 'Options Activity']
            }
        ]
        
        # Add more results for higher tier plans
        if plan_type == 'enterprise':
            base_results.extend([
                {
                    'symbol': 'AMZN',
                    'company_name': 'Amazon.com, Inc.',
                    'price': 3456.78,
                    'change_percent': 1.89,
                    'volume': 3456789,
                    'market_cap': 1800000000000,
                    'sector': 'Technology',
                    'ai_score': 0.82,
                    'momentum': 'Moderate Bullish',
                    'signals': ['Earnings Beat', 'Revenue Growth']
                }
            ])
        
        return base_results[:filters.get('max_results', 20)]
    
    @staticmethod
    def _calculate_sector_concentration(portfolio_data: Dict) -> Dict:
        """Calculate sector concentration metrics"""
        sectors = {}
        total_value = sum(stock['current_price'] for stock in portfolio_data.values())
        
        for stock in portfolio_data.values():
            sector = stock.get('sector', 'Unknown')
            weight = stock['current_price'] / total_value if total_value > 0 else 0
            sectors[sector] = sectors.get(sector, 0) + weight
        
        return {
            'sectors': sectors,
            'max_concentration': max(sectors.values()) if sectors else 0,
            'herfindahl_index': sum(weight**2 for weight in sectors.values())
        }
    
    @staticmethod
    def _identify_risk_factors(portfolio_data: Dict) -> List[str]:
        """Identify key risk factors in the portfolio"""
        risk_factors = []
        
        # High beta concentration
        high_beta_count = sum(1 for stock in portfolio_data.values() if stock.get('beta', 1.0) > 1.5)
        if high_beta_count > len(portfolio_data) * 0.5:
            risk_factors.append('High Beta Concentration')
        
        # Sector concentration
        sectors = [stock.get('sector', 'Unknown') for stock in portfolio_data.values()]
        if sectors.count(max(set(sectors), key=sectors.count)) > len(sectors) * 0.6:
            risk_factors.append('Sector Concentration Risk')
        
        # Volatility cluster
        high_vol_count = sum(1 for stock in portfolio_data.values() if stock['volatility_annualized'] > 0.3)
        if high_vol_count > len(portfolio_data) * 0.4:
            risk_factors.append('High Volatility Cluster')
        
        return risk_factors or ['Moderate Diversification']

# Global instance
enhanced_features = EnhancedPremiumFeatures()