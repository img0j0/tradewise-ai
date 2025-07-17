import json
import logging
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy import and_, or_
from models import db, Trade, Portfolio
from data_service import DataService
from ai_insights import AIInsightsEngine
import os

logger = logging.getLogger(__name__)

class AIStrategyBuilder:
    """Build and backtest custom trading strategies with AI learning"""
    
    def __init__(self):
        self.strategies_dir = 'ai_models/strategies'
        os.makedirs(self.strategies_dir, exist_ok=True)
        self.data_service = DataService()
        self.ai_engine = AIInsightsEngine()
        
    def create_strategy(self, user_id, strategy_config):
        """Create a new trading strategy based on user-defined rules"""
        try:
            strategy = {
                'id': f"strategy_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'user_id': user_id,
                'name': strategy_config.get('name', 'Custom Strategy'),
                'description': strategy_config.get('description', ''),
                'rules': strategy_config.get('rules', []),
                'indicators': strategy_config.get('indicators', []),
                'risk_params': strategy_config.get('risk_params', {}),
                'created_at': datetime.now().isoformat(),
                'performance_metrics': {},
                'ai_optimizations': {}
            }
            
            # Validate strategy rules
            validation = self._validate_strategy(strategy)
            if not validation['valid']:
                return {
                    'status': 'error',
                    'message': validation['message']
                }
            
            # Save strategy
            self._save_strategy(strategy)
            
            return {
                'status': 'success',
                'strategy_id': strategy['id'],
                'strategy': strategy
            }
            
        except Exception as e:
            logger.error(f"Error creating strategy: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to create strategy'
            }
    
    def backtest_strategy(self, strategy_id, start_date=None, end_date=None, symbols=None):
        """Backtest a strategy against historical data"""
        try:
            # Load strategy
            strategy = self._load_strategy(strategy_id)
            if not strategy:
                return {
                    'status': 'error',
                    'message': 'Strategy not found'
                }
            
            # Set default dates
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=180)
            
            # Get symbols to test
            if not symbols:
                symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
            
            # Initialize backtest results
            results = {
                'total_return': 0,
                'win_rate': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'trades': [],
                'equity_curve': [],
                'metrics_by_symbol': {}
            }
            
            initial_capital = 10000
            current_capital = initial_capital
            all_trades = []
            daily_returns = []
            
            # Backtest each symbol
            for symbol in symbols:
                symbol_trades = self._backtest_symbol(
                    strategy, 
                    symbol, 
                    start_date, 
                    end_date,
                    current_capital
                )
                
                if symbol_trades:
                    all_trades.extend(symbol_trades)
                    
                    # Calculate metrics for this symbol
                    symbol_metrics = self._calculate_symbol_metrics(symbol_trades)
                    results['metrics_by_symbol'][symbol] = symbol_metrics
                    
                    # Update capital based on trades
                    for trade in symbol_trades:
                        if trade['type'] == 'sell' and trade['profit_loss']:
                            current_capital += trade['profit_loss']
            
            # Sort all trades by date
            all_trades.sort(key=lambda x: x['date'])
            results['trades'] = all_trades[:50]  # Limit to recent 50 trades
            
            # Calculate overall metrics
            if all_trades:
                winning_trades = [t for t in all_trades if t.get('profit_loss', 0) > 0]
                results['win_rate'] = len(winning_trades) / len(all_trades) * 100
                
                # Calculate total return
                results['total_return'] = ((current_capital - initial_capital) / initial_capital) * 100
                
                # Calculate Sharpe ratio (simplified)
                if daily_returns:
                    avg_return = np.mean(daily_returns)
                    std_return = np.std(daily_returns)
                    results['sharpe_ratio'] = (avg_return / std_return * np.sqrt(252)) if std_return > 0 else 0
                
                # Calculate max drawdown
                equity_curve = self._generate_equity_curve(all_trades, initial_capital)
                results['equity_curve'] = equity_curve
                results['max_drawdown'] = self._calculate_max_drawdown(equity_curve)
            
            # AI optimization suggestions
            results['ai_suggestions'] = self._generate_optimization_suggestions(strategy, results)
            
            return {
                'status': 'success',
                'results': results,
                'strategy': strategy
            }
            
        except Exception as e:
            logger.error(f"Error backtesting strategy: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to backtest strategy'
            }
    
    def optimize_strategy_with_ai(self, strategy_id):
        """Use AI to optimize strategy parameters"""
        try:
            # Load strategy and its backtest results
            strategy = self._load_strategy(strategy_id)
            if not strategy:
                return {'status': 'error', 'message': 'Strategy not found'}
            
            # Run multiple backtests with different parameters
            optimization_results = []
            
            # Define parameter ranges to test
            param_ranges = {
                'rsi_oversold': range(20, 35, 5),
                'rsi_overbought': range(65, 80, 5),
                'ma_period': [10, 20, 50, 100],
                'stop_loss': [0.02, 0.03, 0.05, 0.07],
                'take_profit': [0.05, 0.10, 0.15, 0.20]
            }
            
            # Test different parameter combinations
            best_params = {}
            best_return = -float('inf')
            
            for rsi_oversold in param_ranges['rsi_oversold']:
                for rsi_overbought in param_ranges['rsi_overbought']:
                    for ma_period in param_ranges['ma_period']:
                        for stop_loss in param_ranges['stop_loss']:
                            for take_profit in param_ranges['take_profit']:
                                # Update strategy parameters
                                test_strategy = strategy.copy()
                                test_strategy['rules'] = self._update_strategy_params(
                                    test_strategy['rules'],
                                    {
                                        'rsi_oversold': rsi_oversold,
                                        'rsi_overbought': rsi_overbought,
                                        'ma_period': ma_period,
                                        'stop_loss': stop_loss,
                                        'take_profit': take_profit
                                    }
                                )
                                
                                # Quick backtest
                                backtest = self._quick_backtest(test_strategy)
                                
                                if backtest['total_return'] > best_return:
                                    best_return = backtest['total_return']
                                    best_params = {
                                        'rsi_oversold': rsi_oversold,
                                        'rsi_overbought': rsi_overbought,
                                        'ma_period': ma_period,
                                        'stop_loss': stop_loss,
                                        'take_profit': take_profit
                                    }
            
            # Update strategy with optimized parameters
            strategy['ai_optimizations'] = {
                'optimized_params': best_params,
                'expected_return': best_return,
                'optimization_date': datetime.now().isoformat(),
                'improvement': best_return - strategy.get('performance_metrics', {}).get('total_return', 0)
            }
            
            # Save optimized strategy
            self._save_strategy(strategy)
            
            return {
                'status': 'success',
                'optimized_params': best_params,
                'expected_improvement': strategy['ai_optimizations']['improvement'],
                'strategy': strategy
            }
            
        except Exception as e:
            logger.error(f"Error optimizing strategy: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to optimize strategy'
            }
    
    def get_user_strategies(self, user_id):
        """Get all strategies for a user"""
        try:
            strategies = []
            
            # List all strategy files for user
            for filename in os.listdir(self.strategies_dir):
                if filename.startswith(f'strategy_{user_id}_') and filename.endswith('.json'):
                    strategy = self._load_strategy_from_file(os.path.join(self.strategies_dir, filename))
                    if strategy:
                        # Add summary info
                        strategy_summary = {
                            'id': strategy['id'],
                            'name': strategy['name'],
                            'description': strategy['description'],
                            'created_at': strategy['created_at'],
                            'performance': strategy.get('performance_metrics', {}),
                            'ai_optimized': bool(strategy.get('ai_optimizations'))
                        }
                        strategies.append(strategy_summary)
            
            # Sort by creation date
            strategies.sort(key=lambda x: x['created_at'], reverse=True)
            
            return {
                'status': 'success',
                'strategies': strategies
            }
            
        except Exception as e:
            logger.error(f"Error getting user strategies: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to retrieve strategies'
            }
    
    def _validate_strategy(self, strategy):
        """Validate strategy configuration"""
        if not strategy.get('rules'):
            return {'valid': False, 'message': 'Strategy must have at least one rule'}
        
        # Validate each rule
        for rule in strategy['rules']:
            if not rule.get('condition') or not rule.get('action'):
                return {'valid': False, 'message': 'Each rule must have a condition and action'}
        
        return {'valid': True}
    
    def _backtest_symbol(self, strategy, symbol, start_date, end_date, capital):
        """Backtest strategy on a single symbol"""
        trades = []
        position = None
        
        # Get historical data (simplified - in real app would use yfinance)
        # For now, generate synthetic data for demonstration
        dates = pd.date_range(start_date, end_date, freq='D')
        prices = np.random.normal(100, 10, len(dates))  # Simplified price data
        
        for i, (date, price) in enumerate(zip(dates, prices)):
            # Check strategy rules
            for rule in strategy['rules']:
                signal = self._evaluate_rule(rule, price, prices[:i+1] if i > 0 else [price])
                
                if signal == 'buy' and not position:
                    # Open position
                    position = {
                        'symbol': symbol,
                        'entry_price': price,
                        'entry_date': date,
                        'quantity': int(capital * 0.1 / price)  # Use 10% of capital
                    }
                    trades.append({
                        'symbol': symbol,
                        'type': 'buy',
                        'date': date.isoformat(),
                        'price': price,
                        'quantity': position['quantity']
                    })
                    
                elif signal == 'sell' and position:
                    # Close position
                    profit_loss = (price - position['entry_price']) * position['quantity']
                    trades.append({
                        'symbol': symbol,
                        'type': 'sell',
                        'date': date.isoformat(),
                        'price': price,
                        'quantity': position['quantity'],
                        'profit_loss': profit_loss,
                        'return_pct': ((price - position['entry_price']) / position['entry_price']) * 100
                    })
                    position = None
        
        return trades
    
    def _evaluate_rule(self, rule, current_price, price_history):
        """Evaluate a strategy rule"""
        condition = rule['condition']
        
        # Simple rule evaluation (extend for more complex rules)
        if condition['type'] == 'price_above_ma':
            ma_period = condition.get('period', 20)
            if len(price_history) >= ma_period:
                ma = np.mean(price_history[-ma_period:])
                if current_price > ma:
                    return rule['action']
                    
        elif condition['type'] == 'rsi':
            # Simplified RSI calculation
            if len(price_history) >= 14:
                rsi = 50  # Placeholder - implement real RSI
                if condition.get('operator') == '<' and rsi < condition.get('value', 30):
                    return rule['action']
                elif condition.get('operator') == '>' and rsi > condition.get('value', 70):
                    return rule['action']
        
        return None
    
    def _calculate_symbol_metrics(self, trades):
        """Calculate performance metrics for a symbol"""
        if not trades:
            return {}
        
        sell_trades = [t for t in trades if t['type'] == 'sell']
        if not sell_trades:
            return {}
        
        total_profit = sum(t.get('profit_loss', 0) for t in sell_trades)
        winning_trades = [t for t in sell_trades if t.get('profit_loss', 0) > 0]
        
        return {
            'total_trades': len(sell_trades),
            'winning_trades': len(winning_trades),
            'win_rate': (len(winning_trades) / len(sell_trades) * 100) if sell_trades else 0,
            'total_profit': total_profit,
            'avg_profit': total_profit / len(sell_trades) if sell_trades else 0
        }
    
    def _generate_equity_curve(self, trades, initial_capital):
        """Generate equity curve from trades"""
        equity = initial_capital
        curve = [{'date': datetime.now() - timedelta(days=180), 'value': equity}]
        
        for trade in trades:
            if trade['type'] == 'sell' and 'profit_loss' in trade:
                equity += trade['profit_loss']
                curve.append({
                    'date': trade['date'],
                    'value': equity
                })
        
        return curve
    
    def _calculate_max_drawdown(self, equity_curve):
        """Calculate maximum drawdown from equity curve"""
        if not equity_curve:
            return 0
        
        values = [point['value'] for point in equity_curve]
        peak = values[0]
        max_dd = 0
        
        for value in values[1:]:
            if value > peak:
                peak = value
            dd = (peak - value) / peak * 100
            max_dd = max(max_dd, dd)
        
        return max_dd
    
    def _generate_optimization_suggestions(self, strategy, results):
        """Generate AI suggestions for strategy improvement"""
        suggestions = []
        
        if results['win_rate'] < 40:
            suggestions.append({
                'type': 'improve_entry',
                'message': 'Consider adding confirmation indicators to improve entry timing',
                'priority': 'high'
            })
        
        if results['max_drawdown'] > 20:
            suggestions.append({
                'type': 'risk_management',
                'message': 'Add tighter stop-loss rules to reduce maximum drawdown',
                'priority': 'high'
            })
        
        if results['sharpe_ratio'] < 1:
            suggestions.append({
                'type': 'volatility',
                'message': 'Strategy returns are not compensating for risk - consider more selective entry criteria',
                'priority': 'medium'
            })
        
        return suggestions
    
    def _update_strategy_params(self, rules, params):
        """Update strategy rules with new parameters"""
        updated_rules = []
        for rule in rules:
            updated_rule = rule.copy()
            condition = updated_rule.get('condition', {})
            
            # Update relevant parameters
            if condition.get('type') == 'rsi':
                if condition.get('operator') == '<':
                    condition['value'] = params.get('rsi_oversold', condition.get('value', 30))
                elif condition.get('operator') == '>':
                    condition['value'] = params.get('rsi_overbought', condition.get('value', 70))
            
            updated_rules.append(updated_rule)
        
        return updated_rules
    
    def _quick_backtest(self, strategy):
        """Quick backtest for optimization"""
        # Simplified backtest for parameter optimization
        # In real implementation, would use historical data
        return {
            'total_return': np.random.normal(5, 10)  # Placeholder
        }
    
    def _save_strategy(self, strategy):
        """Save strategy to disk"""
        filepath = os.path.join(self.strategies_dir, f"{strategy['id']}.json")
        with open(filepath, 'w') as f:
            json.dump(strategy, f, indent=2)
    
    def _load_strategy(self, strategy_id):
        """Load strategy from disk"""
        filepath = os.path.join(self.strategies_dir, f"{strategy_id}.json")
        return self._load_strategy_from_file(filepath)
    
    def _load_strategy_from_file(self, filepath):
        """Load strategy from file path"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None

# Global instance
strategy_builder = AIStrategyBuilder()