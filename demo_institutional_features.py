#!/usr/bin/env python3

"""
Live Demo of Institutional Features
Demonstrates Bloomberg Terminal capabilities in browser
"""

import webbrowser
import time
import requests

def open_platform_demo():
    """Open the platform and provide demo instructions"""
    
    platform_url = "http://localhost:5000"
    
    print("🏛️ TradeWise AI - Institutional Features Demo")
    print("=" * 60)
    print("Bloomberg Terminal capabilities at 98% cost savings!")
    print("Elite Plan: $39.99/month vs Bloomberg Terminal: $2,000/month")
    print("=" * 60)
    
    print("\n🚀 Opening TradeWise AI Platform...")
    
    # Check if platform is running
    try:
        response = requests.get(platform_url, timeout=5)
        if response.status_code == 200:
            print("✅ Platform is running and accessible")
        else:
            print(f"⚠️ Platform response: {response.status_code}")
    except:
        print("❌ Platform may not be running. Please ensure the server is started.")
        return
    
    # Open browser
    webbrowser.open(platform_url)
    
    print("\n📋 Demo Instructions:")
    print("=" * 40)
    
    print("\n1️⃣ LOGIN")
    print("   Username: institutional_test")
    print("   Password: TestPass123!")
    
    print("\n2️⃣ ACCESS INSTITUTIONAL FEATURES")
    print("   • Click 'Tools' in the top navigation")
    print("   • Select 'Institutional Features'")
    
    print("\n3️⃣ EXPLORE 5 BLOOMBERG TERMINAL CAPABILITIES")
    print("   📊 Smart Order Routing")
    print("      • Enter stock symbol (e.g., AAPL)")
    print("      • Set quantity (e.g., 100 shares)")
    print("      • View optimal venue selection & execution scores")
    print("      • Compare fees across NYSE, NASDAQ, ARCA, BATS, IEX")
    
    print("\n   📈 Level 2 Market Data")
    print("      • Enter stock symbol")
    print("      • View professional order book depth")
    print("      • See bid/ask levels with market maker data")
    print("      • Analyze market depth and liquidity")
    
    print("\n   🔄 Options Flow Analysis")
    print("      • Enter stock symbol")
    print("      • Detect unusual options activity")
    print("      • Monitor institutional block trades")
    print("      • Track put/call ratios and sentiment")
    
    print("\n   🌊 Dark Pool Intelligence")
    print("      • Enter stock symbol")
    print("      • Monitor institutional flow patterns")
    print("      • Track major dark pool venues")
    print("      • Analyze block trading activity")
    
    print("\n   🤖 Algorithm Builder")
    print("      • Create custom trading strategies")
    print("      • Backtest with historical data")
    print("      • Optimize parameters with AI")
    print("      • View performance metrics")
    
    print("\n4️⃣ COMPARE WITH BLOOMBERG TERMINAL")
    print("   💰 Cost Comparison:")
    print("      • TradeWise Elite: $39.99/month")
    print("      • Bloomberg Terminal: $2,000/month")
    print("      • SAVINGS: 98% cost reduction!")
    
    print("\n   🎯 Target Market:")
    print("      • Serious retail traders")
    print("      • Small hedge funds")
    print("      • Family offices")
    print("      • Professional traders")
    
    print("\n5️⃣ TEST REAL STOCKS")
    print("   Try these symbols:")
    print("   • AAPL - Apple Inc.")
    print("   • TSLA - Tesla Inc.")
    print("   • NVDA - NVIDIA Corp.")
    print("   • MSFT - Microsoft Corp.")
    print("   • GOOGL - Alphabet Inc.")
    
    print("\n🎯 EXPECTED RESULTS")
    print("   ✅ Smart Order Routing: Optimal venue recommendations")
    print("   ✅ Level 2 Data: Professional order book analysis")
    print("   ✅ Options Flow: Institutional activity detection")
    print("   ✅ Dark Pools: Block trading intelligence")
    print("   ✅ Algorithm Builder: Strategy creation & backtesting")
    
    print("\n💼 BUSINESS IMPACT")
    print("   • Revenue potential: $1M+ annually")
    print("   • Market disruption: First platform with these capabilities at retail prices")
    print("   • User value: Professional trading tools for everyone")
    
    print("\n🔗 Platform URL: " + platform_url)
    print("\n📞 Ready for questions and feedback!")

if __name__ == "__main__":
    open_platform_demo()