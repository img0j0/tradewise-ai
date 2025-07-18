#!/usr/bin/env python3
"""
Optimization Engine
Uses trading data analysis to optimize AI models and trading strategies
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizationEngine:
    def __init__(self, analysis_data: Dict = None):
        self.analysis_data = analysis_data or {}
        self.optimization_results = {}
        self.model_improvements = {}
        
    def load_analysis_data(self, filename: str) -> Dict:
        """Load analysis data from file"""
        try:
            with open(filename, 'r') as f:
                self.analysis_data = json.load(f)
            logger.info(f"Loaded analysis data from {filename}")
            return self.analysis_data
        except Exception as e:
            logger.error(f"Error loading analysis data: {e}")
            return {}
    
    def identify_optimization_opportunities(self) -> Dict:
        """Identify areas for optimization based on analysis"""
        opportunities = {
            'model_improvements': [],
            'parameter_tuning': [],
            'feature_engineering': [],
            'confidence_calibration': [],
            'risk_management': []
        }
        
        accuracy_data = self.analysis_data.get('accuracy_metrics', {})
        
        # Model accuracy improvements
        overall_accuracy = accuracy_data.get('accuracy_percentage', 0)
        if overall_accuracy < 60:
            opportunities['model_improvements'].append({
                'issue': 'Low overall accuracy',
                'current': f"{overall_accuracy:.1f}%",
                'target': '65%+',
                'priority': 'high',
                'solution': 'Retrain model with more features and data'
            })
        
        # Symbol-specific improvements
        symbol_accuracy = accuracy_data.get('by_symbol', {})
        low_performers = [(symbol, data) for symbol, data in symbol_accuracy.items() 
                         if data.get('accuracy', 0) < 50]
        
        if low_performers:
            opportunities['model_improvements'].append({
                'issue': 'Poor performance on specific symbols',
                'symbols': [s[0] for s in low_performers],
                'priority': 'medium',
                'solution': 'Create symbol-specific models or features'
            })
        
        # Confidence calibration
        confidence_data = accuracy_data.get('by_confidence_level', {})
        confidence_issues = []
        
        for bucket, data in confidence_data.items():
            expected_accuracy = float(bucket.split('-')[0])
            actual_accuracy = data.get('accuracy', 0)
            
            if abs(expected_accuracy - actual_accuracy) > 15:
                confidence_issues.append({
                    'bucket': bucket,
                    'expected': expected_accuracy,
                    'actual': actual_accuracy,
                    'difference': abs(expected_accuracy - actual_accuracy)
                })
        
        if confidence_issues:
            opportunities['confidence_calibration'].append({
                'issue': 'Confidence scores not calibrated',
                'details': confidence_issues,
                'priority': 'high',
                'solution': 'Recalibrate confidence scoring algorithm'
            })
        
        # Feature engineering opportunities
        portfolio_data = self.analysis_data.get('portfolio_performance', {})
        avg_confidence = portfolio_data.get('average_confidence', 0)
        
        if avg_confidence < 70:
            opportunities['feature_engineering'].append({
                'issue': 'Low average confidence',
                'current': f"{avg_confidence:.1f}%",
                'priority': 'medium',
                'solution': 'Add more technical indicators and market features'
            })
        
        return opportunities
    
    def optimize_model_parameters(self, trading_data: List[Dict]) -> Dict:
        """Optimize model parameters based on trading results"""
        if not trading_data:
            return {}
        
        # Prepare training data
        features = []
        labels = []
        
        for decision in trading_data:
            if not all(key in decision for key in ['symbol', 'action', 'confidence', 'reasoning']):
                continue
                
            # Extract features from reasoning
            reasoning = decision.get('reasoning', '').lower()
            
            # Technical indicator features
            feature_vector = [
                1 if 'rsi' in reasoning else 0,
                1 if 'macd' in reasoning else 0,
                1 if 'bollinger' in reasoning else 0,
                1 if 'volume' in reasoning else 0,
                1 if 'oversold' in reasoning else 0,
                1 if 'overbought' in reasoning else 0,
                1 if 'bullish' in reasoning else 0,
                1 if 'bearish' in reasoning else 0,
                decision.get('confidence', 0) / 100,
                1 if decision.get('action') == 'BUY' else 0
            ]
            
            features.append(feature_vector)
            # For now, use action as label (would need actual outcomes in real scenario)
            labels.append(1 if decision.get('action') == 'BUY' else 0)
        
        if len(features) < 10:
            logger.warning("Not enough data for parameter optimization")
            return {}
        
        # Train model with different parameters
        X = np.array(features)
        y = np.array(labels)
        
        best_params = {}
        best_score = 0
        
        # Test different parameter combinations
        param_combinations = [
            {'n_estimators': 50, 'max_depth': 5},
            {'n_estimators': 100, 'max_depth': 10},
            {'n_estimators': 200, 'max_depth': 15},
            {'n_estimators': 150, 'max_depth': None}
        ]
        
        for params in param_combinations:
            try:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
                
                model = RandomForestClassifier(**params, random_state=42)
                model.fit(X_train, y_train)
                
                y_pred = model.predict(X_test)
                score = accuracy_score(y_test, y_pred)
                
                if score > best_score:
                    best_score = score
                    best_params = params
                    
            except Exception as e:
                logger.error(f"Error testing parameters {params}: {e}")
        
        return {
            'best_parameters': best_params,
            'best_score': best_score,
            'feature_importance': list(model.feature_importances_) if 'model' in locals() else [],
            'optimization_date': datetime.now().isoformat()
        }
    
    def generate_feature_improvements(self) -> List[Dict]:
        """Generate suggestions for feature improvements"""
        improvements = []
        
        # Analyze current feature usage
        technical_analysis = self.analysis_data.get('technical_analysis', {})
        
        # RSI improvements
        rsi_usage = len(technical_analysis.get('rsi_effectiveness', {}))
        if rsi_usage > 0:
            improvements.append({
                'feature': 'RSI',
                'current_usage': rsi_usage,
                'suggestions': [
                    'Add RSI divergence detection',
                    'Implement multi-timeframe RSI analysis',
                    'Include RSI momentum indicators'
                ]
            })
        
        # MACD improvements
        macd_usage = len(technical_analysis.get('macd_effectiveness', {}))
        if macd_usage > 0:
            improvements.append({
                'feature': 'MACD',
                'current_usage': macd_usage,
                'suggestions': [
                    'Add MACD histogram analysis',
                    'Implement MACD signal line crossovers',
                    'Include MACD trend strength indicators'
                ]
            })
        
        # Volume improvements
        volume_usage = len(technical_analysis.get('volume_effectiveness', {}))
        if volume_usage > 0:
            improvements.append({
                'feature': 'Volume',
                'current_usage': volume_usage,
                'suggestions': [
                    'Add volume-weighted average price (VWAP)',
                    'Implement volume breakout detection',
                    'Include volume trend analysis'
                ]
            })
        
        # New feature suggestions
        improvements.extend([
            {
                'feature': 'Market Sentiment',
                'type': 'new',
                'suggestions': [
                    'Add news sentiment analysis',
                    'Include social media sentiment',
                    'Implement earnings calendar impact'
                ]
            },
            {
                'feature': 'Market Structure',
                'type': 'new',
                'suggestions': [
                    'Add support/resistance levels',
                    'Include trend line analysis',
                    'Implement market regime detection'
                ]
            }
        ])
        
        return improvements
    
    def optimize_confidence_scoring(self) -> Dict:
        """Optimize confidence scoring algorithm"""
        confidence_data = self.analysis_data.get('accuracy_metrics', {}).get('by_confidence_level', {})
        
        if not confidence_data:
            return {}
        
        optimization = {
            'current_calibration': {},
            'suggested_adjustments': {},
            'calibration_formula': {}
        }
        
        for bucket, data in confidence_data.items():
            expected = float(bucket.split('-')[0])
            actual = data.get('accuracy', 0)
            difference = actual - expected
            
            optimization['current_calibration'][bucket] = {
                'expected': expected,
                'actual': actual,
                'difference': difference,
                'sample_size': data.get('total', 0)
            }
            
            # Suggest adjustments
            if abs(difference) > 10:
                adjustment_factor = 1 + (difference / 100)
                optimization['suggested_adjustments'][bucket] = {
                    'current_multiplier': 1.0,
                    'suggested_multiplier': adjustment_factor,
                    'explanation': f"{'Increase' if difference > 0 else 'Decrease'} confidence by {abs(difference):.1f}%"
                }
        
        # Generate improved calibration formula
        optimization['calibration_formula'] = {
            'method': 'linear_adjustment',
            'formula': 'adjusted_confidence = base_confidence * calibration_factor',
            'implementation': 'Apply per-confidence-bucket multipliers based on historical accuracy'
        }
        
        return optimization
    
    def create_optimization_plan(self) -> Dict:
        """Create comprehensive optimization plan"""
        plan = {
            'analysis_date': datetime.now().isoformat(),
            'current_performance': {
                'overall_accuracy': self.analysis_data.get('accuracy_metrics', {}).get('accuracy_percentage', 0),
                'total_trades': len(self.analysis_data.get('raw_data', [])),
                'average_confidence': self.analysis_data.get('portfolio_performance', {}).get('average_confidence', 0)
            },
            'optimization_opportunities': self.identify_optimization_opportunities(),
            'model_improvements': self.optimize_model_parameters(self.analysis_data.get('raw_data', [])),
            'feature_improvements': self.generate_feature_improvements(),
            'confidence_optimization': self.optimize_confidence_scoring(),
            'implementation_timeline': self.create_implementation_timeline(),
            'success_metrics': self.define_success_metrics()
        }
        
        return plan
    
    def create_implementation_timeline(self) -> List[Dict]:
        """Create implementation timeline for optimizations"""
        timeline = [
            {
                'phase': 'Phase 1: Quick Wins',
                'duration': '1-2 days',
                'tasks': [
                    'Adjust confidence scoring based on calibration analysis',
                    'Fine-tune existing technical indicator parameters',
                    'Remove or reduce weight of poorly performing features'
                ]
            },
            {
                'phase': 'Phase 2: Model Improvements',
                'duration': '3-5 days',
                'tasks': [
                    'Retrain models with optimized parameters',
                    'Implement symbol-specific model variants',
                    'Add new technical indicators based on analysis'
                ]
            },
            {
                'phase': 'Phase 3: Feature Engineering',
                'duration': '5-7 days',
                'tasks': [
                    'Develop market sentiment features',
                    'Implement advanced technical analysis',
                    'Add market structure detection'
                ]
            },
            {
                'phase': 'Phase 4: Validation',
                'duration': '2-3 days',
                'tasks': [
                    'Test optimized models with historical data',
                    'Validate confidence scoring improvements',
                    'Measure performance improvements'
                ]
            }
        ]
        
        return timeline
    
    def define_success_metrics(self) -> Dict:
        """Define success metrics for optimization"""
        current_accuracy = self.analysis_data.get('accuracy_metrics', {}).get('accuracy_percentage', 0)
        
        return {
            'primary_metrics': {
                'prediction_accuracy': {
                    'current': f"{current_accuracy:.1f}%",
                    'target': f"{current_accuracy + 10:.1f}%",
                    'minimum': f"{max(current_accuracy + 5, 60):.1f}%"
                },
                'confidence_calibration': {
                    'current': 'Needs improvement',
                    'target': 'Within 5% of expected accuracy',
                    'measurement': 'Average absolute difference between expected and actual'
                }
            },
            'secondary_metrics': {
                'trading_frequency': 'Maintain current levels',
                'risk_management': 'Improve position sizing accuracy',
                'symbol_coverage': 'Consistent performance across all symbols'
            },
            'validation_criteria': {
                'minimum_sample_size': 50,
                'validation_period': '1 trading day',
                'success_threshold': '10% improvement in accuracy'
            }
        }
    
    def save_optimization_plan(self, filename: str = None) -> str:
        """Save optimization plan to file"""
        if not filename:
            filename = f'optimization_plan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        plan = self.create_optimization_plan()
        
        try:
            with open(filename, 'w') as f:
                json.dump(plan, f, indent=2)
            
            logger.info(f"Optimization plan saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving optimization plan: {e}")
            return ""
    
    def print_optimization_summary(self):
        """Print optimization summary"""
        opportunities = self.identify_optimization_opportunities()
        
        print("\n" + "="*70)
        print("AI TRADING SYSTEM OPTIMIZATION PLAN")
        print("="*70)
        
        print("\nCURRENT PERFORMANCE:")
        current_accuracy = self.analysis_data.get('accuracy_metrics', {}).get('accuracy_percentage', 0)
        print(f"Overall Accuracy: {current_accuracy:.1f}%")
        
        print("\nOPTIMIZATION OPPORTUNITIES:")
        
        for category, items in opportunities.items():
            if items:
                print(f"\n{category.replace('_', ' ').title()}:")
                for item in items:
                    print(f"  • {item.get('issue', 'Improvement needed')}")
                    if 'priority' in item:
                        print(f"    Priority: {item['priority']}")
                    if 'solution' in item:
                        print(f"    Solution: {item['solution']}")
        
        print("\nIMPLEMENTATION PHASES:")
        timeline = self.create_implementation_timeline()
        for phase in timeline:
            print(f"\n{phase['phase']} ({phase['duration']}):")
            for task in phase['tasks']:
                print(f"  • {task}")
        
        print("\nSUCCESS TARGETS:")
        metrics = self.define_success_metrics()
        for metric, details in metrics['primary_metrics'].items():
            print(f"  • {metric.replace('_', ' ').title()}: {details['target']}")
        
        print("="*70)

def main():
    """Main function to run optimization analysis"""
    # Look for the most recent analysis file
    import glob
    analysis_files = glob.glob('trading_analysis_*.json')
    
    if not analysis_files:
        print("No analysis files found. Please run trading_data_analyzer.py first.")
        return
    
    # Use the most recent analysis file
    latest_file = max(analysis_files, key=lambda f: f.split('_')[-1])
    print(f"Using analysis data from: {latest_file}")
    
    # Create optimization engine
    optimizer = OptimizationEngine()
    optimizer.load_analysis_data(latest_file)
    
    # Print optimization summary
    optimizer.print_optimization_summary()
    
    # Save optimization plan
    plan_file = optimizer.save_optimization_plan()
    print(f"\nDetailed optimization plan saved to: {plan_file}")

if __name__ == "__main__":
    main()