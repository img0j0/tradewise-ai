
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class AdvancedAIMemory:
    """Advanced AI system that remembers and learns from every interaction"""
    
    def __init__(self):
        self.memory_storage = {}
        self.user_patterns = {}
        self.market_memory = {}
        self.neural_networks = {}
        self.scalers = {}
        
    def record_user_decision(self, user_id, stock_symbol, decision, market_context, outcome=None):
        """Record every user decision for pattern learning"""
        if user_id not in self.memory_storage:
            self.memory_storage[user_id] = []
            
        decision_record = {
            'timestamp': datetime.now().isoformat(),
            'stock_symbol': stock_symbol,
            'decision': decision,  # 'buy', 'sell', 'hold'
            'market_context': market_context,
            'user_confidence': decision.get('confidence', 50),
            'outcome': outcome,
            'market_sentiment': self._analyze_market_sentiment(market_context)
        }
        
        self.memory_storage[user_id].append(decision_record)
        self._update_user_patterns(user_id, decision_record)
        
    def _analyze_market_sentiment(self, market_context):
        """Analyze overall market sentiment from context"""
        sentiment_score = 0
        
        if market_context.get('market_trend', 0) > 0:
            sentiment_score += 1
        if market_context.get('volume_ratio', 1) > 1.2:
            sentiment_score += 1
        if market_context.get('volatility', 0.15) < 0.1:
            sentiment_score += 1
            
        return 'bullish' if sentiment_score >= 2 else 'bearish' if sentiment_score == 0 else 'neutral'
    
    def _update_user_patterns(self, user_id, decision_record):
        """Update learned patterns for this user"""
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = {
                'risk_tolerance': 'moderate',
                'preferred_sectors': [],
                'decision_timing': [],
                'success_patterns': []
            }
        
        patterns = self.user_patterns[user_id]
        
        # Learn risk tolerance
        if decision_record['decision'] == 'buy' and decision_record['market_context'].get('volatility', 0) > 0.2:
            patterns['risk_tolerance'] = 'aggressive'
        elif decision_record['decision'] == 'sell' and decision_record['market_context'].get('volatility', 0) < 0.1:
            patterns['risk_tolerance'] = 'conservative'
            
        # Track sector preferences
        sector = decision_record['market_context'].get('sector', 'Unknown')
        if sector not in patterns['preferred_sectors']:
            patterns['preferred_sectors'].append(sector)
            
    def get_personalized_recommendation(self, user_id, stock_symbol, current_market_context):
        """Generate personalized recommendation based on user's history"""
        if user_id not in self.memory_storage:
            return self._default_recommendation(stock_symbol, current_market_context)
            
        user_history = self.memory_storage[user_id]
        user_patterns = self.user_patterns.get(user_id, {})
        
        # Analyze similar past decisions
        similar_decisions = self._find_similar_decisions(user_history, current_market_context)
        
        if similar_decisions:
            success_rate = sum(1 for d in similar_decisions if d.get('outcome', 0) > 0) / len(similar_decisions)
            
            recommendation = {
                'action': 'buy' if success_rate > 0.6 else 'hold' if success_rate > 0.4 else 'sell',
                'confidence': min(95, int(success_rate * 100) + 20),
                'reasoning': f"Based on {len(similar_decisions)} similar past decisions with {success_rate:.1%} success rate",
                'risk_adjusted': True,
                'personalization_factor': 0.8
            }
        else:
            recommendation = self._default_recommendation(stock_symbol, current_market_context)
            recommendation['personalization_factor'] = 0.2
            
        return recommendation
    
    def _find_similar_decisions(self, user_history, current_context):
        """Find similar past decisions based on market context"""
        similar = []
        
        for decision in user_history[-50:]:  # Last 50 decisions
            similarity_score = 0
            past_context = decision['market_context']
            
            # Compare key factors
            if abs(past_context.get('volatility', 0) - current_context.get('volatility', 0)) < 0.05:
                similarity_score += 1
            if past_context.get('sector') == current_context.get('sector'):
                similarity_score += 2
            if abs(past_context.get('market_trend', 0) - current_context.get('market_trend', 0)) < 0.02:
                similarity_score += 1
                
            if similarity_score >= 2:
                similar.append(decision)
                
        return similar
    
    def _default_recommendation(self, stock_symbol, market_context):
        """Default recommendation when no user history exists"""
        return {
            'action': 'hold',
            'confidence': 50,
            'reasoning': 'No sufficient user history for personalized recommendation',
            'risk_adjusted': False,
            'personalization_factor': 0.0
        }
    
    def train_neural_predictor(self, user_id):
        """Train a neural network for this specific user"""
        if user_id not in self.memory_storage or len(self.memory_storage[user_id]) < 20:
            return False
            
        try:
            # Prepare training data
            decisions = self.memory_storage[user_id]
            
            features = []
            targets = []
            
            for decision in decisions:
                if decision.get('outcome') is not None:
                    context = decision['market_context']
                    feature_vector = [
                        context.get('volatility', 0.15),
                        context.get('volume_ratio', 1.0),
                        context.get('market_trend', 0),
                        context.get('price_change_pct', 0),
                        1 if decision['decision'] == 'buy' else 0 if decision['decision'] == 'hold' else -1
                    ]
                    features.append(feature_vector)
                    targets.append(decision['outcome'])
            
            if len(features) < 10:
                return False
                
            # Train neural network
            X = np.array(features)
            y = np.array(targets)
            
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            model = MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=1000, random_state=42)
            model.fit(X_scaled, y)
            
            # Store the trained model
            self.neural_networks[user_id] = model
            self.scalers[user_id] = scaler
            
            logger.info(f"Neural network trained for user {user_id} with {len(features)} samples")
            return True
            
        except Exception as e:
            logger.error(f"Error training neural predictor for user {user_id}: {e}")
            return False
    
    def predict_outcome(self, user_id, stock_symbol, decision, market_context):
        """Predict outcome using user's trained neural network"""
        if user_id not in self.neural_networks:
            return None
            
        try:
            model = self.neural_networks[user_id]
            scaler = self.scalers[user_id]
            
            feature_vector = np.array([[
                market_context.get('volatility', 0.15),
                market_context.get('volume_ratio', 1.0),
                market_context.get('market_trend', 0),
                market_context.get('price_change_pct', 0),
                1 if decision == 'buy' else 0 if decision == 'hold' else -1
            ]])
            
            feature_scaled = scaler.transform(feature_vector)
            prediction = model.predict(feature_scaled)[0]
            
            return {
                'predicted_outcome': prediction,
                'confidence': min(95, abs(prediction) * 20 + 60),
                'model_based': True
            }
            
        except Exception as e:
            logger.error(f"Error predicting outcome for user {user_id}: {e}")
            return None
    
    def save_memory(self, filepath='ai_models/advanced_memory.pkl'):
        """Save AI memory to disk"""
        try:
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'memory_storage': self.memory_storage,
                    'user_patterns': self.user_patterns,
                    'market_memory': self.market_memory
                }, f)
            return True
        except Exception as e:
            logger.error(f"Error saving AI memory: {e}")
            return False
    
    def load_memory(self, filepath='ai_models/advanced_memory.pkl'):
        """Load AI memory from disk"""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.memory_storage = data.get('memory_storage', {})
                self.user_patterns = data.get('user_patterns', {})
                self.market_memory = data.get('market_memory', {})
            return True
        except Exception as e:
            logger.error(f"Error loading AI memory: {e}")
            return False

# Global instance
advanced_ai_memory = AdvancedAIMemory()
