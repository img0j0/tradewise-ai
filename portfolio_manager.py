import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from sqlalchemy import func
from app import db
from models import User, PortfolioHolding

logger = logging.getLogger(__name__)

class PortfolioManager:
    """Comprehensive portfolio management and analytics system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def add_holding(self, user_id: str, symbol: str, shares: float, 
                   purchase_price: float, purchase_date: str = None) -> Dict:
        """Add a new stock holding to user's portfolio"""
        try:
            # Validate stock symbol
            stock_info = self.get_stock_info(symbol.upper())
            if not stock_info:
                return {
                    'success': False,
                    'error': f'Invalid stock symbol: {symbol}',
                    'message': 'Please check the symbol and try again'
                }
            
            # Parse purchase date
            if purchase_date:
                try:
                    purchase_dt = datetime.strptime(purchase_date, '%Y-%m-%d')
                except ValueError:
                    purchase_dt = datetime.now()
            else:
                purchase_dt = datetime.now()
            
            # Check if holding already exists
            existing = PortfolioHolding.query.filter_by(
                user_id=user_id, 
                symbol=symbol.upper()
            ).first()
            
            if existing:
                # Update existing holding
                existing.shares += shares
                existing.average_cost = (
                    (existing.average_cost * (existing.shares - shares)) + 
                    (purchase_price * shares)
                ) / existing.shares
                existing.last_updated = datetime.now()
                
                db.session.commit()
                action = 'updated'
            else:
                # Create new holding
                holding = PortfolioHolding(
                    user_id=user_id,
                    symbol=symbol.upper(),
                    shares=shares,
                    average_cost=purchase_price,
                    purchase_date=purchase_dt,
                    last_updated=datetime.now()
                )
                
                db.session.add(holding)
                db.session.commit()
                action = 'added'
            
            current_price = stock_info.get('current_price', purchase_price)
            return {
                'success': True,
                'action': action,
                'holding': {
                    'symbol': symbol.upper(),
                    'company_name': stock_info.get('company_name', symbol),
                    'shares': shares,
                    'purchase_price': purchase_price,
                    'current_price': current_price,
                    'market_value': shares * current_price,
                    'cost_basis': shares * purchase_price,
                    'unrealized_gain_loss': (current_price - purchase_price) * shares,
                    'gain_loss_percent': ((current_price - purchase_price) / purchase_price) * 100
                }
            }
            
        except Exception as e:
            logger.error(f"Error adding holding: {e}")
            return {
                'success': False,
                'error': 'Failed to add holding',
                'message': 'Please try again or contact support'
            }
    
    def remove_holding(self, user_id: str, symbol: str, shares: float = None) -> Dict:
        """Remove or reduce shares from a holding"""
        try:
            holding = PortfolioHolding.query.filter_by(
                user_id=user_id, 
                symbol=symbol.upper()
            ).first()
            
            if not holding:
                return {
                    'success': False,
                    'error': 'Holding not found',
                    'message': f'You do not have {symbol.upper()} in your portfolio'
                }
            
            if shares is None or shares >= holding.shares:
                # Remove entire holding
                db.session.delete(holding)
                action = 'removed'
                remaining_shares = 0
            else:
                # Reduce shares
                holding.shares -= shares
                holding.last_updated = datetime.now()
                action = 'reduced'
                remaining_shares = holding.shares
            
            db.session.commit()
            
            return {
                'success': True,
                'action': action,
                'symbol': symbol.upper(),
                'shares_removed': shares or holding.shares,
                'remaining_shares': remaining_shares
            }
            
        except Exception as e:
            logger.error(f"Error removing holding: {e}")
            return {
                'success': False,
                'error': 'Failed to remove holding',
                'message': 'Please try again or contact support'
            }
    
    def get_portfolio_summary(self, user_id: str) -> Dict:
        """Get comprehensive portfolio summary with performance metrics"""
        try:
            holdings = PortfolioHolding.query.filter_by(user_id=user_id).all()
            
            if not holdings:
                return {
                    'success': True,
                    'total_holdings': 0,
                    'total_value': 0,
                    'total_cost_basis': 0,
                    'total_gain_loss': 0,
                    'gain_loss_percent': 0,
                    'holdings': [],
                    'sector_allocation': {},
                    'top_performers': [],
                    'bottom_performers': []
                }
            
            portfolio_data = []
            total_value = 0
            total_cost_basis = 0
            sector_allocation = {}
            
            for holding in holdings:
                stock_info = self.get_stock_info(holding.symbol)
                current_price = stock_info.get('current_price', holding.average_cost)
                sector = stock_info.get('sector', 'Unknown')
                
                market_value = holding.shares * current_price
                cost_basis = holding.shares * holding.average_cost
                gain_loss = market_value - cost_basis
                gain_loss_percent = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
                
                holding_data = {
                    'symbol': holding.symbol,
                    'company_name': stock_info.get('company_name', holding.symbol),
                    'shares': holding.shares,
                    'average_cost': holding.average_cost,
                    'current_price': current_price,
                    'market_value': market_value,
                    'cost_basis': cost_basis,
                    'unrealized_gain_loss': gain_loss,
                    'gain_loss_percent': gain_loss_percent,
                    'sector': sector,
                    'purchase_date': holding.purchase_date.isoformat() if holding.purchase_date else None,
                    'days_held': (datetime.now() - holding.purchase_date).days if holding.purchase_date else 0
                }
                
                portfolio_data.append(holding_data)
                total_value += market_value
                total_cost_basis += cost_basis
                
                # Sector allocation
                if sector in sector_allocation:
                    sector_allocation[sector] += market_value
                else:
                    sector_allocation[sector] = market_value
            
            # Calculate percentages for sector allocation
            for sector in sector_allocation:
                sector_allocation[sector] = {
                    'value': sector_allocation[sector],
                    'percentage': (sector_allocation[sector] / total_value) * 100 if total_value > 0 else 0
                }
            
            # Sort holdings by performance
            portfolio_data.sort(key=lambda x: x['gain_loss_percent'], reverse=True)
            top_performers = portfolio_data[:3]
            bottom_performers = portfolio_data[-3:] if len(portfolio_data) > 3 else []
            
            total_gain_loss = total_value - total_cost_basis
            total_gain_loss_percent = (total_gain_loss / total_cost_basis) * 100 if total_cost_basis > 0 else 0
            
            return {
                'success': True,
                'total_holdings': len(holdings),
                'total_value': total_value,
                'total_cost_basis': total_cost_basis,
                'total_gain_loss': total_gain_loss,
                'gain_loss_percent': total_gain_loss_percent,
                'holdings': portfolio_data,
                'sector_allocation': sector_allocation,
                'top_performers': top_performers,
                'bottom_performers': bottom_performers,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {
                'success': False,
                'error': 'Failed to get portfolio summary',
                'message': 'Please try again or contact support'
            }
    
    def get_portfolio_analytics(self, user_id: str) -> Dict:
        """Get advanced portfolio analytics and risk metrics"""
        try:
            summary = self.get_portfolio_summary(user_id)
            if not summary['success'] or summary['total_holdings'] == 0:
                return summary
            
            holdings = summary['holdings']
            symbols = [h['symbol'] for h in holdings]
            weights = [h['market_value'] / summary['total_value'] for h in holdings]
            
            # Get historical data for portfolio analysis
            returns_data = self.get_portfolio_returns(symbols, weights)
            
            # Calculate risk metrics
            portfolio_beta = self.calculate_portfolio_beta(symbols, weights)
            sharpe_ratio = self.calculate_sharpe_ratio(returns_data)
            volatility = np.std(returns_data) * np.sqrt(252) if len(returns_data) > 0 else 0
            
            # Diversification analysis
            diversification_score = self.calculate_diversification_score(summary['sector_allocation'])
            concentration_risk = max(weights) if weights else 0
            
            analytics = {
                'risk_metrics': {
                    'portfolio_beta': portfolio_beta,
                    'sharpe_ratio': sharpe_ratio,
                    'annual_volatility': volatility,
                    'concentration_risk': concentration_risk,
                    'diversification_score': diversification_score
                },
                'performance_metrics': {
                    'total_return': summary['gain_loss_percent'],
                    'best_performer': holdings[0] if holdings else None,
                    'worst_performer': holdings[-1] if holdings else None,
                    'win_rate': len([h for h in holdings if h['gain_loss_percent'] > 0]) / len(holdings) * 100 if holdings else 0
                },
                'rebalancing_suggestions': self.get_rebalancing_suggestions(holdings, summary['sector_allocation'])
            }
            
            return {
                'success': True,
                'portfolio_summary': summary,
                'analytics': analytics
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio analytics: {e}")
            return {
                'success': False,
                'error': 'Failed to get portfolio analytics',
                'message': 'Please try again or contact support'
            }
    
    def get_stock_info(self, symbol: str) -> Dict:
        """Get current stock information from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if hist.empty:
                return {}
            
            current_price = hist['Close'].iloc[-1]
            
            return {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'current_price': current_price,
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting stock info for {symbol}: {e}")
            return {}
    
    def get_portfolio_returns(self, symbols: List[str], weights: List[float], period: str = "1y") -> List[float]:
        """Calculate portfolio returns for risk analysis"""
        try:
            returns = []
            for symbol, weight in zip(symbols, weights):
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                if not hist.empty:
                    stock_returns = hist['Close'].pct_change().dropna()
                    weighted_returns = stock_returns * weight
                    returns.extend(weighted_returns.tolist())
            
            return returns
            
        except Exception as e:
            logger.error(f"Error calculating portfolio returns: {e}")
            return []
    
    def calculate_portfolio_beta(self, symbols: List[str], weights: List[float]) -> float:
        """Calculate portfolio beta relative to S&P 500"""
        try:
            # Get S&P 500 data
            spy = yf.Ticker("SPY")
            spy_hist = spy.history(period="1y")
            spy_returns = spy_hist['Close'].pct_change().dropna()
            
            portfolio_beta = 0
            for symbol, weight in zip(symbols, weights):
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1y")
                if not hist.empty:
                    stock_returns = hist['Close'].pct_change().dropna()
                    
                    # Align data
                    aligned_data = pd.concat([stock_returns, spy_returns], axis=1, join='inner')
                    if len(aligned_data) > 20:  # Need sufficient data
                        covariance = np.cov(aligned_data.iloc[:, 0], aligned_data.iloc[:, 1])[0, 1]
                        market_variance = np.var(aligned_data.iloc[:, 1])
                        stock_beta = covariance / market_variance if market_variance > 0 else 1.0
                        portfolio_beta += stock_beta * weight
            
            return portfolio_beta
            
        except Exception as e:
            logger.error(f"Error calculating portfolio beta: {e}")
            return 1.0  # Default beta
    
    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio for portfolio"""
        try:
            if not returns or len(returns) < 2:
                return 0
            
            returns_array = np.array(returns)
            avg_return = np.mean(returns_array) * 252  # Annualized
            volatility = np.std(returns_array) * np.sqrt(252)  # Annualized
            
            if volatility == 0:
                return 0
            
            sharpe = (avg_return - risk_free_rate) / volatility
            return sharpe
            
        except Exception as e:
            logger.error(f"Error calculating Sharpe ratio: {e}")
            return 0
    
    def calculate_diversification_score(self, sector_allocation: Dict) -> float:
        """Calculate diversification score based on sector allocation"""
        try:
            if not sector_allocation:
                return 0
            
            # Calculate Herfindahl-Hirschman Index (HHI)
            percentages = [sector['percentage'] / 100 for sector in sector_allocation.values()]
            hhi = sum(p**2 for p in percentages)
            
            # Convert to diversification score (0-100, higher is more diversified)
            max_hhi = 1.0  # Completely concentrated
            min_hhi = 1.0 / len(sector_allocation)  # Perfectly diversified
            
            if max_hhi == min_hhi:
                return 100
            
            diversification_score = ((max_hhi - hhi) / (max_hhi - min_hhi)) * 100
            return max(0, min(100, diversification_score))
            
        except Exception as e:
            logger.error(f"Error calculating diversification score: {e}")
            return 0
    
    def get_rebalancing_suggestions(self, holdings: List[Dict], sector_allocation: Dict) -> List[Dict]:
        """Generate portfolio rebalancing suggestions"""
        try:
            suggestions = []
            
            # Check for over-concentration
            for sector, data in sector_allocation.items():
                if data['percentage'] > 30:  # Over 30% in one sector
                    suggestions.append({
                        'type': 'reduce_concentration',
                        'message': f'Consider reducing {sector} allocation (currently {data["percentage"]:.1f}%)',
                        'priority': 'high' if data['percentage'] > 40 else 'medium'
                    })
            
            # Check for underperforming holdings
            poor_performers = [h for h in holdings if h['gain_loss_percent'] < -20]
            for holding in poor_performers:
                suggestions.append({
                    'type': 'review_holding',
                    'message': f'Review {holding["symbol"]} - down {abs(holding["gain_loss_percent"]):.1f}%',
                    'priority': 'medium'
                })
            
            # Check for missing diversification
            represented_sectors = set(sector_allocation.keys())
            target_sectors = {'Technology', 'Healthcare', 'Financials', 'Consumer Discretionary'}
            missing_sectors = target_sectors - represented_sectors
            
            if missing_sectors and len(holdings) < 10:
                suggestions.append({
                    'type': 'add_diversification',
                    'message': f'Consider adding exposure to: {", ".join(missing_sectors)}',
                    'priority': 'low'
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating rebalancing suggestions: {e}")
            return []