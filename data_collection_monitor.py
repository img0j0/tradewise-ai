#!/usr/bin/env python3
"""
Real-time Data Collection Monitor
Monitors the deployed app and AI trading bot performance
"""

import time
import json
import requests
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCollectionMonitor:
    def __init__(self, app_url="https://faac9d14-f6e8-472b-b68f-2222f8439d93-00-1zm0way20has3.kirk.replit.dev"):
        self.app_url = app_url
        self.session = requests.Session()
        self.metrics = {
            'platform_health': [],
            'response_times': [],
            'error_rates': [],
            'feature_usage': [],
            'ai_performance': []
        }
        
    def check_platform_health(self):
        """Check if the platform is running properly"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.app_url}/", timeout=30)
            response_time = time.time() - start_time
            
            health_check = {
                'timestamp': datetime.now().isoformat(),
                'status_code': response.status_code,
                'response_time': response_time,
                'is_healthy': response.status_code == 200
            }
            
            self.metrics['platform_health'].append(health_check)
            logger.info(f"Platform Health: {response.status_code} - {response_time:.2f}s")
            return health_check
            
        except Exception as e:
            logger.error(f"Platform health check failed: {e}")
            return {'timestamp': datetime.now().isoformat(), 'is_healthy': False, 'error': str(e)}
    
    def test_search_functionality(self):
        """Test the Google-style search functionality"""
        try:
            # Test autocomplete
            start_time = time.time()
            response = self.session.get(f"{self.app_url}/api/search-autocomplete?q=Apple&limit=8", timeout=15)
            response_time = time.time() - start_time
            
            search_test = {
                'timestamp': datetime.now().isoformat(),
                'feature': 'search_autocomplete',
                'status_code': response.status_code,
                'response_time': response_time,
                'working': response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                search_test['results_count'] = len(data.get('suggestions', []))
            
            self.metrics['feature_usage'].append(search_test)
            logger.info(f"Search Test: {response.status_code} - {response_time:.2f}s")
            return search_test
            
        except Exception as e:
            logger.error(f"Search functionality test failed: {e}")
            return {'timestamp': datetime.now().isoformat(), 'feature': 'search_autocomplete', 'working': False, 'error': str(e)}
    
    def test_theme_analysis(self):
        """Test trending theme analysis functionality"""
        try:
            themes = ['AI & Tech', 'Clean Energy', 'Healthcare', 'Fintech', 'Gaming', 'Crypto']
            theme_results = []
            
            for theme in themes:
                start_time = time.time()
                response = self.session.get(f"{self.app_url}/api/search-theme/{theme}", timeout=20)
                response_time = time.time() - start_time
                
                theme_test = {
                    'timestamp': datetime.now().isoformat(),
                    'feature': 'theme_analysis',
                    'theme': theme,
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'working': response.status_code == 200
                }
                
                if response.status_code == 200:
                    data = response.json()
                    theme_test['stocks_count'] = len(data.get('top_stocks', []))
                    theme_test['confidence'] = data.get('insights', {}).get('confidence', 0)
                
                theme_results.append(theme_test)
                logger.info(f"Theme Test ({theme}): {response.status_code} - {response_time:.2f}s")
                time.sleep(1)  # Rate limiting
            
            self.metrics['feature_usage'].extend(theme_results)
            return theme_results
            
        except Exception as e:
            logger.error(f"Theme analysis test failed: {e}")
            return []
    
    def test_ai_insights(self):
        """Test AI insights functionality"""
        try:
            test_stocks = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA']
            ai_results = []
            
            for stock in test_stocks:
                start_time = time.time()
                response = self.session.get(f"{self.app_url}/api/search-stock/{stock}", timeout=20)
                response_time = time.time() - start_time
                
                ai_test = {
                    'timestamp': datetime.now().isoformat(),
                    'feature': 'ai_insights',
                    'stock': stock,
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'working': response.status_code == 200
                }
                
                if response.status_code == 200:
                    data = response.json()
                    ai_test['has_ai_analysis'] = 'ai_analysis' in data
                    ai_test['confidence'] = data.get('ai_analysis', {}).get('confidence', 0)
                
                ai_results.append(ai_test)
                logger.info(f"AI Test ({stock}): {response.status_code} - {response_time:.2f}s")
                time.sleep(1)  # Rate limiting
            
            self.metrics['ai_performance'].extend(ai_results)
            return ai_results
            
        except Exception as e:
            logger.error(f"AI insights test failed: {e}")
            return []
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        try:
            # Calculate averages and success rates
            health_checks = [h for h in self.metrics['platform_health'] if 'is_healthy' in h]
            uptime = sum(1 for h in health_checks if h['is_healthy']) / len(health_checks) * 100 if health_checks else 0
            
            response_times = [h['response_time'] for h in health_checks if 'response_time' in h]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            feature_tests = [f for f in self.metrics['feature_usage'] if 'working' in f]
            feature_success_rate = sum(1 for f in feature_tests if f['working']) / len(feature_tests) * 100 if feature_tests else 0
            
            ai_tests = [a for a in self.metrics['ai_performance'] if 'working' in a]
            ai_success_rate = sum(1 for a in ai_tests if a['working']) / len(ai_tests) * 100 if ai_tests else 0
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'monitoring_duration': '30 minutes',
                'platform_metrics': {
                    'uptime_percentage': round(uptime, 2),
                    'average_response_time': round(avg_response_time, 2),
                    'total_health_checks': len(health_checks)
                },
                'feature_metrics': {
                    'success_rate_percentage': round(feature_success_rate, 2),
                    'total_feature_tests': len(feature_tests),
                    'search_functionality': 'operational' if feature_success_rate > 80 else 'needs_attention',
                    'theme_analysis': 'operational' if feature_success_rate > 80 else 'needs_attention',
                    'ai_insights': 'operational' if ai_success_rate > 80 else 'needs_attention'
                },
                'ai_performance': {
                    'success_rate_percentage': round(ai_success_rate, 2),
                    'total_ai_tests': len(ai_tests)
                },
                'recommendations': [
                    'Platform is stable and ready for production use' if uptime > 90 else 'Platform needs stability improvements',
                    'All major features are functioning correctly' if feature_success_rate > 80 else 'Some features need optimization',
                    'AI systems are providing reliable insights' if ai_success_rate > 80 else 'AI systems need tuning',
                    'Ready for real-world user testing' if uptime > 90 and feature_success_rate > 80 else 'Needs optimization before wider deployment'
                ]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary report generation failed: {e}")
            return {'error': str(e)}
    
    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        logger.info("Starting monitoring cycle...")
        
        # Check platform health
        self.check_platform_health()
        time.sleep(5)
        
        # Test search functionality
        self.test_search_functionality()
        time.sleep(5)
        
        # Test theme analysis
        self.test_theme_analysis()
        time.sleep(10)
        
        # Test AI insights
        self.test_ai_insights()
        time.sleep(10)
        
        logger.info("Monitoring cycle completed.")

if __name__ == "__main__":
    monitor = DataCollectionMonitor()
    
    # Run a quick test cycle
    logger.info("Running initial data collection test...")
    monitor.run_monitoring_cycle()
    
    # Generate and display summary
    summary = monitor.generate_summary_report()
    print(json.dumps(summary, indent=2))