"""
Portfolio Management System for TradeWise AI
Handles portfolio tracking, performance analytics, and holdings management
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yfinance as yf
from sqlalchemy import func, and_
from models import Portfolio, Trade, UserAccount, User
from app import db

logger = logging.getLogger(__name__)

class PortfolioManager:
    """Comprehensive portfolio management and analytics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_user_portfolio(self, user_id: str) -> Dict:
        """Get complete portfolio data for user"""
        try:
            # Get all portfolio holdings
            holdings = Portfolio.query.filter_by(user_id=user_id).all()
            
            # Get user account for cash balance
            account = UserAccount.query.filter_by(user_id=user_id).first()
            cash_balance = account.balance if account else 0.0
            
            # Calculate portfolio metrics
            portfolio_data = {
                'holdings': [],
                'total_value': 0.0,
                'total_invested': 0.0,
                'daily_change': 0.0,
                'daily_change_percent': 0.0,
                'cash_balance': cash_balance,
                'performance_data': []
            }
            
            total_market_value = 0.0
            total_cost_basis = 0.0
            
            for holding in holdings:
                # Get current price
                current_price = self._get_current_price(holding.symbol)
                
                if current_price:
                    market_value = holding.quantity * current_price
                    cost_basis = holding.quantity * holding.average_price
                    profit_loss = market_value - cost_basis
                    profit_loss_percent = (profit_loss / cost_basis * 100) if cost_basis > 0 else 0.0
                    
                    holding_data = {
                        'symbol': holding.symbol,
                        'quantity': holding.quantity,
                        'average_price': holding.average_price,
                        'current_price': current_price,
                        'market_value': market_value,
                        'cost_basis': cost_basis,
                        'profit_loss': profit_loss,
                        'profit_loss_percent': profit_loss_percent,
                        'weight': 0.0  # Will be calculated after total
                    }
                    
                    portfolio_data['holdings'].append(holding_data)
                    total_market_value += market_value
                    total_cost_basis += cost_basis
            
            # Calculate portfolio totals
            portfolio_data['total_value'] = total_market_value + cash_balance
            portfolio_data['total_invested'] = total_cost_basis
            portfolio_data['total_return'] = total_market_value - total_cost_basis
            portfolio_data['total_return_percent'] = (portfolio_data['total_return'] / total_cost_basis * 100) if total_cost_basis > 0 else 0.0
            
            # Calculate weights
            for holding in portfolio_data['holdings']:
                holding['weight'] = (holding['market_value'] / total_market_value * 100) if total_market_value > 0 else 0.0
            
            # Get performance history
            portfolio_data['performance_data'] = self._get_portfolio_performance_history(user_id)
            
            return {
                'success': True,
                'portfolio': portfolio_data
            }
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio for user {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'portfolio': {
                    'holdings': [],
                    'total_value': 0.0,
                    'cash_balance': 0.0,
                    'performance_data': []
                }
            }
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a stock symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Try different price fields
            current_price = (
                info.get('currentPrice') or 
                info.get('regularMarketPrice') or 
                info.get('previousClose')
            )
            
            return float(current_price) if current_price else None
            
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    def _get_portfolio_performance_history(self, user_id: str, days: int = 30) -> List[Dict]:
        """Get portfolio performance over time"""
        try:
            # Get trades history for the past period
            start_date = datetime.now() - timedelta(days=days)
            trades = Trade.query.filter(
                and_(
                    Trade.user_id == user_id,
                    Trade.trade_date >= start_date
                )
            ).order_by(Trade.trade_date).all()
            
            # Generate performance data points
            performance_data = []
            current_date = start_date
            
            while current_date <= datetime.now():
                # Calculate portfolio value at this point in time
                portfolio_value = self._calculate_portfolio_value_at_date(user_id, current_date)
                
                performance_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'value': portfolio_value,
                    'timestamp': int(current_date.timestamp())
                })
                
                current_date += timedelta(days=1)
            
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Error getting performance history: {e}")
            return []
    
    def _calculate_portfolio_value_at_date(self, user_id: str, target_date: datetime) -> float:
        """Calculate portfolio value at a specific date"""
        try:
            # Get all trades up to the target date
            trades = Trade.query.filter(
                and_(
                    Trade.user_id == user_id,
                    Trade.trade_date <= target_date
                )
            ).all()
            
            # Calculate holdings at that date
            holdings = {}
            for trade in trades:
                if trade.symbol not in holdings:
                    holdings[trade.symbol] = 0
                
                if trade.trade_type == 'buy':
                    holdings[trade.symbol] += trade.quantity
                else:  # sell
                    holdings[trade.symbol] -= trade.quantity
            
            # Calculate total value (simplified - using current prices)
            total_value = 0.0
            for symbol, quantity in holdings.items():
                if quantity > 0:
                    current_price = self._get_current_price(symbol)
                    if current_price:
                        total_value += quantity * current_price
            
            return total_value
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio value at date: {e}")
            return 0.0
    
    def get_portfolio_analytics(self, user_id: str) -> Dict:
        """Get advanced portfolio analytics and insights"""
        try:
            portfolio = self.get_user_portfolio(user_id)
            if not portfolio['success']:
                return portfolio
            
            holdings = portfolio['portfolio']['holdings']
            
            # Risk analysis
            risk_metrics = self._calculate_risk_metrics(holdings)
            
            # Diversification analysis
            diversification = self._analyze_diversification(holdings)
            
            # Performance comparison
            benchmark_comparison = self._compare_to_benchmark(user_id)
            
            # Recommendations
            recommendations = self._generate_portfolio_recommendations(holdings, risk_metrics)
            
            analytics = {
                'risk_metrics': risk_metrics,
                'diversification': diversification,
                'benchmark_comparison': benchmark_comparison,
                'recommendations': recommendations,
                'sector_allocation': self._get_sector_allocation(holdings),
                'top_performers': self._get_top_performers(holdings),
                'underperformers': self._get_underperformers(holdings)
            }
            
            return {
                'success': True,
                'analytics': analytics
            }
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio analytics: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_risk_metrics(self, holdings: List[Dict]) -> Dict:
        """Calculate portfolio risk metrics"""
        try:
            if not holdings:
                return {
                    'portfolio_beta': 0.0,
                    'volatility': 0.0,
                    'sharpe_ratio': 0.0,
                    'risk_level': 'Low'
                }
            
            # Simplified risk calculation
            total_value = sum(h['market_value'] for h in holdings)
            weighted_volatility = 0.0
            
            for holding in holdings:
                # Estimate volatility based on stock characteristics
                symbol = holding['symbol']
                weight = holding['market_value'] / total_value if total_value > 0 else 0
                
                # Simplified volatility estimation
                estimated_volatility = self._estimate_stock_volatility(symbol)
                weighted_volatility += weight * estimated_volatility
            
            # Determine risk level
            if weighted_volatility < 15:
                risk_level = 'Low'
            elif weighted_volatility < 25:
                risk_level = 'Medium'
            else:
                risk_level = 'High'
            
            return {
                'portfolio_beta': round(weighted_volatility / 20, 2),  # Simplified beta
                'volatility': round(weighted_volatility, 2),
                'sharpe_ratio': round(max(0, (10 - weighted_volatility) / 10), 2),  # Simplified Sharpe
                'risk_level': risk_level
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating risk metrics: {e}")
            return {
                'portfolio_beta': 0.0,
                'volatility': 0.0,
                'sharpe_ratio': 0.0,
                'risk_level': 'Unknown'
            }
    
    def _estimate_stock_volatility(self, symbol: str) -> float:
        """Estimate stock volatility based on symbol characteristics"""
        # Simplified volatility estimation
        large_cap_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'BRK.B', 'JNJ', 'V', 'WMT']
        tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX', 'NVDA', 'AMD', 'INTC']
        growth_stocks = ['TSLA', 'NVDA', 'AMD', 'SQ', 'ROKU', 'ZOOM', 'PTON']
        
        base_volatility = 20.0  # Base volatility
        
        if symbol in large_cap_stocks:
            base_volatility -= 5.0
        if symbol in tech_stocks:
            base_volatility += 3.0
        if symbol in growth_stocks:
            base_volatility += 8.0
            
        return max(5.0, min(50.0, base_volatility))  # Clamp between 5% and 50%
    
    def _analyze_diversification(self, holdings: List[Dict]) -> Dict:
        """Analyze portfolio diversification"""
        try:
            if len(holdings) == 0:
                return {
                    'diversification_score': 0,
                    'concentration_risk': 'High',
                    'recommendations': ['Add more positions to reduce concentration risk']
                }
            
            # Calculate concentration
            total_value = sum(h['market_value'] for h in holdings)
            max_position = max(h['market_value'] for h in holdings) if holdings else 0
            concentration = (max_position / total_value * 100) if total_value > 0 else 0
            
            # Diversification score based on number of holdings and concentration
            num_holdings = len(holdings)
            diversification_score = min(100, (num_holdings * 10) - concentration)
            
            # Concentration risk assessment
            if concentration > 40:
                concentration_risk = 'High'
            elif concentration > 25:
                concentration_risk = 'Medium'
            else:
                concentration_risk = 'Low'
            
            recommendations = []
            if num_holdings < 5:
                recommendations.append('Consider adding more holdings for better diversification')
            if concentration > 30:
                recommendations.append('Consider reducing concentration in your largest position')
            if num_holdings > 20:
                recommendations.append('Consider consolidating some smaller positions')
            
            return {
                'diversification_score': round(diversification_score),
                'concentration_risk': concentration_risk,
                'number_of_holdings': num_holdings,
                'largest_position_percent': round(concentration, 1),
                'recommendations': recommendations
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing diversification: {e}")
            return {
                'diversification_score': 0,
                'concentration_risk': 'Unknown',
                'recommendations': []
            }
    
    def _compare_to_benchmark(self, user_id: str) -> Dict:
        """Compare portfolio performance to market benchmarks"""
        try:
            # Simplified benchmark comparison
            portfolio = self.get_user_portfolio(user_id)
            if not portfolio['success']:
                return {}
            
            portfolio_return = portfolio['portfolio'].get('total_return_percent', 0.0)
            
            # Simplified benchmark returns (would be real market data in production)
            benchmarks = {
                'S&P 500': 8.5,
                'NASDAQ': 12.2,
                'Dow Jones': 6.8,
                'Russell 2000': 9.1
            }
            
            comparisons = {}
            for benchmark, benchmark_return in benchmarks.items():
                outperformance = portfolio_return - benchmark_return
                comparisons[benchmark] = {
                    'benchmark_return': benchmark_return,
                    'outperformance': round(outperformance, 2),
                    'status': 'Outperforming' if outperformance > 0 else 'Underperforming'
                }
            
            return {
                'portfolio_return': round(portfolio_return, 2),
                'benchmarks': comparisons
            }
            
        except Exception as e:
            self.logger.error(f"Error comparing to benchmark: {e}")
            return {}
    
    def _generate_portfolio_recommendations(self, holdings: List[Dict], risk_metrics: Dict) -> List[Dict]:
        """Generate AI-powered portfolio recommendations"""
        try:
            recommendations = []
            
            if not holdings:
                recommendations.append({
                    'type': 'diversification',
                    'priority': 'high',
                    'title': 'Start Building Your Portfolio',
                    'description': 'Begin with 3-5 positions in different sectors for basic diversification',
                    'action': 'Consider adding blue-chip stocks like AAPL, MSFT, or broad market ETFs'
                })
                return recommendations
            
            # Risk-based recommendations
            risk_level = risk_metrics.get('risk_level', 'Medium')
            volatility = risk_metrics.get('volatility', 20)
            
            if risk_level == 'High':
                recommendations.append({
                    'type': 'risk_management',
                    'priority': 'high',
                    'title': 'High Risk Portfolio Detected',
                    'description': f'Portfolio volatility of {volatility}% suggests high risk',
                    'action': 'Consider adding defensive stocks or bonds to reduce volatility'
                })
            
            # Concentration recommendations
            total_value = sum(h['market_value'] for h in holdings)
            for holding in holdings:
                weight = (holding['market_value'] / total_value * 100) if total_value > 0 else 0
                if weight > 30:
                    recommendations.append({
                        'type': 'concentration',
                        'priority': 'medium',
                        'title': f'High Concentration in {holding["symbol"]}',
                        'description': f'{holding["symbol"]} represents {weight:.1f}% of your portfolio',
                        'action': 'Consider taking some profits and diversifying into other positions'
                    })
            
            # Performance recommendations
            for holding in holdings:
                if holding['profit_loss_percent'] < -15:
                    recommendations.append({
                        'type': 'performance',
                        'priority': 'medium',
                        'title': f'{holding["symbol"]} Underperforming',
                        'description': f'Down {abs(holding["profit_loss_percent"]):.1f}% from your cost basis',
                        'action': 'Review investment thesis and consider stop-loss or position reduction'
                    })
                elif holding['profit_loss_percent'] > 50:
                    recommendations.append({
                        'type': 'profit_taking',
                        'priority': 'low',
                        'title': f'Consider Profit Taking on {holding["symbol"]}',
                        'description': f'Up {holding["profit_loss_percent"]:.1f}% from your cost basis',
                        'action': 'Consider taking partial profits to lock in gains'
                    })
            
            return recommendations[:5]  # Limit to top 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _get_sector_allocation(self, holdings: List[Dict]) -> Dict:
        """Get sector allocation breakdown"""
        try:
            # Simplified sector mapping
            sector_map = {
                'AAPL': 'Technology',
                'MSFT': 'Technology', 
                'GOOGL': 'Technology',
                'AMZN': 'Consumer Discretionary',
                'TSLA': 'Consumer Discretionary',
                'META': 'Technology',
                'NVDA': 'Technology',
                'JNJ': 'Healthcare',
                'JPM': 'Financial Services',
                'V': 'Financial Services',
                'WMT': 'Consumer Staples',
                'DIS': 'Communication Services'
            }
            
            sector_allocation = {}
            total_value = sum(h['market_value'] for h in holdings)
            
            for holding in holdings:
                sector = sector_map.get(holding['symbol'], 'Other')
                weight = (holding['market_value'] / total_value * 100) if total_value > 0 else 0
                
                if sector in sector_allocation:
                    sector_allocation[sector] += weight
                else:
                    sector_allocation[sector] = weight
            
            return {k: round(v, 1) for k, v in sector_allocation.items()}
            
        except Exception as e:
            self.logger.error(f"Error getting sector allocation: {e}")
            return {}
    
    def _get_top_performers(self, holdings: List[Dict]) -> List[Dict]:
        """Get top performing holdings"""
        try:
            sorted_holdings = sorted(
                holdings, 
                key=lambda x: x['profit_loss_percent'], 
                reverse=True
            )
            return sorted_holdings[:3]
            
        except Exception as e:
            self.logger.error(f"Error getting top performers: {e}")
            return []
    
    def _get_underperformers(self, holdings: List[Dict]) -> List[Dict]:
        """Get underperforming holdings"""
        try:
            sorted_holdings = sorted(
                holdings, 
                key=lambda x: x['profit_loss_percent']
            )
            return [h for h in sorted_holdings[:3] if h['profit_loss_percent'] < 0]
            
        except Exception as e:
            self.logger.error(f"Error getting underperformers: {e}")
            return []

# Global portfolio manager instance
portfolio_manager = PortfolioManager()