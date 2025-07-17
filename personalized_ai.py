import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sqlalchemy import func
from models import db, Trade, Portfolio, User, UserAccount
from ai_insights import AIInsightsEngine
import pickle
import os

logger = logging.getLogger(__name__)

class PersonalizedAIAssistant:
    """AI Assistant that learns from individual user trading patterns and preferences"""
    
    def __init__(self):
        self.user_models = {}  # Store personalized models for each user
        self.user_preferences = {}  # Store learned preferences
        self.models_dir = 'ai_models/personalized'
        os.makedirs(self.models_dir, exist_ok=True)
        
    def learn_from_user_trades(self, user_id):
        """Analyze user's trading history to learn their patterns"""
        try:
            # Get user's trading history
            trades = Trade.query.filter_by(user_id=user_id).order_by(Trade.created_at.desc()).all()
            
            if len(trades) < 5:
                return {
                    'status': 'insufficient_data',
                    'message': 'Need at least 5 trades to learn your pattern'
                }
            
            # Analyze trading patterns
            patterns = {
                'preferred_sectors': defaultdict(int),
                'avg_holding_period': 0,
                'risk_tolerance': 'moderate',
                'preferred_trade_size': 0,
                'profit_loss_ratio': 0,
                'trading_frequency': 'moderate',
                'favorite_stocks': defaultdict(int),
                'best_performing_trades': [],
                'worst_performing_trades': []
            }
            
            total_profit = 0
            total_loss = 0
            holding_periods = []
            trade_sizes = []
            
            for trade in trades:
                # Track favorite stocks
                patterns['favorite_stocks'][trade.symbol] += 1
                
                # Track trade sizes
                trade_value = trade.quantity * trade.price
                trade_sizes.append(trade_value)
                
                # Calculate profit/loss (simplified)
                if trade.action == 'sell':
                    # Find corresponding buy trade
                    buy_trade = Trade.query.filter_by(
                        user_id=user_id,
                        symbol=trade.symbol,
                        action='buy'
                    ).filter(Trade.created_at < trade.created_at).first()
                    
                    if buy_trade:
                        profit = (trade.price - buy_trade.price) * trade.quantity
                        if profit > 0:
                            total_profit += profit
                            patterns['best_performing_trades'].append({
                                'symbol': trade.symbol,
                                'profit': profit,
                                'return_pct': ((trade.price - buy_trade.price) / buy_trade.price) * 100
                            })
                        else:
                            total_loss += abs(profit)
                            patterns['worst_performing_trades'].append({
                                'symbol': trade.symbol,
                                'loss': abs(profit),
                                'return_pct': ((trade.price - buy_trade.price) / buy_trade.price) * 100
                            })
                        
                        # Calculate holding period
                        holding_period = (trade.created_at - buy_trade.created_at).days
                        holding_periods.append(holding_period)
            
            # Calculate averages and ratios
            if trade_sizes:
                patterns['preferred_trade_size'] = np.mean(trade_sizes)
            
            if holding_periods:
                patterns['avg_holding_period'] = np.mean(holding_periods)
            
            if total_loss > 0:
                patterns['profit_loss_ratio'] = total_profit / total_loss
            else:
                patterns['profit_loss_ratio'] = float('inf') if total_profit > 0 else 0
            
            # Determine risk tolerance based on volatility of trades
            if len(trades) > 10:
                trade_volatility = np.std([t.price for t in trades]) / np.mean([t.price for t in trades])
                if trade_volatility < 0.1:
                    patterns['risk_tolerance'] = 'conservative'
                elif trade_volatility < 0.2:
                    patterns['risk_tolerance'] = 'moderate'
                else:
                    patterns['risk_tolerance'] = 'aggressive'
            
            # Determine trading frequency
            if len(trades) > 20:
                days_active = (trades[0].created_at - trades[-1].created_at).days
                trades_per_week = len(trades) / (days_active / 7) if days_active > 0 else 0
                if trades_per_week < 2:
                    patterns['trading_frequency'] = 'low'
                elif trades_per_week < 5:
                    patterns['trading_frequency'] = 'moderate'
                else:
                    patterns['trading_frequency'] = 'high'
            
            # Sort and limit results
            patterns['favorite_stocks'] = dict(sorted(
                patterns['favorite_stocks'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5])
            
            patterns['best_performing_trades'] = sorted(
                patterns['best_performing_trades'], 
                key=lambda x: x['return_pct'], 
                reverse=True
            )[:3]
            
            patterns['worst_performing_trades'] = sorted(
                patterns['worst_performing_trades'], 
                key=lambda x: x['return_pct']
            )[:3]
            
            # Store learned preferences
            self.user_preferences[user_id] = patterns
            self._save_user_preferences(user_id, patterns)
            
            return {
                'status': 'success',
                'patterns': patterns,
                'insights': self._generate_insights_from_patterns(patterns)
            }
            
        except Exception as e:
            logger.error(f"Error learning from user trades: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to analyze trading patterns'
            }
    
    def get_personalized_recommendations(self, user_id, market_data=None):
        """Generate recommendations based on user's learned preferences"""
        try:
            # Load user preferences
            preferences = self._load_user_preferences(user_id)
            if not preferences:
                return {
                    'status': 'no_profile',
                    'message': 'No trading profile found. Make some trades to build your profile!'
                }
            
            recommendations = []
            
            # Get general AI insights
            ai_engine = AIInsightsEngine()
            
            # Filter recommendations based on user preferences
            if market_data:
                for symbol, data in market_data.items():
                    score = self._calculate_recommendation_score(symbol, data, preferences)
                    
                    if score > 0.6:  # Threshold for recommendation
                        recommendation = {
                            'symbol': symbol,
                            'score': score,
                            'reason': self._generate_recommendation_reason(symbol, data, preferences, score),
                            'action': 'buy' if data.get('expected_return', 0) > 0 else 'hold',
                            'personalized': True
                        }
                        recommendations.append(recommendation)
            
            # Sort by score
            recommendations = sorted(recommendations, key=lambda x: x['score'], reverse=True)[:5]
            
            # Add personalized insights
            insights = {
                'trading_style': self._describe_trading_style(preferences),
                'risk_profile': preferences.get('risk_tolerance', 'moderate'),
                'suggestions': self._generate_personalized_suggestions(preferences)
            }
            
            return {
                'status': 'success',
                'recommendations': recommendations,
                'insights': insights,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Error generating personalized recommendations: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to generate recommendations'
            }
    
    def _calculate_recommendation_score(self, symbol, data, preferences):
        """Calculate how well a stock matches user preferences"""
        score = 0.5  # Base score
        
        # Check if it's a favorite stock
        if symbol in preferences.get('favorite_stocks', {}):
            score += 0.2
        
        # Check risk alignment
        volatility = data.get('volatility', 0.15)
        if preferences['risk_tolerance'] == 'conservative' and volatility < 0.1:
            score += 0.15
        elif preferences['risk_tolerance'] == 'moderate' and 0.1 <= volatility <= 0.2:
            score += 0.15
        elif preferences['risk_tolerance'] == 'aggressive' and volatility > 0.2:
            score += 0.15
        
        # Check expected return
        expected_return = data.get('expected_return', 0)
        if expected_return > 0.05:  # 5% expected return
            score += 0.1
        
        # Check trade size alignment
        current_price = data.get('current_price', 100)
        typical_shares = preferences['preferred_trade_size'] / current_price if current_price > 0 else 100
        if 50 <= typical_shares <= 500:  # Reasonable share count
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _generate_recommendation_reason(self, symbol, data, preferences, score):
        """Generate personalized reason for recommendation"""
        reasons = []
        
        if symbol in preferences.get('favorite_stocks', {}):
            reasons.append(f"You've successfully traded {symbol} before")
        
        volatility = data.get('volatility', 0.15)
        if preferences['risk_tolerance'] == 'conservative' and volatility < 0.1:
            reasons.append("Low volatility matches your conservative style")
        elif preferences['risk_tolerance'] == 'moderate' and 0.1 <= volatility <= 0.2:
            reasons.append("Moderate risk aligns with your profile")
        elif preferences['risk_tolerance'] == 'aggressive' and volatility > 0.2:
            reasons.append("High volatility opportunity for aggressive traders")
        
        expected_return = data.get('expected_return', 0)
        if expected_return > 0.05:
            reasons.append(f"Strong return potential: {expected_return*100:.1f}%")
        
        if score > 0.8:
            reasons.append("Excellent match for your trading style")
        
        return " • ".join(reasons) if reasons else "Matches your trading profile"
    
    def _describe_trading_style(self, preferences):
        """Generate a description of user's trading style"""
        style_parts = []
        
        # Risk tolerance
        risk = preferences.get('risk_tolerance', 'moderate')
        style_parts.append(f"{risk.capitalize()} risk")
        
        # Trading frequency
        freq = preferences.get('trading_frequency', 'moderate')
        if freq == 'high':
            style_parts.append("active trader")
        elif freq == 'low':
            style_parts.append("patient investor")
        else:
            style_parts.append("balanced trader")
        
        # Holding period
        avg_holding = preferences.get('avg_holding_period', 7)
        if avg_holding < 1:
            style_parts.append("day trader")
        elif avg_holding < 7:
            style_parts.append("short-term")
        elif avg_holding < 30:
            style_parts.append("swing trader")
        else:
            style_parts.append("long-term investor")
        
        return ", ".join(style_parts)
    
    def _generate_personalized_suggestions(self, preferences):
        """Generate actionable suggestions based on user patterns"""
        suggestions = []
        
        # Based on profit/loss ratio
        pl_ratio = preferences.get('profit_loss_ratio', 1)
        if pl_ratio < 1:
            suggestions.append("Consider setting tighter stop-losses to improve your profit/loss ratio")
        elif pl_ratio > 3:
            suggestions.append("Great profit/loss ratio! Keep using your current strategy")
        
        # Based on holding period
        avg_holding = preferences.get('avg_holding_period', 7)
        if avg_holding < 1:
            suggestions.append("Very short holding periods increase trading costs - consider holding longer")
        elif avg_holding > 60:
            suggestions.append("Long holding periods are great for reducing taxes")
        
        # Based on favorite stocks
        fav_stocks = list(preferences.get('favorite_stocks', {}).keys())
        if len(fav_stocks) < 3:
            suggestions.append("Consider diversifying into more stocks")
        elif len(fav_stocks) == 5:
            suggestions.append(f"You tend to focus on {', '.join(fav_stocks[:3])} - know them well!")
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _save_user_preferences(self, user_id, preferences):
        """Save user preferences to disk"""
        filepath = os.path.join(self.models_dir, f'user_{user_id}_preferences.json')
        with open(filepath, 'w') as f:
            # Convert defaultdict to regular dict for JSON serialization
            save_prefs = {}
            for key, value in preferences.items():
                if isinstance(value, defaultdict):
                    save_prefs[key] = dict(value)
                else:
                    save_prefs[key] = value
            json.dump(save_prefs, f)
    
    def _load_user_preferences(self, user_id):
        """Load user preferences from disk"""
        filepath = os.path.join(self.models_dir, f'user_{user_id}_preferences.json')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None

# Global instance
personalized_ai = PersonalizedAIAssistant()