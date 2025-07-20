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
            
            # Handle case where model only has one class
            if len(prob) == 1:
                confidence = 50.0  # Neutral confidence if only one class
            else:
                confidence = float(prob[1]) * 100  # Probability of positive class
            
            return int(min(max(confidence, 0), 100))  # Clamp between 0-100
            
        except Exception as e:
            logger.error(f"Error generating confidence score: {e}")
            return self._rule_based_confidence(stock_info)
    
    def _rule_based_confidence(self, stock_info):
        """Fallback rule-based confidence scoring"""
        score = 50  # Base score
        
        try:
            # Get values with defaults
            current_price = float(stock_info.get('current_price', 0))
            previous_close = float(stock_info.get('previous_close', current_price))
            
            # Price momentum
            if previous_close > 0:
                price_change_pct = ((current_price - previous_close) / previous_close) * 100
            else:
                price_change_pct = 0
            
            if price_change_pct > 5:
                score += 20
            elif price_change_pct > 2:
                score += 10
            elif price_change_pct < -5:
                score -= 20
            elif price_change_pct < -2:
                score -= 10
            
            # Volume analysis
            volume = float(stock_info.get('volume', 0))
            avg_volume = float(stock_info.get('avg_volume', 1))
            if avg_volume > 0:
                volume_ratio = volume / avg_volume
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
    
    def get_insights(self, symbol, stock_data):
        """Get comprehensive AI insights with intelligent market analysis"""
        try:
            # Enhanced intelligent analysis
            market_analysis = self._analyze_market_conditions(symbol, stock_data)
            fundamental_analysis = self._analyze_fundamentals(symbol, stock_data)
            technical_analysis = self._analyze_technical_indicators(symbol, stock_data)
            
            # Calculate intelligent confidence score (0-100)
            confidence_score = self._calculate_intelligent_confidence(
                market_analysis, fundamental_analysis, technical_analysis, stock_data
            )
            
            # Generate intelligent recommendation with reasoning
            recommendation = self._generate_intelligent_recommendation(
                market_analysis, fundamental_analysis, technical_analysis, confidence_score
            )
            
            # Return comprehensive insights
            return {
                'recommendation': recommendation['action'],
                'confidence': confidence_score,
                'risk_level': recommendation['risk_level'],
                'key_points': recommendation['key_points'],
                'ai_reasoning': recommendation['reasoning'],
                'investment_thesis': recommendation['thesis'],
                'price_target': recommendation['price_target'],
                'market_sentiment': market_analysis['sentiment'],
                'fundamental_score': fundamental_analysis['score'],
                'technical_score': technical_analysis['score'],
                'risk_factors': recommendation['risk_factors'],
                'catalyst_events': market_analysis['catalysts']
            }
            
        except Exception as e:
            logger.error(f"Error getting insights for {symbol}: {e}")
            return self._generate_enhanced_fallback_insights(symbol, stock_data)
    
    def _analyze_market_conditions(self, symbol, stock_data):
        """Analyze current market conditions and sentiment"""
        try:
            current_price = float(stock_data.get('current_price', 0))
            previous_close = float(stock_data.get('previous_close', current_price))
            volume = float(stock_data.get('volume', 0))
            avg_volume = float(stock_data.get('avg_volume', 1))
            
            # Price momentum analysis
            price_change = ((current_price - previous_close) / previous_close) * 100 if previous_close > 0 else 0
            
            # Volume analysis
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1
            
            # Market sentiment scoring
            sentiment_score = 50  # Neutral base
            if price_change > 3:
                sentiment_score += 25
            elif price_change > 1:
                sentiment_score += 15
            elif price_change < -3:
                sentiment_score -= 25
            elif price_change < -1:
                sentiment_score -= 15
                
            if volume_ratio > 1.5:
                sentiment_score += 10
            elif volume_ratio < 0.7:
                sentiment_score -= 5
            
            sentiment = "BULLISH" if sentiment_score > 65 else "BEARISH" if sentiment_score < 35 else "NEUTRAL"
            
            # Identify potential catalysts
            catalysts = []
            if volume_ratio > 2.0:
                catalysts.append("Unusual trading volume detected")
            if abs(price_change) > 5:
                catalysts.append("Significant price movement")
            if price_change > 0 and volume_ratio > 1.3:
                catalysts.append("Strong buying momentum")
            
            return {
                'sentiment': sentiment,
                'sentiment_score': min(max(sentiment_score, 0), 100),
                'price_momentum': price_change,
                'volume_activity': volume_ratio,
                'catalysts': catalysts,
                'sector_outlook': self._assess_sector_outlook(symbol)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market conditions: {e}")
            return {
                'sentiment': 'NEUTRAL',
                'sentiment_score': 50,
                'price_momentum': 0,
                'volume_activity': 1,
                'catalysts': [],
                'sector_outlook': 'NEUTRAL'
            }
    
    def _analyze_fundamentals(self, symbol, stock_data):
        """Analyze fundamental factors"""
        try:
            market_cap = float(stock_data.get('market_cap', 0))
            current_price = float(stock_data.get('current_price', 0))
            
            score = 50  # Base fundamental score
            
            # Market cap analysis
            if market_cap > 100_000_000_000:  # Large cap (>100B)
                score += 15
            elif market_cap > 10_000_000_000:  # Mid cap (10-100B)
                score += 10
            elif market_cap > 1_000_000_000:  # Small cap (1-10B)
                score += 5
            else:  # Micro cap (<1B)
                score -= 5
            
            # Price level analysis
            if 20 <= current_price <= 500:  # Sweet spot for institutional interest
                score += 10
            elif current_price < 5:  # Penny stock risk
                score -= 15
            elif current_price > 1000:  # High price may limit accessibility
                score -= 5
            
            return {
                'score': min(max(score, 0), 100),
                'market_cap_tier': self._get_market_cap_tier(market_cap),
                'valuation_assessment': self._assess_valuation(stock_data),
                'growth_potential': self._assess_growth_potential(stock_data)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing fundamentals: {e}")
            return {
                'score': 50,
                'market_cap_tier': 'Unknown',
                'valuation_assessment': 'Neutral',
                'growth_potential': 'Moderate'
            }
    
    def _analyze_technical_indicators(self, symbol, stock_data):
        """Analyze technical indicators"""
        try:
            current_price = float(stock_data.get('current_price', 0))
            moving_avg_20 = float(stock_data.get('moving_avg_20', current_price))
            day_high = float(stock_data.get('day_high', current_price))
            day_low = float(stock_data.get('day_low', current_price))
            
            score = 50  # Base technical score
            
            # Moving average analysis
            ma_ratio = current_price / moving_avg_20 if moving_avg_20 > 0 else 1
            if ma_ratio > 1.05:
                score += 20
            elif ma_ratio > 1.02:
                score += 10
            elif ma_ratio < 0.95:
                score -= 20
            elif ma_ratio < 0.98:
                score -= 10
            
            # Intraday momentum
            if day_high > day_low:
                day_range = (day_high - day_low) / day_low * 100
                position_in_range = (current_price - day_low) / (day_high - day_low) * 100
                
                if position_in_range > 80:  # Near daily high
                    score += 15
                elif position_in_range > 60:
                    score += 5
                elif position_in_range < 20:  # Near daily low
                    score -= 15
                elif position_in_range < 40:
                    score -= 5
            
            # Volatility assessment
            volatility = self._calculate_volatility(stock_data)
            trend = "UPTREND" if ma_ratio > 1.02 else "DOWNTREND" if ma_ratio < 0.98 else "SIDEWAYS"
            
            return {
                'score': min(max(score, 0), 100),
                'trend': trend,
                'volatility': volatility,
                'momentum': self._assess_momentum(stock_data),
                'support_resistance': self._identify_support_resistance(stock_data)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing technical indicators: {e}")
            return {
                'score': 50,
                'trend': 'NEUTRAL',
                'volatility': 'MODERATE',
                'momentum': 'NEUTRAL',
                'support_resistance': {'support': 0, 'resistance': 0}
            }
    
    def _calculate_intelligent_confidence(self, market_analysis, fundamental_analysis, technical_analysis, stock_data):
        """Calculate intelligent confidence score based on multiple factors"""
        try:
            # Weight different analysis components
            market_weight = 0.4
            fundamental_weight = 0.3
            technical_weight = 0.3
            
            # Get scores
            market_score = market_analysis['sentiment_score']
            fundamental_score = fundamental_analysis['score']
            technical_score = technical_analysis['score']
            
            # Calculate weighted confidence
            confidence = (
                market_score * market_weight +
                fundamental_score * fundamental_weight +
                technical_score * technical_weight
            )
            
            # Adjust for data quality and volume
            volume_ratio = float(stock_data.get('volume', 0)) / float(stock_data.get('avg_volume', 1))
            if volume_ratio > 1.5:
                confidence += 5  # High volume increases confidence
            elif volume_ratio < 0.5:
                confidence -= 10  # Low volume decreases confidence
            
            return int(min(max(confidence, 0), 100))
            
        except Exception as e:
            logger.error(f"Error calculating intelligent confidence: {e}")
            return 50
    
    def _generate_intelligent_recommendation(self, market_analysis, fundamental_analysis, technical_analysis, confidence):
        """Generate intelligent recommendation with detailed reasoning"""
        try:
            # Determine action based on scores and confidence
            action = "HOLD"
            risk_level = "MEDIUM"
            
            if confidence >= 75:
                if market_analysis['sentiment'] == 'BULLISH' and technical_analysis['trend'] == 'UPTREND':
                    action = "STRONG BUY"
                    risk_level = "LOW"
                elif market_analysis['sentiment'] == 'BULLISH':
                    action = "BUY"
                    risk_level = "LOW"
            elif confidence >= 60:
                if market_analysis['sentiment'] == 'BULLISH':
                    action = "BUY"
                    risk_level = "MEDIUM"
                elif market_analysis['sentiment'] == 'BEARISH':
                    action = "SELL"
                    risk_level = "MEDIUM"
            elif confidence <= 25:
                action = "STRONG SELL"
                risk_level = "HIGH"
            elif confidence <= 40:
                action = "SELL"
                risk_level = "HIGH"
            
            # Generate key points
            key_points = []
            if market_analysis['price_momentum'] > 2:
                key_points.append(f"Strong upward momentum (+{market_analysis['price_momentum']:.1f}%)")
            elif market_analysis['price_momentum'] < -2:
                key_points.append(f"Downward pressure ({market_analysis['price_momentum']:.1f}%)")
            
            if market_analysis['volume_activity'] > 1.5:
                key_points.append("Above-average trading volume")
            
            if technical_analysis['trend'] != 'SIDEWAYS':
                key_points.append(f"Technical trend: {technical_analysis['trend'].lower()}")
            
            # Generate reasoning
            reasoning = self._generate_ai_reasoning(market_analysis, fundamental_analysis, technical_analysis, confidence)
            
            # Generate investment thesis
            thesis = self._generate_investment_thesis(market_analysis, fundamental_analysis, technical_analysis, action)
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(market_analysis, fundamental_analysis, technical_analysis)
            
            # Calculate price target
            price_target = self._calculate_intelligent_price_target(market_analysis, technical_analysis, confidence)
            
            return {
                'action': action,
                'risk_level': risk_level,
                'key_points': key_points,
                'reasoning': reasoning,
                'thesis': thesis,
                'risk_factors': risk_factors,
                'price_target': price_target
            }
            
        except Exception as e:
            logger.error(f"Error generating intelligent recommendation: {e}")
            return {
                'action': 'HOLD',
                'risk_level': 'MEDIUM',
                'key_points': ['Analysis pending'],
                'reasoning': 'AI analysis temporarily unavailable',
                'thesis': 'Market data under review',
                'risk_factors': ['General market risk'],
                'price_target': 'TBD'
            }
    
    def _generate_enhanced_fallback_insights(self, symbol, stock_data=None):
        """Generate enhanced fallback insights when main analysis fails"""
        return {
            'recommendation': 'HOLD',
            'confidence': 50,
            'risk_level': 'MEDIUM',
            'key_points': ['Analysis in progress', 'Market data updating'],
            'ai_reasoning': f'AI analysis for {symbol} is currently processing market data and will provide enhanced insights shortly.',
            'investment_thesis': 'Awaiting comprehensive market analysis',
            'price_target': 'Under analysis',
            'market_sentiment': 'NEUTRAL',
            'fundamental_score': 50,
            'technical_score': 50,
            'risk_factors': ['Market volatility', 'Data processing delay'],
            'catalyst_events': []
        }
    
    # Helper methods for detailed analysis
    def _assess_sector_outlook(self, symbol):
        """Assess sector outlook based on symbol"""
        tech_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA']
        if symbol in tech_symbols:
            return 'POSITIVE'
        return 'NEUTRAL'
    
    def _get_market_cap_tier(self, market_cap):
        """Get market cap tier classification"""
        if market_cap > 100_000_000_000:
            return 'Large Cap'
        elif market_cap > 10_000_000_000:
            return 'Mid Cap'
        elif market_cap > 1_000_000_000:
            return 'Small Cap'
        else:
            return 'Micro Cap'
    
    def _assess_valuation(self, stock_data):
        """Assess valuation level"""
        return 'Fair Value'  # Simplified for now
    
    def _assess_growth_potential(self, stock_data):
        """Assess growth potential"""
        return 'Moderate'  # Simplified for now
    
    def _calculate_volatility(self, stock_data):
        """Calculate volatility assessment"""
        day_high = float(stock_data.get('day_high', 0))
        day_low = float(stock_data.get('day_low', 0))
        current_price = float(stock_data.get('current_price', 1))
        
        if day_high > day_low and current_price > 0:
            daily_range = (day_high - day_low) / current_price * 100
            if daily_range > 5:
                return 'HIGH'
            elif daily_range > 2:
                return 'MODERATE'
            else:
                return 'LOW'
        return 'MODERATE'
    
    def _assess_momentum(self, stock_data):
        """Assess price momentum"""
        current_price = float(stock_data.get('current_price', 0))
        previous_close = float(stock_data.get('previous_close', current_price))
        
        if previous_close > 0:
            change_pct = ((current_price - previous_close) / previous_close) * 100
            if change_pct > 2:
                return 'STRONG POSITIVE'
            elif change_pct > 0.5:
                return 'POSITIVE'
            elif change_pct < -2:
                return 'STRONG NEGATIVE'
            elif change_pct < -0.5:
                return 'NEGATIVE'
        return 'NEUTRAL'
    
    def _identify_support_resistance(self, stock_data):
        """Identify support and resistance levels"""
        current_price = float(stock_data.get('current_price', 0))
        day_high = float(stock_data.get('day_high', current_price))
        day_low = float(stock_data.get('day_low', current_price))
        
        return {
            'support': day_low,
            'resistance': day_high
        }
    
    def _generate_ai_reasoning(self, market_analysis, fundamental_analysis, technical_analysis, confidence):
        """Generate AI reasoning explanation"""
        reasoning = f"AI confidence: {confidence}%. "
        
        if market_analysis['sentiment'] == 'BULLISH':
            reasoning += "Market sentiment is bullish with positive price momentum. "
        elif market_analysis['sentiment'] == 'BEARISH':
            reasoning += "Market sentiment shows bearish pressure. "
        
        if technical_analysis['trend'] == 'UPTREND':
            reasoning += "Technical indicators confirm upward trend. "
        elif technical_analysis['trend'] == 'DOWNTREND':
            reasoning += "Technical indicators suggest downward trend. "
        
        if fundamental_analysis['score'] > 60:
            reasoning += "Fundamental analysis shows positive outlook."
        elif fundamental_analysis['score'] < 40:
            reasoning += "Fundamental factors present some concerns."
        
        return reasoning
    
    def _generate_investment_thesis(self, market_analysis, fundamental_analysis, technical_analysis, action):
        """Generate investment thesis"""
        if action in ['STRONG BUY', 'BUY']:
            return "Strong fundamentals combined with positive technical momentum create compelling investment opportunity."
        elif action in ['STRONG SELL', 'SELL']:
            return "Current market conditions and technical indicators suggest caution warranted."
        else:
            return "Mixed signals recommend maintaining current position while monitoring developments."
    
    def _identify_risk_factors(self, market_analysis, fundamental_analysis, technical_analysis):
        """Identify key risk factors"""
        risks = []
        
        if market_analysis['sentiment'] == 'BEARISH':
            risks.append("Negative market sentiment")
        
        if technical_analysis['volatility'] == 'HIGH':
            risks.append("High price volatility")
        
        if market_analysis['volume_activity'] < 0.5:
            risks.append("Low trading volume")
        
        if fundamental_analysis['market_cap_tier'] == 'Micro Cap':
            risks.append("Small company risk")
        
        if not risks:
            risks.append("General market risk")
        
        return risks
    
    def _calculate_intelligent_price_target(self, market_analysis, technical_analysis, confidence):
        """Calculate intelligent price target"""
        if confidence > 70:
            if market_analysis['sentiment'] == 'BULLISH':
                return f"+{confidence//10}% upside potential"
            else:
                return "Fair value range"
        elif confidence < 30:
            return f"-{(100-confidence)//10}% downside risk"
        else:
            return "Current levels appropriate"
