"""
Simple Investment Strategy Personalization
Creates clear, visible differences in stock analysis based on user-selected investment strategies.
"""

import logging
from flask import session

logger = logging.getLogger(__name__)

class SimplePersonalization:
    """Simple strategy-based personalization that creates visible analytical differences"""
    
    def __init__(self):
        # Define clear investment strategies with distinct characteristics
        self.strategies = {
            'growth_investor': {
                'name': 'Growth Investor',
                'description': 'Focus on companies with strong growth potential',
                'icon': '🚀',
                'buy_threshold': 60,  # Lower threshold for growth stocks
                'sectors_boost': ['Technology', 'Healthcare', 'Consumer Discretionary'],
                'metrics_focus': ['revenue_growth', 'earnings_growth'],
                'risk_adjustment': 'optimistic'
            },
            'value_investor': {
                'name': 'Value Investor', 
                'description': 'Seek undervalued stocks with strong fundamentals',
                'icon': '💎',
                'buy_threshold': 75,  # Higher threshold for value plays
                'sectors_boost': ['Financial Services', 'Utilities', 'Real Estate'],
                'metrics_focus': ['pe_ratio', 'book_value', 'dividend_yield'],
                'risk_adjustment': 'conservative'
            },
            'dividend_investor': {
                'name': 'Dividend Investor',
                'description': 'Prioritize steady income from dividend-paying stocks',
                'icon': '💰',
                'buy_threshold': 70,
                'sectors_boost': ['Utilities', 'Consumer Staples', 'Real Estate'],
                'metrics_focus': ['dividend_yield', 'payout_ratio'],
                'risk_adjustment': 'income_focused'
            },
            'momentum_trader': {
                'name': 'Momentum Trader',
                'description': 'Capitalize on trending stocks and technical signals',
                'icon': '⚡',
                'buy_threshold': 55,  # Lowest threshold for momentum plays
                'sectors_boost': ['Technology', 'Consumer Discretionary'],
                'metrics_focus': ['price_momentum', 'volume', 'rsi'],
                'risk_adjustment': 'aggressive'
            }
        }
    
    def get_user_strategy(self):
        """Get user's selected investment strategy"""
        return session.get('investment_strategy', 'growth_investor')
    
    def set_user_strategy(self, strategy_key):
        """Set user's investment strategy"""
        if strategy_key in self.strategies:
            session['investment_strategy'] = strategy_key
            session.permanent = True
            logger.info(f"User strategy set to: {strategy_key}")
            return True
        return False
    
    def get_available_strategies(self):
        """Get all available investment strategies for UI"""
        return [
            {
                'key': key,
                'name': strategy['name'],
                'description': strategy['description'],
                'icon': strategy['icon']
            }
            for key, strategy in self.strategies.items()
        ]
    
    def personalize_analysis(self, symbol, base_analysis):
        """Apply strategy-based personalization with visible differences"""
        try:
            strategy_key = self.get_user_strategy()
            strategy = self.strategies.get(strategy_key)
            
            if not strategy:
                return base_analysis
            
            # Create a copy of analysis to modify
            analysis = base_analysis.copy()
            original_recommendation = analysis.get('recommendation', 'HOLD')
            original_confidence = analysis.get('confidence', 50)
            
            # Apply strategy-specific adjustments
            analysis = self._apply_strategy_logic(analysis, strategy, symbol)
            
            # Add strategy metadata for display
            analysis['strategy_applied'] = {
                'key': strategy_key,
                'name': strategy['name'],
                'icon': strategy['icon'],
                'description': strategy['description']
            }
            
            # Track if strategy changed the recommendation
            new_recommendation = analysis.get('recommendation', original_recommendation)
            new_confidence = analysis.get('confidence', original_confidence)
            
            if new_recommendation != original_recommendation or abs(new_confidence - original_confidence) > 5:
                analysis['strategy_impact'] = {
                    'changed': True,
                    'original_recommendation': original_recommendation,
                    'original_confidence': original_confidence,
                    'explanation': f"{strategy['name']} strategy modified this analysis"
                }
                logger.info(f"Strategy {strategy_key} changed {symbol}: {original_recommendation}({original_confidence}%) → {new_recommendation}({new_confidence}%)")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error applying strategy personalization: {e}")
            return base_analysis
    
    def _apply_strategy_logic(self, analysis, strategy, symbol):
        """Apply specific strategy logic to create visible differences"""
        
        # Get strategy parameters
        buy_threshold = strategy['buy_threshold']
        risk_adjustment = strategy['risk_adjustment']
        sectors_boost = strategy.get('sectors_boost', [])
        
        # Simple sector mapping for demonstration
        sector_map = {
            'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology',
            'JPM': 'Financial Services', 'BAC': 'Financial Services',
            'JNJ': 'Healthcare', 'PFE': 'Healthcare',
            'XOM': 'Energy', 'CVX': 'Energy',
            'KO': 'Consumer Staples', 'PG': 'Consumer Staples'
        }
        
        stock_sector = sector_map.get(symbol, 'Other')
        original_confidence = analysis.get('confidence', 50)
        
        # Strategy-specific modifications
        if strategy['name'] == 'Growth Investor':
            if stock_sector in sectors_boost:
                # Boost growth stocks
                analysis['confidence'] = min(90, original_confidence + 15)
                analysis['strategy_note'] = f"Growth strategy boosted {stock_sector} stock confidence"
                if original_confidence > 45:
                    analysis['recommendation'] = 'BUY'
            else:
                # Be more selective on non-growth sectors
                analysis['confidence'] = max(30, original_confidence - 10)
                if analysis.get('recommendation') == 'BUY' and original_confidence < 70:
                    analysis['recommendation'] = 'HOLD'
                    analysis['strategy_note'] = "Growth strategy prefers high-growth sectors"
        
        elif strategy['name'] == 'Value Investor':
            # Value investors are more conservative
            if original_confidence < buy_threshold:
                if analysis.get('recommendation') in ['BUY', 'STRONG_BUY']:
                    analysis['recommendation'] = 'HOLD'
                    analysis['strategy_note'] = f"Value strategy requires {buy_threshold}%+ confidence"
            
            if stock_sector in sectors_boost:
                analysis['confidence'] = min(85, original_confidence + 10)
                analysis['strategy_note'] = f"Value strategy favors {stock_sector} fundamentals"
        
        elif strategy['name'] == 'Dividend Investor':
            # Focus on income-generating assets
            if stock_sector in sectors_boost:
                analysis['confidence'] = min(85, original_confidence + 12)
                analysis['recommendation'] = 'BUY' if original_confidence > 55 else analysis.get('recommendation')
                analysis['strategy_note'] = f"Dividend strategy values {stock_sector} income potential"
            else:
                analysis['confidence'] = max(40, original_confidence - 8)
                analysis['strategy_note'] = "Dividend strategy prefers income-generating sectors"
        
        elif strategy['name'] == 'Momentum Trader':
            # More aggressive, lower thresholds
            if original_confidence > 45:
                if analysis.get('recommendation') == 'HOLD':
                    analysis['recommendation'] = 'BUY'
                    analysis['strategy_note'] = "Momentum strategy capitalizes on trends"
                analysis['confidence'] = min(85, original_confidence + 10)
            
            # Add momentum-specific insights
            analysis['momentum_note'] = "Analysis weighted toward technical momentum indicators"
        
        return analysis

# Global instance
simple_personalization = SimplePersonalization()