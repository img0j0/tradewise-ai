"""
Performance Tracking - Track portfolio performance and trading statistics
"""
import json
import time
from typing import List, Dict, Any
import yfinance as yf

class PerformanceTracker:
    def __init__(self):
        self.performance_history = []
        
    def calculate_portfolio_performance(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive portfolio performance metrics"""
        if not portfolio_data.get('holdings'):
            return {
                'total_value': 0,
                'total_invested': 0,
                'total_gain_loss': 0,
                'total_return_percent': 0,
                'best_performer': None,
                'worst_performer': None,
                'win_rate': 0,
                'total_trades': 0
            }
        
        total_value = 0
        total_invested = 0
        winners = 0
        total_trades = len(portfolio_data['holdings'])
        
        best_performer = None
        worst_performer = None
        best_return = float('-inf')
        worst_return = float('inf')
        
        for holding in portfolio_data['holdings']:
            current_value = holding['current_value']
            invested_amount = holding['purchase_price'] * holding['shares']
            gain_loss_percent = holding['gain_loss_percent']
            
            total_value += current_value
            total_invested += invested_amount
            
            if gain_loss_percent > 0:
                winners += 1
            
            # Track best and worst performers
            if gain_loss_percent > best_return:
                best_return = gain_loss_percent
                best_performer = {
                    'symbol': holding['symbol'],
                    'return_percent': gain_loss_percent,
                    'gain_loss': holding['gain_loss']
                }
            
            if gain_loss_percent < worst_return:
                worst_return = gain_loss_percent
                worst_performer = {
                    'symbol': holding['symbol'],
                    'return_percent': gain_loss_percent,
                    'gain_loss': holding['gain_loss']
                }
        
        total_gain_loss = total_value - total_invested
        total_return_percent = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0
        win_rate = (winners / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_value': round(total_value, 2),
            'total_invested': round(total_invested, 2),
            'total_gain_loss': round(total_gain_loss, 2),
            'total_return_percent': round(total_return_percent, 2),
            'best_performer': best_performer,
            'worst_performer': worst_performer,
            'win_rate': round(win_rate, 1),
            'total_trades': total_trades
        }
    
    def get_daily_performance_summary(self) -> Dict[str, Any]:
        """Get today's performance summary"""
        # This would track daily changes in portfolio value
        return {
            'daily_change': 0,  # Would calculate from previous day
            'daily_change_percent': 0,
            'trades_today': 0,
            'top_gainer_today': None,
            'top_loser_today': None
        }
    
    def get_risk_metrics(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate portfolio risk metrics"""
        if not portfolio_data.get('holdings'):
            return {
                'portfolio_beta': 0,
                'diversification_score': 0,
                'concentration_risk': 'Low',
                'sector_allocation': {}
            }
        
        # Calculate concentration risk
        total_value = sum(holding['current_value'] for holding in portfolio_data['holdings'])
        max_position_percent = 0
        
        if total_value > 0:
            max_position_percent = max(
                holding['current_value'] / total_value * 100 
                for holding in portfolio_data['holdings']
            )
        
        concentration_risk = 'High' if max_position_percent > 40 else 'Medium' if max_position_percent > 20 else 'Low'
        
        # Diversification score (simple version based on number of holdings)
        num_holdings = len(portfolio_data['holdings'])
        diversification_score = min(100, num_holdings * 10)  # 10 points per holding, max 100
        
        return {
            'portfolio_beta': 1.0,  # Would need market data to calculate properly
            'diversification_score': diversification_score,
            'concentration_risk': concentration_risk,
            'largest_position_percent': round(max_position_percent, 1),
            'num_positions': num_holdings
        }
    
    def get_trading_insights(self, portfolio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered trading insights"""
        insights = []
        
        if not portfolio_data.get('holdings'):
            insights.append({
                'type': 'suggestion',
                'title': 'Start Building Your Portfolio',
                'message': 'Consider diversifying across different sectors to reduce risk.',
                'priority': 'medium'
            })
            return insights
        
        performance = self.calculate_portfolio_performance(portfolio_data)
        risk_metrics = self.get_risk_metrics(portfolio_data)
        
        # High concentration warning
        if risk_metrics['concentration_risk'] == 'High':
            insights.append({
                'type': 'warning',
                'title': 'High Concentration Risk',
                'message': f"Your largest position represents {risk_metrics['largest_position_percent']}% of your portfolio. Consider diversifying.",
                'priority': 'high'
            })
        
        # Diversification suggestion
        if risk_metrics['diversification_score'] < 50:
            insights.append({
                'type': 'suggestion',
                'title': 'Improve Diversification',
                'message': 'Adding more positions across different sectors could reduce your portfolio risk.',
                'priority': 'medium'
            })
        
        # Performance insights
        if performance['total_return_percent'] > 10:
            insights.append({
                'type': 'positive',
                'title': 'Strong Performance',
                'message': f"Your portfolio is up {performance['total_return_percent']}%! Consider taking some profits.",
                'priority': 'low'
            })
        elif performance['total_return_percent'] < -10:
            insights.append({
                'type': 'warning',
                'title': 'Portfolio Down',
                'message': f"Portfolio is down {abs(performance['total_return_percent'])}%. Review positions for potential rebalancing.",
                'priority': 'medium'
            })
        
        return insights

# Global instance
performance_tracker = PerformanceTracker()