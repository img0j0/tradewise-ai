"""
Gamification and Achievement System
Make trading more engaging with achievements, leaderboards, and rewards
"""

from datetime import datetime, timedelta
from app import db
from models import User, Trade, Portfolio
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

class AchievementSystem:
    """Manages achievements and gamification features"""
    
    def __init__(self):
        self.achievements = {
            # Trading Milestones
            'first_trade': {
                'name': 'First Steps',
                'description': 'Complete your first trade',
                'icon': 'fa-baby-carriage',
                'points': 10,
                'criteria': lambda user_id: self._check_trade_count(user_id, 1)
            },
            'ten_trades': {
                'name': 'Active Trader',
                'description': 'Complete 10 trades',
                'icon': 'fa-chart-line',
                'points': 25,
                'criteria': lambda user_id: self._check_trade_count(user_id, 10)
            },
            'hundred_trades': {
                'name': 'Market Veteran',
                'description': 'Complete 100 trades',
                'icon': 'fa-crown',
                'points': 100,
                'criteria': lambda user_id: self._check_trade_count(user_id, 100)
            },
            
            # Profit Achievements
            'first_profit': {
                'name': 'In the Green',
                'description': 'Make your first profitable trade',
                'icon': 'fa-dollar-sign',
                'points': 15,
                'criteria': lambda user_id: self._check_profitable_trades(user_id, 1)
            },
            'streak_5': {
                'name': 'Hot Streak',
                'description': '5 profitable trades in a row',
                'icon': 'fa-fire',
                'points': 50,
                'criteria': lambda user_id: self._check_profit_streak(user_id, 5)
            },
            'profit_1k': {
                'name': 'Four Figures',
                'description': 'Earn $1,000 in total profits',
                'icon': 'fa-money-bill-wave',
                'points': 75,
                'criteria': lambda user_id: self._check_total_profit(user_id, 1000)
            },
            
            # Portfolio Achievements
            'diversified': {
                'name': 'Diversified',
                'description': 'Hold 5 different stocks in your portfolio',
                'icon': 'fa-briefcase',
                'points': 30,
                'criteria': lambda user_id: self._check_portfolio_diversity(user_id, 5)
            },
            'blue_chip': {
                'name': 'Blue Chip Investor',
                'description': 'Own shares in 3 major tech companies',
                'icon': 'fa-building',
                'points': 40,
                'criteria': lambda user_id: self._check_blue_chip_holdings(user_id)
            },
            
            # AI Usage Achievements
            'ai_follower': {
                'name': 'AI Believer',
                'description': 'Follow 10 AI recommendations',
                'icon': 'fa-robot',
                'points': 35,
                'criteria': lambda user_id: self._check_ai_trades(user_id, 10)
            },
            'ai_success': {
                'name': 'Smart Investor',
                'description': 'Profit from 5 AI-recommended trades',
                'icon': 'fa-brain',
                'points': 60,
                'criteria': lambda user_id: self._check_ai_profit_trades(user_id, 5)
            },
            
            # Time-based Achievements
            'early_bird': {
                'name': 'Early Bird',
                'description': 'Make a trade before 10 AM',
                'icon': 'fa-sun',
                'points': 20,
                'criteria': lambda user_id: self._check_early_trades(user_id)
            },
            'night_owl': {
                'name': 'Night Owl',
                'description': 'Make a trade after 8 PM',
                'icon': 'fa-moon',
                'points': 20,
                'criteria': lambda user_id: self._check_late_trades(user_id)
            },
            'weekend_warrior': {
                'name': 'Weekend Warrior',
                'description': 'Plan trades on the weekend',
                'icon': 'fa-calendar-week',
                'points': 25,
                'criteria': lambda user_id: self._check_weekend_activity(user_id)
            },
            
            # Learning Achievements
            'quick_learner': {
                'name': 'Quick Learner',
                'description': 'Use the AI assistant 20 times',
                'icon': 'fa-graduation-cap',
                'points': 30,
                'criteria': lambda user_id: self._check_ai_assistant_usage(user_id, 20)
            }
        }
        
        self.levels = {
            1: {'name': 'Beginner', 'min_points': 0, 'perks': ['Basic trading features']},
            2: {'name': 'Amateur', 'min_points': 100, 'perks': ['Extended market hours']},
            3: {'name': 'Trader', 'min_points': 250, 'perks': ['Advanced analytics']},
            4: {'name': 'Pro Trader', 'min_points': 500, 'perks': ['Priority AI insights']},
            5: {'name': 'Expert', 'min_points': 1000, 'perks': ['Copy trading access']},
            6: {'name': 'Master', 'min_points': 2000, 'perks': ['Custom AI models']},
            7: {'name': 'Legend', 'min_points': 5000, 'perks': ['VIP support']}
        }
    
    def check_achievements(self, user_id):
        """Check and award new achievements for a user"""
        try:
            earned_achievements = []
            user_achievements = self._get_user_achievements(user_id)
            
            for achievement_id, achievement in self.achievements.items():
                if achievement_id not in user_achievements:
                    if achievement['criteria'](user_id):
                        # Award achievement
                        self._award_achievement(user_id, achievement_id)
                        earned_achievements.append({
                            'id': achievement_id,
                            'name': achievement['name'],
                            'description': achievement['description'],
                            'points': achievement['points'],
                            'icon': achievement['icon']
                        })
            
            return earned_achievements
            
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            return []
    
    def get_user_stats(self, user_id):
        """Get comprehensive gamification stats for a user"""
        try:
            achievements = self._get_user_achievements(user_id)
            total_points = sum(self.achievements[a]['points'] for a in achievements if a in self.achievements)
            current_level = self._calculate_level(total_points)
            next_level = current_level + 1 if current_level < len(self.levels) else current_level
            
            stats = {
                'total_points': total_points,
                'current_level': current_level,
                'level_name': self.levels[current_level]['name'],
                'level_perks': self.levels[current_level]['perks'],
                'next_level_points': self.levels[next_level]['min_points'] if next_level != current_level else None,
                'progress_to_next': self._calculate_progress(total_points, current_level),
                'achievements_earned': len(achievements),
                'achievements_total': len(self.achievements),
                'recent_achievements': self._get_recent_achievements(user_id, 5),
                'achievement_list': [
                    {
                        'id': aid,
                        'name': self.achievements[aid]['name'],
                        'description': self.achievements[aid]['description'],
                        'points': self.achievements[aid]['points'],
                        'icon': self.achievements[aid]['icon'],
                        'earned': aid in achievements
                    } for aid in self.achievements
                ]
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return None
    
    def get_leaderboard(self, timeframe='all', limit=10):
        """Get leaderboard of top traders"""
        try:
            # Get all users with their points
            leaderboard_data = []
            
            users = User.query.all()
            for user in users:
                achievements = self._get_user_achievements(user.id)
                total_points = sum(self.achievements[a]['points'] for a in achievements if a in self.achievements)
                
                if total_points > 0:
                    leaderboard_data.append({
                        'user_id': user.id,
                        'username': user.username,
                        'points': total_points,
                        'level': self._calculate_level(total_points),
                        'level_name': self.levels[self._calculate_level(total_points)]['name'],
                        'achievements': len(achievements),
                        'trades': Trade.query.filter_by(user_id=user.id).count()
                    })
            
            # Sort by points
            leaderboard_data.sort(key=lambda x: x['points'], reverse=True)
            
            return leaderboard_data[:limit]
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    # Helper methods for achievement criteria
    def _check_trade_count(self, user_id, required_count):
        """Check if user has made required number of trades"""
        count = Trade.query.filter_by(user_id=user_id).count()
        return count >= required_count
    
    def _check_profitable_trades(self, user_id, required_count):
        """Check if user has made required number of profitable trades"""
        # Simplified check - in production would need proper P&L calculation
        sell_trades = Trade.query.filter_by(user_id=user_id, action='sell').count()
        return sell_trades >= required_count
    
    def _check_profit_streak(self, user_id, required_streak):
        """Check if user has a profit streak"""
        # Simplified - would need proper implementation
        return False
    
    def _check_total_profit(self, user_id, required_profit):
        """Check if user has achieved required total profit"""
        # Simplified - would need proper P&L calculation
        sells = db.session.query(func.sum(Trade.quantity * Trade.price)).filter_by(
            user_id=user_id, action='sell'
        ).scalar() or 0
        buys = db.session.query(func.sum(Trade.quantity * Trade.price)).filter_by(
            user_id=user_id, action='buy'
        ).scalar() or 0
        return (sells - buys) >= required_profit
    
    def _check_portfolio_diversity(self, user_id, required_stocks):
        """Check if user has required portfolio diversity"""
        unique_stocks = Portfolio.query.filter_by(user_id=user_id).count()
        return unique_stocks >= required_stocks
    
    def _check_blue_chip_holdings(self, user_id):
        """Check if user holds blue chip stocks"""
        blue_chips = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']
        holdings = Portfolio.query.filter_by(user_id=user_id).all()
        held_blue_chips = sum(1 for h in holdings if h.symbol in blue_chips)
        return held_blue_chips >= 3
    
    def _check_ai_trades(self, user_id, required_count):
        """Check if user has followed AI recommendations"""
        ai_trades = Trade.query.filter(
            Trade.user_id == user_id,
            Trade.confidence_score >= 80
        ).count()
        return ai_trades >= required_count
    
    def _check_ai_profit_trades(self, user_id, required_count):
        """Check profitable AI-recommended trades"""
        # Simplified - would need proper implementation
        return False
    
    def _check_early_trades(self, user_id):
        """Check if user made early morning trades"""
        early_trades = Trade.query.filter(
            Trade.user_id == user_id,
            func.extract('hour', Trade.timestamp) < 10
        ).count()
        return early_trades > 0
    
    def _check_late_trades(self, user_id):
        """Check if user made late evening trades"""
        late_trades = Trade.query.filter(
            Trade.user_id == user_id,
            func.extract('hour', Trade.timestamp) >= 20
        ).count()
        return late_trades > 0
    
    def _check_weekend_activity(self, user_id):
        """Check if user was active on weekends"""
        # Simplified check
        return True
    
    def _check_ai_assistant_usage(self, user_id, required_count):
        """Check AI assistant usage"""
        # Would need to track AI assistant interactions
        return False
    
    def _get_user_achievements(self, user_id):
        """Get list of achievements earned by user"""
        # In production, this would query an achievements table
        # For now, return empty list
        return []
    
    def _award_achievement(self, user_id, achievement_id):
        """Award achievement to user"""
        # In production, this would insert into achievements table
        logger.info(f"Awarded achievement {achievement_id} to user {user_id}")
    
    def _calculate_level(self, points):
        """Calculate user level based on points"""
        for level in sorted(self.levels.keys(), reverse=True):
            if points >= self.levels[level]['min_points']:
                return level
        return 1
    
    def _calculate_progress(self, points, current_level):
        """Calculate progress to next level"""
        if current_level >= len(self.levels):
            return 100
            
        current_min = self.levels[current_level]['min_points']
        next_min = self.levels[current_level + 1]['min_points']
        
        progress = ((points - current_min) / (next_min - current_min)) * 100
        return min(max(progress, 0), 100)
    
    def _get_recent_achievements(self, user_id, limit):
        """Get recently earned achievements"""
        # In production, would query achievements table with timestamps
        return []


class ChallengeSystem:
    """Manages trading challenges and competitions"""
    
    def __init__(self):
        self.active_challenges = {
            'weekly_trader': {
                'name': 'Weekly Trading Champion',
                'description': 'Most profitable trader this week',
                'reward_points': 100,
                'timeframe': 'week'
            },
            'risk_master': {
                'name': 'Risk Management Master',
                'description': 'Best risk-adjusted returns this month',
                'reward_points': 150,
                'timeframe': 'month'
            },
            'ai_challenger': {
                'name': 'AI vs Human Challenge',
                'description': 'Beat the AI recommendations this week',
                'reward_points': 200,
                'timeframe': 'week'
            }
        }
    
    def get_active_challenges(self):
        """Get list of active challenges"""
        return [
            {
                'id': cid,
                'name': challenge['name'],
                'description': challenge['description'],
                'reward': challenge['reward_points'],
                'timeframe': challenge['timeframe'],
                'participants': self._get_participant_count(cid),
                'ends_in': self._get_time_remaining(challenge['timeframe'])
            }
            for cid, challenge in self.active_challenges.items()
        ]
    
    def _get_participant_count(self, challenge_id):
        """Get number of participants in a challenge"""
        # Simplified - would query challenge participants table
        return 42
    
    def _get_time_remaining(self, timeframe):
        """Calculate time remaining in challenge"""
        now = datetime.utcnow()
        if timeframe == 'week':
            days_until_sunday = (6 - now.weekday()) % 7
            return f"{days_until_sunday} days"
        elif timeframe == 'month':
            next_month = now.replace(day=28) + timedelta(days=4)
            last_day = next_month - timedelta(days=next_month.day)
            days_remaining = (last_day - now).days
            return f"{days_remaining} days"
        return "Unknown"