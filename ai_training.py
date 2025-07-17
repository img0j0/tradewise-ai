"""
Advanced AI Training System for Trading Intelligence
Implements continuous learning, pattern recognition, and adaptive market analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import logging
from collections import deque
import yfinance as yf
from app import db
from models import Trade, Portfolio, User
from sqlalchemy import desc, func
import json
import os
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AdvancedAITrainingSystem:
    """Enhanced AI system with continuous learning and market intelligence"""

    def __init__(self):
        self.models = {
            'price_prediction': MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000),
            'trend_classifier': RandomForestClassifier(n_estimators=150, max_depth=10),
            'volatility_predictor': MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000),
            'sentiment_analyzer': RandomForestClassifier(n_estimators=100)
        }
        self.scalers = {
            'price': StandardScaler(),
            'volatility': StandardScaler(),
            'sentiment': StandardScaler()
        }
        self.training_history = deque(maxlen=1000)  # Keep last 1000 training samples
        self.model_performance = {}
        self.market_memory = {}  # Store market patterns
        self.load_or_initialize_models()

    def load_or_initialize_models(self):
        """Load existing models or initialize new ones"""
        try:
            model_dir = 'ai_models'
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)

            for model_name, model in self.models.items():
                model_path = f'{model_dir}/{model_name}.pkl'
                if os.path.exists(model_path):
                    self.models[model_name] = joblib.load(model_path)
                    logger.info(f"Loaded existing model: {model_name}")
                else:
                    logger.info(f"Initializing new model: {model_name}")

        except Exception as e:
            logger.error(f"Error loading models: {e}")

    def save_models(self):
        """Save trained models to disk"""
        try:
            model_dir = 'ai_models'
            for model_name, model in self.models.items():
                model_path = f'{model_dir}/{model_name}.pkl'
                joblib.dump(model, model_path)
                logger.info(f"Saved model: {model_name}")
        except Exception as e:
            logger.error(f"Error saving models: {e}")

    def collect_training_data(self, symbols=None, days=90):
        """Collect comprehensive training data from multiple sources"""
        try:
            if not symbols:
                # Get most traded symbols from database
                popular_symbols = db.session.query(
                    Trade.symbol, 
                    func.count(Trade.id).label('count')
                ).group_by(Trade.symbol).order_by(desc('count')).limit(20).all()

                symbols = [s[0] for s in popular_symbols] if popular_symbols else ['AAPL', 'MSFT', 'GOOGL', 'AMZN']

            training_data = []

            for symbol in symbols:
                try:
                    # Fetch historical data
                    stock = yf.Ticker(symbol)
                    hist = stock.history(period=f"{days}d")

                    if hist.empty:
                        continue

                    # Calculate technical indicators
                    features = self._calculate_advanced_features(hist, symbol)

                    if features is not None:
                        training_data.extend(features)

                except Exception as e:
                    logger.error(f"Error collecting data for {symbol}: {e}")
                    continue

            return pd.DataFrame(training_data) if training_data else None

        except Exception as e:
            logger.error(f"Error collecting training data: {e}")
            return None

    def _calculate_advanced_features(self, hist, symbol):
        """Calculate advanced technical indicators and features"""
        try:
            features_list = []

            # Basic price features
            hist['Returns'] = hist['Close'].pct_change()
            hist['Log_Returns'] = np.log(hist['Close'] / hist['Close'].shift(1))

            # Moving averages
            hist['MA_7'] = hist['Close'].rolling(window=7).mean()
            hist['MA_21'] = hist['Close'].rolling(window=21).mean()
            hist['MA_50'] = hist['Close'].rolling(window=50).mean()

            # Volatility indicators
            hist['Volatility'] = hist['Returns'].rolling(window=20).std()
            hist['ATR'] = self._calculate_atr(hist)

            # Momentum indicators
            hist['RSI'] = self._calculate_rsi(hist['Close'])
            hist['MACD'], hist['MACD_Signal'] = self._calculate_macd(hist['Close'])

            # Volume indicators
            hist['Volume_Ratio'] = hist['Volume'] / hist['Volume'].rolling(window=20).mean()
            hist['OBV'] = (np.sign(hist['Close'].diff()) * hist['Volume']).cumsum()

            # Market microstructure
            hist['High_Low_Ratio'] = hist['High'] / hist['Low']
            hist['Close_Open_Ratio'] = hist['Close'] / hist['Open']

            # Drop NaN values
            hist = hist.dropna()

            # Create feature vectors
            for i in range(len(hist) - 1):
                features = {
                    'symbol': symbol,
                    'returns': hist['Returns'].iloc[i],
                    'log_returns': hist['Log_Returns'].iloc[i],
                    'volatility': hist['Volatility'].iloc[i],
                    'rsi': hist['RSI'].iloc[i],
                    'macd': hist['MACD'].iloc[i],
                    'macd_signal': hist['MACD_Signal'].iloc[i],
                    'volume_ratio': hist['Volume_Ratio'].iloc[i],
                    'obv_change': hist['OBV'].iloc[i] / hist['OBV'].iloc[i-1] if hist['OBV'].iloc[i-1] != 0 else 1,
                    'ma_7_ratio': hist['Close'].iloc[i] / hist['MA_7'].iloc[i] if hist['MA_7'].iloc[i] != 0 else 1,
                    'ma_21_ratio': hist['Close'].iloc[i] / hist['MA_21'].iloc[i] if hist['MA_21'].iloc[i] != 0 else 1,
                    'atr': hist['ATR'].iloc[i],
                    'high_low_ratio': hist['High_Low_Ratio'].iloc[i],
                    'close_open_ratio': hist['Close_Open_Ratio'].iloc[i],
                    'next_day_return': hist['Returns'].iloc[i + 1],  # Target variable
                    'next_day_direction': 1 if hist['Returns'].iloc[i + 1] > 0 else 0  # Binary target
                }
                features_list.append(features)

            return features_list

        except Exception as e:
            logger.error(f"Error calculating features: {e}")
            return None

    def _calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        return macd_line, signal_line

    def _calculate_atr(self, data, period=14):
        """Calculate Average True Range"""
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

    def train_models(self, training_data=None):
        """Train all AI models with collected data"""
        try:
            if training_data is None:
                training_data = self.collect_training_data()

            if training_data is None or training_data.empty:
                logger.warning("No training data available")
                return False

            # Prepare features
            feature_columns = ['returns', 'log_returns', 'volatility', 'rsi', 'macd', 
                             'macd_signal', 'volume_ratio', 'obv_change', 'ma_7_ratio', 
                             'ma_21_ratio', 'atr', 'high_low_ratio', 'close_open_ratio']

            X = training_data[feature_columns]

            # Train price prediction model
            y_price = training_data['next_day_return']
            X_train, X_test, y_train, y_test = train_test_split(X, y_price, test_size=0.2, random_state=42)

            X_train_scaled = self.scalers['price'].fit_transform(X_train)
            X_test_scaled = self.scalers['price'].transform(X_test)

            self.models['price_prediction'].fit(X_train_scaled, y_train)
            price_score = self.models['price_prediction'].score(X_test_scaled, y_test)

            # Train trend classifier
            y_trend = training_data['next_day_direction']
            X_train, X_test, y_train, y_test = train_test_split(X, y_trend, test_size=0.2, random_state=42)

            self.models['trend_classifier'].fit(X_train, y_train)
            trend_score = self.models['trend_classifier'].score(X_test, y_test)

            # Train volatility predictor
            y_volatility = training_data['volatility']
            X_train, X_test, y_train, y_test = train_test_split(X, y_volatility, test_size=0.2, random_state=42)

            X_train_scaled = self.scalers['volatility'].fit_transform(X_train)
            X_test_scaled = self.scalers['volatility'].transform(X_test)

            self.models['volatility_predictor'].fit(X_train_scaled, y_train)
            volatility_score = self.models['volatility_predictor'].score(X_test_scaled, y_test)

            # Update model performance
            self.model_performance = {
                'price_prediction': price_score,
                'trend_classifier': trend_score,
                'volatility_predictor': volatility_score,
                'last_training': datetime.utcnow().isoformat(),
                'training_samples': len(training_data)
            }

            # Save models
            self.save_models()

            logger.info(f"Models trained successfully: {self.model_performance}")
            return True

        except Exception as e:
            logger.error(f"Error training models: {e}")
            return False
    
    def train_advanced_ensemble(self, training_data=None):
        """Train advanced ensemble models with collected data"""
        try:
            if training_data is None:
                training_data = self.collect_training_data()

            if training_data is None or training_data.empty:
                logger.warning("No training data available")
                return False

            # Prepare features
            feature_columns = ['returns', 'log_returns', 'volatility', 'rsi', 'macd', 
                             'macd_signal', 'volume_ratio', 'obv_change', 'ma_7_ratio', 
                             'ma_21_ratio', 'atr', 'high_low_ratio', 'close_open_ratio']

            X = training_data[feature_columns]
            y_trend = training_data['next_day_direction']

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y_trend, test_size=0.2, random_state=42)

            # Scale the data
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Define individual models
            rf_model = RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42)
            gb_model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
            nn_model = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=300, random_state=42)

            # Train individual models
            rf_model.fit(X_train_scaled, y_train)
            gb_model.fit(X_train_scaled, y_train)
            nn_model.fit(X_train_scaled, y_train)

            # Evaluate individual models
            rf_accuracy = accuracy_score(y_test, rf_model.predict(X_test_scaled))
            gb_accuracy = accuracy_score(y_test, gb_model.predict(X_test_scaled))
            nn_accuracy = accuracy_score(y_test, nn_model.predict(X_test_scaled))

            logger.info(f"Random Forest Accuracy: {rf_accuracy}")
            logger.info(f"Gradient Boosting Accuracy: {gb_accuracy}")
            logger.info(f"Neural Network Accuracy: {nn_accuracy}")

            # Create VotingClassifier ensemble
            voting_clf = VotingClassifier(estimators=[('rf', rf_model), ('gb', gb_model), ('nn', nn_model)], 
                                          voting='soft')  # Use 'soft' for probability-based voting

            # Train the ensemble
            voting_clf.fit(X_train_scaled, y_train)

            # Evaluate the ensemble
            ensemble_accuracy = accuracy_score(y_test, voting_clf.predict(X_test_scaled))
            ensemble_precision = precision_score(y_test, voting_clf.predict(X_test_scaled))
            ensemble_recall = recall_score(y_test, voting_clf.predict(X_test_scaled))
            ensemble_f1 = f1_score(y_test, voting_clf.predict(X_test_scaled))
            
            logger.info(f"Ensemble Accuracy: {ensemble_accuracy}")
            logger.info(f"Ensemble Precision: {ensemble_precision}")
            logger.info(f"Ensemble Recall: {ensemble_recall}")
            logger.info(f"Ensemble F1 Score: {ensemble_f1}")

            # Update model performance
            self.model_performance = {
                'ensemble_accuracy': ensemble_accuracy,
                'ensemble_precision': ensemble_precision,
                'ensemble_recall': ensemble_recall,
                'ensemble_f1': ensemble_f1,
                'last_training': datetime.utcnow().isoformat(),
                'training_samples': len(training_data)
            }

            # Save the ensemble model (optional)
            model_dir = 'ai_models'
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
            ensemble_path = f'{model_dir}/ensemble_model.pkl'
            joblib.dump(voting_clf, ensemble_path)
            logger.info(f"Saved ensemble model to {ensemble_path}")

            return True

        except Exception as e:
            logger.error(f"Error training advanced ensemble models: {e}")
            return False

    def predict_market_conditions(self, symbol):
        """Generate comprehensive market predictions for a symbol"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="60d")

            if hist.empty:
                return None

            # Calculate features
            features_data = self._calculate_advanced_features(hist, symbol)
            if not features_data:
                return None

            # Get latest features
            latest_features = features_data[-1]
            feature_columns = ['returns', 'log_returns', 'volatility', 'rsi', 'macd', 
                             'macd_signal', 'volume_ratio', 'obv_change', 'ma_7_ratio', 
                             'ma_21_ratio', 'atr', 'high_low_ratio', 'close_open_ratio']

            X = pd.DataFrame([latest_features])[feature_columns]

            # Generate predictions
            predictions = {}

            # Price prediction
            X_scaled = self.scalers['price'].transform(X)
            price_prediction = self.models['price_prediction'].predict(X_scaled)[0]
            predictions['expected_return'] = float(price_prediction)

            # Trend prediction
            trend_proba = self.models['trend_classifier'].predict_proba(X)[0]
            predictions['uptrend_probability'] = float(trend_proba[1])
            predictions['trend_confidence'] = float(max(trend_proba))

            # Volatility prediction
            X_scaled = self.scalers['volatility'].transform(X)
            volatility_pred = self.models['volatility_predictor'].predict(X_scaled)[0]
            predictions['expected_volatility'] = float(volatility_pred)

            # Market regime detection
            predictions['market_regime'] = self._detect_market_regime(hist, latest_features)

            # Risk assessment
            predictions['risk_score'] = self._calculate_risk_score(latest_features, predictions)

            # Trading recommendation
            predictions['recommendation'] = self._generate_recommendation(predictions)

            return predictions

        except Exception as e:
            logger.error(f"Error predicting market conditions: {e}")
            return None

    def _detect_market_regime(self, hist, features):
        """Detect current market regime (trending, ranging, volatile)"""
        try:
            # Calculate regime indicators
            volatility = features['volatility']
            trend_strength = abs(features['macd'])

            if volatility > 0.03:
                return "high_volatility"
            elif trend_strength > 0.5:
                return "strong_trend"
            elif 0.01 < volatility < 0.02:
                return "ranging"
            else:
                return "low_volatility"

        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            return "unknown"

    def _calculate_risk_score(self, features, predictions):
        """Calculate comprehensive risk score"""
        try:
            risk_factors = []

            # Volatility risk
            if features['volatility'] > 0.03:
                risk_factors.append(30)
            elif features['volatility'] > 0.02:
                risk_factors.append(20)
            else:
                risk_factors.append(10)

            # Trend uncertainty
            trend_uncertainty = 1 - predictions['trend_confidence']
            risk_factors.append(trend_uncertainty * 25)

            # Technical indicator divergence
            if features['rsi'] > 70 or features['rsi'] < 30:
                risk_factors.append(15)

            # Volume anomaly
            if features['volume_ratio'] > 2 or features['volume_ratio'] < 0.5:
                risk_factors.append(20)

            return min(sum(risk_factors) / len(risk_factors), 100)

        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 50

    def _generate_recommendation(self, predictions):
        """Generate trading recommendation based on predictions"""
        try:
            if predictions['uptrend_probability'] > 0.7 and predictions['risk_score'] < 40:
                return "strong_buy"
            elif predictions['uptrend_probability'] > 0.6 and predictions['risk_score'] < 50:
                return "buy"
            elif predictions['uptrend_probability'] < 0.3 and predictions['risk_score'] > 60:
                return "strong_sell"
            elif predictions['uptrend_probability'] < 0.4:
                return "sell"
            else:
                return "hold"

        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return "hold"

    def continuous_learning(self):
        """Implement continuous learning from user trades"""
        try:
            # Get recent trades
            recent_trades = Trade.query.filter(
                Trade.timestamp >= datetime.utcnow() - timedelta(days=7)
            ).all()

            if not recent_trades:
                return

            # Analyze trade outcomes
            for trade in recent_trades:
                # Check if trade was profitable
                current_price = self._get_current_price(trade.symbol)
                if current_price:
                    if trade.action == 'buy':
                        profit = (current_price - trade.price) / trade.price
                    else:
                        profit = (trade.price - current_price) / trade.price

                    # Store learning data
                    self.training_history.append({
                        'symbol': trade.symbol,
                        'action': trade.action,
                        'confidence': trade.confidence_score,
                        'profit': profit,
                        'timestamp': trade.timestamp
                    })

            # Retrain models periodically
            if len(self.training_history) >= 100:
                self.train_models()

        except Exception as e:
            logger.error(f"Error in continuous learning: {e}")

    def _get_current_price(self, symbol):
        """Get current price for a symbol"""
        try:
            stock = yf.Ticker(symbol)
            return stock.info.get('currentPrice') or stock.info.get('regularMarketPrice')
        except:
            return None

    def get_ai_insights(self, symbol):
        """Generate comprehensive AI insights for a symbol"""
        try:
            predictions = self.predict_market_conditions(symbol)
            if not predictions:
                return None

            insights = {
                'symbol': symbol,
                'predictions': predictions,
                'confidence_score': predictions['trend_confidence'] * 100,
                'risk_level': self._get_risk_level(predictions['risk_score']),
                'key_factors': self._identify_key_factors(symbol, predictions),
                'market_sentiment': self._analyze_market_sentiment(predictions),
                'technical_summary': self._generate_technical_summary(symbol),
                'ai_recommendation': predictions['recommendation'],
                'model_accuracy': self.model_performance.get('trend_classifier', 0) * 100
            }

            return insights

        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return None

    def _get_risk_level(self, risk_score):
        """Convert risk score to risk level"""
        if risk_score < 20:
            return "very_low"
        elif risk_score < 40:
            return "low"
        elif risk_score < 60:
            return "moderate"
        elif risk_score < 80:
            return "high"
        else:
            return "very_high"

    def _identify_key_factors(self, symbol, predictions):
        """Identify key factors influencing the prediction"""
        factors = []

        if predictions['uptrend_probability'] > 0.7:
            factors.append("Strong bullish momentum detected")
        elif predictions['uptrend_probability'] < 0.3:
            factors.append("Bearish pressure identified")

        if predictions['expected_volatility'] > 0.03:
            factors.append("High volatility expected")
        elif predictions['expected_volatility'] < 0.01:
            factors.append("Low volatility environment")

        if predictions['market_regime'] == "strong_trend":
            factors.append("Strong trending market")
        elif predictions['market_regime'] == "ranging":
            factors.append("Range-bound market conditions")

        return factors

    def _analyze_market_sentiment(self, predictions):
        """Analyze overall market sentiment"""
        if predictions['uptrend_probability'] > 0.7:
            return "bullish"
        elif predictions['uptrend_probability'] > 0.6:
            return "moderately_bullish"
        elif predictions['uptrend_probability'] > 0.4:
            return "neutral"
        elif predictions['uptrend_probability'] > 0.3:
            return "moderately_bearish"
        else:
            return "bearish"

    def _generate_technical_summary(self, symbol):
        """Generate technical analysis summary"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="30d")

            if hist.empty:
                return "Unable to generate technical summary"

            latest_close = hist['Close'].iloc[-1]
            ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]

            summary = []

            if latest_close > ma_20:
                summary.append("Trading above 20-day moving average")
            else:
                summary.append("Trading below 20-day moving average")

            # RSI analysis
            rsi = self._calculate_rsi(hist['Close']).iloc[-1]
            if rsi > 70:
                summary.append("RSI indicates overbought conditions")
            elif rsi < 30:
                summary.append("RSI indicates oversold conditions")
            else:
                summary.append(f"RSI at neutral levels ({rsi:.1f})")

            return ". ".join(summary)

        except Exception as e:
            logger.error(f"Error generating technical summary: {e}")
            return "Technical analysis unavailable"

# Initialize the advanced AI training system
ai_trainer = AdvancedAITrainingSystem()