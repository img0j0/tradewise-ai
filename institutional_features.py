"""
Institutional-Grade Trading Features
Advanced order management, risk controls, and market data access
"""

import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)

class SmartOrderRouter:
    """
    Professional Smart Order Routing (SOR) system
    Finds best execution across multiple venues
    """
    
    def __init__(self):
        self.venues = {
            'NYSE': {'fee': 0.0005, 'liquidity': 0.9, 'speed': 0.8},
            'NASDAQ': {'fee': 0.0003, 'liquidity': 0.95, 'speed': 0.9},
            'ARCA': {'fee': 0.0002, 'liquidity': 0.7, 'speed': 0.95},
            'BATS': {'fee': 0.0001, 'liquidity': 0.6, 'speed': 0.85},
            'IEX': {'fee': 0.0000, 'liquidity': 0.5, 'speed': 0.7}
        }
    
    def analyze_execution(self, symbol: str, quantity: int, order_type: str = 'market') -> Dict:
        """Find optimal venue for trade execution"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Calculate market impact based on volume
            avg_volume = info.get('averageVolume', 1000000)
            market_impact = min(quantity / avg_volume * 0.1, 0.05)  # Max 5% impact
            
            # Score each venue
            venue_scores = {}
            for venue, metrics in self.venues.items():
                # Weighted score: liquidity (40%), speed (35%), fees (25%)
                score = (metrics['liquidity'] * 0.4 + 
                        metrics['speed'] * 0.35 + 
                        (1 - metrics['fee']) * 0.25)
                
                # Adjust for market impact
                adjusted_score = score * (1 - market_impact)
                venue_scores[venue] = adjusted_score
            
            # Find best venue
            best_venue = max(venue_scores, key=venue_scores.get)
            best_score = venue_scores[best_venue]
            
            return {
                'recommended_venue': best_venue,
                'execution_score': round(best_score, 3),
                'estimated_fee': self.venues[best_venue]['fee'] * quantity,
                'market_impact': round(market_impact * 100, 2),
                'all_venues': venue_scores
            }
            
        except Exception as e:
            logger.error(f"SOR error for {symbol}: {e}")
            return {
                'recommended_venue': 'NASDAQ',
                'execution_score': 0.8,
                'estimated_fee': 0.0,
                'market_impact': 0.1,
                'error': str(e)
            }

class AdvancedOrderManager:
    """
    Professional order types and execution algorithms
    """
    
    def __init__(self):
        self.sor = SmartOrderRouter()
    
    def create_stop_loss_order(self, symbol: str, quantity: int, stop_price: float, 
                              current_price: float) -> Dict:
        """Create stop-loss order with smart execution"""
        try:
            # Calculate optimal stop distance
            stock = yf.Ticker(symbol)
            hist = stock.history(period='30d')
            volatility = hist['Close'].pct_change().std() * np.sqrt(252)
            
            # Recommend stop distance based on volatility
            recommended_stop = current_price * (1 - volatility * 0.5)
            
            # Get execution recommendation
            execution_plan = self.sor.find_best_execution(symbol, quantity, 'stop')
            
            return {
                'order_type': 'stop_loss',
                'symbol': symbol,
                'quantity': quantity,
                'stop_price': stop_price,
                'current_price': current_price,
                'recommended_stop': round(recommended_stop, 2),
                'volatility': round(volatility * 100, 2),
                'execution_plan': execution_plan,
                'risk_reward_ratio': round((current_price - stop_price) / current_price * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"Stop loss order error: {e}")
            return {'error': str(e)}
    
    def create_bracket_order(self, symbol: str, quantity: int, entry_price: float,
                            stop_loss: float, take_profit: float) -> Dict:
        """Create bracket order (entry + stop + profit target)"""
        try:
            # Calculate risk metrics
            risk_amount = abs(entry_price - stop_loss)
            reward_amount = abs(take_profit - entry_price)
            risk_reward = reward_amount / risk_amount if risk_amount > 0 else 0
            
            # Get execution plans for each leg
            entry_plan = self.sor.find_best_execution(symbol, quantity, 'limit')
            
            return {
                'order_type': 'bracket',
                'symbol': symbol,
                'quantity': quantity,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_reward_ratio': round(risk_reward, 2),
                'risk_amount': round(risk_amount, 2),
                'reward_amount': round(reward_amount, 2),
                'execution_plan': entry_plan,
                'recommendation': 'GOOD' if risk_reward >= 2.0 else 'REVIEW'
            }
            
        except Exception as e:
            logger.error(f"Bracket order error: {e}")
            return {'error': str(e)}

class Level2MarketData:
    """
    Professional Level 2 market data and order book analysis
    """
    
    def get_order_book(self, symbol: str) -> Dict:
        """Simulate Level 2 order book data"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 100))
            
            # Simulate order book depth
            spread = current_price * 0.001  # 0.1% spread
            bid_price = current_price - spread/2
            ask_price = current_price + spread/2
            
            # Generate realistic order book levels
            order_book = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'current_price': round(current_price, 2),
                'bid_ask_spread': round(spread, 4),
                'spread_percentage': round(spread/current_price * 100, 3),
                'bids': [],
                'asks': []
            }
            
            # Generate bid levels
            for i in range(10):
                price = bid_price - (i * spread * 0.1)
                size = np.random.randint(100, 5000)
                order_book['bids'].append({
                    'price': round(price, 2),
                    'size': size,
                    'orders': np.random.randint(1, 10)
                })
            
            # Generate ask levels  
            for i in range(10):
                price = ask_price + (i * spread * 0.1)
                size = np.random.randint(100, 5000)
                order_book['asks'].append({
                    'price': round(price, 2),
                    'size': size,
                    'orders': np.random.randint(1, 10)
                })
            
            # Calculate market depth metrics
            total_bid_size = sum(level['size'] for level in order_book['bids'][:5])
            total_ask_size = sum(level['size'] for level in order_book['asks'][:5])
            
            order_book['market_depth'] = {
                'bid_depth_5': total_bid_size,
                'ask_depth_5': total_ask_size,
                'imbalance': round((total_bid_size - total_ask_size) / (total_bid_size + total_ask_size) * 100, 2),
                'liquidity_score': min(total_bid_size + total_ask_size, 50000) / 50000
            }
            
            return order_book
            
        except Exception as e:
            logger.error(f"Level 2 data error for {symbol}: {e}")
            return {'error': str(e)}

class OptionsFlowAnalyzer:
    """
    Professional options flow analysis and unusual activity detection
    """
    
    def analyze_unusual_activity(self, symbol: str) -> Dict:
        """Analyze options flow for unusual activity"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 100))
            
            # Simulate options flow data
            flow_data = {
                'symbol': symbol,
                'current_price': current_price,
                'timestamp': datetime.now().isoformat(),
                'unusual_activity': [],
                'flow_summary': {
                    'total_volume': 0,
                    'call_volume': 0,
                    'put_volume': 0,
                    'call_put_ratio': 0,
                    'bullish_flow': 0,
                    'bearish_flow': 0
                }
            }
            
            # Generate unusual options activity
            strikes = [current_price * (1 + i*0.05) for i in range(-4, 5)]
            expirations = [(datetime.now() + timedelta(days=d)).strftime('%Y-%m-%d') 
                          for d in [7, 14, 21, 35, 49]]
            
            for _ in range(np.random.randint(3, 8)):
                strike = np.random.choice(strikes)
                expiration = np.random.choice(expirations)
                option_type = np.random.choice(['CALL', 'PUT'])
                volume = np.random.randint(500, 5000)
                premium = np.random.uniform(0.5, 10.0)
                
                # Determine if unusual (high volume, high premium)
                is_unusual = volume > 2000 or premium > 5.0
                
                if is_unusual:
                    flow_data['unusual_activity'].append({
                        'strike': round(strike, 2),
                        'expiration': expiration,
                        'type': option_type,
                        'volume': volume,
                        'premium': round(premium, 2),
                        'unusual_score': min(volume / 1000 + premium, 10),
                        'sentiment': 'BULLISH' if option_type == 'CALL' else 'BEARISH'
                    })
                
                # Update flow summary
                flow_data['flow_summary']['total_volume'] += volume
                if option_type == 'CALL':
                    flow_data['flow_summary']['call_volume'] += volume
                    flow_data['flow_summary']['bullish_flow'] += volume * premium
                else:
                    flow_data['flow_summary']['put_volume'] += volume
                    flow_data['flow_summary']['bearish_flow'] += volume * premium
            
            # Calculate ratios
            total_vol = flow_data['flow_summary']['total_volume']
            if total_vol > 0:
                call_vol = flow_data['flow_summary']['call_volume']
                flow_data['flow_summary']['call_put_ratio'] = round(
                    call_vol / (total_vol - call_vol) if total_vol > call_vol else 0, 2
                )
            
            # Sort by unusual score
            flow_data['unusual_activity'].sort(key=lambda x: x['unusual_score'], reverse=True)
            
            return flow_data
            
        except Exception as e:
            logger.error(f"Options flow error for {symbol}: {e}")
            return {'error': str(e)}

class RiskManagementSystem:
    """
    Professional risk management and portfolio controls
    """
    
    def calculate_portfolio_risk(self, positions: List[Dict]) -> Dict:
        """Calculate comprehensive portfolio risk metrics"""
        try:
            if not positions:
                return {'error': 'No positions provided'}
            
            total_value = sum(pos.get('market_value', 0) for pos in positions)
            
            # Calculate Value at Risk (VaR)
            portfolio_volatility = 0
            position_weights = []
            
            for position in positions:
                weight = position.get('market_value', 0) / total_value if total_value > 0 else 0
                position_weights.append(weight)
                
                # Get stock volatility
                try:
                    stock = yf.Ticker(position['symbol'])
                    hist = stock.history(period='90d')
                    vol = hist['Close'].pct_change().std() * np.sqrt(252)
                    portfolio_volatility += (weight ** 2) * (vol ** 2)
                except:
                    portfolio_volatility += (weight ** 2) * (0.3 ** 2)  # Default 30% vol
            
            portfolio_volatility = np.sqrt(portfolio_volatility)
            
            # Calculate VaR (95% confidence, 1-day horizon)
            var_95 = total_value * portfolio_volatility * 1.645 / np.sqrt(252)
            
            # Calculate position concentration
            max_position = max(position_weights) if position_weights else 0
            concentration_risk = 'HIGH' if max_position > 0.25 else 'MEDIUM' if max_position > 0.15 else 'LOW'
            
            # Sector analysis
            sectors = {}
            for position in positions:
                sector = position.get('sector', 'Unknown')
                sectors[sector] = sectors.get(sector, 0) + position.get('market_value', 0)
            
            sector_concentration = max(sectors.values()) / total_value if total_value > 0 else 0
            
            return {
                'portfolio_value': round(total_value, 2),
                'portfolio_volatility': round(portfolio_volatility * 100, 2),
                'var_95_1day': round(var_95, 2),
                'var_percentage': round(var_95 / total_value * 100, 2) if total_value > 0 else 0,
                'max_position_weight': round(max_position * 100, 2),
                'concentration_risk': concentration_risk,
                'sector_concentration': round(sector_concentration * 100, 2),
                'number_of_positions': len(positions),
                'diversification_score': min(len(positions) / 10, 1) * (1 - max_position),
                'sectors': sectors
            }
            
        except Exception as e:
            logger.error(f"Portfolio risk calculation error: {e}")
            return {'error': str(e)}
    
    def kelly_criterion_sizing(self, win_rate: float, avg_win: float, avg_loss: float,
                              account_balance: float) -> Dict:
        """Calculate optimal position size using Kelly Criterion"""
        try:
            if avg_loss <= 0:
                return {'error': 'Average loss must be positive'}
            
            # Kelly formula: f = (bp - q) / b
            # where: b = avg_win/avg_loss, p = win_rate, q = 1-win_rate
            b = avg_win / avg_loss
            p = win_rate
            q = 1 - win_rate
            
            kelly_fraction = (b * p - q) / b
            
            # Apply safety factor (typically 25-50% of Kelly)
            safe_kelly = kelly_fraction * 0.25  # Conservative 25%
            moderate_kelly = kelly_fraction * 0.50  # Moderate 50%
            
            # Calculate position sizes
            conservative_size = account_balance * safe_kelly
            moderate_size = account_balance * moderate_kelly
            full_kelly_size = account_balance * kelly_fraction
            
            return {
                'kelly_fraction': round(kelly_fraction, 4),
                'conservative_size': max(0, round(conservative_size, 2)),
                'moderate_size': max(0, round(moderate_size, 2)),
                'full_kelly_size': max(0, round(full_kelly_size, 2)),
                'recommendation': 'conservative_size',  # Always recommend conservative
                'win_rate': round(win_rate * 100, 2),
                'risk_reward': round(avg_win / avg_loss, 2),
                'expected_value': round((win_rate * avg_win) - ((1-win_rate) * avg_loss), 2)
            }
            
        except Exception as e:
            logger.error(f"Kelly criterion error: {e}")
            return {'error': str(e)}

# Initialize institutional features
institutional_features = {
    'smart_order_router': SmartOrderRouter(),
    'advanced_orders': AdvancedOrderManager(),
    'level2_data': Level2MarketData(),
    'options_flow': OptionsFlowAnalyzer(),
    'risk_management': RiskManagementSystem()
}