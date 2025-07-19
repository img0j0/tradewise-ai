"""
AI-Powered Portfolio Builder
Automatically creates diversified portfolios based on user risk tolerance and goals
"""

import logging
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class PortfolioBuilder:
    def __init__(self):
        """Initialize the portfolio builder with predefined allocations and stock pools"""
        
        # Stock pools by category (real tickers)
        self.stock_pools = {
            'large_cap_growth': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA'],
            'large_cap_value': ['BRK.B', 'JPM', 'V', 'JNJ', 'PG', 'HD', 'UNH'],
            'mid_cap': ['AMD', 'NFLX', 'CRM', 'PYPL', 'UBER', 'SHOP', 'SQ'],
            'small_cap': ['ROKU', 'PLTR', 'COIN', 'SOFI', 'HOOD', 'RBLX', 'SNOW'],
            'international': ['ASML', 'TSM', 'BABA', 'NIO', 'SAP', 'ADBE', 'CRM'],
            'bonds_etf': ['TLT', 'IEF', 'LQD', 'HYG', 'AGG'],
            'commodities_etf': ['GLD', 'SLV', 'DBA', 'USO', 'PDBC'],
            'real_estate': ['VNQ', 'IYR', 'REIT', 'SPG', 'PLD', 'AMT', 'CCI'],
            'dividend': ['VIG', 'SCHD', 'VYM', 'DVY', 'NOBL', 'HDV'],
            'tech_focused': ['QQQ', 'XLK', 'VGT', 'FTEC', 'SOXX', 'ARKK'],
            'defensive': ['XLP', 'XLU', 'VDC', 'FMCG', 'PEP', 'KO', 'WMT']
        }
        
        # Portfolio allocation strategies
        self.portfolio_strategies = {
            'conservative': {
                'name': 'Conservative Growth',
                'description': 'Focus on stability with modest growth potential',
                'risk_level': 'Low',
                'expected_return': '5-8% annually',
                'allocation': {
                    'large_cap_value': 30,
                    'bonds_etf': 25,
                    'dividend': 20,
                    'defensive': 15,
                    'real_estate': 10
                }
            },
            'balanced': {
                'name': 'Balanced Portfolio',
                'description': 'Equal focus on growth and stability',
                'risk_level': 'Medium',
                'expected_return': '7-10% annually',
                'allocation': {
                    'large_cap_growth': 25,
                    'large_cap_value': 20,
                    'mid_cap': 15,
                    'international': 15,
                    'bonds_etf': 15,
                    'dividend': 10
                }
            },
            'growth': {
                'name': 'Growth Focused',
                'description': 'Emphasis on capital appreciation',
                'risk_level': 'Medium-High',
                'expected_return': '9-12% annually',
                'allocation': {
                    'large_cap_growth': 35,
                    'mid_cap': 20,
                    'tech_focused': 15,
                    'small_cap': 15,
                    'international': 10,
                    'bonds_etf': 5
                }
            },
            'aggressive': {
                'name': 'Aggressive Growth',
                'description': 'Maximum growth potential with higher risk',
                'risk_level': 'High',
                'expected_return': '12-18% annually',
                'allocation': {
                    'large_cap_growth': 30,
                    'tech_focused': 25,
                    'small_cap': 20,
                    'mid_cap': 15,
                    'commodities_etf': 10
                }
            },
            'income': {
                'name': 'Income Focused',
                'description': 'Prioritizes dividend income and stability',
                'risk_level': 'Low-Medium',
                'expected_return': '6-9% annually',
                'allocation': {
                    'dividend': 35,
                    'large_cap_value': 25,
                    'real_estate': 20,
                    'bonds_etf': 15,
                    'defensive': 5
                }
            }
        }
        
        logger.info("Portfolio Builder initialized with 5 strategy types")

    def build_portfolio(self, strategy: str, investment_amount: float, 
                       user_preferences: Optional[Dict] = None) -> Dict:
        """
        Build a diversified portfolio based on strategy and investment amount
        
        Args:
            strategy: Portfolio strategy ('conservative', 'balanced', 'growth', 'aggressive', 'income')
            investment_amount: Total amount to invest
            user_preferences: Optional user preferences (sectors to avoid, ESG focus, etc.)
        
        Returns:
            Complete portfolio with allocations and stock selections
        """
        try:
            if strategy not in self.portfolio_strategies:
                raise ValueError(f"Invalid strategy: {strategy}")
            
            strategy_config = self.portfolio_strategies[strategy]
            portfolio = {
                'strategy': strategy_config,
                'total_investment': investment_amount,
                'created_at': datetime.now().isoformat(),
                'holdings': [],
                'allocation_summary': {},
                'performance_metrics': {
                    'diversification_score': 0,
                    'risk_score': 0,
                    'expected_annual_return': strategy_config['expected_return']
                }
            }
            
            # Calculate actual dollar amounts for each category
            allocations = strategy_config['allocation']
            
            for category, percentage in allocations.items():
                category_amount = (percentage / 100) * investment_amount
                
                # Select stocks from this category
                stocks = self._select_stocks_from_category(
                    category, category_amount, user_preferences
                )
                
                portfolio['holdings'].extend(stocks)
                portfolio['allocation_summary'][category] = {
                    'percentage': percentage,
                    'amount': category_amount,
                    'stocks': len(stocks)
                }
            
            # Calculate portfolio metrics
            portfolio['performance_metrics'] = self._calculate_portfolio_metrics(
                portfolio['holdings'], strategy
            )
            
            logger.info(f"Built {strategy} portfolio with {len(portfolio['holdings'])} holdings")
            return portfolio
            
        except Exception as e:
            logger.error(f"Error building portfolio: {str(e)}")
            return {'error': str(e)}

    def _select_stocks_from_category(self, category: str, amount: float, 
                                   user_preferences: Optional[Dict] = None) -> List[Dict]:
        """Select appropriate stocks from a category based on investment amount"""
        
        if category not in self.stock_pools:
            return []
        
        available_stocks = self.stock_pools[category].copy()
        
        # Apply user preferences (sector exclusions, ESG filters, etc.)
        if user_preferences:
            if 'exclude_sectors' in user_preferences:
                # Simple exclusion logic (would be more sophisticated in production)
                pass
        
        # Determine number of stocks based on investment amount
        if amount < 500:
            num_stocks = 1
        elif amount < 2000:
            num_stocks = 2
        elif amount < 5000:
            num_stocks = 3
        else:
            num_stocks = min(4, len(available_stocks))
        
        # Randomly select stocks (in production, this would use more sophisticated selection)
        selected_tickers = random.sample(available_stocks, min(num_stocks, len(available_stocks)))
        
        # Calculate equal weighting within category
        amount_per_stock = amount / len(selected_tickers)
        
        holdings = []
        for ticker in selected_tickers:
            # Simulate current price (in production, get from yfinance)
            simulated_price = random.uniform(50, 300)
            shares = max(1, int(amount_per_stock / simulated_price))
            actual_amount = shares * simulated_price
            
            holdings.append({
                'symbol': ticker,
                'shares': shares,
                'price': round(simulated_price, 2),
                'amount': round(actual_amount, 2),
                'category': category,
                'weight': round((actual_amount / amount) * 100, 2) if amount > 0 else 0
            })
        
        return holdings

    def _calculate_portfolio_metrics(self, holdings: List[Dict], strategy: str) -> Dict:
        """Calculate portfolio performance metrics"""
        
        total_positions = len(holdings)
        categories = set(holding['category'] for holding in holdings)
        
        # Diversification score (0-100)
        diversification_score = min(100, (len(categories) * 15) + (total_positions * 5))
        
        # Risk score based on strategy
        risk_scores = {
            'conservative': 25,
            'balanced': 50,
            'growth': 70,
            'aggressive': 90,
            'income': 35
        }
        
        risk_score = risk_scores.get(strategy, 50)
        
        return {
            'diversification_score': diversification_score,
            'risk_score': risk_score,
            'total_positions': total_positions,
            'categories_covered': len(categories),
            'rebalance_frequency': 'Quarterly' if strategy in ['aggressive', 'growth'] else 'Semi-annually'
        }

    def get_strategy_recommendations(self, user_profile: Dict) -> List[Dict]:
        """
        Recommend portfolio strategies based on user profile
        
        Args:
            user_profile: Dict with age, income, risk_tolerance, investment_goals, time_horizon
        
        Returns:
            List of recommended strategies with scores
        """
        
        age = user_profile.get('age', 30)
        risk_tolerance = user_profile.get('risk_tolerance', 'medium')
        time_horizon = user_profile.get('time_horizon', 5)  # years
        investment_goals = user_profile.get('investment_goals', ['growth'])
        
        recommendations = []
        
        for strategy_key, strategy in self.portfolio_strategies.items():
            score = self._calculate_strategy_score(
                strategy_key, age, risk_tolerance, time_horizon, investment_goals
            )
            
            recommendations.append({
                'strategy': strategy_key,
                'score': score,
                'name': strategy['name'],
                'description': strategy['description'],
                'risk_level': strategy['risk_level'],
                'expected_return': strategy['expected_return'],
                'suitability_reasons': self._get_suitability_reasons(
                    strategy_key, age, risk_tolerance, time_horizon
                )
            })
        
        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:3]  # Return top 3 recommendations

    def _calculate_strategy_score(self, strategy: str, age: int, risk_tolerance: str, 
                                time_horizon: int, investment_goals: List[str]) -> int:
        """Calculate how well a strategy matches user profile"""
        
        score = 50  # Base score
        
        # Age factor
        if strategy == 'conservative' and age > 55:
            score += 20
        elif strategy == 'aggressive' and age < 30:
            score += 25
        elif strategy == 'balanced' and 30 <= age <= 50:
            score += 20
        elif strategy == 'growth' and 25 <= age <= 40:
            score += 15
        
        # Risk tolerance factor
        risk_strategy_match = {
            'low': ['conservative', 'income'],
            'medium': ['balanced', 'income'],
            'high': ['growth', 'aggressive']
        }
        
        if strategy in risk_strategy_match.get(risk_tolerance, []):
            score += 25
        
        # Time horizon factor
        if time_horizon >= 10 and strategy in ['growth', 'aggressive']:
            score += 15
        elif time_horizon <= 3 and strategy in ['conservative', 'income']:
            score += 20
        
        # Investment goals factor
        if 'growth' in investment_goals and strategy in ['growth', 'aggressive']:
            score += 15
        elif 'income' in investment_goals and strategy in ['income', 'conservative']:
            score += 15
        elif 'stability' in investment_goals and strategy == 'conservative':
            score += 20
        
        return min(100, score)

    def _get_suitability_reasons(self, strategy: str, age: int, risk_tolerance: str, 
                               time_horizon: int) -> List[str]:
        """Generate reasons why a strategy is suitable for the user"""
        
        reasons = []
        
        strategy_reasons = {
            'conservative': [
                'Low risk approach suitable for capital preservation',
                'Steady dividend income for regular cash flow',
                'Good for investors nearing or in retirement'
            ],
            'balanced': [
                'Provides growth potential with managed risk',
                'Diversified across multiple asset classes',
                'Suitable for medium-term investment horizons'
            ],
            'growth': [
                'Focus on capital appreciation over time',
                'Higher return potential for long-term investors',
                'Good balance of growth and established companies'
            ],
            'aggressive': [
                'Maximum growth potential for young investors',
                'Suitable for long investment time horizons',
                'Higher risk tolerance accommodated'
            ],
            'income': [
                'Regular dividend payments for cash flow needs',
                'Focus on stable, dividend-paying companies',
                'Lower volatility than growth-focused strategies'
            ]
        }
        
        base_reasons = strategy_reasons.get(strategy, [])
        
        # Add personalized reasons based on profile
        if age < 30 and strategy in ['growth', 'aggressive']:
            reasons.append('Your young age allows for higher risk tolerance')
        elif age > 55 and strategy in ['conservative', 'income']:
            reasons.append('Appropriate for pre-retirement planning')
        
        if time_horizon >= 10 and strategy in ['growth', 'aggressive']:
            reasons.append('Long time horizon supports growth-oriented approach')
        
        return base_reasons + reasons

# Global instance
portfolio_builder = PortfolioBuilder()