"""
Social Trading Module - Handles top traders, achievements, and challenges
"""
import random
from datetime import datetime, timedelta

class SocialTradingEngine:
    def __init__(self):
        self.achievements = [
            {
                'id': 'first_trade',
                'name': 'First Trade',
                'description': 'Complete your first trade',
                'icon': 'fas fa-play',
                'progress': 100,
                'completed': True,
                'reward': 100
            },
            {
                'id': 'profit_milestone',
                'name': 'Profit Master',
                'description': 'Earn $1,000 in profits',
                'icon': 'fas fa-chart-line',
                'progress': 75,
                'completed': False,
                'reward': 500
            },
            {
                'id': 'diverse_portfolio',
                'name': 'Diversifier',
                'description': 'Own 10 different stocks',
                'icon': 'fas fa-layer-group',
                'progress': 60,
                'completed': False,
                'reward': 300
            },
            {
                'id': 'winning_streak',
                'name': 'Winning Streak',
                'description': '5 profitable trades in a row',
                'icon': 'fas fa-fire',
                'progress': 40,
                'completed': False,
                'reward': 750
            }
        ]
        
        self.top_traders = [
            {
                'rank': 1,
                'username': 'ProTrader88',
                'return_percentage': 156.8,
                'trades': 234,
                'win_rate': 78.5,
                'followers': 1289,
                'avatar': 'fas fa-user-astronaut'
            },
            {
                'rank': 2,
                'username': 'InvestorQueen',
                'return_percentage': 142.3,
                'trades': 189,
                'win_rate': 82.1,
                'followers': 987,
                'avatar': 'fas fa-user-ninja'
            },
            {
                'rank': 3,
                'username': 'BullishBear',
                'return_percentage': 128.9,
                'trades': 312,
                'win_rate': 71.2,
                'followers': 756,
                'avatar': 'fas fa-user-tie'
            },
            {
                'rank': 4,
                'username': 'CryptoKing',
                'return_percentage': 119.4,
                'trades': 145,
                'win_rate': 69.8,
                'followers': 623,
                'avatar': 'fas fa-user-crown'
            },
            {
                'rank': 5,
                'username': 'SmartMoney',
                'return_percentage': 108.7,
                'trades': 278,
                'win_rate': 73.5,
                'followers': 534,
                'avatar': 'fas fa-user-graduate'
            }
        ]
        
        self.active_challenges = [
            {
                'id': 'weekly_profit',
                'name': 'Weekly Profit Challenge',
                'description': 'Achieve 5% portfolio growth this week',
                'end_date': (datetime.now() + timedelta(days=3)).isoformat(),
                'participants': 3421,
                'reward': '$100 bonus',
                'progress': 68,
                'target': 5.0,
                'current': 3.4,
                'icon': 'fas fa-trophy'
            },
            {
                'id': 'tech_trader',
                'name': 'Tech Stock Master',
                'description': 'Trade 10 tech stocks profitably',
                'end_date': (datetime.now() + timedelta(days=7)).isoformat(),
                'participants': 2156,
                'reward': 'Exclusive badge',
                'progress': 30,
                'target': 10,
                'current': 3,
                'icon': 'fas fa-microchip'
            },
            {
                'id': 'risk_manager',
                'name': 'Risk Management Pro',
                'description': 'Keep losses under 2% for the month',
                'end_date': (datetime.now() + timedelta(days=14)).isoformat(),
                'participants': 1879,
                'reward': 'AI Premium Access',
                'progress': 85,
                'target': 2.0,
                'current': 0.3,
                'icon': 'fas fa-shield-alt'
            }
        ]
    
    def get_user_achievements(self, user_id=None):
        """Get user's achievements with progress"""
        return {
            'achievements': self.achievements,
            'total_points': sum(a['reward'] for a in self.achievements if a['completed']),
            'level': self._calculate_level(sum(a['reward'] for a in self.achievements if a['completed']))
        }
    
    def get_top_traders(self, limit=5):
        """Get top performing traders"""
        return {
            'traders': self.top_traders[:limit],
            'last_updated': datetime.now().isoformat()
        }
    
    def get_active_challenges(self, user_id=None):
        """Get active trading challenges"""
        return {
            'challenges': self.active_challenges,
            'user_rank': random.randint(50, 500),  # Mock user rank
            'total_participants': sum(c['participants'] for c in self.active_challenges)
        }
    
    def get_leaderboard(self, timeframe='week'):
        """Get overall leaderboard"""
        leaderboard = []
        for i in range(10):
            leaderboard.append({
                'rank': i + 1,
                'username': f'Trader{random.randint(100, 999)}',
                'return_percentage': round(random.uniform(50, 200), 1),
                'trades': random.randint(50, 500),
                'points': random.randint(1000, 10000)
            })
        
        return {
            'timeframe': timeframe,
            'leaderboard': leaderboard,
            'user_rank': random.randint(15, 100),
            'last_updated': datetime.now().isoformat()
        }
    
    def follow_trader(self, user_id, trader_id):
        """Follow a top trader"""
        return {
            'success': True,
            'message': 'Successfully followed trader',
            'following_count': random.randint(5, 20)
        }
    
    def join_challenge(self, user_id, challenge_id):
        """Join a trading challenge"""
        challenge = next((c for c in self.active_challenges if c['id'] == challenge_id), None)
        if challenge:
            return {
                'success': True,
                'message': f'Successfully joined {challenge["name"]}',
                'challenge': challenge
            }
        return {
            'success': False,
            'message': 'Challenge not found'
        }
    
    def _calculate_level(self, points):
        """Calculate user level based on points"""
        if points < 500:
            return 'Bronze'
        elif points < 1500:
            return 'Silver'
        elif points < 3000:
            return 'Gold'
        elif points < 5000:
            return 'Platinum'
        else:
            return 'Diamond'