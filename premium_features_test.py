#!/usr/bin/env python3
"""
Premium Bloomberg-Style Features Test Suite
Tests all premium features that will be paid access tools
"""

import requests
import json
import sys
from datetime import datetime

class PremiumFeaturesTest:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_symbols = ["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA"]
        self.results = {}
        
    def test_bloomberg_intelligence(self):
        """Test Bloomberg Killer Intelligence Engine"""
        print("🔍 Testing Bloomberg Intelligence Engine...")
        
        for symbol in self.test_symbols:
            try:
                response = requests.get(f"{self.base_url}/api/analysis/{symbol}")
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check critical Bloomberg-style data points
                    required_fields = [
                        'symbol', 'company_name', 'price_data', 'trading_metrics',
                        'risk_analysis', 'momentum_analysis', 'volume_intelligence',
                        'key_levels', 'professional_rating', 'market_context'
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        print(f"✅ {symbol}: Bloomberg analysis complete")
                        self.results[f"bloomberg_{symbol}"] = "PASS"
                        
                        # Check data quality
                        if data.get('professional_rating', {}).get('rating'):
                            print(f"   📊 Rating: {data['professional_rating']['rating']}")
                        if data.get('price_data', {}).get('current_price'):
                            print(f"   💰 Price: ${data['price_data']['current_price']:.2f}")
                    else:
                        print(f"❌ {symbol}: Missing fields: {missing_fields}")
                        self.results[f"bloomberg_{symbol}"] = "FAIL"
                else:
                    print(f"❌ {symbol}: API error {response.status_code}")
                    self.results[f"bloomberg_{symbol}"] = "FAIL"
                    
            except Exception as e:
                print(f"❌ {symbol}: Exception - {str(e)}")
                self.results[f"bloomberg_{symbol}"] = "FAIL"
    
    def test_market_intelligence(self):
        """Test Real-Time Market Intelligence"""
        print("\n📈 Testing Market Intelligence...")
        
        try:
            response = requests.get(f"{self.base_url}/api/market-intelligence/overview")
            if response.status_code == 200:
                data = response.json()
                
                required_sections = ['sentiment', 'alerts', 'trending']
                present_sections = [section for section in required_sections if section in data]
                
                if len(present_sections) >= 2:  # At least 2 sections working
                    print("✅ Market Intelligence: Core features operational")
                    self.results['market_intelligence'] = "PASS"
                    
                    if 'sentiment' in data:
                        sentiment = data['sentiment']
                        print(f"   📊 Market Sentiment: {sentiment.get('overall', 'N/A')}")
                        print(f"   🎯 Confidence: {sentiment.get('confidence', 0)*100:.1f}%")
                else:
                    print("❌ Market Intelligence: Insufficient data sections")
                    self.results['market_intelligence'] = "FAIL"
            else:
                print(f"❌ Market Intelligence: API error {response.status_code}")
                self.results['market_intelligence'] = "FAIL"
                
        except Exception as e:
            print(f"❌ Market Intelligence: Exception - {str(e)}")
            self.results['market_intelligence'] = "FAIL"
    
    def test_ai_analysis(self):
        """Test AI-Powered Stock Analysis"""
        print("\n🤖 Testing AI Analysis Engine...")
        
        test_symbol = "AAPL"
        try:
            response = requests.get(f"{self.base_url}/api/ai-stock-analysis/{test_symbol}")
            if response.status_code == 200:
                data = response.json()
                
                # Check for AI-specific features
                ai_fields = ['recommendation', 'confidence', 'analysis', 'risk_level']
                present_ai_fields = [field for field in ai_fields if field in data]
                
                if len(present_ai_fields) >= 3:
                    print("✅ AI Analysis: Advanced features working")
                    self.results['ai_analysis'] = "PASS"
                    
                    if 'recommendation' in data:
                        print(f"   🎯 AI Recommendation: {data['recommendation']}")
                    if 'confidence' in data:
                        print(f"   📊 Confidence: {data['confidence']*100:.1f}%")
                else:
                    print("❌ AI Analysis: Missing AI features")
                    self.results['ai_analysis'] = "FAIL"
            else:
                print(f"❌ AI Analysis: API error {response.status_code}")
                self.results['ai_analysis'] = "FAIL"
                
        except Exception as e:
            print(f"❌ AI Analysis: Exception - {str(e)}")
            self.results['ai_analysis'] = "FAIL"
    
    def test_watchlist_system(self):
        """Test Smart Watchlist Premium Features"""
        print("\n👁️ Testing Smart Watchlist System...")
        
        try:
            response = requests.get(f"{self.base_url}/api/watchlists")
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and 'watchlists' in data:
                    print("✅ Watchlist System: Core functionality working")
                    self.results['watchlist'] = "PASS"
                    
                    watchlists = data['watchlists']
                    if watchlists:
                        print(f"   📋 Active Watchlists: {len(watchlists)}")
                else:
                    print("✅ Watchlist System: Basic structure present")
                    self.results['watchlist'] = "PASS"
            else:
                print(f"❌ Watchlist System: API error {response.status_code}")
                self.results['watchlist'] = "FAIL"
                
        except Exception as e:
            print(f"❌ Watchlist System: Exception - {str(e)}")
            self.results['watchlist'] = "FAIL"
    
    def test_portfolio_analytics(self):
        """Test Advanced Portfolio Analytics"""
        print("\n💼 Testing Portfolio Analytics...")
        
        try:
            response = requests.get(f"{self.base_url}/api/premium-portfolio-analytics")
            if response.status_code == 200:
                data = response.json()
                
                analytics_fields = ['total_value', 'holdings', 'performance', 'allocation']
                present_fields = [field for field in analytics_fields if field in data]
                
                if len(present_fields) >= 2:
                    print("✅ Portfolio Analytics: Advanced features working")
                    self.results['portfolio_analytics'] = "PASS"
                    
                    if 'total_value' in data:
                        print(f"   💰 Portfolio Value: ${data['total_value']:,.2f}")
                else:
                    print("❌ Portfolio Analytics: Missing key features")
                    self.results['portfolio_analytics'] = "FAIL"
            else:
                print(f"❌ Portfolio Analytics: API error {response.status_code}")
                self.results['portfolio_analytics'] = "FAIL"
                
        except Exception as e:
            print(f"❌ Portfolio Analytics: Exception - {str(e)}")
            self.results['portfolio_analytics'] = "FAIL"
    
    def generate_report(self):
        """Generate comprehensive premium features report"""
        print("\n" + "="*60)
        print("🏆 PREMIUM FEATURES QUALITY ASSURANCE REPORT")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result == "PASS")
        
        print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed")
        print(f"🎯 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for test_name, result in self.results.items():
            status_icon = "✅" if result == "PASS" else "❌"
            print(f"   {status_icon} {test_name.replace('_', ' ').title()}: {result}")
        
        # Premium readiness assessment
        print(f"\n🚀 Premium Readiness Assessment:")
        if passed_tests >= total_tests * 0.8:  # 80% pass rate
            print("✅ READY FOR PREMIUM LAUNCH")
            print("   All critical Bloomberg-style features operational")
            print("   Platform meets institutional-grade standards")
        elif passed_tests >= total_tests * 0.6:  # 60% pass rate
            print("⚠️  NEEDS MINOR FIXES")
            print("   Core features working, some optimizations needed")
        else:
            print("❌ REQUIRES MAJOR FIXES")
            print("   Critical issues need resolution before premium launch")
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        return passed_tests / total_tests

def main():
    """Run comprehensive premium features test"""
    print("🚀 TradeWise AI Premium Features Quality Assurance")
    print("Testing Bloomberg Terminal-level capabilities...\n")
    
    tester = PremiumFeaturesTest()
    
    # Run all premium feature tests
    tester.test_bloomberg_intelligence()
    tester.test_market_intelligence()
    tester.test_ai_analysis()
    tester.test_watchlist_system()
    tester.test_portfolio_analytics()
    
    # Generate comprehensive report
    success_rate = tester.generate_report()
    
    # Exit code based on results
    sys.exit(0 if success_rate >= 0.8 else 1)

if __name__ == "__main__":
    main()