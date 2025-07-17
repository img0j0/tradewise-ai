"""
Social Trading and Copy Trading Module
Allows users to follow and copy successful traders
"""

from datetime import datetime, timedelta
from app import db
from models import User, Trade, Portfolio
from sqlalchemy import desc, func
import json
import logging

logger = logging.getLogger(__name__)

class SocialTradingManager:
    """Manages social trading features including trader rankings and copy trading"""
    
    def __init__(self):
        self.min_trades_for_ranking = 1  # Lowered for demonstration
        self.performance_window_days = 30
        
    def get_top_traders(self, limit=10, timeframe='month'):
        """Get top performing traders based on various metrics"""
        try:
            # Calculate timeframe
            if timeframe == 'week':
                start_date = datetime.utcnow() - timedelta(days=7)
            elif timeframe == 'month':
                start_date = datetime.utcnow() - timedelta(days=30)
            elif timeframe == 'year':
                start_date = datetime.utcnow() - timedelta(days=365)
            else:
                start_date = datetime.utcnow() - timedelta(days=30)
            
            # Get traders with recent trades
            trader_stats = db.session.query(
                Trade.user_id,
                User.username,
                func.count(Trade.id).label('total_trades'),
                func.avg(Trade.confidence_score).label('avg_confidence'),
                func.sum(
                    db.case(
                        (Trade.action == 'buy', Trade.quantity * Trade.price * -1),
                        (Trade.action == 'sell', Trade.quantity * Trade.price),
                        else_=0
                    )
                ).label('profit_loss')
            ).join(
                User, Trade.user_id == User.id
            ).filter(
                Trade.timestamp >= start_date
            ).group_by(
                Trade.user_id, User.username
            ).having(
                func.count(Trade.id) >= self.min_trades_for_ranking
            ).order_by(
                desc('profit_loss')
            ).limit(limit).all()
            
            # Calculate additional metrics for each trader
            top_traders = []
            for stat in trader_stats:
                trader_info = {
                    'user_id': stat.user_id,
                    'username': stat.username,
                    'total_trades': stat.total_trades,
                    'avg_confidence': float(stat.avg_confidence or 0),
                    'profit_loss': float(stat.profit_loss or 0),
                    'win_rate': self._calculate_win_rate(stat.user_id, start_date),
                    'risk_score': self._calculate_risk_score(stat.user_id),
                    'followers': self._get_follower_count(stat.user_id),
                    'ranking_score': 0
                }
                
                # Calculate composite ranking score
                trader_info['ranking_score'] = self._calculate_ranking_score(trader_info)
                top_traders.append(trader_info)
            
            # Sort by ranking score
            top_traders.sort(key=lambda x: x['ranking_score'], reverse=True)
            
            return top_traders
            
        except Exception as e:
            logger.error(f"Error getting top traders: {e}")
            return []
    
    def _calculate_win_rate(self, user_id, start_date):
        """Calculate win rate for a trader"""
        try:
            # Get all trades for the user in timeframe
            trades = Trade.query.filter(
                Trade.user_id == user_id,
                Trade.timestamp >= start_date
            ).all()
            
            if not trades:
                return 0
            
            # Group trades by symbol to calculate P&L
            symbol_trades = {}
            for trade in trades:
                if trade.symbol not in symbol_trades:
                    symbol_trades[trade.symbol] = []
                symbol_trades[trade.symbol].append(trade)
            
            wins = 0
            total_closed = 0
            
            for symbol, trades_list in symbol_trades.items():
                # Calculate if position was profitable
                buy_value = sum(t.quantity * t.price for t in trades_list if t.action == 'buy')
                sell_value = sum(t.quantity * t.price for t in trades_list if t.action == 'sell')
                
                if sell_value > 0:  # Position was closed
                    total_closed += 1
                    if sell_value > buy_value:
                        wins += 1
            
            return (wins / total_closed * 100) if total_closed > 0 else 0
            
        except Exception as e:
            logger.error(f"Error calculating win rate: {e}")
            return 0
    
    def _calculate_risk_score(self, user_id):
        """Calculate risk score based on trading patterns"""
        try:
            # Get recent trades
            recent_trades = Trade.query.filter(
                Trade.user_id == user_id,
                Trade.timestamp >= datetime.utcnow() - timedelta(days=30)
            ).all()
            
            if not recent_trades:
                return 50  # Default medium risk
            
            # Factors for risk calculation
            volatility_score = self._calculate_volatility_score(recent_trades)
            concentration_score = self._calculate_concentration_score(user_id)
            frequency_score = len(recent_trades) / 30  # Trades per day
            
            # Weighted risk score
            risk_score = (
                volatility_score * 0.4 +
                concentration_score * 0.4 +
                min(frequency_score * 10, 100) * 0.2
            )
            
            return min(max(risk_score, 0), 100)
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 50
    
    def _calculate_volatility_score(self, trades):
        """Calculate volatility score based on trade sizes"""
        if not trades:
            return 0
            
        trade_values = [t.quantity * t.price for t in trades]
        avg_value = sum(trade_values) / len(trade_values)
        
        if avg_value == 0:
            return 0
            
        variance = sum((v - avg_value) ** 2 for v in trade_values) / len(trade_values)
        std_dev = variance ** 0.5
        
        # Normalize to 0-100 scale
        coefficient_of_variation = (std_dev / avg_value) * 100
        return min(coefficient_of_variation, 100)
    
    def _calculate_concentration_score(self, user_id):
        """Calculate portfolio concentration risk"""
        try:
            portfolio = Portfolio.query.filter_by(user_id=user_id).all()
            
            if not portfolio:
                return 0
                
            total_value = sum(p.quantity * p.avg_price for p in portfolio)
            if total_value == 0:
                return 0
                
            # Calculate Herfindahl index
            concentration = sum(
                ((p.quantity * p.avg_price) / total_value) ** 2 
                for p in portfolio
            )
            
            # Convert to 0-100 scale (1 = maximum concentration)
            return concentration * 100
            
        except Exception as e:
            logger.error(f"Error calculating concentration score: {e}")
            return 50
    
    def _get_follower_count(self, user_id):
        """Get number of followers for a trader"""
        # Placeholder - would need a followers table in production
        return 0
    
    def _calculate_ranking_score(self, trader_info):
        """Calculate composite ranking score"""
        # Weighted scoring algorithm
        score = (
            trader_info['profit_loss'] * 0.3 +
            trader_info['win_rate'] * 0.25 +
            trader_info['avg_confidence'] * 0.15 +
            (100 - trader_info['risk_score']) * 0.15 +
            min(trader_info['total_trades'] / 10, 100) * 0.15
        )
        
        return score
    
    def get_trader_profile(self, user_id):
        """Get detailed profile for a specific trader"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            # Get recent performance
            recent_trades = Trade.query.filter(
                Trade.user_id == user_id,
                Trade.timestamp >= datetime.utcnow() - timedelta(days=30)
            ).order_by(desc(Trade.timestamp)).all()
            
            # Get portfolio composition
            portfolio = Portfolio.query.filter_by(user_id=user_id).all()
            
            # Calculate statistics
            profile = {
                'user_id': user_id,
                'username': user.username,
                'member_since': user.created_at.isoformat() if user.created_at else None,
                'total_trades': len(recent_trades),
                'portfolio_value': sum(p.quantity * p.avg_price for p in portfolio),
                'portfolio_composition': [
                    {
                        'symbol': p.symbol,
                        'quantity': p.quantity,
                        'value': p.quantity * p.avg_price,
                        'percentage': 0  # Will calculate below
                    } for p in portfolio
                ],
                'recent_trades': [
                    {
                        'symbol': t.symbol,
                        'action': t.action,
                        'quantity': t.quantity,
                        'price': t.price,
                        'confidence': t.confidence_score,
                        'timestamp': t.timestamp.isoformat()
                    } for t in recent_trades[:10]  # Last 10 trades
                ],
                'performance_metrics': {
                    'win_rate': self._calculate_win_rate(user_id, datetime.utcnow() - timedelta(days=30)),
                    'risk_score': self._calculate_risk_score(user_id),
                    'avg_confidence': sum(t.confidence_score for t in recent_trades) / len(recent_trades) if recent_trades else 0,
                    'best_trade': self._get_best_trade(user_id),
                    'worst_trade': self._get_worst_trade(user_id)
                }
            }
            
            # Calculate portfolio percentages
            total_value = profile['portfolio_value']
            if total_value > 0:
                for position in profile['portfolio_composition']:
                    position['percentage'] = (position['value'] / total_value) * 100
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting trader profile: {e}")
            return None
    
    def _get_best_trade(self, user_id):
        """Get the most profitable trade"""
        # Simplified - would need more complex P&L calculation in production
        best_sell = Trade.query.filter(
            Trade.user_id == user_id,
            Trade.action == 'sell'
        ).order_by(desc(Trade.quantity * Trade.price)).first()
        
        if best_sell:
            return {
                'symbol': best_sell.symbol,
                'profit': best_sell.quantity * best_sell.price,
                'date': best_sell.timestamp.isoformat()
            }
        return None
    
    def _get_worst_trade(self, user_id):
        """Get the least profitable trade"""
        # Simplified - would need more complex P&L calculation in production
        worst_sell = Trade.query.filter(
            Trade.user_id == user_id,
            Trade.action == 'sell'
        ).order_by(Trade.quantity * Trade.price).first()
        
        if worst_sell:
            return {
                'symbol': worst_sell.symbol,
                'loss': worst_sell.quantity * worst_sell.price,
                'date': worst_sell.timestamp.isoformat()
            }
        return None
    
    def simulate_copy_trade(self, follower_id, trader_id, amount=1000):
        """Simulate copying a trader's portfolio"""
        try:
            # Get trader's current portfolio
            trader_portfolio = Portfolio.query.filter_by(user_id=trader_id).all()
            
            if not trader_portfolio:
                return {'error': 'Trader has no active positions'}
            
            # Calculate total portfolio value
            total_value = sum(p.quantity * p.avg_price for p in trader_portfolio)
            
            if total_value == 0:
                return {'error': 'Invalid portfolio value'}
            
            # Calculate proportional allocation
            copy_trades = []
            for position in trader_portfolio:
                # Calculate percentage of portfolio
                percentage = (position.quantity * position.avg_price) / total_value
                
                # Calculate shares to buy with allocated amount
                allocated_amount = amount * percentage
                shares_to_buy = int(allocated_amount / position.avg_price)
                
                if shares_to_buy > 0:
                    copy_trades.append({
                        'symbol': position.symbol,
                        'shares': shares_to_buy,
                        'allocated_amount': shares_to_buy * position.avg_price,
                        'percentage': percentage * 100
                    })
            
            return {
                'trader_id': trader_id,
                'follower_id': follower_id,
                'total_amount': amount,
                'copy_trades': copy_trades,
                'unallocated': amount - sum(t['allocated_amount'] for t in copy_trades)
            }
            
        except Exception as e:
            logger.error(f"Error simulating copy trade: {e}")
            return {'error': str(e)}


class TradingSignalGenerator:
    """Generates trading signals for social trading features"""
    
    def __init__(self):
        self.confidence_threshold = 80
        
    def generate_signals(self, top_traders_data):
        """Generate trading signals based on top traders' activities"""
        signals = []
        
        for trader in top_traders_data:
            if trader['avg_confidence'] >= self.confidence_threshold:
                signal = {
                    'trader_id': trader['user_id'],
                    'trader_name': trader['username'],
                    'signal_type': 'follow',
                    'strength': self._calculate_signal_strength(trader),
                    'reason': self._generate_signal_reason(trader),
                    'risk_level': self._categorize_risk(trader['risk_score'])
                }
                signals.append(signal)
        
        return sorted(signals, key=lambda x: x['strength'], reverse=True)
    
    def _calculate_signal_strength(self, trader):
        """Calculate signal strength (0-100)"""
        strength = (
            min(trader['win_rate'], 100) * 0.3 +
            trader['avg_confidence'] * 0.3 +
            (100 - trader['risk_score']) * 0.2 +
            min(trader['profit_loss'] / 1000, 100) * 0.2
        )
        return min(max(strength, 0), 100)
    
    def _generate_signal_reason(self, trader):
        """Generate human-readable reason for signal"""
        reasons = []
        
        if trader['win_rate'] > 70:
            reasons.append(f"{trader['win_rate']:.0f}% win rate")
        if trader['avg_confidence'] > 85:
            reasons.append(f"{trader['avg_confidence']:.0f}% avg confidence")
        if trader['profit_loss'] > 1000:
            reasons.append(f"${trader['profit_loss']:.0f} profit")
        if trader['risk_score'] < 30:
            reasons.append("Low risk profile")
            
        return " • ".join(reasons) if reasons else "Strong overall performance"
    
    def _categorize_risk(self, risk_score):
        """Categorize risk level"""
        if risk_score < 30:
            return 'low'
        elif risk_score < 70:
            return 'medium'
        else:
            return 'high'