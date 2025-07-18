#!/usr/bin/env python3
"""
Trading Data Analyzer
Analyzes AI trading decisions and performance metrics from live market data
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any
import yfinance as yf
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingDataAnalyzer:
    def __init__(self, log_file='paper_trading.log'):
        self.log_file = log_file
        self.trading_data = []
        self.performance_metrics = {}
        self.market_data = {}
        
    def load_trading_data(self) -> List[Dict]:
        """Load trading decisions from log file"""
        trading_decisions = []
        
        try:
            with open(self.log_file, 'r') as f:
                content = f.read()
                
            # Parse trading decisions from log
            lines = content.split('\n')
            current_decision = {}
            
            for line in lines:
                if 'Trading Decision:' in line:
                    if current_decision:
                        trading_decisions.append(current_decision)
                    current_decision = {
                        'timestamp': datetime.now().isoformat(),
                        'decision': line.split('Trading Decision:')[1].strip()
                    }
                elif 'Symbol:' in line and current_decision:
                    current_decision['symbol'] = line.split('Symbol:')[1].strip()
                elif 'Action:' in line and current_decision:
                    current_decision['action'] = line.split('Action:')[1].strip()
                elif 'Confidence:' in line and current_decision:
                    current_decision['confidence'] = float(line.split('Confidence:')[1].strip().replace('%', ''))
                elif 'Price:' in line and current_decision:
                    current_decision['price'] = float(line.split('Price:')[1].strip().replace('$', ''))
                elif 'Reasoning:' in line and current_decision:
                    current_decision['reasoning'] = line.split('Reasoning:')[1].strip()
                    
            if current_decision:
                trading_decisions.append(current_decision)
                
            self.trading_data = trading_decisions
            logger.info(f"Loaded {len(trading_decisions)} trading decisions")
            return trading_decisions
            
        except Exception as e:
            logger.error(f"Error loading trading data: {e}")
            return []
    
    def fetch_market_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict:
        """Fetch actual market data for comparison"""
        market_data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=end_date, interval='1m')
                market_data[symbol] = hist
                logger.info(f"Fetched market data for {symbol}")
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                
        self.market_data = market_data
        return market_data
    
    def calculate_prediction_accuracy(self) -> Dict:
        """Calculate AI prediction accuracy vs actual market movements"""
        accuracy_metrics = {
            'total_predictions': 0,
            'correct_predictions': 0,
            'accuracy_percentage': 0,
            'by_symbol': {},
            'by_confidence_level': {}
        }
        
        for decision in self.trading_data:
            symbol = decision.get('symbol')
            action = decision.get('action')
            confidence = decision.get('confidence', 0)
            price = decision.get('price', 0)
            timestamp = decision.get('timestamp')
            
            if not all([symbol, action, timestamp]):
                continue
                
            accuracy_metrics['total_predictions'] += 1
            
            # Get actual market movement
            if symbol in self.market_data:
                hist = self.market_data[symbol]
                decision_time = pd.to_datetime(timestamp)
                
                # Find closest market data point
                closest_idx = hist.index.get_indexer([decision_time], method='nearest')[0]
                if closest_idx < len(hist) - 1:
                    current_price = hist.iloc[closest_idx]['Close']
                    future_price = hist.iloc[closest_idx + 1]['Close']
                    
                    actual_movement = 'BUY' if future_price > current_price else 'SELL'
                    predicted_correct = (action.upper() == actual_movement)
                    
                    if predicted_correct:
                        accuracy_metrics['correct_predictions'] += 1
                    
                    # Track by symbol
                    if symbol not in accuracy_metrics['by_symbol']:
                        accuracy_metrics['by_symbol'][symbol] = {'total': 0, 'correct': 0}
                    accuracy_metrics['by_symbol'][symbol]['total'] += 1
                    if predicted_correct:
                        accuracy_metrics['by_symbol'][symbol]['correct'] += 1
                    
                    # Track by confidence level
                    confidence_bucket = f"{int(confidence//10)*10}-{int(confidence//10)*10+9}%"
                    if confidence_bucket not in accuracy_metrics['by_confidence_level']:
                        accuracy_metrics['by_confidence_level'][confidence_bucket] = {'total': 0, 'correct': 0}
                    accuracy_metrics['by_confidence_level'][confidence_bucket]['total'] += 1
                    if predicted_correct:
                        accuracy_metrics['by_confidence_level'][confidence_bucket]['correct'] += 1
        
        # Calculate percentages
        if accuracy_metrics['total_predictions'] > 0:
            accuracy_metrics['accuracy_percentage'] = (
                accuracy_metrics['correct_predictions'] / accuracy_metrics['total_predictions']
            ) * 100
        
        for symbol_data in accuracy_metrics['by_symbol'].values():
            if symbol_data['total'] > 0:
                symbol_data['accuracy'] = (symbol_data['correct'] / symbol_data['total']) * 100
        
        for conf_data in accuracy_metrics['by_confidence_level'].values():
            if conf_data['total'] > 0:
                conf_data['accuracy'] = (conf_data['correct'] / conf_data['total']) * 100
        
        self.performance_metrics['accuracy'] = accuracy_metrics
        return accuracy_metrics
    
    def analyze_technical_indicators(self) -> Dict:
        """Analyze effectiveness of technical indicators"""
        indicator_analysis = {
            'rsi_effectiveness': {},
            'macd_effectiveness': {},
            'bollinger_effectiveness': {},
            'volume_effectiveness': {}
        }
        
        for decision in self.trading_data:
            reasoning = decision.get('reasoning', '').lower()
            symbol = decision.get('symbol')
            action = decision.get('action')
            
            # Extract technical indicators mentioned in reasoning
            indicators_used = []
            if 'rsi' in reasoning:
                indicators_used.append('rsi')
            if 'macd' in reasoning:
                indicators_used.append('macd')
            if 'bollinger' in reasoning:
                indicators_used.append('bollinger')
            if 'volume' in reasoning:
                indicators_used.append('volume')
            
            # Track indicator usage and effectiveness
            for indicator in indicators_used:
                if indicator not in indicator_analysis[f'{indicator}_effectiveness']:
                    indicator_analysis[f'{indicator}_effectiveness'][symbol] = []
                indicator_analysis[f'{indicator}_effectiveness'][symbol].append({
                    'action': action,
                    'reasoning': reasoning,
                    'timestamp': decision.get('timestamp')
                })
        
        return indicator_analysis
    
    def calculate_portfolio_performance(self) -> Dict:
        """Calculate overall portfolio performance"""
        portfolio_metrics = {
            'total_trades': len(self.trading_data),
            'buy_trades': 0,
            'sell_trades': 0,
            'average_confidence': 0,
            'confidence_distribution': {},
            'most_traded_symbols': {},
            'trading_frequency': {}
        }
        
        confidences = []
        for decision in self.trading_data:
            action = decision.get('action', '').upper()
            confidence = decision.get('confidence', 0)
            symbol = decision.get('symbol')
            timestamp = decision.get('timestamp')
            
            if action == 'BUY':
                portfolio_metrics['buy_trades'] += 1
            elif action == 'SELL':
                portfolio_metrics['sell_trades'] += 1
            
            confidences.append(confidence)
            
            # Track symbol frequency
            if symbol not in portfolio_metrics['most_traded_symbols']:
                portfolio_metrics['most_traded_symbols'][symbol] = 0
            portfolio_metrics['most_traded_symbols'][symbol] += 1
            
            # Track trading frequency by hour
            if timestamp:
                hour = pd.to_datetime(timestamp).hour
                if hour not in portfolio_metrics['trading_frequency']:
                    portfolio_metrics['trading_frequency'][hour] = 0
                portfolio_metrics['trading_frequency'][hour] += 1
        
        if confidences:
            portfolio_metrics['average_confidence'] = np.mean(confidences)
            portfolio_metrics['confidence_std'] = np.std(confidences)
            portfolio_metrics['min_confidence'] = np.min(confidences)
            portfolio_metrics['max_confidence'] = np.max(confidences)
        
        return portfolio_metrics
    
    def generate_insights(self) -> Dict:
        """Generate actionable insights from analysis"""
        insights = {
            'key_findings': [],
            'optimization_opportunities': [],
            'risk_factors': [],
            'recommendations': []
        }
        
        # Key findings based on accuracy
        accuracy = self.performance_metrics.get('accuracy', {})
        if accuracy.get('accuracy_percentage', 0) > 60:
            insights['key_findings'].append(f"AI achieved {accuracy['accuracy_percentage']:.1f}% prediction accuracy")
        else:
            insights['key_findings'].append(f"AI accuracy at {accuracy['accuracy_percentage']:.1f}% needs improvement")
        
        # Best performing symbols
        best_symbols = []
        for symbol, data in accuracy.get('by_symbol', {}).items():
            if data.get('accuracy', 0) > 70:
                best_symbols.append(f"{symbol} ({data['accuracy']:.1f}%)")
        
        if best_symbols:
            insights['key_findings'].append(f"Top performing symbols: {', '.join(best_symbols)}")
        
        # Confidence vs accuracy correlation
        conf_levels = accuracy.get('by_confidence_level', {})
        high_conf_accurate = any(
            data.get('accuracy', 0) > 70 for bucket, data in conf_levels.items() 
            if '80-89%' in bucket or '90-99%' in bucket
        )
        
        if high_conf_accurate:
            insights['key_findings'].append("High confidence predictions show strong accuracy")
        else:
            insights['optimization_opportunities'].append("Improve confidence scoring calibration")
        
        # Recommendations
        insights['recommendations'].extend([
            "Focus on symbols with highest prediction accuracy",
            "Refine technical indicators for better signal quality",
            "Optimize confidence scoring for better risk management",
            "Consider portfolio diversification based on prediction success"
        ])
        
        return insights
    
    def create_analysis_report(self) -> Dict:
        """Create comprehensive analysis report"""
        report = {
            'analysis_date': datetime.now().isoformat(),
            'data_summary': {
                'total_decisions': len(self.trading_data),
                'analysis_period': 'Market session',
                'symbols_analyzed': list(set(d.get('symbol') for d in self.trading_data if d.get('symbol')))
            },
            'accuracy_metrics': self.performance_metrics.get('accuracy', {}),
            'portfolio_performance': self.calculate_portfolio_performance(),
            'technical_analysis': self.analyze_technical_indicators(),
            'insights': self.generate_insights(),
            'raw_data': self.trading_data
        }
        
        return report
    
    def save_analysis_report(self, filename: str = None) -> str:
        """Save analysis report to file"""
        if not filename:
            filename = f'trading_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        report = self.create_analysis_report()
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Analysis report saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            return ""
    
    def print_summary(self):
        """Print analysis summary to console"""
        print("\n" + "="*60)
        print("AI TRADING PERFORMANCE ANALYSIS")
        print("="*60)
        
        accuracy = self.performance_metrics.get('accuracy', {})
        print(f"Total Predictions: {accuracy.get('total_predictions', 0)}")
        print(f"Correct Predictions: {accuracy.get('correct_predictions', 0)}")
        print(f"Accuracy: {accuracy.get('accuracy_percentage', 0):.1f}%")
        
        print("\nPer Symbol Performance:")
        for symbol, data in accuracy.get('by_symbol', {}).items():
            print(f"  {symbol}: {data.get('accuracy', 0):.1f}% ({data.get('correct', 0)}/{data.get('total', 0)})")
        
        print("\nConfidence Level Analysis:")
        for bucket, data in accuracy.get('by_confidence_level', {}).items():
            print(f"  {bucket}: {data.get('accuracy', 0):.1f}% ({data.get('correct', 0)}/{data.get('total', 0)})")
        
        portfolio = self.calculate_portfolio_performance()
        print(f"\nPortfolio Metrics:")
        print(f"  Total Trades: {portfolio.get('total_trades', 0)}")
        print(f"  Buy/Sell Ratio: {portfolio.get('buy_trades', 0)}/{portfolio.get('sell_trades', 0)}")
        print(f"  Average Confidence: {portfolio.get('average_confidence', 0):.1f}%")
        
        insights = self.generate_insights()
        print("\nKey Insights:")
        for finding in insights.get('key_findings', []):
            print(f"  • {finding}")
        
        print("\nRecommendations:")
        for rec in insights.get('recommendations', []):
            print(f"  • {rec}")
        
        print("="*60)

def main():
    """Main analysis function"""
    analyzer = TradingDataAnalyzer()
    
    # Load trading data
    trading_decisions = analyzer.load_trading_data()
    
    if not trading_decisions:
        print("No trading data found. Run the analysis after market hours tomorrow.")
        return
    
    # Get unique symbols from decisions
    symbols = list(set(d.get('symbol') for d in trading_decisions if d.get('symbol')))
    
    # Fetch market data for comparison
    today = datetime.now().strftime('%Y-%m-%d')
    analyzer.fetch_market_data(symbols, today, today)
    
    # Calculate accuracy
    analyzer.calculate_prediction_accuracy()
    
    # Print summary
    analyzer.print_summary()
    
    # Save detailed report
    report_file = analyzer.save_analysis_report()
    print(f"\nDetailed report saved to: {report_file}")

if __name__ == "__main__":
    main()