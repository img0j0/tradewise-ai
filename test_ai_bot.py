#!/usr/bin/env python3
"""
Test the AI Paper Trading Bot with the deployed platform
"""

import os
import sys
import time
import json
import logging
import requests
from datetime import datetime
from paper_trading_automation import PaperTradingBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_platform_health():
    """Test if the platform is healthy and ready"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            logger.info(f"Platform Status: {health_data['status']}")
            logger.info(f"Database: {health_data.get('database', 'unknown')}")
            logger.info(f"AI Services: {health_data.get('ai_services', {})}")
            logger.info(f"Features: {', '.join(health_data.get('features', []))}")
            return True
        else:
            logger.error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return False

def test_ai_bot():
    """Test the AI paper trading bot"""
    logger.info("Testing AI Paper Trading Bot...")
    
    # Initialize the bot
    bot = PaperTradingBot(base_url="http://localhost:5000")
    
    # Test authentication
    if not bot.authenticate():
        logger.error("Bot authentication failed")
        return False
    
    logger.info("Bot authenticated successfully")
    
    # Test market data retrieval
    logger.info("Testing market data retrieval...")
    for symbol in ['AAPL', 'MSFT', 'GOOGL']:
        market_data = bot.get_market_data(symbol)
        if market_data:
            logger.info(f"{symbol}: ${market_data['current_price']:.2f}")
        else:
            logger.warning(f"No market data for {symbol}")
    
    # Test AI analysis
    logger.info("Testing AI analysis...")
    decision = bot.analyze_stock('AAPL')
    if decision:
        logger.info(f"AI Decision: {decision.action} {decision.quantity} shares of {decision.symbol}")
        logger.info(f"Confidence: {decision.confidence:.2f}")
        logger.info(f"Reasoning: {decision.reasoning}")
    else:
        logger.info("No trading decision made for AAPL")
    
    # Test performance metrics
    logger.info("Testing performance metrics...")
    bot.update_performance_metrics()
    
    # Generate test report
    logger.info("Generating test report...")
    bot.save_report("test_report.json")
    
    logger.info("AI Bot test completed successfully!")
    return True

def main():
    """Main test function"""
    logger.info("🤖 AI Paper Trading Bot Test Suite")
    logger.info("=" * 50)
    
    # Test platform health
    if not test_platform_health():
        logger.error("Platform health check failed. Ensure the platform is running.")
        return False
    
    logger.info("Platform is healthy ✓")
    
    # Test AI bot
    if not test_ai_bot():
        logger.error("AI Bot test failed")
        return False
    
    logger.info("AI Bot test successful ✓")
    
    logger.info("=" * 50)
    logger.info("🎉 All tests passed! The AI Paper Trading Bot is ready for deployment.")
    logger.info("To start automated trading during market hours, run:")
    logger.info("python3 paper_trading_automation.py")
    logger.info("=" * 50)
    
    return True

if __name__ == "__main__":
    main()