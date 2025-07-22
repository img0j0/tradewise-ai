"""
Premium Features Module for TradeWise AI
Handles premium subscription features and access control
"""

from datetime import datetime, timedelta
from functools import wraps
import yfinance as yf
import pandas as pd
import numpy as np
from flask import jsonify, session
from models import User
import logging

logger = logging.getLogger(__name__)

def premium_required(f):
    """Decorator to check if user has active premium subscription"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Authentication required', 'premium_required': True}), 401
        
        user = User.query.get(user_id)
        if not user or not user.is_premium_active():
            return jsonify({
                'success': False, 
                'error': 'Premium subscription required',
                'premium_required': True,
                'upgrade_url': '/premium/upgrade'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

class PremiumFeatures:
    """Premium features implementation"""
    
    @staticmethod
    def get_portfolio_optimization_suggestions(portfolio_symbols, user_id=None):
        """
        AI-powered portfolio optimization suggestions
        Premium Feature: Advanced Portfolio Analysis
        """
        try:
            if not portfolio_symbols:
                return {
                    'suggestions': [],
                    'risk_score': 0,
                    'diversification_score': 0
                }
            
            # Fetch portfolio data
            portfolio_data = {}
            for symbol in portfolio_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='3mo')
                    info = ticker.info
                    
                    if not hist.empty:
                        portfolio_data[symbol] = {
                            'returns': hist['Close'].pct_change().dropna(),
                            'price': hist['Close'].iloc[-1],
                            'sector': info.get('sector', 'Unknown'),
                            'industry': info.get('industry', 'Unknown'),
                            'market_cap': info.get('marketCap', 0)
                        }
                except Exception as e:
                    logger.warning(f"Could not fetch data for {symbol}: {e}")
                    continue
            
            if not portfolio_data:
                return {'error': 'Unable to analyze portfolio'}
            
            # Calculate portfolio metrics
            returns_df = pd.DataFrame({symbol: data['returns'] for symbol, data in portfolio_data.items()})
            
            # Portfolio risk analysis
            correlation_matrix = returns_df.corr()
            risk_score = PremiumFeatures._calculate_portfolio_risk(correlation_matrix, returns_df)
            
            # Diversification analysis
            sectors = [data['sector'] for data in portfolio_data.values()]
            sector_distribution = pd.Series(sectors).value_counts()
            diversification_score = PremiumFeatures._calculate_diversification_score(sector_distribution)
            
            # Generate optimization suggestions
            suggestions = PremiumFeatures._generate_optimization_suggestions(
                portfolio_data, correlation_matrix, sector_distribution
            )
            
            return {
                'suggestions': suggestions,
                'risk_score': round(risk_score, 2),
                'diversification_score': round(diversification_score, 2),
                'correlation_analysis': correlation_matrix.to_dict(),
                'sector_allocation': sector_distribution.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Portfolio optimization error: {e}")
            return {'error': 'Portfolio analysis failed'}
    
    @staticmethod
    def _calculate_portfolio_risk(correlation_matrix, returns_df):
        """Calculate portfolio risk score (0-100, lower is better)"""
        try:
            # Calculate volatility
            volatilities = returns_df.std()
            avg_volatility = volatilities.mean()
            
            # Calculate correlation risk
            avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
            
            # Risk score combines volatility and correlation
            risk_score = (avg_volatility * 100 * 252**0.5) + (max(0, avg_correlation) * 50)
            return min(100, max(0, risk_score))
        except:
            return 50  # Default moderate risk
    
    @staticmethod
    def _calculate_diversification_score(sector_distribution):
        """Calculate diversification score (0-100, higher is better)"""
        try:
            total_stocks = sector_distribution.sum()
            if total_stocks <= 1:
                return 0
            
            # Calculate Shannon diversity index
            proportions = sector_distribution / total_stocks
            shannon_index = -sum(p * np.log(p) for p in proportions if p > 0)
            
            # Normalize to 0-100 scale
            max_possible_diversity = np.log(len(sector_distribution))
            if max_possible_diversity > 0:
                diversity_score = (shannon_index / max_possible_diversity) * 100
                return min(100, max(0, diversity_score))
            return 50
        except:
            return 50  # Default moderate diversification
    
    @staticmethod
    def _generate_optimization_suggestions(portfolio_data, correlation_matrix, sector_distribution):
        """Generate AI-powered portfolio optimization suggestions"""
        suggestions = []
        
        # Sector concentration check
        total_positions = len(portfolio_data)
        dominant_sector = sector_distribution.index[0] if len(sector_distribution) > 0 else None
        dominant_sector_count = sector_distribution.iloc[0] if len(sector_distribution) > 0 else 0
        
        if dominant_sector and dominant_sector_count / total_positions > 0.6:
            suggestions.append({
                'type': 'diversification',
                'priority': 'high',
                'title': f'Reduce {dominant_sector} Concentration',
                'description': f'Your portfolio is {dominant_sector_count/total_positions*100:.1f}% concentrated in {dominant_sector}. Consider diversifying into other sectors.',
                'icon': '⚠️'
            })
        
        # High correlation warning
        if len(portfolio_data) > 1:
            high_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.8:
                        high_correlations.append({
                            'stock1': correlation_matrix.columns[i],
                            'stock2': correlation_matrix.columns[j],
                            'correlation': corr_value
                        })
            
            if high_correlations:
                suggestions.append({
                    'type': 'correlation',
                    'priority': 'medium',
                    'title': 'High Correlation Risk Detected',
                    'description': f'Found {len(high_correlations)} highly correlated stock pairs. Consider reducing overlap.',
                    'icon': '📊',
                    'details': high_correlations[:3]  # Show top 3
                })
        
        # Small portfolio suggestion
        if total_positions < 5:
            suggestions.append({
                'type': 'size',
                'priority': 'medium',
                'title': 'Consider Adding More Positions',
                'description': f'Your portfolio has {total_positions} stocks. Consider 8-12 positions for better diversification.',
                'icon': '📈'
            })
        
        # If no major issues, provide positive feedback
        if not suggestions:
            suggestions.append({
                'type': 'positive',
                'priority': 'low',
                'title': 'Well-Diversified Portfolio',
                'description': 'Your portfolio shows good diversification across sectors and low correlation risk.',
                'icon': '✅'
            })
        
        return suggestions
    
    @staticmethod
    def get_ai_market_scanner():
        """
        Premium Feature: AI Market Scanner
        Daily AI-curated list of opportunities
        """
        try:
            # Popular stocks to analyze
            scan_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', 'AMZN', 'META', 'NFLX', 'AMD', 'CRM']
            
            opportunities = []
            
            for symbol in scan_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='1mo')
                    info = ticker.info
                    
                    if hist.empty:
                        continue
                    
                    current_price = hist['Close'].iloc[-1]
                    month_change = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                    
                    # Calculate RSI
                    rsi = PremiumFeatures._calculate_rsi(hist['Close'])
                    
                    # Volume analysis
                    avg_volume = hist['Volume'].mean()
                    recent_volume = hist['Volume'][-5:].mean()
                    volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
                    
                    # AI scoring logic
                    opportunity_score = 0
                    signals = []
                    
                    # Oversold opportunity
                    if rsi < 35:
                        opportunity_score += 3
                        signals.append("Oversold RSI")
                    
                    # High volume
                    if volume_ratio > 1.5:
                        opportunity_score += 2
                        signals.append("High Volume")
                    
                    # Recent decline
                    if -10 < month_change < -5:
                        opportunity_score += 2
                        signals.append("Recent Dip")
                    
                    # Strong rebound
                    if hist['Close'].iloc[-1] > hist['Close'].iloc[-5]:
                        week_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100
                        if week_change > 3:
                            opportunity_score += 3
                            signals.append("Rebound Signal")
                    
                    if opportunity_score >= 3:  # Threshold for inclusion
                        opportunities.append({
                            'symbol': symbol,
                            'name': info.get('longName', symbol),
                            'price': round(current_price, 2),
                            'change_1m': round(month_change, 2),
                            'rsi': round(rsi, 1),
                            'volume_ratio': round(volume_ratio, 2),
                            'opportunity_score': opportunity_score,
                            'signals': signals,
                            'market_cap': info.get('marketCap', 0)
                        })
                        
                except Exception as e:
                    logger.warning(f"Error scanning {symbol}: {e}")
                    continue
            
            # Sort by opportunity score
            opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
            
            return {
                'opportunities': opportunities[:10],  # Top 10
                'scan_date': datetime.now().isoformat(),
                'total_scanned': len(scan_symbols)
            }
            
        except Exception as e:
            logger.error(f"Market scanner error: {e}")
            return {'error': 'Market scan failed'}
    
    @staticmethod
    def _calculate_rsi(prices, period=14):
        """Calculate RSI (Relative Strength Index)"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1] if not rsi.empty else 50
        except:
            return 50  # Default neutral RSI
    
    @staticmethod
    def get_earnings_predictions(symbol):
        """
        Premium Feature: Earnings prediction engine
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get earnings data
            calendar = ticker.calendar
            earnings_dates = ticker.earnings_dates
            
            prediction = {
                'symbol': symbol,
                'next_earnings_date': None,
                'prediction': 'Hold',
                'confidence': 65,
                'factors': []
            }
            
            # Simple prediction logic based on recent performance
            hist = ticker.history(period='3mo')
            if not hist.empty:
                recent_trend = ((hist['Close'][-1] - hist['Close'][-30]) / hist['Close'][-30]) * 100
                
                if recent_trend > 10:
                    prediction['prediction'] = 'Beat'
                    prediction['confidence'] = 75
                    prediction['factors'].append('Strong recent performance')
                elif recent_trend < -10:
                    prediction['prediction'] = 'Miss'
                    prediction['confidence'] = 70
                    prediction['factors'].append('Weak recent performance')
                
                # Volume factor
                avg_volume = hist['Volume'].mean()
                recent_volume = hist['Volume'][-5:].mean()
                if recent_volume > avg_volume * 1.2:
                    prediction['factors'].append('Above average volume')
                    prediction['confidence'] += 5
            
            return prediction
            
        except Exception as e:
            logger.error(f"Earnings prediction error for {symbol}: {e}")
            return {'error': 'Earnings prediction failed'}