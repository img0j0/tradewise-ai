"""
Preference Engine - Integrates user preferences with AI analysis and data display
"""

import json
import logging
from datetime import datetime
from models import User
from ai_insights import AIInsightsEngine
from flask_login import current_user

logger = logging.getLogger(__name__)

class PreferenceEngine:
    """Engine that applies user preferences to AI analysis and data display"""
    
    def __init__(self):
        self.default_preferences = {
            'risk_tolerance': 'moderate',
            'preferred_sectors': [],
            'analysis_depth': 'detailed',
            'display_currency': 'USD',
            'chart_type': 'candlestick',
            'time_horizon': 'medium',
            'notification_types': ['price_alerts', 'analysis_updates'],
            'market_hours_only': False,
            'show_technical_indicators': True,
            'confidence_threshold': 70
        }
    
    def get_user_preferences(self, user_id=None):
        """Get user preferences with fallback to defaults"""
        if not user_id and current_user and current_user.is_authenticated:
            user_id = current_user.id
            
        if user_id:
            user = User.query.get(user_id)
            if user and user.analysis_settings:
                try:
                    preferences = json.loads(user.analysis_settings)
                    # Merge with defaults to ensure all keys exist
                    merged = self.default_preferences.copy()
                    merged.update(preferences)
                    return merged
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in user {user_id} analysis_settings")
        
        # Check session for anonymous users
        from flask import session
        if 'user_preferences' in session:
            try:
                session_prefs = session['user_preferences']
                merged = self.default_preferences.copy()
                merged.update(session_prefs)
                return merged
            except Exception as e:
                logger.error(f"Error loading session preferences: {e}")
        
        return self.default_preferences.copy()
    
    def save_user_preferences(self, preferences, user_id=None):
        """Save user preferences to database or session"""
        try:
            if not user_id and current_user and current_user.is_authenticated:
                user_id = current_user.id
            
            if user_id:
                user = User.query.get(user_id)
                if user:
                    # Merge with existing preferences to avoid losing data
                    existing_prefs = self.get_user_preferences(user_id)
                    existing_prefs.update(preferences)
                    
                    # Save to database
                    user.analysis_settings = json.dumps(existing_prefs)
                    user.preferred_sectors = json.dumps(existing_prefs.get('preferred_sectors', []))
                    from app import db
                    db.session.commit()
                    logger.info(f"Preferences saved to database for user {user_id}")
                    return True
            else:
                # For anonymous users, save to session
                from flask import session
                existing_prefs = session.get('user_preferences', self.default_preferences.copy())
                existing_prefs.update(preferences)
                session['user_preferences'] = existing_prefs
                session.permanent = True
                logger.info("Preferences saved to session for anonymous user")
                return True
                
        except Exception as e:
            logger.error(f"Error saving user preferences: {e}")
            if user_id:
                from app import db
                db.session.rollback()
            
        return False
    
    def apply_risk_tolerance(self, analysis_result, risk_tolerance):
        """Adjust analysis based on user's risk tolerance"""
        if risk_tolerance == 'conservative':
            # Increase confidence threshold for buy recommendations
            if analysis_result.get('recommendation') in ['BUY', 'STRONG_BUY']:
                confidence = analysis_result.get('confidence', 0)
                if confidence < 80:
                    analysis_result['recommendation'] = 'HOLD'
                    analysis_result['risk_adjusted'] = True
                    analysis_result['risk_note'] = "Conservative risk setting - higher confidence required for BUY"
            
            # Lower position size suggestions
            if 'position_sizing' in analysis_result:
                analysis_result['position_sizing'] = min(analysis_result['position_sizing'], 5.0)
                
        elif risk_tolerance == 'aggressive':
            # Lower confidence threshold for buy recommendations
            if analysis_result.get('recommendation') == 'HOLD':
                confidence = analysis_result.get('confidence', 0)
                if confidence > 60:
                    analysis_result['recommendation'] = 'BUY'
                    analysis_result['risk_adjusted'] = True
                    analysis_result['risk_note'] = "Aggressive risk setting - accepting lower confidence threshold"
        
        return analysis_result
    
    def apply_sector_preferences(self, analysis_result, preferred_sectors, symbol):
        """Boost analysis for preferred sectors"""
        if not preferred_sectors:
            return analysis_result
            
        # Get sector for this stock (simplified mapping)
        sector_map = {
            'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'NVDA': 'Technology',
            'TSLA': 'Consumer Cyclical', 'AMD': 'Technology', 'META': 'Technology',
            'JPM': 'Financial Services', 'BAC': 'Financial Services', 'GS': 'Financial Services',
            'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'UNH': 'Healthcare',
            'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy'
        }
        
        stock_sector = sector_map.get(symbol, 'Other')
        
        if stock_sector in preferred_sectors:
            # Boost confidence for preferred sectors
            current_confidence = analysis_result.get('confidence', 50)
            analysis_result['confidence'] = min(95, current_confidence + 10)
            analysis_result['sector_boost'] = True
            analysis_result['sector_note'] = f"Preferred sector: {stock_sector}"
        
        return analysis_result
    
    def apply_time_horizon(self, analysis_result, time_horizon):
        """Adjust analysis based on investment time horizon"""
        if time_horizon == 'short':
            # Emphasize technical analysis for short-term
            if 'technical_score' in analysis_result:
                analysis_result['weighted_score'] = (analysis_result.get('technical_score', 0) * 0.7 + 
                                                   analysis_result.get('fundamental_score', 0) * 0.3)
            analysis_result['time_horizon_note'] = "Short-term focus: Technical analysis weighted higher"
            
        elif time_horizon == 'long':
            # Emphasize fundamental analysis for long-term
            if 'fundamental_score' in analysis_result:
                analysis_result['weighted_score'] = (analysis_result.get('fundamental_score', 0) * 0.7 + 
                                                   analysis_result.get('technical_score', 0) * 0.3)
            analysis_result['time_horizon_note'] = "Long-term focus: Fundamental analysis weighted higher"
        
        return analysis_result
    
    def apply_confidence_threshold(self, analysis_result, threshold):
        """Apply user's confidence threshold to recommendations"""
        current_confidence = analysis_result.get('confidence', 0)
        
        if current_confidence < threshold:
            if analysis_result.get('recommendation') in ['BUY', 'STRONG_BUY']:
                analysis_result['original_recommendation'] = analysis_result['recommendation']
                analysis_result['recommendation'] = 'HOLD'
                analysis_result['threshold_adjusted'] = True
                analysis_result['threshold_note'] = f"Confidence {current_confidence}% below your threshold of {threshold}%"
        
        return analysis_result
    
    def get_personalized_analysis(self, symbol, base_analysis, user_id=None):
        """Apply all user preferences to base analysis"""
        preferences = self.get_user_preferences(user_id)
        
        # Apply preference-based adjustments
        analysis = base_analysis.copy()
        
        # Apply risk tolerance
        analysis = self.apply_risk_tolerance(analysis, preferences['risk_tolerance'])
        
        # Apply sector preferences
        analysis = self.apply_sector_preferences(analysis, preferences['preferred_sectors'], symbol)
        
        # Apply time horizon
        analysis = self.apply_time_horizon(analysis, preferences['time_horizon'])
        
        # Apply confidence threshold
        analysis = self.apply_confidence_threshold(analysis, preferences['confidence_threshold'])
        
        # Add preference metadata
        analysis['preferences_applied'] = {
            'risk_tolerance': preferences['risk_tolerance'],
            'preferred_sectors': preferences['preferred_sectors'],
            'time_horizon': preferences['time_horizon'],
            'confidence_threshold': preferences['confidence_threshold']
        }
        
        # Log preference application
        logger.info(f"Applied preferences for user {user_id}: {symbol} - {analysis.get('recommendation')} "
                   f"(confidence: {analysis.get('confidence')}%)")
        
        return analysis
    
    def format_display_data(self, data, preferences):
        """Format data according to display preferences"""
        formatted = data.copy()
        
        # Currency formatting
        currency = preferences.get('display_currency', 'USD')
        currency_symbols = {'USD': '$', 'EUR': '€', 'GBP': '£'}
        symbol = currency_symbols.get(currency, '$')
        
        # Format price fields
        price_fields = ['current_price', 'target_price', 'stop_loss', 'market_cap']
        for field in price_fields:
            if field in formatted and formatted[field]:
                formatted[f'{field}_formatted'] = f"{symbol}{formatted[field]:,.2f}"
        
        # Chart type preference
        formatted['chart_type'] = preferences.get('chart_type', 'candlestick')
        
        # Technical indicators
        formatted['show_technical'] = preferences.get('show_technical_indicators', True)
        
        return formatted

# Global instance
preference_engine = PreferenceEngine()