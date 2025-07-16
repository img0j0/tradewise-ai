import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class AIInsightsEngine:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_features(self, stock_data):
        """Prepare features for ML model from stock data"""
        try:
            # Calculate technical indicators
            df = pd.DataFrame(stock_data)
            
            # Price change features
            df['price_change'] = df['current_price'] - df['previous_close']
            df['price_change_pct'] = (df['price_change'] / df['previous_close']) * 100
            
            # Volume features
            df['volume_normalized'] = df['volume'] / df['avg_volume']
            
            # Market cap features
            df['market_cap_log'] = np.log(df['market_cap'] + 1)
            
            # Moving averages (simulated)
            df['ma_ratio'] = df['current_price'] / df['moving_avg_20']
            
            # Volatility (simulated)
            df['volatility'] = df['high'] - df['low']
            df['volatility_pct'] = (df['volatility'] / df['current_price']) * 100
            
            # Select features for model
            features = ['price_change_pct', 'volume_normalized', 'market_cap_log', 
                       'ma_ratio', 'volatility_pct']
            
            return df[features].fillna(0)
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return pd.DataFrame()
    
    def train_model(self, stock_data):
        """Train the AI model with historical data"""
        try:
            features_df = self.prepare_features(stock_data)
            
            if features_df.empty:
                logger.warning("No features available for training")
                return False
            
            # Generate synthetic target labels for training
            # In a real scenario, this would be based on actual performance
            targets = []
            for _, row in features_df.iterrows():
                # Simple heuristic: positive price change + high volume = buy signal
                score = 0
                if row['price_change_pct'] > 0:
                    score += 1
                if row['volume_normalized'] > 1.2:
                    score += 1
                if row['ma_ratio'] > 1.05:
                    score += 1
                
                targets.append(1 if score >= 2 else 0)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features_df, targets, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            logger.info(f"Model trained - Train Score: {train_score:.3f}, Test Score: {test_score:.3f}")
            
            self.is_trained = True
            return True
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return False
    
    def generate_confidence_score(self, stock_info):
        """Generate confidence score for a single stock"""
        try:
            if not self.is_trained:
                # Use rule-based scoring if model isn't trained
                return self._rule_based_confidence(stock_info)
            
            # Prepare features for single stock
            features_df = self.prepare_features([stock_info])
            
            if features_df.empty:
                return self._rule_based_confidence(stock_info)
            
            # Scale features
            features_scaled = self.scaler.transform(features_df)
            
            # Get prediction probability
            prob = self.model.predict_proba(features_scaled)[0]
            
            # Convert to confidence score (0-100)
            confidence = prob[1] * 100  # Probability of positive class
            
            return min(max(confidence, 0), 100)  # Clamp between 0-100
            
        except Exception as e:
            logger.error(f"Error generating confidence score: {e}")
            return self._rule_based_confidence(stock_info)
    
    def _rule_based_confidence(self, stock_info):
        """Fallback rule-based confidence scoring"""
        score = 50  # Base score
        
        try:
            # Price momentum
            price_change_pct = ((stock_info['current_price'] - stock_info['previous_close']) / 
                               stock_info['previous_close']) * 100
            
            if price_change_pct > 5:
                score += 20
            elif price_change_pct > 2:
                score += 10
            elif price_change_pct < -5:
                score -= 20
            elif price_change_pct < -2:
                score -= 10
            
            # Volume analysis
            volume_ratio = stock_info['volume'] / stock_info['avg_volume']
            if volume_ratio > 1.5:
                score += 15
            elif volume_ratio > 1.2:
                score += 10
            elif volume_ratio < 0.5:
                score -= 10
            
            # Market cap consideration
            if stock_info['market_cap'] > 10000000000:  # Large cap
                score += 5
            elif stock_info['market_cap'] < 1000000000:  # Small cap
                score -= 5
            
            # Moving average
            ma_ratio = stock_info['current_price'] / stock_info['moving_avg_20']
            if ma_ratio > 1.05:
                score += 10
            elif ma_ratio < 0.95:
                score -= 10
            
            return min(max(score, 0), 100)
            
        except Exception as e:
            logger.error(f"Error in rule-based scoring: {e}")
            return 50
    
    def generate_insights(self, stock_info):
        """Generate AI insights for a stock"""
        confidence = self.generate_confidence_score(stock_info)
        
        insights = {
            'confidence_score': confidence,
            'recommendation': 'HOLD',
            'risk_level': 'MEDIUM',
            'key_factors': [],
            'analysis': ''
        }
        
        try:
            # Determine recommendation
            if confidence > 75:
                insights['recommendation'] = 'BUY'
                insights['risk_level'] = 'LOW'
            elif confidence > 60:
                insights['recommendation'] = 'WEAK BUY'
                insights['risk_level'] = 'MEDIUM'
            elif confidence < 25:
                insights['recommendation'] = 'SELL'
                insights['risk_level'] = 'HIGH'
            elif confidence < 40:
                insights['recommendation'] = 'WEAK SELL'
                insights['risk_level'] = 'MEDIUM'
            
            # Key factors analysis
            price_change_pct = ((stock_info['current_price'] - stock_info['previous_close']) / 
                               stock_info['previous_close']) * 100
            
            if abs(price_change_pct) > 2:
                insights['key_factors'].append(f"Price movement: {price_change_pct:.1f}%")
            
            volume_ratio = stock_info['volume'] / stock_info['avg_volume']
            if volume_ratio > 1.2:
                insights['key_factors'].append(f"High volume: {volume_ratio:.1f}x average")
            
            if stock_info['current_price'] > stock_info['moving_avg_20']:
                insights['key_factors'].append("Above 20-day moving average")
            else:
                insights['key_factors'].append("Below 20-day moving average")
            
            # Generate analysis text
            insights['analysis'] = self._generate_analysis_text(stock_info, confidence)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return insights
    
    def _generate_analysis_text(self, stock_info, confidence):
        """Generate human-readable analysis text"""
        try:
            symbol = stock_info['symbol']
            price = stock_info['current_price']
            change_pct = ((stock_info['current_price'] - stock_info['previous_close']) / 
                         stock_info['previous_close']) * 100
            
            analysis = f"{symbol} is currently trading at ${price:.2f}. "
            
            if change_pct > 0:
                analysis += f"The stock is up {change_pct:.1f}% from previous close. "
            else:
                analysis += f"The stock is down {abs(change_pct):.1f}% from previous close. "
            
            if confidence > 70:
                analysis += "Technical indicators suggest strong bullish momentum. "
            elif confidence > 50:
                analysis += "Technical indicators show moderate positive sentiment. "
            elif confidence < 30:
                analysis += "Technical indicators suggest bearish pressure. "
            else:
                analysis += "Mixed signals from technical indicators. "
            
            volume_ratio = stock_info['volume'] / stock_info['avg_volume']
            if volume_ratio > 1.5:
                analysis += "High trading volume supports the price movement. "
            elif volume_ratio < 0.7:
                analysis += "Low trading volume may indicate weak conviction. "
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating analysis text: {e}")
            return "Analysis unavailable due to data processing error."
