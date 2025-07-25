"""
Portfolio Backtesting Engine
Provides comprehensive portfolio backtesting with performance metrics and visualizations
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from functools import lru_cache
import json
from flask import session

logger = logging.getLogger(__name__)

class PortfolioBacktestingEngine:
    def __init__(self):
        
        # Risk-free rate (10-year Treasury average)
        self.risk_free_rate = 0.04
        
        # Benchmark symbols
        self.benchmarks = {
            'SPY': 'S&P 500',
            'QQQ': 'NASDAQ 100',
            'VTI': 'Total Stock Market',
            'IWM': 'Russell 2000'
        }

    def run_backtest(self, portfolio_data, strategy_params=None, benchmark='SPY'):
        """Run comprehensive portfolio backtest"""
        try:
            # Validate inputs
            if not portfolio_data or not isinstance(portfolio_data, list):
                return {
                    'success': False,
                    'error': 'Invalid portfolio data provided'
                }
            
            # Parse portfolio
            portfolio = self._parse_portfolio(portfolio_data)
            if not portfolio:
                return {
                    'success': False,
                    'error': 'Unable to parse portfolio data'
                }
            
            # Set default strategy parameters
            if not strategy_params:
                strategy_params = {
                    'start_date': '2023-01-01',
                    'end_date': datetime.now().strftime('%Y-%m-%d'),
                    'initial_capital': 100000,
                    'rebalancing_frequency': 'monthly',  # daily, weekly, monthly, quarterly
                    'strategy_type': 'buy_and_hold'  # buy_and_hold, momentum, mean_reversion
                }
            
            # Download historical data
            price_data = self._get_historical_data(portfolio, strategy_params)
            if price_data.empty:
                return {
                    'success': False,
                    'error': 'Unable to retrieve historical price data'
                }
            
            # Run backtest simulation
            backtest_results = self._simulate_backtest(portfolio, price_data, strategy_params)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(backtest_results, strategy_params)
            
            # Get benchmark comparison
            benchmark_data = self._get_benchmark_performance(benchmark, strategy_params)
            
            # Generate visualization data
            chart_data = self._generate_chart_data(backtest_results, benchmark_data)
            
            return {
                'success': True,
                'portfolio': portfolio,
                'strategy_params': strategy_params,
                'performance_metrics': performance_metrics,
                'benchmark_comparison': benchmark_data,
                'chart_data': chart_data,
                'analysis_insights': self._generate_insights(performance_metrics, benchmark_data),
                'backtest_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Backtest error: {e}")
            return {
                'success': False,
                'error': 'Backtesting service temporarily unavailable',
                'details': str(e)
            }

    def _parse_portfolio(self, portfolio_data):
        """Parse and validate portfolio data"""
        try:
            portfolio = {}
            total_weight = 0
            
            for holding in portfolio_data:
                symbol = holding.get('symbol', '').upper()
                weight = float(holding.get('weight', 0))
                
                if symbol and weight > 0:
                    portfolio[symbol] = weight
                    total_weight += weight
            
            # Normalize weights to sum to 100%
            if total_weight > 0:
                for symbol in portfolio:
                    portfolio[symbol] = portfolio[symbol] / total_weight
            
            return portfolio if portfolio else None
            
        except Exception as e:
            logger.error(f"Portfolio parsing error: {e}")
            return None

    def _get_historical_data(self, portfolio, strategy_params):
        """Get historical price data for portfolio"""
        try:
            symbols = list(portfolio.keys())
            
            start_date = strategy_params.get('start_date', '2023-01-01')
            end_date = strategy_params.get('end_date', datetime.now().strftime('%Y-%m-%d'))
            
            # Download data for all symbols
            data = yf.download(symbols, start=start_date, end=end_date, group_by='ticker')
            
            if len(symbols) == 1:
                # Single stock - reformat data
                symbol = symbols[0]
                if not data.empty:
                    data = pd.DataFrame({symbol: data['Adj Close']})
            else:
                # Multiple stocks - extract adjusted close prices
                price_data = pd.DataFrame()
                for symbol in symbols:
                    if symbol in data.columns.levels[0]:
                        price_data[symbol] = data[symbol]['Adj Close']
                    else:
                        logger.warning(f"No data available for {symbol}")
                data = price_data
            
            # Forward fill missing values
            data = data.ffill().dropna()
            
            return data
            
        except Exception as e:
            logger.error(f"Data download error: {e}")
            return pd.DataFrame()

    def _simulate_backtest(self, portfolio, price_data, strategy_params):
        """Simulate portfolio backtest"""
        try:
            initial_capital = strategy_params.get('initial_capital', 100000)
            rebalancing_freq = strategy_params.get('rebalancing_frequency', 'monthly')
            strategy_type = strategy_params.get('strategy_type', 'buy_and_hold')
            
            # Initialize portfolio value tracking
            portfolio_values = []
            holdings = {}
            cash = initial_capital
            
            # Calculate rebalancing dates
            rebalancing_dates = self._get_rebalancing_dates(price_data.index, rebalancing_freq)
            
            for date in price_data.index:
                is_rebalancing_date = date in rebalancing_dates
                
                if is_rebalancing_date or not holdings:
                    # Rebalance portfolio
                    total_value = cash + sum(holdings.get(symbol, 0) * price_data.loc[date, symbol] 
                                           for symbol in portfolio if symbol in price_data.columns)
                    
                    # Apply strategy adjustments
                    adjusted_weights = self._apply_strategy(portfolio, price_data, date, strategy_type)
                    
                    # Update holdings
                    holdings = {}
                    for symbol, weight in adjusted_weights.items():
                        if symbol in price_data.columns:
                            target_value = total_value * weight
                            price = price_data.loc[date, symbol]
                            if pd.notna(price) and price > 0:
                                holdings[symbol] = target_value / price
                    
                    cash = 0  # Assume fully invested
                
                # Calculate portfolio value
                portfolio_value = sum(holdings.get(symbol, 0) * price_data.loc[date, symbol] 
                                    for symbol in portfolio if symbol in price_data.columns)
                
                portfolio_values.append({
                    'date': date,
                    'portfolio_value': portfolio_value,
                    'holdings': holdings.copy()
                })
            
            return pd.DataFrame(portfolio_values).set_index('date')
            
        except Exception as e:
            logger.error(f"Backtest simulation error: {e}")
            return pd.DataFrame()

    def _get_rebalancing_dates(self, date_range, frequency):
        """Get rebalancing dates based on frequency"""
        try:
            rebalancing_dates = set()
            
            if frequency == 'daily':
                return set(date_range)
            elif frequency == 'weekly':
                # Every Monday
                for date in date_range:
                    if date.weekday() == 0:  # Monday
                        rebalancing_dates.add(date)
            elif frequency == 'monthly':
                # First trading day of each month
                current_month = None
                for date in date_range:
                    if current_month != date.month:
                        rebalancing_dates.add(date)
                        current_month = date.month
            elif frequency == 'quarterly':
                # First trading day of quarter
                current_quarter = None
                for date in date_range:
                    quarter = (date.month - 1) // 3 + 1
                    if current_quarter != quarter:
                        rebalancing_dates.add(date)
                        current_quarter = quarter
            
            return rebalancing_dates
            
        except Exception as e:
            logger.error(f"Rebalancing dates error: {e}")
            return set()

    def _apply_strategy(self, portfolio, price_data, current_date, strategy_type):
        """Apply investment strategy to adjust portfolio weights"""
        try:
            if strategy_type == 'buy_and_hold':
                return portfolio
            
            elif strategy_type == 'momentum':
                # Momentum strategy - overweight recent winners
                lookback_period = 60  # 3 months
                momentum_scores = {}
                
                start_idx = max(0, price_data.index.get_loc(current_date) - lookback_period)
                
                for symbol in portfolio:
                    if symbol in price_data.columns:
                        price_series = price_data[symbol].iloc[start_idx:price_data.index.get_loc(current_date)+1]
                        if len(price_series) > 1:
                            momentum = (price_series.iloc[-1] / price_series.iloc[0]) - 1
                            momentum_scores[symbol] = momentum
                
                # Adjust weights based on momentum
                adjusted_weights = {}
                total_score = sum(max(0, score) for score in momentum_scores.values())
                
                if total_score > 0:
                    for symbol, base_weight in portfolio.items():
                        momentum = momentum_scores.get(symbol, 0)
                        momentum_multiplier = 1 + (momentum / total_score if momentum > 0 else -0.2)
                        adjusted_weights[symbol] = base_weight * momentum_multiplier
                    
                    # Normalize weights
                    total_weight = sum(adjusted_weights.values())
                    if total_weight > 0:
                        adjusted_weights = {k: v/total_weight for k, v in adjusted_weights.items()}
                else:
                    adjusted_weights = portfolio
                
                return adjusted_weights
            
            elif strategy_type == 'mean_reversion':
                # Mean reversion strategy - overweight recent losers
                lookback_period = 20  # 1 month
                reversion_scores = {}
                
                start_idx = max(0, price_data.index.get_loc(current_date) - lookback_period)
                
                for symbol in portfolio:
                    if symbol in price_data.columns:
                        price_series = price_data[symbol].iloc[start_idx:price_data.index.get_loc(current_date)+1]
                        if len(price_series) > 1:
                            recent_return = (price_series.iloc[-1] / price_series.iloc[0]) - 1
                            # Inverse of momentum for mean reversion
                            reversion_scores[symbol] = -recent_return
                
                # Adjust weights based on mean reversion
                adjusted_weights = {}
                for symbol, base_weight in portfolio.items():
                    reversion = reversion_scores.get(symbol, 0)
                    reversion_multiplier = 1 + (reversion * 0.5)  # More conservative adjustment
                    adjusted_weights[symbol] = base_weight * max(0.5, reversion_multiplier)
                
                # Normalize weights
                total_weight = sum(adjusted_weights.values())
                if total_weight > 0:
                    adjusted_weights = {k: v/total_weight for k, v in adjusted_weights.items()}
                else:
                    adjusted_weights = portfolio
                
                return adjusted_weights
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Strategy application error: {e}")
            return portfolio

    def _calculate_performance_metrics(self, backtest_results, strategy_params):
        """Calculate comprehensive performance metrics"""
        try:
            if backtest_results.empty:
                return {}
            
            portfolio_values = backtest_results['portfolio_value']
            returns = portfolio_values.pct_change().dropna()
            
            # Basic performance metrics
            total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) - 1
            annualized_return = (1 + total_return) ** (252 / len(portfolio_values)) - 1
            
            # Risk metrics
            volatility = returns.std() * np.sqrt(252)
            max_drawdown = self._calculate_max_drawdown(portfolio_values)
            
            # Risk-adjusted metrics
            sharpe_ratio = (annualized_return - self.risk_free_rate) / volatility if volatility > 0 else 0
            sortino_ratio = self._calculate_sortino_ratio(returns, self.risk_free_rate)
            
            # Additional metrics
            positive_periods = (returns > 0).sum()
            total_periods = len(returns)
            win_rate = positive_periods / total_periods if total_periods > 0 else 0
            
            # Best and worst periods
            best_day = returns.max()
            worst_day = returns.min()
            
            # Value at Risk (95% confidence)
            var_95 = np.percentile(returns, 5)
            
            return {
                'total_return': total_return,
                'annualized_return': annualized_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': win_rate,
                'best_day': best_day,
                'worst_day': worst_day,
                'var_95': var_95,
                'total_periods': total_periods,
                'positive_periods': positive_periods,
                'final_value': portfolio_values.iloc[-1],
                'initial_value': portfolio_values.iloc[0],
                'peak_value': portfolio_values.max(),
                'trough_value': portfolio_values.min()
            }
            
        except Exception as e:
            logger.error(f"Performance metrics calculation error: {e}")
            return {}

    def _calculate_max_drawdown(self, portfolio_values):
        """Calculate maximum drawdown"""
        try:
            peak = portfolio_values.cummax()
            drawdown = (portfolio_values - peak) / peak
            return drawdown.min()
        except Exception:
            return 0

    def _calculate_sortino_ratio(self, returns, risk_free_rate):
        """Calculate Sortino ratio (downside deviation)"""
        try:
            excess_returns = returns - risk_free_rate/252
            downside_returns = excess_returns[excess_returns < 0]
            
            if len(downside_returns) == 0:
                return float('inf')
            
            downside_deviation = downside_returns.std() * np.sqrt(252)
            
            if downside_deviation == 0:
                return float('inf')
            
            return (returns.mean() * 252 - risk_free_rate) / downside_deviation
            
        except Exception:
            return 0

    def _get_benchmark_performance(self, benchmark_symbol, strategy_params):
        """Get benchmark performance for comparison"""
        try:
            start_date = strategy_params.get('start_date', '2023-01-01')
            end_date = strategy_params.get('end_date', datetime.now().strftime('%Y-%m-%d'))
            
            benchmark_data = yf.download(benchmark_symbol, start=start_date, end=end_date)
            
            if benchmark_data.empty:
                return None
            
            benchmark_prices = benchmark_data['Adj Close']
            benchmark_returns = benchmark_prices.pct_change().dropna()
            
            # Calculate benchmark metrics
            total_return = (benchmark_prices.iloc[-1] / benchmark_prices.iloc[0]) - 1
            annualized_return = (1 + total_return) ** (252 / len(benchmark_prices)) - 1
            volatility = benchmark_returns.std() * np.sqrt(252)
            sharpe_ratio = (annualized_return - self.risk_free_rate) / volatility if volatility > 0 else 0
            max_drawdown = self._calculate_max_drawdown(benchmark_prices)
            
            return {
                'symbol': benchmark_symbol,
                'name': self.benchmarks.get(benchmark_symbol, benchmark_symbol),
                'total_return': total_return,
                'annualized_return': annualized_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'prices': benchmark_prices.tolist(),
                'dates': [date.strftime('%Y-%m-%d') for date in benchmark_prices.index]
            }
            
        except Exception as e:
            logger.error(f"Benchmark performance error: {e}")
            return None

    def _generate_chart_data(self, backtest_results, benchmark_data):
        """Generate data for portfolio performance charts"""
        try:
            chart_data = {
                'portfolio_performance': {
                    'dates': [date.strftime('%Y-%m-%d') for date in backtest_results.index],
                    'values': backtest_results['portfolio_value'].tolist()
                },
                'drawdown_chart': [],
                'monthly_returns': [],
                'allocation_over_time': []
            }
            
            # Calculate drawdown data
            portfolio_values = backtest_results['portfolio_value']
            peak = portfolio_values.cummax()
            drawdown = (portfolio_values - peak) / peak * 100
            
            chart_data['drawdown_chart'] = {
                'dates': [date.strftime('%Y-%m-%d') for date in backtest_results.index],
                'drawdowns': drawdown.tolist()
            }
            
            # Monthly returns heatmap data
            returns = portfolio_values.pct_change().dropna()
            monthly_returns = returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
            
            for date, return_val in monthly_returns.items():
                chart_data['monthly_returns'].append({
                    'year': date.year,
                    'month': date.month,
                    'return': return_val
                })
            
            # Add benchmark if available
            if benchmark_data:
                chart_data['benchmark_performance'] = {
                    'dates': benchmark_data['dates'],
                    'values': benchmark_data['prices']
                }
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Chart data generation error: {e}")
            return {}

    def _generate_insights(self, performance_metrics, benchmark_data):
        """Generate actionable insights from backtest results"""
        try:
            insights = []
            
            # Performance vs benchmark
            if benchmark_data:
                portfolio_return = performance_metrics.get('annualized_return', 0)
                benchmark_return = benchmark_data.get('annualized_return', 0)
                
                if portfolio_return > benchmark_return:
                    outperformance = (portfolio_return - benchmark_return) * 100
                    insights.append(f"Portfolio outperformed benchmark by {outperformance:.1f}% annually")
                else:
                    underperformance = (benchmark_return - portfolio_return) * 100
                    insights.append(f"Portfolio underperformed benchmark by {underperformance:.1f}% annually")
            
            # Risk analysis
            sharpe_ratio = performance_metrics.get('sharpe_ratio', 0)
            if sharpe_ratio > 1.0:
                insights.append("Excellent risk-adjusted returns (Sharpe ratio > 1.0)")
            elif sharpe_ratio > 0.5:
                insights.append("Good risk-adjusted returns")
            else:
                insights.append("Consider reducing portfolio risk or improving returns")
            
            # Drawdown analysis
            max_drawdown = performance_metrics.get('max_drawdown', 0)
            if abs(max_drawdown) > 0.20:
                insights.append("High maximum drawdown - consider risk management strategies")
            elif abs(max_drawdown) > 0.10:
                insights.append("Moderate drawdown risk - monitor portfolio closely")
            else:
                insights.append("Low drawdown risk - well-controlled portfolio")
            
            # Volatility analysis
            volatility = performance_metrics.get('volatility', 0)
            if volatility > 0.25:
                insights.append("High volatility portfolio - suitable for risk-tolerant investors")
            elif volatility > 0.15:
                insights.append("Moderate volatility - balanced risk profile")
            else:
                insights.append("Low volatility - conservative risk profile")
            
            # Win rate analysis
            win_rate = performance_metrics.get('win_rate', 0)
            if win_rate > 0.6:
                insights.append(f"High win rate ({win_rate:.1%}) indicates consistent performance")
            elif win_rate < 0.4:
                insights.append(f"Low win rate ({win_rate:.1%}) suggests high volatility periods")
            
            return insights
            
        except Exception as e:
            logger.error(f"Insights generation error: {e}")
            return ["Analysis completed successfully"]

# Global instance
portfolio_backtesting_engine = PortfolioBacktestingEngine()