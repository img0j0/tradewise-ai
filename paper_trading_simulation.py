#!/usr/bin/env python3
"""
Paper Trading Simulation System
Comprehensive testing of all trading platform features with realistic market scenarios
"""

import sys
import os
import time
import json
import random
from datetime import datetime, timedelta
from decimal import Decimal
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, Trade, Portfolio, Alert, UserAccount, Transaction
from ai_insights import AIInsightsEngine
try:
    from personalized_ai import PersonalizedAIAssistant
except ImportError:
    PersonalizedAIAssistant = None
try:
    from strategy_builder import StrategyBuilder
except ImportError:
    StrategyBuilder = None
try:
    from gamification import GamificationEngine
except ImportError:
    GamificationEngine = None
try:
    from portfolio_optimizer import PortfolioOptimizer
except ImportError:
    PortfolioOptimizer = None
from stock_search import StockSearchService
from technical_indicators import TechnicalIndicators
import yfinance as yf

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PaperTradingSimulation:
    def __init__(self, initial_balance=100000):
        """Initialize paper trading simulation with comprehensive testing"""
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.positions = {}
        self.trade_history = []
        self.ai_engine = AIInsightsEngine()
        self.personalized_ai = PersonalizedAIAssistant() if PersonalizedAIAssistant else None
        self.strategy_builder = StrategyBuilder() if StrategyBuilder else None
        self.gamification = GamificationEngine() if GamificationEngine else None
        self.portfolio_optimizer = PortfolioOptimizer() if PortfolioOptimizer else None
        self.technical_indicators = TechnicalIndicators()
        self.stock_search = StockSearchService()
        
        # Test symbols for simulation
        self.test_symbols = [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 
            'META', 'NVDA', 'NFLX', 'AMD', 'BABA'
        ]
        
        # Simulation parameters
        self.simulation_days = 30
        self.daily_trades = 3
        self.risk_tolerance = 0.02  # 2% risk per trade
        
        logger.info(f"Initialized paper trading simulation with ${initial_balance:,.2f}")
        
    def run_comprehensive_simulation(self):
        """Run full simulation testing all platform features"""
        logger.info("Starting comprehensive trading simulation...")
        
        # Initialize user account for simulation
        self.setup_simulation_account()
        
        # Test 1: AI-Powered Stock Analysis
        logger.info("=== Testing AI-Powered Stock Analysis ===")
        self.test_ai_analysis()
        
        # Test 2: Technical Indicators and Charting
        logger.info("=== Testing Technical Indicators ===")
        self.test_technical_indicators()
        
        # Test 3: Strategy Building and Backtesting
        logger.info("=== Testing Strategy Builder ===")
        self.test_strategy_building()
        
        # Test 4: Portfolio Optimization
        logger.info("=== Testing Portfolio Optimization ===")
        self.test_portfolio_optimization()
        
        # Test 5: Real Trading Simulation
        logger.info("=== Running Trading Simulation ===")
        self.run_trading_simulation()
        
        # Test 6: Personalized AI Learning
        logger.info("=== Testing Personalized AI ===")
        self.test_personalized_ai()
        
        # Test 7: Gamification Features
        logger.info("=== Testing Gamification ===")
        self.test_gamification_features()
        
        # Generate comprehensive report
        self.generate_simulation_report()
        
    def setup_simulation_account(self):
        """Setup simulation user account"""
        try:
            # Create or get simulation user account
            account = UserAccount.query.filter_by(user_id=1).first()
            if not account:
                account = UserAccount(
                    user_id=1,
                    balance=self.initial_balance,
                    total_deposited=self.initial_balance,
                    total_withdrawn=0
                )
                db.session.add(account)
                db.session.commit()
            else:
                account.balance = self.initial_balance
                db.session.commit()
                
            logger.info(f"Simulation account setup with balance: ${account.balance:,.2f}")
            return account
            
        except Exception as e:
            logger.error(f"Error setting up simulation account: {e}")
            return None
    
    def test_ai_analysis(self):
        """Test AI-powered stock analysis capabilities"""
        results = {}
        
        for symbol in self.test_symbols[:5]:  # Test top 5 stocks
            try:
                # Get AI insights
                insights = self.ai_engine.get_insights(symbol)
                
                # Test personalized recommendations
                personal_rec = self.personalized_ai.get_personalized_recommendations(1)
                
                results[symbol] = {
                    'ai_insights': insights,
                    'confidence_score': insights.get('confidence_score', 0),
                    'recommendation': insights.get('recommendation', 'HOLD'),
                    'risk_assessment': insights.get('risk_assessment', {}),
                    'personalized_score': personal_rec.get('recommendations', [{}])[0].get('score', 0) if personal_rec.get('recommendations') else 0
                }
                
                logger.info(f"{symbol}: AI Recommendation: {results[symbol]['recommendation']}, "
                           f"Confidence: {results[symbol]['confidence_score']:.1f}%")
                
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                results[symbol] = {'error': str(e)}
        
        self.ai_analysis_results = results
        return results
    
    def test_technical_indicators(self):
        """Test technical indicators calculation"""
        indicators_results = {}
        
        for symbol in self.test_symbols[:3]:  # Test top 3 stocks
            try:
                # Get stock data
                stock_data = self.stock_search.search_stock(symbol)
                if not stock_data:
                    continue
                
                # Calculate technical indicators
                indicators = self.technical_indicators.calculate_all_indicators(symbol, period='1mo')
                
                indicators_results[symbol] = {
                    'current_price': stock_data.get('current_price', 0),
                    'sma_20': indicators.get('sma_20', [])[-1] if indicators.get('sma_20') else 0,
                    'rsi': indicators.get('rsi', [])[-1] if indicators.get('rsi') else 0,
                    'macd': indicators.get('macd', {}).get('macd', [])[-1] if indicators.get('macd', {}).get('macd') else 0,
                    'bollinger_bands': indicators.get('bollinger_bands', {}),
                    'volume_trend': 'bullish' if indicators.get('volume', [])[-1] > indicators.get('volume', [])[-2] else 'bearish' if len(indicators.get('volume', [])) > 1 else 'neutral'
                }
                
                logger.info(f"{symbol}: Price: ${indicators_results[symbol]['current_price']:.2f}, "
                           f"RSI: {indicators_results[symbol]['rsi']:.1f}, "
                           f"SMA20: ${indicators_results[symbol]['sma_20']:.2f}")
                
            except Exception as e:
                logger.error(f"Error calculating indicators for {symbol}: {e}")
                indicators_results[symbol] = {'error': str(e)}
        
        self.technical_results = indicators_results
        return indicators_results
    
    def test_strategy_building(self):
        """Test strategy building and backtesting"""
        if not self.strategy_builder:
            logger.warning("Strategy builder not available - skipping test")
            return {'error': 'Strategy builder not available'}
        
        strategy_results = {}
        
        try:
            # Create a simple momentum strategy
            strategy_config = {
                'name': 'Momentum Strategy',
                'rules': [
                    {'type': 'technical', 'indicator': 'RSI', 'condition': 'below', 'value': 30, 'action': 'buy'},
                    {'type': 'technical', 'indicator': 'RSI', 'condition': 'above', 'value': 70, 'action': 'sell'},
                    {'type': 'price', 'condition': 'above', 'indicator': 'SMA', 'period': 20, 'action': 'buy_signal'}
                ],
                'risk_management': {
                    'stop_loss': 0.05,
                    'take_profit': 0.10,
                    'position_size': 0.1
                }
            }
            
            # Test strategy creation
            strategy = self.strategy_builder.create_strategy(1, strategy_config)
            logger.info(f"Created strategy: {strategy.get('name', 'Unknown')}")
            
            # Test backtesting
            backtest_results = self.strategy_builder.backtest_strategy(
                strategy.get('id', 1), 
                'AAPL', 
                days=90
            )
            
            strategy_results = {
                'strategy_id': strategy.get('id', 1),
                'backtest_results': backtest_results,
                'total_return': backtest_results.get('total_return', 0),
                'win_rate': backtest_results.get('win_rate', 0),
                'sharpe_ratio': backtest_results.get('sharpe_ratio', 0),
                'max_drawdown': backtest_results.get('max_drawdown', 0)
            }
            
            logger.info(f"Strategy backtest - Return: {strategy_results['total_return']:.2%}, "
                       f"Win Rate: {strategy_results['win_rate']:.1%}, "
                       f"Sharpe: {strategy_results['sharpe_ratio']:.2f}")
            
        except Exception as e:
            logger.error(f"Error in strategy testing: {e}")
            strategy_results = {'error': str(e)}
        
        self.strategy_results = strategy_results
        return strategy_results
    
    def test_portfolio_optimization(self):
        """Test portfolio optimization features"""
        if not self.portfolio_optimizer:
            logger.warning("Portfolio optimizer not available - skipping test")
            return {'error': 'Portfolio optimizer not available'}
        
        optimization_results = {}
        
        try:
            # Create sample portfolio
            portfolio_data = []
            for i, symbol in enumerate(self.test_symbols[:5]):
                stock_data = self.stock_search.search_stock(symbol)
                if stock_data:
                    portfolio_data.append({
                        'symbol': symbol,
                        'quantity': 100 * (i + 1),
                        'current_price': stock_data.get('current_price', 100),
                        'avg_price': stock_data.get('current_price', 100) * 0.95  # Assume 5% profit
                    })
            
            # Test portfolio optimization
            optimized = self.portfolio_optimizer.optimize_portfolio(portfolio_data, target_return=0.12)
            
            optimization_results = {
                'original_portfolio': portfolio_data,
                'optimized_weights': optimized.get('weights', {}),
                'expected_return': optimized.get('expected_return', 0),
                'expected_volatility': optimized.get('expected_volatility', 0),
                'sharpe_ratio': optimized.get('sharpe_ratio', 0),
                'recommendations': optimized.get('recommendations', [])
            }
            
            logger.info(f"Portfolio optimization - Expected Return: {optimization_results['expected_return']:.2%}, "
                       f"Volatility: {optimization_results['expected_volatility']:.2%}, "
                       f"Sharpe: {optimization_results['sharpe_ratio']:.2f}")
            
        except Exception as e:
            logger.error(f"Error in portfolio optimization: {e}")
            optimization_results = {'error': str(e)}
        
        self.optimization_results = optimization_results
        return optimization_results
    
    def run_trading_simulation(self):
        """Run realistic trading simulation"""
        simulation_results = {
            'trades': [],
            'daily_performance': [],
            'final_balance': self.current_balance,
            'total_return': 0,
            'winning_trades': 0,
            'losing_trades': 0
        }
        
        start_date = datetime.now() - timedelta(days=self.simulation_days)
        
        for day in range(self.simulation_days):
            current_date = start_date + timedelta(days=day)
            daily_pnl = 0
            
            # Simulate daily trading
            for _ in range(self.daily_trades):
                trade_result = self.simulate_trade(current_date)
                if trade_result:
                    simulation_results['trades'].append(trade_result)
                    daily_pnl += trade_result.get('pnl', 0)
                    
                    if trade_result.get('pnl', 0) > 0:
                        simulation_results['winning_trades'] += 1
                    else:
                        simulation_results['losing_trades'] += 1
            
            # Update portfolio values
            portfolio_value = self.calculate_portfolio_value()
            simulation_results['daily_performance'].append({
                'date': current_date.strftime('%Y-%m-%d'),
                'portfolio_value': portfolio_value,
                'daily_pnl': daily_pnl,
                'cash_balance': self.current_balance
            })
            
            # Log progress every 5 days
            if day % 5 == 0:
                logger.info(f"Day {day}: Portfolio Value: ${portfolio_value:,.2f}, "
                           f"Daily P&L: ${daily_pnl:,.2f}")
        
        # Calculate final results
        final_value = self.calculate_portfolio_value()
        simulation_results['final_balance'] = final_value
        simulation_results['total_return'] = (final_value - self.initial_balance) / self.initial_balance
        simulation_results['win_rate'] = (simulation_results['winning_trades'] / 
                                        max(1, simulation_results['winning_trades'] + simulation_results['losing_trades']))
        
        logger.info(f"Trading simulation completed - Final Value: ${final_value:,.2f}, "
                   f"Total Return: {simulation_results['total_return']:.2%}, "
                   f"Win Rate: {simulation_results['win_rate']:.1%}")
        
        self.simulation_results = simulation_results
        return simulation_results
    
    def simulate_trade(self, date):
        """Simulate a single trade with AI recommendations"""
        try:
            # Select random stock
            symbol = random.choice(self.test_symbols)
            
            # Get AI recommendation
            insights = self.ai_engine.get_insights(symbol)
            recommendation = insights.get('recommendation', 'HOLD')
            confidence = insights.get('confidence_score', 50)
            
            # Skip if confidence is too low
            if confidence < 60:
                return None
            
            # Get stock data
            stock_data = self.stock_search.search_stock(symbol)
            if not stock_data:
                return None
            
            current_price = stock_data.get('current_price', 0)
            if current_price <= 0:
                return None
            
            # Determine trade parameters
            if recommendation == 'BUY':
                action = 'buy'
                # Calculate position size based on risk tolerance
                position_value = self.current_balance * self.risk_tolerance
                quantity = int(position_value / current_price)
                
                if quantity > 0 and self.current_balance >= quantity * current_price:
                    # Execute buy
                    cost = quantity * current_price
                    self.current_balance -= cost
                    
                    if symbol in self.positions:
                        self.positions[symbol]['quantity'] += quantity
                        self.positions[symbol]['avg_price'] = (
                            (self.positions[symbol]['avg_price'] * self.positions[symbol]['quantity'] + cost) /
                            (self.positions[symbol]['quantity'] + quantity)
                        )
                    else:
                        self.positions[symbol] = {
                            'quantity': quantity,
                            'avg_price': current_price
                        }
                    
                    # Simulate price movement (random walk with slight bias)
                    price_change = random.normalvariate(0.001, 0.02)  # 0.1% mean, 2% std
                    new_price = current_price * (1 + price_change)
                    pnl = quantity * (new_price - current_price)
                    
                    return {
                        'date': date.strftime('%Y-%m-%d'),
                        'symbol': symbol,
                        'action': action,
                        'quantity': quantity,
                        'price': current_price,
                        'new_price': new_price,
                        'pnl': pnl,
                        'confidence': confidence,
                        'ai_recommendation': recommendation
                    }
            
            elif recommendation == 'SELL' and symbol in self.positions:
                # Execute sell
                quantity = self.positions[symbol]['quantity']
                if quantity > 0:
                    # Simulate price movement
                    price_change = random.normalvariate(-0.001, 0.02)  # Slight negative bias for sells
                    new_price = current_price * (1 + price_change)
                    
                    revenue = quantity * new_price
                    cost = quantity * self.positions[symbol]['avg_price']
                    pnl = revenue - cost
                    
                    self.current_balance += revenue
                    del self.positions[symbol]
                    
                    return {
                        'date': date.strftime('%Y-%m-%d'),
                        'symbol': symbol,
                        'action': 'sell',
                        'quantity': quantity,
                        'price': current_price,
                        'new_price': new_price,
                        'pnl': pnl,
                        'confidence': confidence,
                        'ai_recommendation': recommendation
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error simulating trade: {e}")
            return None
    
    def calculate_portfolio_value(self):
        """Calculate current portfolio value"""
        total_value = self.current_balance
        
        for symbol, position in self.positions.items():
            try:
                stock_data = self.stock_search.search_stock(symbol)
                if stock_data:
                    current_price = stock_data.get('current_price', position['avg_price'])
                    total_value += position['quantity'] * current_price
            except:
                # Use average price if current price unavailable
                total_value += position['quantity'] * position['avg_price']
        
        return total_value
    
    def test_personalized_ai(self):
        """Test personalized AI learning capabilities"""
        if not self.personalized_ai:
            logger.warning("Personalized AI not available - skipping test")
            return {'error': 'Personalized AI not available'}
        
        try:
            # Test learning from user trades
            patterns = self.personalized_ai.learn_from_user_trades(1)
            
            # Get personalized recommendations
            recommendations = self.personalized_ai.get_personalized_recommendations(1)
            
            personalized_results = {
                'learning_status': patterns.get('status', 'success'),
                'recommendations': recommendations,
                'risk_tolerance': patterns.get('risk_tolerance', 'medium'),
                'preferred_sectors': dict(patterns.get('preferred_sectors', {})),
                'avg_holding_period': patterns.get('avg_holding_period', 0)
            }
            
            logger.info(f"Personalized AI - Learning Status: {personalized_results['learning_status']}, "
                       f"Risk Tolerance: {personalized_results['risk_tolerance']}")
            
            self.personalized_results = personalized_results
            return personalized_results
            
        except Exception as e:
            logger.error(f"Error in personalized AI testing: {e}")
            return {'error': str(e)}
    
    def test_gamification_features(self):
        """Test gamification system"""
        if not self.gamification:
            logger.warning("Gamification system not available - skipping test")
            return {'error': 'Gamification system not available'}
        
        try:
            # Get user stats
            user_stats = self.gamification.get_user_stats(1)
            
            # Get achievements
            achievements = self.gamification.get_user_achievements(1)
            
            # Test leaderboard
            leaderboard = self.gamification.get_leaderboard('all')
            
            gamification_results = {
                'user_stats': user_stats,
                'achievements': achievements,
                'leaderboard_position': next((i for i, user in enumerate(leaderboard) if user.get('user_id') == 1), None),
                'total_points': user_stats.get('total_points', 0),
                'level': user_stats.get('level', 1),
                'badges_earned': len(achievements)
            }
            
            logger.info(f"Gamification - Level: {gamification_results['level']}, "
                       f"Points: {gamification_results['total_points']}, "
                       f"Badges: {gamification_results['badges_earned']}")
            
            self.gamification_results = gamification_results
            return gamification_results
            
        except Exception as e:
            logger.error(f"Error in gamification testing: {e}")
            return {'error': str(e)}
    
    def generate_simulation_report(self):
        """Generate comprehensive simulation report"""
        report = {
            'simulation_overview': {
                'initial_balance': self.initial_balance,
                'final_value': getattr(self, 'simulation_results', {}).get('final_balance', self.initial_balance),
                'total_return': getattr(self, 'simulation_results', {}).get('total_return', 0),
                'simulation_days': self.simulation_days,
                'total_trades': len(getattr(self, 'simulation_results', {}).get('trades', [])),
                'win_rate': getattr(self, 'simulation_results', {}).get('win_rate', 0)
            },
            'ai_analysis': getattr(self, 'ai_analysis_results', {}),
            'technical_indicators': getattr(self, 'technical_results', {}),
            'strategy_performance': getattr(self, 'strategy_results', {}),
            'portfolio_optimization': getattr(self, 'optimization_results', {}),
            'personalized_ai': getattr(self, 'personalized_results', {}),
            'gamification': getattr(self, 'gamification_results', {}),
            'trading_simulation': getattr(self, 'simulation_results', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save report
        with open('simulation_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        logger.info("\n" + "="*80)
        logger.info("COMPREHENSIVE SIMULATION REPORT")
        logger.info("="*80)
        
        overview = report['simulation_overview']
        logger.info(f"Initial Balance: ${overview['initial_balance']:,.2f}")
        logger.info(f"Final Value: ${overview['final_value']:,.2f}")
        logger.info(f"Total Return: {overview['total_return']:.2%}")
        logger.info(f"Total Trades: {overview['total_trades']}")
        logger.info(f"Win Rate: {overview['win_rate']:.1%}")
        
        # AI Analysis Summary
        ai_success = len([r for r in report['ai_analysis'].values() if 'error' not in r])
        logger.info(f"AI Analysis: {ai_success}/{len(report['ai_analysis'])} stocks analyzed successfully")
        
        # Technical Indicators Summary
        tech_success = len([r for r in report['technical_indicators'].values() if 'error' not in r])
        logger.info(f"Technical Indicators: {tech_success}/{len(report['technical_indicators'])} stocks analyzed")
        
        # Strategy Performance
        if 'error' not in report['strategy_performance']:
            strategy = report['strategy_performance']
            logger.info(f"Strategy Backtest: {strategy.get('total_return', 0):.2%} return, "
                       f"{strategy.get('win_rate', 0):.1%} win rate")
        
        # Portfolio Optimization
        if 'error' not in report['portfolio_optimization']:
            opt = report['portfolio_optimization']
            logger.info(f"Portfolio Optimization: {opt.get('expected_return', 0):.2%} expected return, "
                       f"{opt.get('sharpe_ratio', 0):.2f} Sharpe ratio")
        
        # Gamification
        if 'error' not in report['gamification']:
            game = report['gamification']
            logger.info(f"Gamification: Level {game.get('level', 1)}, "
                       f"{game.get('total_points', 0)} points, "
                       f"{game.get('badges_earned', 0)} badges")
        
        logger.info("="*80)
        logger.info("Report saved to: simulation_report.json")
        logger.info("="*80)
        
        return report

def main():
    """Main function to run the simulation"""
    logger.info("Starting Paper Trading Simulation...")
    
    # Initialize simulation
    sim = PaperTradingSimulation(initial_balance=100000)
    
    # Run comprehensive simulation
    sim.run_comprehensive_simulation()
    
    logger.info("Simulation completed successfully!")

if __name__ == "__main__":
    main()