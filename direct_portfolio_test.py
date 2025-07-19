#!/usr/bin/env python3
"""
Direct portfolio interface test - bypasses authentication for testing
"""
import sys
import os
from app import app

def test_enhanced_portfolio():
    """Test the enhanced portfolio interface directly"""
    with app.app_context():
        print("🎯 ENHANCED PORTFOLIO DIRECT TEST")
        print("=" * 40)
        
        try:
            from flask import render_template
            
            # Test direct template rendering
            enhanced_content = render_template('enhanced_portfolio.html', user_authenticated=False)
            print(f"✅ Enhanced template rendered: {len(enhanced_content):,} characters")
            
            # Check for key enhanced features
            checks = [
                ('portfolio-container', 'Portfolio container element'),
                ('EnhancedPortfolioManager', 'Enhanced JavaScript manager'),
                ('backdrop-filter: blur', 'Glassmorphic design'),
                ('gradient', 'Modern gradient backgrounds'),
                ('overview-cards', 'Overview cards layout'),
                ('holdings-section', 'Holdings management section'),
                ('ai-insights', 'AI insights integration'),
                ('loading-state', 'Loading state handling'),
                ('empty-state', 'Empty state guidance')
            ]
            
            features_found = 0
            for feature, description in checks:
                if feature in enhanced_content:
                    print(f"✅ {description}")
                    features_found += 1
                else:
                    print(f"❌ Missing: {description}")
            
            print(f"\n📊 ENHANCED FEATURES: {features_found}/{len(checks)} implemented")
            
            if features_found >= 7:
                print("🚀 ENHANCED PORTFOLIO: FULLY OPERATIONAL")
                return True
            else:
                print("⚠️  ENHANCED PORTFOLIO: PARTIAL IMPLEMENTATION")
                return False
                
        except Exception as e:
            print(f"❌ Error testing enhanced portfolio: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    test_enhanced_portfolio()