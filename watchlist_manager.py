"""
Professional Watchlist Manager for TradeWise AI
Integrated with Bloomberg Killer Intelligence for real-time monitoring
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask_login import current_user
from app import db
from models import User
from bloomberg_killer_intelligence import bloomberg_killer
import yfinance as yf

logger = logging.getLogger(__name__)

class WatchlistManager:
    """Professional watchlist management with intelligent alerts"""
    
    def __init__(self):
        self.default_watchlists = {
            'My Portfolio': [],
            'Tech Giants': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],
            'AI & Innovation': ['NVDA', 'TSLA', 'CRM', 'NOW', 'PLTR'],
            'Market Indices': ['SPY', 'QQQ', 'IWM', 'VTI', 'DIA']
        }
        logger.info("Watchlist Manager initialized")
    
    def get_user_watchlists(self, user_id: str) -> Dict:
        """Get all watchlists for a user"""
        try:
            user = User.query.filter_by(id=user_id).first()
            
            if not user:
                return self._get_default_watchlists()
            
            # Get saved watchlists from user profile or use defaults
            watchlists = getattr(user, 'watchlists', None)
            if not watchlists:
                watchlists = self.default_watchlists.copy()
                # Save defaults to user
                self._save_user_watchlists(user_id, watchlists)
            
            # Add real-time data to watchlists
            enhanced_watchlists = {}
            for name, symbols in watchlists.items():
                enhanced_watchlists[name] = self._enhance_watchlist_data(symbols)
            
            return {
                'success': True,
                'watchlists': enhanced_watchlists,
                'total_symbols': sum(len(symbols) for symbols in watchlists.values()),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting watchlists for user {user_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def add_to_watchlist(self, user_id: str, watchlist_name: str, symbol: str) -> Dict:
        """Add symbol to specific watchlist"""
        try:
            # Get current watchlists
            result = self.get_user_watchlists(user_id)
            if not result['success']:
                return result
            
            watchlists = {name: [item['symbol'] for item in items] 
                         for name, items in result['watchlists'].items()}
            
            # Add symbol to watchlist
            if watchlist_name not in watchlists:
                watchlists[watchlist_name] = []
            
            if symbol.upper() not in watchlists[watchlist_name]:
                watchlists[watchlist_name].append(symbol.upper())
                
                # Save updated watchlists
                self._save_user_watchlists(user_id, watchlists)
                
                return {
                    'success': True,
                    'message': f'{symbol} added to {watchlist_name}',
                    'watchlist_count': len(watchlists[watchlist_name])
                }
            else:
                return {
                    'success': False,
                    'message': f'{symbol} already in {watchlist_name}'
                }
                
        except Exception as e:
            logger.error(f"Error adding {symbol} to watchlist: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def remove_from_watchlist(self, user_id: str, watchlist_name: str, symbol: str) -> Dict:
        """Remove symbol from watchlist"""
        try:
            result = self.get_user_watchlists(user_id)
            if not result['success']:
                return result
            
            watchlists = {name: [item['symbol'] for item in items] 
                         for name, items in result['watchlists'].items()}
            
            if watchlist_name in watchlists and symbol.upper() in watchlists[watchlist_name]:
                watchlists[watchlist_name].remove(symbol.upper())
                self._save_user_watchlists(user_id, watchlists)
                
                return {
                    'success': True,
                    'message': f'{symbol} removed from {watchlist_name}',
                    'watchlist_count': len(watchlists[watchlist_name])
                }
            else:
                return {
                    'success': False,
                    'message': f'{symbol} not found in {watchlist_name}'
                }
                
        except Exception as e:
            logger.error(f"Error removing {symbol} from watchlist: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_watchlist(self, user_id: str, watchlist_name: str) -> Dict:
        """Create new watchlist"""
        try:
            result = self.get_user_watchlists(user_id)
            if not result['success']:
                return result
            
            watchlists = {name: [item['symbol'] for item in items] 
                         for name, items in result['watchlists'].items()}
            
            if watchlist_name not in watchlists:
                watchlists[watchlist_name] = []
                self._save_user_watchlists(user_id, watchlists)
                
                return {
                    'success': True,
                    'message': f'Watchlist "{watchlist_name}" created',
                    'total_watchlists': len(watchlists)
                }
            else:
                return {
                    'success': False,
                    'message': f'Watchlist "{watchlist_name}" already exists'
                }
                
        except Exception as e:
            logger.error(f"Error creating watchlist: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_watchlist(self, user_id: str, watchlist_name: str) -> Dict:
        """Delete watchlist"""
        try:
            # Don't allow deletion of default watchlists
            if watchlist_name in ['My Portfolio', 'Tech Giants', 'AI & Innovation', 'Market Indices']:
                return {
                    'success': False,
                    'message': 'Cannot delete default watchlists'
                }
            
            result = self.get_user_watchlists(user_id)
            if not result['success']:
                return result
            
            watchlists = {name: [item['symbol'] for item in items] 
                         for name, items in result['watchlists'].items()}
            
            if watchlist_name in watchlists:
                del watchlists[watchlist_name]
                self._save_user_watchlists(user_id, watchlists)
                
                return {
                    'success': True,
                    'message': f'Watchlist "{watchlist_name}" deleted',
                    'total_watchlists': len(watchlists)
                }
            else:
                return {
                    'success': False,
                    'message': f'Watchlist "{watchlist_name}" not found'
                }
                
        except Exception as e:
            logger.error(f"Error deleting watchlist: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_watchlist_alerts(self, user_id: str) -> Dict:
        """Generate intelligent alerts for watchlist stocks"""
        try:
            result = self.get_user_watchlists(user_id)
            if not result['success']:
                return result
            
            alerts = []
            all_symbols = set()
            
            # Collect all symbols from all watchlists
            for watchlist_name, items in result['watchlists'].items():
                for item in items:
                    all_symbols.add(item['symbol'])
            
            # Generate alerts for each symbol
            for symbol in all_symbols:
                try:
                    analysis = bloomberg_killer.get_professional_analysis(symbol)
                    if 'error' in analysis:
                        continue
                    
                    # Generate intelligent alerts
                    symbol_alerts = self._generate_symbol_alerts(symbol, analysis)
                    alerts.extend(symbol_alerts)
                    
                except Exception as e:
                    logger.error(f"Error generating alerts for {symbol}: {str(e)}")
                    continue
            
            # Sort alerts by priority
            alerts.sort(key=lambda x: x['priority_score'], reverse=True)
            
            return {
                'success': True,
                'alerts': alerts[:20],  # Top 20 alerts
                'total_alerts': len(alerts),
                'symbols_monitored': len(all_symbols),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating watchlist alerts: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _enhance_watchlist_data(self, symbols: List[str]) -> List[Dict]:
        """Enhance watchlist symbols with real-time data"""
        enhanced_data = []
        
        for symbol in symbols:
            try:
                # Get basic stock data
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if not info or 'symbol' not in info:
                    continue
                
                # Get professional analysis
                analysis = bloomberg_killer.get_professional_analysis(symbol)
                
                enhanced_item = {
                    'symbol': symbol,
                    'company_name': info.get('longName', symbol),
                    'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                    'change_percent': info.get('regularMarketChangePercent', 0),
                    'volume': info.get('volume', info.get('regularMarketVolume', 0)),
                    'market_cap': info.get('marketCap', 0),
                    'sector': info.get('sector', 'Unknown')
                }
                
                # Add professional analysis if available
                if 'error' not in analysis:
                    enhanced_item.update({
                        'professional_rating': analysis['professional_rating']['overall_rating'],
                        'confidence': analysis['professional_rating']['confidence'],
                        'risk_level': analysis['risk_analysis']['risk_level'],
                        'momentum': analysis['momentum_analysis']['momentum_ranking'],
                        'unusual_volume': analysis['volume_intelligence']['unusual_volume']
                    })
                
                enhanced_data.append(enhanced_item)
                
            except Exception as e:
                logger.error(f"Error enhancing data for {symbol}: {str(e)}")
                # Add basic symbol info even if analysis fails
                enhanced_data.append({
                    'symbol': symbol,
                    'company_name': symbol,
                    'current_price': 0,
                    'change_percent': 0,
                    'error': str(e)
                })
        
        return enhanced_data
    
    def _generate_symbol_alerts(self, symbol: str, analysis: Dict) -> List[Dict]:
        """Generate intelligent alerts for a symbol based on analysis"""
        alerts = []
        
        try:
            # Price alerts
            price_data = analysis['price_data']
            if price_data['position_in_range'] > 95:
                alerts.append({
                    'symbol': symbol,
                    'type': 'BREAKOUT',
                    'message': f'{symbol} near 52-week high at {price_data["position_in_range"]:.1f}% of range',
                    'priority': 'HIGH',
                    'priority_score': 90,
                    'action': 'WATCH_BREAKOUT'
                })
            
            if price_data['position_in_range'] < 5:
                alerts.append({
                    'symbol': symbol,
                    'type': 'OVERSOLD',
                    'message': f'{symbol} near 52-week low at {price_data["position_in_range"]:.1f}% of range',
                    'priority': 'HIGH',
                    'priority_score': 85,
                    'action': 'CONSIDER_BUYING'
                })
            
            # Volume alerts
            if analysis['volume_intelligence']['unusual_volume']:
                alerts.append({
                    'symbol': symbol,
                    'type': 'VOLUME_SPIKE',
                    'message': f'{symbol} showing unusual volume activity',
                    'priority': 'MEDIUM',
                    'priority_score': 75,
                    'action': 'INVESTIGATE_NEWS'
                })
            
            # Rating alerts
            rating = analysis['professional_rating']['overall_rating']
            confidence = analysis['professional_rating']['confidence']
            
            if rating == 'STRONG BUY' and confidence > 0.8:
                alerts.append({
                    'symbol': symbol,
                    'type': 'STRONG_BUY',
                    'message': f'{symbol} rated STRONG BUY with {confidence*100:.0f}% confidence',
                    'priority': 'HIGH',
                    'priority_score': 95,
                    'action': 'CONSIDER_BUYING'
                })
            
            if rating == 'STRONG SELL' and confidence > 0.8:
                alerts.append({
                    'symbol': symbol,
                    'type': 'STRONG_SELL',
                    'message': f'{symbol} rated STRONG SELL with {confidence*100:.0f}% confidence',
                    'priority': 'HIGH',
                    'priority_score': 88,
                    'action': 'CONSIDER_SELLING'
                })
            
            # Risk alerts
            if analysis['risk_analysis']['risk_level'] == 'EXTREME':
                alerts.append({
                    'symbol': symbol,
                    'type': 'HIGH_RISK',
                    'message': f'{symbol} classified as EXTREME risk',
                    'priority': 'MEDIUM',
                    'priority_score': 70,
                    'action': 'REDUCE_POSITION'
                })
            
            # Technical alerts
            rsi = analysis['trading_metrics']['rsi']
            if rsi > 80:
                alerts.append({
                    'symbol': symbol,
                    'type': 'OVERBOUGHT',
                    'message': f'{symbol} RSI at {rsi:.1f} - potentially overbought',
                    'priority': 'MEDIUM',
                    'priority_score': 65,
                    'action': 'CONSIDER_SELLING'
                })
            elif rsi < 20:
                alerts.append({
                    'symbol': symbol,
                    'type': 'OVERSOLD_RSI',
                    'message': f'{symbol} RSI at {rsi:.1f} - potentially oversold',
                    'priority': 'MEDIUM',
                    'priority_score': 68,
                    'action': 'CONSIDER_BUYING'
                })
            
        except Exception as e:
            logger.error(f"Error generating alerts for {symbol}: {str(e)}")
        
        return alerts
    
    def _save_user_watchlists(self, user_id: str, watchlists: Dict):
        """Save watchlists to user profile"""
        try:
            user = User.query.filter_by(id=user_id).first()
            if user:
                # Store as JSON in user profile
                user.watchlists = json.dumps(watchlists)
                db.session.commit()
                
        except Exception as e:
            logger.error(f"Error saving watchlists for user {user_id}: {str(e)}")
    
    def _get_default_watchlists(self) -> Dict:
        """Get default watchlists for non-authenticated users"""
        enhanced_watchlists = {}
        for name, symbols in self.default_watchlists.items():
            enhanced_watchlists[name] = self._enhance_watchlist_data(symbols)
        
        return {
            'success': True,
            'watchlists': enhanced_watchlists,
            'total_symbols': sum(len(symbols) for symbols in self.default_watchlists.values()),
            'last_updated': datetime.now().isoformat()
        }

# Global instance
watchlist_manager = WatchlistManager()