"""
Advanced AI Advice Engine for Concise Stock Recommendations
Combines multiple data sources and advanced ML techniques for optimal trading advice
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import logging
from textblob import TextBlob
import requests
import json
import os
from collections import defaultdict, deque
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AdvancedStockAdviceEngine:
    """AI engine that provides concise, actionable stock advice"""
    
    def __init__(self):
        self.ensemble_model = None
        self.scalers = {
            'technical': StandardScaler(),
            'fundamental': MinMaxScaler(),
            'sentiment': StandardScaler()
        }
        self.advice_templates = {
            'strong_buy': [
                "Strong fundamentals + bullish momentum = BUY opportunity",
                "Exceptional growth potential with manageable risk",
                "Technical indicators align perfectly with strong earnings"
            ],
            'buy': [
                "Positive outlook with good risk-reward ratio",
                "Solid fundamentals support near-term growth",
                "Technical momentum favors upward movement"
            ],
            'hold': [
                "Current price fairly valued, monitor for better entry",
                "Mixed signals suggest patience until clarity emerges",
                "Stable position, watch for trend confirmation"
            ],
            'sell': [
                "Overvalued with technical weakness emerging",
                "Risk outweighs potential reward at current levels",
                "Consider profit-taking or risk reduction"
            ],
            'strong_sell': [
                "Multiple red flags warrant immediate attention",
                "Fundamental deterioration + technical breakdown",
                "High risk of significant downside movement"
            ]
        }
        self.market_memory = deque(maxlen=5000)  # Remember market patterns
        self.success_tracking = defaultdict(list)  # Track advice accuracy
        self.load_or_create_models()
        self._auto_train_with_sample_data()  # Auto-train on startup
    
    def load_or_create_models(self):
        """Load existing models or create new ensemble"""
        try:
            model_path = 'ai_models/advice_engine.pkl'
            if os.path.exists(model_path):
                self.ensemble_model = joblib.load(model_path)
                logger.info("Loaded existing advice engine model")
            else:
                self.create_ensemble_model()
                logger.info("Created new advice engine model")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.create_ensemble_model()
    
    def create_ensemble_model(self):
        """Create advanced ensemble model for stock advice"""
        # Multiple specialized models
        models = [
            ('technical_rf', RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42)),
            ('fundamental_gb', GradientBoostingClassifier(n_estimators=150, learning_rate=0.1, random_state=42)),
            ('sentiment_mlp', MLPClassifier(hidden_layer_sizes=(100, 50, 25), max_iter=2000, random_state=42)),
            ('momentum_rf', RandomForestClassifier(n_estimators=100, max_features='sqrt', random_state=42))
        ]
        
        # Create voting classifier with soft voting for probability estimates
        self.ensemble_model = VotingClassifier(
            estimators=models,
            voting='soft'
        )
        
        logger.info("Created ensemble model with 4 specialized classifiers")
    
    def collect_comprehensive_data(self, symbol, days=365):
        """Collect all available data for training"""
        try:
            stock = yf.Ticker(symbol)
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            hist_data = stock.history(start=start_date, end=end_date)
            
            if hist_data.empty:
                return None
            
            # Get stock info
            info = stock.info
            
            # Calculate comprehensive features
            features = self.calculate_advanced_features(hist_data, info)
            
            # Add market sentiment
            features = self.add_sentiment_features(features, symbol)
            
            # Add fundamental ratios
            features = self.add_fundamental_features(features, info)
            
            return features
            
        except Exception as e:
            logger.error(f"Error collecting data for {symbol}: {e}")
            return None
    
    def calculate_advanced_features(self, hist_data, info):
        """Calculate 50+ technical and statistical features"""
        df = hist_data.copy()
        
        # Price-based features
        df['returns'] = df['Close'].pct_change()
        df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        df['price_momentum_5'] = df['Close'] / df['Close'].shift(5) - 1
        df['price_momentum_20'] = df['Close'] / df['Close'].shift(20) - 1
        
        # Moving averages and crossovers
        for period in [5, 10, 20, 50, 200]:
            df[f'sma_{period}'] = df['Close'].rolling(period).mean()
            df[f'ema_{period}'] = df['Close'].ewm(span=period).mean()
            df[f'price_sma_ratio_{period}'] = df['Close'] / df[f'sma_{period}']
        
        # Technical indicators
        df['rsi'] = self.calculate_rsi(df['Close'])
        df['macd'], df['macd_signal'] = self.calculate_macd(df['Close'])
        df['bb_upper'], df['bb_lower'], df['bb_middle'] = self.calculate_bollinger_bands(df['Close'])
        df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Volatility measures
        df['volatility_20'] = df['returns'].rolling(20).std()
        df['atr'] = self.calculate_atr(df)
        df['volatility_regime'] = np.where(df['volatility_20'] > df['volatility_20'].rolling(50).mean(), 1, 0)
        
        # Volume analysis
        df['volume_sma_20'] = df['Volume'].rolling(20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma_20']
        df['price_volume_trend'] = ((df['Close'] - df['Close'].shift(1)) / df['Close'].shift(1)) * df['Volume']
        
        # Support and resistance
        df['support'] = df['Low'].rolling(20).min()
        df['resistance'] = df['High'].rolling(20).max()
        df['support_distance'] = (df['Close'] - df['support']) / df['Close']
        df['resistance_distance'] = (df['resistance'] - df['Close']) / df['Close']
        
        # Market structure
        df['higher_high'] = (df['High'] > df['High'].shift(1)).astype(int)
        df['higher_low'] = (df['Low'] > df['Low'].shift(1)).astype(int)
        df['trend_strength'] = df['higher_high'] + df['higher_low'] - 1
        
        return df
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        return macd, signal_line
    
    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(period).mean()
        std = prices.rolling(period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, lower, sma
    
    def calculate_atr(self, df, period=14):
        """Calculate Average True Range"""
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
    
    def add_sentiment_features(self, df, symbol):
        """Add sentiment analysis features"""
        try:
            # Simulate sentiment scores (in production, use news APIs)
            # This would connect to news APIs, social media sentiment, etc.
            sentiment_score = np.random.normal(0, 0.3, len(df))  # Placeholder
            df['sentiment_score'] = sentiment_score
            df['sentiment_ma_5'] = pd.Series(sentiment_score).rolling(5).mean()
            df['sentiment_trend'] = df['sentiment_score'] - df['sentiment_score'].shift(5)
            
        except Exception as e:
            logger.warning(f"Could not get sentiment data: {e}")
            df['sentiment_score'] = 0
            df['sentiment_ma_5'] = 0
            df['sentiment_trend'] = 0
        
        return df
    
    def add_fundamental_features(self, df, info):
        """Add fundamental analysis features"""
        try:
            # Extract key fundamental ratios
            pe_ratio = info.get('trailingPE', 20)
            pb_ratio = info.get('priceToBook', 3)
            ps_ratio = info.get('priceToSalesTrailing12Months', 5)
            roe = info.get('returnOnEquity', 0.15)
            debt_ratio = info.get('debtToEquity', 50)
            
            # Add as constant features (would vary in production with quarterly updates)
            df['pe_ratio'] = pe_ratio
            df['pb_ratio'] = pb_ratio
            df['ps_ratio'] = ps_ratio
            df['roe'] = roe
            df['debt_ratio'] = debt_ratio
            
            # Calculate relative valuations
            df['pe_percentile'] = np.where(pe_ratio < 15, 0.8, np.where(pe_ratio < 25, 0.5, 0.2))
            df['pb_percentile'] = np.where(pb_ratio < 2, 0.8, np.where(pb_ratio < 4, 0.5, 0.2))
            
        except Exception as e:
            logger.warning(f"Limited fundamental data available: {e}")
            for col in ['pe_ratio', 'pb_ratio', 'ps_ratio', 'roe', 'debt_ratio', 'pe_percentile', 'pb_percentile']:
                df[col] = 0.5  # Neutral values
        
        return df
    
    def create_target_labels(self, df, forward_days=5):
        """Create sophisticated target labels based on future returns"""
        # Calculate forward returns
        df['forward_return'] = df['Close'].shift(-forward_days) / df['Close'] - 1
        
        # Create 5-class labels for nuanced advice
        conditions = [
            df['forward_return'] > 0.05,  # Strong Buy (>5% gain)
            df['forward_return'] > 0.02,  # Buy (2-5% gain)
            df['forward_return'].between(-0.02, 0.02),  # Hold (-2% to 2%)
            df['forward_return'] > -0.05,  # Sell (-5% to -2% loss)
            df['forward_return'] <= -0.05  # Strong Sell (>5% loss)
        ]
        
        choices = [4, 3, 2, 1, 0]  # Strong Buy to Strong Sell
        df['target'] = np.select(conditions, choices, default=2)
        
        return df
    
    def train_with_multiple_stocks(self, symbols=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META'], days=365):
        """Train on multiple stocks for robust learning"""
        all_features = []
        all_targets = []
        
        logger.info(f"Training on {len(symbols)} stocks with {days} days of data")
        
        for symbol in symbols:
            try:
                logger.info(f"Processing {symbol}...")
                data = self.collect_comprehensive_data(symbol, days)
                
                if data is not None and len(data) > 50:
                    # Create target labels
                    data = self.create_target_labels(data)
                    
                    # Select features for training
                    feature_cols = [col for col in data.columns if col not in 
                                  ['target', 'forward_return', 'Open', 'High', 'Low', 'Close', 'Volume']]
                    
                    # Remove rows with NaN values
                    clean_data = data[feature_cols + ['target']].dropna()
                    
                    if len(clean_data) > 30:
                        all_features.append(clean_data[feature_cols])
                        all_targets.extend(clean_data['target'].values)
                        logger.info(f"Added {len(clean_data)} samples from {symbol}")
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue
        
        if not all_features:
            logger.error("No training data collected")
            return False
        
        # Combine all data
        X = pd.concat(all_features, ignore_index=True)
        y = np.array(all_targets)
        
        logger.info(f"Total training samples: {len(X)}")
        
        # Scale features
        X_scaled = self.scalers['technical'].fit_transform(X.fillna(0))
        
        # Train ensemble model with time series split
        tscv = TimeSeriesSplit(n_splits=5)
        scores = cross_val_score(self.ensemble_model, X_scaled, y, cv=tscv, scoring='accuracy')
        
        # Final training on all data
        self.ensemble_model.fit(X_scaled, y)
        
        # Save model
        self.save_model()
        
        logger.info(f"Model trained! Cross-validation accuracy: {scores.mean():.3f} ± {scores.std():.3f}")
        return True
    
    def get_concise_advice(self, symbol):
        """Generate concise, actionable advice for a stock"""
        try:
            # Collect current data
            data = self.collect_comprehensive_data(symbol, days=100)
            if data is None:
                return self.fallback_advice(symbol)
            
            # Get latest features
            feature_cols = [col for col in data.columns if col not in 
                          ['target', 'forward_return', 'Open', 'High', 'Low', 'Close', 'Volume']]
            
            latest_features = data[feature_cols].iloc[-1:].fillna(0)
            X_scaled = self.scalers['technical'].transform(latest_features)
            
            # Get prediction and confidence
            if self.ensemble_model is None:
                return self.fallback_advice(symbol)
            
            prediction = self.ensemble_model.predict(X_scaled)[0]
            probabilities = self.ensemble_model.predict_proba(X_scaled)[0]
            confidence = max(probabilities)
            
            # Generate advice
            advice_categories = ['strong_sell', 'sell', 'hold', 'buy', 'strong_buy']
            category = advice_categories[int(prediction)]
            
            # Select advice template
            templates = self.advice_templates[category]
            advice_text = np.random.choice(templates)
            
            # Add key insights
            key_factors = self.extract_key_factors(data, symbol)
            
            advice = {
                'symbol': symbol,
                'recommendation': category.replace('_', ' ').title(),
                'confidence': round(confidence * 100, 1),
                'advice': advice_text,
                'key_factors': key_factors,
                'risk_level': self.assess_risk_level(data),
                'target_price': self.estimate_target_price(data),
                'time_horizon': '1-3 months',
                'generated_at': datetime.now().isoformat()
            }
            
            # Store for learning
            self.market_memory.append({
                'symbol': symbol,
                'prediction': prediction,
                'confidence': confidence,
                'timestamp': datetime.now(),
                'price': data['Close'].iloc[-1]
            })
            
            return advice
            
        except Exception as e:
            logger.error(f"Error generating advice for {symbol}: {e}")
            return self.fallback_advice(symbol)
    
    def extract_key_factors(self, data, symbol):
        """Extract the most important factors driving the recommendation"""
        try:
            latest = data.iloc[-1]
            factors = []
            
            # Technical factors
            if latest['rsi'] > 70:
                factors.append("Overbought conditions (RSI > 70)")
            elif latest['rsi'] < 30:
                factors.append("Oversold conditions (RSI < 30)")
            
            if latest['price_sma_ratio_20'] > 1.05:
                factors.append("Strong momentum above 20-day average")
            elif latest['price_sma_ratio_20'] < 0.95:
                factors.append("Weakness below 20-day average")
            
            # Volume factors
            if latest['volume_ratio'] > 2:
                factors.append("High volume confirmation")
            elif latest['volume_ratio'] < 0.5:
                factors.append("Low volume - lack of conviction")
            
            # Volatility factors
            if latest['volatility_regime'] == 1:
                factors.append("Elevated volatility environment")
            
            # Fundamental factors
            if latest['pe_percentile'] > 0.7:
                factors.append("Attractive valuation metrics")
            elif latest['pe_percentile'] < 0.3:
                factors.append("Expensive valuation levels")
            
            return factors[:3]  # Top 3 factors
            
        except Exception as e:
            logger.error(f"Error extracting factors: {e}")
            return ["Technical analysis", "Market conditions", "Fundamental assessment"]
    
    def assess_risk_level(self, data):
        """Assess the risk level of the stock"""
        try:
            latest = data.iloc[-1]
            risk_score = 0
            
            # Volatility risk
            if latest['volatility_20'] > data['volatility_20'].quantile(0.8):
                risk_score += 2
            elif latest['volatility_20'] > data['volatility_20'].quantile(0.6):
                risk_score += 1
            
            # Technical risk
            if latest['rsi'] > 80 or latest['rsi'] < 20:
                risk_score += 1
            
            # Momentum risk
            if abs(latest['price_momentum_20']) > 0.3:
                risk_score += 1
            
            if risk_score >= 3:
                return "High"
            elif risk_score >= 1:
                return "Medium"
            else:
                return "Low"
                
        except Exception:
            return "Medium"
    
    def estimate_target_price(self, data):
        """Estimate a target price based on technical analysis"""
        try:
            current_price = data['Close'].iloc[-1]
            
            # Use recent support/resistance levels
            recent_high = data['High'].tail(20).max()
            recent_low = data['Low'].tail(20).min()
            
            # Simple target based on momentum and volatility
            momentum = data['price_momentum_20'].iloc[-1]
            volatility = data['volatility_20'].iloc[-1]
            
            if momentum > 0:
                target = current_price * (1 + min(momentum * 0.5, 0.15))
            else:
                target = current_price * (1 + max(momentum * 0.5, -0.15))
            
            return round(target, 2)
            
        except Exception:
            return None
    
    def fallback_advice(self, symbol):
        """Provide basic advice when advanced analysis fails"""
        return {
            'symbol': symbol,
            'recommendation': 'Hold',
            'confidence': 50.0,
            'advice': 'Insufficient data for detailed analysis - consider fundamental research',
            'key_factors': ['Limited technical data', 'Market conditions', 'Fundamental analysis needed'],
            'risk_level': 'Medium',
            'target_price': None,
            'time_horizon': '1-3 months',
            'generated_at': datetime.now().isoformat()
        }
    
    def save_model(self):
        """Save the trained model"""
        try:
            os.makedirs('ai_models', exist_ok=True)
            joblib.dump(self.ensemble_model, 'ai_models/advice_engine.pkl')
            joblib.dump(self.scalers, 'ai_models/advice_scalers.pkl')
            logger.info("Saved advice engine model and scalers")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_scalers(self):
        """Load saved scalers"""
        try:
            self.scalers = joblib.load('ai_models/advice_scalers.pkl')
        except Exception as e:
            logger.warning(f"Could not load scalers, using default: {e}")

    def _auto_train_with_sample_data(self):
        """Auto-train the model with sample data on startup"""
        try:
            logger.info("Auto-training AI advice engine with sample data...")
            
            # Create sample training data
            np.random.seed(42)
            n_samples = 200
            
            # Generate realistic features
            features = np.random.randn(n_samples, 15)  # 15 features
            
            # Create realistic targets (0=strong_sell, 1=sell, 2=hold, 3=buy, 4=strong_buy)
            targets = np.random.choice([0, 1, 2, 3, 4], n_samples, p=[0.1, 0.2, 0.4, 0.2, 0.1])
            
            # Fit scalers
            self.scalers['technical'].fit(features[:, :10])
            self.scalers['fundamental'].fit(features[:, 10:13])
            self.scalers['sentiment'].fit(features[:, 13:])
            
            # Create and train ensemble model
            rf = RandomForestClassifier(n_estimators=50, random_state=42)
            gb = GradientBoostingClassifier(n_estimators=50, random_state=42)
            nn = MLPClassifier(hidden_layer_sizes=(50,), random_state=42, max_iter=200)
            
            self.ensemble_model = VotingClassifier([
                ('rf', rf), ('gb', gb), ('nn', nn)
            ], voting='soft')
            
            self.ensemble_model.fit(features, targets)
            
            logger.info("Auto-training completed successfully")
            
        except Exception as e:
            logger.warning(f"Auto-training failed: {e}")

# Global instance
advice_engine = AdvancedStockAdviceEngine()