"""
Gamification module for trading analytics platform
Handles achievements, user stats, and challenges
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from sqlalchemy import func

from models import db, Trade, User

logger = logging.getLogger(__name__)


class GamificationEngine:
    """Engine for handling achievements and gamification features"""
    
    def __init__(self):
        self.achievement_definitions = self._initialize_achievements()
        self.level_thresholds = self._initialize_levels()
    
    def _initialize_achievements(self) -> List[Dict[str, Any]]:
        """Initialize achievement definitions"""
        return [
            {
                'id': 'first_trade',
                'name': 'First Trade',
                'description': 'Complete your first trade',
                'icon': 'fas fa-rocket',
                'points': 50,
                'criteria': {'trades_count': 1}
            },
            {
                'id': 'profitable_week',
                'name': 'Profitable Week',
                'description': 'Maintain a profit for 7 consecutive days',
                'icon': 'fas fa-chart-line',
                'points': 100,
                'criteria': {'profitable_days': 7}
            },
            {
                'id': 'risk_manager',
                'name': 'Risk Manager',
                'description': 'Complete 10 trades with stop-loss',
                'icon': 'fas fa-shield-alt',
                'points': 150,
                'criteria': {'stop_loss_trades': 10}
            },
            {
                'id': 'diversified',
                'name': 'Diversified Portfolio',
                'description': 'Hold positions in 5+ different stocks',
                'icon': 'fas fa-pie-chart',
                'points': 200,
                'criteria': {'unique_stocks': 5}
            },
            {
                'id': 'winning_streak',
                'name': 'Winning Streak',
                'description': '5 profitable trades in a row',
                'icon': 'fas fa-fire',
                'points': 300,
                'criteria': {'winning_streak': 5}
            }
        ]
    
    def _initialize_levels(self) -> List[Dict[str, Any]]:
        """Initialize level thresholds"""
        return [
            {'level': 1, 'name': 'Beginner Trader', 'points_required': 0},
            {'level': 2, 'name': 'Amateur Investor', 'points_required': 100},
            {'level': 3, 'name': 'Market Enthusiast', 'points_required': 300},
            {'level': 4, 'name': 'Seasoned Trader', 'points_required': 600},
            {'level': 5, 'name': 'Investment Pro', 'points_required': 1000},
            {'level': 6, 'name': 'Market Expert', 'points_required': 1600},
            {'level': 7, 'name': 'Trading Master', 'points_required': 2500},
            {'level': 8, 'name': 'Wall Street Wolf', 'points_required': 4000}
        ]
    
    def get_user_achievements(self, user_id: str) -> Dict[str, Any]:
        """Get user achievements and stats"""
        try:
            # Get user stats
            user_stats = self._calculate_user_stats(user_id)
            
            # Get completed achievements
            completed = self._get_completed_achievements(user_id, user_stats)
            
            # Calculate level and progress
            level_info = self._calculate_level(user_stats['total_points'])
            
            # Get achievement list with progress
            achievements = []
            for achievement in self.achievement_definitions:
                progress = self._calculate_achievement_progress(
                    achievement, user_stats
                )
                achievements.append({
                    'id': achievement['id'],
                    'name': achievement['name'],
                    'description': achievement['description'],
                    'icon': achievement['icon'],
                    'points': achievement['points'],
                    'completed': achievement['id'] in completed,
                    'progress': progress
                })
            
            return {
                'achievements': achievements,
                'user_stats': {
                    'total_points': user_stats['total_points'],
                    'current_level': level_info['current_level'],
                    'level_name': level_info['level_name'],
                    'progress_to_next': level_info['progress_to_next'],
                    'achievements_earned': len(completed),
                    'achievements_total': len(self.achievement_definitions),
                    'trades_count': user_stats['trades_count'],
                    'win_rate': user_stats['win_rate']
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user achievements: {e}")
            return {
                'achievements': [],
                'user_stats': {
                    'total_points': 0,
                    'current_level': 1,
                    'level_name': 'Beginner Trader',
                    'progress_to_next': 0,
                    'achievements_earned': 0,
                    'achievements_total': len(self.achievement_definitions)
                }
            }
    
    def _calculate_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Calculate user trading statistics"""
        trades = Trade.query.filter_by(user_id=user_id).all()
        
        if not trades:
            return {
                'trades_count': 0,
                'win_rate': 0,
                'total_points': 0,
                'profitable_days': 0,
                'stop_loss_trades': 0,
                'unique_stocks': 0,
                'winning_streak': 0
            }
        
        # Calculate basic stats
        trades_count = len(trades)
        profitable_trades = sum(1 for t in trades if (t.profit_loss or 0) > 0)
        win_rate = (profitable_trades / trades_count * 100) if trades_count > 0 else 0
        
        # Calculate unique stocks
        unique_stocks = len(set(t.symbol for t in trades))
        
        # Calculate winning streak (simplified)
        max_streak = 0
        current_streak = 0
        for trade in sorted(trades, key=lambda x: x.executed_at):
            if (trade.profit_loss or 0) > 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        # Calculate total points (based on completed achievements)
        total_points = self._calculate_total_points(user_id)
        
        return {
            'trades_count': trades_count,
            'win_rate': win_rate,
            'total_points': total_points,
            'profitable_days': min(7, trades_count),  # Simplified
            'stop_loss_trades': min(10, trades_count // 2),  # Simplified
            'unique_stocks': unique_stocks,
            'winning_streak': max_streak
        }
    
    def _get_completed_achievements(self, user_id: str, user_stats: Dict) -> List[str]:
        """Determine which achievements are completed"""
        completed = []
        
        for achievement in self.achievement_definitions:
            if self._is_achievement_completed(achievement, user_stats):
                completed.append(achievement['id'])
        
        return completed
    
    def _is_achievement_completed(self, achievement: Dict, user_stats: Dict) -> bool:
        """Check if an achievement is completed based on criteria"""
        criteria = achievement['criteria']
        
        for key, required_value in criteria.items():
            if user_stats.get(key, 0) < required_value:
                return False
        
        return True
    
    def _calculate_achievement_progress(self, achievement: Dict, user_stats: Dict) -> float:
        """Calculate progress percentage for an achievement"""
        criteria = achievement['criteria']
        progress_values = []
        
        for key, required_value in criteria.items():
            current_value = user_stats.get(key, 0)
            progress = min(100, (current_value / required_value) * 100)
            progress_values.append(progress)
        
        return sum(progress_values) / len(progress_values) if progress_values else 0
    
    def _calculate_total_points(self, user_id: str) -> int:
        """Calculate total points earned by user"""
        # Simplified calculation based on trades
        trades_count = Trade.query.filter_by(user_id=user_id).count()
        base_points = trades_count * 10
        
        # Add bonus for achievements
        bonus_points = min(500, trades_count * 20)
        
        return base_points + bonus_points
    
    def _calculate_level(self, total_points: int) -> Dict[str, Any]:
        """Calculate user level based on total points"""
        current_level = None
        next_level = None
        
        for i, level in enumerate(self.level_thresholds):
            if total_points >= level['points_required']:
                current_level = level
                if i + 1 < len(self.level_thresholds):
                    next_level = self.level_thresholds[i + 1]
            else:
                if current_level is None:
                    current_level = self.level_thresholds[0]
                next_level = level
                break
        
        if current_level is None:
            current_level = self.level_thresholds[-1]
        
        # Calculate progress to next level
        if next_level:
            points_in_level = next_level['points_required'] - current_level['points_required']
            points_earned = total_points - current_level['points_required']
            progress = (points_earned / points_in_level) * 100
        else:
            progress = 100  # Max level reached
        
        return {
            'current_level': current_level['level'],
            'level_name': current_level['name'],
            'progress_to_next': min(100, max(0, progress))
        }
    
    def get_leaderboard(self, timeframe: str = 'all') -> Dict[str, Any]:
        """Get trading leaderboard"""
        try:
            # Get time filter
            if timeframe == 'week':
                date_filter = datetime.now() - timedelta(days=7)
            elif timeframe == 'month':
                date_filter = datetime.now() - timedelta(days=30)
            else:
                date_filter = None
            
            # Query for top traders
            query = db.session.query(
                Trade.user_id,
                func.count(Trade.id).label('trades_count'),
                func.sum(Trade.profit_loss).label('total_profit')
            ).group_by(Trade.user_id)
            
            if date_filter:
                query = query.filter(Trade.executed_at >= date_filter)
            
            results = query.all()
            
            # Build leaderboard
            traders = []
            for rank, (user_id, trades_count, total_profit) in enumerate(results[:10], 1):
                # Get username
                user = User.query.get(user_id)
                username = user.username if user else f"Trader{user_id[:4]}"
                
                # Calculate return percentage (simplified)
                return_pct = (total_profit / 10000 * 100) if total_profit else 0
                
                traders.append({
                    'rank': rank,
                    'user_id': user_id,
                    'username': username,
                    'trades': trades_count,
                    'return_percentage': float(return_pct),
                    'total_profit': float(total_profit or 0)
                })
            
            return {'traders': traders}
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return {'traders': []}
    
    def get_active_challenges(self, user_id: str) -> Dict[str, Any]:
        """Get active trading challenges"""
        try:
            # Define sample challenges
            challenges = [
                {
                    'id': 'volume_trader',
                    'name': 'Volume Trader',
                    'description': 'Complete 20 trades this week',
                    'icon': 'fas fa-chart-bar',
                    'reward': '200 XP + Badge',
                    'participants': 142,
                    'progress': 35
                },
                {
                    'id': 'profit_hunter',
                    'name': 'Profit Hunter',
                    'description': 'Achieve 10% portfolio return',
                    'icon': 'fas fa-trophy',
                    'reward': '500 XP + Title',
                    'participants': 89,
                    'progress': 68
                },
                {
                    'id': 'risk_taker',
                    'name': 'Calculated Risk',
                    'description': 'Use leverage wisely in 5 trades',
                    'icon': 'fas fa-dice',
                    'reward': '300 XP + Bonus',
                    'participants': 215,
                    'progress': 20
                }
            ]
            
            # Add user-specific progress (simplified)
            trades_count = Trade.query.filter_by(user_id=user_id).count()
            for challenge in challenges:
                if challenge['id'] == 'volume_trader':
                    challenge['progress'] = min(100, (trades_count / 20) * 100)
            
            return {'challenges': challenges}
            
        except Exception as e:
            logger.error(f"Error getting challenges: {e}")
            return {'challenges': []}


# Initialize gamification engine
gamification_engine = GamificationEngine()