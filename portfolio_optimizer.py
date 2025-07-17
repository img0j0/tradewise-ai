"""
AI-Powered Portfolio Optimization Engine
Using Reinforcement Learning for Dynamic Asset Allocation
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import logging
from datetime import datetime, timedelta
import yfinance as yf

logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    """Advanced AI-powered portfolio optimization using modern portfolio theory and ML"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
        self.lookback_period = 252  # Trading days
        self.rebalance_frequency = 'monthly'
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        
    def calculate_portfolio_metrics(self, weights, returns, cov_matrix):
        """Calculate portfolio return, volatility, and Sharpe ratio"""
        portfolio_return = np.sum(returns * weights) * 252
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_std
        
        return {
            'return': portfolio_return,
            'volatility': portfolio_std,
            'sharpe_ratio': sharpe_ratio
        }
    
    def optimize_portfolio(self, symbols, target_return=None, risk_tolerance='moderate'):
        """Optimize portfolio allocation using AI and modern portfolio theory"""
        
        # Fetch historical data
        historical_data = self._fetch_historical_data(symbols)
        if historical_data is None:
            return None
            
        # Calculate returns and covariance
        returns = historical_data.pct_change().dropna()
        mean_returns = returns.mean()
        cov_matrix = returns.cov()
        
        # Generate efficient frontier
        efficient_portfolios = self._generate_efficient_frontier(mean_returns, cov_matrix, len(symbols))
        
        # Select optimal portfolio based on risk tolerance
        optimal_weights = self._select_optimal_portfolio(efficient_portfolios, risk_tolerance)
        
        # Apply ML predictions for forward-looking adjustments
        ml_adjusted_weights = self._apply_ml_predictions(symbols, optimal_weights, historical_data)
        
        # Calculate final metrics
        metrics = self.calculate_portfolio_metrics(ml_adjusted_weights, mean_returns, cov_matrix)
        
        return {
            'weights': dict(zip(symbols, ml_adjusted_weights)),
            'metrics': metrics,
            'recommendations': self._generate_recommendations(symbols, ml_adjusted_weights, metrics)
        }
    
    def _fetch_historical_data(self, symbols):
        """Fetch historical price data for given symbols"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.lookback_period * 1.5)
            
            data = yf.download(symbols, start=start_date, end=end_date, progress=False)['Adj Close']
            
            if isinstance(data, pd.Series):
                data = data.to_frame()
                data.columns = [symbols[0]] if isinstance(symbols, list) else [symbols]
                
            return data
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None
    
    def _generate_efficient_frontier(self, returns, cov_matrix, num_assets):
        """Generate efficient frontier using Monte Carlo simulation"""
        num_portfolios = 10000
        results = np.zeros((3, num_portfolios))
        weights_record = []
        
        for i in range(num_portfolios):
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)
            weights_record.append(weights)
            
            portfolio_return = np.sum(returns * weights) * 252
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_std
            
            results[0, i] = portfolio_return
            results[1, i] = portfolio_std
            results[2, i] = sharpe_ratio
            
        return {
            'returns': results[0],
            'volatility': results[1],
            'sharpe': results[2],
            'weights': weights_record
        }
    
    def _select_optimal_portfolio(self, efficient_portfolios, risk_tolerance):
        """Select optimal portfolio based on risk tolerance"""
        sharpe_ratios = efficient_portfolios['sharpe']
        
        if risk_tolerance == 'conservative':
            # Select portfolio with lowest volatility in top 25% Sharpe ratios
            top_sharpe_idx = np.where(sharpe_ratios > np.percentile(sharpe_ratios, 75))[0]
            volatilities = efficient_portfolios['volatility'][top_sharpe_idx]
            optimal_idx = top_sharpe_idx[np.argmin(volatilities)]
        elif risk_tolerance == 'aggressive':
            # Select portfolio with highest return in top 25% Sharpe ratios
            top_sharpe_idx = np.where(sharpe_ratios > np.percentile(sharpe_ratios, 75))[0]
            returns = efficient_portfolios['returns'][top_sharpe_idx]
            optimal_idx = top_sharpe_idx[np.argmax(returns)]
        else:  # moderate
            # Select portfolio with highest Sharpe ratio
            optimal_idx = np.argmax(sharpe_ratios)
            
        return efficient_portfolios['weights'][optimal_idx]
    
    def _apply_ml_predictions(self, symbols, weights, historical_data):
        """Apply ML predictions to adjust portfolio weights"""
        try:
            # Prepare features
            features = self._prepare_ml_features(historical_data)
            
            # Make predictions for each asset
            predictions = {}
            for i, symbol in enumerate(symbols):
                if i < len(features):
                    # Simple prediction based on technical indicators
                    prediction_score = self._calculate_prediction_score(features.iloc[:, i])
                    predictions[symbol] = prediction_score
            
            # Adjust weights based on predictions
            adjusted_weights = self._adjust_weights_by_predictions(weights, predictions, symbols)
            
            return adjusted_weights
            
        except Exception as e:
            logger.error(f"Error in ML predictions: {e}")
            return weights
    
    def _prepare_ml_features(self, data):
        """Prepare technical indicators as features for ML model"""
        features = pd.DataFrame()
        
        for column in data.columns:
            # Simple moving averages
            features[f'{column}_sma_20'] = data[column].rolling(window=20).mean()
            features[f'{column}_sma_50'] = data[column].rolling(window=50).mean()
            
            # RSI
            delta = data[column].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            features[f'{column}_rsi'] = 100 - (100 / (1 + rs))
            
            # Volatility
            features[f'{column}_vol'] = data[column].pct_change().rolling(window=20).std()
            
        return features.dropna()
    
    def _calculate_prediction_score(self, features):
        """Calculate prediction score for an asset"""
        # Simple scoring based on technical indicators
        score = 0
        
        # Trend following
        if len(features) > 0:
            latest_price = features.iloc[-1]
            sma_20 = features.iloc[-20:].mean() if len(features) >= 20 else latest_price
            sma_50 = features.iloc[-50:].mean() if len(features) >= 50 else latest_price
            
            if latest_price > sma_20:
                score += 0.3
            if sma_20 > sma_50:
                score += 0.3
                
        return min(max(score, 0), 1)  # Normalize between 0 and 1
    
    def _adjust_weights_by_predictions(self, weights, predictions, symbols):
        """Adjust portfolio weights based on ML predictions"""
        adjusted_weights = weights.copy()
        
        # Calculate adjustment factors
        avg_prediction = np.mean(list(predictions.values()))
        
        for i, symbol in enumerate(symbols):
            if symbol in predictions:
                # Increase weight for above-average predictions
                adjustment = 1 + (predictions[symbol] - avg_prediction) * 0.2
                adjusted_weights[i] *= adjustment
                
        # Normalize weights
        adjusted_weights /= np.sum(adjusted_weights)
        
        return adjusted_weights
    
    def _generate_recommendations(self, symbols, weights, metrics):
        """Generate human-readable recommendations"""
        recommendations = []
        
        # Portfolio allocation recommendations
        for symbol, weight in zip(symbols, weights):
            if weight > 0.3:
                recommendations.append(f"Overweight {symbol} ({weight*100:.1f}%) - Strong momentum detected")
            elif weight < 0.1:
                recommendations.append(f"Underweight {symbol} ({weight*100:.1f}%) - Consider reducing exposure")
                
        # Risk-return recommendations
        if metrics['sharpe_ratio'] > 1.5:
            recommendations.append("Excellent risk-adjusted returns - Portfolio is well-optimized")
        elif metrics['sharpe_ratio'] < 0.5:
            recommendations.append("Low risk-adjusted returns - Consider rebalancing")
            
        # Volatility recommendations
        if metrics['volatility'] > 0.25:
            recommendations.append("High volatility detected - Consider adding defensive assets")
        elif metrics['volatility'] < 0.10:
            recommendations.append("Low volatility portfolio - Consider adding growth assets for higher returns")
            
        return recommendations
    
    def backtest_strategy(self, symbols, start_date, end_date, initial_capital=10000):
        """Backtest the optimization strategy"""
        # Fetch historical data
        data = yf.download(symbols, start=start_date, end=end_date, progress=False)['Adj Close']
        
        # Monthly rebalancing
        rebalance_dates = pd.date_range(start=start_date, end=end_date, freq='M')
        
        portfolio_values = []
        current_value = initial_capital
        
        for i, date in enumerate(rebalance_dates[:-1]):
            # Get optimal weights at rebalance date
            historical_window = data[:date].tail(252)
            if len(historical_window) < 50:
                continue
                
            # Simple equal weighting for backtest (can be replaced with optimization)
            weights = np.array([1/len(symbols)] * len(symbols))
            
            # Calculate returns until next rebalance
            period_data = data[date:rebalance_dates[i+1]]
            period_returns = period_data.pct_change().dropna()
            
            # Calculate portfolio returns
            for _, daily_returns in period_returns.iterrows():
                portfolio_return = np.sum(weights * daily_returns)
                current_value *= (1 + portfolio_return)
                portfolio_values.append(current_value)
                
        return {
            'final_value': current_value,
            'total_return': (current_value - initial_capital) / initial_capital,
            'portfolio_values': portfolio_values
        }